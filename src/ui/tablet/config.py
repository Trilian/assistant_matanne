"""
Configuration du mode tablette.

Gestion de l'état et configuration des modes d'affichage.
"""

from enum import StrEnum

import streamlit as st


class ModeTablette(StrEnum):
    """Modes d'affichage tablette."""

    NORMAL = "normal"
    TABLETTE = "tablette"
    CUISINE = "cuisine"  # Mode cuisine (très gros, tactile)


def obtenir_mode_tablette() -> ModeTablette:
    """Retourne le mode tablette actuel."""
    mode = st.session_state.get("mode_tablette", ModeTablette.NORMAL)
    return ModeTablette(mode) if isinstance(mode, str) else mode


def definir_mode_tablette(mode: ModeTablette):
    """Définit le mode tablette."""
    st.session_state["mode_tablette"] = mode
