"""
Service Photo Frigo — Analyse photo du frigo → suggestions de recettes.

Utilise Pixtral (vision multimodale) pour détecter les ingrédients
visibles dans une photo du frigo et suggérer des recettes.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory
from src.services.integrations.multimodal import MultiModalAIService

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class IngredientDetecte(BaseModel):
    """Ingrédient détecté dans la photo du frigo."""

    nom: str = Field(description="Nom de l'ingrédient")
    quantite_estimee: str | None = Field(None, description="Quantité estimée")
    confiance: float = Field(default=0.8, ge=0, le=1, description="Score de confiance")


class RecetteSuggestion(BaseModel):
    """Recette suggérée à partir des ingrédients détectés."""

    nom: str = Field(description="Nom de la recette")
    description: str = Field(description="Description courte")
    temps_preparation: int | None = Field(None, description="Temps en minutes")
    ingredients_utilises: list[str] = Field(default_factory=list)
    ingredients_manquants: list[str] = Field(default_factory=list)


class ResultatPhotoFrigo(BaseModel):
    """Résultat complet de l'analyse photo frigo."""

    ingredients_detectes: list[IngredientDetecte] = Field(default_factory=list)
    recettes_suggerees: list[RecetteSuggestion] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


SYSTEM_PROMPT_DETECTION = """Tu es un expert en alimentation. Analyse cette photo de frigo ou d'aliments.

Identifie TOUS les ingrédients visibles (fruits, légumes, viandes, produits laitiers, condiments, etc.).
Pour chaque ingrédient, estime la quantité visible.

Réponds en JSON avec ce format exact:
{
    "ingredients": [
        {"nom": "tomates", "quantite_estimee": "4-5 pièces", "confiance": 0.95},
        {"nom": "fromage râpé", "quantite_estimee": "200g environ", "confiance": 0.8}
    ]
}

Sois exhaustif et précis. Langue: français."""

SYSTEM_PROMPT_RECETTES = """Tu es un chef cuisinier expert. À partir des ingrédients disponibles, suggère des recettes réalisables.

Privilégie:
- Les recettes utilisant un maximum d'ingrédients disponibles
- Les recettes simples et rapides
- La cuisine française et familiale

Pour chaque recette, indique les ingrédients utilisés parmi ceux disponibles
ET les ingrédients manquants (condiments basiques comme sel/poivre/huile sont considérés disponibles).

Réponds en JSON:
{
    "recettes": [
        {
            "nom": "Nom de la recette",
            "description": "Description courte et appétissante",
            "temps_preparation": 30,
            "ingredients_utilises": ["tomates", "fromage"],
            "ingredients_manquants": ["basilic frais"]
        }
    ]
}

Suggère 3 à 5 recettes maximum. Langue: français."""


class PhotoFrigoService:
    """Service d'analyse photo frigo via IA multimodale."""

    def __init__(self) -> None:
        self._multimodal: MultiModalAIService | None = None

    @property
    def multimodal(self) -> MultiModalAIService:
        if self._multimodal is None:
            from src.services.integrations.multimodal import get_multimodal_service
            self._multimodal = get_multimodal_service()
        return self._multimodal

    async def analyser_photo_frigo(self, image_bytes: bytes) -> ResultatPhotoFrigo:
        """Analyse une photo du frigo et suggère des recettes.

        1. Détecte les ingrédients dans l'image
        2. Suggère des recettes à partir des ingrédients détectés
        """
        # Étape 1 : Détection des ingrédients
        ingredients = await self._detecter_ingredients(image_bytes)

        if not ingredients:
            return ResultatPhotoFrigo()

        # Étape 2 : Suggestion de recettes
        recettes = await self._suggerer_recettes(ingredients)

        return ResultatPhotoFrigo(
            ingredients_detectes=ingredients,
            recettes_suggerees=recettes,
        )

    async def _detecter_ingredients(self, image_bytes: bytes) -> list[IngredientDetecte]:
        """Détecte les ingrédients dans une photo via IA vision."""
        image_b64 = self.multimodal._encode_image(image_bytes)

        result = await self.multimodal._call_vision_model(
            image_b64=image_b64,
            prompt="Identifie tous les ingrédients visibles dans cette photo de frigo.",
            system_prompt=SYSTEM_PROMPT_DETECTION,
        )

        if not result or not isinstance(result, dict):
            return []

        raw_ingredients = result.get("ingredients", [])
        return [
            IngredientDetecte(
                nom=ing.get("nom", ""),
                quantite_estimee=ing.get("quantite_estimee"),
                confiance=ing.get("confiance", 0.8),
            )
            for ing in raw_ingredients
            if ing.get("nom")
        ]

    async def _suggerer_recettes(
        self, ingredients: list[IngredientDetecte]
    ) -> list[RecetteSuggestion]:
        """Suggère des recettes à partir des ingrédients détectés."""
        noms = [i.nom for i in ingredients]
        prompt = f"Ingrédients disponibles : {', '.join(noms)}. Suggère des recettes."

        result = self.multimodal.call_with_json_parsing_sync(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT_RECETTES,
        )

        if not result or not isinstance(result, dict):
            return []

        raw_recettes = result.get("recettes", [])
        return [
            RecetteSuggestion(
                nom=r.get("nom", ""),
                description=r.get("description", ""),
                temps_preparation=r.get("temps_preparation"),
                ingredients_utilises=r.get("ingredients_utilises", []),
                ingredients_manquants=r.get("ingredients_manquants", []),
            )
            for r in raw_recettes
            if r.get("nom")
        ]


@service_factory("photo_frigo")
def get_photo_frigo_service() -> PhotoFrigoService:
    """Factory pour le service photo frigo."""
    return PhotoFrigoService()
