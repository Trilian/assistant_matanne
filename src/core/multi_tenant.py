"""
Service Multi-utilisateurs - Isolation des données par utilisateur

[OK] Filtrage automatique par user_id
[OK] Décorateur pour isolation données
[OK] Middleware pour injection user context
[OK] Helpers pour requêtes multi-tenant
"""

import logging
from functools import wraps
from typing import Any, Callable, TypeVar, Optional
from contextlib import contextmanager

from sqlalchemy import and_
from sqlalchemy.orm import Session, Query

logger = logging.getLogger(__name__)
T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# CONTEXT UTILISATEUR
# ═══════════════════════════════════════════════════════════


class UserContext:
    """
    Contexte utilisateur pour isolation multi-tenant.
    
    Stocke l'ID utilisateur courant et fournit des helpers
    pour filtrer automatiquement les requêtes.
    """
    
    _current_user_id: str | None = None
    _bypass_isolation: bool = False
    
    @classmethod
    def set_user(cls, user_id: str | None):
        """Définit l'utilisateur courant"""
        cls._current_user_id = user_id
        logger.debug(f"User context set: {user_id}")
    
    @classmethod
    def get_user(cls) -> str | None:
        """Retourne l'ID utilisateur courant"""
        return cls._current_user_id
    
    @classmethod
    def clear(cls):
        """Efface le contexte utilisateur"""
        cls._current_user_id = None
        cls._bypass_isolation = False
    
    @classmethod
    def set_bypass(cls, bypass: bool = True):
        """Active/désactive le bypass d'isolation (admin only)"""
        cls._bypass_isolation = bypass
    
    @classmethod
    def is_bypassed(cls) -> bool:
        """Vérifie si l'isolation est bypassée"""
        return cls._bypass_isolation


@contextmanager
def user_context(user_id: str):
    """
    Context manager pour définir temporairement l'utilisateur.
    
    Example:
        with user_context("user-123"):
            data = service.get_all()  # Filtré automatiquement
    """
    previous_user = UserContext.get_user()
    try:
        UserContext.set_user(user_id)
        yield
    finally:
        UserContext.set_user(previous_user)


@contextmanager
def admin_context():
    """
    Context manager pour accès admin (bypass isolation).
    
    Example:
        with admin_context():
            all_data = service.get_all()  # Toutes les données
    """
    previous_bypass = UserContext.is_bypassed()
    try:
        UserContext.set_bypass(True)
        yield
    finally:
        UserContext.set_bypass(previous_bypass)


# ═══════════════════════════════════════════════════════════
# DÉCORATEURS MULTI-TENANT
# ═══════════════════════════════════════════════════════════


def with_user_isolation(user_id_param: str = "user_id"):
    """
    Décorateur pour ajouter automatiquement le filtrage par user_id.
    
    Args:
        user_id_param: Nom du paramètre user_id dans la fonction
        
    Example:
        @with_user_isolation()
        def get_recettes(db: Session, user_id: str = None):
            return db.query(Recette).all()  # Filtré automatiquement
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Injecter user_id depuis le contexte si non fourni
            if user_id_param not in kwargs or kwargs[user_id_param] is None:
                current_user = UserContext.get_user()
                if current_user and not UserContext.is_bypassed():
                    kwargs[user_id_param] = current_user
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_user():
    """
    Décorateur qui requiert un utilisateur authentifié.
    
    Example:
        @require_user()
        def create_recette(data: dict):
            # user_id automatiquement disponible
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = UserContext.get_user()
            if not user_id and not UserContext.is_bypassed():
                raise PermissionError("Utilisateur non authentifié")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# QUERY HELPERS MULTI-TENANT
# ═══════════════════════════════════════════════════════════


class MultiTenantQuery:
    """
    Helper pour requêtes multi-tenant avec filtrage automatique.
    """
    
    @staticmethod
    def filter_by_user(query: Query, model: type, user_id: str = None) -> Query:
        """
        Ajoute un filtre user_id à une requête.
        
        Args:
            query: Requête SQLAlchemy
            model: Modèle avec attribut user_id
            user_id: ID utilisateur (ou depuis contexte)
            
        Returns:
            Requête filtrée
        """
        if UserContext.is_bypassed():
            return query
        
        user_id = user_id or UserContext.get_user()
        
        if user_id and hasattr(model, 'user_id'):
            return query.filter(model.user_id == user_id)
        
        return query
    
    @staticmethod
    def get_user_filter(model: type, user_id: str = None):
        """
        Retourne une condition de filtre pour user_id.
        
        Example:
            stmt = select(Recette).where(
                MultiTenantQuery.get_user_filter(Recette)
            )
        """
        if UserContext.is_bypassed():
            return True  # Pas de filtre
        
        user_id = user_id or UserContext.get_user()
        
        if user_id and hasattr(model, 'user_id'):
            return model.user_id == user_id
        
        return True


# ═══════════════════════════════════════════════════════════
# SERVICE BASE MULTI-TENANT
# ═══════════════════════════════════════════════════════════


class MultiTenantService:
    """
    Service de base avec support multi-tenant intégré.
    
    Hériter de cette classe pour avoir automatiquement
    le filtrage par user_id sur toutes les opérations.
    """
    
    def __init__(self, model: type):
        self.model = model
        self._has_user_id = hasattr(model, 'user_id')
    
    def _apply_user_filter(self, query: Query) -> Query:
        """Applique le filtre utilisateur si applicable"""
        if not self._has_user_id or UserContext.is_bypassed():
            return query
        
        user_id = UserContext.get_user()
        if user_id:
            return query.filter(self.model.user_id == user_id)
        
        return query
    
    def _inject_user_id(self, data: dict) -> dict:
        """Injecte user_id dans les données si applicable"""
        if not self._has_user_id or UserContext.is_bypassed():
            return data
        
        user_id = UserContext.get_user()
        if user_id and 'user_id' not in data:
            data['user_id'] = user_id
        
        return data
    
    def get_all(self, db: Session, **filters) -> list:
        """Récupère tous les enregistrements (filtrés par user)"""
        query = db.query(self.model)
        query = self._apply_user_filter(query)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return query.all()
    
    def get_by_id(self, db: Session, id: int):
        """Récupère par ID (vérifie appartenance user)"""
        query = db.query(self.model).filter(self.model.id == id)
        query = self._apply_user_filter(query)
        return query.first()
    
    def create(self, db: Session, data: dict):
        """Crée un enregistrement (avec user_id auto)"""
        data = self._inject_user_id(data)
        entity = self.model(**data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    def update(self, db: Session, id: int, data: dict):
        """Met à jour (vérifie appartenance user)"""
        entity = self.get_by_id(db, id)
        if not entity:
            return None
        
        for key, value in data.items():
            if hasattr(entity, key) and key != 'id' and key != 'user_id':
                setattr(entity, key, value)
        
        db.commit()
        db.refresh(entity)
        return entity
    
    def delete(self, db: Session, id: int) -> bool:
        """Supprime (vérifie appartenance user)"""
        entity = self.get_by_id(db, id)
        if not entity:
            return False
        
        db.delete(entity)
        db.commit()
        return True
    
    def count(self, db: Session, **filters) -> int:
        """Compte les enregistrements (filtrés par user)"""
        query = db.query(self.model)
        query = self._apply_user_filter(query)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return query.count()


# ═══════════════════════════════════════════════════════════
# MIDDLEWARE STREAMLIT
# ═══════════════════════════════════════════════════════════


def init_user_context_streamlit():
    """
    Initialise le contexte utilisateur depuis Streamlit session.
    
    À appeler au début de chaque page/module Streamlit.
    
    Example:
        # Dans app.py ou chaque module
        init_user_context_streamlit()
    """
    try:
        import streamlit as st
        
        # Récupérer user_id depuis session
        user_id = st.session_state.get("user_id")
        
        if user_id:
            UserContext.set_user(user_id)
            logger.debug(f"User context initialized: {user_id}")
        else:
            UserContext.clear()
            logger.debug("No user in session, context cleared")
            
    except ImportError:
        logger.warning("Streamlit not available, skipping context init")


def set_user_from_auth(user_data: dict):
    """
    Définit l'utilisateur depuis les données d'authentification.
    
    Args:
        user_data: Dict avec 'id', 'email', etc.
    """
    if user_data and 'id' in user_data:
        UserContext.set_user(str(user_data['id']))
        
        try:
            import streamlit as st
            st.session_state["user_id"] = str(user_data['id'])
            st.session_state["user_email"] = user_data.get('email')
        except ImportError:
            pass


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def create_multi_tenant_service(model: type) -> MultiTenantService:
    """
    Factory pour créer un service multi-tenant.
    
    Example:
        RecetteService = create_multi_tenant_service(Recette)
        service = RecetteService()
        recettes = service.get_all(db)  # Filtrées par user
    """
    return MultiTenantService(model)
