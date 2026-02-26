"""
Fonctions CRUD pour le module Meubles.

Délègue toutes les opérations au service MeublesCrudService.
Ce fichier est conservé pour compatibilité des imports existants.
"""

import logging

logger = logging.getLogger(__name__)


def _get_service():
    """Retourne le service singleton MeublesCrudService."""
    from src.services.maison.meubles_crud_service import get_meubles_crud_service

    return get_meubles_crud_service()


def get_all_meubles(filtre_statut: str | None = None, filtre_piece: str | None = None) -> list:
    """Récupère tous les meubles avec filtres optionnels.

    Args:
        filtre_statut: Filtrer par statut.
        filtre_piece: Filtrer par pièce.

    Returns:
        Liste d'objets Meuble.
    """
    return _get_service().get_all_meubles(filtre_statut=filtre_statut, filtre_piece=filtre_piece)


def get_meuble_by_id(meuble_id: int):
    """Récupère un meuble par son ID."""
    return _get_service().get_meuble_by_id(meuble_id)


def create_meuble(data: dict) -> None:
    """Crée un nouveau meuble."""
    _get_service().create_meuble(data)


def update_meuble(meuble_id: int, data: dict):
    """Met à jour un meuble existant."""
    return _get_service().update_meuble(meuble_id, data)


def delete_meuble(meuble_id: int) -> bool:
    """Supprime un meuble."""
    return _get_service().delete_meuble(meuble_id)


def get_budget_resume() -> dict:
    """Calcule le résumé budget des meubles souhaités.

    Returns:
        Dict avec nb_articles, total_estime, total_max, par_piece.
    """
    return _get_service().get_budget_resume()
