"""
Routes pour les notifications push.

Endpoints:
- POST /api/v1/push/subscribe: Enregistrer un abonnement push
- DELETE /api/v1/push/unsubscribe: Supprimer un abonnement push
- GET /api/v1/push/status: Statut des notifications pour l'utilisateur
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/push",
    tags=["Notifications Push"],
)


# ═══════════════════════════════════════════════════════════
# SCHÉMAS
# ═══════════════════════════════════════════════════════════


class PushSubscriptionKeys(BaseModel):
    """Clés de l'abonnement push (Web Push)."""

    p256dh: str = Field(..., description="Clé publique ECDH P-256")
    auth: str = Field(..., description="Clé d'authentification")


class PushSubscriptionRequest(BaseModel):
    """Demande d'enregistrement d'abonnement push.

    Structure standard du PushSubscription JavaScript.
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


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post(
    "/subscribe",
    response_model=PushSubscriptionResponse,
    summary="Enregistrer un abonnement push",
    description="Enregistre un nouvel abonnement Web Push pour recevoir des notifications.",
)
async def subscribe_push(
    request: PushSubscriptionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Enregistre un abonnement push pour l'utilisateur authentifié.

    Le frontend doit envoyer l'objet PushSubscription.toJSON() obtenu
    après navigator.serviceWorker.pushManager.subscribe().
    """
    try:
        from src.services.core.notifications.notif_web import get_push_notification_service

        service = get_push_notification_service()

        subscription_info = {
            "endpoint": request.endpoint,
            "keys": {
                "p256dh": request.keys.p256dh,
                "auth": request.keys.auth,
            },
        }

        user_id = current_user["user_id"]
        subscription = service.sauvegarder_abonnement(user_id, subscription_info)

        logger.info(f"✅ Abonnement push enregistré pour {user_id}")

        return PushSubscriptionResponse(
            success=True,
            message="Abonnement push enregistré avec succès",
            user_id=user_id,
            endpoint=subscription.endpoint,
        )

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement push: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'enregistrement: {str(e)}",
        )


@router.delete(
    "/unsubscribe",
    response_model=PushSubscriptionResponse,
    summary="Supprimer un abonnement push",
    description="Supprime un abonnement Web Push existant.",
)
async def unsubscribe_push(
    request: PushUnsubscribeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Supprime un abonnement push pour l'utilisateur authentifié.
    """
    try:
        from src.services.core.notifications.notif_web import get_push_notification_service

        service = get_push_notification_service()
        user_id = current_user["user_id"]

        service.supprimer_abonnement(user_id, request.endpoint)

        logger.info(f"Abonnement push supprimé pour {user_id}")

        return PushSubscriptionResponse(
            success=True,
            message="Abonnement push supprimé",
            user_id=user_id,
            endpoint=request.endpoint,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la suppression push: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de la suppression: {str(e)}",
        )


@router.get(
    "/status",
    response_model=PushStatusResponse,
    summary="Statut des notifications push",
    description="Retourne le statut des notifications push pour l'utilisateur.",
)
async def get_push_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Retourne le statut des notifications push pour l'utilisateur authentifié.
    """
    try:
        from src.services.core.notifications.notif_web import get_push_notification_service

        service = get_push_notification_service()
        user_id = current_user["user_id"]

        subscriptions = service.obtenir_abonnements_utilisateur(user_id)
        preferences = service.obtenir_preferences(user_id)

        return PushStatusResponse(
            has_subscriptions=len(subscriptions) > 0,
            subscription_count=len(subscriptions),
            notifications_enabled=preferences.global_enabled if preferences else True,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut push: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur: {str(e)}",
        )
