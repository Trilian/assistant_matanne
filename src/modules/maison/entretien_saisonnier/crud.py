"""CRUD delegation pour Entretien Saisonnier."""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.services.maison.extensions_crud_service import get_entretien_saisonnier_service

if TYPE_CHECKING:
    from src.core.models.maison_extensions import EntretienSaisonnier


def get_all_entretiens(saison: str | None = None) -> list[EntretienSaisonnier]:
    """Récupère les entretiens, optionnellement filtrés par saison."""
    service = get_entretien_saisonnier_service()
    return service.get_all_entretiens(saison=saison)


def marquer_fait(entretien_id: int) -> EntretienSaisonnier | None:
    """Marque un entretien comme réalisé aujourd'hui."""
    service = get_entretien_saisonnier_service()
    return service.marquer_fait(entretien_id)


def get_alertes_saisonnieres() -> list[EntretienSaisonnier]:
    """Récupère les entretiens à faire pour la saison en cours."""
    service = get_entretien_saisonnier_service()
    return service.get_alertes_saisonnieres()
