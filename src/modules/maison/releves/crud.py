"""CRUD delegation pour Relevés Compteurs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.services.maison.extensions_crud_service import get_releves_service

if TYPE_CHECKING:
    from src.core.models.maison_extensions import ReleveCompteur


def get_all_releves(type_compteur: str | None = None) -> list[ReleveCompteur]:
    """Récupère tous les relevés, optionnellement filtrés par type."""
    service = get_releves_service()
    return service.get_all_releves(type_compteur=type_compteur)


def create_releve(data: dict) -> ReleveCompteur:
    """Crée un nouveau relevé."""
    service = get_releves_service()
    return service.create_releve(data)


def get_stats_releves(type_compteur: str) -> dict:
    """Récupère les statistiques pour un type de compteur."""
    service = get_releves_service()
    return service.get_stats_releves(type_compteur)
