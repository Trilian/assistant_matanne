"""
Schémas Pydantic pour les routes IA avancée (routing IA avancée).

Réexporte les types du service + ajoute les schémas de requête API.
"""

from typing import Any

from pydantic import BaseModel, Field

# Réexport depuis le service pour utilisation dans les routes
from src.services.ia_avancee.types import (
    AdaptationsMeteoResponse,
    AnalysePhotoMultiUsage,
    DiagnosticPlante,
    DocumentAnalyse,
    EstimationTravauxPhoto,
    IdeesCadeauxResponse,
    OptimisationRoutinesResponse,
    PlanningAdaptatif,
    PlanningVoyage,
    PredictionsPannesResponse,
    PrevisionDepenses,
    RecommandationsEnergieResponse,
    SuggestionsAchatsResponse,
    SuggestionsProactivesResponse,
)

__all__ = [
    "AdaptationsMeteoResponse",
    "AnalysePhotoMultiUsage",
    "DiagnosticPlante",
    "DocumentAnalyse",
    "EstimationTravauxPhoto",
    "IdeesCadeauxResponse",
    "OptimisationRoutinesResponse",
    "PlanningAdaptatif",
    "PlanningVoyage",
    "PredictionsPannesResponse",
    "PrevisionDepenses",
    "RecommandationsEnergieResponse",
    "SuggestionsAchatsResponse",
    "SuggestionsProactivesResponse",
    # Request schemas
    "PlanningAdaptatifRequest",
    "IdeesCadeauxRequest",
    "PlanningVoyageRequest",
    "EstimationTravauxRequest",
    "AdaptationsMeteoRequest",
]


# ═══════════════════════════════════════════════════════════
# SCHEMAS DE REQUÊTE
# ═══════════════════════════════════════════════════════════


class PlanningAdaptatifRequest(BaseModel):
    """Requête pour le planning adaptatif."""

    meteo: dict[str, Any] | None = Field(default=None, description="Données météo")
    budget_restant: float | None = Field(default=None, description="Budget restant ce mois")


class IdeesCadeauxRequest(BaseModel):
    """Requête pour les idées cadeaux."""

    nom: str = Field(description="Prénom du destinataire", max_length=50)
    age: int = Field(ge=0, le=150, description="Âge du destinataire")
    relation: str = Field(default="famille", max_length=30)
    budget_max: float = Field(default=50.0, ge=1, le=10000)
    occasion: str = Field(default="anniversaire", max_length=30)


class PlanningVoyageRequest(BaseModel):
    """Requête pour le planning voyage."""

    destination: str = Field(description="Destination du voyage", max_length=100)
    duree_jours: int = Field(default=7, ge=1, le=30)
    budget_total: float | None = Field(default=None, ge=0)
    avec_enfant: bool = Field(default=True)


class EstimationTravauxRequest(BaseModel):
    """Requête pour estimation travaux (texte seul, image via upload)."""

    description: str = Field(default="", max_length=200)


class AdaptationsMeteoRequest(BaseModel):
    """Requête pour les adaptations météo."""

    previsions_meteo: dict[str, Any] = Field(description="Prévisions météo JSON")
