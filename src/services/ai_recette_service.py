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
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatCompletionRequest, ChatMessage

logger = logging.getLogger(__name__)


class AIRecipeService:
    """Service de génération de recettes avec Mistral AI"""

    def __init__(self):
        """Initialise le service avec la clé API Mistral"""
        try:
            self.api_key = api_key or st.secrets["mistral"]["api_key"]
            self.client = MistralClient(api_key=self.api_key)
            self.model = st.secrets.get("mistral", {}).get("model", "mistral-small")
            self.base_url = "https://api.mistral.ai/v1"
            self.timeout = 30
            logger.info("✅ AIRecipeService initialisé")
        except KeyError:
            raise ValueError("Clé API Mistral manquante dans les secrets Streamlit")
            self.api_key = api_key or st.secrets["mistral"]["api_key"]


    async def generate_recipes(self, count: int, filters: Dict, version_type: str = "standard") -> List[Dict]:
        """Génère des recettes avec l'API Mistral 0.4.2"""
        try:
            # Préparation du prompt selon le type de version
            if version_type == "standard":
                prompt = self._build_standard_prompt(filters)
            elif version_type == "baby":
                prompt = self._build_baby_prompt(filters)
            elif version_type == "batch_cooking":
                prompt = self._build_batch_prompt(filters)
            else:
                raise ValueError(f"Type de version inconnu: {version_type}")

            # Appel à l'API Mistral
            chat_completion = await self.client.chat(
                model=self.model,
                messages=[
                    ChatMessage(role="user", content=prompt)
                ],
                max_tokens=2000,
                temperature=0.7
            )

            # Traitement de la réponse
            response_content = chat_completion.choices[0].message.content
            return self._parse_recipe_response(response_content, version_type)

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

    def _build_standard_prompt(self, filters: Dict) -> str:
        """Construit le prompt pour une recette standard"""
        ingredients = ", ".join(filters.get("ingredients", []))
        prompt = f"""
        Génère {filters.get('count', 1)} recette(s) {filters.get('meal_type', 'dîner')} pour {filters.get('servings', 4)} personnes.
        Saison: {filters.get('season', 'toutes saisons')}.
        Catégorie: {filters.get('category', 'sans précision')}.
        Ingrédients à utiliser: {ingredients if ingredients else 'aucun ingrédient spécifique'}.
    
        Pour chaque recette, retourne un JSON avec cette structure exacte:
        {{
            "name": "Nom de la recette",
            "description": "Description courte",
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "easy|medium|hard",
            "ingredients": [
                {{"name": "ingrédient", "quantity": 100, "unit": "g"}}
            ],
            "steps": [
                {{"order": 1, "description": "Étape 1"}}
            ],
            "is_quick": true|false,
            "is_balanced": true|false
        }}
        """
        return prompt

    def _build_baby_prompt(self, filters: Dict) -> str:
        """Construit le prompt pour une version bébé"""
        base_prompt = self._build_standard_prompt(filters)
        return f"""
        {base_prompt}
    
        Adapte cette recette pour un bébé de 6-12 mois.
        Ajoute des instructions spécifiques pour bébé et des notes de précaution.
        Retourne un JSON avec cette structure supplémentaire:
        {{
            "baby_version": {{
                "modified_instructions": "Instructions adaptées pour bébé",
                "baby_notes": "Précautions spécifiques"
            }}
        }}
        """

    def _parse_recipe_response(self, response: str, version_type: str) -> List[Dict]:
        """Parse la réponse de l'API et retourne une liste de recettes"""
        import json
        try:
            # Nettoyage de la réponse (l'API peut retourner du texte avant/après le JSON)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            clean_response = response[json_start:json_end]

            data = json.loads(clean_response)

            # Si c'est une seule recette, on la met dans une liste
            if isinstance(data, dict):
                return [data]
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Erreur parsing JSON: {e}\nRéponse reçue: {response}")
            raise

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
    """Génère une URL d'image pour une recette (mock pour l'instant)"""
    # Pour l'instant, retourne une image placeholder
    # Tu peux remplacer par un vrai service d'images plus tard
    return f"https://source.unsplash.com/400x300/?{recipe_name.replace(' ', ',')}"

    # Si tu veux utiliser un vrai service d'images, voici un exemple avec DALL-E:
    # prompt = f"Créé une image réaliste de {recipe_name}. {description}"
    # response = await self.client.images.generate(
    #     model="dall-e-3",
    #     prompt=prompt,
    #     size="1024x1024",
    #     quality="standard",
    #     n=1
    # )
    # return response.data[0].url


# Instance globale
ai_recipe_service = AIRecipeService()