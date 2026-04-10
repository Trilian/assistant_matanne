"""
Routes pour les notifications push.

Endpoints:
- POST /api/v1/push/subscribe: Enregistrer un abonnement push
- DELETE /api/v1/push/unsubscribe: Supprimer un abonnement push
- GET /api/v1/push/status: Statut des notifications pour l'utilisateur
"""

import logging
from typing import Any

from fastapi import APIRouter, Body, Depends

from src.api.dependencies import require_auth
from src.api.schemas.errors import REPONSES_AUTH
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CLÃ‰S VAPID
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.get(
    "/vapid-public-key",
    summary="ClÃ© publique VAPID",
    description="Retourne la clÃ© publique VAPID pour l'abonnement Web Push cÃ´tÃ© frontend.",
)
async def obtenir_cle_vapid_publique():
    """Retourne la clÃ© publique VAPID pour l'abonnement push navigateur.

    Le frontend doit utiliser cette clÃ© pour le `applicationServerKey`
    lors de l'appel Ã  `pushManager.subscribe()`.
    """
    from src.services.core.notifications.types import VAPID_PUBLIC_KEY

    return {"public_key": VAPID_PUBLIC_KEY}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENDPOINTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@router.post(
    "/subscribe",
    response_model=PushSubscriptionResponse,
    responses=REPONSES_AUTH,
    summary="Enregistrer un abonnement push",
    description="Enregistre un nouvel abonnement Web Push pour recevoir des notifications.",
)
@gerer_exception_api
async def souscrire_push(
    request: PushSubscriptionRequest = Body(...),
    current_user: dict = Depends(require_auth),
):
    """
    Enregistre un abonnement push pour l'utilisateur authentifiÃ©.

    Le frontend doit envoyer l'objet AbonnementPush.toJSON() obtenu
    aprÃ¨s navigator.serviceWorker.pushManager.subscribe().
    """
    from src.services.core.notifications.notif_web_core import obtenir_push_notification_service

    service = obtenir_push_notification_service()

    subscription_info = {
        "endpoint": request.endpoint,
        "keys": {
            "p256dh": request.keys.p256dh,
            "auth": request.keys.auth,
        },
    }

    user_id = current_user["id"]
    subscription = service.sauvegarder_abonnement(user_id, subscription_info)

    logger.info(f"âœ… Abonnement push enregistrÃ© pour {user_id}")

    return PushSubscriptionResponse(
        success=True,
        message="Abonnement push enregistrÃ© avec succÃ¨s",
        user_id=user_id,
        endpoint=subscription.endpoint,
    )


@router.delete(
    "/unsubscribe",
    response_model=PushSubscriptionResponse,
    responses=REPONSES_AUTH,
    summary="Supprimer un abonnement push",
    description="Supprime un abonnement Web Push existant.",
)
@gerer_exception_api
async def desabonner_push(
    request: PushUnsubscribeRequest = Body(...),
    current_user: dict = Depends(require_auth),
):
    """
    Supprime un abonnement push pour l'utilisateur authentifiÃ©.
    """
    from src.services.core.notifications.notif_web_core import obtenir_push_notification_service

    service = obtenir_push_notification_service()
    user_id = current_user["id"]

    service.supprimer_abonnement(user_id, request.endpoint)

    logger.info(f"Abonnement push supprimÃ© pour {user_id}")

    return PushSubscriptionResponse(
        success=True,
        message="Abonnement push supprimÃ©",
        user_id=user_id,
        endpoint=request.endpoint,
    )


@router.get(
    "/status",
    response_model=PushStatusResponse,
    responses=REPONSES_AUTH,
    summary="Statut des notifications push",
    description="Retourne le statut des notifications push pour l'utilisateur.",
)
@gerer_exception_api
async def obtenir_statut_push(
    current_user: dict = Depends(require_auth),
):
    """
    Retourne le statut des notifications push pour l'utilisateur authentifiÃ©.
    """
    from src.services.core.notifications.notif_web_core import obtenir_push_notification_service

    service = obtenir_push_notification_service()
    user_id = current_user["id"]

    subscriptions = service.obtenir_abonnements_utilisateur(user_id)
    preferences = service.obtenir_preferences(user_id)

    return PushStatusResponse(
        has_subscriptions=len(subscriptions) > 0,
        subscription_count=len(subscriptions),
        notifications_enabled=preferences.global_enabled if preferences else True,
    )


@router.get(
    "/rappels/evaluer",
    responses=REPONSES_AUTH,
    summary="Ã‰valuer les rappels intelligents",
    description=(
        "Analyse les donnÃ©es de l'application et retourne les rappels "
        "contextuels actifs : stocks bas, "
        "tÃ¢ches d'entretien en retard."
    ),
)
@gerer_exception_api
async def evaluer_rappels(
    current_user: dict = Depends(require_auth),
):
    """Retourne la liste consolidÃ©e des rappels intelligents."""
    from src.api.utils import executer_async
    from src.services.core.rappels_intelligents import obtenir_rappels_intelligents_service

    service = obtenir_rappels_intelligents_service()

    rappels = await executer_async(service.evaluer_rappels)

    return {"rappels": rappels, "total": len(rappels)}


@router.post(
    "/notifier-metier",
    responses=REPONSES_AUTH,
    summary="DÃ©clencher une notification push mÃ©tier",
    description=(
        "Envoie une notification push Web Push Ã  l'utilisateur authentifiÃ© "
        "depuis un Ã©vÃ©nement mÃ©tier (famille, jeux, maison). "
        "Utile pour les tests manuels et les dÃ©clenchements depuis des cron jobs."
    ),
)
@gerer_exception_api
async def notifier_metier(
    module: str = Body(..., description="Module origine : famille | jeux | maison"),
    type_evenement: str = Body(
        ..., description="Type : rappel | serie_defaites | alerte_predictive | budget"
    ),
    titre: str = Body(..., description="Titre de la notification"),
    message: str = Body(..., description="Corps de la notification"),
    url: str = Body("/", description="URL de redirection"),
    dry_run: bool = Body(False, description="Si True, vÃ©rifie sans envoyer"),
    donnees: dict[str, Any] = Body(
        default_factory=dict, description="DonnÃ©es optionnelles selon le type"
    ),
    current_user: dict = Depends(require_auth),
):
    """DÃ©clenche une notification push mÃ©tier vers l'utilisateur authentifiÃ©.

    Modules supportÃ©s:
    - famille / rappel â†’ notifier_rappel_famille
    - jeux / serie_defaites â†’ notifier_alerte_serie_jeux
    - maison / alerte_predictive â†’ notifier_alerte_predictive_maison
    - tout module / message gÃ©nÃ©rique si type inconnu
    """
    from src.api.utils import executer_async
    from src.services.core.notifications.notif_web_core import obtenir_push_notification_service

    user_id = current_user["id"]
    service = obtenir_push_notification_service()

    if dry_run:
        subscriptions = service.obtenir_abonnements_utilisateur(user_id)
        return {
            "dry_run": True,
            "user_id": user_id,
            "module": module,
            "type_evenement": type_evenement,
            "abonnements_actifs": len(subscriptions),
            "envoi_possible": len(subscriptions) > 0,
        }

    def _envoyer():
        if module == "famille" or type_evenement == "rappel":
            return service.notifier_rappel_famille(user_id, titre, message, url)
        if module == "maison" or type_evenement == "alerte_predictive":
            return service.notifier_alerte_predictive_maison(user_id, titre, message, url)
        # Fallback gÃ©nÃ©rique
        from src.services.core.notifications.types import NotificationPush, TypeNotification

        notif = NotificationPush(
            title=titre,
            body=message,
            notification_type=TypeNotification.MISE_A_JOUR_SYSTEME,
            url=url,
            tag=f"{module}_{type_evenement}",
        )
        return service.envoyer_notification(user_id, notif)

    envoye = await executer_async(_envoyer)

    logger.info(
        f"Notification mÃ©tier {'envoyÃ©e' if envoye else 'ignorÃ©e (prÃ©fÃ©rences)'} â†’ {user_id} [{module}/{type_evenement}]"
    )

    return {
        "success": bool(envoye),
        "user_id": user_id,
        "module": module,
        "type_evenement": type_evenement,
        "message": "Notification envoyÃ©e"
        if envoye
        else "IgnorÃ©e (prÃ©fÃ©rences ou pas d'abonnement)",
    }
