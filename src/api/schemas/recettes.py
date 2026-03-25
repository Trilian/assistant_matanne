"""
Schémas Pydantic pour les recettes.
"""

from pydantic import BaseModel, Field, field_validator

from .base import IdentifiedResponse, NomValidatorMixin


# ═══════════════════════════════════════════════════════════
# SOUS-SCHÉMAS INGRÉDIENTS & ÉTAPES
# ═══════════════════════════════════════════════════════════


class IngredientItem(BaseModel):
    """Un ingrédient dans une recette (entrée)."""

    nom: str = Field(..., min_length=1)
    quantite: float = Field(1, ge=0)
    unite: str = "pièce"


class IngredientResponse(BaseModel):
    """Un ingrédient dans une recette (sortie)."""

    id: int
    nom: str
    quantite: float
    unite: str
    optionnel: bool = False

    model_config = {"from_attributes": True}


class EtapeResponse(BaseModel):
    """Une étape de recette (sortie)."""

    id: int
    ordre: int
    description: str
    titre: str | None = None
    duree: int | None = None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════
# RECETTES
# ═══════════════════════════════════════════════════════════


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

    ingredients: list[IngredientItem] = Field(default_factory=list)
    instructions: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @field_validator("instructions", mode="before")
    @classmethod
    def normaliser_instructions(cls, v: str | list[str] | None) -> list[str]:
        """Accepte une chaîne (split par lignes) ou une liste."""
        if v is None:
            return []
        if isinstance(v, str):
            return [line.strip() for line in v.splitlines() if line.strip()]
        return v

    @field_validator("ingredients", mode="before")
    @classmethod
    def normaliser_ingredients(cls, v: list | None) -> list:
        """Accepte les dicts bruts et les convertit en IngredientItem."""
        if v is None:
            return []
        return v


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
    ingredients: list[IngredientItem] | None = None
    instructions: list[str] | None = None
    tags: list[str] | None = None

    @field_validator("instructions", mode="before")
    @classmethod
    def normaliser_instructions(cls, v: str | list[str] | None) -> list[str] | None:
        """Accepte une chaîne (split par lignes) ou une liste."""
        if v is None:
            return None
        if isinstance(v, str):
            return [line.strip() for line in v.splitlines() if line.strip()]
        return v


class RecetteResponse(RecetteBase, IdentifiedResponse):
    """Schéma de réponse pour une recette."""

    ingredients: list[IngredientResponse] = Field(default_factory=list)
    etapes: list[EtapeResponse] = Field(default_factory=list)
    est_favori: bool = False
    note_moyenne: float | None = None
    url_source: str | None = None
