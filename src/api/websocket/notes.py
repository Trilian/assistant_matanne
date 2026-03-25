"""
WebSocket pour collaboration temps réel sur les notes.

Permet l'édition collaborative de notes avec indicateur de curseur
et résolution de conflits last-write-wins.
"""

import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from .manager import get_manager
from .types import WSBaseMessageType, WSNotesMessageType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["WebSocket Notes"])

NOTES_MESSAGE_TYPES = {t.value for t in WSNotesMessageType}


@router.websocket("/notes/{note_id}")
async def ws_notes(
    websocket: WebSocket,
    note_id: int,
    user: str = Query(default="anonyme"),
    username: str = Query(default="Anonyme"),
):
    """WebSocket de collaboration sur les notes."""
    manager = get_manager("notes")
    await manager.connect(websocket, note_id, user, username)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await manager.send_personal(
                    websocket,
                    {
                        "type": WSBaseMessageType.ERROR,
                        "message": "JSON invalide",
                    },
                )
                continue

            action = data.get("action", "")

            if action == WSBaseMessageType.PING:
                await manager.send_personal(
                    websocket,
                    {"type": WSBaseMessageType.PONG},
                )
                continue

            if action not in NOTES_MESSAGE_TYPES:
                await manager.send_personal(
                    websocket,
                    {
                        "type": WSBaseMessageType.ERROR,
                        "message": f"Action inconnue: {action}",
                    },
                )
                continue

            timestamp = datetime.now(UTC).isoformat()

            # CURSOR_MOVED est envoyé à tout le monde sauf l'expéditeur (pas de conflit)
            # CONTENT_UPDATED et TITLE_CHANGED utilisent last-write-wins avec timestamp
            message = {
                "type": action,
                "data": data.get("data", {}),
                "user_id": user,
                "username": username,
                "timestamp": timestamp,
            }

            await manager.broadcast(
                note_id,
                message,
                exclude_user=user,
            )

    except WebSocketDisconnect:
        await manager.disconnect(note_id, user)
    except Exception as e:
        logger.error(f"Erreur WS notes: {e}")
        await manager.disconnect(note_id, user)
