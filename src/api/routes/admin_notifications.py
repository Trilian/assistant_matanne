"""Routes admin — Notifications (test, templates, simulation, historique, queue)."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException, Query
from sqlalchemy import text

from src.api.dependencies import require_role
from src.api.schemas.admin import (
    AdminHistoriqueNotificationsResponse,
    AdminNotificationTestAllResponse,
    AdminNotificationTestResponse,
    AdminPreviewTemplateResponse,
    AdminQueueNotificationsResponse,
    AdminSimulerNotificationResponse,
    AdminTemplatesNotificationsResponse,
)
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    _NOTIFICATION_TEMPLATES,
    NotificationSimulationRequest,
    NotificationTestAllRequest,
    NotificationTestRequest,
    _journaliser_action_admin,
    router,
)

logger = logging.getLogger(__name__)


@router.post(
    "/notifications/test",
    response_model=AdminNotificationTestResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Envoyer une notification de test",
    description="Envoie une notification sur le canal spécifié (ntfy/push/email/telegram). Nécessite le rôle admin.",
)
@gerer_exception_api
async def envoyer_notification_test(
    body: NotificationTestRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Envoie une notification de test sur le canal demandé."""
    from src.api.utils import executer_async

    def _send():
        if body.canal == "telegram":
            import asyncio

            from src.core.config import obtenir_parametres
            from src.services.integrations.telegram import envoyer_message_telegram

            parametres = obtenir_parametres()
            destinataire = body.numero_destinataire or parametres.TELEGRAM_CHAT_ID or ""
            if not destinataire:
                raise HTTPException(
                    status_code=422,
                    detail="Aucun chat Telegram de destination configuré.",
                )

            result = asyncio.run(
                envoyer_message_telegram(destinataire=destinataire, texte=body.message)
            )
            return {
                "resultats": {"telegram": result},
                "message": "Notification Telegram de test envoyée."
                if result
                else "Échec envoi Telegram.",
            }

        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        kwargs: dict[str, Any] = {"titre": body.titre}
        if body.email:
            kwargs["email"] = body.email

        resultats = dispatcher.envoyer(
            user_id=user.get("id", "admin"),
            message=body.message,
            canaux=[body.canal],
            **kwargs,
        )
        return {"resultats": resultats, "message": "Notification de test envoyée."}

    return await executer_async(_send)


@router.post(
    "/notifications/test-all",
    response_model=AdminNotificationTestAllResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Tester tous les canaux notifications",
    description="Envoie un test sur l'ensemble des canaux admin configurés.",
)
@gerer_exception_api
async def envoyer_notification_test_all(
    body: NotificationTestAllRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Envoie un test multi-canal pour valider la cascade notifications."""
    from src.api.utils import executer_async

    def _send_all() -> dict[str, Any]:
        from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

        dispatcher = get_dispatcher_notifications()
        canaux = ["ntfy", "push", "email"]
        if body.inclure_telegram:
            canaux.append("telegram")

        kwargs: dict[str, Any] = {"titre": body.titre, "strategie": "parallel"}
        if body.email:
            kwargs["email"] = body.email

        resultats = dispatcher.envoyer(
            user_id=str(user.get("id", "admin")),
            message=body.message,
            canaux=canaux,
            forcer=True,
            **kwargs,
        )
        succes = [canal for canal, ok in resultats.items() if ok]
        echecs = [canal for canal, ok in resultats.items() if not ok]
        return {
            "resultats": resultats,
            "canaux_testes": canaux,
            "succes": succes,
            "echecs": echecs,
            "message": "Test multi-canal terminé.",
        }

    result = await executer_async(_send_all)
    _journaliser_action_admin(
        action="admin.notifications.test_all",
        entite_type="notification",
        utilisateur_id=str(user.get("id", "admin")),
        details={"inclure_telegram": body.inclure_telegram},
    )
    return result


@router.get(
    "/notifications/templates",
    response_model=AdminTemplatesNotificationsResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les templates notifications admin",
    description="Retourne les templates disponibles (Telegram + Email).",
)
@gerer_exception_api
async def lister_templates_notifications(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    return {
        "status": "ok",
        "templates": _NOTIFICATION_TEMPLATES,
        "total": sum(len(v) for v in _NOTIFICATION_TEMPLATES.values()),
    }


@router.get(
    "/notifications/templates/{canal}/{template_id}/preview",
    response_model=AdminPreviewTemplateResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Prévisualiser un template de notification",
    description="Construit un rendu texte simple d'un template avec variables de démonstration.",
)
@gerer_exception_api
async def previsualiser_template_notification(
    canal: str,
    template_id: str,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    templates = _NOTIFICATION_TEMPLATES.get(canal, [])
    template = next((t for t in templates if t.get("id") == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template introuvable")

    contexte_demo = {
        "prenom": "Alex",
        "date": datetime.now().strftime("%d/%m/%Y"),
        "heure": datetime.now().strftime("%H:%M"),
        "module": "cuisine",
        "action": "Ouvrir le planning",
    }
    message = (
        f"[{template.get('label', template_id)}]\n"
        f"Bonjour {contexte_demo['prenom']},\n"
        f"Action suggérée: {contexte_demo['action']} ({contexte_demo['module']})\n"
        f"Généré le {contexte_demo['date']} à {contexte_demo['heure']}."
    )
    return {
        "status": "ok",
        "canal": canal,
        "template_id": template_id,
        "trigger": template.get("trigger"),
        "preview": message,
        "contexte_demo": contexte_demo,
    }


@router.post(
    "/notifications/simulate",
    response_model=AdminSimulerNotificationResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Simuler une notification",
    description="Simule l'envoi d'une notification template (dry-run par défaut).",
)
@gerer_exception_api
async def simuler_notification(
    body: NotificationSimulationRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    templates = _NOTIFICATION_TEMPLATES.get(body.canal, [])
    template = next((t for t in templates if t.get("id") == body.template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template introuvable")

    payload = {
        "template_id": body.template_id,
        "canal": body.canal,
        "payload": body.payload,
    }

    if body.dry_run:
        _journaliser_action_admin(
            action="admin.notifications.simulate",
            entite_type="notification",
            utilisateur_id=str(user.get("id", "admin")),
            details={"dry_run": True, **payload},
        )
        return {
            "status": "ok",
            "dry_run": True,
            "template": template,
            "message": "Simulation effectuée (aucun envoi réel).",
            "payload": payload,
        }

    from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

    dispatcher = get_dispatcher_notifications()
    message = f"[{template.get('label', body.template_id)}] Notification déclenchée depuis admin."
    resultats = dispatcher.envoyer(
        user_id=str(user.get("id", "admin")),
        message=message,
        canaux=[body.canal],
        forcer=True,
    )
    _journaliser_action_admin(
        action="admin.notifications.simulate",
        entite_type="notification",
        utilisateur_id=str(user.get("id", "admin")),
        details={"dry_run": False, "resultats": resultats, **payload},
    )
    return {
        "status": "ok",
        "dry_run": False,
        "template": template,
        "resultats": resultats,
        "payload": payload,
    }


@router.get(
    "/notifications/history",
    response_model=AdminHistoriqueNotificationsResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Historique livraison notifications",
    description="Retourne les dernières actions notifications admin (audit).",
)
@gerer_exception_api
async def historique_notifications(
    limit: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_avec_session

    with executer_avec_session() as session:
        rows = (
            session.execute(
                text(
                    """
                SELECT id, created_at, action, details
                FROM audit_logs
                WHERE action LIKE 'admin.notifications.%'
                ORDER BY created_at DESC, id DESC
                LIMIT :limit
                """
                ),
                {"limit": limit},
            )
            .mappings()
            .all()
        )

    items = [
        {
            "id": int(r["id"]),
            "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
            "action": r.get("action"),
            "details": r.get("details") or {},
        }
        for r in rows
    ]
    return {
        "items": items,
        "total": len(items),
    }


@router.get(
    "/notifications/queue",
    response_model=AdminQueueNotificationsResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister la file digest notifications",
    description="Expose les éléments en attente de digest notifications par utilisateur.",
)
@gerer_exception_api
async def lister_queue_notifications(
    user_id: str | None = Query(None, description="Filtrer par utilisateur"),
    limit: int = Query(20, ge=1, le=100),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Liste la file d'attente des digest notifications."""
    from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

    dispatcher = get_dispatcher_notifications()
    pending_users = dispatcher.lister_users_digest_pending()
    if user_id:
        pending_users = [uid for uid in pending_users if uid == user_id]

    items: list[dict[str, Any]] = []
    for uid in pending_users[:limit]:
        queue = dispatcher._digest_queue.get(uid, [])  # noqa: SLF001 - endpoint admin interne
        latest = queue[-1] if queue else {}
        items.append(
            {
                "user_id": uid,
                "taille_queue": len(queue),
                "dernier_message": latest.get("message"),
                "dernier_evenement": latest.get("type_evenement"),
                "last_updated": latest.get("created_at"),
            }
        )

    return {
        "items": items,
        "total": len(items),
        "total_users_pending": len(pending_users),
    }


@router.post(
    "/notifications/queue/{user_id}/retry",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Relancer une queue digest",
    description="Force l'envoi du digest d'un utilisateur et vide la file si succès.",
)
@gerer_exception_api
async def relancer_queue_notifications(
    user_id: str,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Relance un digest en attente pour un utilisateur."""
    from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

    dispatcher = get_dispatcher_notifications()
    resultats = dispatcher.vider_digest(user_id)
    _journaliser_action_admin(
        action="admin.notifications.queue.retry",
        entite_type="notification",
        utilisateur_id=str(user.get("id", "admin")),
        details={"target_user_id": user_id, "resultats": resultats},
    )
    return {"status": "ok", "user_id": user_id, "resultats": resultats}


@router.delete(
    "/notifications/queue/{user_id}",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Supprimer la queue digest d'un utilisateur",
    description="Vide les notifications digest en attente pour un utilisateur.",
)
@gerer_exception_api
async def supprimer_queue_notifications(
    user_id: str,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Supprime une file digest utilisateur sans envoi."""
    from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

    dispatcher = get_dispatcher_notifications()
    count = len(dispatcher._digest_queue.get(user_id, []))  # noqa: SLF001 - endpoint admin interne
    dispatcher._digest_queue[user_id] = []  # noqa: SLF001 - endpoint admin interne
    _journaliser_action_admin(
        action="admin.notifications.queue.delete",
        entite_type="notification",
        utilisateur_id=str(user.get("id", "admin")),
        details={"target_user_id": user_id, "deleted": count},
    )
    return {"status": "ok", "user_id": user_id, "deleted": count}
