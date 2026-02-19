"""
Service de notifications Web Push.

Utilise Web Push API avec VAPID pour envoyer des notifications
aux navigateurs des utilisateurs.
"""

import json
import logging
from datetime import datetime, time
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import (
    NotificationPreference as NotificationPreferenceModel,
)
from src.core.models import (
    PushSubscription as PushSubscriptionModel,
)
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


class ServiceWebPush:
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
    # NOTIFICATIONS PRÉDÉFINIES
    # ═══════════════════════════════════════════════════════════

    def notifier_stock_bas(self, user_id: str, nom_article: str, quantite: float):
        """Notifie un stock bas."""
        notification = NotificationPush(
            title="📦 Stock bas",
            body=f"{nom_article} est presque épuisé ({quantite} restant)",
            notification_type=TypeNotification.STOCK_BAS,
            url="/?module=cuisine.inventaire",
            tag=f"stock_{nom_article}",
            actions=[
                {"action": "add_to_cart", "title": "Ajouter aux courses"},
                {"action": "dismiss", "title": "Ignorer"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_peremption(
        self, user_id: str, nom_article: str, jours_restants: int, critique: bool = False
    ):
        """Notifie une péremption proche."""
        if jours_restants <= 0:
            title = "⚠️ Produit périmé!"
            body = f"{nom_article} a expiré!"
            notif_type = TypeNotification.PEREMPTION_CRITIQUE
        elif jours_restants == 1:
            title = "🔴 Péremption demain"
            body = f"{nom_article} expire demain"
            notif_type = (
                TypeNotification.PEREMPTION_CRITIQUE
                if critique
                else TypeNotification.PEREMPTION_ALERTE
            )
        else:
            title = "🟡 Péremption proche"
            body = f"{nom_article} expire dans {jours_restants} jours"
            notif_type = TypeNotification.PEREMPTION_ALERTE

        notification = NotificationPush(
            title=title,
            body=body,
            notification_type=notif_type,
            url="/?module=cuisine.inventaire&filter=expiring",
            tag=f"expiry_{nom_article}",
            require_interaction=critique,
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_rappel_repas(
        self, user_id: str, type_repas: str, nom_recette: str, temps_restant: str
    ):
        """Notifie un rappel de repas."""
        notification = NotificationPush(
            title=f"🍽️ {type_repas.title()} dans {temps_restant}",
            body=f"Au menu: {nom_recette}",
            notification_type=TypeNotification.RAPPEL_REPAS,
            url="/?module=planning",
            tag=f"meal_{type_repas}",
            actions=[
                {"action": "view_recipe", "title": "Voir la recette"},
                {"action": "dismiss", "title": "OK"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    def notifier_liste_partagee(self, user_id: str, partage_par: str, nom_liste: str):
        """Notifie le partage d'une liste."""
        notification = NotificationPush(
            title="🛒 Liste partagée",
            body=f"{partage_par} a partagé la liste '{nom_liste}'",
            notification_type=TypeNotification.LISTE_PARTAGEE,
            url="/?module=cuisine.courses",
            actions=[
                {"action": "view", "title": "Voir"},
                {"action": "dismiss", "title": "Plus tard"},
            ],
        )
        return self.envoyer_notification(user_id, notification)

    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE SUPABASE
    # ═══════════════════════════════════════════════════════════

    def _get_supabase_client(self):
        """Récupère le client Supabase."""
        try:
            from supabase import create_client

            from src.core.config import obtenir_parametres

            params = obtenir_parametres()
            supabase_url = getattr(params, "SUPABASE_URL", None)
            supabase_key = getattr(params, "SUPABASE_SERVICE_KEY", None) or getattr(
                params, "SUPABASE_ANON_KEY", None
            )

            if supabase_url and supabase_key:
                return create_client(supabase_url, supabase_key)
        except Exception as e:
            logger.warning(f"Supabase non disponible: {e}")
        return None

    def _sauvegarder_abonnement_supabase(self, subscription: AbonnementPush):
        """Sauvegarde un abonnement en base Supabase."""
        client = self._get_supabase_client()
        if not client:
            logger.debug("Supabase non configuré, abonnement en mémoire uniquement")
            return

        try:
            data = {
                "user_id": subscription.user_id,
                "endpoint": subscription.endpoint,
                "p256dh_key": subscription.p256dh_key,
                "auth_key": subscription.auth_key,
                "user_agent": subscription.user_agent,
                "created_at": subscription.created_at.isoformat(),
                "is_active": subscription.is_active,
            }

            client.table("push_subscriptions").upsert(data, on_conflict="endpoint").execute()

            logger.debug(f"Abonnement sauvegardé pour {subscription.user_id}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde abonnement: {e}")

    def _supprimer_abonnement_supabase(self, user_id: str, endpoint: str):
        """Supprime un abonnement de la base Supabase."""
        client = self._get_supabase_client()
        if not client:
            return

        try:
            client.table("push_subscriptions").delete().match(
                {"user_id": user_id, "endpoint": endpoint}
            ).execute()

            logger.debug(f"Abonnement supprimé pour {user_id}")
        except Exception as e:
            logger.error(f"Erreur suppression abonnement: {e}")

    def _charger_abonnements_supabase(self, user_id: str) -> list[AbonnementPush]:
        """Charge les abonnements depuis Supabase."""
        client = self._get_supabase_client()
        if not client:
            return []

        try:
            response = (
                client.table("push_subscriptions")
                .select("*")
                .eq("user_id", user_id)
                .eq("is_active", True)
                .execute()
            )

            subscriptions = []
            for row in response.data:
                subscriptions.append(
                    AbonnementPush(
                        id=row.get("id"),
                        user_id=row["user_id"],
                        endpoint=row["endpoint"],
                        p256dh_key=row["p256dh_key"],
                        auth_key=row["auth_key"],
                        user_agent=row.get("user_agent"),
                        created_at=datetime.fromisoformat(row["created_at"])
                        if row.get("created_at")
                        else datetime.now(),
                        is_active=row.get("is_active", True),
                    )
                )

            return subscriptions
        except Exception as e:
            logger.error(f"Erreur chargement abonnements: {e}")
            return []

    def _sauvegarder_preferences_supabase(self, preferences: PreferencesNotification):
        """Sauvegarde les préférences en base Supabase."""
        client = self._get_supabase_client()
        if not client:
            return

        try:
            data = {
                "user_id": preferences.user_id,
                "stock_alerts": preferences.alertes_stock,
                "expiration_alerts": preferences.alertes_peremption,
                "meal_reminders": preferences.rappels_repas,
                "activity_reminders": preferences.rappels_activites,
                "shopping_updates": preferences.mises_a_jour_courses,
                "family_reminders": preferences.rappels_famille,
                "system_updates": preferences.mises_a_jour_systeme,
                "quiet_hours_start": preferences.heures_silencieuses_debut,
                "quiet_hours_end": preferences.heures_silencieuses_fin,
                "max_per_hour": preferences.max_par_heure,
                "digest_mode": preferences.mode_digest,
            }

            client.table("notification_preferences").upsert(data, on_conflict="user_id").execute()

            logger.debug(f"Préférences sauvegardées pour {preferences.user_id}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde préférences: {e}")

    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE SQLALCHEMY (ALTERNATIVE)
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def sauvegarder_abonnement_db(
        self,
        user_id: UUID | str,
        endpoint: str,
        p256dh_key: str,
        auth_key: str,
        device_info: dict | None = None,
        db: Session = None,
    ) -> PushSubscriptionModel:
        """
        Sauvegarde un abonnement push via SQLAlchemy.
        """
        existing = (
            db.query(PushSubscriptionModel)
            .filter(PushSubscriptionModel.endpoint == endpoint)
            .first()
        )

        if existing:
            existing.p256dh_key = p256dh_key
            existing.auth_key = auth_key
            existing.device_info = device_info or {}
            existing.last_used = datetime.now()
            db.commit()
            db.refresh(existing)
            return existing

        subscription = PushSubscriptionModel(
            endpoint=endpoint,
            p256dh_key=p256dh_key,
            auth_key=auth_key,
            device_info=device_info or {},
            user_id=UUID(str(user_id)),
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    @avec_session_db
    def lister_abonnements_utilisateur_db(
        self,
        user_id: UUID | str,
        db: Session = None,
    ) -> list[PushSubscriptionModel]:
        """Liste les abonnements push d'un utilisateur via SQLAlchemy."""
        return (
            db.query(PushSubscriptionModel)
            .filter(PushSubscriptionModel.user_id == UUID(str(user_id)))
            .all()
        )

    @avec_session_db
    def supprimer_abonnement_db(
        self,
        endpoint: str,
        db: Session = None,
    ) -> bool:
        """Supprime un abonnement par endpoint via SQLAlchemy."""
        subscription = (
            db.query(PushSubscriptionModel)
            .filter(PushSubscriptionModel.endpoint == endpoint)
            .first()
        )
        if subscription:
            db.delete(subscription)
            db.commit()
            return True
        return False

    @avec_session_db
    def obtenir_preferences_db(
        self,
        user_id: UUID | str,
        db: Session = None,
    ) -> NotificationPreferenceModel | None:
        """Récupère les préférences de notification depuis DB."""
        return (
            db.query(NotificationPreferenceModel)
            .filter(NotificationPreferenceModel.user_id == UUID(str(user_id)))
            .first()
        )

    @avec_session_db
    def sauvegarder_preferences_db(
        self,
        user_id: UUID | str,
        courses_rappel: bool = True,
        repas_suggestion: bool = True,
        stock_alerte: bool = True,
        meteo_alerte: bool = True,
        budget_alerte: bool = True,
        quiet_hours_start: time | None = None,
        quiet_hours_end: time | None = None,
        db: Session = None,
    ) -> NotificationPreferenceModel:
        """Crée ou met à jour les préférences de notification via SQLAlchemy."""
        prefs = (
            db.query(NotificationPreferenceModel)
            .filter(NotificationPreferenceModel.user_id == UUID(str(user_id)))
            .first()
        )

        if not prefs:
            prefs = NotificationPreferenceModel(user_id=UUID(str(user_id)))
            db.add(prefs)

        prefs.courses_rappel = courses_rappel
        prefs.repas_suggestion = repas_suggestion
        prefs.stock_alerte = stock_alerte
        prefs.meteo_alerte = meteo_alerte
        prefs.budget_alerte = budget_alerte
        if quiet_hours_start:
            prefs.quiet_hours_start = quiet_hours_start
        if quiet_hours_end:
            prefs.quiet_hours_end = quiet_hours_end

        db.commit()
        db.refresh(prefs)
        return prefs

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
    notify_stock_low = notifier_stock_bas
    notify_expiration = notifier_peremption
    notify_meal_reminder = notifier_rappel_repas
    notify_shopping_list_shared = notifier_liste_partagee

    # Private methods aliases (for tests)
    _send_web_push = _envoyer_web_push
    _save_subscription_to_db = _sauvegarder_abonnement_supabase
    _remove_subscription_from_db = _supprimer_abonnement_supabase
    _load_subscriptions_from_db = _charger_abonnements_supabase
    _save_preferences_to_db = _sauvegarder_preferences_supabase


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

_service_webpush: ServiceWebPush | None = None


def obtenir_service_webpush() -> ServiceWebPush:
    """Factory pour le service de notifications Web Push."""
    global _service_webpush
    if _service_webpush is None:
        _service_webpush = ServiceWebPush()
    return _service_webpush


__all__ = [
    "ServiceWebPush",
    "obtenir_service_webpush",
]
