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


class IngredientDetecteResponse(BaseModel):
    """Ingrédient détecté dans une photo."""

    nom: str = Field(description="Nom de l'ingrédient")
    quantite_estimee: str | None = Field(None, description="Quantité estimée")
    confiance: float = Field(description="Score de confiance 0-1")


class RecetteSuggestionResponse(BaseModel):
    """Recette suggérée à partir d'ingrédients."""

    nom: str = Field(description="Nom de la recette")
    description: str = Field(description="Description courte")
    temps_preparation: int | None = Field(None, description="Temps en minutes")
    ingredients_utilises: list[str] = Field(default_factory=list)
    ingredients_manquants: list[str] = Field(default_factory=list)


class PhotoFrigoResponse(BaseModel):
    """Réponse de l'analyse photo frigo."""

    ingredients_detectes: list[IngredientDetecteResponse] = Field(default_factory=list)
    recettes_suggerees: list[RecetteSuggestionResponse] = Field(default_factory=list)
