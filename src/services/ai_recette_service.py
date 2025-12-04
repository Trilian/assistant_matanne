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

    def __init__(self):
        """Initialise le service avec la clé API Mistral"""
        try:
            self.api_key = st.secrets["mistral"]["api_key"]
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 30
            logger.info("✅ AIRecipeService initialisé")
        except KeyError:
            raise ValueError("Clé API Mistral manquante dans les secrets Streamlit")

    async def generate_recipes(
            self,
            count: int = 3,
            filters: Optional[Dict] = None,
            version_type: str = "standard"
    ) -> List[Dict]:
        """
        Génère des recettes selon les filtres

        Args:
            count: Nombre de recettes à générer
            filters: Filtres (season, is_quick, is_balanced, etc.)
            version_type: standard, baby, batch_cooking

        Returns:
            Liste de recettes au format structuré
        """
        filters = filters or {}

        # Construction du prompt
        prompt = self._build_prompt(count, filters, version_type)
        system_prompt = self._build_system_prompt(version_type)

        try:
            # Appel API Mistral
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.8,
                        "max_tokens": 2000
                    }
                )

                response.raise_for_status()
                result = response.json()
                content = result["choices"][0]["message"]["content"]

                # Parse JSON
                recipes = self._parse_response(content, count)
                return recipes

        except httpx.HTTPError as e:
            logger.error(f"Erreur API Mistral: {e}")
            raise ValueError(f"Erreur API: {str(e)}")
        except Exception as e:
            logger.error(f"Erreur génération recettes: {e}")
            raise ValueError(f"Erreur: {str(e)}")

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
                "- Aucun sel, sucre ajouté, miel"
                "- Textures adaptées (purée, morceaux fondants)"
                "- Ingrédients sûrs et nutritifs"
            )
        elif version_type == "batch_cooking":
            base += (
                "\n\nTu optimises les recettes pour le batch cooking : "
                "- Identifie les étapes parallélisables"
                "- Optimise le temps total"
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
        prompt_parts = [f"Génère {count} recettes"]

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
Format JSON requis :
{
  "recipes": [
    {
      "name": "Nom de la recette",
      "description": "Description courte et appétissante (2-3 phrases)",
      "prep_time": 15,
      "cook_time": 30,
      "servings": 4,
      "difficulty": "easy|medium|hard",
      "meal_type": "breakfast|lunch|dinner|snack",
      "season": "spring|summer|fall|winter|all_year",
      "category": "Végétarien|Viande|Poisson|etc.",
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

    async def generate_image_url(self, recipe_name: str, description: str) -> Optional[str]:
        """
        Génère une URL d'image pour la recette (Unsplash API)
        Alternative gratuite à la génération d'images
        """
        try:
            # Utiliser Unsplash API pour trouver une image correspondante
            query = f"{recipe_name} food"

            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(
                    "https://api.unsplash.com/search/photos",
                    params={
                        "query": query,
                        "per_page": 1,
                        "orientation": "landscape"
                    },
                    headers={
                        "Authorization": f"Client-ID {st.secrets.get('unsplash', {}).get('access_key', '')}"
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data["results"]:
                        return data["results"][0]["urls"]["regular"]

        except Exception as e:
            logger.warning(f"Impossible de récupérer une image: {e}")

        # Fallback : URL placeholder
        return f"https://via.placeholder.com/400x300.png?text={recipe_name.replace(' ', '+')}"


# Instance globale
ai_recipe_service = AIRecipeService()