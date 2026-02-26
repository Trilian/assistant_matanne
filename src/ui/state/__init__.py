"""
Gestion d'état avancée pour Streamlit.

Modules:
- url: Synchronisation avec st.query_params (deep linking)
"""

from src.ui.state.url import (
    DeepLinkState,
    URLState,
    clear_url_param,
    get_url_param,
    pagination_with_url,
    selectbox_with_url,
    set_url_param,
    sync_to_url,
    tabs_with_url,
    text_input_with_url,
    url_state,
)

__all__ = [
    # Classes
    "URLState",
    "DeepLinkState",
    # Décorateurs
    "url_state",
    # Helpers
    "sync_to_url",
    "get_url_param",
    "set_url_param",
    "clear_url_param",
    # Widgets synchronisés
    "tabs_with_url",
    "selectbox_with_url",
    "pagination_with_url",
    "text_input_with_url",
]
