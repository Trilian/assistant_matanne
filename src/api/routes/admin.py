"""
Routes d'administration complètes.

Endpoints:
- GET  /api/v1/admin/audit-logs       : Audit logs paginés + filtrés
- GET  /api/v1/admin/audit-stats      : Statistiques d'audit
- GET  /api/v1/admin/audit-export     : Export CSV des logs
- GET  /api/v1/admin/jobs             : Liste jobs cron + statut
- POST /api/v1/admin/jobs/{id}/run    : Trigger manuel (rate-limited: 5 req/min)
- GET  /api/v1/admin/jobs/{id}/logs   : Logs dernière exécution job
- GET  /api/v1/admin/services/health  : Health check registre services
- POST /api/v1/admin/notifications/test : Test ntfy / push / email / whatsapp
- GET  /api/v1/admin/cache/stats      : Statistiques cache hit/miss
- POST /api/v1/admin/cache/clear      : Vider cache L1 + L3
- GET  /api/v1/admin/users            : Liste utilisateurs
- POST /api/v1/admin/users/{id}/disable : Désactiver un compte
- GET  /api/v1/admin/db/coherence     : Test cohérence DB rapide

Sécurité:
- Toutes les routes nécessitent le rôle admin (Depends(require_role("admin")))
- Rate limiting spécifique sur trigger jobs : 5 req/min par admin
- Audit log automatique sur toutes les actions admin mutantes
"""

from __future__ import annotations

import collections
import csv
import io
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import text

from src.api.dependencies import require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
)

# ── Rate limiting jobs triggers (5 req/min par admin) ────────────────────────
_JOB_TRIGGER_RATE_LIMIT = 5  # requêtes par minute
_job_trigger_timestamps: dict[str, collections.deque] = {}


def _verifier_limite_jobs(user_id: str) -> None:
    """Lève HTTPException 429 si l'admin dépasse 5 triggers/min."""
    now = time.time()
    window = 60.0
    q = _job_trigger_timestamps.setdefault(user_id, collections.deque())
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= _JOB_TRIGGER_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Trop de déclenchements. Maximum {_JOB_TRIGGER_RATE_LIMIT} par minute.",
        )
    q.append(now)


# ── Logs in-memory pour dernière exécution des jobs ──────────────────────────
_job_logs: dict[str, list[dict]] = {}  # job_id → list of {timestamp, status, message}
_MAX_LOGS_PAR_JOB = 20


def _ajouter_log_job(job_id: str, status: str, message: str) -> None:
    logs = _job_logs.setdefault(job_id, [])
    logs.append({"timestamp": datetime.now().isoformat(), "status": status, "message": message})
    if len(logs) > _MAX_LOGS_PAR_JOB:
        logs.pop(0)


def _journaliser_action_admin(
    action: str,
    entite_type: str,
    utilisateur_id: str,
    details: dict[str, Any] | None = None,
) -> None:
    """Enregistre l'action admin dans le journal d'audit (best-effort)."""
    try:
        from src.services.core.audit import obtenir_service_audit

        obtenir_service_audit().enregistrer_action(
            action=action,
            entite_type=entite_type,
            source="admin",
            utilisateur_id=utilisateur_id,
            details=details or {},
        )
    except Exception as exc:
        logger.warning("Impossible de journaliser l'action admin '%s': %s", action, exc)


@router.get(
    "/audit-logs",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les logs d'audit",
    description="Retourne les logs d'audit paginés avec filtres optionnels. Nécessite le rôle admin.",
)
@gerer_exception_api
async def lister_audit_logs(
    page: int = Query(1, ge=1),
    par_page: int = Query(50, ge=1, le=200),
    action: str | None = Query(None, description="Filtrer par type d'action"),
    entite_type: str | None = Query(None, description="Filtrer par type d'entité"),
    depuis: datetime | None = Query(None, description="Date de début (ISO 8601)"),
    jusqu_a: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Retourne les logs d'audit paginés avec filtres."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    resultat = service.consulter(
        action=action,
        entite_type=entite_type,
        depuis=depuis,
        jusqu_a=jusqu_a,
        limite=par_page,
        page=page,
    )

    return {
        "items": [e.model_dump() for e in resultat.entrees],
        "total": resultat.total,
        "page": resultat.page,
        "par_page": resultat.par_page,
        "pages_totales": max(1, (resultat.total + par_page - 1) // par_page),
    }


@router.get(
    "/security-logs",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les événements de sécurité",
    description="Retourne les logs de sécurité (auth, rate limiting, admin) avec filtres.",
)
@gerer_exception_api
async def lister_logs_securite(
    page: int = Query(1, ge=1),
    par_page: int = Query(20, ge=1, le=200),
    event_type: str | None = Query(None, description="Filtrer par type d'événement"),
    depuis: datetime | None = Query(None, description="Date de début (ISO 8601)"),
    jusqu_a: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Expose un flux dédié sécurité pour le dashboard admin."""
    from sqlalchemy import text

    from src.api.utils import executer_avec_session

    offset = (page - 1) * par_page
    conditions: list[str] = ["1=1"]
    params: dict[str, Any] = {"limit": par_page, "offset": offset}

    if event_type:
        conditions.append("event_type = :event_type")
        params["event_type"] = event_type
    else:
        conditions.append("(event_type LIKE 'auth.%' OR event_type LIKE 'rate_limit.%' OR event_type LIKE 'admin.%')")

    if depuis:
        conditions.append("created_at >= :depuis")
        params["depuis"] = depuis
    if jusqu_a:
        conditions.append("created_at <= :jusqu_a")
        params["jusqu_a"] = jusqu_a

    where_clause = " AND ".join(conditions)

    with executer_avec_session() as session:
        total = int(
            session.execute(
                text(f"SELECT COUNT(*) FROM logs_securite WHERE {where_clause}"),
                params,
            ).scalar()
            or 0
        )

        rows = session.execute(
            text(
                f"""
                SELECT id, created_at, event_type, user_id, ip, user_agent, details
                FROM logs_securite
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()

    items = [
        {
            "id": int(r["id"]),
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "event_type": r["event_type"],
            "user_id": r["user_id"],
            "ip": r["ip"],
            "user_agent": r["user_agent"],
            "source": "security",
            "details": r["details"] or {},
        }
        for r in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "par_page": par_page,
        "pages_totales": max(1, (total + par_page - 1) // par_page),
    }


@router.get(
    "/audit-stats",
    responses=REPONSES_AUTH_ADMIN,
    summary="Statistiques d'audit",
    description="Statistiques agrégées du journal d'audit.",
)
@gerer_exception_api
async def statistiques_audit(
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Retourne les statistiques d'audit (compteurs par action, entité, source)."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    return service.statistiques()


@router.get(
    "/audit-export",
    responses=REPONSES_AUTH_ADMIN,
    summary="Export CSV des logs",
    description="Exporte les logs d'audit au format CSV.",
)
@gerer_exception_api
async def exporter_audit_csv(
    action: str | None = Query(None),
    entite_type: str | None = Query(None),
    depuis: datetime | None = Query(None),
    jusqu_a: datetime | None = Query(None),
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Export CSV des logs d'audit."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    resultat = service.consulter(
        action=action,
        entite_type=entite_type,
        depuis=depuis,
        jusqu_a=jusqu_a,
        limite=10000,
        page=1,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Timestamp", "Action", "Source", "Utilisateur", "Entité", "ID Entité", "Détails"])

    for e in resultat.entrees:
        writer.writerow([
            e.timestamp.isoformat(),
            e.action,
            e.source,
            e.utilisateur_id or "",
            e.entite_type,
            str(e.entite_id) if e.entite_id else "",
            str(e.details) if e.details else "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=audit-logs.csv"},
    )


# ═══════════════════════════════════════════════════════════
# SCHÉMAS ADMIN ÉTENDU
# ═══════════════════════════════════════════════════════════


class JobInfoResponse(BaseModel):
    id: str
    nom: str
    schedule: str
    prochain_run: str | None
    dernier_run: str | None
    statut: str  # "actif" | "inactif"


class UtilisateurAdminResponse(BaseModel):
    id: str
    email: str
    nom: str | None
    role: str
    actif: bool
    cree_le: str | None


class NotificationTestRequest(BaseModel):
    canal: Literal["ntfy", "push", "email", "whatsapp"]
    message: str
    email: str | None = None
    titre: str = "Test Matanne"


class CachePurgeRequest(BaseModel):
    pattern: str = "*"


class DesactiverUtilisateurRequest(BaseModel):
    raison: str | None = None


class ServiceActionRunRequest(BaseModel):
    params: dict[str, Any] = {}


class FeatureFlagsUpdateRequest(BaseModel):
    flags: dict[str, bool]


class RuntimeConfigUpdateRequest(BaseModel):
    values: dict[str, Any]


class SeedDataRequest(BaseModel):
    scope: Literal["recettes_standard"] = "recettes_standard"


# ═══════════════════════════════════════════════════════════
# JOBS
# ═══════════════════════════════════════════════════════════

# Mapping ID → libellé lisible pour les jobs connus
_LABELS_JOBS: dict[str, str] = {
    "rappels_famille": "Rappels famille quotidiens (07h00)",
    "rappels_maison": "Rappels maison quotidiens (08h00)",
    "rappels_generaux": "Rappels intelligents (08h30)",
    "entretien_saisonnier": "Entretien saisonnier (lun 06h00)",
    "push_quotidien": "Push Web quotidien (09h00)",
    "enrichissement_catalogues": "Enrichissement catalogues IA (1er/mois 03h00)",
    "digest_ntfy": "Digest ntfy.sh (09h00)",
    "digest_notifications_queue": "Flush digest notifications (toutes les 2h)",
    "rappel_courses": "Rappel courses ntfy.sh (18h00)",
    "push_contextuel_soir": "Push contextuel soir (18h00)",
    "resume_hebdo": "Résumé hebdomadaire (lun 07h30)",
    "peremptions_urgentes": "Alerte péremptions urgentes (08h00)",
    "score_bienetre": "Score bien-être Jules (dim 20h00)",
    "planning_semaine_si_vide": "J-03 Vérification planning semaine suivante (dim 20h00)",
    "alertes_peremption_48h": "J-04 Alertes péremption 48h (06h00)",
    "rapport_mensuel_budget": "J-07 Rapport mensuel budget (1er/mois 08h15)",
    "score_weekend": "J-08 Score weekend (ven 17h00)",
    "controle_contrats_garanties": "J-09 Contrats & garanties (1er/mois 09h00)",
    "rapport_jardin": "J-10 Rapport jardin hebdo (mer 20h00)",
    "score_bien_etre_hebdo": "J-11 Score bien-être hebdo (dim 20h00)",
        "sync_calendrier_scolaire": "INNO-14 Sync calendrier scolaire auto (05h30)",
    "garmin_sync_matinal": "Sync Garmin automatique matinale (06h00)",
    "automations_runner": "Exécution automations (toutes les 5 min)",
    "points_famille_hebdo": "Calcul points famille hebdo (dim 20h00)",
    "sync_google_calendar": "J1 Sync Google Calendar (quotidien 23h00)",
    "alerte_stock_bas": "J3 Alerte stock bas → liste courses (07h00)",
    "archive_batches_expires": "J4 Archivage préparations batch expirées (02h00)",
    "rapport_maison_mensuel": "J5 Rapport maison mensuel (1er/mois 09h30)",
    "sync_openfoodfacts": "J6 Sync cache OpenFoodFacts (dim 03h00)",
    "prediction_courses_weekly": "JOB-1 Prédiction courses hebdo (dim 10h00)",
    "sync_jeux_budget": "JOB-2 Sync jeux -> budget (22h00)",
    "analyse_nutrition_hebdo": "JOB-3 Analyse nutrition hebdo (dim 20h00)",
    "alertes_energie": "JOB-4 Alertes énergie (07h00)",
    "nettoyage_logs": "JOB-5 Nettoyage logs > 90j (dim 04h00)",
    "check_garmin_anomalies": "JOB-6 Anomalies Garmin (08h00)",
    "resume_jardin_saisonnier": "JOB-7 Résumé jardin saisonnier (1er 08h00)",
    "expiration_documents": "JOB-8 Expiration documents (09h00)",
}

# Vues SQL explicitement autorisées (lecture seule)
_VUES_SQL_AUTORISEES: tuple[str, ...] = (
    "v_objets_a_remplacer",
    "v_temps_par_activite_30j",
    "v_budget_travaux_par_piece",
    "v_charge_semaine",
)

_NAMESPACE_FEATURE_FLAGS = "admin_feature_flags"
_NAMESPACE_RUNTIME_CONFIG = "admin_runtime_config"

_FEATURE_FLAGS_PAR_DEFAUT: dict[str, bool] = {
    "admin.service_actions_enabled": True,
    "admin.resync_enabled": True,
    "admin.seed_dev_enabled": True,
    "jeux.bankroll_page_enabled": True,
    "outils.notes_tags_ui_enabled": True,
}

_RUNTIME_CONFIG_PAR_DEFAUT: dict[str, Any] = {
    "dashboard.refresh_seconds": 300,
    "notifications.digest_interval_minutes": 120,
    "admin.max_jobs_triggers_per_min": _JOB_TRIGGER_RATE_LIMIT,
}


def _lire_namespace_persistant(
    namespace: str,
    fallback: dict[str, Any],
    *,
    user_id: str = "global",
) -> dict[str, Any]:
    """Lit une configuration persistante dans ``etats_persistants`` (best-effort)."""
    from src.api.utils import executer_avec_session

    try:
        from src.core.models import EtatPersistantDB

        with executer_avec_session() as session:
            row = (
                session.query(EtatPersistantDB)
                .filter(
                    EtatPersistantDB.namespace == namespace,
                    EtatPersistantDB.user_id == user_id,
                )
                .first()
            )
            if row and isinstance(row.data, dict):
                return {**fallback, **row.data}
    except Exception:
        logger.debug("Namespace persistant indisponible: %s", namespace, exc_info=True)
    return dict(fallback)


def _ecrire_namespace_persistant(
    namespace: str,
    values: dict[str, Any],
    *,
    user_id: str = "global",
) -> dict[str, Any]:
    """Écrit une configuration persistante dans ``etats_persistants`` (best-effort)."""
    from src.api.utils import executer_avec_session

    from src.core.models import EtatPersistantDB

    with executer_avec_session() as session:
        row = (
            session.query(EtatPersistantDB)
            .filter(
                EtatPersistantDB.namespace == namespace,
                EtatPersistantDB.user_id == user_id,
            )
            .first()
        )
        if row is None:
            row = EtatPersistantDB(namespace=namespace, user_id=user_id, data={})
            session.add(row)

        current_data = row.data if isinstance(row.data, dict) else {}
        row.data = {**current_data, **values}
        session.commit()
        return dict(row.data)


def _catalogue_actions_services() -> list[dict[str, Any]]:
    """Retourne le catalogue d'actions de services exécutables manuellement."""
    return [
        {
            "id": "dashboard.score_bien_etre.recalculer",
            "service": "score_bien_etre",
            "description": "Recalculer immédiatement le score bien-être.",
            "dry_run": False,
        },
        {
            "id": "dashboard.points_famille.recalculer",
            "service": "points_famille",
            "description": "Recalculer les points famille.",
            "dry_run": False,
        },
        {
            "id": "automations.executer",
            "service": "moteur_automations",
            "description": "Exécuter le moteur d'automations actif.",
            "dry_run": True,
        },
        {
            "id": "cache.clear_all",
            "service": "cache",
            "description": "Vider le cache multi-niveaux.",
            "dry_run": True,
        },
    ]


def _executer_action_service(
    action_id: str,
    *,
    dry_run: bool,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Exécute une action de service autorisée."""
    if action_id == "dashboard.score_bien_etre.recalculer":
        from src.services.dashboard.score_bienetre import obtenir_score_bien_etre_service

        result = obtenir_score_bien_etre_service().calculer_score()
        return {"status": "ok", "action_id": action_id, "result": result, "dry_run": False}

    if action_id == "dashboard.points_famille.recalculer":
        from src.services.dashboard.points_famille import get_points_famille_service

        result = get_points_famille_service().calculer_points()
        return {"status": "ok", "action_id": action_id, "result": result, "dry_run": False}

    if action_id == "automations.executer":
        from src.services.utilitaires.automations_engine import get_moteur_automations_service

        service = get_moteur_automations_service()
        result = (
            service.executer_automations_actives_dry_run()
            if dry_run
            else service.executer_automations_actives()
        )
        return {"status": "ok", "action_id": action_id, "result": result, "dry_run": dry_run}

    if action_id == "cache.clear_all":
        if dry_run:
            return {
                "status": "dry_run",
                "action_id": action_id,
                "dry_run": True,
                "result": {"message": "Simulation uniquement - cache non vidé."},
            }

        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        cache.clear(levels="all")
        return {
            "status": "ok",
            "action_id": action_id,
            "dry_run": False,
            "result": {"message": "Cache vidé (L1 + L3)."},
        }

    raise HTTPException(status_code=404, detail=f"Action de service inconnue: {action_id}")


def _cibles_resync() -> list[dict[str, str]]:
    """Catalogue des cibles de re-synchronisation externe."""
    return [
        {
            "id": "garmin",
            "job_id": "garmin_sync_matinal",
            "description": "Forcer la synchronisation Garmin.",
        },
        {
            "id": "google_calendar",
            "job_id": "sync_google_calendar",
            "description": "Forcer la synchronisation Google Calendar.",
        },
        {
            "id": "openfoodfacts",
            "job_id": "sync_openfoodfacts",
            "description": "Rafraîchir le cache OpenFoodFacts.",
        },
    ]


@router.get(
    "/jobs",
    response_model=list[JobInfoResponse],
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les jobs cron",
    description="Retourne tous les jobs planifiés avec leur statut. Nécessite le rôle admin.",
)
@gerer_exception_api
async def lister_jobs(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> list[dict]:
    """Liste tous les jobs APScheduler et leur prochain déclenchement."""
    try:
        from src.services.core.cron.jobs import _demarreur

        if _demarreur is None or not _demarreur._scheduler.running:
            return []

        jobs = []
        for job in _demarreur._scheduler.get_jobs():
            prochain = job.next_run_time
            jobs.append({
                "id": job.id,
                "nom": _LABELS_JOBS.get(job.id, job.name or job.id),
                "schedule": str(job.trigger),
                "prochain_run": prochain.isoformat() if prochain else None,
                "dernier_run": None,  # APScheduler ne stocke pas le dernier run
                "statut": "actif" if prochain else "inactif",
            })
        return jobs
    except Exception as e:
        logger.warning("Impossible de lister les jobs : %s", e)
        return []


@router.post(
    "/jobs/{job_id}/run",
    responses=REPONSES_AUTH_ADMIN,
    summary="Déclencher un job manuellement",
    description="Exécute immédiatement le job indiqué. Nécessite le rôle admin. Rate-limited: 5 req/min.",
)
@gerer_exception_api
async def executer_job(
    job_id: str,
    dry_run: bool = Query(False, description="Simuler le job sans exécution réelle"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Déclenche un job cron de façon asynchrone."""
    from src.api.utils import executer_async

    # Rate limiting : 5 triggers/min par admin
    _verifier_limite_jobs(str(user.get("id", "admin")))

    from src.services.core.cron.jobs import executer_job_par_id, lister_jobs_disponibles

    jobs_disponibles = lister_jobs_disponibles()
    if job_id not in jobs_disponibles:
        raise HTTPException(
            status_code=404,
            detail=f"Job '{job_id}' inconnu. Jobs disponibles : {jobs_disponibles}",
        )

    def _run():
        resultat = executer_job_par_id(
            job_id,
            dry_run=dry_run,
            source="manual",
            triggered_by_user_id=str(user.get("id", "admin")),
            relancer_exception=True,
        )
        _ajouter_log_job(
            job_id,
            "succes" if resultat.get("status") in {"ok", "dry_run"} else "erreur",
            str(resultat.get("message", "")),
        )
        return resultat

    result = await executer_async(_run)
    _journaliser_action_admin(
        action="admin.job.run",
        entite_type="job",
        utilisateur_id=str(user.get("id", "admin")),
        details={"job_id": job_id, "dry_run": dry_run},
    )
    return result


@router.get(
    "/jobs/{job_id}/logs",
    responses=REPONSES_AUTH_ADMIN,
    summary="Logs dernière exécution d'un job",
    description="Retourne l'historique des déclenchements manuels du job. Nécessite le rôle admin.",
)
@gerer_exception_api
async def logs_job(
    job_id: str,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Retourne les logs des N dernières exécutions manuelles du job."""
    from src.api.utils import executer_avec_session

    logs_persistes: list[dict[str, Any]] = []
    try:
        with executer_avec_session() as session:
            logs_rows = session.execute(
                text(
                    """
                    SELECT started_at, ended_at, duration_ms, status, error_message, output_logs
                    FROM job_executions
                    WHERE job_id = :job_id
                    ORDER BY started_at DESC
                    LIMIT 50
                    """
                ),
                {"job_id": job_id},
            ).mappings().all()
        logs_persistes = [
            {
                "timestamp": row["started_at"].isoformat() if row["started_at"] else None,
                "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
                "status": row["status"],
                "duration_ms": int(row["duration_ms"] or 0),
                "message": row["error_message"] or row["output_logs"] or "",
                "source": "db",
            }
            for row in logs_rows
        ]
    except Exception:
        logs_persistes = []

    logs_mem = _job_logs.get(job_id, [])
    logs = logs_persistes or list(reversed(logs_mem))
    return {
        "job_id": job_id,
        "nom": _LABELS_JOBS.get(job_id, job_id),
        "logs": logs,
        "total": len(logs),
    }


# ═══════════════════════════════════════════════════════════
# SERVICES HEALTH
# ═══════════════════════════════════════════════════════════


@router.get(
    "/services/health",
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
# NOTIFICATIONS TEST
# ═══════════════════════════════════════════════════════════


@router.post(
    "/notifications/test",
    responses=REPONSES_AUTH_ADMIN,
    summary="Envoyer une notification de test",
    description="Envoie une notification sur le canal spécifié (ntfy/push/email/whatsapp). Nécessite le rôle admin.",
)
@gerer_exception_api
async def envoyer_notification_test(
    body: NotificationTestRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Envoie une notification de test sur le canal demandé."""
    from src.api.utils import executer_async

    def _send():
        if body.canal == "whatsapp":
            import asyncio

            from src.services.integrations.whatsapp import envoyer_message_whatsapp

            result = asyncio.run(envoyer_message_whatsapp(destinataire="", texte=body.message))
            return {
                "resultats": {"whatsapp": result},
                "message": "Notification WhatsApp de test envoyée." if result else "Échec envoi WhatsApp.",
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


# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════


@router.post(
    "/cache/purge",
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


# ═══════════════════════════════════════════════════════════
# DB COHÉRENCE
# ═══════════════════════════════════════════════════════════


@router.get(
    "/db/coherence",
    responses=REPONSES_AUTH_ADMIN,
    summary="Test cohérence base de données",
    description="Lance des vérifications rapides d'intégrité DB. Nécessite le rôle admin.",
)
@gerer_exception_api
async def coherence_db(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict:
    """Vérifie la cohérence de la base de données (checks rapides)."""
    from src.api.utils import executer_async, executer_avec_session

    def _check():
        resultats: list[dict] = []
        erreurs: list[str] = []

        with executer_avec_session() as session:
            # 1. Connexion DB
            try:
                session.execute(__import__("sqlalchemy").text("SELECT 1"))
                resultats.append({"check": "connexion_db", "status": "ok"})
            except Exception as exc:
                erreurs.append(f"connexion_db: {exc}")
                resultats.append({"check": "connexion_db", "status": "erreur", "detail": str(exc)})

            # 2. Tables principales présentes
            tables_essentielles = [
                "recettes", "articles_courses", "listes_courses",
                "inventaire_items", "profils_utilisateurs",
            ]
            try:
                from sqlalchemy import text

                for table in tables_essentielles:
                    try:
                        session.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                        resultats.append({"check": f"table_{table}", "status": "ok"})
                    except Exception as exc:
                        erreurs.append(f"table_{table}: {exc}")
                        resultats.append({"check": f"table_{table}", "status": "erreur", "detail": str(exc)})
            except Exception as exc:
                erreurs.append(f"vérification tables: {exc}")

            # 3. Articles de courses sans liste parent (orphelins)
            try:
                from sqlalchemy import text

                row = session.execute(
                    text(
                        "SELECT COUNT(*) FROM articles_courses ac "
                        "LEFT JOIN listes_courses lc ON lc.id = ac.liste_id "
                        "WHERE lc.id IS NULL"
                    )
                ).scalar()
                resultats.append({
                    "check": "articles_orphelins",
                    "status": "ok" if (row or 0) == 0 else "avertissement",
                    "detail": f"{row} article(s) orphelin(s)",
                })
            except Exception as exc:
                logger.debug("Check articles orphelins ignoré: %s", exc)

        statut_global = "erreur" if erreurs else "ok"
        return {
            "status": statut_global,
            "checks": resultats,
            "erreurs": erreurs,
            "total_checks": len(resultats),
            "checks_ok": sum(1 for c in resultats if c["status"] == "ok"),
        }

    return await executer_async(_check)


# ═══════════════════════════════════════════════════════════
# DASHBOARD ADMIN CONSOLIDÉ
# ═══════════════════════════════════════════════════════════


@router.get(
    "/dashboard",
    responses=REPONSES_AUTH_ADMIN,
    summary="Dashboard admin consolidé",
    description="Retourne une vue consolidée des métriques admin (audit, jobs, services, cache, sécurité).",
)
@gerer_exception_api
async def dashboard_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Vue consolidée pour le cockpit admin."""
    from src.api.utils import executer_async, executer_avec_session

    def _query():
        from src.services.core.cron.jobs import _demarreur
        from src.services.core.registry import registre

        jobs = []
        if _demarreur is not None and _demarreur._scheduler.running:
            jobs = list(_demarreur._scheduler.get_jobs())

        jobs_actifs = sum(1 for j in jobs if j.next_run_time is not None)

        try:
            from src.core.caching import obtenir_cache

            cache_stats = (
                obtenir_cache().obtenir_statistiques() if hasattr(obtenir_cache(), "obtenir_statistiques") else {}
            )
        except Exception:
            cache_stats = {}

        security_24h = 0
        with executer_avec_session() as session:
            security_24h = int(
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM logs_securite
                        WHERE created_at >= NOW() - INTERVAL '24 HOURS'
                        """
                    )
                ).scalar()
                or 0
            )

        return {
            "generated_at": datetime.now().isoformat(),
            "jobs": {
                "total": len(jobs),
                "actifs": jobs_actifs,
                "inactifs": max(0, len(jobs) - jobs_actifs),
            },
            "services": registre.health_check_global(),
            "metriques_services": registre.obtenir_metriques(),
            "cache": cache_stats,
            "security": {
                "events_24h": security_24h,
            },
            "feature_flags": _lire_namespace_persistant(
                _NAMESPACE_FEATURE_FLAGS,
                _FEATURE_FLAGS_PAR_DEFAUT,
            ),
        }

    return await executer_async(_query)


# ═══════════════════════════════════════════════════════════
# SERVICE ACTIONS MANUELLES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/services/actions",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les actions de service manuelles",
    description="Catalogue d'actions de services exécutables manuellement depuis l'admin.",
)
@gerer_exception_api
async def lister_actions_services(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {
        "items": _catalogue_actions_services(),
        "total": len(_catalogue_actions_services()),
        "enabled": bool(flags.get("admin.service_actions_enabled", True)),
    }


@router.post(
    "/services/actions/{action_id}/run",
    responses=REPONSES_AUTH_ADMIN,
    summary="Exécuter une action de service",
    description="Lance une action de service whitelistée (avec support dry-run selon l'action).",
)
@gerer_exception_api
async def executer_action_service(
    action_id: str,
    body: ServiceActionRunRequest,
    dry_run: bool = Query(False, description="Simulation sans écriture"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_async

    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    if not bool(flags.get("admin.service_actions_enabled", True)):
        raise HTTPException(status_code=403, detail="Les actions de service manuelles sont désactivées.")

    result = await executer_async(
        lambda: _executer_action_service(action_id, dry_run=dry_run, params=body.params)
    )
    _journaliser_action_admin(
        action="admin.service_action.run",
        entite_type="service_action",
        utilisateur_id=str(user.get("id", "admin")),
        details={"action_id": action_id, "dry_run": dry_run},
    )
    return result


# ═══════════════════════════════════════════════════════════
# FEATURE FLAGS & CONFIG RUNTIME
# ═══════════════════════════════════════════════════════════


@router.get(
    "/feature-flags",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire les feature flags",
    description="Retourne les feature flags runtime modifiables depuis l'admin.",
)
@gerer_exception_api
async def lire_feature_flags(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {"flags": flags, "total": len(flags)}


@router.put(
    "/feature-flags",
    responses=REPONSES_AUTH_ADMIN,
    summary="Mettre à jour les feature flags",
    description="Met à jour les feature flags runtime côté admin.",
)
@gerer_exception_api
async def mettre_a_jour_feature_flags(
    body: FeatureFlagsUpdateRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _ecrire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, body.flags)
    _journaliser_action_admin(
        action="admin.feature_flags.update",
        entite_type="feature_flag",
        utilisateur_id=str(user.get("id", "admin")),
        details={"updates": body.flags},
    )
    return {"status": "ok", "flags": flags, "total": len(flags)}


@router.get(
    "/runtime-config",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire la configuration runtime admin",
    description="Retourne la configuration runtime éditable et quelques valeurs système en lecture seule.",
)
@gerer_exception_api
async def lire_runtime_config(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.core.config import obtenir_parametres

    params = obtenir_parametres()
    runtime = _lire_namespace_persistant(_NAMESPACE_RUNTIME_CONFIG, _RUNTIME_CONFIG_PAR_DEFAUT)
    readonly = {
        "env": params.ENV,
        "debug": params.DEBUG,
        "mistral_model": params.MISTRAL_MODEL,
        "cache_enabled": params.CACHE_ENABLED,
        "log_level": params.LOG_LEVEL,
    }
    return {"values": runtime, "readonly": readonly}


@router.put(
    "/runtime-config",
    responses=REPONSES_AUTH_ADMIN,
    summary="Mettre à jour la configuration runtime admin",
    description="Met à jour la configuration runtime éditable stockée côté serveur.",
)
@gerer_exception_api
async def mettre_a_jour_runtime_config(
    body: RuntimeConfigUpdateRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    values = _ecrire_namespace_persistant(_NAMESPACE_RUNTIME_CONFIG, body.values)
    _journaliser_action_admin(
        action="admin.runtime_config.update",
        entite_type="runtime_config",
        utilisateur_id=str(user.get("id", "admin")),
        details={"updates": body.values},
    )
    return {"status": "ok", "values": values}


# ═══════════════════════════════════════════════════════════
# FORCER RE-SYNC EXTERNES
# ═══════════════════════════════════════════════════════════


@router.get(
    "/resync/targets",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les cibles de re-sync",
    description="Catalogue des synchronisations externes déclenchables manuellement.",
)
@gerer_exception_api
async def lister_cibles_resync(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {
        "items": _cibles_resync(),
        "total": len(_cibles_resync()),
        "enabled": bool(flags.get("admin.resync_enabled", True)),
    }


@router.post(
    "/resync/{target_id}",
    responses=REPONSES_AUTH_ADMIN,
    summary="Forcer une synchronisation externe",
    description="Déclenche une synchronisation externe (Garmin, Google Calendar, OpenFoodFacts).",
)
@gerer_exception_api
async def forcer_resync(
    target_id: str,
    dry_run: bool = Query(False, description="Simuler sans exécution"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.cron.jobs import executer_job_par_id

    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    if not bool(flags.get("admin.resync_enabled", True)):
        raise HTTPException(status_code=403, detail="Les actions de re-sync sont désactivées.")

    cible = next((c for c in _cibles_resync() if c["id"] == target_id), None)
    if cible is None:
        raise HTTPException(status_code=404, detail=f"Cible de re-sync inconnue: {target_id}")

    result = executer_job_par_id(
        cible["job_id"],
        dry_run=dry_run,
        source="manual",
        triggered_by_user_id=str(user.get("id", "admin")),
        relancer_exception=False,
    )
    _journaliser_action_admin(
        action="admin.resync.run",
        entite_type="resync",
        utilisateur_id=str(user.get("id", "admin")),
        details={"target": target_id, "dry_run": dry_run},
    )
    return {"target": target_id, **result}


# ═══════════════════════════════════════════════════════════
# SEED DEV
# ═══════════════════════════════════════════════════════════


@router.post(
    "/seed/dev",
    responses=REPONSES_AUTH_ADMIN,
    summary="Injecter des données seed (dev)",
    description="Injecte des données de seed en environnement dev/test uniquement.",
)
@gerer_exception_api
async def injecter_seed_dev(
    body: SeedDataRequest,
    dry_run: bool = Query(False, description="Simulation sans écriture"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.core.config import obtenir_parametres

    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    if not bool(flags.get("admin.seed_dev_enabled", True)):
        raise HTTPException(status_code=403, detail="Le seed dev est désactivé.")

    env = obtenir_parametres().ENV.lower()
    if env not in {"development", "dev", "test"}:
        raise HTTPException(status_code=403, detail="Le seed est autorisé uniquement en dev/test.")

    if body.scope != "recettes_standard":
        raise HTTPException(status_code=422, detail=f"Scope seed non supporté: {body.scope}")

    seed_file = Path("data/seed/recettes_standard.json")
    if dry_run:
        total = 0
        try:
            payload = json.loads(seed_file.read_text(encoding="utf-8"))
            total = len(payload.get("recettes_standard", []))
        except Exception:
            total = 0

        return {
            "status": "dry_run",
            "scope": body.scope,
            "file": str(seed_file),
            "recettes_detectees": total,
            "message": "Simulation uniquement - aucune écriture DB.",
        }

    from scripts.db.import_recettes import importer_recettes_standard

    imported = int(importer_recettes_standard())
    _journaliser_action_admin(
        action="admin.seed.run",
        entite_type="seed",
        utilisateur_id=str(user.get("id", "admin")),
        details={"scope": body.scope, "imported": imported},
    )
    return {
        "status": "ok",
        "scope": body.scope,
        "imported": imported,
        "message": f"Seed terminé ({imported} recette(s) importée(s)).",
    }


@router.get(
    "/sql-views",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les vues SQL exposées",
    description="Retourne la liste des vues SQL disponibles via l'API admin (lecture seule).",
)
@gerer_exception_api
async def lister_vues_sql(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Liste blanche des vues SQL consultables depuis l'admin."""
    return {
        "items": [
            {"nom": nom_vue, "endpoint": f"/api/v1/admin/sql-views/{nom_vue}"}
            for nom_vue in _VUES_SQL_AUTORISEES
        ],
        "total": len(_VUES_SQL_AUTORISEES),
    }


@router.get(
    "/sql-views/{view_name}",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire une vue SQL exposée",
    description="Exécute un SELECT paginé en lecture seule sur une vue SQL autorisée.",
)
@gerer_exception_api
async def lire_vue_sql(
    view_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Retourne les lignes d'une vue SQL autorisée."""
    from sqlalchemy import text

    from src.api.utils import executer_avec_session

    if view_name not in _VUES_SQL_AUTORISEES:
        raise HTTPException(
            status_code=404,
            detail=f"Vue SQL '{view_name}' non exposée.",
        )

    offset = (page - 1) * page_size

    with executer_avec_session() as session:
        total = int(
            session.execute(text(f"SELECT COUNT(*) FROM {view_name}")).scalar() or 0
        )
        rows = session.execute(
            text(
                f"SELECT * FROM {view_name} "
                "ORDER BY 1 "
                "LIMIT :limit OFFSET :offset"
            ),
            {"limit": page_size, "offset": offset},
        ).mappings().all()

    items = [dict(row) for row in rows]
    return {
        "view": view_name,
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages_totales": max(1, (total + page_size - 1) // page_size),
    }
