"""
Schémas Pydantic pour le planning.
"""

from datetime import date as DateType
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .base import IdentifiedResponse, TypeRepasValidator


class RepasBase(BaseModel, TypeRepasValidator):
    """Schéma de base pour un repas.

    Le champ ``date`` utilise l'alias ``date_repas`` pour la sérialisation
    depuis les objets ORM (modèle ``Repas.date_repas``).  Les clients API
    peuvent envoyer le champ sous les deux noms (``date`` ou ``date_repas``)
    grâce à ``populate_by_name=True``.
    """

    model_config = ConfigDict(populate_by_name=True)

    type_repas: str
    date: DateType = Field(alias="date_repas")
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


class GenererPlanningRequest(BaseModel):
    """Paramètres pour générer un planning IA."""

    date_debut: DateType | None = Field(None, description="Début de semaine (défaut: lundi courant)")
    nb_personnes: int = Field(4, ge=1, le=20, description="Nombre de personnes")
    preferences: dict[str, Any] | None = Field(None, description="Préférences (allergies, régime, etc.)")


class RepasRapideSuggestion(BaseModel):
    """Une suggestion de repas rapide."""

    id: int
    nom: str
    description: str | None = None
    temps_total: int = 0
    categorie: str | None = None
