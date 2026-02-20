"""Entretien - Onglets principaux (re-exports)."""

from .onglets_analytics import onglet_graphiques, onglet_historique, onglet_stats
from .onglets_core import onglet_inventaire, onglet_pieces, onglet_taches
from .onglets_export import onglet_export

__all__ = [
    "onglet_taches",
    "onglet_inventaire",
    "onglet_pieces",
    "onglet_historique",
    "onglet_stats",
    "onglet_graphiques",
    "onglet_export",
]
