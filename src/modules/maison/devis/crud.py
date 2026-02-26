"""CRUD delegation pour Devis Comparatifs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.services.maison.extensions_crud_service import get_devis_service

if TYPE_CHECKING:
    from src.core.models.maison_extensions import DevisComparatif


def get_all_devis(projet_id: int | None = None) -> list[DevisComparatif]:
    """Récupère tous les devis, optionnellement filtrés par projet."""
    service = get_devis_service()
    return service.get_all_devis(projet_id=projet_id)


def get_devis_by_id(devis_id: int) -> DevisComparatif | None:
    """Récupère un devis par son ID."""
    service = get_devis_service()
    return service.get_devis_by_id(devis_id)


def create_devis(data: dict) -> DevisComparatif:
    """Crée un nouveau devis."""
    service = get_devis_service()
    return service.create_devis(data)


def update_devis(devis_id: int, data: dict) -> DevisComparatif | None:
    """Met à jour un devis."""
    service = get_devis_service()
    return service.update_devis(devis_id, data)


def delete_devis(devis_id: int) -> bool:
    """Supprime un devis."""
    service = get_devis_service()
    return service.delete_devis(devis_id)


def choisir_devis(devis_id: int) -> DevisComparatif | None:
    """Marque un devis comme accepté et refuse les concurrents."""
    service = get_devis_service()
    return service.choisir_devis(devis_id)
