"""
Service IA pour la génération de recettes - Compatible models.py français
Version corrigée avec parsing JSON robuste
"""
import streamlit as st
import httpx
import json
import logging
import re
from typing import List, Dict, Optional
from src.core.models import TypeVersionRecetteEnum

logger = logging.getLogger(__name__)

class AIRecipeService:
    """Service de génération de recettes avec Mistral AI"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            self.api_key = api_key or st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 60  # Augmenté pour laisser plus de temps
            logger.info("AIRecipeService initialisé")
        except KeyError:
            raise ValueError("Clé API Mistral manquante dans les secrets Streamlit")

    async def _call_mistral_api(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: float = 0.7,
            max_tokens: int = 2000
    ) -> str:
        """Appel direct à l'API Mistral avec retry"""
        max_retries = 2

        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    messages = []
                    if system_prompt:
                        messages.append({"role": "system", "content": system_prompt})
                    messages.append({"role": "user", "content": prompt})

                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": self.model,
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens
                        }
                    )
                    response.raise_for_status()
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]

                    logger.info(f"Réponse Mistral (tentative {attempt + 1}):\n{content[:200]}...")
                    return content

            except httpx.HTTPError as e:
                logger.error(f"Erreur HTTP Mistral (tentative {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Erreur de connexion à l'API Mistral après {max_retries} tentatives")
            except Exception as e:
                logger.error(f"Erreur appel Mistral (tentative {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Erreur lors de l'appel à l'API Mistral: {str(e)}")

    async def generate_recipes(
            self,
            count: int,
            filters: Dict,
            version_type: str = TypeVersionRecetteEnum.STANDARD.value
    ) -> List[Dict]:
        """Génère des recettes avec parsing JSON robuste"""
        try:
            system_prompt = self._build_system_prompt(version_type)
            user_prompt = self._build_prompt(count, filters, version_type)

            logger.info(f"Génération de {count} recette(s) avec filtres: {filters}")

            response_content = await self._call_mistral_api(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            recipes = self._parse_response_v2(response_content, count, version_type)
            logger.info(f"✅ {len(recipes)} recette(s) générée(s) avec succès")
            return recipes

        except Exception as e:
            logger.error(f"❌ Erreur génération recettes: {e}")
            raise ValueError(f"Échec de la génération : {str(e)}")

    def _build_system_prompt(self, version_type: str) -> str:
        """Prompt système ultra-strict pour forcer du JSON valide"""
        base = (
            "Tu es un assistant JSON. Tu génères UNIQUEMENT du JSON valide. "
            "INTERDICTION ABSOLUE de:\n"
            "- Ajouter du texte avant le JSON\n"
            "- Ajouter du texte après le JSON\n"
            "- Utiliser des markdown (```json ou ```)\n"
            "- Ajouter des commentaires\n"
            "- Utiliser des apostrophes dans le JSON\n\n"
            "RÈGLES STRICTES:\n"
            "- Commence DIRECTEMENT par {\n"
            "- Termine DIRECTEMENT par }\n"
            "- Utilise UNIQUEMENT des doubles guillemets\n"
            "- Échappe les apostrophes avec \\'\n"
            "- Pas de texte explicatif\n\n"
            "Contexte: Génération de recettes de cuisine françaises."
        )

        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base += "\nAdapte pour bébés 6-18 mois: sans sel, sans sucre ajouté, sans miel."
        elif version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base += "\nOptimise pour batch cooking: étapes parallèles, portions multiples."

        return base

    def _build_prompt(self, count: int, filters: Dict, version_type: str) -> str:
        """Prompt utilisateur avec format JSON strict"""
        parts = [f"Génère {count} recette(s)"]

        if filters.get("saison"):
            parts.append(f"de saison {filters['saison']}")
        if filters.get("is_quick"):
            parts.append("rapides (<30min)")
        if filters.get("is_balanced"):
            parts.append("équilibrées")
        if filters.get("type_repas"):
            parts.append(f"pour le {filters['type_repas']}")
        if filters.get("ingredients"):
            parts.append("avec: " + ", ".join(filters["ingredients"]))
        if filters.get("nom"):
            parts.append(f"similaire à '{filters['nom']}'")

        prompt = " ".join(parts) + ".\n\n"
        prompt += "RÉPONDS UNIQUEMENT AVEC CE FORMAT JSON (commence par { et termine par }):\n"
        prompt += self._get_json_format(version_type)
        prompt += "\n\nATTENTION: PAS DE TEXTE, UNIQUEMENT LE JSON!"

        return prompt

    def _get_json_format(self, version_type: str) -> str:
        """Format JSON strict et minimal"""
        base = """{
  "recettes": [
    {
      "nom": "Pâtes à la tomate",
      "description": "Recette simple et rapide",
      "temps_preparation": 10,
      "temps_cuisson": 15,
      "portions": 4,
      "difficulte": "facile",
      "type_repas": "dîner",
      "saison": "toute_année",
      "categorie": "Italien",
      "est_rapide": true,
      "est_equilibre": true,
      "compatible_bebe": false,
      "compatible_batch": false,
      "congelable": true,
      "ingredients": [
        {"nom": "Pâtes", "quantite": 400, "unite": "g", "optionnel": false},
        {"nom": "Tomates", "quantite": 500, "unite": "g", "optionnel": false}
      ],
      "etapes": [
        {"ordre": 1, "description": "Faire bouillir l eau", "duree": 5},
        {"ordre": 2, "description": "Cuire les pâtes", "duree": 10}
      ]
    }
  ]
}"""

        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base = base.replace(
                "]",
                """],
      "version_bebe": {
        "instructions_modifiees": "Mixer finement",
        "notes_bebe": "À partir de 6 mois",
        "ingredients_modifies": []
      }"""
            )

        if version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base = base.replace(
                "]",
                """],
      "version_batch": {
        "etapes_paralleles": ["Préparer les légumes pendant la cuisson"],
        "temps_optimise": 20,
        "conseils_batch": "Doubler les quantités"
      }"""
            )

        return base

    def _parse_response_v2(self, content: str, expected_count: int, version_type: str) -> List[Dict]:
        """
        Parsing JSON ultra-robuste avec plusieurs stratégies de fallback
        """
        logger.info(f"🔍 Parsing JSON (longueur: {len(content)} caractères)")

        # ========================================
        # STRATÉGIE 1: Nettoyage basique
        # ========================================
        try:
            cleaned = self._clean_json_basic(content)
            data = json.loads(cleaned)
            recipes = self._extract_recipes(data, expected_count)
            if recipes:
                logger.info("✅ Parsing réussi (stratégie 1: nettoyage basique)")
                return self._validate_recipes(recipes)
        except Exception as e:
            logger.warning(f"⚠️ Stratégie 1 échouée: {e}")

        # ========================================
        # STRATÉGIE 2: Extraction forcée d'objet JSON
        # ========================================
        try:
            json_obj = self._extract_json_object(content)
            data = json.loads(json_obj)
            recipes = self._extract_recipes(data, expected_count)
            if recipes:
                logger.info("✅ Parsing réussi (stratégie 2: extraction forcée)")
                return self._validate_recipes(recipes)
        except Exception as e:
            logger.warning(f"⚠️ Stratégie 2 échouée: {e}")

        # ========================================
        # STRATÉGIE 3: Recherche de pattern "recettes"
        # ========================================
        try:
            recipes_array = self._extract_recipes_array(content)
            if recipes_array:
                data = json.loads(recipes_array)
                if isinstance(data, list):
                    recipes = data[:expected_count]
                else:
                    recipes = data.get("recettes", [])[:expected_count]

                if recipes:
                    logger.info("✅ Parsing réussi (stratégie 3: pattern recettes)")
                    return self._validate_recipes(recipes)
        except Exception as e:
            logger.warning(f"⚠️ Stratégie 3 échouée: {e}")

        # ========================================
        # STRATÉGIE 4: Fallback - Recette par défaut
        # ========================================
        logger.error("❌ Toutes les stratégies ont échoué")
        logger.error(f"Réponse brute:\n{content[:500]}")

        return self._get_fallback_recipes(expected_count, version_type)

    def _clean_json_basic(self, content: str) -> str:
        """Nettoyage JSON basique"""
        # Supprimer BOM et caractères invisibles
        cleaned = content.replace("\ufeff", "")
        cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)

        # Supprimer markdown
        cleaned = re.sub(r"```json\s*", "", cleaned)
        cleaned = re.sub(r"```\s*", "", cleaned)

        # Trim
        cleaned = cleaned.strip()

        return cleaned

    def _extract_json_object(self, content: str) -> str:
        """Extrait le premier objet JSON complet avec comptage de brackets"""
        level = 0
        start = None

        for i, ch in enumerate(content):
            if ch == '{':
                if level == 0:
                    start = i
                level += 1
            elif ch == '}':
                if level > 0:
                    level -= 1
                    if level == 0 and start is not None:
                        return content[start:i+1]

        raise ValueError("Aucun objet JSON complet trouvé")

    def _extract_recipes_array(self, content: str) -> str:
        """Cherche spécifiquement le tableau 'recettes'"""
        # Chercher "recettes": [...]
        match = re.search(r'"recettes"\s*:\s*\[', content, re.IGNORECASE)
        if not match:
            raise ValueError("Clé 'recettes' non trouvée")

        start_bracket = match.end() - 1  # Position du [
        level = 0

        for i in range(start_bracket, len(content)):
            if content[i] == '[':
                level += 1
            elif content[i] == ']':
                level -= 1
                if level == 0:
                    # Reconstituer un JSON complet
                    array = content[start_bracket:i+1]
                    return f'{{"recettes": {array}}}'

        raise ValueError("Tableau 'recettes' incomplet")

    def _extract_recipes(self, data: Dict, expected_count: int) -> List[Dict]:
        """Extrait les recettes depuis différentes structures"""
        if "recettes" in data:
            return data["recettes"][:expected_count]
        elif "recipes" in data:
            return data["recipes"][:expected_count]
        elif isinstance(data, list):
            return data[:expected_count]
        else:
            raise ValueError("Structure JSON inattendue")

    def _validate_recipes(self, recipes: List[Dict]) -> List[Dict]:
        """Valide et nettoie les recettes"""
        validated = []
        required_fields = ["nom", "description", "temps_preparation", "temps_cuisson",
                           "portions", "ingredients", "etapes"]

        for idx, recipe in enumerate(recipes):
            try:
                # Vérifier champs obligatoires
                missing = [f for f in required_fields if f not in recipe]
                if missing:
                    logger.warning(f"Recette {idx}: champs manquants {missing}")
                    continue

                # Vérifier ingrédients
                if not isinstance(recipe["ingredients"], list) or not recipe["ingredients"]:
                    logger.warning(f"Recette {idx}: ingrédients invalides")
                    continue

                # Vérifier étapes
                if not isinstance(recipe["etapes"], list) or not recipe["etapes"]:
                    logger.warning(f"Recette {idx}: étapes invalides")
                    continue

                # Nettoyer les apostrophes
                recipe["nom"] = recipe["nom"].replace("'", "'")
                recipe["description"] = recipe["description"].replace("'", "'")

                # Valeurs par défaut
                recipe.setdefault("difficulte", "moyen")
                recipe.setdefault("type_repas", "dîner")
                recipe.setdefault("saison", "toute_année")
                recipe.setdefault("categorie", "Autre")
                recipe.setdefault("est_rapide", False)
                recipe.setdefault("est_equilibre", True)
                recipe.setdefault("compatible_bebe", False)
                recipe.setdefault("compatible_batch", False)
                recipe.setdefault("congelable", False)

                validated.append(recipe)

            except Exception as e:
                logger.error(f"❌ Erreur validation recette {idx}: {e}")
                continue

        if not validated:
            raise ValueError("Aucune recette valide après validation")

        return validated

    def _get_fallback_recipes(self, count: int, version_type: str) -> List[Dict]:
        """Recettes par défaut en cas d'échec total"""
        logger.warning("🆘 Utilisation des recettes de fallback")

        fallbacks = [
            {
                "nom": "Pâtes au beurre",
                "description": "Recette simple et rapide",
                "temps_preparation": 5,
                "temps_cuisson": 10,
                "portions": 4,
                "difficulte": "facile",
                "type_repas": "dîner",
                "saison": "toute_année",
                "categorie": "Italien",
                "est_rapide": True,
                "est_equilibre": False,
                "compatible_bebe": False,
                "compatible_batch": False,
                "congelable": False,
                "ingredients": [
                    {"nom": "Pâtes", "quantite": 400, "unite": "g", "optionnel": False},
                    {"nom": "Beurre", "quantite": 50, "unite": "g", "optionnel": False}
                ],
                "etapes": [
                    {"ordre": 1, "description": "Faire bouillir de l'eau salée", "duree": 5},
                    {"ordre": 2, "description": "Cuire les pâtes selon les instructions", "duree": 8},
                    {"ordre": 3, "description": "Égoutter et mélanger avec le beurre", "duree": 2}
                ]
            },
            {
                "nom": "Omelette nature",
                "description": "Classique et nutritif",
                "temps_preparation": 5,
                "temps_cuisson": 5,
                "portions": 2,
                "difficulte": "facile",
                "type_repas": "dîner",
                "saison": "toute_année",
                "categorie": "Œufs",
                "est_rapide": True,
                "est_equilibre": True,
                "compatible_bebe": False,
                "compatible_batch": False,
                "congelable": False,
                "ingredients": [
                    {"nom": "Œufs", "quantite": 4, "unite": "pcs", "optionnel": False},
                    {"nom": "Beurre", "quantite": 20, "unite": "g", "optionnel": False},
                    {"nom": "Sel", "quantite": 2, "unite": "g", "optionnel": False}
                ],
                "etapes": [
                    {"ordre": 1, "description": "Battre les œufs dans un bol", "duree": 2},
                    {"ordre": 2, "description": "Faire fondre le beurre dans une poêle", "duree": 1},
                    {"ordre": 3, "description": "Verser les œufs et cuire à feu moyen", "duree": 4}
                ]
            },
            {
                "nom": "Salade verte",
                "description": "Fraîche et légère",
                "temps_preparation": 10,
                "temps_cuisson": 0,
                "portions": 4,
                "difficulte": "facile",
                "type_repas": "déjeuner",
                "saison": "été",
                "categorie": "Salade",
                "est_rapide": True,
                "est_equilibre": True,
                "compatible_bebe": False,
                "compatible_batch": False,
                "congelable": False,
                "ingredients": [
                    {"nom": "Laitue", "quantite": 1, "unite": "pcs", "optionnel": False},
                    {"nom": "Tomates", "quantite": 2, "unite": "pcs", "optionnel": False},
                    {"nom": "Huile d'olive", "quantite": 30, "unite": "ml", "optionnel": False},
                    {"nom": "Vinaigre", "quantite": 15, "unite": "ml", "optionnel": False}
                ],
                "etapes": [
                    {"ordre": 1, "description": "Laver et essorer la salade", "duree": 5},
                    {"ordre": 2, "description": "Couper les tomates", "duree": 3},
                    {"ordre": 3, "description": "Préparer la vinaigrette et mélanger", "duree": 2}
                ]
            }
        ]

        return fallbacks[:count]

    def generate_image_url(self, recipe_name: str, description: str) -> str:
        """Génère une URL d'image (Unsplash fallback)"""
        try:
            # Vérifier si Stability AI est configuré
            if "stability" in st.secrets and st.secrets["stability"].get("api_key"):
                # TODO: Implémenter Stability AI si nécessaire
                pass
        except:
            pass

        # Fallback: Unsplash
        safe_name = recipe_name.replace(" ", ",").replace("'", "")
        return f"https://source.unsplash.com/400x300/?{safe_name},food,cooking"


# Instance globale
ai_recette_service = AIRecipeService()