"""
Schémas Pydantic pour les suggestions IA.

Modèles de réponse pour les endpoints de suggestions de recettes et planning.
"""

from typing import Any

from pydantic import BaseModel, Field


class SuggestionRecetteItem(BaseModel):
    """Un item de suggestion de recette."""

    nom: str = Field(description="Nom de la recette suggérée")
    description: str | None = Field(None, description="Description courte")
    temps_preparation: int | None = Field(None, description="Temps de préparation en minutes")


class SuggestionsRecettesResponse(BaseModel):
    """Réponse pour les suggestions de recettes IA."""

    suggestions: list[Any] = Field(description="Liste des recettes suggérées")
    contexte: str = Field(description="Contexte utilisé pour la génération")
    nombre: int = Field(description="Nombre de suggestions demandées")


class SuggestionsPlanningResponse(BaseModel):
    """Réponse pour les suggestions de planning IA."""

    planning: dict[str, Any] = Field(description="Planning structuré par jour")
    jours: int = Field(description="Nombre de jours planifiés")
    personnes: int = Field(description="Nombre de personnes")
