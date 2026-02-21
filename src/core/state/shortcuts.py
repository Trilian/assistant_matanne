"""
Raccourcis d'état — Fonctions helper simplifiées.

Usage::
    from src.core.state import obtenir_etat, naviguer, revenir

    etat = obtenir_etat()
    naviguer("cuisine.recettes")
    revenir()
"""

from __future__ import annotations

from .manager import GestionnaireEtat
from .slices import EtatApp


def obtenir_etat() -> EtatApp:
    """Raccourci pour récupérer le state"""
    return GestionnaireEtat.obtenir()


def naviguer(module: str):
    """Raccourci pour naviguer"""
    GestionnaireEtat.naviguer_vers(module)
    from src.core.storage import obtenir_rerun_callback

    obtenir_rerun_callback()()


def revenir():
    """Raccourci pour revenir en arrière"""
    GestionnaireEtat.revenir()
    from src.core.storage import obtenir_rerun_callback

    obtenir_rerun_callback()()


def obtenir_fil_ariane() -> list[str]:
    """Raccourci pour fil d'Ariane"""
    return GestionnaireEtat.obtenir_fil_ariane_navigation()


def est_mode_debug() -> bool:
    """Raccourci pour vérifier mode debug"""
    etat = obtenir_etat()
    return etat.mode_debug


def nettoyer_etats_ui():
    """Raccourci pour nettoyer états UI"""
    GestionnaireEtat.nettoyer_etats_ui()


__all__ = [
    "obtenir_etat",
    "naviguer",
    "revenir",
    "obtenir_fil_ariane",
    "est_mode_debug",
    "nettoyer_etats_ui",
]
