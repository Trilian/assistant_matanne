"""
State Package — Gestion unifiée de l'état applicatif.

Architecture "State Slices":
- EtatNavigation : Module actuel, historique, fil d'Ariane
- EtatCuisine    : Recettes, inventaire, planning repas
- EtatUI         : Flags formulaires, onglets, modales
- EtatApp        : Agrège tous les slices (rétro-compatibilité)

Architecture "PersistentState":
- Synchronisation automatique session_state ↔ DB
- Décorateur @persistent_state pour factories persistantes

Usage::
    from src.core.state import obtenir_etat, naviguer, GestionnaireEtat

    # Raccourci simple
    etat = obtenir_etat()
    print(etat.module_actuel)

    # Navigation
    naviguer("cuisine.recettes")

    # Gestionnaire complet
    GestionnaireEtat.definir_recette_visualisation(42)

    # État persistant (sync DB)
    from src.core.state import PersistentState, persistent_state

    pstate = PersistentState("foyer_config")
    pstate["nb_adultes"] = 2
    pstate.commit()
"""

from __future__ import annotations

# Gestionnaire
from .manager import GestionnaireEtat

# Persistent State (sync DB)
from .persistent import (
    PersistentState,
    PersistentStateConfig,
    forcer_sync_tous,
    obtenir_etat_persistant,
    persistent_state,
)

# Raccourcis
from .shortcuts import (
    est_mode_debug,
    naviguer,
    nettoyer_etats_ui,
    obtenir_etat,
    obtenir_fil_ariane,
    rerun,
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
    "rerun",
    "revenir",
    "obtenir_fil_ariane",
    "est_mode_debug",
    "nettoyer_etats_ui",
    # Persistent State
    "PersistentState",
    "PersistentStateConfig",
    "persistent_state",
    "obtenir_etat_persistant",
    "forcer_sync_tous",
]
