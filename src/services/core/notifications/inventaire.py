"""
Service de notifications pour l'inventaire.

Gère les notifications locales (en mémoire) pour les alertes de stock
et de péremption.
"""

import logging
from typing import Any

from src.services.core.notifications.types import (
    NotificationInventaire,
    TypeAlerte,
)

logger = logging.getLogger(__name__)


class ServiceNotificationsInventaire:
    """Service pour gérer les notifications d'inventaire (locales)."""

    def __init__(self):
        self.notifications: dict[int, list[NotificationInventaire]] = {}
        self._next_id = 1

    def creer_notification_stock_critique(
        self,
        article: dict[str, Any],
    ) -> NotificationInventaire | None:
        """Crée une notification pour stock critique."""
        message = (
            f"❌ CRITIQUE: {article['nom']} est en stock critique!\n"
            f"Quantité actuelle: {article['quantite']} {article.get('unite', '')}\n"
            f"Seuil minimum: {article['quantite_min']} {article.get('unite', '')}"
        )

        return NotificationInventaire(
            id=self._next_id,
            type_alerte=TypeAlerte.STOCK_CRITIQUE,
            article_id=article["id"],
            ingredient_id=article["ingredient_id"],
            titre=f"⚠️ Stock critique: {article['nom']}",
            message=message,
            icone="❌",
            priorite="haute",
        )

    def creer_notification_stock_bas(
        self,
        article: dict[str, Any],
    ) -> NotificationInventaire | None:
        """Crée une notification pour stock bas."""
        message = (
            f"⚠️ ALERTE: {article['nom']} a un stock bas.\n"
            f"Quantité actuelle: {article['quantite']} {article.get('unite', '')}\n"
            f"Seuil minimum: {article['quantite_min']} {article.get('unite', '')}"
        )

        return NotificationInventaire(
            id=self._next_id,
            type_alerte=TypeAlerte.STOCK_BAS,
            article_id=article["id"],
            ingredient_id=article["ingredient_id"],
            titre=f"⚠️ Stock bas: {article['nom']}",
            message=message,
            icone="⚠️",
            priorite="moyenne",
        )

    def creer_notification_peremption(
        self,
        article: dict[str, Any],
        jours_avant: int,
    ) -> NotificationInventaire | None:
        """Crée une notification pour péremption proche."""
        if jours_avant <= 0:
            titre = f"🚨 EXPIRÉ: {article['nom']}"
            type_alerte = TypeAlerte.PEREMPTION_DEPASSEE
            priorite = "haute"
            icone = "🚨"
        elif jours_avant <= 3:
            titre = f"🔴 Péremption très proche: {article['nom']}"
            type_alerte = TypeAlerte.PEREMPTION_PROCHE
            priorite = "haute"
            icone = "🔴"
        else:
            titre = f"🟠 Péremption proche: {article['nom']}"
            type_alerte = TypeAlerte.PEREMPTION_PROCHE
            priorite = "moyenne"
            icone = "🟠"

        message = (
            f"{icone} Date de péremption: {article.get('date_peremption')}\n"
            f"Jours restants: {jours_avant}\n"
            f"À consommer dès que possible!"
        )

        return NotificationInventaire(
            id=self._next_id,
            type_alerte=type_alerte,
            article_id=article["id"],
            ingredient_id=article["ingredient_id"],
            titre=titre,
            message=message,
            icone=icone,
            priorite=priorite,
        )

    def ajouter_notification(
        self,
        notification: NotificationInventaire,
        utilisateur_id: int = 1,
    ) -> NotificationInventaire:
        """Ajoute une notification pour un utilisateur."""
        if utilisateur_id not in self.notifications:
            self.notifications[utilisateur_id] = []

        # Évite les doublons
        for notif in self.notifications[utilisateur_id]:
            if (
                notif.type_alerte == notification.type_alerte
                and notif.article_id == notification.article_id
            ):
                return notif

        notification.id = self._next_id
        self._next_id += 1

        self.notifications[utilisateur_id].append(notification)
        logger.info(f"🔔 Notification créée: {notification.titre}")

        return notification

    def obtenir_notifications(
        self,
        utilisateur_id: int = 1,
        non_lues_seulement: bool = False,
    ) -> list[NotificationInventaire]:
        """Récupère les notifications d'un utilisateur."""
        notifs = self.notifications.get(utilisateur_id, [])

        if non_lues_seulement:
            notifs = [n for n in notifs if not n.lue]

        priorite_ordre = {"haute": 0, "moyenne": 1, "basse": 2}
        notifs.sort(
            key=lambda x: (priorite_ordre[x.priorite], -x.date_creation.timestamp()),
        )

        return notifs

    def marquer_lue(
        self,
        notification_id: int | None,
        utilisateur_id: int = 1,
    ) -> bool:
        """Marque une notification comme lue."""
        if notification_id is None:
            return False

        notifs = self.notifications.get(utilisateur_id, [])
        for notif in notifs:
            if notif.id == notification_id:
                notif.lue = True
                return True
        return False

    def supprimer_notification(
        self,
        notification_id: int | None,
        utilisateur_id: int = 1,
    ) -> bool:
        """Supprime une notification."""
        if notification_id is None:
            return False

        if utilisateur_id in self.notifications:
            original_len = len(self.notifications[utilisateur_id])
            self.notifications[utilisateur_id] = [
                n for n in self.notifications[utilisateur_id] if n.id != notification_id
            ]
            return len(self.notifications[utilisateur_id]) < original_len
        return False

    def effacer_toutes_lues(self, utilisateur_id: int = 1) -> int:
        """Supprime toutes les notifications lues."""
        if utilisateur_id not in self.notifications:
            return 0

        avant = len(self.notifications[utilisateur_id])
        self.notifications[utilisateur_id] = [
            n for n in self.notifications[utilisateur_id] if not n.lue
        ]
        apres = len(self.notifications[utilisateur_id])

        logger.info(f"Effacé {avant - apres} notifications lues")
        return avant - apres

    def obtenir_stats(self, utilisateur_id: int = 1) -> dict[str, Any]:
        """Récupère les statistiques de notifications."""
        notifs = self.notifications.get(utilisateur_id, [])

        stats: dict[str, Any] = {
            "total": len(notifs),
            "non_lues": len([n for n in notifs if not n.lue]),
            "par_type": {},
            "par_priorite": {},
        }

        for notif in notifs:
            type_key = notif.type_alerte.value
            stats["par_type"][type_key] = stats["par_type"].get(type_key, 0) + 1
            stats["par_priorite"][notif.priorite] = stats["par_priorite"].get(notif.priorite, 0) + 1

        return stats

    def obtenir_alertes_actives(
        self,
        utilisateur_id: int = 1,
    ) -> dict[str, list[NotificationInventaire]]:
        """Récupère les alertes groupées par type."""
        notifs = self.notifications.get(utilisateur_id, [])

        alertes: dict[str, list[NotificationInventaire]] = {
            "critiques": [],
            "hautes": [],
            "moyennes": [],
            "basses": [],
        }

        for notif in notifs:
            if not notif.lue:
                if notif.priorite == "haute":
                    alertes["critiques"].append(notif)
                elif notif.priorite == "moyenne":
                    alertes["hautes"].append(notif)
                else:
                    alertes["moyennes"].append(notif)

        return alertes

    def envoyer_email_alerte(
        self,
        notification: NotificationInventaire,
        email_destinataire: str,
    ) -> bool:
        """Envoie une notification par email (stub)."""
        logger.info(f"🔧 Email alerte à {email_destinataire}: {notification.titre}")

        notification.email = email_destinataire
        notification.push_envoyee = True

        return True


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_service_notifications_inventaire: ServiceNotificationsInventaire | None = None


def obtenir_service_notifications_inventaire() -> ServiceNotificationsInventaire:
    """Obtient l'instance singleton du service de notifications inventaire."""
    global _service_notifications_inventaire

    if _service_notifications_inventaire is None:
        _service_notifications_inventaire = ServiceNotificationsInventaire()
        logger.info("✅ Service de notifications inventaire initialisé")

    return _service_notifications_inventaire


def get_inventory_notification_service() -> ServiceNotificationsInventaire:
    """Factory for inventory notification service (English alias)."""
    return obtenir_service_notifications_inventaire()


__all__ = [
    "ServiceNotificationsInventaire",
    "obtenir_service_notifications_inventaire",
    "get_inventory_notification_service",
]
