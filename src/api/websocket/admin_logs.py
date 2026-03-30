"""
WebSocket admin — Stream de logs structurés en temps réel.

Route : /api/v1/ws/admin/logs
Authentification : token admin dans query param.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin WebSocket"])

# Buffer circulaire de logs récents
_LOG_BUFFER: deque[dict[str, Any]] = deque(maxlen=500)
_CONNECTED_ADMINS: set[WebSocket] = set()


class WebSocketLogHandler(logging.Handler):
    """Handler de logging qui diffuse les logs aux admins connectés via WebSocket."""

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "type": "log_entry",
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }
        _LOG_BUFFER.append(entry)
        # La diffusion réelle est gérée par la boucle async du WebSocket


def installer_handler_logs() -> None:
    """Installe le handler WebSocket sur le root logger."""
    handler = WebSocketLogHandler()
    handler.setLevel(logging.INFO)
    logging.getLogger().addHandler(handler)


@router.websocket("/api/v1/ws/admin/logs")
async def ws_admin_logs(
    websocket: WebSocket,
    token: str = Query("", description="Token admin"),
):
    """Stream WebSocket des logs structurés (réservé admin).

    Se connecte et reçoit les logs INFO+ en temps réel.
    Envoie un historique des 50 derniers logs à la connexion.
    """
    # Validation basique du token admin
    try:
        from src.api.auth import decoder_token

        payload = decoder_token(token)
        role = payload.get("role", "")
        if role != "admin":
            await websocket.close(code=4003, reason="Accès admin requis")
            return
    except Exception:
        await websocket.close(code=4001, reason="Token invalide")
        return

    await websocket.accept()
    _CONNECTED_ADMINS.add(websocket)

    try:
        # Envoyer l'historique récent
        recent = list(_LOG_BUFFER)[-50:]
        for entry in recent:
            await websocket.send_json(entry)

        # Boucle de diffusion
        last_index = len(_LOG_BUFFER)
        while True:
            await asyncio.sleep(1)
            current = list(_LOG_BUFFER)
            if len(current) > last_index:
                new_entries = current[last_index:]
                for entry in new_entries:
                    await websocket.send_json(entry)
                last_index = len(current)

    except WebSocketDisconnect:
        logger.debug("Admin déconnecté du stream de logs")
    except Exception:
        logger.debug("Erreur WebSocket admin logs", exc_info=True)
    finally:
        _CONNECTED_ADMINS.discard(websocket)
