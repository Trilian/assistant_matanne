"""Jardin - Onglets principaux (facade).

Re-exporte les fonctions d'onglets depuis les sous-modules spécialisés.
Refactoré en Phase 4 Audit (item 18 — split fichier >500 LOC).

Sous-modules:
  - onglets_culture: mes_plantes, récoltes, plan
  - onglets_stats: tâches, autonomie, graphiques
  - onglets_export: export CSV
"""

from .onglets_culture import onglet_mes_plantes, onglet_plan, onglet_recoltes
from .onglets_export import onglet_export
from .onglets_stats import onglet_autonomie, onglet_graphiques, onglet_taches

__all__ = [
    "onglet_autonomie",
    "onglet_export",
    "onglet_graphiques",
    "onglet_mes_plantes",
    "onglet_plan",
    "onglet_recoltes",
    "onglet_taches",
]
