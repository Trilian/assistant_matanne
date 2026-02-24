"""
Module Paramètres - Configuration Application
Point d'entrée avec navigation par onglets
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.state.url import tabs_with_url


@profiler_rerun("parametres")
def app():
    """Point d'entree module paramètres"""

    from src.modules.parametres.about import afficher_about
    from src.modules.parametres.affichage import afficher_display_config
    from src.modules.parametres.budget import afficher_budget_config
    from src.modules.parametres.cache import afficher_cache_config
    from src.modules.parametres.database import afficher_database_config
    from src.modules.parametres.foyer import afficher_foyer_config
    from src.modules.parametres.ia import afficher_ia_config
    from src.ui.views.sauvegarde import afficher_sauvegarde

    st.title("⚙️ Paramètres")

    # Navigation par onglets avec deep linking
    TAB_LABELS = [
        "👨‍👩‍👧‍👦 Foyer",
        "🤖 IA",
        "🗄️ BD",
        "💾 Cache",
        "💿 Sauvegarde",
        "🖥️ Affichage",
        "💰 Budget",
        "ℹ️ À Propos",
    ]
    tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    with tabs[0]:
        with error_boundary(titre="Erreur config foyer"):
            afficher_foyer_config()
    with tabs[1]:
        with error_boundary(titre="Erreur config IA"):
            afficher_ia_config()
    with tabs[2]:
        with error_boundary(titre="Erreur config BD"):
            afficher_database_config()
    with tabs[3]:
        with error_boundary(titre="Erreur config cache"):
            afficher_cache_config()
    with tabs[4]:
        with error_boundary(titre="Erreur sauvegarde"):
            afficher_sauvegarde()
    with tabs[5]:
        with error_boundary(titre="Erreur config affichage"):
            afficher_display_config()
    with tabs[6]:
        with error_boundary(titre="Erreur config budget"):
            afficher_budget_config()
    with tabs[7]:
        with error_boundary(titre="Erreur à propos"):
            afficher_about()


__all__ = [
    "app",
    "afficher_about",
    "afficher_budget_config",
    "afficher_cache_config",
    "afficher_database_config",
    "afficher_display_config",
    "afficher_foyer_config",
    "afficher_ia_config",
]

# ═══════════════════════════════════════════════════════════
# LAZY LOADING pour imports directs (tests, etc.)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, str] = {
    "afficher_about": "about",
    "afficher_budget_config": "budget",
    "afficher_cache_config": "cache",
    "afficher_database_config": "database",
    "afficher_display_config": "affichage",
    "afficher_foyer_config": "foyer",
    "afficher_ia_config": "ia",
}


def __getattr__(name: str):
    """Lazy loading des fonctions de configuration."""
    if name in _LAZY_IMPORTS:
        from importlib import import_module

        mod = import_module(f"src.modules.parametres.{_LAZY_IMPORTS[name]}")
        return getattr(mod, name)
    raise AttributeError(f"module 'src.modules.parametres' has no attribute '{name}'")
