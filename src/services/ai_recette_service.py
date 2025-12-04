"""
Service IA pour la génération de recettes avec Mistral
Supporte les versions standard, bébé et batch cooking
"""
import streamlit as st
import httpx
import json
import logging
from typing import List, Dict, Optional
from datetime import datetime

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
        """Appel direct à l'API Mistral via httpx"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                messages = []

                if system_prompt:
                    messages.append({
                        "role": "system",
                        "content": system_prompt
                    })

                messages.append({
                    "role": "user",
                    "content": prompt
                })

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
            raise
        except Exception as e:
            logger.error(f"Erreur appel Mistral: {e}")
            raise

    async def generate_recipes(
            self,
            count: int,
            filters: Dict,
            version_type: str = "standard"
    ) -> List[Dict]:
        """Génère des recettes avec l'API Mistral"""
        try:
            # Construire les prompts
            system_prompt = self._build_system_prompt(version_type)
            user_prompt = self._build_prompt(count, filters, version_type)

            # Appel API
            response_content = await self._call_mistral_api(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=2000
            )

            # Parser la réponse
            recipes = self._parse_response(response_content, count)
            return recipes

        except Exception as e:
            logger.error(f"Erreur génération recettes: {e}")
            raise

    def _build_system_prompt(self, version_type: str) -> str:
        """Construit le system prompt selon le type de version"""
        base = (
            "Tu es un chef cuisinier expert et nutritionniste. "
            "Tu génères des recettes précises, réalisables et équilibrées. "
            "Réponds UNIQUEMENT en JSON valide, sans commentaires, sans balises markdown."
        )

        if version_type == "baby":
            base += (
                "\n\nTu adaptes les recettes pour bébés (6-18 mois) : "
                "- Aucun sel, sucre ajouté, miel\n"
                "- Textures adaptées (purée, morceaux fondants)\n"
                "- Ingrédients sûrs et nutritifs"
            )
        elif version_type == "batch_cooking":
            base += (
                "\n\nTu optimises les recettes pour le batch cooking : "
                "- Identifie les étapes parallélisables\n"
                "- Optimise le temps total\n"
                "- Suggère des quantités pour préparer plusieurs portions"
            )

        return base

    def _build_prompt(
            self,
            count: int,
            filters: Dict,
            version_type: str
    ) -> str:
        """Construit le prompt utilisateur"""
        prompt_parts = [f"Génère {count} recette(s)"]

        # Filtres
        if filters.get("season"):
            prompt_parts.append(f"de saison ({filters['season']})")

        if filters.get("is_quick"):
            prompt_parts.append("rapides (<30 minutes)")

        if filters.get("is_balanced"):
            prompt_parts.append("équilibrées (protéines, légumes, féculents)")

        if filters.get("meal_type"):
            prompt_parts.append(f"pour le {filters['meal_type']}")

        if filters.get("ingredients"):
            ing_list = ", ".join(filters["ingredients"])
            prompt_parts.append(f"avec ces ingrédients : {ing_list}")

        if filters.get("category"):
            prompt_parts.append(f"de type {filters['category']}")

        prompt = " ".join(prompt_parts) + ".\n\n"

        # Format JSON
        prompt += self._get_json_format(version_type)

        return prompt

    def _get_json_format(self, version_type: str) -> str:
        """Retourne le format JSON attendu"""
        base_format = """
Format JSON requis (structure EXACTE) :
{
  "recipes": [
    {
      "name": "Nom de la recette",
      "description": "Description courte et appétissante (2-3 phrases)",
      "prep_time": 15,
      "cook_time": 30,
      "servings": 4,
      "difficulty": "easy",
      "meal_type": "dinner",
      "season": "all_year",
      "category": "Végétarien",
      "is_quick": true,
      "is_balanced": true,
      "is_baby_friendly": false,
      "is_batch_friendly": true,
      "is_freezable": true,
      "ingredients": [
        {
          "name": "Tomates",
          "quantity": 500,
          "unit": "g",
          "optional": false
        }
      ],
      "steps": [
        {
          "order": 1,
          "description": "Éplucher et couper les tomates",
          "duration": 5
        }
      ]
    }
  ]
}
"""

        if version_type == "baby":
            base_format += """
Ajoute pour chaque recette :
"baby_version": {
  "modified_instructions": "Mixez finement avant de servir. Ne pas ajouter de sel.",
  "baby_notes": "Introduire la tomate dès 6 mois. Surveiller les allergies.",
  "modified_ingredients": [
    {"name": "Tomates", "quantity": 100, "unit": "g", "note": "Pelées et épépinées"}
  ]
}
"""
        elif version_type == "batch_cooking":
            base_format += """
Ajoute pour chaque recette :
"batch_version": {
  "parallel_steps": ["Éplucher légumes pendant que l'eau chauffe", "Préparer la sauce pendant la cuisson"],
  "optimized_time": 45,
  "batch_tips": "Préparer x4 portions. Se congèle 3 mois."
}
"""

        return base_format

    def _parse_response(self, content: str, expected_count: int) -> List[Dict]:
        """Parse et valide la réponse JSON"""
        try:
            # Nettoyer la réponse
            cleaned = content.strip()

            # Retirer markdown si présent
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            cleaned = cleaned.strip()

            # Parser JSON
            data = json.loads(cleaned)

            if "recipes" not in data:
                raise ValueError("Clé 'recipes' manquante dans la réponse")

            recipes = data["recipes"][:expected_count]

            # Valider chaque recette
            validated = []
            for recipe in recipes:
                if self._validate_recipe(recipe):
                    validated.append(recipe)

            if not validated:
                raise ValueError("Aucune recette valide générée")

            return validated

        except json.JSONDecodeError as e:
            logger.error(f"Erreur JSON: {e}")
            logger.error(f"Contenu: {content[:500]}")
            raise ValueError("Réponse JSON invalide de l'IA")

    def _validate_recipe(self, recipe: Dict) -> bool:
        """Valide qu'une recette a les champs requis"""
        required = ["name", "description", "prep_time", "cook_time", "servings", "ingredients", "steps"]

        for field in required:
            if field not in recipe:
                logger.warning(f"Champ '{field}' manquant dans la recette '{recipe.get('name', 'inconnue')}'")
                return False

        # Valider ingrédients
        if not isinstance(recipe["ingredients"], list) or len(recipe["ingredients"]) == 0:
            logger.warning(f"Ingrédients invalides pour '{recipe['name']}'")
            return False

        # Valider étapes
        if not isinstance(recipe["steps"], list) or len(recipe["steps"]) == 0:
            logger.warning(f"Étapes invalides pour '{recipe['name']}'")
            return False

        return True

    async def generate_image_url(self, recipe_name: str, description: str) -> str:
        """Génère une URL d'image pour une recette (placeholder)"""
        # Pour l'instant, retourne une image placeholder Unsplash
        safe_name = recipe_name.replace(' ', ',')
        return f"https://source.unsplash.com/400x300/?{safe_name},food"


# Instance globale
ai_recipe_service = AIRecipeService()