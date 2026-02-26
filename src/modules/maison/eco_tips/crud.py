"""
Fonctions CRUD pour les actions écologiques.

Délègue toutes les opérations au service EcoTipsCrudService.
Ce fichier est conservé pour compatibilité des imports existants.
"""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    """Retourne le service singleton EcoTipsCrudService."""
    from src.services.maison.eco_tips_crud_service import get_eco_tips_crud_service

    return get_eco_tips_crud_service()


def get_all_actions(actif_only: bool = False) -> list:
    """Récupère toutes les actions écologiques.

    Args:
        actif_only: Ne retourner que les actions actives.

    Returns:
        Liste d'objets ActionEcologique.
    """
    return _get_service().get_all_actions(actif_only=actif_only)


def get_action_by_id(action_id: int):
    """Récupère une action par son ID.

    Args:
        action_id: ID de l'action.

    Returns:
        Objet ActionEcologique ou None.
    """
    return _get_service().get_action_by_id(action_id)


def create_action(data: dict) -> None:
    """Crée une nouvelle action écologique.

    Args:
        data: Dict avec les champs de l'action.
    """
    _get_service().create_action(data)


def update_action(action_id: int, data: dict):
    """Met à jour une action existante.

    Args:
        action_id: ID de l'action.
        data: Dict des champs à mettre à jour.

    Returns:
        Objet ActionEcologique mis à jour ou None si non trouvé.
    """
    return _get_service().update_action(action_id, data)


def delete_action(action_id: int) -> bool:
    """Supprime une action écologique.

    Args:
        action_id: ID de l'action.

    Returns:
        True si supprimée, False si non trouvée.
    """
    return _get_service().delete_action(action_id)
