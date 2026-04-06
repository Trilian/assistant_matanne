"""
Module partagé pour les routes admin.

Contient les dépendances (rate limiting, router) et re-exporte
les schémas, constantes et helpers depuis les sous-modules dédiés.
"""

from __future__ import annotations

import collections
import logging
import os
import time
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import require_role

# ── Re-exports depuis les sous-modules ───────────────────────────────────────
from .admin_constants import (  # noqa: F401
    _FEATURE_FLAGS_PAR_DEFAUT,
    _LABELS_JOBS,
    _NAMESPACE_FEATURE_FLAGS,
    _NAMESPACE_RUNTIME_CONFIG,
    _NOTIFICATION_TEMPLATES,
    _RUNTIME_CONFIG_PAR_DEFAUT,
    _VUES_SQL_AUTORISEES,
)
from .admin_helpers import (  # noqa: F401
    _catalogue_actions_services,
    _cibles_resync,
    _construire_pdf_audit,
    _executer_action_service,
    _exporter_config_admin,
    _extraire_jobs_matin,
    _importer_config_admin,
    _lire_namespace_persistant,
    _normaliser_nom_table,
    _resumer_api_metrics,
    _serialiser_valeur_export_db,
    _simuler_flux_admin,
    _simuler_test_e2e_one_click,
    _ecrire_namespace_persistant,
    est_mode_test_actif,
)
from .admin_schemas import (  # noqa: F401
    AdminAIConsoleRequest,
    CachePurgeRequest,
    ConfigImportRequest,
    DbImportRequest,
    DesactiverUtilisateurRequest,
    EventBusReplayRequest,
    EventBusTriggerRequest,
    FeatureFlagsUpdateRequest,
    FlowSimulationRequest,
    JobInfoResponse,
    JobRunAllRequest,
    JobRunRequest,
    JobScheduleUpdateRequest,
    JobsBulkRequest,
    JobsSimulationJourneeRequest,
    MaintenanceModeRequest,
    NotificationSimulationRequest,
    NotificationTestAllRequest,
    NotificationTestRequest,
    RuntimeConfigUpdateRequest,
    SeedDataRequest,
    ServiceActionRunRequest,
    UserImpersonationRequest,
    UtilisateurAdminResponse,
)

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

    # Diffuser via WebSocket admin jobs (best-effort)
    try:
        from src.api.websocket.admin_jobs import emettre_evenement_job

        emettre_evenement_job(job_id=job_id, status=status, message=message)
    except Exception:
        pass  # Ne jamais bloquer le job pour un échec WS


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
