"""Schémas de validation pour l'inventaire."""

from datetime import date

from pydantic import BaseModel, Field, field_validator

from ...constants import (
    MAX_LENGTH_MEDIUM,
    MAX_LENGTH_SHORT,
    MAX_QUANTITE,
)
from ._helpers import nettoyer_texte


class ArticleInventaireInput(BaseModel):
    """
    Validation d'un article inventaire.

    Attributes:
        nom: Nom de l'article
        categorie: Catégorie
        quantite: Quantité en stock
        unite: Unité de mesure
        quantite_min: Seuil minimal
        emplacement: Lieu de stockage (optionnel)
        date_peremption: Date de péremption (optionnelle)
    """

    nom: str = Field(..., min_length=2, max_length=MAX_LENGTH_MEDIUM)
    categorie: str = Field(..., min_length=2, max_length=MAX_LENGTH_SHORT)
    quantite: float = Field(..., ge=0, le=MAX_QUANTITE)
    unite: str = Field(..., min_length=1, max_length=50)
    quantite_min: float = Field(..., ge=0, le=1000)
    emplacement: str | None = None
    date_peremption: date | None = None

    @field_validator("nom", "categorie")
    @classmethod
    def nettoyer_chaines(cls, v):
        return nettoyer_texte(v) if v else v


class IngredientStockInput(BaseModel):
    """
    Input pour ajouter/modifier un article en inventaire.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    quantite: float = Field(..., ge=0.01)
    unite: str = Field(..., min_length=1, max_length=50)
    date_expiration: date | None = Field(None, description="Date d'expiration")
    localisation: str | None = Field(None, max_length=200)
    prix_unitaire: float | None = Field(None, ge=0)

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("localisation")
    @classmethod
    def nettoyer_localisation(cls, v: str | None) -> str | None:
        if v:
            return v.strip().capitalize()
        return None


# Schéma dict-based pour formulaires simples
SCHEMA_INVENTAIRE = {
    "nom": {"type": "string", "max_length": MAX_LENGTH_MEDIUM, "required": True, "label": "Nom"},
    "categorie": {
        "type": "string",
        "max_length": MAX_LENGTH_SHORT,
        "required": True,
        "label": "Catégorie",
    },
    "quantite": {
        "type": "number",
        "min": 0,
        "max": MAX_QUANTITE,
        "required": True,
        "label": "Quantité",
    },
    "unite": {"type": "string", "max_length": 50, "required": True, "label": "Unité"},
    "quantite_min": {"type": "number", "min": 0, "max": 1000, "label": "Seuil"},
    "emplacement": {"type": "string", "max_length": MAX_LENGTH_SHORT, "label": "Emplacement"},
    "date_peremption": {"type": "date", "label": "Date péremption"},
}
