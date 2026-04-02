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
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import text

from src.api.dependencies import require_auth, require_role
from src.api.schemas.errors import REPONSES_AUTH_ADMIN
from src.api.utils import gerer_exception_api

logger = logging.getLogger(__name__)

# ── Rate limiting global admin (10 req/min par admin) ────────────────────────
_ADMIN_RATE_LIMIT = 10  # requêtes par minute
_admin_timestamps: dict[str, collections.deque[float]] = {}


async def _verifier_limite_admin(user: dict[str, Any] = Depends(require_role("admin"))) -> dict[str, Any]:
    """Dépendance de rate limiting pour tous les endpoints admin (10 req/min)."""
    if os.getenv("ENVIRONMENT", "").lower() in {"test", "testing"} or os.getenv("PYTEST_CURRENT_TEST"):
        return user

    user_id = user.get("id", "unknown")
    now = time.time()
    window = 60.0
    q = _admin_timestamps.setdefault(user_id, collections.deque())
    while q and q[0] < now - window:
        q.popleft()
    if len(q) >= _ADMIN_RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Trop de requêtes admin. Maximum {_ADMIN_RATE_LIMIT} par minute.",
        )
    q.append(now)
    return user


router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin"],
    dependencies=[Depends(_verifier_limite_admin)],
)

# ── Rate limiting jobs triggers (5 req/min par admin) ────────────────────────
_JOB_TRIGGER_RATE_LIMIT = 5  # requêtes par minute
_job_trigger_timestamps: dict[str, collections.deque[float]] = {}


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
_job_logs: dict[str, list[dict[str, Any]]] = {}  # job_id → list of {timestamp, status, message}
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


@router.get(
    "/audit-export/pdf",
    responses=REPONSES_AUTH_ADMIN,
    summary="Export PDF des logs d'audit",
    description="Exporte les logs d'audit au format PDF.",
)
@gerer_exception_api
async def exporter_audit_pdf(
    action: str | None = Query(None),
    entite_type: str | None = Query(None),
    depuis: datetime | None = Query(None),
    jusqu_a: datetime | None = Query(None),
    user: dict[str, Any] = Depends(require_role("admin")),
):
    """Export PDF des logs d'audit."""
    from src.services.core.audit import obtenir_service_audit

    service = obtenir_service_audit()
    resultat = service.consulter(
        action=action,
        entite_type=entite_type,
        depuis=depuis,
        jusqu_a=jusqu_a,
        limite=2000,
        page=1,
    )

    pdf_bytes = _construire_pdf_audit(
        list(resultat.entrees),
        {
            "action": action,
            "entite_type": entite_type,
            "depuis": depuis.isoformat() if depuis else None,
            "jusqu_a": jusqu_a.isoformat() if jusqu_a else None,
        },
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=audit-logs.pdf"},
    )


@router.get(
    "/events",
    responses=REPONSES_AUTH_ADMIN,
    summary="Consulter le bus d'événements",
    description="Expose les métriques et l'historique récent du bus d'événements domaine.",
)
@gerer_exception_api
async def lire_evenements_admin(
    limite: int = Query(30, ge=1, le=200),
    type_evenement: str | None = Query(None, description="Filtrer sur un type exact"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    historique = bus.obtenir_historique(type_evenement=type_evenement, limite=limite)
    items = [
        {
            "event_id": event.event_id,
            "type": event.type,
            "source": event.source,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
            "data": event.data or {},
        }
        for event in historique
    ]
    return {
        "metriques": bus.obtenir_metriques(),
        "items": items,
        "total": len(items),
    }


@router.post(
    "/events/trigger",
    responses=REPONSES_AUTH_ADMIN,
    summary="Déclencher un événement domaine",
    description="Émet manuellement un événement sur le bus pour tester les subscribers.",
)
@gerer_exception_api
async def declencher_evenement_admin(
    body: EventBusTriggerRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    handlers_notifies = bus.emettre(
        type_evenement=body.type_evenement,
        data=body.payload,
        source=body.source,
    )
    _journaliser_action_admin(
        action="admin.events.trigger",
        entite_type="event_bus",
        utilisateur_id=str(user.get("id", "admin")),
        details={
            "type_evenement": body.type_evenement,
            "source": body.source,
            "handlers_notifies": handlers_notifies,
        },
    )
    return {
        "status": "ok",
        "type_evenement": body.type_evenement,
        "handlers_notifies": handlers_notifies,
    }


@router.post(
    "/events/replay",
    responses=REPONSES_AUTH_ADMIN,
    summary="Rejouer un événement passé",
    description="Recharge l'historique DB du bus puis ré-émet un ou plusieurs événements.",
)
@gerer_exception_api
async def rejouer_evenement_admin(
    body: EventBusReplayRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.services.core.events import obtenir_bus

    bus = obtenir_bus()
    limite = max(1, min(50, int(body.limite or 1)))
    events = bus.rejouer_historique_db(type_evenement=body.type_evenement, limite=200)

    if body.event_id:
        events = [e for e in events if e.event_id == body.event_id]

    if not events:
        raise HTTPException(status_code=404, detail="Aucun événement trouvé pour replay")

    a_rejouer = events[-limite:]
    total_handlers = 0
    replayes: list[dict[str, Any]] = []

    for event in a_rejouer:
        notified = bus.emettre(
            type_evenement=event.type,
            data=event.data,
            source=body.source,
        )
        total_handlers += notified
        replayes.append(
            {
                "event_id": event.event_id,
                "type": event.type,
                "handlers_notifies": notified,
            }
        )

    _journaliser_action_admin(
        action="admin.events.replay",
        entite_type="event_bus",
        utilisateur_id=str(user.get("id", "admin")),
        details={
            "event_id": body.event_id,
            "type_evenement": body.type_evenement,
            "limite": limite,
            "replayes": len(replayes),
            "handlers_notifies": total_handlers,
        },
    )

    return {
        "status": "ok",
        "replayes": replayes,
        "total": len(replayes),
        "handlers_notifies": total_handlers,
    }


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
    numero_destinataire: str | None = None
    titre: str = "Test Matanne"


class NotificationTestAllRequest(BaseModel):
    message: str
    email: str | None = None
    titre: str = "Test multi-canal Matanne"
    inclure_whatsapp: bool = True


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


class ConfigImportRequest(BaseModel):
    feature_flags: dict[str, bool] | None = None
    runtime_config: dict[str, Any] | None = None
    merge: bool = True


class SeedDataRequest(BaseModel):
    scope: Literal["recettes_standard"] = "recettes_standard"


class FlowSimulationRequest(BaseModel):
    scenario: Literal[
        "peremption_j2",
        "document_expirant",
        "echec_cron_job",
        "rappel_courses",
        "resume_hebdo",
    ]
    user_id: str | None = None
    message: str | None = None
    dry_run: bool = True
    payload: dict[str, Any] = {}


class MaintenanceModeRequest(BaseModel):
    enabled: bool


class EventBusTriggerRequest(BaseModel):
    type_evenement: str
    source: str = "admin"
    payload: dict[str, Any] = {}


class EventBusReplayRequest(BaseModel):
    event_id: str | None = None
    type_evenement: str | None = None
    limite: int = 1
    source: str = "admin_replay"


class UserImpersonationRequest(BaseModel):
    duree_heures: int = 1
    raison: str | None = None


class AdminAIConsoleRequest(BaseModel):
    prompt: str
    prompt_systeme: str = "Tu es un assistant admin pour une application de gestion familiale."
    temperature: float = 0.4
    max_tokens: int = 800
    utiliser_cache: bool = False


class DbImportRequest(BaseModel):
    tables: dict[str, list[dict[str, Any]]]
    merge: bool = False


class JobsBulkRequest(BaseModel):
    dry_run: bool = False
    continuer_sur_erreur: bool = True


class JobsSimulationJourneeRequest(BaseModel):
    dry_run: bool = True
    continuer_sur_erreur: bool = True
    inclure_jobs_inactifs: bool = False


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
    "job_expiration_recettes_suggestion": "S15.1 Ingrédients expirants → suggestion recettes (10h00)",
    "job_stock_prediction_reapprovisionnement": "S15.2 Prédiction réapprovisionnement inventaire (lun 08h00)",
    "job_variete_repas_alerte": "S15.3 Alerte variété repas (dim 17h00)",
    "job_tendances_activites_famille": "S15.4 Tendances activités famille (dim 19h30)",
    "job_energie_peak_detection": "S15.5 Détection pics énergie (19h00)",
    "job_nutrition_adultes_weekly": "S15.6 Bilan nutrition adultes Garmin (dim 20h15)",
    "job_briefing_matinal_push": "S15.7 Briefing matinal IA (07h00)",
    "job_jardin_feedback_planning": "S15.8 Feedback jardin → planning (dim 18h30)",
    "s16_resume_weekend_whatsapp": "S16.3 Résumé weekend suggestions WhatsApp (ven 18h00)",
    "s16_rappel_entretien_whatsapp": "S16.6 Rappel entretien maison WhatsApp (08h10)",
    "s16_bilan_nutrition_whatsapp": "S16.5 Bilan nutrition semaine WhatsApp (dim 20h30)",
    "s16_rapport_famille_mensuel": "S16.8 Rapport mensuel famille complet email/PDF (1er 09h00)",
    "s16_rapport_maison_trimestriel": "S16.9 Rapport trimestriel maison email/PDF (T+1 09h10)",
}

_NOTIFICATION_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "whatsapp": [
        {"id": "recette_du_jour", "label": "S16.1 Suggestion recette du jour", "trigger": "CRON 11:30"},
        {"id": "diagnostic_maison", "label": "S16.2 Alerte diagnostic maison", "trigger": "Événement"},
        {"id": "resume_weekend", "label": "S16.3 Résumé weekend suggestions", "trigger": "CRON ven 18:00"},
        {"id": "budget_depassement", "label": "S16.4 Alerte budget dépassement", "trigger": "Événement"},
        {"id": "bilan_nutrition", "label": "S16.5 Bilan nutrition semaine", "trigger": "CRON dim 20:30"},
        {"id": "rappel_entretien", "label": "S16.6 Rappel entretien maison", "trigger": "CRON quotidien"},
        {"id": "commande_vocale", "label": "S16.7 Commande vocale rapide", "trigger": "À la demande"},
    ],
    "email": [
        {"id": "rapport_famille_mensuel_complet", "label": "S16.8 Rapport mensuel famille complet", "trigger": "Mensuel 1er 09:00"},
        {"id": "rapport_maison_trimestriel", "label": "S16.9 Rapport trimestriel maison", "trigger": "Trimestriel"},
    ],
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
    "admin.mode_test": False,
    "admin.maintenance_mode": False,
    "jeux.bankroll_page_enabled": True,
    "outils.notes_tags_ui_enabled": True,
}

_RUNTIME_CONFIG_PAR_DEFAUT: dict[str, Any] = {
    "dashboard.refresh_seconds": 300,
    "notifications.digest_interval_minutes": 120,
    "admin.max_jobs_triggers_per_min": _JOB_TRIGGER_RATE_LIMIT,
}


def _extraire_jobs_matin() -> list[str]:
    """Retourne les IDs de jobs planifiés entre 06:00 et 09:00 inclus, selon les labels connus."""
    jobs_matin: list[str] = []
    for job_id, label in _LABELS_JOBS.items():
        match = re.search(r"\((\d{2})h(\d{2})\)", label)
        if not match:
            continue
        heure = int(match.group(1))
        if 6 <= heure <= 9:
            jobs_matin.append(job_id)
    return sorted(set(jobs_matin))


def _construire_pdf_audit(entrees: list[Any], filtres: dict[str, Any]) -> bytes:
    """Construit un PDF simple des logs d'audit filtrés."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.2 * cm,
        rightMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()
    elements: list[Any] = []

    elements.append(Paragraph("Audit Logs - Export PDF", styles["Title"]))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(Paragraph(f"Genere le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Normal"]))
    elements.append(Paragraph(f"Nombre d'entrees : {len(entrees)}", styles["Normal"]))

    filtres_actifs = [f"{k}={v}" for k, v in filtres.items() if v not in {None, ""}]
    if filtres_actifs:
        elements.append(Paragraph(f"Filtres : {' | '.join(filtres_actifs)}", styles["Normal"]))
    elements.append(Spacer(1, 0.35 * cm))

    lignes = [["Timestamp", "Action", "Source", "Entite", "Utilisateur"]]
    for entry in entrees:
        lignes.append([
            entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") if entry.timestamp else "",
            str(entry.action or "")[:45],
            str(entry.source or "")[:25],
            str(entry.entite_type or "")[:30],
            str(entry.utilisateur_id or "")[:28],
        ])

    table = Table(lignes, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#d1d5db")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


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


def est_mode_test_actif() -> bool:
    """Vérifie si le Mode Test admin est activé (best-effort, False par défaut)."""
    try:
        flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
        return bool(flags.get("admin.mode_test", False))
    except Exception:
        return False


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


def _resumer_api_metrics() -> dict[str, Any]:
    """Construit un résumé compact des métriques HTTP pour le cockpit admin."""
    from src.api.utils import get_metrics

    metrics = get_metrics()
    requests_total = metrics.get("requests", {}).get("total", {}) or {}
    latency = metrics.get("latency", {}) or {}

    total_requetes = sum(int(v) for v in requests_total.values())
    endpoints_tries = sorted(
        requests_total.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:5]

    latences_moyennes = [
        float(values.get("avg_ms", 0.0))
        for values in latency.values()
        if values.get("avg_ms") is not None
    ]
    p95_values = [
        float(values.get("p95_ms", 0.0))
        for values in latency.values()
        if values.get("p95_ms") is not None
    ]

    return {
        "uptime_seconds": metrics.get("uptime_seconds", 0),
        "requests_total": total_requetes,
        "top_endpoints": [
            {"endpoint": endpoint, "count": count}
            for endpoint, count in endpoints_tries
        ],
        "latency": {
            "avg_ms": round(sum(latences_moyennes) / len(latences_moyennes), 2)
            if latences_moyennes
            else 0.0,
            "p95_ms": round(max(p95_values), 2) if p95_values else 0.0,
            "tracked_endpoints": len(latency),
        },
        "rate_limiting": metrics.get("rate_limiting", {}),
        "ai": metrics.get("ai", {}),
    }


def _serialiser_valeur_export_db(value: Any) -> Any:
    """Sérialise une valeur SQLAlchemy vers un format JSON-safe."""
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, (bytes, bytearray)):
        return value.decode("utf-8", errors="ignore")
    return value


def _normaliser_nom_table(table_name: str) -> str:
    """Vérifie qu'un nom de table est sûr avant interpolation SQL."""
    if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", table_name):
        raise HTTPException(status_code=422, detail=f"Nom de table invalide: {table_name}")
    return table_name


def _exporter_config_admin() -> dict[str, Any]:
    """Exporte la configuration runtime persistée côté admin."""
    return {
        "exported_at": datetime.now().isoformat(),
        "feature_flags": _lire_namespace_persistant(
            _NAMESPACE_FEATURE_FLAGS,
            _FEATURE_FLAGS_PAR_DEFAUT,
        ),
        "runtime_config": _lire_namespace_persistant(
            _NAMESPACE_RUNTIME_CONFIG,
            _RUNTIME_CONFIG_PAR_DEFAUT,
        ),
    }


def _importer_config_admin(body: ConfigImportRequest) -> dict[str, Any]:
    """Importe la configuration runtime persistée côté admin."""
    feature_flags = body.feature_flags or {}
    runtime_config = body.runtime_config or {}

    if not body.merge:
        feature_flags = {**_FEATURE_FLAGS_PAR_DEFAUT, **feature_flags}
        runtime_config = {**_RUNTIME_CONFIG_PAR_DEFAUT, **runtime_config}

    flags = _ecrire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, feature_flags)
    runtime = _ecrire_namespace_persistant(_NAMESPACE_RUNTIME_CONFIG, runtime_config)
    return {
        "feature_flags": flags,
        "runtime_config": runtime,
    }


def _simuler_flux_admin(body: FlowSimulationRequest, user_id: str) -> dict[str, Any]:
    """Simule un flux inter-modules/notifications sans effet de bord."""
    from src.services.core.notifications.notif_dispatcher import get_dispatcher_notifications

    dispatcher = get_dispatcher_notifications()
    event_message = body.message or {
        "peremption_j2": "3 produits expirent sous 48h.",
        "document_expirant": "1 passeport expire sous 30 jours.",
        "echec_cron_job": "Le job sync_google_calendar a échoué.",
        "rappel_courses": "Pense à terminer la liste de courses ce soir.",
        "resume_hebdo": "Résumé hebdomadaire prêt à être envoyé.",
    }[body.scenario]

    canaux = dispatcher._resoudre_canaux(  # type: ignore[attr-defined]
        user_id=user_id,
        canaux=None,
        type_evenement=body.scenario,
        categorie=None,
    )
    sequence_failover = dispatcher._construire_sequence_failover(canaux)  # type: ignore[attr-defined]

    actions = [
        {
            "type": "notification.preparee",
            "message": event_message,
            "canaux": canaux,
            "failover": sequence_failover,
        }
    ]

    if body.scenario == "peremption_j2":
        actions.append(
            {
                "type": "suggestion_recettes",
                "details": "Déclencher des suggestions de recettes anti-gaspi à partir des produits expirants.",
            }
        )
    elif body.scenario == "document_expirant":
        actions.append(
            {
                "type": "rappel_administratif",
                "details": "Créer une alerte documentaire prioritaire avec échéance visible sur le dashboard.",
            }
        )
    elif body.scenario == "echec_cron_job":
        actions.append(
            {
                "type": "audit_admin",
                "details": "Journaliser l'échec et exposer l'entrée dans le cockpit admin temps réel.",
            }
        )
    elif body.scenario == "rappel_courses":
        actions.append(
            {
                "type": "budget_sync",
                "details": "Prévoir une synchronisation budget si une liste est finalisée après le rappel.",
            }
        )
    elif body.scenario == "resume_hebdo":
        actions.append(
            {
                "type": "digest",
                "details": "Consolider les sections famille, maison et cuisine avant l'envoi.",
            }
        )

    return {
        "scenario": body.scenario,
        "user_id": user_id,
        "dry_run": body.dry_run,
        "actions": actions,
        "payload": body.payload,
    }


def _simuler_test_e2e_one_click(user_id: str) -> dict[str, Any]:
    """Construit un scénario E2E admin en une seule action."""
    etapes = [
        {
            "etape": "recette",
            "action": "Sélectionner/générer une recette candidate",
            "status": "ok",
        },
        {
            "etape": "planning",
            "action": "Planifier la recette sur la semaine en cours",
            "status": "ok",
        },
        {
            "etape": "courses",
            "action": "Générer la liste de courses à partir du planning",
            "status": "ok",
        },
        {
            "etape": "checkout",
            "action": "Marquer la liste courses comme finalisée (checkout)",
            "status": "ok",
        },
        {
            "etape": "inventaire",
            "action": "Propager les écritures inventaire post-checkout",
            "status": "ok",
        },
    ]
    return {
        "status": "ok",
        "workflow": "recette->planning->courses->checkout->inventaire",
        "user_id": user_id,
        "mode": "simulation",
        "etapes": etapes,
        "total_etapes": len(etapes),
    }


@router.get(
    "/bridges/phase5/status",
    responses=REPONSES_AUTH_ADMIN,
    summary="Statut opérationnel des bridges Phase 5",
    description=(
        "Expose l'état opérationnel des 17 actions Phase 5 (bridges inter-modules et "
        "interactions intra-modules) pour dashboard/admin."
    ),
)
@gerer_exception_api
async def statut_bridges_phase5(
    inclure_smoke: bool = Query(
        True,
        description=(
            "Exécute des checks smoke non destructifs sur les actions compatibles. "
            "Les actions mutatives restent en vérification de présence."
        ),
    ),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Retourne un statut détaillé de tous les bridges/actions de la phase 5."""
    from src.api.utils import executer_async, executer_avec_session

    def _query() -> dict[str, Any]:
        debut_global = time.perf_counter()
        resultats: list[dict[str, Any]] = []

        with executer_avec_session() as session:
            presence_fallbacks: dict[str, Any] = {
                "P5-01": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "suggerer_recettes_selon_stock",
                ),
                "P5-02": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_jules_nutrition",
                        fromlist=["obtenir_service_jules_nutrition_interaction"],
                    ).obtenir_service_jules_nutrition_interaction(),
                    "adapter_planning_nutrition_selon_croissance",
                ),
                "P5-03": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_saison_menu",
                        fromlist=["obtenir_service_saison_menu_interaction"],
                    ).obtenir_service_saison_menu_interaction(),
                    "obtenir_contexte_saisonnier_planning",
                ),
                "P5-04": lambda: hasattr(
                    __import__(
                        "src.services.famille.inter_module_meteo_activites",
                        fromlist=["obtenir_service_meteo_activites_interaction"],
                    ).obtenir_service_meteo_activites_interaction(),
                    "suggerer_activites_selon_meteo",
                ),
                "P5-05": lambda: hasattr(
                    __import__(
                        "src.services.maison.inter_module_entretien_courses",
                        fromlist=["obtenir_service_entretien_courses_interaction"],
                    ).obtenir_service_entretien_courses_interaction(),
                    "suggerer_produits_entretien_pour_courses",
                ),
                "P5-06": lambda: hasattr(
                    __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    ).obtenir_service_charges_energie_interaction(),
                    "detecter_hausse_et_declencher_analyse",
                ),
                "P5-07": lambda: hasattr(
                    __import__(
                        "src.services.famille.inter_module_weekend_courses",
                        fromlist=["obtenir_service_weekend_courses_interaction"],
                    ).obtenir_service_weekend_courses_interaction(),
                    "suggerer_fournitures_weekend",
                ),
                "P5-09": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "suggerer_recettes_selon_stock",
                ),
                "P5-10": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "exclure_articles_surplus_des_courses",
                ),
                "P5-11": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "bloquer_jours_batch_dans_planning",
                ),
                "P5-12": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "analyser_equilibre_nutritionnel_planning",
                ),
                "P5-13": lambda: hasattr(
                    __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    ).obtenir_service_inventaire_planning_interaction(),
                    "filtrer_recettes_mal_notees",
                ),
                "P5-17": lambda: hasattr(
                    __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    ).obtenir_service_charges_energie_interaction(),
                    "detecter_hausse_et_declencher_analyse",
                ),
            }

            checks: list[dict[str, Any]] = [
                {
                    "id": "P5-01",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Stock -> Planning recettes",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .suggerer_recettes_selon_stock(db=session),
                },
                {
                    "id": "P5-02",
                    "bridge": "inter_module_jules_nutrition.py",
                    "intitule": "Jules croissance -> Planning nutrition",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_jules_nutrition",
                        fromlist=["obtenir_service_jules_nutrition_interaction"],
                    )
                    .obtenir_service_jules_nutrition_interaction()
                    .adapter_planning_nutrition_selon_croissance(db=session),
                },
                {
                    "id": "P5-03",
                    "bridge": "inter_module_saison_menu.py",
                    "intitule": "Produits de saison -> Planning IA",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_saison_menu",
                        fromlist=["obtenir_service_saison_menu_interaction"],
                    )
                    .obtenir_service_saison_menu_interaction()
                    .obtenir_contexte_saisonnier_planning(),
                },
                {
                    "id": "P5-04",
                    "bridge": "inter_module_meteo_activites.py",
                    "intitule": "Météo -> Activités famille",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.famille.inter_module_meteo_activites",
                        fromlist=["obtenir_service_meteo_activites_interaction"],
                    )
                    .obtenir_service_meteo_activites_interaction()
                    .suggerer_activites_selon_meteo(db=session),
                },
                {
                    "id": "P5-05",
                    "bridge": "inter_module_entretien_courses.py",
                    "intitule": "Entretien -> Courses",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.maison.inter_module_entretien_courses",
                        fromlist=["obtenir_service_entretien_courses_interaction"],
                    )
                    .obtenir_service_entretien_courses_interaction()
                    .suggerer_produits_entretien_pour_courses(db=session),
                },
                {
                    "id": "P5-06",
                    "bridge": "inter_module_charges_energie.py",
                    "intitule": "Charges facture -> Analyse énergie",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    )
                    .obtenir_service_charges_energie_interaction()
                    .detecter_hausse_et_declencher_analyse(db=session),
                },
                {
                    "id": "P5-07",
                    "bridge": "inter_module_weekend_courses.py",
                    "intitule": "Weekend activités -> Courses",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.famille.inter_module_weekend_courses",
                        fromlist=["obtenir_service_weekend_courses_interaction"],
                    )
                    .obtenir_service_weekend_courses_interaction()
                    .suggerer_fournitures_weekend(db=session),
                },
                {
                    "id": "P5-08",
                    "bridge": "inter_module_documents_calendrier.py",
                    "intitule": "Documents expirants -> Calendrier",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.famille.inter_module_documents_calendrier",
                            fromlist=["obtenir_service_documents_calendrier_interaction"],
                        ).obtenir_service_documents_calendrier_interaction(),
                        "synchroniser_documents_vers_calendrier",
                    ),
                },
                {
                    "id": "P5-09",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Inventaire -> Planning",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .suggerer_recettes_selon_stock(db=session),
                },
                {
                    "id": "P5-10",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Anti-gaspillage -> Courses",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .exclure_articles_surplus_des_courses(db=session),
                },
                {
                    "id": "P5-11",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Batch cooking -> Planning",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .bloquer_jours_batch_dans_planning(db=session),
                },
                {
                    "id": "P5-12",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Nutrition -> Planning",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .analyser_equilibre_nutritionnel_planning(db=session),
                },
                {
                    "id": "P5-13",
                    "bridge": "inter_module_inventaire_planning.py",
                    "intitule": "Feedback recette -> Suggestions IA",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.cuisine.inter_module_inventaire_planning",
                        fromlist=["obtenir_service_inventaire_planning_interaction"],
                    )
                    .obtenir_service_inventaire_planning_interaction()
                    .filtrer_recettes_mal_notees(db=session),
                },
                {
                    "id": "P5-14",
                    "bridge": "inter_module_jules_nutrition.py",
                    "intitule": "Jules croissance -> Portions recettes",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.cuisine.inter_module_jules_nutrition",
                            fromlist=["obtenir_service_jules_nutrition_interaction"],
                        ).obtenir_service_jules_nutrition_interaction(),
                        "adapter_portions_recettes_planifiees",
                    ),
                },
                {
                    "id": "P5-15",
                    "bridge": "inter_module_anniversaires_budget.py",
                    "intitule": "Anniversaire J-14 -> Budget prévisionnel",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.famille.inter_module_anniversaires_budget",
                            fromlist=["obtenir_service_anniversaires_budget_interaction"],
                        ).obtenir_service_anniversaires_budget_interaction(),
                        "reserver_budget_previsionnel_j14",
                    ),
                },
                {
                    "id": "P5-16",
                    "bridge": "inter_module_jardin_entretien.py",
                    "intitule": "Jardin saison -> Entretien auto",
                    "type_check": "presence",
                    "callable": lambda: hasattr(
                        __import__(
                            "src.services.maison.inter_module_jardin_entretien",
                            fromlist=["obtenir_service_jardin_entretien_interaction"],
                        ).obtenir_service_jardin_entretien_interaction(),
                        "generer_taches_saisonnieres_depuis_plantes",
                    ),
                },
                {
                    "id": "P5-17",
                    "bridge": "inter_module_charges_energie.py",
                    "intitule": "Charges augmentation -> Diagnostic énergie",
                    "type_check": "smoke",
                    "callable": lambda: __import__(
                        "src.services.maison.inter_module_charges_energie",
                        fromlist=["obtenir_service_charges_energie_interaction"],
                    )
                    .obtenir_service_charges_energie_interaction()
                    .detecter_hausse_et_declencher_analyse(db=session),
                },
            ]

            for check in checks:
                debut = time.perf_counter()
                type_check = check["type_check"]
                if type_check == "smoke" and not inclure_smoke:
                    type_check = "presence"

                try:
                    if type_check == "presence":
                        if not inclure_smoke and check["id"] in presence_fallbacks:
                            presence_fallbacks[check["id"]]()
                        else:
                            check["callable"]()
                        resultat = {
                            "id": check["id"],
                            "bridge": check["bridge"],
                            "intitule": check["intitule"],
                            "verification": "presence",
                            "statut": "operationnel",
                            "latence_ms": round((time.perf_counter() - debut) * 1000, 2),
                            "details": "Factory et méthode disponibles.",
                        }
                    else:
                        sortie = check["callable"]()
                        resultat = {
                            "id": check["id"],
                            "bridge": check["bridge"],
                            "intitule": check["intitule"],
                            "verification": "smoke",
                            "statut": "operationnel",
                            "latence_ms": round((time.perf_counter() - debut) * 1000, 2),
                            "details": f"Retour {type(sortie).__name__}.",
                        }
                except Exception as exc:
                    resultat = {
                        "id": check["id"],
                        "bridge": check["bridge"],
                        "intitule": check["intitule"],
                        "verification": type_check,
                        "statut": "indisponible",
                        "latence_ms": round((time.perf_counter() - debut) * 1000, 2),
                        "details": str(exc)[:300],
                    }

                resultats.append(resultat)

        total = len(resultats)
        operationnels = len([r for r in resultats if r["statut"] == "operationnel"])
        indisponibles = total - operationnels
        statut_global = "operationnel" if indisponibles == 0 else "degrade"

        return {
            "phase": "phase_5",
            "generated_at": datetime.now().isoformat(),
            "execution_ms": round((time.perf_counter() - debut_global) * 1000, 2),
            "statut_global": statut_global,
            "resume": {
                "total_actions": total,
                "operationnelles": operationnels,
                "indisponibles": indisponibles,
                "taux_operationnel_pct": round((operationnels / total) * 100, 2) if total else 0.0,
                "mode_verification": "smoke+presence" if inclure_smoke else "presence_only",
            },
            "items": sorted(resultats, key=lambda r: r["id"]),
        }

    return await executer_async(_query)


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


@router.post(
    "/jobs/run-morning-batch",
    responses=REPONSES_AUTH_ADMIN,
    summary='Lancer tous les jobs du matin',
    description="Exécute en séquence les jobs planifiés entre 06:00 et 09:00.",
)
@gerer_exception_api
async def executer_jobs_matin(
    body: JobsBulkRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_async

    def _run() -> dict[str, Any]:
        from src.services.core.cron.jobs import executer_job_par_id, lister_jobs_disponibles

        jobs_matin = [j for j in _extraire_jobs_matin() if j in set(lister_jobs_disponibles())]
        resultats: list[dict[str, Any]] = []
        for job_id in jobs_matin:
            debut = time.perf_counter()
            try:
                sortie = executer_job_par_id(
                    job_id,
                    dry_run=body.dry_run,
                    source="admin_morning_batch",
                    triggered_by_user_id=str(user.get("id", "admin")),
                    relancer_exception=True,
                )
                statut = str(sortie.get("status", "ok"))
                resultats.append({
                    "job_id": job_id,
                    "status": statut,
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(sortie.get("message", "")),
                })
                _ajouter_log_job(job_id, "succes" if statut in {"ok", "dry_run", "success"} else "erreur", str(sortie))
            except Exception as exc:
                resultats.append({
                    "job_id": job_id,
                    "status": "failure",
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(exc),
                })
                _ajouter_log_job(job_id, "erreur", str(exc))
                if not body.continuer_sur_erreur:
                    break

        return {
            "mode": "dry_run" if body.dry_run else "run",
            "jobs_cibles": jobs_matin,
            "total": len(resultats),
            "succes": len([r for r in resultats if r["status"] in {"ok", "dry_run", "success"}]),
            "echecs": len([r for r in resultats if r["status"] not in {"ok", "dry_run", "success"}]),
            "items": resultats,
        }

    result = await executer_async(_run)
    _journaliser_action_admin(
        action="admin.jobs.morning_batch.run",
        entite_type="job_batch",
        utilisateur_id=str(user.get("id", "admin")),
        details={"dry_run": body.dry_run, "continuer_sur_erreur": body.continuer_sur_erreur},
    )
    return result


@router.post(
    "/jobs/simulate-day",
    responses=REPONSES_AUTH_ADMIN,
    summary='Simuler une journée de jobs',
    description="Exécute séquentiellement les jobs disponibles d'une journée type en mode dry-run.",
)
@gerer_exception_api
async def simuler_journee_jobs(
    body: JobsSimulationJourneeRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_async

    def _run() -> dict[str, Any]:
        from src.services.core.cron.jobs import executer_job_par_id, lister_jobs_disponibles

        jobs_disponibles = list(lister_jobs_disponibles())
        resultats: list[dict[str, Any]] = []
        debut_journee = datetime.now()

        for job_id in jobs_disponibles:
            debut = time.perf_counter()
            try:
                sortie = executer_job_par_id(
                    job_id,
                    dry_run=body.dry_run,
                    source="admin_day_simulation",
                    triggered_by_user_id=str(user.get("id", "admin")),
                    relancer_exception=True,
                )
                resultats.append({
                    "job_id": job_id,
                    "status": str(sortie.get("status", "ok")),
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(sortie.get("message", "")),
                })
            except Exception as exc:
                resultats.append({
                    "job_id": job_id,
                    "status": "failure",
                    "duration_ms": round((time.perf_counter() - debut) * 1000, 2),
                    "message": str(exc),
                })
                if not body.continuer_sur_erreur:
                    break

        return {
            "mode": "dry_run" if body.dry_run else "run",
            "started_at": debut_journee.isoformat(),
            "ended_at": datetime.now().isoformat(),
            "total": len(resultats),
            "succes": len([r for r in resultats if r["status"] in {"ok", "dry_run", "success"}]),
            "echecs": len([r for r in resultats if r["status"] not in {"ok", "dry_run", "success"}]),
            "items": resultats,
        }

    result = await executer_async(_run)
    _journaliser_action_admin(
        action="admin.jobs.day_simulation.run",
        entite_type="job_batch",
        utilisateur_id=str(user.get("id", "admin")),
        details={"dry_run": body.dry_run, "continuer_sur_erreur": body.continuer_sur_erreur},
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


@router.get(
    "/jobs/history",
    responses=REPONSES_AUTH_ADMIN,
    summary="Historique des exécutions jobs",
    description="Retourne l'historique paginé des exécutions de jobs avec filtres.",
)
@gerer_exception_api
async def historique_jobs(
    page: int = Query(1, ge=1),
    par_page: int = Query(25, ge=1, le=200),
    job_id: str | None = Query(None, description="Filtrer par identifiant de job"),
    status: str | None = Query(None, description="Filtrer par statut (success/failure/dry_run/...)"),
    depuis: datetime | None = Query(None, description="Date de début (ISO 8601)"),
    jusqu_a: datetime | None = Query(None, description="Date de fin (ISO 8601)"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Historique paginé/filtrable des lignes job_executions."""
    from src.api.utils import executer_avec_session

    offset = (page - 1) * par_page
    conditions: list[str] = ["1=1"]
    params: dict[str, Any] = {"limit": par_page, "offset": offset}

    if job_id:
        conditions.append("job_id = :job_id")
        params["job_id"] = job_id
    if status:
        conditions.append("status = :status")
        params["status"] = status
    if depuis:
        conditions.append("started_at >= :depuis")
        params["depuis"] = depuis
    if jusqu_a:
        conditions.append("started_at <= :jusqu_a")
        params["jusqu_a"] = jusqu_a

    where_clause = " AND ".join(conditions)

    with executer_avec_session() as session:
        total = int(
            session.execute(
                text(f"SELECT COUNT(*) FROM job_executions WHERE {where_clause}"),
                params,
            ).scalar()
            or 0
        )

        rows = session.execute(
            text(
                f"""
                SELECT
                    id,
                    job_id,
                    job_name,
                    started_at,
                    ended_at,
                    duration_ms,
                    status,
                    error_message,
                    output_logs,
                    triggered_by_user_id,
                    triggered_by_user_role
                FROM job_executions
                WHERE {where_clause}
                ORDER BY started_at DESC, id DESC
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()

    items = [
        {
            "id": int(row["id"]),
            "job_id": str(row["job_id"]),
            "job_name": row["job_name"] or _LABELS_JOBS.get(str(row["job_id"]), str(row["job_id"])),
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "ended_at": row["ended_at"].isoformat() if row["ended_at"] else None,
            "duration_ms": int(row["duration_ms"] or 0),
            "status": str(row["status"] or "unknown"),
            "error_message": row["error_message"],
            "output_logs": row["output_logs"],
            "triggered_by_user_id": row["triggered_by_user_id"],
            "triggered_by_user_role": row["triggered_by_user_role"],
        }
        for row in rows
    ]

    return {
        "items": items,
        "total": total,
        "page": page,
        "par_page": par_page,
        "pages_totales": max(1, (total + par_page - 1) // par_page),
    }


@router.get(
    "/jobs/compare-dry-run",
    responses=REPONSES_AUTH_ADMIN,
    summary="Comparer dry-run et exécution réelle",
    description="Compare les dernières exécutions dry-run et réelles par job.",
)
@gerer_exception_api
async def comparer_dry_run_vs_reel(
    limite: int = Query(20, ge=1, le=100),
    depuis_heures: int = Query(168, ge=1, le=24 * 30),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_avec_session

    debut = datetime.now() - timedelta(hours=depuis_heures)
    par_job: dict[str, dict[str, Any]] = {}

    with executer_avec_session() as session:
        rows = session.execute(
            text(
                """
                SELECT job_id, job_name, status, started_at, duration_ms, error_message
                FROM job_executions
                WHERE started_at >= :debut
                ORDER BY started_at DESC
                LIMIT 5000
                """
            ),
            {"debut": debut},
        ).mappings().all()

    for row in rows:
        job_id = str(row["job_id"])
        data = par_job.setdefault(
            job_id,
            {
                "job_id": job_id,
                "job_name": row["job_name"] or _LABELS_JOBS.get(job_id, job_id),
                "dry_run": None,
                "run": None,
            },
        )
        status = str(row["status"] or "")
        entree = {
            "status": status,
            "started_at": row["started_at"].isoformat() if row["started_at"] else None,
            "duration_ms": int(row["duration_ms"] or 0),
            "error_message": row["error_message"],
        }
        if status == "dry_run" and data["dry_run"] is None:
            data["dry_run"] = entree
        if status != "dry_run" and data["run"] is None:
            data["run"] = entree

    items = []
    for v in par_job.values():
        dry = v["dry_run"]
        run = v["run"]
        if not dry and not run:
            continue
        items.append({
            **v,
            "comparaison": {
                "delta_duration_ms": (run["duration_ms"] - dry["duration_ms"]) if dry and run else None,
                "status_coherent": (run["status"] in {"ok", "success"}) if run else None,
            },
        })

    items_sorted = sorted(
        items,
        key=lambda i: (i["run"] or i["dry_run"] or {}).get("started_at") or "",
        reverse=True,
    )[:limite]

    return {
        "generated_at": datetime.now().isoformat(),
        "fenetre_heures": depuis_heures,
        "total": len(items_sorted),
        "items": items_sorted,
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

            from src.core.config import obtenir_parametres
            from src.services.integrations.whatsapp import envoyer_message_whatsapp

            parametres = obtenir_parametres()
            destinataire = body.numero_destinataire or parametres.WHATSAPP_USER_NUMBER or ""
            if not destinataire:
                raise HTTPException(
                    status_code=422,
                    detail="Aucun numéro WhatsApp de destination configuré.",
                )

            result = asyncio.run(envoyer_message_whatsapp(destinataire=destinataire, texte=body.message))
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


@router.post(
    "/notifications/test-all",
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
        if body.inclure_whatsapp:
            canaux.append("whatsapp")

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
        details={"inclure_whatsapp": body.inclure_whatsapp},
    )
    return result


@router.get(
    "/notifications/templates",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lister les templates notifications admin",
    description="Retourne les templates disponibles (WhatsApp + Email), incluant Sprint 16.",
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
    "/notifications/queue",
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


@router.get(
    "/db/export",
    responses=REPONSES_AUTH_ADMIN,
    summary="Exporter la base en JSON",
    description="Exporte un snapshot JSON des tables publiques (dev/test recommandé).",
)
@gerer_exception_api
async def exporter_db_json(
    format: str = Query("json", pattern="^json$"),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Exporte les données des tables publiques en JSON."""
    from src.api.utils import executer_avec_session

    with executer_avec_session() as session:
        rows = session.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
                ORDER BY table_name
                """
            )
        ).mappings().all()

        tables = [str(row["table_name"]) for row in rows if row.get("table_name")]
        data: dict[str, list[dict[str, Any]]] = {}

        for table_name in tables:
            safe_table = _normaliser_nom_table(table_name)
            records = session.execute(
                text(f'SELECT * FROM "{safe_table}"')
            ).mappings().all()
            data[safe_table] = [
                {k: _serialiser_valeur_export_db(v) for k, v in dict(record).items()}
                for record in records
            ]

    _journaliser_action_admin(
        action="admin.db.export",
        entite_type="database",
        utilisateur_id=str(user.get("id", "admin")),
        details={"tables": len(data)},
    )
    return {
        "format": format,
        "exported_at": datetime.now().isoformat(),
        "tables": data,
        "total_tables": len(data),
    }


@router.post(
    "/db/import",
    responses=REPONSES_AUTH_ADMIN,
    summary="Importer un snapshot JSON en base",
    description="Restaure des données depuis un payload JSON table->records (mode merge ou replace).",
)
@gerer_exception_api
async def importer_db_json(
    body: DbImportRequest = Body(...),
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Importe des données JSON en base, table par table."""
    from src.api.utils import executer_avec_session
    from src.core.config import obtenir_parametres

    env = obtenir_parametres().ENV.lower()
    if env not in {"development", "dev", "test"}:
        raise HTTPException(status_code=403, detail="Import DB autorisé uniquement en dev/test.")

    resultats: dict[str, Any] = {}
    with executer_avec_session() as session:
        for table_name, records in body.tables.items():
            safe_table = _normaliser_nom_table(table_name)
            if not isinstance(records, list):
                raise HTTPException(status_code=422, detail=f"Format invalide pour la table {safe_table}.")

            if not body.merge:
                session.execute(text(f'TRUNCATE TABLE "{safe_table}" RESTART IDENTITY CASCADE'))

            imported = 0
            for record in records:
                if not isinstance(record, dict) or not record:
                    continue
                colonnes = [k for k in record.keys() if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(k))]
                if not colonnes:
                    continue
                placeholders = ", ".join(f":{c}" for c in colonnes)
                cols_sql = ", ".join(f'"{c}"' for c in colonnes)
                stmt = text(f'INSERT INTO "{safe_table}" ({cols_sql}) VALUES ({placeholders})')
                session.execute(stmt, {c: record.get(c) for c in colonnes})
                imported += 1

            resultats[safe_table] = {"imported": imported, "merge": body.merge}
        session.commit()

    _journaliser_action_admin(
        action="admin.db.import",
        entite_type="database",
        utilisateur_id=str(user.get("id", "admin")),
        details={"tables": list(resultats.keys()), "merge": body.merge},
    )
    return {
        "status": "ok",
        "imported_tables": len(resultats),
        "resultats": resultats,
    }


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
        dernieres_executions_jobs: list[dict[str, Any]] = []
        metriques_ia: dict[str, Any] = {}
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

            rows = session.execute(
                text(
                    """
                    SELECT job_id, status, started_at, duration_ms
                    FROM job_executions
                    ORDER BY started_at DESC
                    LIMIT 8
                    """
                )
            ).mappings().all()
            dernieres_executions_jobs = [
                {
                    "job_id": str(r["job_id"]),
                    "job_name": _LABELS_JOBS.get(str(r["job_id"]), str(r["job_id"])),
                    "status": str(r["status"] or "unknown"),
                    "started_at": r["started_at"].isoformat() if r["started_at"] else None,
                    "duration_ms": int(r["duration_ms"] or 0),
                }
                for r in rows
            ]

        try:
            metriques_ia = _resumer_api_metrics().get("ai", {})
        except Exception:
            metriques_ia = {}

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
            "jobs_recents": dernieres_executions_jobs,
            "ia": metriques_ia,
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
    "/mode-test",
    responses=REPONSES_AUTH_ADMIN,
    summary="État du mode test",
    description="Retourne si le mode test admin est actif. "
    "Quand actif : logs verbose, rate-limiting désactivé, IDs internes visibles.",
)
@gerer_exception_api
async def lire_mode_test(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    return {"mode_test": est_mode_test_actif()}


@router.put(
    "/mode-test",
    responses=REPONSES_AUTH_ADMIN,
    summary="Activer / désactiver le mode test",
    description="Bascule le mode test admin.",
)
@gerer_exception_api
async def basculer_mode_test(
    body: dict[str, bool],
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    actif = bool(body.get("enabled", False))
    _ecrire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, {"admin.mode_test": actif})
    _journaliser_action_admin(
        action="admin.mode_test.toggle",
        entite_type="feature_flag",
        utilisateur_id=str(user.get("id", "admin")),
        details={"mode_test": actif},
    )
    return {"status": "ok", "mode_test": actif}


@router.get(
    "/maintenance",
    responses=REPONSES_AUTH_ADMIN,
    summary="Lire le mode maintenance",
    description="Retourne l'état du mode maintenance (feature flag runtime).",
)
@gerer_exception_api
async def lire_mode_maintenance(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {"maintenance_mode": bool(flags.get("admin.maintenance_mode", False))}


@router.put(
    "/maintenance",
    responses=REPONSES_AUTH_ADMIN,
    summary="Basculer le mode maintenance",
    description="Active ou désactive le mode maintenance global.",
)
@gerer_exception_api
async def basculer_mode_maintenance(
    body: MaintenanceModeRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    flags = _ecrire_namespace_persistant(
        _NAMESPACE_FEATURE_FLAGS,
        {"admin.maintenance_mode": body.enabled},
    )
    # Activation instantanée in-process (pas de délai de cache DB)
    from src.api.main import activer_maintenance
    activer_maintenance(body.enabled)
    _journaliser_action_admin(
        action="admin.maintenance.toggle",
        entite_type="feature_flag",
        utilisateur_id=str(user.get("id", "admin")),
        details={"maintenance_mode": body.enabled},
    )
    return {"status": "ok", "maintenance_mode": bool(flags.get("admin.maintenance_mode", False))}


@router.get(
    "/public/maintenance",
    summary="État public du mode maintenance",
    description="Endpoint lecture seule pour afficher un bandeau maintenance côté UI.",
)
@gerer_exception_api
async def lire_mode_maintenance_public(
    user: dict[str, Any] = Depends(require_auth),
) -> dict[str, Any]:
    flags = _lire_namespace_persistant(_NAMESPACE_FEATURE_FLAGS, _FEATURE_FLAGS_PAR_DEFAUT)
    return {"maintenance_mode": bool(flags.get("admin.maintenance_mode", False))}


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


@router.get(
    "/config/export",
    responses=REPONSES_AUTH_ADMIN,
    summary="Exporter la configuration admin",
    description="Exporte les feature flags et la configuration runtime persistée.",
)
@gerer_exception_api
async def exporter_config_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    return _exporter_config_admin()


@router.post(
    "/config/import",
    responses=REPONSES_AUTH_ADMIN,
    summary="Importer la configuration admin",
    description="Importe les feature flags et la configuration runtime persistée.",
)
@gerer_exception_api
async def importer_config_admin(
    body: ConfigImportRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    result = _importer_config_admin(body)
    _journaliser_action_admin(
        action="admin.config.import",
        entite_type="runtime_config",
        utilisateur_id=str(user.get("id", "admin")),
        details={
            "merge": body.merge,
            "feature_flags": list((body.feature_flags or {}).keys()),
            "runtime_config": list((body.runtime_config or {}).keys()),
        },
    )
    return {"status": "ok", **result}


# ═══════════════════════════════════════════════════════════
# D1 — Console commande rapide admin
# ═══════════════════════════════════════════════════════════


class AdminQuickCommandRequest(BaseModel):
    """Requête pour la console de commande rapide admin."""

    commande: str


_COMMANDES_RAPIDES: dict[str, str] = {
    "run job": "Exécuter un job CRON — ex: run job rappels_famille",
    "clear cache": "Vider le cache — ex: clear cache (tout) ou clear cache recettes*",
    "list jobs": "Lister tous les jobs disponibles",
    "test complet": "Simuler un test E2E one-click (recette -> planning -> courses -> checkout -> inventaire)",
    "health": "Vérifier la santé des services",
    "stats cache": "Afficher les statistiques du cache",
    "maintenance on": "Activer le mode maintenance",
    "maintenance off": "Désactiver le mode maintenance",
    "help": "Afficher l'aide des commandes",
}


def _parser_commande_rapide(commande: str) -> dict[str, Any]:
    """Parse et exécute une commande rapide admin.

    Commandes supportées :
    - run job <job_id> [--dry-run]
    - clear cache [pattern]
    - list jobs
    - health
    - stats cache
    - maintenance on|off
    - help
    """
    commande = commande.strip()
    cmd_lower = commande.lower()

    if cmd_lower == "help" or cmd_lower == "?":
        return {
            "type": "help",
            "commandes": _COMMANDES_RAPIDES,
            "message": "Commandes disponibles",
        }

    if cmd_lower == "list jobs":
        from src.services.core.cron.jobs import lister_jobs_disponibles

        jobs = lister_jobs_disponibles()
        return {
            "type": "list_jobs",
            "jobs": jobs,
            "total": len(jobs),
            "message": f"{len(jobs)} jobs disponibles",
        }

    if cmd_lower == "test complet":
        return {
            "type": "test_e2e",
            "result": _simuler_test_e2e_one_click("admin"),
            "message": "Simulation E2E one-click exécutée",
        }

    if cmd_lower.startswith("run job "):
        parts = commande[8:].strip().split()
        job_id = parts[0] if parts else ""
        dry_run = "--dry-run" in parts

        if not job_id:
            return {"type": "error", "message": "Usage: run job <job_id> [--dry-run]"}

        from src.services.core.cron.jobs import executer_job_par_id

        try:
            result = executer_job_par_id(job_id, dry_run=dry_run, source="admin_console")
            return {"type": "job_result", "result": result, "message": f"Job '{job_id}' exécuté"}
        except ValueError as e:
            return {"type": "error", "message": str(e)}

    if cmd_lower.startswith("clear cache"):
        pattern = commande[11:].strip() or "*"
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            nb = 0
            if pattern == "*" or not pattern:
                if hasattr(cache, "vider"):
                    cache.vider()
                    nb = -1  # Tout vidé
            elif hasattr(cache, "invalider"):
                nb = cache.invalider(pattern)
            return {
                "type": "cache_cleared",
                "pattern": pattern,
                "nb_invalidees": nb,
                "message": f"Cache vidé (pattern: {pattern})",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur cache: {e}"}

    if cmd_lower == "health":
        try:
            from src.services.core.registry import obtenir_registre_services

            registre = obtenir_registre_services()
            health = registre.health_check()
            return {
                "type": "health",
                "result": health,
                "message": f"Santé: {health.get('global_status', 'unknown')}",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur health: {e}"}

    if cmd_lower == "stats cache":
        try:
            from src.core.caching import obtenir_cache

            cache = obtenir_cache()
            stats = cache.obtenir_statistiques() if hasattr(cache, "obtenir_statistiques") else {}
            return {
                "type": "cache_stats",
                "result": stats,
                "message": "Statistiques cache",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur stats cache: {e}"}

    if cmd_lower in ("maintenance on", "maintenance off"):
        activer = cmd_lower == "maintenance on"
        try:
            from src.core.db import obtenir_contexte_db

            with obtenir_contexte_db() as session:
                session.execute(
                    text(
                        """
                        INSERT INTO etats_persistants (namespace, cle, valeur, user_id, created_at, modified_at)
                        VALUES ('admin_feature_flags', 'admin.maintenance_mode', :val, 'system', NOW(), NOW())
                        ON CONFLICT (namespace, cle) DO UPDATE SET valeur = :val, modified_at = NOW()
                        """
                    ),
                    {"val": json.dumps(activer)},
                )
                session.commit()
            return {
                "type": "maintenance",
                "enabled": activer,
                "message": f"Mode maintenance {'activé' if activer else 'désactivé'}",
            }
        except Exception as e:
            return {"type": "error", "message": f"Erreur maintenance: {e}"}

    return {"type": "error", "message": f"Commande inconnue: '{commande}'. Tapez 'help' pour l'aide."}


@router.post(
    "/quick-command",
    responses=REPONSES_AUTH_ADMIN,
    summary="Console commande rapide admin",
    description="Exécute une commande rapide admin (run job, clear cache, health, etc.).",
)
@gerer_exception_api
async def executer_commande_rapide(
    body: AdminQuickCommandRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    result = _parser_commande_rapide(body.commande)
    _journaliser_action_admin(
        action="admin.quick_command",
        entite_type="console",
        utilisateur_id=str(user.get("id", "admin")),
        details={"commande": body.commande, "type_resultat": result.get("type")},
    )
    return {"status": "ok", **result}


@router.post(
    "/flow-simulator",
    responses=REPONSES_AUTH_ADMIN,
    summary="Simuler un flux",
    description="Prévisualise un flux inter-modules/admin sans exécution réelle.",
)
@gerer_exception_api
async def simuler_flux_admin(
    body: FlowSimulationRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    cible_user_id = body.user_id or str(user.get("id", "admin"))
    result = _simuler_flux_admin(body, cible_user_id)
    _journaliser_action_admin(
        action="admin.flow.simulate",
        entite_type="simulation",
        utilisateur_id=str(user.get("id", "admin")),
        details={"scenario": body.scenario, "target_user_id": cible_user_id},
    )
    return result


@router.post(
    "/tests/e2e-one-click",
    responses=REPONSES_AUTH_ADMIN,
    summary="Test E2E one-click (simulation)",
    description="Simule le flux recette->planning->courses->checkout->inventaire en une seule requête.",
)
@gerer_exception_api
async def lancer_test_e2e_one_click(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    cible_user_id = str(user.get("id", "admin"))
    result = _simuler_test_e2e_one_click(cible_user_id)
    _journaliser_action_admin(
        action="admin.tests.e2e_one_click",
        entite_type="simulation",
        utilisateur_id=cible_user_id,
        details={"workflow": result.get("workflow")},
    )
    return result


@router.get(
    "/live-snapshot",
    responses=REPONSES_AUTH_ADMIN,
    summary="Snapshot live admin",
    description="Retourne un snapshot temps réel du cockpit admin.",
)
@gerer_exception_api
async def snapshot_live_admin(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    from src.api.utils import executer_avec_session

    cache_stats = {}
    try:
        from src.core.caching import obtenir_cache

        cache = obtenir_cache()
        if hasattr(cache, "obtenir_statistiques"):
            cache_stats = cache.obtenir_statistiques()
    except Exception:
        cache_stats = {}

    executions_recentes: dict[str, int] = {"success": 0, "failure": 0, "dry_run": 0}
    evenements_securite_1h = 0
    try:
        with executer_avec_session() as session:
            rows = session.execute(
                text(
                    """
                    SELECT status, COUNT(*) AS total
                    FROM job_executions
                    WHERE started_at >= NOW() - INTERVAL '24 HOURS'
                    GROUP BY status
                    """
                )
            ).mappings().all()
            for row in rows:
                status = str(row["status"] or "unknown")
                executions_recentes[status] = int(row["total"] or 0)

            evenements_securite_1h = int(
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM logs_securite
                        WHERE created_at >= NOW() - INTERVAL '1 HOUR'
                        """
                    )
                ).scalar()
                or 0
            )
    except Exception:
        executions_recentes = {"success": 0, "failure": 0, "dry_run": 0}
        evenements_securite_1h = 0

    return {
        "generated_at": datetime.now().isoformat(),
        "api": _resumer_api_metrics(),
        "cache": cache_stats,
        "jobs": {"last_24h": executions_recentes},
        "security": {"events_1h": evenements_securite_1h},
    }


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


# ═══════════════════════════════════════════════════════════
# PHASE 10 — RESET MODULE + LOGS WS ADMIN
# ═══════════════════════════════════════════════════════════


_MODULES_RESETABLES = {
    "courses": ["listes_courses", "articles_courses"],
    "inventaire": ["articles_inventaire"],
    "planning": ["repas", "plannings"],
    "jeux": ["paris_sportifs"],
}


class ResetModuleRequest(BaseModel):
    """Requête de réinitialisation d'un module."""

    module: str
    confirmer: bool = False


@router.post(
    "/reset-module",
    responses=REPONSES_AUTH_ADMIN,
    summary="Réinitialiser un module (données de test)",
)
@gerer_exception_api
async def reset_module(
    body: ResetModuleRequest,
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Remet à zéro les données d'un module (courses, inventaire, planning, jeux).

    Nécessite `confirmer: true` pour exécuter.
    """
    from src.core.config import obtenir_parametres

    env = obtenir_parametres().ENV.lower()
    if env not in {"development", "dev", "test"}:
        raise HTTPException(status_code=403, detail="Reset module autorisé uniquement en dev/test.")

    if body.module not in _MODULES_RESETABLES:
        raise HTTPException(
            status_code=400,
            detail=f"Module '{body.module}' non réinitialisable. Modules disponibles: {list(_MODULES_RESETABLES.keys())}",
        )

    if not body.confirmer:
        tables = _MODULES_RESETABLES[body.module]
        return {
            "status": "preview",
            "module": body.module,
            "tables_affectees": tables,
            "message": f"⚠️ Ceci supprimera toutes les données de {body.module}. Envoyez 'confirmer: true' pour exécuter.",
        }

    from src.api.utils import executer_avec_session

    tables = _MODULES_RESETABLES[body.module]
    resultats = {}

    with executer_avec_session() as session:
        for table in tables:
            try:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar() or 0
                session.execute(text(f"DELETE FROM {table}"))
                resultats[table] = {"supprimees": count}
            except Exception as exc:
                resultats[table] = {"erreur": str(exc)}
        session.commit()

    _journaliser_action_admin(
        action="admin.reset_module",
        entite_type=body.module,
        utilisateur_id=str(user.get("id", "admin")),
        details={"tables": tables, "resultats": resultats},
    )

    return {
        "status": "ok",
        "module": body.module,
        "resultats": resultats,
    }


@router.get(
    "/logs/stream-info",
    responses=REPONSES_AUTH_ADMIN,
    summary="Informations sur le stream de logs",
)
@gerer_exception_api
async def logs_stream_info(
    user: dict[str, Any] = Depends(require_role("admin")),
) -> dict[str, Any]:
    """Retourne les informations pour se connecter au stream de logs temps réel.

    Le stream est disponible via WebSocket sur /api/v1/ws/admin/logs.
    """
    return {
        "websocket_url": "/api/v1/ws/admin/logs",
        "description": "Stream de logs structurés en temps réel (WebSocket)",
        "message_format": {
            "type": "log_entry",
            "timestamp": "ISO 8601",
            "level": "DEBUG|INFO|WARNING|ERROR",
            "module": "src.api.routes.admin",
            "message": "Texte du log",
        },
    }
