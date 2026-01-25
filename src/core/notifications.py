"""
Notifications Temps Réel - Système de notifications centralisé.

Fonctionnalités :
- Notifications en temps réel dans l'interface
- Historique des notifications
- Catégories (info, warning, success, error)
- Actions rapides depuis les notifications
- Badge compteur non-lues
- Toast notifications
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable
from uuid import uuid4

import streamlit as st

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET MODÈLES
# ═══════════════════════════════════════════════════════════


class NotificationType(str, Enum):
    """Types de notification."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"


class NotificationCategory(str, Enum):
    """Catégories de notification."""
    INVENTAIRE = "inventaire"
    COURSES = "courses"
    RECETTES = "recettes"
    PLANNING = "planning"
    FAMILLE = "famille"
    MAISON = "maison"
    SYSTEME = "systeme"


@dataclass
class Notification:
    """Notification avec métadonnées."""
    
    id: str = field(default_factory=lambda: str(uuid4())[:8])
    titre: str = ""
    message: str = ""
    type: NotificationType = NotificationType.INFO
    category: NotificationCategory = NotificationCategory.SYSTEME
    icone: str = "ℹ️"
    created_at: datetime = field(default_factory=datetime.now)
    read: bool = False
    dismissed: bool = False
    action_label: str | None = None
    action_module: str | None = None
    action_data: dict | None = None
    expires_at: datetime | None = None
    priority: int = 0  # 0=normal, 1=important, 2=urgent
    
    @property
    def is_expired(self) -> bool:
        """Vérifie si la notification est expirée."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    @property
    def age_str(self) -> str:
        """Retourne l'âge formaté."""
        delta = datetime.now() - self.created_at
        
        if delta.seconds < 60:
            return "À l'instant"
        elif delta.seconds < 3600:
            minutes = delta.seconds // 60
            return f"Il y a {minutes} min"
        elif delta.days == 0:
            heures = delta.seconds // 3600
            return f"Il y a {heures}h"
        elif delta.days == 1:
            return "Hier"
        else:
            return f"Il y a {delta.days} jours"
    
    def to_dict(self) -> dict:
        """Convertit en dictionnaire."""
        return {
            "id": self.id,
            "titre": self.titre,
            "message": self.message,
            "type": self.type.value,
            "category": self.category.value,
            "icone": self.icone,
            "created_at": self.created_at.isoformat(),
            "read": self.read,
            "dismissed": self.dismissed,
            "action_label": self.action_label,
            "action_module": self.action_module,
            "priority": self.priority,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Notification":
        """Crée depuis un dictionnaire."""
        return cls(
            id=data.get("id", str(uuid4())[:8]),
            titre=data.get("titre", ""),
            message=data.get("message", ""),
            type=NotificationType(data.get("type", "info")),
            category=NotificationCategory(data.get("category", "systeme")),
            icone=data.get("icone", "ℹ️"),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(),
            read=data.get("read", False),
            dismissed=data.get("dismissed", False),
            action_label=data.get("action_label"),
            action_module=data.get("action_module"),
            priority=data.get("priority", 0),
        )


# ═══════════════════════════════════════════════════════════
# GESTIONNAIRE DE NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class NotificationManager:
    """
    Gestionnaire centralisé des notifications.
    
    Utilise session_state pour persister pendant la session.
    """
    
    SESSION_KEY = "_notifications_store"
    MAX_NOTIFICATIONS = 50
    
    @classmethod
    def _get_store(cls) -> list[dict]:
        """Récupère le store de notifications."""
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = []
        return st.session_state[cls.SESSION_KEY]
    
    @classmethod
    def _set_store(cls, store: list[dict]) -> None:
        """Met à jour le store."""
        st.session_state[cls.SESSION_KEY] = store
    
    @classmethod
    def add(
        cls,
        titre: str,
        message: str = "",
        type: NotificationType = NotificationType.INFO,
        category: NotificationCategory = NotificationCategory.SYSTEME,
        icone: str | None = None,
        action_label: str | None = None,
        action_module: str | None = None,
        action_data: dict | None = None,
        expires_hours: int | None = None,
        priority: int = 0,
    ) -> Notification:
        """
        Ajoute une notification.
        
        Args:
            titre: Titre de la notification
            message: Message détaillé
            type: Type (info, success, warning, error)
            category: Catégorie (inventaire, courses, etc.)
            icone: Emoji icône (auto si None)
            action_label: Label du bouton d'action
            action_module: Module vers lequel naviguer
            expires_hours: Expiration en heures (None = jamais)
            priority: Priorité (0=normal, 1=important, 2=urgent)
            
        Returns:
            Notification créée
        """
        # Icône par défaut selon le type
        if icone is None:
            icones = {
                NotificationType.INFO: "ℹ️",
                NotificationType.SUCCESS: "✅",
                NotificationType.WARNING: "⚠️",
                NotificationType.ERROR: "❌",
                NotificationType.ALERT: "🔔",
            }
            icone = icones.get(type, "ℹ️")
        
        # Expiration
        expires_at = None
        if expires_hours:
            expires_at = datetime.now() + timedelta(hours=expires_hours)
        
        notif = Notification(
            titre=titre,
            message=message,
            type=type,
            category=category,
            icone=icone,
            action_label=action_label,
            action_module=action_module,
            action_data=action_data,
            expires_at=expires_at,
            priority=priority,
        )
        
        store = cls._get_store()
        store.insert(0, notif.to_dict())  # Plus récent en premier
        
        # Limiter le nombre
        if len(store) > cls.MAX_NOTIFICATIONS:
            store = store[:cls.MAX_NOTIFICATIONS]
        
        cls._set_store(store)
        
        logger.debug(f"Notification ajoutée: {titre}")
        return notif
    
    @classmethod
    def get_all(
        cls,
        include_read: bool = True,
        include_dismissed: bool = False,
        category: NotificationCategory | None = None,
        limit: int | None = None,
    ) -> list[Notification]:
        """
        Récupère les notifications.
        
        Args:
            include_read: Inclure les lues
            include_dismissed: Inclure les ignorées
            category: Filtrer par catégorie
            limit: Nombre max
            
        Returns:
            Liste de notifications
        """
        store = cls._get_store()
        notifications = []
        
        for data in store:
            try:
                notif = Notification.from_dict(data)
                
                # Filtrer expirées
                if notif.is_expired:
                    continue
                
                # Filtrer lues
                if not include_read and notif.read:
                    continue
                
                # Filtrer ignorées
                if not include_dismissed and notif.dismissed:
                    continue
                
                # Filtrer par catégorie
                if category and notif.category != category:
                    continue
                
                notifications.append(notif)
                
            except Exception:
                continue
        
        # Trier par priorité puis date
        notifications.sort(key=lambda n: (-n.priority, n.created_at), reverse=True)
        
        if limit:
            notifications = notifications[:limit]
        
        return notifications
    
    @classmethod
    def get_unread_count(cls, category: NotificationCategory | None = None) -> int:
        """Compte les notifications non lues."""
        return len(cls.get_all(include_read=False, category=category))
    
    @classmethod
    def mark_as_read(cls, notification_id: str) -> bool:
        """Marque une notification comme lue."""
        store = cls._get_store()
        
        for data in store:
            if data.get("id") == notification_id:
                data["read"] = True
                cls._set_store(store)
                return True
        
        return False
    
    @classmethod
    def mark_all_read(cls, category: NotificationCategory | None = None) -> int:
        """Marque toutes les notifications comme lues."""
        store = cls._get_store()
        count = 0
        
        for data in store:
            if category is None or data.get("category") == category.value:
                if not data.get("read", False):
                    data["read"] = True
                    count += 1
        
        cls._set_store(store)
        return count
    
    @classmethod
    def dismiss(cls, notification_id: str) -> bool:
        """Ignore une notification."""
        store = cls._get_store()
        
        for data in store:
            if data.get("id") == notification_id:
                data["dismissed"] = True
                cls._set_store(store)
                return True
        
        return False
    
    @classmethod
    def clear_all(cls, category: NotificationCategory | None = None) -> int:
        """Supprime toutes les notifications."""
        if category is None:
            count = len(cls._get_store())
            cls._set_store([])
            return count
        
        store = cls._get_store()
        new_store = [d for d in store if d.get("category") != category.value]
        count = len(store) - len(new_store)
        cls._set_store(new_store)
        return count
    
    @classmethod
    def cleanup_expired(cls) -> int:
        """Nettoie les notifications expirées."""
        store = cls._get_store()
        now = datetime.now()
        
        new_store = []
        for data in store:
            expires = data.get("expires_at")
            if expires:
                try:
                    expires_dt = datetime.fromisoformat(expires)
                    if expires_dt < now:
                        continue
                except Exception:
                    pass
            new_store.append(data)
        
        removed = len(store) - len(new_store)
        cls._set_store(new_store)
        return removed


# ═══════════════════════════════════════════════════════════
# HELPERS DE CRÉATION RAPIDE
# ═══════════════════════════════════════════════════════════


def notify_info(titre: str, message: str = "", **kwargs) -> Notification:
    """Crée une notification info."""
    return NotificationManager.add(titre, message, NotificationType.INFO, **kwargs)


def notify_success(titre: str, message: str = "", **kwargs) -> Notification:
    """Crée une notification succès."""
    return NotificationManager.add(titre, message, NotificationType.SUCCESS, **kwargs)


def notify_warning(titre: str, message: str = "", **kwargs) -> Notification:
    """Crée une notification avertissement."""
    return NotificationManager.add(titre, message, NotificationType.WARNING, priority=1, **kwargs)


def notify_error(titre: str, message: str = "", **kwargs) -> Notification:
    """Crée une notification erreur."""
    return NotificationManager.add(titre, message, NotificationType.ERROR, priority=2, **kwargs)


def notify_stock_bas(article_nom: str, quantite: float, seuil: float) -> Notification:
    """Notification spécifique stock bas."""
    return NotificationManager.add(
        titre=f"Stock bas: {article_nom}",
        message=f"Quantité: {quantite} (seuil: {seuil})",
        type=NotificationType.WARNING,
        category=NotificationCategory.INVENTAIRE,
        action_label="Voir inventaire",
        action_module="cuisine.inventaire",
        priority=1,
    )


def notify_peremption(article_nom: str, jours: int) -> Notification:
    """Notification spécifique péremption."""
    urgence = NotificationType.ERROR if jours <= 0 else NotificationType.WARNING
    priority = 2 if jours <= 0 else 1
    
    if jours <= 0:
        titre = f"EXPIRÉ: {article_nom}"
        message = "À consommer immédiatement ou jeter"
    else:
        titre = f"Expire bientôt: {article_nom}"
        message = f"Expire dans {jours} jour(s)"
    
    return NotificationManager.add(
        titre=titre,
        message=message,
        type=urgence,
        category=NotificationCategory.INVENTAIRE,
        action_label="Voir inventaire",
        action_module="cuisine.inventaire",
        priority=priority,
    )


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_notification_badge() -> int:
    """
    Affiche le badge avec le nombre de notifications non lues.
    
    Returns:
        Nombre de notifications non lues
    """
    count = NotificationManager.get_unread_count()
    
    if count > 0:
        st.markdown(
            f'<span style="'
            f'background: #FF5722; color: white; '
            f'padding: 2px 8px; border-radius: 12px; '
            f'font-size: 0.8rem; font-weight: bold;'
            f'">{count}</span>',
            unsafe_allow_html=True
        )
    
    return count


def render_notification_center():
    """Affiche le centre de notifications dans un expander."""
    
    count = NotificationManager.get_unread_count()
    label = f"🔔 Notifications ({count} non lues)" if count > 0 else "🔔 Notifications"
    
    with st.expander(label, expanded=count > 0):
        # Actions en haut
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("✓ Tout marquer lu", key="notif_mark_all", use_container_width=True):
                NotificationManager.mark_all_read()
                st.rerun()
        with col2:
            if st.button("🗑️ Tout effacer", key="notif_clear_all", use_container_width=True):
                NotificationManager.clear_all()
                st.rerun()
        
        st.markdown("---")
        
        # Liste des notifications
        notifications = NotificationManager.get_all(limit=10)
        
        if not notifications:
            st.info("Aucune notification")
            return
        
        for notif in notifications:
            render_notification_item(notif)


def render_notification_item(notif: Notification):
    """Affiche une notification individuelle."""
    
    # Couleurs selon type
    colors = {
        NotificationType.INFO: "#2196F3",
        NotificationType.SUCCESS: "#4CAF50",
        NotificationType.WARNING: "#FF9800",
        NotificationType.ERROR: "#F44336",
        NotificationType.ALERT: "#9C27B0",
    }
    color = colors.get(notif.type, "#9E9E9E")
    
    # Style non-lu
    bg_color = "#f8f9fa" if notif.read else "#fff3e0"
    font_weight = "normal" if notif.read else "500"
    
    st.markdown(
        f'''
        <div style="
            background: {bg_color};
            border-left: 4px solid {color};
            border-radius: 8px;
            padding: 0.8rem;
            margin-bottom: 0.5rem;
        ">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">{notif.icone}</span>
                    <strong style="font-weight: {font_weight};">{notif.titre}</strong>
                    <br>
                    <small style="color: #6c757d;">{notif.message}</small>
                    <br>
                    <small style="color: #9e9e9e;">{notif.age_str} • {notif.category.value}</small>
                </div>
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    
    # Boutons d'action
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if notif.action_label and notif.action_module:
            if st.button(notif.action_label, key=f"action_{notif.id}", use_container_width=True):
                from src.core.state import StateManager
                NotificationManager.mark_as_read(notif.id)
                StateManager.navigate_to(notif.action_module)
                st.rerun()
    
    with col2:
        if not notif.read:
            if st.button("✓", key=f"read_{notif.id}", help="Marquer comme lu"):
                NotificationManager.mark_as_read(notif.id)
                st.rerun()
    
    with col3:
        if st.button("✕", key=f"dismiss_{notif.id}", help="Ignorer"):
            NotificationManager.dismiss(notif.id)
            st.rerun()


def render_toast_notifications():
    """Affiche les notifications récentes en toast."""
    
    # Notifications non lues des 5 dernières minutes
    notifications = NotificationManager.get_all(include_read=False, limit=3)
    recent = [
        n for n in notifications 
        if (datetime.now() - n.created_at).seconds < 300
    ]
    
    for notif in recent:
        if notif.type == NotificationType.SUCCESS:
            st.success(f"{notif.icone} {notif.titre}")
        elif notif.type == NotificationType.WARNING:
            st.warning(f"{notif.icone} {notif.titre}")
        elif notif.type == NotificationType.ERROR:
            st.error(f"{notif.icone} {notif.titre}")
        else:
            st.info(f"{notif.icone} {notif.titre}")


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    "Notification",
    "NotificationType",
    "NotificationCategory",
    "NotificationManager",
    "notify_info",
    "notify_success",
    "notify_warning",
    "notify_error",
    "notify_stock_bas",
    "notify_peremption",
    "render_notification_badge",
    "render_notification_center",
    "render_toast_notifications",
]
