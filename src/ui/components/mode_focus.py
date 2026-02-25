"""
Mode Focus/Zen - Interface concentrée.

Permet de masquer la sidebar et le header pour se concentrer
sur une recette ou un planning. Toggle via st.query_params.

Usage:
    from src.ui.components import mode_focus_toggle, is_mode_focus

    if not is_mode_focus():
        afficher_header()

    mode_focus_toggle()  # Bouton toggle
"""

import logging

import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui
from src.ui.state.url import get_url_param, set_url_param

logger = logging.getLogger(__name__)

_keys = KeyNamespace("mode_focus")

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

URL_PARAM_FOCUS = "focus"
SESSION_KEY_FOCUS = "_mode_focus_active"


# ═══════════════════════════════════════════════════════════
# ÉTAT DU MODE FOCUS
# ═══════════════════════════════════════════════════════════


def is_mode_focus() -> bool:
    """
    Vérifie si le mode focus est actif.

    Le mode focus peut être activé via:
    - URL param ?focus=1
    - Session state (toggle UI)

    Returns:
        True si mode focus actif
    """
    # Vérifier URL param
    url_focus = get_url_param(URL_PARAM_FOCUS)
    if url_focus in ("1", "true", True):
        return True

    # Vérifier session state
    return st.session_state.get(SESSION_KEY_FOCUS, False)


def activer_mode_focus() -> None:
    """Active le mode focus."""
    st.session_state[SESSION_KEY_FOCUS] = True
    set_url_param(URL_PARAM_FOCUS, "1")


def desactiver_mode_focus() -> None:
    """Désactive le mode focus."""
    st.session_state[SESSION_KEY_FOCUS] = False
    from src.ui.state.url import clear_url_param

    clear_url_param(URL_PARAM_FOCUS)


def toggle_mode_focus() -> bool:
    """
    Bascule le mode focus.

    Returns:
        Nouvel état du mode focus
    """
    if is_mode_focus():
        desactiver_mode_focus()
        return False
    else:
        activer_mode_focus()
        return True


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


@composant_ui("focus", tags=("ui", "toggle", "focus"))
def mode_focus_toggle(position: str = "top-right") -> None:
    """
    Affiche le bouton toggle du mode focus.

    Args:
        position: Position du bouton ("top-right", "bottom-right", "inline")
    """
    actif = is_mode_focus()
    icone = "🔲" if actif else "⬜"
    label = "Quitter Focus" if actif else "Mode Focus"
    tooltip = "Masquer la navigation pour se concentrer" if not actif else "Afficher la navigation"

    # CSS pour positionnement absolu
    if position in ("top-right", "bottom-right"):
        pos_css = "top: 70px;" if position == "top-right" else "bottom: 20px;"
        st.markdown(
            f"""
            <style>
            .focus-toggle-container {{
                position: fixed;
                right: 20px;
                {pos_css}
                z-index: 1000;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )

    # Bouton de toggle
    if st.button(
        f"{icone} {label}",
        key=_keys("toggle"),
        help=tooltip,
        type="secondary" if not actif else "primary",
    ):
        toggle_mode_focus()
        st.rerun()


@composant_ui("focus", tags=("ui", "fab", "focus"))
def mode_focus_fab() -> None:
    """
    Bouton flottant (FAB) pour le mode focus.
    Plus discret que le toggle standard.
    """
    actif = is_mode_focus()
    icone = "↩️" if actif else "🧘"

    # CSS pour le FAB
    st.markdown(
        """
        <style>
        .focus-fab {
            position: fixed;
            bottom: 80px;
            right: 20px;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            background: var(--st-color-primary);
            color: white;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .focus-fab:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.2);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Utiliser st.button invisible + HTML visible
    col_spacer, col_fab = st.columns([9, 1])
    with col_fab:
        if st.button(icone, key=_keys("fab"), help="Mode focus"):
            toggle_mode_focus()
            st.rerun()


@composant_ui("focus", tags=("css", "layout", "focus"))
def injecter_css_mode_focus() -> None:
    """
    Injecte le CSS pour masquer sidebar/header en mode focus.
    À appeler dans app.py après vérification is_mode_focus().
    """
    if not is_mode_focus():
        return

    st.markdown(
        """
        <style>
        /* Masquer la sidebar en mode focus */
        [data-testid="stSidebar"] {
            display: none !important;
        }

        /* Masquer le bouton hamburger sidebar */
        button[kind="header"] {
            display: none !important;
        }

        /* Masquer le header custom (si présent) */
        .main-header {
            display: none !important;
        }

        /* Masquer la barre de navigation st.navigation */
        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        /* Maximiser le contenu */
        .main .block-container {
            max-width: 100% !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
            padding-top: 1rem !important;
        }

        /* Bandeau mode focus */
        .focus-mode-banner {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            z-index: 9999;
        }
        </style>

        <!-- Bandeau visuel mode focus -->
        <div class="focus-mode-banner"></div>
        """,
        unsafe_allow_html=True,
    )


@composant_ui("focus", tags=("ui", "bouton", "focus"))
def focus_exit_button() -> None:
    """
    Bouton de sortie du mode focus.
    À afficher dans le contenu en mode focus.
    """
    if not is_mode_focus():
        return

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(
            "↩️ Quitter le mode focus",
            key=_keys("exit"),
            type="secondary",
            use_container_width=True,
        ):
            desactiver_mode_focus()
            st.rerun()


__all__ = [
    "is_mode_focus",
    "activer_mode_focus",
    "desactiver_mode_focus",
    "toggle_mode_focus",
    "mode_focus_toggle",
    "mode_focus_fab",
    "injecter_css_mode_focus",
    "focus_exit_button",
]
