"""
Types et schémas pour le service d'historique des actions utilisateur.

Contient les enums et modèles Pydantic utilisés par ActionHistoryService.
"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ActionType(StrEnum):
    """Types d'actions traçables."""

    # Recettes
    RECETTE_CREATED = "recette.created"
    RECETTE_UPDATED = "recette.updated"
    RECETTE_DELETED = "recette.deleted"
    RECETTE_FAVORITED = "recette.favorited"

    # Inventaire
    INVENTAIRE_ADDED = "inventaire.added"
    INVENTAIRE_UPDATED = "inventaire.updated"
    INVENTAIRE_CONSUMED = "inventaire.consumed"
    INVENTAIRE_EXPIRED = "inventaire.expired"

    # Courses
    COURSES_LIST_CREATED = "courses.list_created"
    COURSES_ITEM_ADDED = "courses.item_added"
    COURSES_ITEM_CHECKED = "courses.item_checked"
    COURSES_LIST_ARCHIVED = "courses.list_archived"

    # Planning
    PLANNING_REPAS_ADDED = "planning.repas_added"
    PLANNING_REPAS_MOVED = "planning.repas_moved"
    PLANNING_REPAS_DELETED = "planning.repas_deleted"

    # Famille
    FAMILLE_ACTIVITY_LOGGED = "famille.activity_logged"
    FAMILLE_MILESTONE_ADDED = "famille.milestone_added"

    # Système
    SYSTEM_LOGIN = "system.login"
    SYSTEM_LOGOUT = "system.logout"
    SYSTEM_SETTINGS_CHANGED = "system.settings_changed"
    SYSTEM_EXPORT = "system.export"
    SYSTEM_IMPORT = "system.import"


class ActionEntry(BaseModel):
    """Entrée d'historique d'action."""

    id: int | None = None
    user_id: str
    user_name: str
    action_type: ActionType
    entity_type: str  # recette, inventaire, courses, etc.
    entity_id: int | None = None
    entity_name: str | None = None
    description: str
    details: dict = Field(default_factory=dict)
    old_value: dict | None = None  # Pour restauration
    new_value: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class ActionFilter(BaseModel):
    """Filtres pour la recherche d'actions."""

    user_id: str | None = None
    action_types: list[ActionType] | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    search_text: str | None = None
    limit: int = 50
    offset: int = 0


class ActionStats(BaseModel):
    """Statistiques d'activité."""

    total_actions: int = 0
    actions_today: int = 0
    actions_this_week: int = 0
    most_active_users: list[dict] = Field(default_factory=list)
    most_common_actions: list[dict] = Field(default_factory=list)
    peak_hours: list[int] = Field(default_factory=list)
