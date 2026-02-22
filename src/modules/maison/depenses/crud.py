"""
Module Depenses Maison - Fonctions CRUD et statistiques

Délègue au service DepensesCrudService pour tous les accès DB.
"""

from typing import List, Optional

from src.services.maison import get_depenses_crud_service


def _service():
    return get_depenses_crud_service()


def get_depenses_mois(mois: int, annee: int) -> list:
    """Recupère les depenses d'un mois"""
    return _service().get_depenses_mois(mois, annee)


def get_depenses_annee(annee: int) -> list:
    """Recupère toutes les depenses d'une annee"""
    return _service().get_depenses_annee(annee)


def get_depense_by_id(depense_id: int) -> object | None:
    """Recupère une depense par ID"""
    return _service().get_depense_by_id(depense_id)


def create_depense(data: dict):
    """Cree une nouvelle depense"""
    return _service().create_depense(data)


def update_depense(depense_id: int, data: dict):
    """Met a jour une depense"""
    return _service().update_depense(depense_id, data)


def delete_depense(depense_id: int) -> bool:
    """Supprime une depense"""
    return _service().delete_depense(depense_id)


def get_stats_globales() -> dict:
    """Calcule les statistiques globales"""
    return _service().get_stats_globales()


def get_historique_categorie(categorie: str, nb_mois: int = 12) -> list[dict]:
    """Recupère l'historique d'une categorie"""
    return _service().get_historique_categorie(categorie, nb_mois)
