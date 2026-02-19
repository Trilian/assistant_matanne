"""
Schémas Pydantic pour le planning.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from .base import IdentifiedResponse, TypeRepasValidator


class RepasBase(BaseModel, TypeRepasValidator):
    """Schéma de base pour un repas."""

    type_repas: str
    date: datetime
    recette_id: int | None = None
    notes: str | None = None


class RepasCreate(RepasBase):
    """Schéma pour créer un repas."""

    pass


class RepasResponse(RepasBase, IdentifiedResponse):
    """Schéma de réponse pour un repas."""

    pass


class PlanningSemaineResponse(BaseModel):
    """Réponse du planning hebdomadaire."""

    date_debut: str
    date_fin: str
    planning: dict[str, dict[str, Any]]
