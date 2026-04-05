"""
Schémas Pydantic pour l'intégration Garmin.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GarminStatusResponse(BaseModel):
    """Statut de la connexion Garmin."""

    connected: bool = False
    display_name: str | None = None
    objectif_pas: int | None = None
    objectif_calories: int | None = None


class GarminConnectUrlResponse(BaseModel):
    """URL d'autorisation Garmin OAuth."""

    authorization_url: str
    request_token: str


class GarminConnectCompleteResponse(BaseModel):
    """Réponse de finalisation de connexion Garmin."""

    connected: bool = True
    message: str = "Garmin connecté"


class GarminSyncResponse(BaseModel):
    """Résultat de la synchronisation Garmin."""

    status: str
    activities_synced: int = 0


class GarminStatsResponse(BaseModel):
    """Statistiques Garmin de l'utilisateur."""

    steps: int = 0
    calories: int = 0
    distance: float = 0.0
    date_range: str = ""


class GarminDisconnectResponse(BaseModel):
    """Réponse de déconnexion Garmin."""

    success: bool = True


class RecetteDinerItem(BaseModel):
    """Suggestion de recette pour le dîner Garmin."""

    id: int
    nom: str
    calories: int = 0
    categorie: str = ""
    temps_preparation: int | None = None


class GarminRecommandationDinerResponse(BaseModel):
    """Recommandation de dîner basée sur l'activité Garmin."""

    strategie: str = Field(description="recharge | equilibre | leger")
    calories_brulees: int = 0
    message: str = ""
    items: list[RecetteDinerItem] = Field(default_factory=list)
