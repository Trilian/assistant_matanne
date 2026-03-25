"""
Package WebSocket — Collaboration temps réel multi-modules.

Modules:
- manager: ConnectionManager générique partagé
- types: Types de messages WebSocket extensibles
- planning: Collaboration sur le planning repas
- notes: Collaboration sur les notes
- projets: Collaboration sur les projets Kanban
"""

from .manager import ConnectionManager, get_manager
from .notes import router as ws_notes_router
from .planning import router as ws_planning_router
from .projets import router as ws_projets_router
from .types import WSBaseMessageType

__all__ = [
    "ConnectionManager",
    "get_manager",
    "WSBaseMessageType",
    "ws_planning_router",
    "ws_notes_router",
    "ws_projets_router",
]
