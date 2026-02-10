"""
Service de notifications push.

Utilise Web Push API et Supabase pour envoyer des notifications
aux utilisateurs même quand l'application n'est pas ouverte.

Fonctionnalités:
- Inscription aux notifications push
- Envoi de notifications
- Gestion des abonnements
- Notifications programmées
"""

import json
import logging
from datetime import datetime, timedelta, time
from enum import Enum
from typing import Any
from uuid import UUID

import streamlit as st
import streamlit.components.v1 as components
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db
from src.services.push_notifications_utils import (
    check_notification_type_enabled,
    is_quiet_hours,
    can_send_during_quiet_hours,
    should_send_notification,
    build_push_payload,
    build_subscription_info,
    generate_count_key,
    validate_subscription,
    validate_preferences,
    create_stock_notification,
    create_expiration_notification,
    create_meal_reminder_notification,
)
from src.core.models import (
    PushSubscription as PushSubscriptionModel,
    NotificationPreference as NotificationPreferenceModel,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════


# Clés VAPID pour Web Push (à remplacer par vos propres clés)
# Générer avec: npx web-push generate-vapid-keys
VAPID_PUBLIC_KEY = "BEl62iUYgUivxIkv69yViEuiBIa-Ib9-SkvMeAtA3LFgDzkrxZJjSgSnfckjBJuBkr3qBUYIHBQFLXYp5Nksh8U"
VAPID_PRIVATE_KEY = ""  # À configurer via variable d'environnement
VAPID_EMAIL = "mailto:contact@assistant-matanne.fr"


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class NotificationType(str, Enum):
    """Types de notifications push."""
    # Alertes importantes
    STOCK_LOW = "stock_low"
    EXPIRATION_WARNING = "expiration_warning"
    EXPIRATION_CRITICAL = "expiration_critical"
    
    # Planning
    MEAL_REMINDER = "meal_reminder"
    ACTIVITY_REMINDER = "activity_reminder"
    
    # Courses
    SHOPPING_LIST_SHARED = "shopping_list_shared"
    SHOPPING_LIST_UPDATED = "shopping_list_updated"
    
    # Famille
    MILESTONE_REMINDER = "milestone_reminder"
    HEALTH_CHECK_REMINDER = "health_check_reminder"
    
    # Système
    SYSTEM_UPDATE = "system_update"
    SYNC_COMPLETE = "sync_complete"


class PushSubscription(BaseModel):
    """Abonnement push d'un utilisateur."""
    
    id: int | None = None
    user_id: str
    endpoint: str
    p256dh_key: str
    auth_key: str
    user_agent: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    last_used: datetime | None = None
    is_active: bool = True


class PushNotification(BaseModel):
    """Notification push à envoyer."""
    
    id: int | None = None
    title: str
    body: str
    icon: str = "/static/icons/icon-192x192.png"
    badge: str = "/static/icons/badge-72x72.png"
    tag: str | None = None  # Pour regrouper/remplacer les notifications
    notification_type: NotificationType = NotificationType.SYSTEM_UPDATE
    url: str = "/"  # URL à ouvrir au clic
    data: dict = Field(default_factory=dict)
    actions: list[dict] = Field(default_factory=list)
    vibrate: list[int] = Field(default_factory=lambda: [100, 50, 100])
    require_interaction: bool = False
    silent: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class NotificationPreferences(BaseModel):
    """Préférences de notification d'un utilisateur."""
    
    user_id: str
    
    # Catégories activées
    stock_alerts: bool = True
    expiration_alerts: bool = True
    meal_reminders: bool = True
    activity_reminders: bool = True
    shopping_updates: bool = True
    family_reminders: bool = True
    system_updates: bool = False
    
    # Horaires de silence
    quiet_hours_start: int | None = 22  # 22h
    quiet_hours_end: int | None = 7  # 7h
    
    # Fréquence
    max_per_hour: int = 5
    digest_mode: bool = False  # Regrouper en résumé


# ═══════════════════════════════════════════════════════════
# SERVICE DE NOTIFICATIONS PUSH
# ═══════════════════════════════════════════════════════════


class PushNotificationService:
    """
    Service d'envoi de notifications push.
    
    Utilise Web Push API avec VAPID pour envoyer des notifications
    aux navigateurs des utilisateurs.
    """
    
    def __init__(self):
        """Initialise le service."""
        self._subscriptions: dict[str, list[PushSubscription]] = {}
        self._preferences: dict[str, NotificationPreferences] = {}
        self._sent_count: dict[str, int] = {}  # user_id -> count this hour
    
    # ═══════════════════════════════════════════════════════════
    # GESTION DES ABONNEMENTS
    # ═══════════════════════════════════════════════════════════
    
    def save_subscription(
        self,
        user_id: str,
        subscription_info: dict
    ) -> PushSubscription:
        """
        Sauvegarde un nouvel abonnement push.
        
        Args:
            user_id: ID de l'utilisateur
            subscription_info: Info d'abonnement du navigateur
            
        Returns:
            Abonnement créé
        """
        subscription = PushSubscription(
            user_id=user_id,
            endpoint=subscription_info["endpoint"],
            p256dh_key=subscription_info["keys"]["p256dh"],
            auth_key=subscription_info["keys"]["auth"],
        )
        
        # Sauvegarder en mémoire (et en base dans une vraie implémentation)
        if user_id not in self._subscriptions:
            self._subscriptions[user_id] = []
        
        # Éviter les doublons
        existing = [s for s in self._subscriptions[user_id] 
                   if s.endpoint == subscription.endpoint]
        if not existing:
            self._subscriptions[user_id].append(subscription)
            self._save_subscription_to_db(subscription)
        
        logger.info(f"✅ Abonnement push enregistré pour {user_id}")
        return subscription
    
    def remove_subscription(self, user_id: str, endpoint: str):
        """Supprime un abonnement."""
        if user_id in self._subscriptions:
            self._subscriptions[user_id] = [
                s for s in self._subscriptions[user_id]
                if s.endpoint != endpoint
            ]
        self._remove_subscription_from_db(user_id, endpoint)
        logger.info(f"Abonnement supprimé pour {user_id}")
    
    def get_user_subscriptions(self, user_id: str) -> list[PushSubscription]:
        """Récupère les abonnements d'un utilisateur."""
        # Essayer le cache, sinon la base
        if user_id in self._subscriptions:
            return self._subscriptions[user_id]
        
        subs = self._load_subscriptions_from_db(user_id)
        self._subscriptions[user_id] = subs
        return subs
    
    # ═══════════════════════════════════════════════════════════
    # PRÉFÉRENCES
    # ═══════════════════════════════════════════════════════════
    
    def get_preferences(self, user_id: str) -> NotificationPreferences:
        """Récupère les préférences de notification."""
        if user_id not in self._preferences:
            self._preferences[user_id] = NotificationPreferences(user_id=user_id)
        return self._preferences[user_id]
    
    def update_preferences(
        self,
        user_id: str,
        preferences: NotificationPreferences
    ):
        """Met à jour les préférences."""
        self._preferences[user_id] = preferences
        self._save_preferences_to_db(preferences)
    
    def should_send(
        self,
        user_id: str,
        notification_type: NotificationType
    ) -> bool:
        """
        Vérifie si on doit envoyer une notification.
        
        Prend en compte:
        - Préférences utilisateur
        - Heures de silence
        - Limite par heure
        
        Utilise les fonctions pures de push_notifications_utils.
        """
        prefs = self.get_preferences(user_id)
        now = datetime.now()
        
        # Convertir prefs en dict pour les utilitaires
        prefs_dict = {
            "stock_alerts": prefs.stock_alerts,
            "expiration_alerts": prefs.expiration_alerts,
            "meal_reminders": prefs.meal_reminders,
            "activity_reminders": prefs.activity_reminders,
            "shopping_updates": prefs.shopping_updates,
            "family_reminders": prefs.family_reminders,
            "system_updates": prefs.system_updates,
            "quiet_hours_enabled": bool(prefs.quiet_hours_start and prefs.quiet_hours_end),
            "quiet_hours_start": prefs.quiet_hours_start,
            "quiet_hours_end": prefs.quiet_hours_end,
            "max_per_hour": prefs.max_per_hour,
        }
        
        # Utiliser should_send_notification de push_notifications_utils
        count_key = generate_count_key(user_id, now)
        current_count = self._sent_count.get(count_key, 0)
        
        result, _ = should_send_notification(
            notification_type=notification_type,
            preferences=prefs_dict,
            sent_count_this_hour=current_count,
            current_hour=now.hour
        )
        return result
    
    # ═══════════════════════════════════════════════════════════
    # ENVOI DE NOTIFICATIONS
    # ═══════════════════════════════════════════════════════════
    
    def send_notification(
        self,
        user_id: str,
        notification: PushNotification
    ) -> bool:
        """
        Envoie une notification push à un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            notification: Notification à envoyer
            
        Returns:
            True si envoyé avec succès
        """
        if not self.should_send(user_id, notification.notification_type):
            logger.debug(f"Notification ignorée pour {user_id} (préférences)")
            return False
        
        subscriptions = self.get_user_subscriptions(user_id)
        
        if not subscriptions:
            logger.warning(f"Pas d'abonnement push pour {user_id}")
            return False
        
        success = False
        for sub in subscriptions:
            try:
                self._send_web_push(sub, notification)
                sub.last_used = datetime.now()
                success = True
            except Exception as e:
                logger.error(f"Erreur envoi push: {e}")
                # Désactiver les abonnements invalides
                if "410" in str(e) or "404" in str(e):
                    sub.is_active = False
        
        # Incrémenter le compteur
        if success:
            now = datetime.now()
            count_key = f"{user_id}_{now.strftime('%Y%m%d%H')}"
            self._sent_count[count_key] = self._sent_count.get(count_key, 0) + 1
        
        return success
    
    def send_to_all_users(self, notification: PushNotification) -> int:
        """
        Envoie une notification à tous les utilisateurs.
        
        Returns:
            Nombre d'utilisateurs notifiés
        """
        count = 0
        for user_id in self._subscriptions:
            if self.send_notification(user_id, notification):
                count += 1
        return count
    
    def _send_web_push(self, subscription: PushSubscription, notification: PushNotification):
        """Envoie via Web Push API."""
        try:
            from pywebpush import webpush, WebPushException
            
            payload = json.dumps({
                "title": notification.title,
                "body": notification.body,
                "icon": notification.icon,
                "badge": notification.badge,
                "tag": notification.tag,
                "data": {
                    "url": notification.url,
                    "type": notification.notification_type.value,
                    **notification.data
                },
                "actions": notification.actions,
                "vibrate": notification.vibrate,
                "requireInteraction": notification.require_interaction,
                "silent": notification.silent,
                "timestamp": notification.timestamp.isoformat(),
            })
            
            webpush(
                subscription_info={
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh_key,
                        "auth": subscription.auth_key,
                    }
                },
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": VAPID_EMAIL}
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
    
    def notify_stock_low(self, user_id: str, item_name: str, quantity: float):
        """Notifie un stock bas."""
        notification = PushNotification(
            title="📦 Stock bas",
            body=f"{item_name} est presque épuisé ({quantity} restant)",
            notification_type=NotificationType.STOCK_LOW,
            url="/?module=cuisine.inventaire",
            tag=f"stock_{item_name}",
            actions=[
                {"action": "add_to_cart", "title": "Ajouter aux courses"},
                {"action": "dismiss", "title": "Ignorer"}
            ]
        )
        return self.send_notification(user_id, notification)
    
    def notify_expiration(
        self,
        user_id: str,
        item_name: str,
        days_left: int,
        critical: bool = False
    ):
        """Notifie une péremption proche."""
        if days_left <= 0:
            title = "⚠️ Produit périmé!"
            body = f"{item_name} a expiré!"
            notif_type = NotificationType.EXPIRATION_CRITICAL
        elif days_left == 1:
            title = "🔴 Péremption demain"
            body = f"{item_name} expire demain"
            notif_type = NotificationType.EXPIRATION_CRITICAL if critical else NotificationType.EXPIRATION_WARNING
        else:
            title = "🟡 Péremption proche"
            body = f"{item_name} expire dans {days_left} jours"
            notif_type = NotificationType.EXPIRATION_WARNING
        
        notification = PushNotification(
            title=title,
            body=body,
            notification_type=notif_type,
            url="/?module=cuisine.inventaire&filter=expiring",
            tag=f"expiry_{item_name}",
            require_interaction=critical,
        )
        return self.send_notification(user_id, notification)
    
    def notify_meal_reminder(
        self,
        user_id: str,
        meal_type: str,
        recipe_name: str,
        time_until: str
    ):
        """Notifie un rappel de repas."""
        notification = PushNotification(
            title=f"🍽️ {meal_type.title()} dans {time_until}",
            body=f"Au menu: {recipe_name}",
            notification_type=NotificationType.MEAL_REMINDER,
            url="/?module=planning",
            tag=f"meal_{meal_type}",
            actions=[
                {"action": "view_recipe", "title": "Voir la recette"},
                {"action": "dismiss", "title": "OK"}
            ]
        )
        return self.send_notification(user_id, notification)
    
    def notify_shopping_list_shared(
        self,
        user_id: str,
        shared_by: str,
        list_name: str
    ):
        """Notifie le partage d'une liste."""
        notification = PushNotification(
            title="🛒 Liste partagée",
            body=f"{shared_by} a partagé la liste '{list_name}'",
            notification_type=NotificationType.SHOPPING_LIST_SHARED,
            url="/?module=cuisine.courses",
            actions=[
                {"action": "view", "title": "Voir"},
                {"action": "dismiss", "title": "Plus tard"}
            ]
        )
        return self.send_notification(user_id, notification)
    
    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE SUPABASE
    # ═══════════════════════════════════════════════════════════
    
    def _get_supabase_client(self):
        """Récupère le client Supabase."""
        try:
            from supabase import create_client
            from src.core.config import obtenir_parametres
            
            params = obtenir_parametres()
            supabase_url = getattr(params, 'SUPABASE_URL', None)
            supabase_key = getattr(params, 'SUPABASE_SERVICE_KEY', None) or getattr(params, 'SUPABASE_ANON_KEY', None)
            
            if supabase_url and supabase_key:
                return create_client(supabase_url, supabase_key)
        except Exception as e:
            logger.warning(f"Supabase non disponible: {e}")
        return None
    
    def _save_subscription_to_db(self, subscription: PushSubscription):
        """Sauvegarde un abonnement en base Supabase."""
        client = self._get_supabase_client()
        if not client:
            logger.debug("Supabase non configuré, abonnement en mémoire uniquement")
            return
        
        try:
            # Table: push_subscriptions
            data = {
                "user_id": subscription.user_id,
                "endpoint": subscription.endpoint,
                "p256dh_key": subscription.p256dh_key,
                "auth_key": subscription.auth_key,
                "user_agent": subscription.user_agent,
                "created_at": subscription.created_at.isoformat(),
                "is_active": subscription.is_active,
            }
            
            # Upsert basé sur endpoint
            client.table("push_subscriptions").upsert(
                data,
                on_conflict="endpoint"
            ).execute()
            
            logger.debug(f"Abonnement sauvegardé pour {subscription.user_id}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde abonnement: {e}")
    
    def _remove_subscription_from_db(self, user_id: str, endpoint: str):
        """Supprime un abonnement de la base Supabase."""
        client = self._get_supabase_client()
        if not client:
            return
        
        try:
            client.table("push_subscriptions").delete().match({
                "user_id": user_id,
                "endpoint": endpoint
            }).execute()
            
            logger.debug(f"Abonnement supprimé pour {user_id}")
        except Exception as e:
            logger.error(f"Erreur suppression abonnement: {e}")
    
    def _load_subscriptions_from_db(self, user_id: str) -> list[PushSubscription]:
        """Charge les abonnements depuis Supabase."""
        client = self._get_supabase_client()
        if not client:
            return []
        
        try:
            response = client.table("push_subscriptions").select("*").eq(
                "user_id", user_id
            ).eq("is_active", True).execute()
            
            subscriptions = []
            for row in response.data:
                subscriptions.append(PushSubscription(
                    id=row.get("id"),
                    user_id=row["user_id"],
                    endpoint=row["endpoint"],
                    p256dh_key=row["p256dh_key"],
                    auth_key=row["auth_key"],
                    user_agent=row.get("user_agent"),
                    created_at=datetime.fromisoformat(row["created_at"]) if row.get("created_at") else datetime.now(),
                    is_active=row.get("is_active", True),
                ))
            
            return subscriptions
        except Exception as e:
            logger.error(f"Erreur chargement abonnements: {e}")
            return []
    
    def _save_preferences_to_db(self, preferences: NotificationPreferences):
        """Sauvegarde les préférences en base Supabase."""
        client = self._get_supabase_client()
        if not client:
            return
        
        try:
            data = {
                "user_id": preferences.user_id,
                "stock_alerts": preferences.stock_alerts,
                "expiration_alerts": preferences.expiration_alerts,
                "meal_reminders": preferences.meal_reminders,
                "activity_reminders": preferences.activity_reminders,
                "shopping_updates": preferences.shopping_updates,
                "family_reminders": preferences.family_reminders,
                "system_updates": preferences.system_updates,
                "quiet_hours_start": preferences.quiet_hours_start,
                "quiet_hours_end": preferences.quiet_hours_end,
                "max_per_hour": preferences.max_per_hour,
                "digest_mode": preferences.digest_mode,
            }
            
            client.table("notification_preferences").upsert(
                data,
                on_conflict="user_id"
            ).execute()
            
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
        
        Args:
            user_id: UUID de l'utilisateur
            endpoint: URL de l'endpoint push
            p256dh_key: Clé p256dh
            auth_key: Clé d'authentification
            device_info: Infos appareil (optionnel)
            db: Session SQLAlchemy
            
        Returns:
            Modèle PushSubscription créé
        """
        # Vérifier si l'endpoint existe déjà
        existing = db.query(PushSubscriptionModel).filter(
            PushSubscriptionModel.endpoint == endpoint
        ).first()
        
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
    def lister_abonnements_utilisateur(
        self,
        user_id: UUID | str,
        db: Session = None,
    ) -> list[PushSubscriptionModel]:
        """
        Liste les abonnements push d'un utilisateur.
        
        Args:
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy
            
        Returns:
            Liste des abonnements
        """
        return db.query(PushSubscriptionModel).filter(
            PushSubscriptionModel.user_id == UUID(str(user_id))
        ).all()

    @avec_session_db
    def supprimer_abonnement_db(
        self,
        endpoint: str,
        db: Session = None,
    ) -> bool:
        """
        Supprime un abonnement par endpoint.
        
        Args:
            endpoint: URL de l'endpoint
            db: Session SQLAlchemy
            
        Returns:
            True si supprimé
        """
        subscription = db.query(PushSubscriptionModel).filter(
            PushSubscriptionModel.endpoint == endpoint
        ).first()
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
        """
        Récupère les préférences de notification depuis DB.
        
        Args:
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy
            
        Returns:
            Préférences ou None
        """
        return db.query(NotificationPreferenceModel).filter(
            NotificationPreferenceModel.user_id == UUID(str(user_id))
        ).first()

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
        """
        Crée ou met à jour les préférences de notification.
        
        Args:
            user_id: UUID de l'utilisateur
            courses_rappel: Rappels courses
            repas_suggestion: Suggestions repas
            stock_alerte: Alertes stock
            meteo_alerte: Alertes météo
            budget_alerte: Alertes budget
            quiet_hours_start: Début heures silencieuses
            quiet_hours_end: Fin heures silencieuses
            db: Session SQLAlchemy
            
        Returns:
            Préférences créées/mises à jour
        """
        prefs = db.query(NotificationPreferenceModel).filter(
            NotificationPreferenceModel.user_id == UUID(str(user_id))
        ).first()
        
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
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_push_permission_request():
    """
    Affiche une demande de permission pour les notifications push.
    """
    html = f"""
    <div id="push-permission-container" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        display: none;
    ">
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 24px;">🔔</span>
            <div style="flex: 1;">
                <div style="font-weight: 600;">Activer les notifications</div>
                <div style="font-size: 13px; opacity: 0.9;">
                    Recevez des alertes pour les péremptions et rappels
                </div>
            </div>
            <button onclick="requestPushPermission()" style="
                background: white;
                color: #667eea;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                cursor: pointer;
            ">Activer</button>
            <button onclick="dismissPushPrompt()" style="
                background: transparent;
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                padding: 8px 12px;
                border-radius: 6px;
                cursor: pointer;
            ">Plus tard</button>
        </div>
    </div>
    
    <script>
        const VAPID_PUBLIC_KEY = '{VAPID_PUBLIC_KEY}';
        
        // Afficher si permission non accordée
        if ('Notification' in window && Notification.permission === 'default') {{
            document.getElementById('push-permission-container').style.display = 'block';
        }}
        
        async function requestPushPermission() {{
            try {{
                const permission = await Notification.requestPermission();
                
                if (permission === 'granted') {{
                    await subscribeToPush();
                    document.getElementById('push-permission-container').style.display = 'none';
                }}
            }} catch (error) {{
                console.error('Push permission error:', error);
            }}
        }}
        
        async function subscribeToPush() {{
            if ('serviceWorker' in navigator) {{
                const registration = await navigator.serviceWorker.ready;
                
                const subscription = await registration.pushManager.subscribe({{
                    userVisibleOnly: true,
                    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
                }});
                
                // Envoyer l'abonnement au serveur
                console.log('Push subscription:', JSON.stringify(subscription));
                // TODO: Envoyer à l'API
            }}
        }}
        
        function dismissPushPrompt() {{
            document.getElementById('push-permission-container').style.display = 'none';
            localStorage.setItem('push_prompt_dismissed', Date.now());
        }}
        
        function urlBase64ToUint8Array(base64String) {{
            const padding = '='.repeat((4 - base64String.length % 4) % 4);
            const base64 = (base64String + padding)
                .replace(/-/g, '+')
                .replace(/_/g, '/');
            
            const rawData = window.atob(base64);
            const outputArray = new Uint8Array(rawData.length);
            
            for (let i = 0; i < rawData.length; ++i) {{
                outputArray[i] = rawData.charCodeAt(i);
            }}
            return outputArray;
        }}
    </script>
    """
    
    components.html(html, height=100)


def render_notification_preferences():
    """Affiche les paramètres de notifications."""
    push_service = get_push_notification_service()
    
    # Récupérer l'utilisateur courant
    try:
        from src.services.auth import get_auth_service
        auth = get_auth_service()
        user = auth.get_current_user()
        user_id = user.id if user else "anonymous"
    except Exception:
        user_id = "anonymous"
    
    prefs = push_service.get_preferences(user_id)
    
    st.markdown("### 🔔 Préférences de notifications")
    
    with st.form("notification_prefs"):
        st.markdown("**Catégories de notifications:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            stock_alerts = st.checkbox("Stock bas", value=prefs.stock_alerts)
            expiration_alerts = st.checkbox("Péremptions", value=prefs.expiration_alerts)
            meal_reminders = st.checkbox("Rappels de repas", value=prefs.meal_reminders)
        
        with col2:
            activity_reminders = st.checkbox("Rappels d'activités", value=prefs.activity_reminders)
            shopping_updates = st.checkbox("Mises à jour courses", value=prefs.shopping_updates)
            family_reminders = st.checkbox("Rappels famille", value=prefs.family_reminders)
        
        system_updates = st.checkbox("Mises à jour système", value=prefs.system_updates)
        
        st.markdown("---")
        st.markdown("**Heures de silence:**")
        
        col1, col2 = st.columns(2)
        with col1:
            quiet_start = st.number_input(
                "Début (heure)",
                min_value=0, max_value=23,
                value=prefs.quiet_hours_start or 22
            )
        with col2:
            quiet_end = st.number_input(
                "Fin (heure)",
                min_value=0, max_value=23,
                value=prefs.quiet_hours_end or 7
            )
        
        st.markdown("---")
        max_per_hour = st.slider(
            "Maximum de notifications par heure",
            min_value=1, max_value=20,
            value=prefs.max_per_hour
        )
        
        if st.form_submit_button("Enregistrer", use_container_width=True):
            new_prefs = NotificationPreferences(
                user_id=user_id,
                stock_alerts=stock_alerts,
                expiration_alerts=expiration_alerts,
                meal_reminders=meal_reminders,
                activity_reminders=activity_reminders,
                shopping_updates=shopping_updates,
                family_reminders=family_reminders,
                system_updates=system_updates,
                quiet_hours_start=quiet_start,
                quiet_hours_end=quiet_end,
                max_per_hour=max_per_hour,
            )
            push_service.update_preferences(user_id, new_prefs)
            st.success("✅ Préférences enregistrées!")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_push_service: PushNotificationService | None = None


def get_push_notification_service() -> PushNotificationService:
    """Factory pour le service de notifications push."""
    global _push_service
    if _push_service is None:
        _push_service = PushNotificationService()
    return _push_service


__all__ = [
    "PushNotificationService",
    "get_push_notification_service",
    "PushNotification",
    "PushSubscription",
    "NotificationType",
    "NotificationPreferences",
    "render_push_permission_request",
    "render_notification_preferences",
]

