"""
Service de gestion des rappels d'événements.

Permet de:
- Récupérer les événements avec rappel imminent
- Envoyer les notifications de rappel
- Marquer les rappels comme envoyés
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import EvenementPlanning
from src.services.core.notifications import (
    NotificationPush,
    TypeNotification,
    obtenir_service_webpush,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# OPTIONS DE RAPPEL
# ═══════════════════════════════════════════════════════════

OPTIONS_RAPPEL = [
    (None, "Aucun rappel"),
    (15, "15 minutes avant"),
    (30, "30 minutes avant"),
    (60, "1 heure avant"),
    (120, "2 heures avant"),
    (1440, "1 jour avant"),
]


def format_rappel(minutes: int | None) -> str:
    """Formate l'option de rappel pour affichage."""
    for val, label in OPTIONS_RAPPEL:
        if val == minutes:
            return label
    return "Aucun rappel"


# ═══════════════════════════════════════════════════════════
# SERVICE DE RAPPELS
# ═══════════════════════════════════════════════════════════


# Delegate to the central planning reminders service for logic and retrieval.
from src.services.planning.rappels import (
    ServiceRappels as _PlanningServiceRappels,
)
from src.services.planning.rappels import (
    obtenir_service_rappels as _obtenir_service_rappels_planning,
)

ServiceRappels = _PlanningServiceRappels


@avec_session_db
def get_rappels_imminents(
    window_minutes: int = 60, *, db: Session | None = None
) -> list[dict[str, Any]]:
    """Wrapper returning reminders in the original dict format by delegating
    to the canonical planning reminders service.
    """
    service = _obtenir_service_rappels_planning()
    # central service expects hours
    heures = max(1, int((window_minutes + 59) // 60))
    rappels = service.rappels_a_venir(heures=heures)

    result: list[dict[str, Any]] = []
    for r in rappels:
        result.append(
            {
                "type": getattr(r, "evenement_type", "evenement"),
                "id": None,
                "titre": getattr(r, "evenement_titre", ""),
                "date_debut": getattr(r, "date_evenement", None),
                "lieu": None,
                "rappel_minutes": None,
                "rappel_at": getattr(r, "date_rappel", None),
            }
        )

    # sort by rappel_at
    result.sort(key=lambda x: x.get("rappel_at") or datetime.max)
    return result


def envoyer_rappels_en_attente(user_id: str = "default") -> int:
    """Send pending reminders using the central reminders service and webpush."""
    service = _obtenir_service_rappels_planning()
    prochains = service.rappels_a_venir(heures=1)
    service_push = obtenir_service_webpush()

    envois = 0
    for r in prochains:
        try:
            notification = NotificationPush(
                title=f"🔔 Rappel: {r.evenement_titre}",
                body=r.message,
                notification_type=TypeNotification.RAPPEL_ACTIVITE,
                data={"type": r.evenement_type},
            )
            service_push.envoyer_notification(user_id, notification)
            envois += 1
            logger.info("✅ Rappel envoyé: %s", r.evenement_titre)
        except Exception as e:
            logger.error("❌ Erreur envoi rappel %s: %s", r.evenement_titre, e)

    return envois


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory

# Reuse central planning reminders service to avoid duplicate factories.


@service_factory("rappels", tags={"cuisine", "planning", "notifications"})
def obtenir_service_rappels() -> Any:
    """Return the central planning reminders service (alias).

    This ensures all modules importing `obtenir_service_rappels` get the same
    singleton instance instead of creating duplicates.
    """
    return _obtenir_service_rappels_planning()


def get_reminders_service() -> Any:
    """English alias returning the unified reminders service."""
    return obtenir_service_rappels()


# ═══════════════════════════════════════════════════════════
# UTILITAIRES UI
# ═══════════════════════════════════════════════════════════


def verifier_et_envoyer_rappels() -> dict:
    """
    Vérifie et envoie les rappels en attente.

    Fonction utilitaire pour être appelée depuis l'UI
    ou un job périodique.

    Returns:
        Dict avec {envoyés: int, erreurs: int, prochains: list}
    """
    service = obtenir_service_rappels()

    try:
        # Envoyer les rappels imminents (15 min)
        envois = service.envoyer_rappels_en_attente()

        # Récupérer les prochains rappels (1h)
        prochains = service.get_rappels_imminents(window_minutes=60)

        return {
            "envoyes": envois,
            "erreurs": 0,
            "prochains": prochains[:5],  # Max 5
        }
    except Exception as e:
        logger.error(f"Erreur vérification rappels: {e}")
        return {
            "envoyes": 0,
            "erreurs": 1,
            "prochains": [],
        }


__all__ = [
    "OPTIONS_RAPPEL",
    "format_rappel",
    "ServiceRappels",
    "obtenir_service_rappels",
    "get_reminders_service",
    "verifier_et_envoyer_rappels",
]
