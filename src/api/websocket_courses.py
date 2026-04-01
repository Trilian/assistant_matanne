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

from src.api.utils import executer_async, executer_avec_session

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
                "connected_at": datetime.now(UTC).isoformat(),
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

                # Persister les changements en base de données
                await _persist_change(liste_id, action, data)

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
# PERSISTANCE EN BASE
# ═══════════════════════════════════════════════════════════


async def _persist_change(liste_id: int, action: str, data: dict[str, Any]) -> None:
    """Persiste un changement WebSocket en base de données."""
    from src.core.models import ArticleCourses, Ingredient, ListeCourses

    try:
        if action == WSMessageType.ITEM_CHECKED:
            item_id = data.get("item_id")
            checked = data.get("checked", False)

            def _toggle():
                with executer_avec_session() as session:
                    article = session.query(ArticleCourses).filter(ArticleCourses.id == item_id).first()
                    if article:
                        article.achete = checked
                        article.achete_le = datetime.now(UTC) if checked else None
                        session.commit()

            await executer_async(_toggle)

        elif action == WSMessageType.ITEM_REMOVED:
            item_id = data.get("item_id")

            def _remove():
                with executer_avec_session() as session:
                    article = session.query(ArticleCourses).filter(
                        ArticleCourses.id == item_id,
                        ArticleCourses.liste_id == liste_id,
                    ).first()
                    if article:
                        session.delete(article)
                        session.commit()

            await executer_async(_remove)

        elif action == WSMessageType.ITEM_ADDED:
            item = data.get("item", {})
            nom = item.get("nom", "")
            quantite = item.get("quantite", 1.0)
            unite = item.get("unite", "pièce")
            categorie = item.get("categorie")

            def _add():
                with executer_avec_session() as session:
                    ingredient = session.query(Ingredient).filter(Ingredient.nom == nom).first()
                    if not ingredient:
                        ingredient = Ingredient(nom=nom, unite=unite)
                        session.add(ingredient)
                        session.flush()
                    article = ArticleCourses(
                        liste_id=liste_id,
                        ingredient_id=ingredient.id,
                        quantite_necessaire=quantite,
                        rayon_magasin=categorie,
                    )
                    session.add(article)
                    session.commit()

            await executer_async(_add)

        elif action == WSMessageType.ITEM_UPDATED:
            item_id = data.get("item_id")
            updates = data.get("updates", {})

            def _update():
                with executer_avec_session() as session:
                    article = session.query(ArticleCourses).filter(
                        ArticleCourses.id == item_id,
                        ArticleCourses.liste_id == liste_id,
                    ).first()
                    if article:
                        if "quantite" in updates:
                            article.quantite_necessaire = updates["quantite"]
                        if "priorite" in updates:
                            article.priorite = updates["priorite"]
                        if "categorie" in updates:
                            article.rayon_magasin = updates["categorie"]
                        if "notes" in updates:
                            article.notes = updates["notes"]
                        session.commit()

            await executer_async(_update)

        elif action == WSMessageType.LIST_RENAMED:
            new_name = data.get("new_name", "")

            def _rename():
                with executer_avec_session() as session:
                    liste = session.query(ListeCourses).filter(ListeCourses.id == liste_id).first()
                    if liste and new_name:
                        liste.nom = new_name
                        session.commit()

            await executer_async(_rename)

    except Exception as e:
        logger.error(f"Erreur persistance WS action={action} liste={liste_id}: {e}")


# ═══════════════════════════════════════════════════════════
# FALLBACK HTTP POLLING (Phase A2)
# ═══════════════════════════════════════════════════════════

# Séquence de changements par liste pour le polling HTTP
_change_sequences: dict[int, list[dict[str, Any]]] = defaultdict(list)
_MAX_CHANGES_HISTORY = 200


@router.get("/courses/{liste_id}/poll")
async def poll_courses_changes(
    liste_id: int,
    since_seq: int = Query(0, description="Séquence depuis laquelle récupérer les changements"),
) -> dict[str, Any]:
    """
    Fallback HTTP polling pour les clients qui ne supportent pas WebSocket.

    Retourne les changements depuis le numéro de séquence donné.
    Utilisé quand le WebSocket est bloqué (proxy, 3G, etc.).
    """
    changes = _change_sequences.get(liste_id, [])
    new_changes = [c for c in changes if c.get("seq", 0) > since_seq]
    current_seq = changes[-1]["seq"] if changes else 0
    users = _manager.get_connected_users(liste_id)

    return {
        "changes": new_changes,
        "current_seq": current_seq,
        "users": users,
    }


@router.post("/courses/{liste_id}/action")
async def post_courses_action(
    liste_id: int,
    action_data: dict[str, Any],
    user_id: str = Query(..., description="ID utilisateur"),
    username: str = Query("Anonyme", description="Nom affiché"),
) -> dict[str, Any]:
    """
    Endpoint REST pour appliquer un changement sur une liste de courses.

    Fallback quand le WebSocket n'est pas disponible.
    Le changement est persisté et broadcasté aux clients WebSocket connectés.
    """
    action = action_data.get("action", "")

    if action not in [
        WSMessageType.ITEM_ADDED,
        WSMessageType.ITEM_REMOVED,
        WSMessageType.ITEM_CHECKED,
        WSMessageType.ITEM_UPDATED,
        WSMessageType.LIST_RENAMED,
    ]:
        return {"error": f"Action inconnue: {action}", "success": False}

    # Persister en base
    await _persist_change(liste_id, action, action_data)

    # Enregistrer dans la séquence de polling
    seq = len(_change_sequences[liste_id]) + 1
    change_record = {
        "seq": seq,
        "type": WSMessageType.SYNC,
        "action": action,
        "user_id": user_id,
        "username": username,
        "timestamp": datetime.now(UTC).isoformat(),
        **{k: v for k, v in action_data.items() if k != "action"},
    }
    _change_sequences[liste_id].append(change_record)

    # Limiter l'historique
    if len(_change_sequences[liste_id]) > _MAX_CHANGES_HISTORY:
        _change_sequences[liste_id] = _change_sequences[liste_id][-_MAX_CHANGES_HISTORY:]

    # Notifier les clients WebSocket
    await _manager.broadcast(liste_id, change_record, exclude_user=user_id)

    return {"success": True, "seq": seq}


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
