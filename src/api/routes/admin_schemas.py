"""Schémas Pydantic pour les routes admin."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel


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


class JobRunAllRequest(BaseModel):
    dry_run: bool = False
    continuer_sur_erreur: bool = True
    inclure_jobs_inactifs: bool = False
    force: bool = False


class JobScheduleUpdateRequest(BaseModel):
    # Format attendu: "minute heure jour_du_mois mois jour_semaine"
    cron: str


class NotificationSimulationRequest(BaseModel):
    canal: Literal["ntfy", "push", "email", "telegram"]
    template_id: str
    dry_run: bool = True
    payload: dict[str, Any] = {}
