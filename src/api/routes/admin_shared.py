"""
Module partagé pour les routes admin.

Contient les dépendances, schémas, constantes et helpers utilisés
par tous les sous-modules admin.
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
    canal: Literal["ntfy", "push", "email", "telegram"]
    message: str
    email: str | None = None
    numero_destinataire: str | None = None
    titre: str = "Test Matanne"


class NotificationTestAllRequest(BaseModel):
    message: str
    email: str | None = None
    titre: str = "Test multi-canal Matanne"
    inclure_telegram: bool = True


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
    "s16_resume_weekend_telegram": "S16.3 Résumé weekend suggestions Telegram (ven 18h00)",
    "s16_rappel_entretien_telegram": "S16.6 Rappel entretien maison Telegram (08h10)",
    "s16_bilan_nutrition_telegram": "S16.5 Bilan nutrition semaine Telegram (dim 20h30)",
    "s16_rapport_famille_mensuel": "S16.8 Rapport mensuel famille complet email/PDF (1er 09h00)",
    "s16_rapport_maison_trimestriel": "S16.9 Rapport trimestriel maison email/PDF (T+1 09h10)",
}

_NOTIFICATION_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "telegram": [
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


