"""
Persistance des notifications Web Push.

Mixin pour la gestion des abonnements et préférences
via Supabase et SQLAlchemy.
"""

import logging
from datetime import datetime, time
from uuid import UUID

from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.models import (
    AbonnementPush as PushSubscriptionModel,
)
from src.core.models import (
    PreferenceNotification as NotificationPreferenceModel,
)
from src.services.core.notifications.types import (
    AbonnementPush,
    PreferencesNotification,
)

logger = logging.getLogger(__name__)


class NotificationPersistenceMixin:
    """
    Mixin pour la persistance des notifications.

    Gestion des abonnements et préférences via Supabase
    et SQLAlchemy (méthodes alternatives).
    """

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

            client.table("abonnements_push").upsert(data, on_conflict="endpoint").execute()

            logger.debug(f"Abonnement sauvegardé pour {subscription.user_id}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde abonnement: {e}")

    def _supprimer_abonnement_supabase(self, user_id: str, endpoint: str):
        """Supprime un abonnement de la base Supabase."""
        client = self._get_supabase_client()
        if not client:
            return

        try:
            client.table("abonnements_push").delete().match(
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
                client.table("abonnements_push")
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

            client.table("preferences_notifications").upsert(data, on_conflict="user_id").execute()

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
    # ALIAS RÉTROCOMPATIBILITÉ
    # ═══════════════════════════════════════════════════════════

    _save_subscription_to_db = _sauvegarder_abonnement_supabase
    _remove_subscription_from_db = _supprimer_abonnement_supabase
    _load_subscriptions_from_db = _charger_abonnements_supabase
    _save_preferences_to_db = _sauvegarder_preferences_supabase
