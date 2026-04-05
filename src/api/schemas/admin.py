"""
Schémas Pydantic pour les routes admin (jobs, opérations, audit, infra).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# ADMIN JOBS
# ═══════════════════════════════════════════════════════════


class AdminJobResume(BaseModel):
    """Résumé d'un job planifié."""

    id: str
    nom: str
    schedule: str
    prochain_run: str | None = None
    dernier_run: str | None = None
    statut: str


class AdminJobResultat(BaseModel):
    """Résultat d'exécution d'un job."""

    job_id: str
    status: str
    duration_ms: float = 0.0
    message: str = ""
    dry_run: bool = False


class AdminJobsRunAllResponse(BaseModel):
    """Réponse de l'exécution batch de tous les jobs."""

    mode: str = Field(description="dry_run | run")
    jobs_cibles: list[str] = Field(default_factory=list)
    total: int = 0
    succes: int = 0
    echecs: int = 0
    items: list[AdminJobResultat] = Field(default_factory=list)


class AdminJobScheduleModifie(BaseModel):
    """Réponse après modification du schedule d'un job."""

    status: str = "ok"
    job_id: str
    schedule: str
    prochain_run: str | None = None


class AdminJobLogEntry(BaseModel):
    """Entrée de log d'un job."""

    timestamp: str | None = None
    ended_at: str | None = None
    status: str
    duration_ms: int = 0
    message: str = ""
    source: str = "db"


class AdminJobLogsResponse(BaseModel):
    """Logs d'un job spécifique."""

    job_id: str
    nom: str
    logs: list[AdminJobLogEntry] = Field(default_factory=list)
    total: int = 0


class AdminJobHistoriqueEntry(BaseModel):
    """Entrée d'historique d'exécution."""

    id: int
    job_id: str
    job_name: str
    started_at: str | None = None
    ended_at: str | None = None
    duration_ms: int = 0
    status: str
    error_message: str | None = None
    output_logs: str | None = None
    triggered_by_user_id: str | None = None
    triggered_by_user_role: str | None = None


class AdminJobHistoriqueResponse(BaseModel):
    """Liste paginée de l'historique des jobs."""

    items: list[AdminJobHistoriqueEntry] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    par_page: int = 20
    pages_totales: int = 0


class DryRunComparaison(BaseModel):
    """Comparaison dry-run vs exécution réelle."""

    status: str
    started_at: str | None = None
    duration_ms: int = 0
    error_message: str | None = None


class DryRunComparaisonItem(BaseModel):
    """Élément de comparaison dry-run."""

    job_id: str
    job_name: str
    dry_run: DryRunComparaison | None = None
    run: DryRunComparaison | None = None
    comparaison: dict[str, Any] = Field(default_factory=dict)


class AdminDryRunCompareResponse(BaseModel):
    """Résultat de la comparaison dry-run vs réel."""

    generated_at: str
    fenetre_heures: int
    total: int = 0
    items: list[DryRunComparaisonItem] = Field(default_factory=list)


class AdminSimulationJourneeResponse(AdminJobsRunAllResponse):
    """Résultat de simulation d'une journée de jobs."""

    date_reference: str = ""
    fenetre: dict[str, str] = Field(default_factory=dict)
    started_at: str | None = None
    ended_at: str | None = None


# ═══════════════════════════════════════════════════════════
# ADMIN BRIDGES STATUS
# ═══════════════════════════════════════════════════════════


class AdminBridgesResumeStats(BaseModel):
    """Résumé statistique des bridges."""

    total_actions: int = 0
    operationnelles: int = 0
    indisponibles: int = 0
    taux_operationnel_pct: float = 0.0
    mode_verification: str = ""


class AdminBridgesStatusResponse(BaseModel):
    """Statut complet des bridges inter-modules."""

    phase: str = "bridges_inter_modules"
    generated_at: str
    execution_ms: float = 0.0
    statut_global: str
    resume: AdminBridgesResumeStats
    consolidation_bridges: dict[str, Any] = Field(default_factory=dict)
    items: list[dict[str, Any]] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# ADMIN OPERATIONS
# ═══════════════════════════════════════════════════════════


class AdminSanteServicesResponse(BaseModel):
    """Réponse health check des services."""

    global_status: str
    total_services: int = 0
    instantiated: int = 0
    healthy: int = 0
    erreurs: list[str] = Field(default_factory=list)
    services: dict[str, Any] = Field(default_factory=dict)
    metriques: dict[str, Any] = Field(default_factory=dict)


class AdminSchemaDiffResponse(BaseModel):
    """Résultat de la comparaison ORM ↔ DB."""

    status: str
    missing_in_db: list[Any] = Field(default_factory=list)
    extra_in_db: list[Any] = Field(default_factory=list)
    column_differences: list[Any] = Field(default_factory=list)


class AdminNotificationTestResponse(BaseModel):
    """Résultat d'un test de notification."""

    resultats: dict[str, Any] = Field(default_factory=dict)
    message: str = ""


class AdminNotificationTestAllResponse(BaseModel):
    """Résultat du test de toutes les notifications."""

    resultats: dict[str, bool] = Field(default_factory=dict)
    canaux_testes: list[str] = Field(default_factory=list)
    succes: list[str] = Field(default_factory=list)
    echecs: list[str] = Field(default_factory=list)
    message: str = ""


class AdminTemplatesNotificationsResponse(BaseModel):
    """Liste des templates de notification."""

    status: str = "ok"
    templates: dict[str, Any] = Field(default_factory=dict)
    total: int = 0


class AdminPreviewTemplateResponse(BaseModel):
    """Prévisualisation d'un template de notification."""

    status: str = "ok"
    canal: str
    template_id: str
    trigger: str = ""
    preview: str = ""
    contexte_demo: dict[str, str] = Field(default_factory=dict)


class AdminSimulerNotificationResponse(BaseModel):
    """Résultat de la simulation de notification."""

    status: str = "ok"
    dry_run: bool = True
    template: dict[str, Any] = Field(default_factory=dict)
    message: str = ""
    resultats: dict[str, bool] | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class AdminHistoriqueNotificationsResponse(BaseModel):
    """Historique des notifications envoyées."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0


class AdminQueueNotificationsResponse(BaseModel):
    """État de la file d'attente des notifications."""

    items: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0
    total_users_pending: int = 0


class AdminConfigExportResponse(BaseModel):
    """Export de la configuration admin."""

    config: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# ADMIN AUDIT
# ═══════════════════════════════════════════════════════════


class AdminAuditLogEntry(BaseModel):
    """Entrée de log d'audit."""

    id: int | None = None
    timestamp: str | None = None
    user_id: str | None = None
    action: str
    resource: str | None = None
    resource_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
    ip_address: str | None = None


class AdminAuditLogsResponse(BaseModel):
    """Liste paginée des logs d'audit."""

    items: list[AdminAuditLogEntry] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    par_page: int = 50


class AdminAuditStatsResponse(BaseModel):
    """Statistiques d'audit agrégées."""

    total_events: int = 0
    par_action: dict[str, int] = Field(default_factory=dict)
    par_resource: dict[str, int] = Field(default_factory=dict)
    periode: dict[str, str] = Field(default_factory=dict)


class AdminEventResponse(BaseModel):
    """Événement admin."""

    id: int | str | None = None
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: str | None = None
    status: str = ""


class AdminEventsListResponse(BaseModel):
    """Liste des événements admin."""

    items: list[AdminEventResponse] = Field(default_factory=list)
    total: int = 0


# ═══════════════════════════════════════════════════════════
# ADMIN INFRA
# ═══════════════════════════════════════════════════════════


class AdminCoherenceDBResponse(BaseModel):
    """Résultat du check de cohérence DB."""

    status: str
    checks: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AdminExportDBResponse(BaseModel):
    """Résultat de l'export DB JSON."""

    status: str = "ok"
    tables: dict[str, int] = Field(default_factory=dict)
    total_rows: int = 0


class AdminImportDBResponse(BaseModel):
    """Résultat de l'import DB JSON."""

    status: str = "ok"
    tables_imported: list[str] = Field(default_factory=list)
    rows_imported: int = 0
    errors: list[str] = Field(default_factory=list)


class AdminDonneesTemporellesResponse(BaseModel):
    """Données temporelles pour graphiques admin."""

    series: list[dict[str, Any]] = Field(default_factory=list)
    labels: list[str] = Field(default_factory=list)
    periode: dict[str, str] = Field(default_factory=dict)


class AdminJobHealthResponse(BaseModel):
    """Health check de l'infrastructure de jobs."""

    status: str
    scheduler_running: bool = False
    total_jobs: int = 0
    jobs_actifs: int = 0
    derniere_execution: str | None = None
    erreurs_recentes: list[str] = Field(default_factory=list)
