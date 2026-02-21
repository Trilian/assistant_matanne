"""
State Package — Gestion unifiée de l'état applicatif.

Architecture "State Slices":
- EtatNavigation : Module actuel, historique, fil d'Ariane
- EtatCuisine    : Recettes, inventaire, planning repas
- EtatUI         : Flags formulaires, onglets, modales
- EtatApp        : Agrège tous les slices (rétro-compatibilité)

Usage::
    from src.core.state import obtenir_etat, naviguer, GestionnaireEtat

    # Raccourci simple
    etat = obtenir_etat()
    print(etat.module_actuel)

    # Navigation
    naviguer("cuisine.recettes")

    # Gestionnaire complet
    GestionnaireEtat.definir_recette_visualisation(42)
"""

from __future__ import annotations

# Gestionnaire
from .manager import GestionnaireEtat

# Raccourcis
from .shortcuts import (
    est_mode_debug,
    naviguer,
    nettoyer_etats_ui,
    obtenir_etat,
    obtenir_fil_ariane,
    revenir,
)

# Slices
from .slices import EtatApp, EtatCuisine, EtatNavigation, EtatUI

__all__ = [
    # Slices
    "EtatNavigation",
    "EtatCuisine",
    "EtatUI",
    "EtatApp",
    # Gestionnaire
    "GestionnaireEtat",
    # Raccourcis
    "obtenir_etat",
    "naviguer",
    "revenir",
    "obtenir_fil_ariane",
    "est_mode_debug",
    "nettoyer_etats_ui",
]
