"""
Schémas Pydantic pour les webhooks sortants.

Validation et sérialisation des données webhook pour l'API REST.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl


class WebhookCreate(BaseModel):
    """Données pour créer un webhook."""

    url: HttpUrl = Field(description="URL de destination (recevra les POST)")
    evenements: list[str] = Field(
        description="Patterns d'événements à écouter (ex: ['recette.*', 'courses.generees'])",
        min_length=1,
    )
    description: str | None = Field(None, description="Description libre du webhook")

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://hooks.slack.com/services/xxx",
                "evenements": ["recette.*", "courses.generees"],
                "description": "Notification Slack quand une recette est planifiée",
            }
        }
    }


class WebhookUpdate(BaseModel):
    """Données pour modifier un webhook (tous optionnels)."""

    url: HttpUrl | None = Field(None, description="Nouvelle URL de destination")
    evenements: list[str] | None = Field(None, description="Nouveaux patterns d'événements")
    actif: bool | None = Field(None, description="Activer/désactiver le webhook")
    description: str | None = Field(None, description="Nouvelle description")


class WebhookResponse(BaseModel):
    """Webhook en lecture."""

    id: int
    url: str
    evenements: list[str]
    secret: str = Field(description="Clé HMAC-SHA256 (affichée uniquement à la création)")
    actif: bool
    description: str | None = None
    derniere_livraison: datetime | None = None
    nb_echecs_consecutifs: int = 0
    cree_le: datetime | None = None
    modifie_le: datetime | None = None

    model_config = {"from_attributes": True}


class WebhookListResponse(BaseModel):
    """Liste de webhooks."""

    items: list[WebhookResponse]
    total: int


class WebhookTestResponse(BaseModel):
    """Résultat d'un test de webhook."""

    success: bool
    status_code: int | None = Field(None, description="Code HTTP retourné par le destinataire")
    response_time_ms: float | None = Field(None, description="Temps de réponse en ms")
    error: str | None = Field(None, description="Message d'erreur si échec")
