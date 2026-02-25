"""
Module Framework - Architecture pour modules Streamlit.

Ce package fournit des utilitaires réutilisables pour les modules:
- Error Boundary: Gestion d'erreurs unifiée avec fallback UI
- BaseModule: Classe de base avec lifecycle et tabs (gelé, 2 modules)
- ModuleState: État préfixé pour éviter collisions (gelé, 3 modules)
- Fragments: Composants auto-refresh avec isolation

Note architecturale (Audit §9.3):
    BaseModule et ModuleState sont **gelés** — utilisés uniquement par
    ParametresModule, DesignSystemModule, et inventaire.
    Le pattern ``def app()`` direct est préféré pour les nouveaux modules.

Usage:
    from src.modules._framework import error_boundary, safe_call

    # Pour les rares modules complexes:
    from src.modules._framework import BaseModule, ModuleState, module_app
"""

from src.modules._framework.base_module import (
    BaseModule,
    ModuleState,
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

__all__ = [
    # Error Boundary
    "error_boundary",
    "ErrorBoundaryContext",
    "avec_gestion_erreurs_ui",
    "safe_call",
    "try_render",
    # Base Module
    "BaseModule",
    "module_app",
    "create_simple_module",
    # State Manager (gelé - utilisé uniquement par BaseModule et inventaire)
    "ModuleState",
    # Fragments
    "auto_refresh_fragment",
    "isolated_fragment",
    "lazy_fragment",
    "with_loading_state",
    "conditional_render",
    "debounced_callback",
]
