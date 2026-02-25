"""
Mixin de suggestions IA pour le service recettes.

Contient les méthodes de découverte/suggestion IA (sans écriture DB) :
- generer_recettes_ia : Suggestions de recettes
- generer_variantes_recette_ia : Variantes d'une recette

Ces méthodes utilisent `self` pour accéder aux méthodes héritées de
BaseAIService et RecipeAIMixin (build_recipe_context, build_json_prompt,
call_with_list_parsing_sync, build_system_prompt).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.core.decorators import avec_cache, avec_gestion_erreurs
from src.core.monitoring import chronometre

from .types import RecetteSuggestion

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ["RecettesIASuggestionsMixin"]


class RecettesIASuggestionsMixin:
    """Mixin fournissant les méthodes de suggestion IA pour les recettes.

    Doit être utilisé avec BaseAIService et RecipeAIMixin dans la classe finale.
    Accède via `self` à :
    - build_recipe_context() (RecipeAIMixin)
    - build_json_prompt() (BaseAIService)
    - build_system_prompt() (BaseAIService)
    - call_with_list_parsing_sync() (BaseAIService)
    """

    @avec_cache(
        ttl=21600,
        key_func=lambda self, type_repas, saison, difficulte, ingredients_dispo, nb_recettes: (
            f"recettes_ia_{type_repas}_{saison}_{difficulte}_{nb_recettes}_"
            f"{hash(tuple(ingredients_dispo or []))}"
        ),
    )
    @avec_gestion_erreurs(default_return=[])
    @chronometre("ia.recettes.generer", seuil_alerte_ms=10000)
    def generer_recettes_ia(
        self,
        type_repas: str,
        saison: str,
        difficulte: str = "moyen",
        ingredients_dispo: list[str] | None = None,
        nb_recettes: int = 3,
    ) -> list[RecetteSuggestion]:
        """Génère des suggestions de recettes avec l'IA.

        Uses Mistral AI to suggest recipes based on meal type, season,
        difficulty, and available ingredients. Results cached for 6 hours.

        Args:
            type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter)
            saison: Season (printemps, été, automne, hiver)
            difficulte: Difficulty level (facile, moyen, difficile)
            ingredients_dispo: List of available ingredient names
            nb_recettes: Number of suggestions to generate

        Returns:
            List of RecetteSuggestion objects, empty list on error
        """
        # Construire contexte métier
        context = self.build_recipe_context(
            filters={
                "type_repas": type_repas,
                "saison": saison,
                "difficulte": difficulte,
                "is_quick": False,
            },
            ingredients_dispo=ingredients_dispo,
            nb_recettes=nb_recettes,
        )

        # Prompt avec instructions JSON ULTRA-STRICTES
        prompt = f"""GENERATE {nb_recettes} RECIPES IN JSON FORMAT ONLY.

{context}

OUTPUT ONLY THIS JSON (no other text, no markdown, no code blocks):

{{"items": [{{"nom": "Poulet Rôti", "description": "Tender roasted chicken with herbs", "temps_preparation": 15, "temps_cuisson": 60, "portions": 4, "difficulte": "facile", "type_repas": "diner", "saison": "toute_année", "ingredients": [{{"nom": "chicken", "quantite": 1.5, "unite": "kg"}}, {{"nom": "olive oil", "quantite": 3, "unite": "tbsp"}}], "etapes": [{{"description": "Prepare chicken"}}, {{"description": "Season and roast"}}]}}]}}

RULES:
1. Return ONLY valid JSON - nothing before or after
2. Generate {nb_recettes} different recipes
3. All fields required: nom, description, temps_preparation, temps_cuisson, portions, difficulte, type_repas, saison, ingredients, etapes
4. ingredients: array of {{nom, quantite, unite}}
5. etapes: array of {{description}}
6. difficulte values: facile, moyen, difficile
7. No explanations, no text, ONLY JSON"""

        logger.info(f"🤖 Generating {nb_recettes} recipe suggestions")

        # IA call with auto rate limiting & parsing
        recettes = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=RecetteSuggestion,
            system_prompt="Return ONLY valid JSON. No text before or after JSON.",
            max_items=nb_recettes,
            temperature=0.5,
            max_tokens=4000,
        )

        logger.info(f"✅ Generated {len(recettes)} recipe suggestions")
        return recettes

    def generer_variantes_recette_ia(
        self,
        nom_recette: str,
        nb_variantes: int = 3,
    ) -> list[RecetteSuggestion]:
        """Génère plusieurs variantes d'une recette spécifique avec l'IA.

        Generates multiple variations of a specific recipe (e.g., "spaghetti bolognaise")
        with different ingredients, cooking methods, or cuisines.

        Args:
            nom_recette: Name of recipe to create variations for
            nb_variantes: Number of variations to generate (1-5)

        Returns:
            List of RecetteSuggestion objects with variations
        """
        # Build context for variations
        context = f"Créer {nb_variantes} variantes différentes et intéressantes de la recette: {nom_recette}"
        context += "\nChaque variante doit avoir une twist unique (ingrédient différent, cuisine différente, technique différente)"

        # Prompt pour générer les variantes
        prompt = self.build_json_prompt(
            context=context,
            task=f"Generate {nb_variantes} different variations of {nom_recette} recipe",
            json_schema="""{
    "items": [
        {
            "nom": "string (recipe name with variation)",
            "description": "string (what makes this variation unique)",
            "temps_preparation": "integer (minutes)",
            "temps_cuisson": "integer (minutes)",
            "portions": "integer",
            "difficulte": "string (facile|moyen|difficile)",
            "type_repas": "string (meal type)",
            "saison": "string (season)",
            "ingredients": [{"nom": "string", "quantite": "number", "unite": "string"}],
            "etapes": [{"description": "string"}]
        }
    ]
}""",
            constraints=[
                "Each variation must be significantly different from the others",
                "Include variations from different cuisines or cooking methods",
                "Each recipe must be complete with ingredients and steps",
                "Vary the ingredients while keeping the essence of the original",
                "Make sure each variation is practical and achievable",
                "Return EXACTLY this JSON structure with 'items' key containing the recipes array",
            ],
        )

        logger.info(f"🤖 Generating {nb_variantes} variations of '{nom_recette}'")

        # Call IA with auto rate limiting & parsing
        variations = self.call_with_list_parsing_sync(
            prompt=prompt,
            item_model=RecetteSuggestion,
            system_prompt=self.build_system_prompt(
                role="Creative chef and culinary expert",
                expertise=[
                    "Recipe variations and adaptations",
                    "Different cooking methods",
                    "International cuisines",
                    "Ingredient substitutions",
                    "Culinary creativity",
                ],
                rules=[
                    "Create truly different variations, not just minor changes",
                    "Suggest creative twists (fusion, different cuisine, new cooking method)",
                    "Keep recipes practical and achievable",
                    "Respect seasonality where applicable",
                ],
            ),
            max_items=nb_variantes,
        )

        logger.info(f"✅ Generated {len(variations)} variations of '{nom_recette}'")
        return variations
