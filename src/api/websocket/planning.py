"""
WebSocket pour collaboration temps réel sur le planning repas.

Permet à plusieurs utilisateurs de modifier le même planning
simultanément avec synchronisation en temps réel.
"""

import json
import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from .manager import get_manager
from .types import WSBaseMessageType, WSPlanningMessageType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ws", tags=["WebSocket Planning"])

PLANNING_MESSAGE_TYPES = {t.value for t in WSPlanningMessageType}


@router.websocket("/planning/{planning_id}")
async def ws_planning(
    websocket: WebSocket,
    planning_id: int,
    user: str = Query(default="anonyme"),
    username: str = Query(default="Anonyme"),
):
    """WebSocket de collaboration sur le planning repas."""
    manager = get_manager("planning")
    await manager.connect(websocket, planning_id, user, username)

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

            if action not in PLANNING_MESSAGE_TYPES:
                await manager.send_personal(
                    websocket,
                    {
                        "type": WSBaseMessageType.ERROR,
                        "message": f"Action inconnue: {action}",
                    },
                )
                continue

            # Broadcaster la modification aux autres
            await manager.broadcast(
                planning_id,
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
        await manager.disconnect(planning_id, user)
    except Exception as e:
        logger.error(f"Erreur WS planning: {e}")
        await manager.disconnect(planning_id, user)
