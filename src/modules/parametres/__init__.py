"""
Module Paramètres - Configuration Application
Point d'entrée avec navigation par onglets
"""

import streamlit as st

from src.modules.parametres.about import render_about
from src.modules.parametres.affichage import render_display_config
from src.modules.parametres.budget import render_budget_config
from src.modules.parametres.cache import render_cache_config
from src.modules.parametres.database import render_database_config
from src.modules.parametres.foyer import render_foyer_config
from src.modules.parametres.ia import render_ia_config


def app():
    """Point d'entree module paramètres"""

    st.title("⚙️ Paramètres")

    # Navigation par onglets
    tabs = st.tabs(
        [
            "👨‍👩‍👧‍👦 Foyer",
            "🤖 IA",
            "🗄️ BD",
            "💾 Cache",
            "🖥️ Affichage",
            "💰 Budget",
            "ℹ️ À Propos",
        ]
    )

    with tabs[0]:
        render_foyer_config()
    with tabs[1]:
        render_ia_config()
    with tabs[2]:
        render_database_config()
    with tabs[3]:
        render_cache_config()
    with tabs[4]:
        render_display_config()
    with tabs[5]:
        render_budget_config()
    with tabs[6]:
        render_about()


__all__ = ["app"]
