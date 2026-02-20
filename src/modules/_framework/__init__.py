"""
Module Framework - Architecture moderne pour modules Streamlit.

Ce package fournit une architecture robuste et réutilisable pour les modules:
- Error Boundary: Gestion d'erreurs unifiée avec fallback UI
- Hooks: Pattern React-like pour état et services (use_state, use_service, use_query)
- BaseModule: Classe de base avec lifecycle et injection de dépendances
- Fragments: Composants auto-refresh avec isolation
- State Manager: Gestion centralisée du session_state

Usage:
    from src.modules._framework import (
        BaseModule,
        module_app,
        error_boundary,
        use_state,
        use_service,
        use_query,
    )

    @module_app
    class MonModule(BaseModule[MonService]):
        titre = "Mon Module"
        icone = "📦"

        def get_service_factory(self):
            return obtenir_mon_service

        def render(self):
            result = use_query(self.service.get_data, "data_key")
            if result.is_success:
                self._render_data(result.data)

Architecture inspirée de React avec adaptations pour Streamlit:
- Error Boundaries pour UX gracieuse
- Hooks pour état local et requêtes
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
from src.modules._framework.hooks import (
    QueryResult,
    StateHook,
    use_callback,
    use_effect,
    use_memo,
    use_previous,
    use_query,
    use_service,
    use_state,
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
    # Hooks
    "use_state",
    "use_service",
    "use_query",
    "use_memo",
    "use_effect",
    "use_callback",
    "use_previous",
    "StateHook",
    "QueryResult",
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
