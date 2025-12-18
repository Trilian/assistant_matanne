"""
Service IA Recettes v2 - Parsing Robuste avec Pydantic
Remplace src/services/ai_recette_service.py
"""
import streamlit as st
import httpx
import json
import logging
import re
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator, ValidationError

from src.core.models import TypeVersionRecetteEnum
from src.core.ai_cache import AICache, RateLimiter

logger = logging.getLogger(__name__)


# ===================================
# SCHÉMAS PYDANTIC POUR VALIDATION
# ===================================


class IngredientAI(BaseModel):
    """Ingrédient validé par Pydantic"""

    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    optionnel: bool = False

    @validator("nom")
    def clean_nom(cls, v):
        # Nettoyer apostrophes
        return v.replace("'", "'").strip()

    @validator("quantite")
    def round_qty(cls, v):
        return round(v, 2)


class EtapeAI(BaseModel):
    """Étape validée"""

    ordre: int = Field(..., ge=1, le=50)
    description: str = Field(..., min_length=10, max_length=1000)
    duree: Optional[int] = Field(None, ge=0, le=300)

    @validator("description")
    def clean_desc(cls, v):
        return v.replace("'", "'").strip()


class VersionBebeAI(BaseModel):
    """Version bébé"""

    instructions_modifiees: Optional[str] = None
    notes_bebe: Optional[str] = None
    ingredients_modifies: Optional[List[IngredientAI]] = None


class VersionBatchAI(BaseModel):
    """Version batch cooking"""

    etapes_paralleles: Optional[List[str]] = None
    temps_optimise: Optional[int] = Field(None, gt=0, le=300)
    conseils_batch: Optional[str] = None


class RecetteAI(BaseModel):
    """Recette complète validée"""

    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(..., gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    type_repas: str = Field("dîner", pattern="^(petit_déjeuner|déjeuner|dîner|goûter)$")
    saison: str = Field("toute_année")
    categorie: Optional[str] = Field(None, max_length=100)

    est_rapide: bool = False
    est_equilibre: bool = True
    compatible_bebe: bool = False
    compatible_batch: bool = False
    congelable: bool = False

    ingredients: List[IngredientAI] = Field(..., min_items=1, max_items=50)
    etapes: List[EtapeAI] = Field(..., min_items=1, max_items=30)

    # Versions optionnelles
    version_bebe: Optional[VersionBebeAI] = None
    version_batch: Optional[VersionBatchAI] = None

    @validator("nom", "description")
    def clean_text(cls, v):
        return v.replace("'", "'").strip()

    @validator("est_rapide", always=True)
    def auto_rapide(cls, v, values):
        """Auto-marque rapide si <30min"""
        prep = values.get("temps_preparation", 0)
        cuisson = values.get("temps_cuisson", 0)
        return (prep + cuisson) < 30

    @validator("etapes")
    def validate_etapes_ordre(cls, v):
        """Vérifie ordre séquentiel"""
        ordres = [e.ordre for e in v]
        if ordres != sorted(ordres):
            # Auto-correction
            for i, etape in enumerate(sorted(v, key=lambda x: x.ordre), start=1):
                etape.ordre = i
        return v

    class Config:
        extra = "ignore"  # Ignore champs non définis


class RecettesResponse(BaseModel):
    """Réponse complète de l'IA"""

    recettes: List[RecetteAI] = Field(..., min_items=1, max_items=10)

    class Config:
        extra = "ignore"


# ===================================
# SERVICE IA AMÉLIORÉ
# ===================================


class AIRecetteService:
    """Service de génération de recettes avec Mistral AI - Version robuste"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            self.api_key = api_key or st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 60
            logger.info("✅ AIRecetteServiceV2 initialisé")
        except KeyError:
            raise ValueError("Clé API Mistral manquante dans les secrets")

    # ===================================
    # APPEL API AVEC CACHE
    # ===================================

    async def _call_mistral_cached(
        self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 2000
    ) -> str:
        """Appel API avec cache et rate limiting"""

        # 1. Vérifier rate limit
        can_call, error_msg = RateLimiter.can_call()
        if not can_call:
            raise ValueError(error_msg)

        # 2. Vérifier cache
        cache_params = {"system": system_prompt, "temp": temperature, "tokens": max_tokens}

        cached = AICache.get(prompt, cache_params)
        if cached:
            logger.info("🎯 Réponse depuis cache")
            return cached

        # 3. Appel API
        logger.info(f"🌐 Appel API Mistral (modèle: {self.model})")

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
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )

                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # 4. Sauvegarder en cache
                AICache.set(prompt, cache_params, content, ttl=3600)

                # 5. Enregistrer l'appel
                RateLimiter.record_call()

                logger.info(f"✅ Réponse reçue ({len(content)} chars)")
                return content

        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP: {e}")
            raise ValueError(f"Erreur API Mistral: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            raise

    # ===================================
    # GÉNÉRATION RECETTES
    # ===================================

    async def generate_recipes(
        self, count: int, filters: Dict, version_type: str = TypeVersionRecetteEnum.STANDARD.value
    ) -> List[Dict]:
        """
        Génère des recettes avec parsing Pydantic robuste

        Args:
            count: Nombre de recettes
            filters: Filtres (saison, type_repas, ingredients, etc.)
            version_type: Type de version à générer

        Returns:
            Liste de recettes validées
        """
        try:
            # 1. Construire prompts
            system_prompt = self._build_system_prompt(version_type)
            user_prompt = self._build_user_prompt(count, filters, version_type)

            logger.info(f"🤖 Génération de {count} recette(s)")
            logger.debug(f"Filtres: {filters}")

            # 2. Appeler l'IA
            response = await self._call_mistral_cached(
                prompt=user_prompt, system_prompt=system_prompt, temperature=0.7, max_tokens=2000
            )

            # 3. Parser avec Pydantic
            recipes = self._parse_with_pydantic(response, count)

            logger.info(f"✅ {len(recipes)} recette(s) générée(s) et validée(s)")
            return recipes

        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            raise ValueError(f"Échec génération: {str(e)}")

    # ===================================
    # PARSING ROBUSTE
    # ===================================

    # src/services/ai_recette_service.py - CORRIGER la méthode _parse_with_pydantic

    def _parse_with_pydantic(self, content: str, expected_count: int) -> List[Dict]:
        """
        Parse la réponse avec Pydantic - VERSION ULTRA-ROBUSTE
        """
        logger.info("🔍 Parsing JSON avec Pydantic")

        # ===================================
        # STRATÉGIE 0: Log pour debug
        # ===================================
        logger.debug(f"Contenu brut (500 premiers chars): {content[:500]}")

        # ===================================
        # STRATÉGIE 1: Parse direct
        # ===================================
        try:
            cleaned = self._clean_json(content)
            response = RecettesResponse.parse_raw(cleaned)
            recipes = [r.dict() for r in response.recettes[:expected_count]]

            logger.info("✅ Parse réussi (stratégie 1: direct)")
            return recipes

        except ValidationError as e:
            logger.warning(f"⚠️ Stratégie 1 échouée - Erreurs Pydantic:")
            for error in e.errors():
                logger.warning(f"  - {error['loc']}: {error['msg']}")

        except Exception as e:
            logger.warning(f"⚠️ Stratégie 1 échouée: {e}")

        # ===================================
        # STRATÉGIE 2: Extraction JSON objet
        # ===================================
        try:
            json_obj = self._extract_json_object(content)
            logger.debug(f"JSON extrait (stratégie 2): {json_obj[:200]}")

            response = RecettesResponse.parse_raw(json_obj)
            recipes = [r.dict() for r in response.recettes[:expected_count]]

            logger.info("✅ Parse réussi (stratégie 2: extraction)")
            return recipes

        except (ValidationError, ValueError) as e:
            logger.warning(f"⚠️ Stratégie 2 échouée: {e}")

        # ===================================
        # STRATÉGIE 3: Parse manuel + validation individuelle
        # ===================================
        try:
            import json

            cleaned = self._clean_json(content)
            data = json.loads(cleaned)

            # Extraire recettes
            if isinstance(data, dict) and "recettes" in data:
                recettes_raw = data["recettes"]
            elif isinstance(data, list):
                recettes_raw = data
            else:
                raise ValueError("Structure JSON non reconnue")

            # Valider chaque recette individuellement
            recipes = []
            for idx, recette_data in enumerate(recettes_raw[:expected_count]):
                try:
                    # Valider avec Pydantic
                    recette_validated = RecetteAI(**recette_data)
                    recipes.append(recette_validated.dict())
                    logger.info(f"✅ Recette {idx+1} validée: {recette_validated.nom}")

                except ValidationError as e:
                    logger.error(f"❌ Recette {idx+1} invalide:")
                    for error in e.errors():
                        logger.error(f"  - {error['loc']}: {error['msg']}")

                    # Essayer de corriger les erreurs courantes
                    try:
                        recette_corrigee = RecipeImageGenerator._fix_common_errors(recette_data)
                        recette_validated = RecetteAI(**recette_corrigee)
                        recipes.append(recette_validated.dict())
                        logger.info(f"✅ Recette {idx+1} corrigée et validée")
                    except:
                        logger.error(f"❌ Impossible de corriger la recette {idx+1}, ignorée")
                        continue

            if recipes:
                logger.info(f"✅ Parse réussi (stratégie 3: manuel) - {len(recipes)} recettes")
                return recipes

        except Exception as e:
            logger.warning(f"⚠️ Stratégie 3 échouée: {e}")

        # ===================================
        # STRATÉGIE 4: Fallback recettes
        # ===================================
        logger.error("❌ Toutes les stratégies ont échoué")
        logger.error(f"Contenu problématique: {content[:1000]}")

        return self._fallback_recipes(expected_count)

    @staticmethod
    def _fix_common_errors(recette_data: dict) -> dict:
        """Corrige les erreurs courantes dans les données recette"""

        # Fix 1: Temps négatifs ou nuls
        if recette_data.get("temps_preparation", 0) <= 0:
            recette_data["temps_preparation"] = 15

        if recette_data.get("temps_cuisson", 0) < 0:
            recette_data["temps_cuisson"] = 0

        # Fix 2: Portions invalides
        if recette_data.get("portions", 0) <= 0:
            recette_data["portions"] = 4

        # Fix 3: Difficulté invalide
        if recette_data.get("difficulte") not in ["facile", "moyen", "difficile"]:
            recette_data["difficulte"] = "moyen"

        # Fix 4: Type repas invalide
        valid_types = ["petit_déjeuner", "déjeuner", "dîner", "goûter"]
        if recette_data.get("type_repas") not in valid_types:
            recette_data["type_repas"] = "dîner"

        # Fix 5: Saison invalide
        valid_saisons = ["printemps", "été", "automne", "hiver", "toute_année"]
        if recette_data.get("saison") not in valid_saisons:
            recette_data["saison"] = "toute_année"

        # Fix 6: Ingrédients vides
        if not recette_data.get("ingredients"):
            recette_data["ingredients"] = [
                {"nom": "Ingrédient 1", "quantite": 1.0, "unite": "pcs", "optionnel": False}
            ]

        # Fix 7: Étapes vides
        if not recette_data.get("etapes"):
            recette_data["etapes"] = [
                {"ordre": 1, "description": "Préparer les ingrédients", "duree": None}
            ]

        # Fix 8: Ordre des étapes
        for idx, etape in enumerate(recette_data.get("etapes", []), 1):
            etape["ordre"] = idx

        return recette_data

    def _clean_json(self, content: str) -> str:
        """Nettoie le JSON basique"""
        # Supprimer BOM et caractères invisibles
        cleaned = content.replace("\ufeff", "")
        cleaned = re.sub(r"[\x00-\x1F\x7F]", "", cleaned)

        # Supprimer markdown
        cleaned = re.sub(r"```json\s*", "", cleaned)
        cleaned = re.sub(r"```\s*", "", cleaned)

        return cleaned.strip()

    def _extract_json_object(self, content: str) -> str:
        """Extrait le premier objet JSON complet"""
        level = 0
        start = None

        for i, ch in enumerate(content):
            if ch == "{":
                if level == 0:
                    start = i
                level += 1
            elif ch == "}":
                level -= 1
                if level == 0 and start is not None:
                    return content[start : i + 1]

        raise ValueError("Aucun objet JSON complet trouvé")

    def _extract_recipes_array(self, content: str) -> str:
        """Extrait spécifiquement le tableau recettes"""
        match = re.search(r'"recettes"\s*:\s*\[', content, re.IGNORECASE)
        if not match:
            raise ValueError("Clé 'recettes' non trouvée")

        start = match.end() - 1  # Position du [
        level = 0

        for i in range(start, len(content)):
            if content[i] == "[":
                level += 1
            elif content[i] == "]":
                level -= 1
                if level == 0:
                    array = content[start : i + 1]
                    return f'{{"recettes": {array}}}'

        raise ValueError("Tableau 'recettes' incomplet")

    def _fallback_recipes(self, count: int) -> List[Dict]:
        """Recettes de fallback si tout échoue"""
        logger.warning("🆘 Utilisation des recettes de fallback")

        fallback = [
            {
                "nom": "Pâtes au beurre",
                "description": "Recette simple et rapide pour dépanner",
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
                    {"nom": "Beurre", "quantite": 50, "unite": "g", "optionnel": False},
                ],
                "etapes": [
                    {"ordre": 1, "description": "Faire bouillir de l'eau salée", "duree": 5},
                    {"ordre": 2, "description": "Cuire les pâtes", "duree": 8},
                    {"ordre": 3, "description": "Égoutter et mélanger avec le beurre", "duree": 2},
                ],
            },
            {
                "nom": "Omelette nature",
                "description": "Classique rapide et nutritif",
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
                ],
                "etapes": [
                    {"ordre": 1, "description": "Battre les œufs", "duree": 2},
                    {"ordre": 2, "description": "Cuire à la poêle", "duree": 4},
                ],
            },
            {
                "nom": "Salade composée",
                "description": "Fraîche et équilibrée",
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
                    {"nom": "Concombre", "quantite": 1, "unite": "pcs", "optionnel": False},
                ],
                "etapes": [
                    {"ordre": 1, "description": "Laver et couper les légumes", "duree": 8},
                    {"ordre": 2, "description": "Assaisonner", "duree": 2},
                ],
            },
        ]

        return fallback[:count]

    # ===================================
    # PROMPTS
    # ===================================

    def _build_system_prompt(self, version_type: str) -> str:
        """Prompt système ultra-strict"""
        base = (
            "Tu es un assistant JSON. Tu génères UNIQUEMENT du JSON valide.\n"
            "RÈGLES ABSOLUES:\n"
            "1. Commence DIRECTEMENT par {\n"
            "2. Termine DIRECTEMENT par }\n"
            "3. Utilise UNIQUEMENT des doubles guillemets\n"
            "4. Pas de markdown (```json)\n"
            "5. Pas de texte avant/après le JSON\n"
            "6. Échappe les apostrophes avec \\'\n\n"
            "Contexte: Chef cuisinier français expert."
        )

        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base += "\n\nADAPTATION BÉBÉ: 6-18 mois, sans sel/sucre ajouté, sans miel."
        elif version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base += "\n\nBATCH COOKING: Portions multiples, étapes parallèles."

        return base

    def _build_user_prompt(self, count: int, filters: Dict, version_type: str) -> str:
        """Prompt utilisateur avec critères"""
        parts = [f"Génère {count} recette(s) française(s)"]

        if filters.get("saison"):
            parts.append(f"de saison {filters['saison']}")
        if filters.get("is_quick"):
            parts.append("rapides (<30min)")
        if filters.get("is_balanced"):
            parts.append("équilibrées")
        if filters.get("type_repas"):
            parts.append(f"pour le {filters['type_repas']}")
        if filters.get("ingredients"):
            ings = ", ".join(filters["ingredients"][:5])
            parts.append(f"avec: {ings}")

        prompt = " ".join(parts) + ".\n\n"
        prompt += self._get_json_schema(version_type)
        prompt += "\n\n⚠️ UNIQUEMENT LE JSON, RIEN D'AUTRE !"

        return prompt

    def _get_json_schema(self, version_type: str) -> str:
        """Schéma JSON exemple"""
        schema = """{
  "recettes": [
    {
      "nom": "Gratin dauphinois",
      "description": "Gratin crémeux aux pommes de terre",
      "temps_preparation": 20,
      "temps_cuisson": 60,
      "portions": 6,
      "difficulte": "moyen",
      "type_repas": "dîner",
      "saison": "toute_année",
      "categorie": "Français",
      "est_rapide": false,
      "est_equilibre": true,
      "compatible_bebe": false,
      "compatible_batch": true,
      "congelable": true,
      "ingredients": [
        {"nom": "Pommes de terre", "quantite": 1.0, "unite": "kg", "optionnel": false},
        {"nom": "Crème fraîche", "quantite": 300, "unite": "mL", "optionnel": false}
      ],
      "etapes": [
        {"ordre": 1, "description": "Éplucher et trancher les pommes de terre", "duree": 15},
        {"ordre": 2, "description": "Disposer en couches dans un plat", "duree": 5},
        {"ordre": 3, "description": "Verser la crème et enfourner 60min à 180°C", "duree": 60}
      ]
    }
  ]
}"""

        if version_type == TypeVersionRecetteEnum.BEBE.value:
            schema = schema.replace(
                "]",
                """],
      "version_bebe": {
        "instructions_modifiees": "Mixer finement après cuisson",
        "notes_bebe": "À partir de 8 mois, texture lisse"
      }""",
            )

        return f"RÉPONDS AVEC CE FORMAT:\n{schema}"

    # ===================================
    # GÉNÉRATION IMAGE
    # ===================================

    def generate_image_url(self, recipe_name: str, description: str) -> str:
        """Génère URL d'image (Unsplash fallback)"""
        safe_name = recipe_name.replace(" ", ",").replace("'", "")
        return f"https://source.unsplash.com/400x300/?{safe_name},food,recipe,cooking"


# ===================================
# INSTANCE GLOBALE
# ===================================

ai_recette_service = AIRecetteService()
