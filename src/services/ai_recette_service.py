"""
Service IA pour la génération de recettes - Compatible models.py français
"""
import streamlit as st
import httpx
import base64
import json
import logging
import re
from typing import List, Dict, Optional
from src.core.models import TypeVersionRecetteEnum

logger = logging.getLogger(__name__)

class AIRecipeService:
    """Service de génération de recettes avec Mistral AI et images avec Stability AI"""

    def __init__(self, api_key: Optional[str] = None):
        try:
            self.api_key = api_key or st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small-latest")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 30
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
        base = (
            "Tu es un chef cuisinier expert et nutritionniste français. "
            "Tu génères des recettes précises, réalisables et équilibrées. "
            "Réponds UNIQUEMENT en JSON valide, sans commentaires, sans balises markdown."
        )
        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base += (
                "\n\nPour bébés (6-18 mois): pas de sel, pas de sucre ajouté, pas de miel."
            )
        elif version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base += (
                "\n\nOptimise les recettes pour le batch cooking : étapes parallélisables, portions multiples."
            )
        return base

    def _build_prompt(self, count: int, filters: Dict, version_type: str) -> str:
        parts = [f"Génère {count} recette(s) françaises"]

        if filters.get("saison"):
            parts.append(f"de saison {filters['saison']}")
        if filters.get("is_quick"):
            parts.append("rapides (<30 minutes)")
        if filters.get("is_balanced"):
            parts.append("équilibrées")
        if filters.get("type_repas"):
            parts.append(f"pour le {filters['type_repas']}")
        if filters.get("ingredients"):
            parts.append("avec : " + ", ".join(filters["ingredients"]))
        if filters.get("nom"):
            parts.append(f"similaires à '{filters['nom']}'")

        prompt = " ".join(parts) + ".\n\n"
        prompt += self._get_json_format(version_type)
        return prompt

    def _get_json_format(self, version_type: str) -> str:
        base = """
Format JSON EXACT attendu :
{
  "recettes": [
    {
      "nom": "Nom",
      "description": "Description",
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
      "compatible_batch": false,
      "congelable": true,
      "ingredients": [
        {"nom": "Tomates", "quantite": 500, "unite": "g", "optionnel": false}
      ],
      "etapes": [
        {"ordre": 1, "description": "Couper les tomates", "duree": 5}
      ]
    }
  ]
}
"""
        if version_type == TypeVersionRecetteEnum.BEBE.value:
            base += """
Chaque recette doit inclure :
"version_bebe": {
  "instructions_modifiees": "Mixez finement",
  "notes_bebe": "Dès 6 mois",
  "ingredients_modifies": []
}
"""
        if version_type == TypeVersionRecetteEnum.BATCH_COOKING.value:
            base += """
Chaque recette doit inclure :
"version_batch": {
  "etapes_paralleles": [],
  "temps_optimise": 45,
  "conseils_batch": "Préparer en lot"
}
"""
        return base

    def _parse_response(self, content: str, expected_count: int) -> List[Dict]:
        """Parse robuste"""

        try:
            cleaned = content.strip()

            # Retire les blocs markdown
            cleaned = cleaned.replace("```json", "").replace("```", "")

            # Enlève BOM éventuel
            cleaned = cleaned.lstrip("\ufeff")

            # Fix guillemets tordus
            cleaned = cleaned.replace("“", "\"").replace("”", "\"")

            # Extraction stricte du JSON le plus long
            matches = re.findall(r'\{(?:[^{}]|(?R))*\}', cleaned)
            if not matches:
                raise ValueError("Aucun JSON détecté")

            # On prend le plus long bloc JSON (celui qui a le plus de chance d’être complet)
            json_str = max(matches, key=len)

            data = json.loads(json_str)

            # Cas standard
            if "recettes" in data:
                recettes = data["recettes"]
            else:
                raise ValueError("Champ 'recettes' manquant")

            recettes = recettes[:expected_count]

            validated = [r for r in recettes if self._validate_recipe(r)]
            if not validated:
                raise ValueError("Aucune recette valide trouvée")

            return validated

        except Exception as e:
            logger.error(f"Erreur parsing JSON: {e}\nRéponse brute:\n{content[:1000]}")
            raise ValueError(f"Réponse JSON invalide. Détails: {str(e)}")

    def _validate_recipe(self, recette: Dict) -> bool:
        required = ["nom", "description", "temps_preparation", "temps_cuisson",
                    "portions", "ingredients", "etapes"]

        for f in required:
            if f not in recette:
                logger.warning(f"Champ manquant : {f}")
                return False

        if not isinstance(recette["ingredients"], list) or not recette["ingredients"]:
            return False

        if not isinstance(recette["etapes"], list) or not recette["etapes"]:
            return False

        return True

    def generate_image_url(self, recipe_name: str, description: str) -> str:
        """Retourne un data:image propre ou fallback"""
        try:
            key = st.secrets.get("stability", {}).get("api_key")
            if not key:
                return self._fallback_image(recipe_name)

            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "text_prompts": [{"text": f"{recipe_name}, {description}, food photography"}],
                        "width": 512,
                        "height": 512,
                        "samples": 1
                    }
                )
                resp.raise_for_status()
                data = resp.json()

                b64 = data["artifacts"][0]["base64"]
                return f"data:image/png;base64,{b64}"

        except Exception as e:
            logger.error(f"Erreur génération image : {e}")
            return self._fallback_image(recipe_name)

    def _fallback_image(self, recipe_name: str) -> str:
        safe = recipe_name.replace(" ", ",")
        return f"https://source.unsplash.com/400x300/?{safe},food"


# instance globale
ai_recette_service = AIRecipeService()
