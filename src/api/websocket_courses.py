"""
WebSocket pour collaboration temps réel sur les courses.

Permet à plusieurs utilisateurs de modifier la même liste de courses
simultanément avec synchronisation en temps réel.

Fonctionnalités:
- Broadcast des modifications (ajout/suppression/coche d'articles)
- Présence des utilisateurs connectés
- Reconnexion automatique côté client

Usage:
    # Côté client (JS):
    const ws = new WebSocket("ws://localhost:8000/api/v1/ws/courses/5");
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        // Mettre à jour l'UI selon data.type
    };

    # Envoyer une modification:
    ws.send(JSON.stringify({
        "action": "item_checked",
        "item_id": 12,
        "checked": true
    }));
"""

import asyncio
import json
import logging
from collections import defaultdict
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["WebSocket"])


# ═══════════════════════════════════════════════════════════
# TYPES DE MESSAGES
# ═══════════════════════════════════════════════════════════


class WSMessageType(StrEnum):
    """Types de messages WebSocket."""

    # Client → Serveur
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_CHECKED = "item_checked"
    ITEM_UPDATED = "item_updated"
    LIST_RENAMED = "list_renamed"
    USER_TYPING = "user_typing"
    PING = "ping"

    # Serveur → Client
    SYNC = "sync"
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"
    USERS_LIST = "users_list"
    ERROR = "error"
    PONG = "pong"


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE DE CONNEXIONS
# ═══════════════════════════════════════════════════════════


class ConnectionManager:
    """
    Gestionnaire de connexions WebSocket par liste de courses.

    Maintient la liste des connexions actives par liste_id
    et gère le broadcast des messages à tous les clients d'une liste.
    """

    def __init__(self):
        # {liste_id: {user_id: WebSocket}}
        self._connexions: dict[int, dict[str, WebSocket]] = defaultdict(dict)
        # {liste_id: {user_id: {"username": str, "connected_at": datetime}}}
        self._users: dict[int, dict[str, dict[str, Any]]] = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def connect(
        self,
        websocket: WebSocket,
        liste_id: int,
        user_id: str,
        username: str = "Anonyme",
    ) -> None:
        """Connecte un utilisateur à une liste."""
        await websocket.accept()

        async with self._lock:
            self._connexions[liste_id][user_id] = websocket
            self._users[liste_id][user_id] = {
                "username": username,
                "connected_at": datetime.now(UTC),
            }

        logger.info(f"🔌 WS: {username} ({user_id}) connecté à liste #{liste_id}")

        # Notifier les autres utilisateurs
        await self.broadcast(
            liste_id,
            {
                "type": WSMessageType.USER_JOINED,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now(UTC).isoformat(),
            },
            exclude_user=user_id,
        )

        # Envoyer la liste des utilisateurs connectés au nouvel arrivant
        await self.send_personal(
            websocket,
            {
                "type": WSMessageType.USERS_LIST,
                "users": [{"user_id": uid, **info} for uid, info in self._users[liste_id].items()],
            },
        )

    async def disconnect(self, liste_id: int, user_id: str) -> None:
        """Déconnecte un utilisateur d'une liste."""
        async with self._lock:
            username = self._users[liste_id].get(user_id, {}).get("username", "Inconnu")
            self._connexions[liste_id].pop(user_id, None)
            self._users[liste_id].pop(user_id, None)

            # Nettoyer les listes vides
            if not self._connexions[liste_id]:
                del self._connexions[liste_id]
            if not self._users[liste_id]:
                del self._users[liste_id]

        logger.info(f"🔌 WS: {username} ({user_id}) déconnecté de liste #{liste_id}")

        # Notifier les autres
        await self.broadcast(
            liste_id,
            {
                "type": WSMessageType.USER_LEFT,
                "user_id": user_id,
                "username": username,
                "timestamp": datetime.now(UTC).isoformat(),
            },
        )

    async def broadcast(
        self,
        liste_id: int,
        message: dict[str, Any],
        exclude_user: str | None = None,
    ) -> None:
        """Envoie un message à tous les utilisateurs d'une liste."""
        connexions = self._connexions.get(liste_id, {})

        tasks = []
        for uid, ws in connexions.items():
            if uid != exclude_user:
                tasks.append(self._safe_send(ws, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_personal(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Envoie un message à un client spécifique."""
        await self._safe_send(websocket, message)

    async def _safe_send(self, websocket: WebSocket, message: dict[str, Any]) -> None:
        """Envoie un message avec gestion d'erreur."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.warning(f"Erreur envoi WS: {e}")

    def get_connected_users(self, liste_id: int) -> list[dict[str, Any]]:
        """Retourne la liste des utilisateurs connectés à une liste."""
        return [{"user_id": uid, **info} for uid, info in self._users.get(liste_id, {}).items()]

    def get_connection_count(self, liste_id: int) -> int:
        """Retourne le nombre de connexions pour une liste."""
        return len(self._connexions.get(liste_id, {}))


# Instance globale
_manager = ConnectionManager()


def get_ws_manager() -> ConnectionManager:
    """Retourne le gestionnaire de connexions WebSocket."""
    return _manager


# ═══════════════════════════════════════════════════════════
# ENDPOINT WEBSOCKET
# ═══════════════════════════════════════════════════════════


@router.websocket("/courses/{liste_id}")
async def websocket_courses(
    websocket: WebSocket,
    liste_id: int,
    user_id: str = Query(..., description="ID utilisateur"),
    username: str = Query("Anonyme", description="Nom affiché"),
):
    """
    WebSocket pour collaboration temps réel sur une liste de courses.

    Protocole:
    -----------

    Messages Client → Serveur:
    - item_added: {"action": "item_added", "item": {...}}
    - item_removed: {"action": "item_removed", "item_id": 123}
    - item_checked: {"action": "item_checked", "item_id": 123, "checked": true}
    - item_updated: {"action": "item_updated", "item_id": 123, "updates": {...}}
    - list_renamed: {"action": "list_renamed", "new_name": "..."}
    - user_typing: {"action": "user_typing", "typing": true}
    - ping: {"action": "ping"}

    Messages Serveur → Clients:
    - sync: Même structure que les messages clients, broadcasté à tous
    - user_joined: {"type": "user_joined", "user_id": "...", "username": "..."}
    - user_left: {"type": "user_left", "user_id": "...", "username": "..."}
    - users_list: {"type": "users_list", "users": [...]}
    - error: {"type": "error", "message": "..."}
    - pong: {"type": "pong"}

    Example:
        ws://localhost:8000/api/v1/ws/courses/5?user_id=abc123&username=Anne
    """
    await _manager.connect(websocket, liste_id, user_id, username)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action", "")

            if action == "ping":
                await _manager.send_personal(websocket, {"type": WSMessageType.PONG})
                continue

            # Valider et traiter l'action
            if action in [
                WSMessageType.ITEM_ADDED,
                WSMessageType.ITEM_REMOVED,
                WSMessageType.ITEM_CHECKED,
                WSMessageType.ITEM_UPDATED,
                WSMessageType.LIST_RENAMED,
                WSMessageType.USER_TYPING,
            ]:
                # Broadcast aux autres utilisateurs
                message = {
                    "type": WSMessageType.SYNC,
                    "action": action,
                    "user_id": user_id,
                    "username": username,
                    "timestamp": datetime.now(UTC).isoformat(),
                    **{k: v for k, v in data.items() if k != "action"},
                }
                await _manager.broadcast(liste_id, message, exclude_user=user_id)

                # TODO: Persister les changements en base de données
                # await _persist_change(liste_id, action, data)

            else:
                await _manager.send_personal(
                    websocket,
                    {
                        "type": WSMessageType.ERROR,
                        "message": f"Action inconnue: {action}",
                    },
                )

    except WebSocketDisconnect:
        await _manager.disconnect(liste_id, user_id)
    except Exception as e:
        logger.error(f"Erreur WebSocket courses: {e}")
        await _manager.disconnect(liste_id, user_id)


# ═══════════════════════════════════════════════════════════
# UTILITAIRES
# ═══════════════════════════════════════════════════════════


async def notifier_changement_courses(
    liste_id: int,
    action: WSMessageType,
    data: dict[str, Any],
    source_user_id: str | None = None,
) -> None:
    """
    Notifie tous les clients WebSocket d'un changement sur une liste.

    Permet aux routes REST de notifier les clients WebSocket
    quand une modification est faite via l'API REST.

    Args:
        liste_id: ID de la liste modifiée
        action: Type d'action
        data: Données du changement
        source_user_id: ID de l'utilisateur ayant fait le changement (exclu du broadcast)
    """
    message = {
        "type": WSMessageType.SYNC,
        "action": action,
        "source": "api",
        "timestamp": datetime.now(UTC).isoformat(),
        **data,
    }
    await _manager.broadcast(liste_id, message, exclude_user=source_user_id)
