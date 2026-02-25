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

from src.api.dependencies import get_current_user
from src.api.schemas.push import (
    PushStatusResponse,
    PushSubscriptionRequest,
    PushSubscriptionResponse,
    PushUnsubscribeRequest,
)
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/push",
    tags=["Notifications Push"],
)


# ═══════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════


@router.post(
    "/subscribe",
    response_model=PushSubscriptionResponse,
    summary="Enregistrer un abonnement push",
    description="Enregistre un nouvel abonnement Web Push pour recevoir des notifications.",
)
@gerer_exception_api
async def souscrire_push(
    request: PushSubscriptionRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Enregistre un abonnement push pour l'utilisateur authentifié.

    Le frontend doit envoyer l'objet AbonnementPush.toJSON() obtenu
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

        user_id = current_user["id"]
        subscription = service.sauvegarder_abonnement(user_id, subscription_info)

        logger.info(f"✅ Abonnement push enregistré pour {user_id}")

        return PushSubscriptionResponse(
            success=True,
            message="Abonnement push enregistré avec succès",
            user_id=user_id,
            endpoint=subscription.endpoint,
        )

    except Exception as e:
        logger.error(f"Erreur lors de l'enregistrement push: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'enregistrement de l'abonnement push.",
        )


@router.delete(
    "/unsubscribe",
    response_model=PushSubscriptionResponse,
    summary="Supprimer un abonnement push",
    description="Supprime un abonnement Web Push existant.",
)
@gerer_exception_api
async def desabonner_push(
    request: PushUnsubscribeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Supprime un abonnement push pour l'utilisateur authentifié.
    """
    try:
        from src.services.core.notifications.notif_web import get_push_notification_service

        service = get_push_notification_service()
        user_id = current_user["id"]

        service.supprimer_abonnement(user_id, request.endpoint)

        logger.info(f"Abonnement push supprimé pour {user_id}")

        return PushSubscriptionResponse(
            success=True,
            message="Abonnement push supprimé",
            user_id=user_id,
            endpoint=request.endpoint,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la suppression push: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression de l'abonnement push.",
        )


@router.get(
    "/status",
    response_model=PushStatusResponse,
    summary="Statut des notifications push",
    description="Retourne le statut des notifications push pour l'utilisateur.",
)
@gerer_exception_api
async def obtenir_statut_push(
    current_user: dict = Depends(get_current_user),
):
    """
    Retourne le statut des notifications push pour l'utilisateur authentifié.
    """
    try:
        from src.services.core.notifications.notif_web import get_push_notification_service

        service = get_push_notification_service()
        user_id = current_user["id"]

        subscriptions = service.obtenir_abonnements_utilisateur(user_id)
        preferences = service.obtenir_preferences(user_id)

        return PushStatusResponse(
            has_subscriptions=len(subscriptions) > 0,
            subscription_count=len(subscriptions),
            notifications_enabled=preferences.global_enabled if preferences else True,
        )

    except Exception as e:
        logger.error(f"Erreur lors de la récupération du statut push: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération du statut des notifications.",
        )
