"""
Gestionnaire de connexions WebSocket générique.

Partagé entre tous les modules de collaboration temps réel.
Paramétré par un type de ressource (liste, planning, note, projet).
"""

import asyncio
import logging
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Gestionnaire de connexions WebSocket générique.

    Maintient les connexions actives par resource_id
    et gère le broadcast des messages.
    """

    def __init__(self, resource_type: str = "resource"):
        self.resource_type = resource_type
        self._connexions: dict[int, dict[str, WebSocket]] = defaultdict(dict)
        self._users: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        resource_id: int,
        user_id: str,
        username: str = "Anonyme",
    ) -> None:
        """Connecte un utilisateur à une ressource."""
        await websocket.accept()

        async with self._lock:
            self._connexions[resource_id][user_id] = websocket
            self._users[resource_id][user_id] = {
                "username": username,
                "connected_at": datetime.now(UTC).isoformat(),
            }

        logger.info(
            f"WS {self.resource_type}: {username} ({user_id}) connecté à #{resource_id}"
        )

        await self.broadcast(
            resource_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            exclude_user=user_id,
        )

        await self.send_personal(
            websocket,
            {
                "type": "users_list",
                "users": [
                    {"user_id": uid, **info}
                    for uid, info in self._users[resource_id].items()
                ],
            },
        )

    async def disconnect(self, resource_id: int, user_id: str) -> None:
        """Déconnecte un utilisateur."""
        async with self._lock:
            username = (
                self._users[resource_id].get(user_id, {}).get("username", "Inconnu")
            )
            self._connexions[resource_id].pop(user_id, None)
            self._users[resource_id].pop(user_id, None)

            if not self._connexions[resource_id]:
                del self._connexions[resource_id]
            if not self._users[resource_id]:
                del self._users[resource_id]

        logger.info(
            f"WS {self.resource_type}: {username} ({user_id}) déconnecté de #{resource_id}"
        )

        await self.broadcast(
            resource_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def broadcast(
        self,
        resource_id: int,
        message: dict[str, Any],
        exclude_user: str | None = None,
    ) -> None:
        """Envoie un message à tous les utilisateurs d'une ressource."""
        connexions = self._connexions.get(resource_id, {})
        tasks: list[asyncio.Task[None]] = []
        for uid, ws in connexions.items():
            if uid != exclude_user:
                tasks.append(asyncio.ensure_future(self._safe_send(ws, message)))
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_personal(
        self, websocket: WebSocket, message: dict[str, Any]
    ) -> None:
        """Envoie un message à un client spécifique."""
        await self._safe_send(websocket, message)

    async def _safe_send(
        self, websocket: WebSocket, message: dict[str, Any]
    ) -> None:
        """Envoie un message avec gestion d'erreur."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Erreur envoi WS {self.resource_type}: {e}")

    def get_connected_users(self, resource_id: int) -> list[dict[str, Any]]:
        """Retourne la liste des utilisateurs connectés."""
        return [
            {"user_id": uid, **info}
            for uid, info in self._users.get(resource_id, {}).items()
        ]

    def get_connection_count(self, resource_id: int) -> int:
        """Retourne le nombre de connexions pour une ressource."""
        return len(self._connexions.get(resource_id, {}))


# ═══════════════════════════════════════════════════════════
# INSTANCES GLOBALES PAR MODULE
# ═══════════════════════════════════════════════════════════

_managers: dict[str, ConnectionManager] = {}


def get_manager(resource_type: str) -> ConnectionManager:
    """Obtient ou crée un ConnectionManager pour un type de ressource."""
    if resource_type not in _managers:
        _managers[resource_type] = ConnectionManager(resource_type)
    return _managers[resource_type]
