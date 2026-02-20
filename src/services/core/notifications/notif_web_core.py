"""
Service de notifications Web Push - Module principal.

Utilise Web Push API avec VAPID pour envoyer des notifications
aux navigateurs des utilisateurs.
"""

import json
import logging
from datetime import datetime

from src.services.core.notifications.notif_web_persistence import NotificationPersistenceMixin
from src.services.core.notifications.notif_web_templates import NotificationTemplatesMixin
from src.services.core.notifications.types import (
    VAPID_EMAIL,
    VAPID_PRIVATE_KEY,
    AbonnementPush,
    NotificationPush,
    PreferencesNotification,
    TypeNotification,
)
from src.services.core.notifications.utils import (
    est_heures_silencieuses,
    generer_cle_compteur,
    peut_envoyer_pendant_silence,
    verifier_type_notification_active,
)

logger = logging.getLogger(__name__)


class ServiceWebPush(NotificationPersistenceMixin, NotificationTemplatesMixin):
    """
    Service d'envoi de notifications push via Web Push API.

    Utilise Web Push API avec VAPID pour envoyer des notifications
    aux navigateurs des utilisateurs.
    """

    def __init__(self):
        """Initialise le service."""
        self._subscriptions: dict[str, list[AbonnementPush]] = {}
        self._preferences: dict[str, PreferencesNotification] = {}
        self._sent_count: dict[str, int] = {}

    # ═══════════════════════════════════════════════════════════
    # GESTION DES ABONNEMENTS
    # ═══════════════════════════════════════════════════════════

    def sauvegarder_abonnement(self, user_id: str, subscription_info: dict) -> AbonnementPush:
        """
        Sauvegarde un nouvel abonnement push.

        Args:
            user_id: ID de l'utilisateur
            subscription_info: Info d'abonnement du navigateur

        Returns:
            Abonnement créé
        """
        subscription = AbonnementPush(
            user_id=user_id,
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )

        if user_id not in self._subscriptions:
            self._subscriptions[user_id] = []

        # Éviter les doublons
        existing = [s for s in self._subscriptions[user_id] if s.endpoint == subscription.endpoint]
        if not existing:
            self._subscriptions[user_id].append(subscription)
            self._sauvegarder_abonnement_supabase(subscription)

        logger.info(f"✅ Abonnement push enregistré pour {user_id}")
        return subscription

    def supprimer_abonnement(self, user_id: str, endpoint: str):
        """Supprime un abonnement."""
        if user_id in self._subscriptions:
            self._subscriptions[user_id] = [
                s for s in self._subscriptions[user_id] if s.endpoint != endpoint
            ]
        self._supprimer_abonnement_supabase(user_id, endpoint)
        logger.info(f"Abonnement supprimé pour {user_id}")

    def obtenir_abonnements_utilisateur(self, user_id: str) -> list[AbonnementPush]:
        """Récupère les abonnements d'un utilisateur."""
        if user_id in self._subscriptions:
            return self._subscriptions[user_id]

        subs = self._charger_abonnements_supabase(user_id)
        self._subscriptions[user_id] = subs
        return subs

    # ═══════════════════════════════════════════════════════════
    # PRÉFÉRENCES
    # ═══════════════════════════════════════════════════════════

    def obtenir_preferences(self, user_id: str) -> PreferencesNotification:
        """Récupère les préférences de notification."""
        if user_id not in self._preferences:
            self._preferences[user_id] = PreferencesNotification(user_id=user_id)
        return self._preferences[user_id]

    def mettre_a_jour_preferences(self, user_id: str, preferences: PreferencesNotification):
        """Met à jour les préférences."""
        self._preferences[user_id] = preferences
        self._sauvegarder_preferences_supabase(preferences)

    def doit_envoyer(self, user_id: str, type_notification: TypeNotification) -> bool:
        """
        Vérifie si on doit envoyer une notification.

        Prend en compte:
        - Préférences utilisateur
        - Heures de silence
        - Limite par heure
        """
        prefs = self.obtenir_preferences(user_id)
        now = datetime.now()

        # Convertir prefs en dict pour les utilitaires
        prefs_dict = {
            "alertes_stock": prefs.alertes_stock,
            "alertes_peremption": prefs.alertes_peremption,
            "rappels_repas": prefs.rappels_repas,
            "rappels_activites": prefs.rappels_activites,
            "mises_a_jour_courses": prefs.mises_a_jour_courses,
            "rappels_famille": prefs.rappels_famille,
            "mises_a_jour_systeme": prefs.mises_a_jour_systeme,
            "heures_silencieuses_debut": prefs.heures_silencieuses_debut,
            "heures_silencieuses_fin": prefs.heures_silencieuses_fin,
            "max_par_heure": prefs.max_par_heure,
        }

        # Vérifier type activé
        if not verifier_type_notification_active(type_notification, prefs_dict):
            return False

        # Vérifier heures silencieuses
        if est_heures_silencieuses(
            now.hour, prefs.heures_silencieuses_debut, prefs.heures_silencieuses_fin
        ):
            if not peut_envoyer_pendant_silence(type_notification):
                return False

        # Vérifier limite par heure
        count_key = generer_cle_compteur(user_id, now)
        current_count = self._sent_count.get(count_key, 0)
        if current_count >= prefs.max_par_heure:
            return False

        return True

    # ═══════════════════════════════════════════════════════════
    # ENVOI DE NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════

    def envoyer_notification(self, user_id: str, notification: NotificationPush) -> bool:
        """
        Envoie une notification push à un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            notification: Notification à envoyer

        Returns:
            True si envoyé avec succès
        """
        if not self.doit_envoyer(user_id, notification.notification_type):
            logger.debug(f"Notification ignorée pour {user_id} (préférences)")
            return False

        subscriptions = self.obtenir_abonnements_utilisateur(user_id)

        if not subscriptions:
            logger.warning(f"Pas d'abonnement push pour {user_id}")
            return False

        success = False
        for sub in subscriptions:
            try:
                self._envoyer_web_push(sub, notification)
                sub.last_used = datetime.now()
                success = True
            except Exception as e:
                logger.error(f"Erreur envoi push: {e}")
                if "410" in str(e) or "404" in str(e):
                    sub.is_active = False

        # Incrémenter le compteur
        if success:
            now = datetime.now()
            count_key = generer_cle_compteur(user_id, now)
            self._sent_count[count_key] = self._sent_count.get(count_key, 0) + 1

        return success

    def envoyer_a_tous(self, notification: NotificationPush) -> int:
        """
        Envoie une notification à tous les utilisateurs.

        Returns:
            Nombre d'utilisateurs notifiés
        """
        count = 0
        for user_id in self._subscriptions:
            if self.envoyer_notification(user_id, notification):
                count += 1
        return count

    def _envoyer_web_push(self, subscription: AbonnementPush, notification: NotificationPush):
        """Envoie via Web Push API."""
        try:
            from pywebpush import webpush

            payload = json.dumps(
                {
                    "title": notification.title,
                    "body": notification.body,
                    "icon": notification.icon,
                    "badge": notification.badge,
                    "tag": notification.tag,
                    "data": {
                        "url": notification.url,
                        "type": notification.notification_type.value,
                        **notification.data,
                    },
                    "actions": notification.actions,
                    "vibrate": notification.vibrate,
                    "requireInteraction": notification.require_interaction,
                    "silent": notification.silent,
                    "timestamp": notification.timestamp.isoformat(),
                }
            )

            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh_key,
                        "auth": subscription.auth_key,
                    },
                },
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL},
            )

            logger.debug(f"Push envoyé: {notification.title}")

        except ImportError:
            logger.warning("pywebpush non installé: pip install pywebpush")
        except Exception as e:
            logger.error(f"Erreur Web Push: {e}")
            raise

    # ═══════════════════════════════════════════════════════════
    # ALIAS MÉTHODES RÉTROCOMPATIBILITÉ
    # ═══════════════════════════════════════════════════════════

    # Public methods aliases
    save_subscription = sauvegarder_abonnement
    remove_subscription = supprimer_abonnement
    get_user_subscriptions = obtenir_abonnements_utilisateur
    get_preferences = obtenir_preferences
    update_preferences = mettre_a_jour_preferences
    should_send = doit_envoyer
    send_notification = envoyer_notification
    send_to_all_users = envoyer_a_tous

    # Private methods alias
    _send_web_push = _envoyer_web_push


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("webpush", tags={"notifications", "web"})
def obtenir_service_webpush() -> ServiceWebPush:
    """Factory pour le service de notifications Web Push (thread-safe via registre)."""
    return ServiceWebPush()


# Alias anglais pour compatibilité API routes
get_push_notification_service = obtenir_service_webpush
