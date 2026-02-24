"""
Module Paramètres - Configuration Application
Navigation par onglets via BaseModule (Phase 4 Audit, item 16).
"""

from __future__ import annotations

from typing import Callable

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import BaseModule, module_app


class ParametresModule(BaseModule[None]):
    """Module Paramètres — piloté avec BaseModule (Phase 4 Audit)."""

    titre = "Paramètres"
    icone = "⚙️"
    description = ""
    show_refresh_button = False

    def get_service_factory(self) -> Callable[[], None] | None:
        return None

    @profiler_rerun("parametres")
    def render(self) -> None:
        """Rendu principal avec onglets gérés par render_tabs."""
        from src.modules.parametres.about import afficher_about
        from src.modules.parametres.affichage import afficher_display_config
        from src.modules.parametres.budget import afficher_budget_config
        from src.modules.parametres.cache import afficher_cache_config
        from src.modules.parametres.database import afficher_database_config
        from src.modules.parametres.foyer import afficher_foyer_config
        from src.modules.parametres.ia import afficher_ia_config
        from src.ui.views.sauvegarde import afficher_sauvegarde

        self.render_tabs(
            {
                "👨‍👩‍👧‍👦 Foyer": afficher_foyer_config,
                "🤖 IA": afficher_ia_config,
                "🗄️ BD": afficher_database_config,
                "💾 Cache": afficher_cache_config,
                "💿 Sauvegarde": afficher_sauvegarde,
                "🖥️ Affichage": afficher_display_config,
                "💰 Budget": afficher_budget_config,
                "ℹ️ À Propos": afficher_about,
            }
        )


# Point d'entrée standard généré par module_app
app = module_app(ParametresModule)


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
