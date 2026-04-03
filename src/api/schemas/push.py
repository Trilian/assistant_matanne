"""
Schémas Pydantic pour les notifications push.
"""

from pydantic import BaseModel, Field


class PushSubscriptionKeys(BaseModel):
    """Clés de l'abonnement push (Web Push)."""

    p256dh: str = Field(..., description="Clé publique ECDH P-256", min_length=16, max_length=512)
    auth: str = Field(..., description="Clé d'authentification", min_length=8, max_length=256)

    model_config = {
        "json_schema_extra": {
            "example": {
                "p256dh": "BOr6SAMPLEp256dhKeyForPushSubscription123456",
                "auth": "sampleAuthKey123",
            }
        }
    }


class PushSubscriptionRequest(BaseModel):
    """Demande d'enregistrement d'abonnement push.

    Structure standard du AbonnementPush JavaScript.
    """

    endpoint: str = Field(..., description="URL de l'endpoint push", min_length=10, max_length=500)
    keys: PushSubscriptionKeys

    model_config = {
        "json_schema_extra": {
            "example": {
                "endpoint": "https://fcm.googleapis.com/fcm/send/sample-subscription-id",
                "keys": {
                    "p256dh": "BOr6SAMPLEp256dhKeyForPushSubscription123456",
                    "auth": "sampleAuthKey123",
                },
            }
        }
    }


class PushUnsubscribeRequest(BaseModel):
    """Demande de suppression d'abonnement."""

    endpoint: str = Field(..., description="URL de l'endpoint à supprimer", min_length=10, max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {"endpoint": "https://fcm.googleapis.com/fcm/send/sample-subscription-id"}
        }
    }


class PushSubscriptionResponse(BaseModel):
    """Réponse après enregistrement de l'abonnement."""

    success: bool
    message: str = Field(max_length=300)
    user_id: str = Field(max_length=100)
    endpoint: str = Field(max_length=500)

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "message": "Abonnement push enregistré avec succès.",
                "user_id": "matanne",
                "endpoint": "https://fcm.googleapis.com/fcm/send/sample-subscription-id",
            }
        }
    }


class PushStatusResponse(BaseModel):
    """Statut des notifications push pour l'utilisateur."""

    has_subscriptions: bool
    subscription_count: int
    notifications_enabled: bool

    model_config = {
        "json_schema_extra": {
            "example": {
                "has_subscriptions": True,
                "subscription_count": 2,
                "notifications_enabled": True,
            }
        }
    }
