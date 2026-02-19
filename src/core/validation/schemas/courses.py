"""Schémas de validation pour les courses."""

from pydantic import BaseModel, Field, field_validator

from ...constants import (
    MAX_LENGTH_MEDIUM,
    MAX_LENGTH_SHORT,
    MAX_QUANTITE,
)
from ._helpers import nettoyer_texte


class ArticleCoursesInput(BaseModel):
    """
    Validation d'un article courses.

    Attributes:
        nom: Nom de l'article
        quantite: Quantité à acheter
        unite: Unité de mesure
        priorite: Priorité d'achat
        magasin: Magasin cible (optionnel)
    """

    nom: str = Field(..., min_length=2, max_length=MAX_LENGTH_MEDIUM)
    quantite: float = Field(..., gt=0, le=MAX_QUANTITE)
    unite: str = Field(..., min_length=1, max_length=50)
    priorite: str = Field("moyenne", pattern="^(haute|moyenne|basse)$")
    magasin: str | None = None

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v):
        return nettoyer_texte(v)


# Schéma dict-based pour formulaires simples
SCHEMA_COURSES = {
    "nom": {
        "type": "string",
        "max_length": MAX_LENGTH_MEDIUM,
        "required": True,
        "label": "Article",
    },
    "quantite": {
        "type": "number",
        "min": 0.1,
        "max": MAX_QUANTITE,
        "required": True,
        "label": "Quantité",
    },
    "unite": {"type": "string", "max_length": 50, "required": True, "label": "Unité"},
    "priorite": {"type": "string", "max_length": 20, "label": "Priorité"},
    "magasin": {"type": "string", "max_length": MAX_LENGTH_SHORT, "label": "Magasin"},
}
