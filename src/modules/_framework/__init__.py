"""
Module Framework - Architecture moderne pour modules Streamlit.

Ce package fournit une architecture robuste et réutilisable pour les modules:
- Error Boundary: Gestion d'erreurs unifiée avec fallback UI
- BaseModule: Classe de base avec lifecycle et injection de dépendances
- Fragments: Composants auto-refresh avec isolation
- State Manager: Gestion centralisée du session_state via ModuleState

Usage:
    from src.modules._framework import (
        BaseModule,
        module_app,
        error_boundary,
        ModuleState,
        init_module_state,
    )

    @module_app
    class MonModule(BaseModule[MonService]):
        titre = "Mon Module"
        icone = "📦"

        def get_service_factory(self):
            return obtenir_mon_service

        def render(self):
            state = ModuleState("mon_module")
            data = self.service.get_data()
            self._render_data(data)

Architecture:
- Error Boundaries pour UX gracieuse
- ModuleState pour état local avec préfixes
- Fragments pour refresh partiel
- Convention over Configuration
"""

from src.modules._framework.base_module import (
    BaseModule,
    create_simple_module,
    module_app,
)
from src.modules._framework.error_boundary import (
    ErrorBoundaryContext,
    avec_gestion_erreurs_ui,
    error_boundary,
    safe_call,
    try_render,
)
from src.modules._framework.fragments import (
    auto_refresh_fragment,
    conditional_render,
    debounced_callback,
    isolated_fragment,
    lazy_fragment,
    with_loading_state,
)
from src.modules._framework.state_manager import (
    ModuleState,
    clear_all_module_states,
    get_all_module_states,
    init_module_state,
    reset_module_state,
)

__all__ = [
    # Error Boundary
    "error_boundary",
    "ErrorBoundaryContext",
    "avec_gestion_erreurs_ui",
    "safe_call",
    "try_render",
    # State Manager
    "ModuleState",
    "init_module_state",
    "reset_module_state",
    "get_all_module_states",
    "clear_all_module_states",
    # Base Module
    "BaseModule",
    "module_app",
    "create_simple_module",
    # Fragments
    "auto_refresh_fragment",
    "isolated_fragment",
    "lazy_fragment",
    "with_loading_state",
    "conditional_render",
    "debounced_callback",
]
