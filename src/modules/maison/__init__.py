"""Module Maison - Gestion intégrée de l'habitat.

Sous-modules disponibles:
- hub: Hub central intelligent avec briefing IA
- jardin: Potager intelligent avec tâches auto-générées
- entretien: Entretien maison avec inventaire équipements
- charges: Suivi énergie et charges fixes
- depenses: Suivi dépenses maison
"""

from . import (
    charges,
    depenses,
    entretien,
    hub,
    jardin,
)

__all__ = [
    "charges",
    "depenses",
    "entretien",
    "hub",
    "jardin",
]
