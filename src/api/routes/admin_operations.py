"""Routes admin — Opérations (Services, Notifications, IA, Cache, Utilisateurs)."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_auth, require_role
from src.api.schemas.admin import (
    AdminHistoriqueNotificationsResponse,
    AdminNotificationTestAllResponse,
    AdminNotificationTestResponse,
    AdminPreviewTemplateResponse,
    AdminQueueNotificationsResponse,
    AdminSanteServicesResponse,
    AdminSchemaDiffResponse,
    AdminSimulerNotificationResponse,
    AdminTemplatesNotificationsResponse,
)
from src.api.schemas.common import MessageResponse
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

from .admin_shared import (
    AdminAIConsoleRequest,
    CachePurgeRequest,
    DesactiverUtilisateurRequest,
    NotificationTestAllRequest,
    NotificationSimulationRequest,
    NotificationTestRequest,
    UserImpersonationRequest,
    UtilisateurAdminResponse,
    _NOTIFICATION_TEMPLATES,
    _admin_timestamps,
    _journaliser_action_admin,
    _verifier_limite_admin,
    router,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# SERVICES HEALTH
# ═══════════════════════════════════════════════════════════


@router.get(
    "/services/health",
    response_model=AdminSanteServicesResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Health check registre services",
    description="Vérifie l'état de santé de tous les services instanciés. Nécessite le rôle admin.",
)
@gerer_exception_api
async def sante_services(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Retourne le health check global du registre de services."""
    from src.api.utils import executer_async

    def _check():
        try:
            from src.services.core.registry import registre

            sante = registre.health_check_global()
            metriques = registre.obtenir_metriques()
            return {
                **sante,
                "metriques": metriques,
            }
        except Exception as exc:
            logger.warning("Impossible de vérifier l'état des services : %s", exc)
            return {
                "global_status": "error",
                "total_services": 0,
                "instantiated": 0,
                "healthy": 0,
                "erreurs": [str(exc)],
                "services": {},
            }

    return await executer_async(_check)


# ═══════════════════════════════════════════════════════════
# SCHÉMA SQL / DIFF
# ═══════════════════════════════════════════════════════════


@router.get(
    "/schema-diff",
    response_model=AdminSchemaDiffResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Comparer le schéma SQL attendu et la base active",
    description="Retourne un diff synthétique entre les fichiers SQL, la metadata ORM et la base configurée.",
)
@gerer_exception_api
async def obtenir_schema_diff_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Expose un diff lisible du schéma pour l'admin."""
    from src.api.utils import executer_async

    def _diff() -> dict[str, Any]:
        from src.core.db.schema_diff import generer_schema_diff

        diff = generer_schema_diff()
        _journaliser_action_admin(
            action="admin.schema.diff",
            entite_type="schema_sql",
            utilisateur_id=str(user.get("id", "admin")),
            details={
                "status": diff.get("status"),
                "missing_in_db": len(diff.get("missing_in_db") or []),
                "extra_in_db": len(diff.get("extra_in_db") or []),
                "column_differences": len(diff.get("column_differences") or []),
            },
        )
        return diff

    return await executer_async(_diff)


# ═══════════════════════════════════════════════════════════
# NOTIFICATIONS TEST
# ═══════════════════════════════════════════════════════════


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

            result = asyncio.run(envoyer_message_telegram(destinataire=destinataire, texte=body.message))
            return {
                "resultats": {"telegram": result},
                "message": "Notification Telegram de test envoyée." if result else "Échec envoi Telegram.",
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
        rows = session.execute(
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
        ).mappings().all()

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


@router.get(
    "/ia/metrics",
    responses=REPONSES_AUTH_ADMIN,
    summary="Métriques IA avancées",
    description="Retourne les métriques IA consolidées (appels, tokens, cache, coût estimé).",
)
@gerer_exception_api
async def lire_metriques_ia_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import get_metrics
    from src.core.ai import RateLimitIA
    from src.core.ai.cache import CacheIA
    from src.core.monitoring.collector import collecteur

    metrics = get_metrics()
    ai_metrics = (metrics.get("ai") or {}) if isinstance(metrics, dict) else {}
    tokens_utilises = int(ai_metrics.get("tokens_used", 0) or 0)
    cout_1k_tokens = float(os.getenv("IA_COST_EUR_1K_TOKENS", "0.002"))
    cout_estime = round((tokens_utilises / 1000.0) * cout_1k_tokens, 4)

    collecteur_ia = collecteur.filtrer_par_prefixe("ia.")
    return {
        "generated_at": datetime.now().isoformat(),
        "api": ai_metrics,
        "rate_limit": RateLimitIA.obtenir_statistiques(),
        "cache": CacheIA.obtenir_statistiques(),
        "monitoring": collecteur_ia,
        "cout_estime_eur": cout_estime,
        "cout_eur_1k_tokens": cout_1k_tokens,
    }


@router.post(
    "/ai/console",
    responses=REPONSES_AUTH_ADMIN,
    summary="Console IA admin",
    description="Exécute un prompt IA admin et retourne la réponse brute.",
)
@gerer_exception_api
async def console_ia_admin(
    body: AdminAIConsoleRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Endpoint de test prompt/réponse brute pour l'admin."""
    from src.core.ai import obtenir_client_ia

    prompt = body.prompt.strip()
    if len(prompt) < 3:
        raise HTTPException(status_code=422, detail="Le prompt doit contenir au moins 3 caractères.")

    start = time.perf_counter()
    client = obtenir_client_ia()
    reponse = await client.appeler(
        prompt=prompt,
        prompt_systeme=body.prompt_systeme,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
        utiliser_cache=body.utiliser_cache,
    )
    duration_ms = round((time.perf_counter() - start) * 1000, 2)

    _journaliser_action_admin(
        action="admin.ai.console",
        entite_type="ai",
        utilisateur_id=str(user.get("id", "admin")),
        details={"duration_ms": duration_ms},
    )
    return {
        "status": "ok",
        "duration_ms": duration_ms,
        "model": getattr(client, "modele", "unknown"),
        "response": reponse,
    }


# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════


@router.post(
    "/cache/purge",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Purger le cache",
    description="Invalide les entrées de cache correspondant au pattern. Nécessite le rôle admin.",
)
@gerer_exception_api
async def purger_cache(
    body: CachePurgeRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Invalide les entrées de cache selon le pattern fourni."""
    from src.api.utils import executer_async

    def _purge():
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            nb = cache.invalidate(pattern=body.pattern)
            _journaliser_action_admin(
                action="admin.cache.purge",
                entite_type="cache",
                utilisateur_id=str(user.get("id", "admin")),
                details={"pattern": body.pattern, "nb_invalidees": nb},
            )
            return {"status": "ok", "pattern": body.pattern, "nb_invalidees": nb, "message": "Cache purgé."}
        except Exception as e:
            logger.warning("Impossible de purger le cache : %s", e)
            return {"status": "error", "pattern": body.pattern, "message": str(e)}

    return await executer_async(_purge)


@router.post(
    "/cache/clear",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Vider entièrement le cache L1 + L3",
    description="Supprime toutes les entrées cache (L1 mémoire + L3 fichier). Nécessite le rôle admin.",
)
@gerer_exception_api
async def vider_cache(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Vide entièrement le cache multi-niveaux."""
    from src.api.utils import executer_async

    def _clear():
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            cache.clear(levels="all")
            _journaliser_action_admin(
                action="admin.cache.clear",
                entite_type="cache",
                utilisateur_id=str(user.get("id", "admin")),
                details={"niveaux": "all"},
            )
            return {"status": "ok", "message": "Cache entièrement vidé (L1 + L3)."}
        except Exception as e:
            logger.warning("Impossible de vider le cache : %s", e)
            return {"status": "error", "message": str(e)}

    return await executer_async(_clear)


@router.get(
    "/cache/stats",
    responses=REPONSES_AUTH_ADMIN,
    summary="Statistiques cache",
    description="Retourne les statistiques hits/misses du cache. Nécessite le rôle admin.",
)
@gerer_exception_api
async def stats_cache(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Retourne les statistiques du cache multi-niveaux."""
    from src.api.utils import executer_async

    def _stats():
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            if hasattr(cache, "obtenir_statistiques"):
                return cache.obtenir_statistiques()
            return {"message": "Statistiques non disponibles pour ce backend de cache."}
        except Exception as e:
            logger.warning("Impossible de lire les stats cache : %s", e)
            return {"message": str(e)}

    return await executer_async(_stats)


# ═══════════════════════════════════════════════════════════
# UTILISATEURS
# ═══════════════════════════════════════════════════════════


@router.get(
    "/users",
    response_model=list[UtilisateurAdminResponse],
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les utilisateurs",
    description="Retourne la liste des comptes utilisateurs. Nécessite le rôle admin.",
)
@gerer_exception_api
async def lister_utilisateurs(
    page: int = Query(1, ge=1),
    par_page: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> list[dict]:
    """Retourne la liste paginée des profils utilisateurs."""
    from src.api.utils import executer_async, executer_avec_session

    def _query():
        with executer_avec_session() as session:
            from src.core.models.users import ProfilUtilisateur

            offset = (page - 1) * par_page
            profils = (
                session.query(ProfilUtilisateur)
                .order_by(ProfilUtilisateur.id)
                .offset(offset)
                .limit(par_page)
                .all()
            )
            result = []
            for p in profils:
                result.append({
                    "id": str(getattr(p, "username", p.id)),
                    "email": getattr(p, "email", ""),
                    "nom": getattr(p, "nom", None) or getattr(p, "display_name", None),
                    "role": getattr(p, "role", "membre"),
                    "actif": not bool(
                        (getattr(p, "preferences_modules", None) or {}).get("compteDesactive")
                    ),
                    "cree_le": (
                        p.cree_le.isoformat()
                        if hasattr(p, "cree_le") and p.cree_le
                        else None
                    ),
                })
            return result

    return await executer_async(_query)


@router.post(
    "/users/{user_id}/disable",
    response_model=MessageResponse,
    responses=REPONSES_AUTH_ADMIN,
    summary="Désactiver un compte utilisateur",
    description="Marque le compte comme désactivé. Nécessite le rôle admin.",
)
@gerer_exception_api
async def desactiver_utilisateur(
    user_id: str,
    body: DesactiverUtilisateurRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Désactive un compte utilisateur (flag dans preferences_modules)."""
    from src.api.utils import executer_async, executer_avec_session

    def _disable():
        with executer_avec_session() as session:
            from src.core.models.users import ProfilUtilisateur

            profil = (
                session.query(ProfilUtilisateur)
                .filter(ProfilUtilisateur.username == user_id)
                .first()
            )
            if not profil:
                raise HTTPException(status_code=404, detail=f"Utilisateur '{user_id}' introuvable.")

            prefs = dict(profil.preferences_modules or {})
            prefs["compteDesactive"] = True
            if body.raison:
                prefs["raisonDesactivation"] = body.raison
            prefs["desactiveParAdmin"] = str(user.get("id", "admin"))
            prefs["desactiveLe"] = datetime.now().isoformat()
            profil.preferences_modules = prefs
            session.commit()
            return {"status": "ok", "user_id": user_id, "message": f"Compte '{user_id}' désactivé."}

    result = await executer_async(_disable)
    _journaliser_action_admin(
        action="admin.user.disable",
        entite_type="utilisateur",
        utilisateur_id=str(user.get("id", "admin")),
        details={"cible_user_id": user_id, "raison": body.raison},
    )
    return result


@router.post(
    "/users/{user_id}/impersonate",
    responses=REPONSES_AUTH_ADMIN,
    summary="Simuler un utilisateur",
    description="Génère un token temporaire pour naviguer avec le contexte d'un utilisateur cible.",
)
@gerer_exception_api
async def simuler_utilisateur(
    user_id: str,
    body: UserImpersonationRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.auth import creer_token_acces
    from src.api.utils import executer_avec_session
    from src.core.models.users import ProfilUtilisateur

    with executer_avec_session() as session:
        profil = (
            session.query(ProfilUtilisateur)
            .filter(ProfilUtilisateur.username == user_id)
            .first()
        )
        if profil is None:
            raise HTTPException(status_code=404, detail=f"Utilisateur '{user_id}' introuvable.")

        role = str(getattr(profil, "role", "membre") or "membre")
        email = str(getattr(profil, "email", "") or f"{user_id}@local")
        token = creer_token_acces(
            user_id=user_id,
            email=email,
            role=role,
            duree_heures=max(1, min(body.duree_heures, 24)),
        )

    _journaliser_action_admin(
        action="admin.user.impersonate",
        entite_type="utilisateur",
        utilisateur_id=str(user.get("id", "admin")),
        details={"cible_user_id": user_id, "duree_heures": body.duree_heures, "raison": body.raison},
    )
    return {
        "status": "ok",
        "token_type": "bearer",
        "access_token": token,
        "expires_in": max(1, min(body.duree_heures, 24)) * 3600,
        "utilisateur": {
            "id": user_id,
            "email": email,
            "role": role,
        },
    }


