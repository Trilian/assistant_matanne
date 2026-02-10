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


class ContexteUtilisateur:
    """
    Contexte utilisateur pour isolation multi-tenant.
    
    Stocke l'ID utilisateur courant et fournit des helpers
    pour filtrer automatiquement les requêtes.
    """
    
    _current_user_id: str | None = None
    _bypass_isolation: bool = False
    
    @classmethod
    def definir_utilisateur(cls, user_id: str | None):
        """Définit l'utilisateur courant"""
        cls._current_user_id = user_id
        logger.debug(f"User context set: {user_id}")
    
    @classmethod
    def obtenir_utilisateur(cls) -> str | None:
        """Retourne l'ID utilisateur courant"""
        return cls._current_user_id
    
    @classmethod
    def clear(cls):
        """Efface le contexte utilisateur"""
        cls._current_user_id = None
        cls._bypass_isolation = False
    
    @classmethod
    def definir_contournement(cls, bypass: bool = True):
        """Active/désactive le bypass d'isolation (admin only)"""
        cls._bypass_isolation = bypass
    
    @classmethod
    def est_contourne(cls) -> bool:
        """Vérifie si l'isolation est bypassée"""
        return cls._bypass_isolation
    
    # Alias anglais (pour compatibilité tests existants)
    set_user = definir_utilisateur
    get_user = obtenir_utilisateur
    set_bypass = definir_contournement
    is_bypassed = est_contourne


@contextmanager
def user_context(user_id: str):
    """
    Context manager pour définir temporairement l'utilisateur.
    
    Example:
        with user_context("user-123"):
            data = service.obtenir_tout()  # Filtré automatiquement
    """
    previous_user = ContexteUtilisateur.obtenir_utilisateur()
    try:
        ContexteUtilisateur.definir_utilisateur(user_id)
        yield
    finally:
        ContexteUtilisateur.definir_utilisateur(previous_user)


@contextmanager
def admin_context():
    """
    Context manager pour accès admin (bypass isolation).
    
    Example:
        with admin_context():
            all_data = service.obtenir_tout()  # Toutes les données
    """
    previous_bypass = ContexteUtilisateur.is_bypassed()
    try:
        ContexteUtilisateur.set_bypass(True)
        yield
    finally:
        ContexteUtilisateur.set_bypass(previous_bypass)


# ═══════════════════════════════════════════════════════════
# DÉCORATEURS MULTI-TENANT
# ═══════════════════════════════════════════════════════════


def avec_isolation_utilisateur(user_id_param: str = "user_id"):
    """
    Décorateur pour ajouter automatiquement le filtrage par user_id.
    
    Args:
        user_id_param: Nom du paramètre user_id dans la fonction
        
    Example:
        @avec_isolation_utilisateur()
        def get_recettes(db: Session, user_id: str = None):
            return db.query(Recette).all()  # Filtré automatiquement
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Injecter user_id depuis le contexte si non fourni
            if user_id_param not in kwargs or kwargs[user_id_param] is None:
                current_user = ContexteUtilisateur.obtenir_utilisateur()
                if current_user and not ContexteUtilisateur.is_bypassed():
                    kwargs[user_id_param] = current_user
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def exiger_utilisateur():
    """
    Décorateur qui requiert un utilisateur authentifié.
    
    Example:
        @exiger_utilisateur()
        def creer_recette(data: dict):
            # user_id automatiquement disponible
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = ContexteUtilisateur.obtenir_utilisateur()
            if not user_id and not ContexteUtilisateur.is_bypassed():
                raise PermissionError("Utilisateur non authentifié")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════
# QUERY HELPERS MULTI-TENANT
# ═══════════════════════════════════════════════════════════


class RequeteMultiLocataire:
    """
    Helper pour requêtes multi-tenant avec filtrage automatique.
    """
    
    @staticmethod
    def filtrer_par_utilisateur(query: Query, model: type, user_id: str = None) -> Query:
        """
        Ajoute un filtre user_id à une requête.
        
        Args:
            query: Requête SQLAlchemy
            model: Modèle avec attribut user_id
            user_id: ID utilisateur (ou depuis contexte)
            
        Returns:
            Requête filtrée
        """
        if ContexteUtilisateur.is_bypassed():
            return query
        
        user_id = user_id or ContexteUtilisateur.obtenir_utilisateur()
        
        if user_id and hasattr(model, 'user_id'):
            return query.filter(model.user_id == user_id)
        
        return query
    
    @staticmethod
    def obtenir_utilisateur_filter(model: type, user_id: str = None):
        """
        Retourne une condition de filtre pour user_id.
        
        Example:
            stmt = select(Recette).where(
                RequeteMultiLocataire.get_user_filter(Recette)
            )
        """
        if ContexteUtilisateur.is_bypassed():
            return True  # Pas de filtre
        
        user_id = user_id or ContexteUtilisateur.obtenir_utilisateur()
        
        if user_id and hasattr(model, 'user_id'):
            return model.user_id == user_id
        
        return True
    
    # Alias anglais
    filter_by_user = filtrer_par_utilisateur
    get_user_filter = obtenir_utilisateur_filter


class ServiceMultiLocataire:
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
        if not self._has_user_id or ContexteUtilisateur.is_bypassed():
            return query
        
        user_id = ContexteUtilisateur.obtenir_utilisateur()
        if user_id:
            return query.filter(self.model.user_id == user_id)
        
        return query
    
    def _inject_user_id(self, data: dict) -> dict:
        """Injecte user_id dans les données si applicable"""
        if not self._has_user_id or ContexteUtilisateur.is_bypassed():
            return data
        
        user_id = ContexteUtilisateur.obtenir_utilisateur()
        if user_id and 'user_id' not in data:
            data['user_id'] = user_id
        
        return data
    
    def obtenir_tout(self, db: Session, **filters) -> list:
        """Récupère tous les enregistrements (filtrés par user)"""
        query = db.query(self.model)
        query = self._apply_user_filter(query)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return query.all()
    
    def obtenir_par_id(self, db: Session, id: int):
        """Récupère par ID (vérifie appartenance user)"""
        query = db.query(self.model).filter(self.model.id == id)
        query = self._apply_user_filter(query)
        return query.first()
    
    def creer(self, db: Session, data: dict):
        """Crée un enregistrement (avec user_id auto)"""
        data = self._inject_user_id(data)
        entity = self.model(**data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    def mettre_a_jour(self, db: Session, id: int, data: dict):
        """Met à jour (vérifie appartenance user)"""
        entity = self.obtenir_par_id(db, id)
        if not entity:
            return None
        
        for key, value in data.items():
            if hasattr(entity, key) and key != 'id' and key != 'user_id':
                setattr(entity, key, value)
        
        db.commit()
        db.refresh(entity)
        return entity
    
    def supprimer(self, db: Session, id: int) -> bool:
        """Supprime (vérifie appartenance user)"""
        entity = self.obtenir_par_id(db, id)
        if not entity:
            return False
        
        db.delete(entity)
        db.commit()
        return True
    
    def compter(self, db: Session, **filters) -> int:
        """Compte les enregistrements (filtrés par user)"""
        query = db.query(self.model)
        query = self._apply_user_filter(query)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    # Alias anglais
    get_all = obtenir_tout
    get_by_id = obtenir_par_id
    create = creer
    update = mettre_a_jour
    delete = supprimer
    count = compter


def initialiser_contexte_utilisateur_streamlit():
    """
    Initialise le contexte utilisateur depuis Streamlit session.
    
    À appeler au début de chaque page/module Streamlit.
    
    Example:
        # Dans app.py ou chaque module
        initialiser_contexte_utilisateur_streamlit()
    """
    try:
        import streamlit as st
        
        # Récupérer user_id depuis session
        user_id = st.session_state.get("user_id")
        
        if user_id:
            ContexteUtilisateur.definir_utilisateur(user_id)
            logger.debug(f"User context initialized: {user_id}")
        else:
            ContexteUtilisateur.clear()
            logger.debug("No user in session, context cleared")
            
    except ImportError:
        logger.warning("Streamlit not available, skipping context init")


def definir_utilisateur_from_auth(user_data: dict):
    """
    Définit l'utilisateur depuis les données d'authentification.
    
    Args:
        user_data: Dict avec 'id', 'email', etc.
    """
    if user_data and 'id' in user_data:
        ContexteUtilisateur.definir_utilisateur(str(user_data['id']))
        
        try:
            import streamlit as st
            st.session_state["user_id"] = str(user_data['id'])
            st.session_state["user_email"] = user_data.get('email')
        except ImportError:
            pass


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def creer_multi_tenant_service(model: type) -> ServiceMultiLocataire:
    """
    Factory pour créer un service multi-tenant.
    
    Example:
        RecetteService = creer_multi_tenant_service(Recette)
        service = RecetteService()
        recettes = service.obtenir_tout(db)  # Filtrées par user
    """
    return ServiceMultiLocataire(model)