"""
Routes API pour Sprint E — Notifications enrichies.

Endpoints:
- E.4: Gérer les préférences notifications granulaires
- E.5: Consulter l'historique des notifications (centre de notifications)
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.dependencies import require_auth
from src.api.schemas import MessageResponse, ReponsePaginee
from src.api.utils import executer_async, executer_avec_session, gerer_exception_api
from src.core.db import obtenir_contexte_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


# ═══════════════════════════════════════════════════════════
# E.4: PRÉFÉRENCES NOTIFICATIONS GRANULAIRES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/preferences",
    response_model=dict[str, Any],
    summary="Récupérer les préférences notifications (E.4)",
    description="Retourne: canal_prefere, canaux_par_categorie, modules_actifs, heures_silencieuses",
)
@gerer_exception_api
async def obtenir_preferences_notifications(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Récupère les préférences notifications granulaires de l'utilisateur (E.4)."""

    def _get_prefs():
        from src.services.core.notifications.notifications_enrichies import (
            ServiceNotificationsEnrichis,
        )

        with obtenir_contexte_db() as session:
            service = ServiceNotificationsEnrichis(session)
            return service.obtenir_preferences(str(user.get("id", "")))

    return await executer_async(_get_prefs)


@router.put(
    "/preferences",
    response_model=MessageResponse,
    summary="Mettre à jour les préférences notifications (E.4)",
)
@gerer_exception_api
async def mettre_a_jour_preferences_notifications(
    body: dict[str, Any],
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Met à jour les préférences notifications granulaires (E.4)."""

    def _update_prefs():
        from src.services.core.notifications.notifications_enrichies import (
            ServiceNotificationsEnrichis,
        )

        with obtenir_contexte_db() as session:
            service = ServiceNotificationsEnrichis(session)
            succes = service.mettre_a_jour_preferences(str(user.get("id", "")), body)
            return {
                "message": "Préférences mises à jour" if succes else "Erreur mise à jour",
                "success": succes,
            }

    result = await executer_async(_update_prefs)
    return MessageResponse(message=result.get("message", "Mise à jour effectuée"))


# ═══════════════════════════════════════════════════════════
# E.5: CENTRE DE NOTIFICATIONS — HISTORIQUE
# ═══════════════════════════════════════════════════════════


@router.get(
    "/historique",
    response_model=ReponsePaginee[dict[str, Any]],
    summary="Lister l'historique des notifications (E.5)",
    description="Centre de notifications — voir les dernières notifications",
)
@gerer_exception_api
async def lister_historique_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    non_lu_seulement: bool = Query(False),
    user: dict[str, Any] = Depends(require_auth),
) -> ReponsePaginee[dict[str, Any]]:
    """Liste l'historique paginé des notifications (E.5)."""

    def _list_history():
        from src.services.core.notifications.notifications_enrichies import (
            ServiceNotificationsEnrichis,
        )

        with obtenir_contexte_db() as session:
            service = ServiceNotificationsEnrichis(session)
            offset = (page - 1) * page_size

            historique = service.lister_historique(
                user_id=str(user.get("id", "")),
                limit=page_size,
                offset=offset,
                non_lu_seulement=non_lu_seulement,
            )

            return {
                "data": historique,
                "page": page,
                "page_size": page_size,
                "total": len(historique),
            }

    result = await executer_async(_list_history)
    return ReponsePaginee[dict[str, Any]](
        data=result.get("data", []),
        page=result.get("page", 1),
        page_size=result.get("page_size", 20),
        total=result.get("total", 0),
    )


@router.post(
    "/historique/{notif_id}/marquer-lu",
    response_model=MessageResponse,
    summary="Marquer une notification comme lue (E.5)",
)
@gerer_exception_api
async def marquer_notification_lue(
    notif_id: int,
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Marque une notification comme lue (E.5)."""

    def _mark_read():
        from src.services.core.notifications.notifications_enrichies import (
            ServiceNotificationsEnrichis,
        )

        with obtenir_contexte_db() as session:
            service = ServiceNotificationsEnrichis(session)
            succes = service.marquer_comme_lu(notif_id)
            return {
                "message": "Notification marquée comme lue" if succes else "Erreur",
                "success": succes,
            }

    result = await executer_async(_mark_read)
    return MessageResponse(message=result.get("message", "Marquée comme lue"))


@router.post(
    "/historique/marquer-tous-lus",
    response_model=MessageResponse,
    summary="Marquer toutes les notifications comme lues (E.5)",
)
@gerer_exception_api
async def marquer_tous_lus(
    user: dict[str, Any] = Depends(require_auth),
) -> MessageResponse:
    """Marque toutes les notifications comme lues (E.5)."""

    def _mark_all_read():
        from src.services.core.notifications.notifications_enrichies import (
            ServiceNotificationsEnrichis,
        )

        with obtenir_contexte_db() as session:
            service = ServiceNotificationsEnrichis(session)
            succes = service.marquer_tous_lus(str(user.get("id", "")))
            return {
                "message": "Toutes les notifications marquées" if succes else "Erreur",
                "success": succes,
            }

    result = await executer_async(_mark_all_read)
    return MessageResponse(message=result.get("message", "Marquées comme lues"))


@router.get(
    "/historique/stats",
    response_model=dict[str, Any],
    summary="Statistiques notifications (E.5)",
    description="Retourne nombre non-lu, par canal, par catégorie",
)
@gerer_exception_api
async def stats_notifications(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    """Retourne des stats sur les notifications (E.5)."""

    def _get_stats():
        from src.services.core.notifications.notifications_enrichies import (
            ServiceNotificationsEnrichis,
        )

        with obtenir_contexte_db() as session:
            service = ServiceNotificationsEnrichis(session)

            # Lister tous (non-lu et lu)
            all_notifs = service.lister_historique(
                user_id=str(user.get("id", "")),
                limit=10000,  # Grande limite pour les stats
            )

            # Calculer stats
            non_lu = sum(1 for n in all_notifs if not n.get("lu"))
            par_canal = {}
            par_categorie = {}

            for notif in all_notifs:
                canal = notif.get("canal", "unknown")
                categorie = notif.get("categorie", "autres")
                par_canal[canal] = par_canal.get(canal, 0) + 1
                par_categorie[categorie] = par_categorie.get(categorie, 0) + 1

            return {
                "non_lu": non_lu,
                "total": len(all_notifs),
                "par_canal": par_canal,
                "par_categorie": par_categorie,
            }

    return await executer_async(_get_stats)
