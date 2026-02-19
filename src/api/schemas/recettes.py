"""
Schémas Pydantic pour les recettes.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .base import IdentifiedResponse, NomValidatorMixin


class RecetteBase(BaseModel, NomValidatorMixin):
    """Schéma de base pour une recette."""

    nom: str
    description: str | None = None
    temps_preparation: int = Field(15, description="Minutes", ge=0)
    temps_cuisson: int = Field(0, description="Minutes", ge=0)
    portions: int = Field(4, ge=1)
    difficulte: str = "moyen"
    categorie: str | None = None


class RecetteCreate(RecetteBase):
    """Schéma pour créer une recette."""

    ingredients: list[dict] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class RecetteResponse(RecetteBase, IdentifiedResponse):
    """Schéma de réponse pour une recette."""

    pass
