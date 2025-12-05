"""
Service IA pour la génération de recettes - Compatible models.py français
"""
import streamlit as st
import httpx
import json
import logging
from typing import List, Dict, Optional
from src.core.models import TypeVersionRecetteEnum

logger = logging.getLogger(__name__)

class AIRecipeService:
    """Service de génération de recettes avec Mistral AI"""
    def __init__(self, api_key: Optional[str] = None):
        """Initialise le service avec la clé API Mistral"""
        try:
            self.api_key = api_key or st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 30
            logger.info("✅ AIRecipeService initialisé")
        except KeyError:
            raise ValueError("Clé API Mistral manquante dans les secrets Streamlit")

    async def _call_mistral_api(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: float = 0.7,
            max_tokens: int = 2000
    ) -> str:
        """Appel direct à l'API Mistral"""
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
                return result["choices"][0]["message"]["content"]
        except httpx.HTTPError as e:
            logger.error(f"Erreur HTTP Mistral: {e}")
            raise ValueError("Erreur de connexion à l'API Mistral")
        except Exception as e:
            logger.error(f"Erreur appel Mistral: {e}")
            raise ValueError("Erreur lors de l'appel à l'API Mistral")

    async def generate_recipes(
            self,
            count: int,
            filters: Dict,
            version_type: str = TypeVersionRecetteEnum.STANDARD.value
    ) -> List[Dict]:
        """Génère des recettes avec l'API Mistral"""
        try:
            system_prompt = self._build_system_prompt(version_type)
            user_prompt = self._build_prompt(count, filters, version_type)
            response_content = await self._call_mistral_api(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            recipes = self._parse_response(response_content, count)
            return recipes
        except Exception as e:
            logger.error(f"Erreur génération recettes: {e}")
            raise ValueError(f"Échec de la génération : {str(e)}")

    def _build_system_prompt(self, version_type: str) -> str:
        """Construit le system prompt"""
        base = (
            "Tu es un chef cuisinier expert et nutritionniste français. "
            "Tu génères des recettes précises, réalisables et équilibrées. "
            "Réponds UNIQUEMENT en JSON valide, sans commentaires, sans balises markdown. "
            "Utilise des noms français pour tous les champs."
        )
        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base += (
                "\n\nTu adaptes les recettes pour bébés (6-18 mois) : "
                "- Aucun sel, sucre ajouté, miel\n"
                "- Textures adaptées (purée, morceaux fondants)\n"
                "- Ingrédients sûrs et nutritifs"
            )
        elif version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base += (
                "\n\nTu optimises les recettes pour le batch cooking : "
                "- Identifie les étapes parallélisables\n"
                "- Optimise le temps total\n"
                "- Suggère des quantités pour préparer plusieurs portions"
            )
        return base

    def _build_prompt(self, count: int, filters: Dict, version_type: str) -> str:
        """Construit le prompt utilisateur"""
        prompt_parts = [f"Génère {count} recette(s) française(s)"]
        if filters.get("saison"):
            prompt_parts.append(f"de saison {filters['saison']}")
        if filters.get("is_quick"):
            prompt_parts.append("rapides (<30 minutes)")
        if filters.get("is_balanced"):
            prompt_parts.append("équilibrées")
        if filters.get("type_repas"):
            prompt_parts.append(f"pour le {filters['type_repas']}")
        if filters.get("ingredients"):
            ing_list = ", ".join(filters["ingredients"])
            prompt_parts.append(f"avec : {ing_list}")
        if filters.get("nom"):
            prompt_parts.append(f"similaires à '{filters['nom']}'")
        prompt = " ".join(prompt_parts) + ".\n\n"
        prompt += self._get_json_format(version_type)
        return prompt

    def _get_json_format(self, version_type: str) -> str:
        """Retourne le format JSON attendu (noms français)"""
        base_format = """
Format JSON EXACT (structure française) :
{
  "recettes": [
    {
      "nom": "Nom de la recette",
      "description": "Description courte (2-3 phrases)",
      "temps_preparation": 15,
      "temps_cuisson": 30,
      "portions": 4,
      "difficulte": "facile",
      "type_repas": "dîner",
      "saison": "toute_année",
      "categorie": "Végétarien",
      "est_rapide": true,
      "est_equilibre": true,
      "compatible_bebe": false,
      "compatible_batch": true,
      "congelable": true,
      "ingredients": [
        {
          "nom": "Tomates",
          "quantite": 500,
          "unite": "g",
          "optionnel": false
        }
      ],
      "etapes": [
        {
          "ordre": 1,
          "description": "Éplucher et couper les tomates",
          "duree": 5
        }
      ]
    }
  ]
}
IMPORTANT :
- Tous les champs doivent être en français
- Les noms de champs doivent correspondre exactement au modèle
- Utilise "facile", "moyen", "difficile" pour difficulte
- Utilise "petit_dejeuner", "dejeuner", "dîner", "goûter" pour type_repas
- Utilise "printemps", "été", "automne", "hiver", "toute_année" pour saison
"""
        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base_format += """
Ajoute pour chaque recette :
"version_bébé": {
  "instructions_modifiees": "Mixez finement. Pas de sel.",
  "notes_bebe": "Dès 6 mois. Surveiller allergies.",
  "ingredients_modifies": [
    {"nom": "Tomates", "quantite": 100, "unite": "g", "note": "Pelées"}
  ]
}
"""
        elif version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base_format += """
Ajoute pour chaque recette :
"version_batch": {
  "etapes_paralleles": ["Éplucher pendant que l'eau chauffe"],
  "temps_optimise": 45,
  "conseils_batch": "x4 portions. Congèle 3 mois."
}
"""
        return base_format

    def _parse_response(self, content: str, expected_count: int) -> List[Dict]:
        """Parse et valide la réponse JSON"""
        try:
            cleaned = content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            data = json.loads(cleaned)
            if "recettes" in data:
                recettes = data["recettes"][\:expected_count]
                elif "recipes" in data:
                recettes = data["recipes"][\:expected_count]
                else:
                raise ValueError("Clé 'recettes' ou 'recipes' manquante")
            validated = []
            for recette in recettes:
                if self._validate_recipe(recette):
                    validated.append(recette)
            if not validated:
                raise ValueError("Aucune recette valide générée")
            return validated
        except json.JSONDecodeError as e:
            logger.error(f"Erreur JSON: {e}")
            logger.error(f"Contenu: {content[:500]}")
            raise ValueError("Réponse JSON invalide de l'IA")
        except Exception as e:
            logger.error(f"Erreur parsing: {e}")
            raise ValueError(f"Échec du parsing : {str(e)}")

    def _validate_recipe(self, recette: Dict) -> bool:
        """Valide qu'une recette a les champs requis"""
        required = ["nom", "description", "temps_preparation", "temps_cuisson",
                    "portions", "ingredients", "etapes"]
        for field in required:
            if field not in recette:
                logger.warning(f"Champ '{field}' manquant dans '{recette.get('nom', 'inconnue')}'")
                return False
        if not isinstance(recette["ingredients"], list) or len(recette["ingredients"]) == 0:
            logger.warning(f"Ingrédients invalides pour '{recette['nom']}'")
            return False
        if not isinstance(recette["etapes"], list) or len(recette["etapes"]) == 0:
            logger.warning(f"Étapes invalides pour '{recette['nom']}'")
            return False
        return True

    async def generate_image_url(self, recipe_name: str, description: str) -> str:
        """Génère une URL d'image (placeholder Unsplash)"""
        safe_name = recipe_name.replace(' ', ',')
        return f"https://source.unsplash.com/400x300/?{safe_name},food"

# Instance globale
ai_recette_service = AIRecipeService()
