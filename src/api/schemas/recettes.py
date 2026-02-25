"""
Schémas Pydantic pour les recettes.
"""

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


class RecettePatch(BaseModel):
    """Schéma pour mise à jour partielle (PATCH) d'une recette.

    Tous les champs sont optionnels. Seuls les champs fournis
    seront modifiés, les autres restent inchangés.

    Example:
        ```json
        {"nom": "Nouveau nom", "temps_cuisson": 45}
        ```
    """

    nom: str | None = None
    description: str | None = None
    temps_preparation: int | None = Field(None, description="Minutes", ge=0)
    temps_cuisson: int | None = Field(None, description="Minutes", ge=0)
    portions: int | None = Field(None, ge=1)
    difficulte: str | None = None
    categorie: str | None = None
    ingredients: list[dict] | None = None
    instructions: list[str] | None = None
    tags: list[str] | None = None


class RecetteResponse(RecetteBase, IdentifiedResponse):
    """Schéma de réponse pour une recette."""

    pass
