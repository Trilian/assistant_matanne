"""Helpers pour la journalisation dédiée des événements de sécurité."""

from __future__ import annotations

import logging
from typing import Any

from src.core.db import obtenir_contexte_db

logger = logging.getLogger(__name__)


def journaliser_evenement_securite(
    event_type: str,
    user_id: str | None,
    ip: str | None,
    user_agent: str | None,
    details: dict[str, Any] | None = None,
) -> None:
    """Insère un événement sécurité dans la table logs_securite (best-effort)."""
    try:
        with obtenir_contexte_db() as session:
            from sqlalchemy import text

            session.execute(
                text(
                    """
                    INSERT INTO logs_securite (user_id, event_type, ip, user_agent, details, created_at)
                    VALUES (:user_id, :event_type, :ip, :user_agent, CAST(:details AS jsonb), NOW())
                    """
                ),
                {
                    "user_id": user_id,
                    "event_type": event_type,
                    "ip": ip,
                    "user_agent": user_agent,
                    "details": str(details or {}),
                },
            )
            session.commit()
    except Exception as exc:
        # Best-effort: ne jamais casser la requête principale.
        logger.debug("Journalisation sécurité ignorée (%s): %s", event_type, exc)
