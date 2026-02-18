"""
Configuration du mode tablette.

Gestion de l'état et configuration des modes d'affichage.
"""

from enum import StrEnum

import streamlit as st


class TabletMode(StrEnum):
    """Modes d'affichage tablette."""

    NORMAL = "normal"
    TABLET = "tablet"
    KITCHEN = "kitchen"  # Mode cuisine (très gros, tactile)


def get_tablet_mode() -> TabletMode:
    """Retourne le mode tablette actuel."""
    mode = st.session_state.get("tablet_mode", TabletMode.NORMAL)
    return TabletMode(mode) if isinstance(mode, str) else mode


def set_tablet_mode(mode: TabletMode):
    """Définit le mode tablette."""
    st.session_state["tablet_mode"] = mode
