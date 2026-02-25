"""
Schémas Pydantic pour les notifications push.
"""

from pydantic import BaseModel, Field


class PushSubscriptionKeys(BaseModel):
    """Clés de l'abonnement push (Web Push)."""

    p256dh: str = Field(..., description="Clé publique ECDH P-256")
    auth: str = Field(..., description="Clé d'authentification")


class PushSubscriptionRequest(BaseModel):
    """Demande d'enregistrement d'abonnement push.

    Structure standard du AbonnementPush JavaScript.
    """

    endpoint: str = Field(..., description="URL de l'endpoint push")
    keys: PushSubscriptionKeys


class PushUnsubscribeRequest(BaseModel):
    """Demande de suppression d'abonnement."""

    endpoint: str = Field(..., description="URL de l'endpoint à supprimer")


class PushSubscriptionResponse(BaseModel):
    """Réponse après enregistrement de l'abonnement."""

    success: bool
    message: str
    user_id: str
    endpoint: str


class PushStatusResponse(BaseModel):
    """Statut des notifications push pour l'utilisateur."""

    has_subscriptions: bool
    subscription_count: int
    notifications_enabled: bool
