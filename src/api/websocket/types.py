"""
Types de messages WebSocket partagés entre tous les modules.
"""

from enum import StrEnum


class WSBaseMessageType(StrEnum):
    """Types de messages de base (communs à tous les modules)."""

    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USERS_LIST = "users_list"
    PING = "ping"
    PONG = "pong"
    ERROR = "error"
    SYNC = "sync"


class WSPlanningMessageType(StrEnum):
    """Types de messages pour la collaboration planning."""

    REPAS_ADDED = "repas_added"
    REPAS_UPDATED = "repas_updated"
    REPAS_REMOVED = "repas_removed"
    SLOT_SWAPPED = "slot_swapped"


class WSNotesMessageType(StrEnum):
    """Types de messages pour la collaboration notes."""

    CONTENT_UPDATED = "content_updated"
    CURSOR_MOVED = "cursor_moved"
    TITLE_CHANGED = "title_changed"


class WSProjetsMessageType(StrEnum):
    """Types de messages pour la collaboration projets Kanban."""

    TACHE_MOVED = "tache_moved"
    TACHE_ADDED = "tache_added"
    TACHE_UPDATED = "tache_updated"
    TACHE_REMOVED = "tache_removed"
