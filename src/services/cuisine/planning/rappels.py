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
from src.core.models import CalendarEvent
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


class ServiceRappels:
    """Service de gestion des rappels d'événements."""

    def __init__(self, db: Session | None = None):
        """Initialise le service."""
        self._db = db

    @avec_session_db
    def get_rappels_imminents(
        self, window_minutes: int = 60, *, db: Session
    ) -> list[dict[str, Any]]:
        """
        Récupère les événements dont le rappel doit être envoyé.

        Args:
            window_minutes: Fenêtre de temps en minutes (par défaut 60)
            db: Session SQLAlchemy

        Returns:
            Liste de dicts avec les événements à rappeler
        """
        now = datetime.now()
        rappels: list[dict[str, Any]] = []

        # Événements CalendarEvent avec rappel
        events = (
            db.query(CalendarEvent)
            .filter(
                CalendarEvent.rappel_avant_minutes.isnot(None),
                CalendarEvent.date_debut > now,
            )
            .all()
        )

        for event in events:
            # Calculer quand le rappel doit être envoyé
            if event.rappel_avant_minutes is None:
                continue
            rappel_at = event.date_debut - timedelta(minutes=event.rappel_avant_minutes)

            # Si le moment du rappel est dans la fenêtre
            if now <= rappel_at <= now + timedelta(minutes=window_minutes):
                rappels.append(
                    {
                        "type": "calendar_event",
                        "id": event.id,
                        "titre": event.titre,
                        "date_debut": event.date_debut,
                        "lieu": event.lieu,
                        "rappel_minutes": event.rappel_avant_minutes,
                        "rappel_at": rappel_at,
                    }
                )

        # Activités famille avec rappel (si elles avaient ce champ)
        # Note: FamilyActivity n'a pas encore rappel_avant_minutes

        # Trier par moment du rappel
        rappels.sort(key=lambda r: r["rappel_at"])

        return rappels

    def envoyer_rappels_en_attente(self, user_id: str = "default") -> int:
        """
        Envoie les notifications pour les rappels imminents.

        Args:
            user_id: ID de l'utilisateur destinataire

        Returns:
            Nombre de rappels envoyés
        """
        rappels = self.get_rappels_imminents(window_minutes=15)
        service_push = obtenir_service_webpush()

        envois = 0
        for rappel in rappels:
            try:
                # Formater le délai
                minutes = rappel["rappel_minutes"]
                if minutes >= 60:
                    delai_str = (
                        f"{minutes // 60}h"
                        if minutes % 60 == 0
                        else f"{minutes // 60}h{minutes % 60}"
                    )
                else:
                    delai_str = f"{minutes} min"

                # Créer la notification
                notification = NotificationPush(
                    title=f"🔔 Rappel: {rappel['titre']}",
                    body=f"Dans {delai_str}"
                    + (f" • {rappel['lieu']}" if rappel.get("lieu") else ""),
                    notification_type=TypeNotification.RAPPEL_ACTIVITE,
                    data={"event_id": rappel["id"], "type": rappel["type"]},
                )

                # Envoyer
                service_push.envoyer_notification(user_id, notification)
                envois += 1
                logger.info(f"✅ Rappel envoyé: {rappel['titre']}")

            except Exception as e:
                logger.error(f"❌ Erreur envoi rappel {rappel['titre']}: {e}")

        return envois


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

_service_rappels: ServiceRappels | None = None


def obtenir_service_rappels() -> ServiceRappels:
    """Retourne l'instance singleton du service de rappels."""
    global _service_rappels
    if _service_rappels is None:
        _service_rappels = ServiceRappels()
    return _service_rappels


# Alias
get_rappels_service = obtenir_service_rappels


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
    "get_rappels_service",
    "verifier_et_envoyer_rappels",
]
