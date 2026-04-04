"""Compatibilité legacy pour le bridge Charges → Énergie."""

from src.services.maison.bridges_charges_energie import (
    ChargesEnergieInteractionService,
    obtenir_service_charges_energie_interaction,
)

__all__ = [
    "ChargesEnergieInteractionService",
    "obtenir_service_charges_energie_interaction",
]
