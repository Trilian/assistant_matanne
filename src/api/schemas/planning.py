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

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "type_repas": "diner",
                "date": "2026-04-06",
                "recette_id": 42,
                "notes": "Prévoir une portion Jules sans sel.",
            }
        },
    )

    type_repas: str = Field(..., max_length=30)
    date: DateType = Field(alias="date_repas")
    recette_id: int | None = None
    notes: str | None = Field(None, max_length=1000)


class RepasCreate(RepasBase):
    """Création d'un repas — hérite tous les champs de RepasBase."""


class RepasResponse(RepasBase, IdentifiedResponse):
    """Schéma de réponse pour un repas."""

    recette_nom: str | None = Field(None, max_length=200)
    plat_jules: str | None = Field(None, max_length=200)
    notes_jules: str | None = Field(None, max_length=1000)
    adaptation_auto: bool = True
    compatible_cookeo: bool = False
    compatible_monsieur_cuisine: bool = False
    compatible_airfryer: bool = False
    consomme: bool = False


class PlanningSemaineResponse(BaseModel):
    """Réponse du planning hebdomadaire."""

    date_debut: str
    date_fin: str
    planning: dict[str, dict[str, Any]]

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_debut": "2026-04-06",
                "date_fin": "2026-04-12",
                "planning": {
                    "2026-04-06": {
                        "dejeuner": {"recette_id": 12, "recette_nom": "Pâtes au pesto"},
                        "diner": {"recette_id": 42, "recette_nom": "Gratin de courgettes"},
                    }
                },
            }
        }
    }


class GenererPlanningRequest(BaseModel):
    """Paramètres pour générer un planning IA."""

    date_debut: DateType | None = Field(None, description="Début de semaine (défaut: lundi courant)")
    nb_personnes: int = Field(4, ge=1, le=20, description="Nombre de personnes")
    preferences: dict[str, Any] | None = Field(None, description="Préférences (allergies, régime, etc.)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date_debut": "2026-04-06",
                "nb_personnes": 3,
                "preferences": {"allergies": ["arachides"], "temps_max": 30, "jules": True},
            }
        }
    }


class RepasRapideSuggestion(BaseModel):
    """Une suggestion de repas rapide."""

    id: int
    nom: str = Field(max_length=200)
    description: str | None = Field(None, max_length=500)
    temps_total: int = 0
    categorie: str | None = Field(None, max_length=100)

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 9,
                "nom": "Omelette aux herbes",
                "description": "Repas prêt en moins de 15 minutes.",
                "temps_total": 12,
                "categorie": "rapide",
            }
        }
    }
