"""
Module Paramètres - Configuration Application
Point d'entrée avec navigation par onglets
"""

import streamlit as st


def app():
    """Point d'entree module paramètres"""

    # Imports différés — chaque sous-module n'est chargé que quand son onglet est affiché
    from src.modules.parametres.about import afficher_about
    from src.modules.parametres.affichage import afficher_display_config
    from src.modules.parametres.budget import afficher_budget_config
    from src.modules.parametres.cache import afficher_cache_config
    from src.modules.parametres.database import afficher_database_config
    from src.modules.parametres.foyer import afficher_foyer_config
    from src.modules.parametres.ia import afficher_ia_config
    from src.ui.views.sauvegarde import afficher_sauvegarde

    st.title("⚙️ Paramètres")

    # Navigation par onglets
    tabs = st.tabs(
        [
            "👨‍👩‍👧‍👦 Foyer",
            "🤖 IA",
            "🗄️ BD",
            "💾 Cache",
            "� Sauvegarde",
            "🖥️ Affichage",
            "💰 Budget",
            "ℹ️ À Propos",
        ]
    )

    with tabs[0]:
        afficher_foyer_config()
    with tabs[1]:
        afficher_ia_config()
    with tabs[2]:
        afficher_database_config()
    with tabs[3]:
        afficher_cache_config()
    with tabs[4]:
        afficher_sauvegarde()
    with tabs[5]:
        afficher_display_config()
    with tabs[6]:
        afficher_budget_config()
    with tabs[7]:
        afficher_about()


__all__ = ["app"]
