"""
WebSocket pour collaboration temps réel sur les projets Kanban.

Permet de voir en direct les déplacements de tâches entre colonnes,
les ajouts et modifications sur un tableau de projet partagé.
"""

import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from .manager import get_manager
from .types import WSBaseMessageType, WSProjetsMessageType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["WebSocket Projets"])

PROJETS_MESSAGE_TYPES = {t.value for t in WSProjetsMessageType}


@router.websocket("/projets/{projet_id}")
async def ws_projets(
    websocket: WebSocket,
    projet_id: int,
    user: str = Query(default="anonyme"),
    username: str = Query(default="Anonyme"),
):
    """WebSocket de collaboration sur les projets Kanban."""
    manager = get_manager("projets")
    await manager.connect(websocket, projet_id, user, username)

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

            if action not in PROJETS_MESSAGE_TYPES:
                await manager.send_personal(
                    websocket,
                    {
                        "type": WSBaseMessageType.ERROR,
                        "message": f"Action inconnue: {action}",
                    },
                )
                continue

            await manager.broadcast(
                projet_id,
                {
                    "type": action,
                    "data": data.get("data", {}),
                    "user_id": user,
                    "username": username,
                    "timestamp": datetime.now(UTC).isoformat(),
                },
                exclude_user=user,
            )

    except WebSocketDisconnect:
        await manager.disconnect(projet_id, user)
    except Exception as e:
        logger.error(f"Erreur WS projets: {e}")
        await manager.disconnect(projet_id, user)
