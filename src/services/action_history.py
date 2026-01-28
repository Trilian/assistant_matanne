"""
Service d'historique des actions utilisateur.

Trace toutes les actions importantes effectuées par les utilisateurs
pour audit, debugging et fonctionnalités de type "annuler".

Fonctionnalités:
- Logging des actions CRUD
- Historique consultable par utilisateur
- Timeline d'activité
- Restauration d'états précédents
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import streamlit as st
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class ActionType(str, Enum):
    """Types d'actions traçables."""
    # Recettes
    RECETTE_CREATED = "recette.created"
    RECETTE_UPDATED = "recette.updated"
    RECETTE_DELETED = "recette.deleted"
    RECETTE_FAVORITED = "recette.favorited"
    
    # Inventaire
    INVENTAIRE_ADDED = "inventaire.added"
    INVENTAIRE_UPDATED = "inventaire.updated"
    INVENTAIRE_CONSUMED = "inventaire.consumed"
    INVENTAIRE_EXPIRED = "inventaire.expired"
    
    # Courses
    COURSES_LIST_CREATED = "courses.list_created"
    COURSES_ITEM_ADDED = "courses.item_added"
    COURSES_ITEM_CHECKED = "courses.item_checked"
    COURSES_LIST_ARCHIVED = "courses.list_archived"
    
    # Planning
    PLANNING_REPAS_ADDED = "planning.repas_added"
    PLANNING_REPAS_MOVED = "planning.repas_moved"
    PLANNING_REPAS_DELETED = "planning.repas_deleted"
    
    # Famille
    FAMILLE_ACTIVITY_LOGGED = "famille.activity_logged"
    FAMILLE_MILESTONE_ADDED = "famille.milestone_added"
    
    # Système
    SYSTEM_LOGIN = "system.login"
    SYSTEM_LOGOUT = "system.logout"
    SYSTEM_SETTINGS_CHANGED = "system.settings_changed"
    SYSTEM_EXPORT = "system.export"
    SYSTEM_IMPORT = "system.import"


class ActionEntry(BaseModel):
    """Entrée d'historique d'action."""
    
    id: int | None = None
    user_id: str
    user_name: str
    action_type: ActionType
    entity_type: str  # recette, inventaire, courses, etc.
    entity_id: int | None = None
    entity_name: str | None = None
    description: str
    details: dict = Field(default_factory=dict)
    old_value: dict | None = None  # Pour restauration
    new_value: dict | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {"from_attributes": True}


class ActionFilter(BaseModel):
    """Filtres pour la recherche d'actions."""
    
    user_id: str | None = None
    action_types: list[ActionType] | None = None
    entity_type: str | None = None
    entity_id: int | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    search_text: str | None = None
    limit: int = 50
    offset: int = 0


class ActionStats(BaseModel):
    """Statistiques d'activité."""
    
    total_actions: int = 0
    actions_today: int = 0
    actions_this_week: int = 0
    most_active_users: list[dict] = Field(default_factory=list)
    most_common_actions: list[dict] = Field(default_factory=list)
    peak_hours: list[int] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SERVICE D'HISTORIQUE
# ═══════════════════════════════════════════════════════════


class ActionHistoryService:
    """
    Service de traçabilité des actions utilisateur.
    
    Enregistre toutes les actions importantes pour:
    - Audit et conformité
    - Debugging
    - Fonctionnalité "annuler"
    - Timeline d'activité
    """
    
    # Cache en mémoire pour les actions récentes (performance)
    _recent_cache: list[ActionEntry] = []
    _cache_max_size: int = 100
    
    def __init__(self, session: Session | None = None):
        """
        Initialise le service.
        
        Args:
            session: Session SQLAlchemy optionnelle
        """
        self._session = session
    
    # ═══════════════════════════════════════════════════════════
    # ENREGISTREMENT D'ACTIONS
    # ═══════════════════════════════════════════════════════════
    
    def log_action(
        self,
        action_type: ActionType,
        entity_type: str,
        description: str,
        entity_id: int | None = None,
        entity_name: str | None = None,
        details: dict | None = None,
        old_value: dict | None = None,
        new_value: dict | None = None,
    ) -> ActionEntry:
        """
        Enregistre une action.
        
        Args:
            action_type: Type d'action
            entity_type: Type d'entité (recette, inventaire, etc.)
            description: Description lisible de l'action
            entity_id: ID de l'entité concernée
            entity_name: Nom de l'entité (pour affichage)
            details: Détails additionnels
            old_value: Valeur avant modification (pour undo)
            new_value: Valeur après modification
            
        Returns:
            Entrée d'historique créée
        """
        user_id, user_name = self._get_current_user()
        
        entry = ActionEntry(
            user_id=user_id,
            user_name=user_name,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            description=description,
            details=details or {},
            old_value=old_value,
            new_value=new_value,
        )
        
        # Sauvegarder en base
        self._save_to_database(entry)
        
        # Ajouter au cache
        self._add_to_cache(entry)
        
        logger.info(f"Action logged: {action_type.value} - {description}")
        
        return entry
    
    def log_recette_created(self, recette_id: int, nom: str, details: dict = None):
        """Log création de recette."""
        return self.log_action(
            action_type=ActionType.RECETTE_CREATED,
            entity_type="recette",
            entity_id=recette_id,
            entity_name=nom,
            description=f"Recette '{nom}' créée",
            new_value=details,
        )
    
    def log_recette_updated(
        self, recette_id: int, nom: str, old_data: dict, new_data: dict
    ):
        """Log modification de recette."""
        changes = self._compute_changes(old_data, new_data)
        return self.log_action(
            action_type=ActionType.RECETTE_UPDATED,
            entity_type="recette",
            entity_id=recette_id,
            entity_name=nom,
            description=f"Recette '{nom}' modifiée",
            details={"changes": changes},
            old_value=old_data,
            new_value=new_data,
        )
    
    def log_recette_deleted(self, recette_id: int, nom: str, backup_data: dict):
        """Log suppression de recette."""
        return self.log_action(
            action_type=ActionType.RECETTE_DELETED,
            entity_type="recette",
            entity_id=recette_id,
            entity_name=nom,
            description=f"Recette '{nom}' supprimée",
            old_value=backup_data,
        )
    
    def log_inventaire_added(self, item_id: int, nom: str, quantite: float, unite: str):
        """Log ajout à l'inventaire."""
        return self.log_action(
            action_type=ActionType.INVENTAIRE_ADDED,
            entity_type="inventaire",
            entity_id=item_id,
            entity_name=nom,
            description=f"'{nom}' ajouté à l'inventaire ({quantite} {unite})",
            details={"quantite": quantite, "unite": unite},
        )
    
    def log_courses_item_checked(self, liste_id: int, item_name: str, checked: bool):
        """Log cochage d'article de courses."""
        status = "coché" if checked else "décoché"
        return self.log_action(
            action_type=ActionType.COURSES_ITEM_CHECKED,
            entity_type="courses",
            entity_id=liste_id,
            entity_name=item_name,
            description=f"'{item_name}' {status}",
            details={"checked": checked},
        )
    
    def log_planning_repas_added(
        self, planning_id: int, recette_nom: str, date: datetime, type_repas: str
    ):
        """Log ajout de repas au planning."""
        return self.log_action(
            action_type=ActionType.PLANNING_REPAS_ADDED,
            entity_type="planning",
            entity_id=planning_id,
            entity_name=recette_nom,
            description=f"'{recette_nom}' planifié pour le {type_repas} du {date.strftime('%d/%m')}",
            details={"date": date.isoformat(), "type_repas": type_repas},
        )
    
    def log_system_login(self):
        """Log connexion utilisateur."""
        return self.log_action(
            action_type=ActionType.SYSTEM_LOGIN,
            entity_type="system",
            description="Connexion à l'application",
        )
    
    def log_system_logout(self):
        """Log déconnexion utilisateur."""
        return self.log_action(
            action_type=ActionType.SYSTEM_LOGOUT,
            entity_type="system",
            description="Déconnexion de l'application",
        )
    
    # ═══════════════════════════════════════════════════════════
    # CONSULTATION DE L'HISTORIQUE
    # ═══════════════════════════════════════════════════════════
    
    def get_history(self, filters: ActionFilter | None = None) -> list[ActionEntry]:
        """
        Récupère l'historique filtré.
        
        Args:
            filters: Critères de filtrage
            
        Returns:
            Liste d'entrées d'historique
        """
        filters = filters or ActionFilter()
        
        try:
            from src.core.database import get_db_context
            from src.core.models import ActionHistory
            
            with get_db_context() as session:
                query = session.query(ActionHistory)
                
                if filters.user_id:
                    query = query.filter(ActionHistory.user_id == filters.user_id)
                
                if filters.action_types:
                    query = query.filter(
                        ActionHistory.action_type.in_([a.value for a in filters.action_types])
                    )
                
                if filters.entity_type:
                    query = query.filter(ActionHistory.entity_type == filters.entity_type)
                
                if filters.entity_id:
                    query = query.filter(ActionHistory.entity_id == filters.entity_id)
                
                if filters.date_from:
                    query = query.filter(ActionHistory.created_at >= filters.date_from)
                
                if filters.date_to:
                    query = query.filter(ActionHistory.created_at <= filters.date_to)
                
                if filters.search_text:
                    query = query.filter(
                        ActionHistory.description.ilike(f"%{filters.search_text}%")
                    )
                
                entries = (
                    query
                    .order_by(ActionHistory.created_at.desc())
                    .offset(filters.offset)
                    .limit(filters.limit)
                    .all()
                )
                
                return [ActionEntry.model_validate(e) for e in entries]
                
        except Exception as e:
            logger.error(f"Erreur lecture historique: {e}")
            # Fallback sur le cache
            return self._recent_cache[:filters.limit]
    
    def get_user_history(
        self, user_id: str, limit: int = 20
    ) -> list[ActionEntry]:
        """Récupère l'historique d'un utilisateur."""
        return self.get_history(ActionFilter(user_id=user_id, limit=limit))
    
    def get_entity_history(
        self, entity_type: str, entity_id: int, limit: int = 20
    ) -> list[ActionEntry]:
        """Récupère l'historique d'une entité spécifique."""
        return self.get_history(ActionFilter(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        ))
    
    def get_recent_actions(self, limit: int = 10) -> list[ActionEntry]:
        """Récupère les actions récentes (toutes utilisateurs)."""
        return self.get_history(ActionFilter(limit=limit))
    
    # ═══════════════════════════════════════════════════════════
    # STATISTIQUES
    # ═══════════════════════════════════════════════════════════
    
    def get_stats(self, days: int = 7) -> ActionStats:
        """
        Calcule les statistiques d'activité.
        
        Args:
            days: Nombre de jours à analyser
            
        Returns:
            Statistiques d'activité
        """
        try:
            from src.core.database import get_db_context
            from src.core.models import ActionHistory
            from sqlalchemy import func
            
            with get_db_context() as session:
                now = datetime.now()
                week_ago = now - timedelta(days=days)
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Total actions
                total = session.query(func.count(ActionHistory.id)).scalar() or 0
                
                # Actions aujourd'hui
                today_count = (
                    session.query(func.count(ActionHistory.id))
                    .filter(ActionHistory.created_at >= today_start)
                    .scalar() or 0
                )
                
                # Actions cette semaine
                week_count = (
                    session.query(func.count(ActionHistory.id))
                    .filter(ActionHistory.created_at >= week_ago)
                    .scalar() or 0
                )
                
                # Utilisateurs les plus actifs
                top_users = (
                    session.query(
                        ActionHistory.user_name,
                        func.count(ActionHistory.id).label("count")
                    )
                    .filter(ActionHistory.created_at >= week_ago)
                    .group_by(ActionHistory.user_name)
                    .order_by(func.count(ActionHistory.id).desc())
                    .limit(5)
                    .all()
                )
                
                # Actions les plus fréquentes
                top_actions = (
                    session.query(
                        ActionHistory.action_type,
                        func.count(ActionHistory.id).label("count")
                    )
                    .filter(ActionHistory.created_at >= week_ago)
                    .group_by(ActionHistory.action_type)
                    .order_by(func.count(ActionHistory.id).desc())
                    .limit(5)
                    .all()
                )
                
                return ActionStats(
                    total_actions=total,
                    actions_today=today_count,
                    actions_this_week=week_count,
                    most_active_users=[
                        {"name": u[0], "count": u[1]} for u in top_users
                    ],
                    most_common_actions=[
                        {"type": a[0], "count": a[1]} for a in top_actions
                    ],
                )
                
        except Exception as e:
            logger.error(f"Erreur stats: {e}")
            return ActionStats()
    
    # ═══════════════════════════════════════════════════════════
    # FONCTIONNALITÉ UNDO
    # ═══════════════════════════════════════════════════════════
    
    def can_undo(self, action_id: int) -> bool:
        """
        Vérifie si une action peut être annulée.
        
        Args:
            action_id: ID de l'action
            
        Returns:
            True si l'action peut être annulée
        """
        # Types d'actions réversibles
        reversible_types = {
            ActionType.RECETTE_DELETED,
            ActionType.INVENTAIRE_CONSUMED,
            ActionType.COURSES_ITEM_CHECKED,
            ActionType.PLANNING_REPAS_DELETED,
        }
        
        history = self.get_history(ActionFilter(limit=100))
        for entry in history:
            if entry.id == action_id:
                return (
                    entry.action_type in reversible_types
                    and entry.old_value is not None
                )
        
        return False
    
    def undo_action(self, action_id: int) -> bool:
        """
        Annule une action.
        
        Args:
            action_id: ID de l'action à annuler
            
        Returns:
            True si l'annulation a réussi
        """
        # TODO: Implémenter la restauration basée sur old_value
        logger.warning(f"Undo action {action_id} not fully implemented")
        return False
    
    # ═══════════════════════════════════════════════════════════
    # MÉTHODES PRIVÉES
    # ═══════════════════════════════════════════════════════════
    
    def _get_current_user(self) -> tuple[str, str]:
        """Retourne (user_id, user_name) de l'utilisateur courant."""
        try:
            from src.services.auth import get_auth_service
            auth = get_auth_service()
            user = auth.get_current_user()
            if user:
                return user.id, user.display_name
        except Exception:
            pass
        return "anonymous", "Anonyme"
    
    def _save_to_database(self, entry: ActionEntry):
        """Sauvegarde l'entrée en base de données."""
        try:
            from src.core.database import get_db_context
            from src.core.models import ActionHistory
            
            with get_db_context() as session:
                db_entry = ActionHistory(
                    user_id=entry.user_id,
                    user_name=entry.user_name,
                    action_type=entry.action_type.value,
                    entity_type=entry.entity_type,
                    entity_id=entry.entity_id,
                    entity_name=entry.entity_name,
                    description=entry.description,
                    details=entry.details,
                    old_value=entry.old_value,
                    new_value=entry.new_value,
                    created_at=entry.created_at,
                )
                session.add(db_entry)
                session.commit()
                entry.id = db_entry.id
                
        except Exception as e:
            logger.error(f"Erreur sauvegarde historique: {e}")
    
    def _add_to_cache(self, entry: ActionEntry):
        """Ajoute une entrée au cache mémoire."""
        self._recent_cache.insert(0, entry)
        if len(self._recent_cache) > self._cache_max_size:
            self._recent_cache.pop()
    
    def _compute_changes(self, old: dict, new: dict) -> list[dict]:
        """Calcule les changements entre deux états."""
        changes = []
        all_keys = set(old.keys()) | set(new.keys())
        
        for key in all_keys:
            old_val = old.get(key)
            new_val = new.get(key)
            
            if old_val != new_val:
                changes.append({
                    "field": key,
                    "old": old_val,
                    "new": new_val,
                })
        
        return changes


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_activity_timeline(limit: int = 10):
    """Affiche la timeline d'activité récente."""
    service = get_action_history_service()
    actions = service.get_recent_actions(limit=limit)
    
    if not actions:
        st.info("Aucune activité récente")
        return
    
    st.markdown("### 📜 Activité récente")
    
    for action in actions:
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # Icône selon le type
            icons = {
                "recette": "🍳",
                "inventaire": "📦",
                "courses": "🛒",
                "planning": "📅",
                "famille": "👨‍👩‍👧",
                "system": "⚙️",
            }
            icon = icons.get(action.entity_type, "📝")
            st.markdown(f"### {icon}")
        
        with col2:
            st.markdown(f"**{action.description}**")
            st.caption(
                f"{action.user_name} • "
                f"{action.created_at.strftime('%d/%m %H:%M')}"
            )
        
        st.markdown("---")


def render_user_activity(user_id: str):
    """Affiche l'activité d'un utilisateur spécifique."""
    service = get_action_history_service()
    actions = service.get_user_history(user_id, limit=20)
    
    st.markdown(f"### 📊 Activité de l'utilisateur")
    
    if not actions:
        st.info("Aucune activité enregistrée")
        return
    
    for action in actions:
        with st.expander(
            f"{action.description} - {action.created_at.strftime('%d/%m %H:%M')}",
            expanded=False
        ):
            st.json(action.details)


def render_activity_stats():
    """Affiche les statistiques d'activité."""
    service = get_action_history_service()
    stats = service.get_stats()
    
    st.markdown("### 📈 Statistiques")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total actions", stats.total_actions)
    with col2:
        st.metric("Aujourd'hui", stats.actions_today)
    with col3:
        st.metric("Cette semaine", stats.actions_this_week)
    
    if stats.most_active_users:
        st.markdown("**🏆 Utilisateurs les plus actifs:**")
        for user in stats.most_active_users[:3]:
            st.write(f"• {user['name']}: {user['count']} actions")


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_history_service: ActionHistoryService | None = None


def get_action_history_service() -> ActionHistoryService:
    """Factory pour le service d'historique."""
    global _history_service
    if _history_service is None:
        _history_service = ActionHistoryService()
    return _history_service


__all__ = [
    "ActionHistoryService",
    "get_action_history_service",
    "ActionType",
    "ActionEntry",
    "ActionFilter",
    "ActionStats",
    "render_activity_timeline",
    "render_user_activity",
    "render_activity_stats",
]
