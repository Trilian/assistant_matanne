"""
Service de Notifications pour les Jeux.

Gère les notifications et alertes pour:
- Opportunités détectées (séries)
- Résultats de synchronisation
- Alertes programmées

Intégration avec:
- Streamlit session state (notifications UI)
- Base de données (historique alertes)
- Scheduler (alertes programmées)
"""

import logging
from collections.abc import MutableMapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, StrEnum
from typing import Any

from src.core.db import obtenir_contexte_db
from src.core.models import AlerteJeux
from src.services.core.registry import service_factory
from src.services.jeux._internal.series_service import SEUIL_VALUE_ALERTE, SEUIL_VALUE_HAUTE

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class TypeNotification(StrEnum):
    """Types de notifications jeux."""

    OPPORTUNITE = "opportunite"  # Nouvelle opportunité détectée
    ALERTE = "alerte"  # Alerte seuil dépassé
    SYNC = "sync"  # Résultat synchronisation
    RAPPEL = "rappel"  # Rappel programmé
    INFO = "info"  # Information générale


class NiveauUrgence(StrEnum):
    """Niveau d'urgence de la notification."""

    HAUTE = "haute"  # 🔴 Value >= 2.5
    MOYENNE = "moyenne"  # 🟡 Value >= 2.0
    BASSE = "basse"  # 🟢 Information


@dataclass
class NotificationJeux:
    """Une notification jeux."""

    id: str
    type: TypeNotification
    titre: str
    message: str
    urgence: NiveauUrgence
    type_jeu: str  # "paris", "loto", "global"
    metadata: dict[str, Any] = field(default_factory=dict)
    lue: bool = False
    cree_le: datetime = field(default_factory=datetime.now)

    @property
    def icone(self) -> str:
        """Icône selon le type."""
        icones = {
            TypeNotification.OPPORTUNITE: "🎯",
            TypeNotification.ALERTE: "⚠️",
            TypeNotification.SYNC: "🔄",
            TypeNotification.RAPPEL: "⏰",
            TypeNotification.INFO: "ℹ️",
        }
        return icones.get(self.type, "📢")

    @property
    def couleur(self) -> str:
        """Couleur selon l'urgence."""
        couleurs = {
            NiveauUrgence.HAUTE: "#FF4B4B",  # Rouge
            NiveauUrgence.MOYENNE: "#FFA500",  # Orange
            NiveauUrgence.BASSE: "#00C851",  # Vert
        }
        return couleurs.get(self.urgence, "#808080")


# ═══════════════════════════════════════════════════════════
# SERVICE NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class NotificationJeuxService:
    """
    Service de gestion des notifications jeux.

    Stocke les notifications en session Streamlit et
    peut les persister en base de données.
    """

    SESSION_KEY = "jeux_notifications"
    MAX_NOTIFICATIONS = 50

    def __init__(self, storage: MutableMapping[str, Any] | None = None):
        """Initialise le service.

        Args:
            storage: Stockage clé-valeur mutable (défaut: st.session_state).
        """
        from src.core.storage import obtenir_session_state

        self._storage = storage if storage is not None else obtenir_session_state()
        self._init_session()

    def _init_session(self):
        """Initialise le stockage session."""
        if self.SESSION_KEY not in self._storage:
            self._storage[self.SESSION_KEY] = []

    @property
    def notifications(self) -> list[NotificationJeux]:
        """Liste des notifications en session."""
        self._init_session()
        return self._storage[self.SESSION_KEY]

    # ───────────────────────────────────────────────────────────────
    # CRÉATION
    # ───────────────────────────────────────────────────────────────

    def creer_notification(
        self,
        type: TypeNotification,
        titre: str,
        message: str,
        urgence: NiveauUrgence = NiveauUrgence.BASSE,
        type_jeu: str = "global",
        metadata: dict[str, Any] | None = None,
    ) -> NotificationJeux:
        """
        Crée une nouvelle notification.

        Args:
            type: Type de notification
            titre: Titre court
            message: Message détaillé
            urgence: Niveau d'urgence
            type_jeu: Type de jeu concerné
            metadata: Données additionnelles

        Returns:
            NotificationJeux créée
        """
        notification = NotificationJeux(
            id=f"{type_jeu}_{datetime.now().timestamp()}",
            type=type,
            titre=titre,
            message=message,
            urgence=urgence,
            type_jeu=type_jeu,
            metadata=metadata or {},
        )

        # Ajouter en session
        self._init_session()
        notifications = self._storage[self.SESSION_KEY]
        notifications.insert(0, notification)

        # Limiter le nombre
        if len(notifications) > self.MAX_NOTIFICATIONS:
            self._storage[self.SESSION_KEY] = notifications[: self.MAX_NOTIFICATIONS]

        logger.info(f"Notification créée: {titre}")
        return notification

    def creer_alerte_opportunite(
        self,
        identifiant: str,
        value: float,
        serie: int,
        type_jeu: str,
        details: str = "",
    ) -> NotificationJeux:
        """
        Crée une notification pour une opportunité détectée.

        Args:
            identifiant: ID de l'opportunité (ex: "Ligue1_More_2_5")
            value: Score value
            serie: Longueur de la série
            type_jeu: "paris" ou "loto"
            details: Détails supplémentaires

        Returns:
            NotificationJeux créée
        """
        # Déterminer urgence
        if value >= SEUIL_VALUE_HAUTE:
            urgence = NiveauUrgence.HAUTE
            niveau_texte = "très en retard 🟢"
        elif value >= SEUIL_VALUE_ALERTE:
            urgence = NiveauUrgence.MOYENNE
            niveau_texte = "en retard 🟡"
        else:
            urgence = NiveauUrgence.BASSE
            niveau_texte = "à surveiller"

        titre = f"Opportunité {type_jeu.capitalize()}: {identifiant}"
        message = (
            f"{identifiant} est {niveau_texte}.\nValue: {value:.2f} | Série: {serie} | {details}"
        )

        return self.creer_notification(
            type=TypeNotification.OPPORTUNITE,
            titre=titre,
            message=message,
            urgence=urgence,
            type_jeu=type_jeu,
            metadata={
                "identifiant": identifiant,
                "value": value,
                "serie": serie,
            },
        )

    def creer_alerte_sync(
        self,
        type_jeu: str,
        succes: bool,
        nb_maj: int = 0,
        nb_alertes: int = 0,
        erreur: str | None = None,
    ) -> NotificationJeux:
        """
        Crée une notification de résultat de synchronisation.

        Args:
            type_jeu: Type de jeu synchronisé
            succes: Sync réussie
            nb_maj: Nombre d'éléments mis à jour
            nb_alertes: Nombre d'alertes créées
            erreur: Message d'erreur si échec

        Returns:
            NotificationJeux créée
        """
        if succes:
            titre = f"Sync {type_jeu.capitalize()} ✅"
            message = f"Synchronisation terminée: {nb_maj} éléments, {nb_alertes} alertes."
            urgence = NiveauUrgence.BASSE
        else:
            titre = f"Sync {type_jeu.capitalize()} ❌"
            message = f"Erreur de synchronisation: {erreur or 'Erreur inconnue'}"
            urgence = NiveauUrgence.HAUTE

        return self.creer_notification(
            type=TypeNotification.SYNC,
            titre=titre,
            message=message,
            urgence=urgence,
            type_jeu=type_jeu,
            metadata={
                "succes": succes,
                "nb_maj": nb_maj,
                "nb_alertes": nb_alertes,
                "erreur": erreur,
            },
        )

    # ───────────────────────────────────────────────────────────────
    # LECTURE
    # ───────────────────────────────────────────────────────────────

    def obtenir_non_lues(self) -> list[NotificationJeux]:
        """Retourne les notifications non lues."""
        return [n for n in self.notifications if not n.lue]

    def obtenir_par_type(self, type: TypeNotification) -> list[NotificationJeux]:
        """Retourne les notifications d'un type donné."""
        return [n for n in self.notifications if n.type == type]

    def obtenir_par_jeu(self, type_jeu: str) -> list[NotificationJeux]:
        """Retourne les notifications pour un type de jeu."""
        return [n for n in self.notifications if n.type_jeu == type_jeu]

    def obtenir_urgentes(self) -> list[NotificationJeux]:
        """Retourne les notifications urgentes (haute et moyenne)."""
        return [
            n
            for n in self.notifications
            if n.urgence in (NiveauUrgence.HAUTE, NiveauUrgence.MOYENNE) and not n.lue
        ]

    def compter_non_lues(self) -> int:
        """Compte les notifications non lues."""
        return len(self.obtenir_non_lues())

    # ───────────────────────────────────────────────────────────────
    # ACTIONS
    # ───────────────────────────────────────────────────────────────

    def marquer_lue(self, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        for notif in self.notifications:
            if notif.id == notification_id:
                notif.lue = True
                return True
        return False

    def marquer_toutes_lues(self) -> int:
        """Marque toutes les notifications comme lues."""
        count = 0
        for notif in self.notifications:
            if not notif.lue:
                notif.lue = True
                count += 1
        return count

    def supprimer(self, notification_id: str) -> bool:
        """Supprime une notification."""
        self._init_session()
        notifications = self._storage[self.SESSION_KEY]
        for i, notif in enumerate(notifications):
            if notif.id == notification_id:
                del notifications[i]
                return True
        return False

    def vider(self) -> int:
        """Vide toutes les notifications."""
        count = len(self.notifications)
        self._storage[self.SESSION_KEY] = []
        return count

    # ───────────────────────────────────────────────────────────────
    # SYNCHRONISATION BASE DE DONNÉES
    # ───────────────────────────────────────────────────────────────

    def charger_alertes_db(self, limite: int = 20) -> list[NotificationJeux]:
        """
        Charge les alertes depuis la base de données.

        Args:
            limite: Nombre max d'alertes à charger

        Returns:
            Liste de NotificationJeux
        """
        try:
            with obtenir_contexte_db() as db:
                alertes = (
                    db.query(AlerteJeux)
                    .filter(AlerteJeux.notifie == False)  # noqa: E712
                    .order_by(AlerteJeux.value_alerte.desc())
                    .limit(limite)
                    .all()
                )

                notifications: list[NotificationJeux] = []
                for alerte in alertes:
                    urgence = (
                        NiveauUrgence.HAUTE
                        if alerte.value_alerte >= SEUIL_VALUE_HAUTE
                        else NiveauUrgence.MOYENNE
                    )

                    # Construire identifiant depuis marché
                    identifiant = f"{alerte.championnat or ''}/{alerte.marche or ''}"

                    notif = NotificationJeux(
                        id=f"db_{alerte.id}",
                        type=TypeNotification.ALERTE,
                        titre=f"Alerte {alerte.type_jeu}: {identifiant}",
                        message=f"Value: {alerte.value_alerte:.2f}, Série: {alerte.serie_alerte}",
                        urgence=urgence,
                        type_jeu=alerte.type_jeu,
                        metadata={
                            "db_id": alerte.id,
                            "value": alerte.value_alerte,
                            "serie": alerte.serie_alerte,
                        },
                    )
                    notifications.append(notif)

                return notifications

        except Exception as e:
            logger.error(f"Erreur chargement alertes DB: {e}")
            return []


# ═══════════════════════════════════════════════════════════
# UI HELPERS — rétrocompatibilité, implémentation dans src.ui.views.jeux
# ═══════════════════════════════════════════════════════════


def afficher_badge_notifications(service: "NotificationJeuxService | None" = None) -> None:
    """Rétrocompat — délègue à src.ui.views.jeux."""
    from src.ui.views.jeux import afficher_badge_notifications_jeux

    afficher_badge_notifications_jeux(service)


def afficher_notification(notification: "NotificationJeux") -> None:
    """Rétrocompat — délègue à src.ui.views.jeux."""
    from src.ui.views.jeux import afficher_notification_jeux

    afficher_notification_jeux(notification)


def afficher_liste_notifications(
    service: "NotificationJeuxService | None" = None,
    limite: int = 10,
    type_jeu: str | None = None,
) -> None:
    """Rétrocompat — délègue à src.ui.views.jeux."""
    from src.ui.views.jeux import afficher_liste_notifications_jeux

    afficher_liste_notifications_jeux(service, limite, type_jeu)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("notification_jeux", tags={"jeux", "notification"})
def get_notification_jeux_service() -> NotificationJeuxService:
    """Factory singleton pour le service de notifications."""
    return NotificationJeuxService()


def obtenir_service_notifications_jeux() -> NotificationJeuxService:
    """Alias français pour get_notification_jeux_service (singleton via registre)."""
    return get_notification_jeux_service()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Classes
    "NotificationJeuxService",
    "NotificationJeux",
    "TypeNotification",
    "NiveauUrgence",
    # UI Helpers
    "afficher_badge_notifications",
    "afficher_notification",
    "afficher_liste_notifications",
    # Factory
    "obtenir_service_notifications_jeux",
    "get_notification_jeux_service",
]
