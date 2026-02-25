"""
Fonctions CRUD pour les actions écologiques.
"""

import logging

from src.core.db import obtenir_contexte_db

logger = logging.getLogger(__name__)


def _get_action_model():
    """Retourne le modèle ActionEcologique (import différé)."""
    try:
        from src.core.models import ActionEcologique

        return ActionEcologique
    except ImportError:
        return type("ActionEcologique", (), {"__tablename__": "actions_ecologiques"})


def get_all_actions(actif_only: bool = False) -> list:
    """Récupère toutes les actions écologiques.

    Args:
        actif_only: Ne retourner que les actions actives.

    Returns:
        Liste d'objets ActionEcologique.
    """
    ActionEcologique = _get_action_model()

    with obtenir_contexte_db() as db:
        query = db.query(ActionEcologique)
        if actif_only:
            query = query.filter(ActionEcologique.actif == True)  # noqa: E712
        return query.order_by(ActionEcologique.id).all()


def get_action_by_id(action_id: int):
    """Récupère une action par son ID.

    Args:
        action_id: ID de l'action.

    Returns:
        Objet ActionEcologique ou None.
    """
    ActionEcologique = _get_action_model()

    with obtenir_contexte_db() as db:
        return db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()


def create_action(data: dict) -> None:
    """Crée une nouvelle action écologique.

    Args:
        data: Dict avec les champs de l'action.
    """
    ActionEcologique = _get_action_model()

    with obtenir_contexte_db() as db:
        action = ActionEcologique(**data)
        db.add(action)
        db.commit()
        db.refresh(action)


def update_action(action_id: int, data: dict):
    """Met à jour une action existante.

    Args:
        action_id: ID de l'action.
        data: Dict des champs à mettre à jour.

    Returns:
        Objet ActionEcologique mis à jour ou None si non trouvé.
    """
    ActionEcologique = _get_action_model()

    with obtenir_contexte_db() as db:
        action = db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()
        if action is None:
            return None
        for key, value in data.items():
            setattr(action, key, value)
        db.commit()
        db.refresh(action)
        return action


def delete_action(action_id: int) -> bool:
    """Supprime une action écologique.

    Args:
        action_id: ID de l'action.

    Returns:
        True si supprimée, False si non trouvée.
    """
    ActionEcologique = _get_action_model()

    with obtenir_contexte_db() as db:
        action = db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()
        if action is None:
            return False
        db.delete(action)
        db.commit()
        return True
