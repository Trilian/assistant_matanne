"""
Service IA Recettes OPTIMISÉ
Utilise AIJsonParser + Cache

"""
import streamlit as st
import httpx
import logging
from typing import List, Dict, Optional
from pydantic import BaseModel, Field, validator

from src.core.models import TypeVersionRecetteEnum
from src.core.ai_json_parser import AIJsonParser, parse_list_response
from src.core.cache import Cache, RateLimit  # ✅ CORRIGÉ
from src.core.exceptions import AIServiceError, RateLimitError, handle_errors

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# SCHÉMAS PYDANTIC (inchangés)
# ═══════════════════════════════════════════════════════════════

class IngredientAI(BaseModel):
    nom: str = Field(..., min_length=2, max_length=200)
    quantite: float = Field(..., gt=0, le=10000)
    unite: str = Field(..., min_length=1, max_length=50)
    optionnel: bool = False

    @validator("nom")
    def clean_nom(cls, v):
        return v.replace("'", "'").strip()

    @validator("quantite")
    def round_qty(cls, v):
        return round(v, 2)

class EtapeAI(BaseModel):
    ordre: int = Field(..., ge=1, le=50)
    description: str = Field(..., min_length=10, max_length=1000)
    duree: Optional[int] = Field(None, ge=0, le=300)

    @validator("description")
    def clean_desc(cls, v):
        return v.replace("'", "'").strip()

class RecetteAI(BaseModel):
    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(..., gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    type_repas: str = Field("dîner")
    saison: str = Field("toute_année")
    categorie: Optional[str] = None

    est_rapide: bool = False
    est_equilibre: bool = True
    compatible_bebe: bool = False
    compatible_batch: bool = False
    congelable: bool = False

    ingredients: List[IngredientAI] = Field(..., min_items=1)
    etapes: List[EtapeAI] = Field(..., min_items=1)

    @validator("est_rapide", always=True)
    def auto_rapide(cls, v, values):
        prep = values.get("temps_preparation", 0)
        cuisson = values.get("temps_cuisson", 0)
        return (prep + cuisson) < 30

# ═══════════════════════════════════════════════════════════════
# SERVICE IA OPTIMISÉ
# ═══════════════════════════════════════════════════════════════

class AIRecetteService:
    """
    Service de génération de recettes

    ✅ Utilise AIJsonParser (pas de parsing manuel)
    ✅ Utilise Cache multi-niveau
    ✅ Gestion d'erreurs avec decorators
    """

    def __init__(self, api_key: Optional[str] = None):
        try:
            self.api_key = api_key or st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 60
            logger.info("✅ AIRecetteService initialisé")
        except KeyError:
            raise AIServiceError(
                "Clé API Mistral manquante",
                user_message="Configuration IA manquante"
            )

    # ═══════════════════════════════════════════════════════════════
    # APPEL API AVEC CACHE
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=1800, key="mistral_api_call")  # ✅ CORRIGÉ
    async def _call_mistral_cached(
            self,
            prompt: str,
            system_prompt: str = "",
            temperature: float = 0.7,
            max_tokens: int = 2000
    ) -> str:
        """
        Appel API avec cache intelligent multi-niveau

        ✅ Cache mémoire (instantané)
        ✅ Cache session (persiste reruns)
        ✅ Cache fichier (persiste redémarrages)
        """
        # Vérifier rate limit
        can_call, error_msg = RateLimit.can_call()  # ✅ CORRIGÉ
        if not can_call:
            raise RateLimitError(error_msg, user_message=error_msg)

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

                # Enregistrer l'appel
                RateLimit.record_call()  # ✅ CORRIGÉ

                logger.info(f"✅ Réponse reçue ({len(content)} chars)")
                return content

        except httpx.HTTPError as e:
            logger.error(f"❌ Erreur HTTP: {e}")
            raise AIServiceError(
                f"Erreur API Mistral: {str(e)}",
                user_message="L'IA est temporairement indisponible"
            )
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            raise AIServiceError(
                f"Erreur appel IA: {str(e)}",
                user_message="Erreur lors de l'appel IA"
            )

    # ═══════════════════════════════════════════════════════════════
    # GÉNÉRATION RECETTES
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    async def generate_recipes(
            self,
            count: int,
            filters: Dict,
            version_type: str = TypeVersionRecetteEnum.STANDARD.value
    ) -> List[Dict]:
        """
        Génère des recettes avec parsing robuste

        ✅ Utilise AIJsonParser (pas de parsing manuel)
        ✅ Fallback automatique si échec
        ✅ Cache intelligent
        """
        try:
            # Construire prompts
            system_prompt = self._build_system_prompt(version_type)
            user_prompt = self._build_user_prompt(count, filters, version_type)

            logger.info(f"🤖 Génération de {count} recette(s)")

            # Appeler l'IA (avec cache)
            response = await self._call_mistral_cached(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            # ✅ Parser avec AIJsonParser (robuste)
            recettes = parse_list_response(
                response,
                RecetteAI,
                list_key="recettes",
                fallback_items=self._get_fallback_recipes(count)
            )

            # Convertir en dicts
            result = [r.dict() for r in recettes[:count]]

            # Ajouter images
            for recipe in result:
                recipe["url_image"] = self.generate_image_url(
                    recipe["nom"],
                    recipe["description"]
                )

            logger.info(f"✅ {len(result)} recette(s) générée(s)")
            return result

        except Exception as e:
            logger.error(f"❌ Erreur génération: {e}")
            raise AIServiceError(
                f"Échec génération: {str(e)}",
                user_message="Impossible de générer les recettes"
            )

    # ═══════════════════════════════════════════════════════════════
    # PROMPTS (inchangés)
    # ═══════════════════════════════════════════════════════════════

    def _build_system_prompt(self, version_type: str) -> str:
        """Prompt système ultra-strict"""
        base = (
            "Tu es un assistant JSON. Tu génères UNIQUEMENT du JSON valide.\n"
            "RÈGLES ABSOLUES:\n"
            "1. Commence DIRECTEMENT par {\n"
            "2. Termine DIRECTEMENT par }\n"
            "3. Utilise UNIQUEMENT des doubles guillemets\n"
            "4. Pas de markdown (```json)\n"
            "5. Pas de texte avant/après le JSON\n\n"
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
        prompt += self._get_json_schema()
        prompt += "\n\n⚠️ UNIQUEMENT LE JSON, RIEN D'AUTRE !"

        return prompt

    def _get_json_schema(self) -> str:
        """Schéma JSON exemple"""
        return """{
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

    # ═══════════════════════════════════════════════════════════════
    # FALLBACK
    # ═══════════════════════════════════════════════════════════════

    def _get_fallback_recipes(self, count: int) -> List[Dict]:
        """Recettes de fallback si IA échoue"""
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
            }
        ]

        return fallback[:count]

    # ═══════════════════════════════════════════════════════════════
    # GÉNÉRATION IMAGE
    # ═══════════════════════════════════════════════════════════════

    def generate_image_url(self, recipe_name: str, description: str) -> str:
        """Génère URL d'image (Unsplash)"""
        safe_name = recipe_name.replace(" ", ",").replace("'", "")
        return f"https://source.unsplash.com/400x300/?{safe_name},food,recipe,cooking"

# Instance globale
ai_recette_service = AIRecetteService()