"""
WebSocket admin — Monitoring temps réel des jobs cron.

Route : /api/v1/ws/admin/jobs
Authentification : token admin dans query param.

Diffuse les événements de jobs (démarrage, progression, succès, erreur)
aux administrateurs connectés en temps réel.
"""

from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Admin WebSocket Jobs"])

# Buffer circulaire d'événements jobs récents
_JOB_EVENT_BUFFER: deque[dict[str, Any]] = deque(maxlen=200)
_CONNECTED_ADMINS: set[WebSocket] = set()
_BROADCAST_LOCK = asyncio.Lock()


async def _auth_admin_ws(websocket: WebSocket, token: str) -> bool:
    """Valide le token WebSocket et s'assure du rôle admin."""
    try:
        from src.api.auth import decoder_token

        payload = decoder_token(token)
        role = payload.get("role", "")
        if role != "admin":
            await websocket.close(code=4003, reason="Accès admin requis")
            return False
        return True
    except Exception:
        await websocket.close(code=4001, reason="Token invalide")
        return False


async def diffuser_evenement_job(event: dict[str, Any]) -> None:
    """Diffuse un événement job à tous les admins connectés.

    Appelé depuis _ajouter_log_job() dans admin_shared.py.
    Thread-safe: peut être appelé depuis un contexte sync via asyncio.
    """
    entry = {
        "type": "job_event",
        "timestamp": datetime.now(UTC).isoformat(),
        **event,
    }
    _JOB_EVENT_BUFFER.append(entry)

    async with _BROADCAST_LOCK:
        dead: list[WebSocket] = []
        for ws in _CONNECTED_ADMINS:
            try:
                await asyncio.wait_for(ws.send_json(entry), timeout=2.0)
            except (TimeoutError, Exception):
                dead.append(ws)
        for ws in dead:
            _CONNECTED_ADMINS.discard(ws)


def emettre_evenement_job(
    job_id: str,
    status: str,
    message: str,
    **extra: Any,
) -> None:
    """Point d'entrée synchrone pour émettre un événement job via WebSocket.

    Fonction utilitaire appelable depuis du code sync (ex: _ajouter_log_job).
    Tente de broadcaster via la loop asyncio existante, sinon buffer seulement.
    """
    event = {
        "job_id": job_id,
        "status": status,
        "message": message,
        **extra,
    }
    entry = {
        "type": "job_event",
        "timestamp": datetime.now(UTC).isoformat(),
        **event,
    }
    _JOB_EVENT_BUFFER.append(entry)

    # Tenter de broadcaster si une loop asyncio tourne
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(diffuser_evenement_job(event))
    except RuntimeError:
        # Pas de loop asyncio active — l'événement est bufferisé,
        # les admins le recevront via le polling du WS
        pass


@router.websocket("/api/v1/ws/admin/jobs")
async def ws_admin_jobs(
    websocket: WebSocket,
    token: str = Query("", description="Token admin"),
):
    """Stream WebSocket des événements jobs admin en temps réel.

    Se connecte et reçoit les événements de jobs (démarrage, succès, erreur).
    Envoie un historique des 30 derniers événements à la connexion.

    Messages envoyés:
    - job_event: {"type": "job_event", "job_id": "...", "status": "...", "message": "..."}
    - heartbeat: {"type": "heartbeat"} toutes les 15s

    Commandes client:
    - {"action": "ping"} → {"type": "pong"}
    """
    if not await _auth_admin_ws(websocket, token):
        return

    await websocket.accept()
    _CONNECTED_ADMINS.add(websocket)

    logger.info("Admin connecté au monitoring jobs WebSocket")

    try:
        # Envoyer l'historique récent
        recent = list(_JOB_EVENT_BUFFER)[-30:]
        for entry in recent:
            await websocket.send_json(entry)

        # Boucle combinée: écouter les messages client + heartbeat
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=15.0,
                )
                action = data.get("action", "")
                if action == "ping":
                    await websocket.send_json({"type": "pong"})
            except TimeoutError:
                # Heartbeat pour maintenir la connexion
                try:
                    await websocket.send_json({"type": "heartbeat"})
                except Exception:
                    break

    except WebSocketDisconnect:
        logger.debug("Admin déconnecté du monitoring jobs")
    except Exception as e:
        logger.warning("Erreur WebSocket admin jobs: %s", e)
    finally:
        _CONNECTED_ADMINS.discard(websocket)
