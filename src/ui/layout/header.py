"""
Header de l'application.
"""

from __future__ import annotations

import streamlit as st

from src.core.config import obtenir_parametres
from src.core.state import obtenir_etat
from src.ui.tokens import Couleur, Variante
from src.ui.utils import echapper_html


def afficher_header():
    """Affiche le header avec badges d'état et skip-link d'accessibilité."""
    from src.ui.components.atoms import badge

    parametres = obtenir_parametres()
    etat = obtenir_etat()

    # Skip-link d'accessibilité (visible uniquement au focus clavier)
    # Skip-link enhanced: set focus to the main landmark via JS to ensure
    # screen-readers and keyboard users land in the correct region.
    st.markdown(
        '<a class="skip-link" href="#main-content" '
        "onclick=\"(function(){var m=document.getElementById('main-content'); if(m){m.focus();} return false; })();\">Aller au contenu principal</a>",
        unsafe_allow_html=True,
    )

    # CSS global: boutons non-wrap, padding plus large, et carte chat stylée
    st.markdown(
        """
        <style>
        /* Empêche le retour à la ligne dans les boutons Streamlit */
        button[data-testid="stButton"] > div {
            white-space: nowrap;
        }

        /* Ajuste padding et arrondi des boutons pour un rendu plus doux */
        button[data-testid="stButton"] {
            padding: 8px 14px !important;
            border-radius: 10px !important;
        }

        /* Petite carte pour l'assistant chat lorsqu'il est affiché inline */
        .chat-card {
            background: var(--st-color-background);
            border-radius: 12px;
            padding: 10px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            border: 1px solid rgba(0,0,0,0.04);
        }

        /* Badge animé pour nouveau message */
        .chat-open-badge {
            display: inline-block;
            background: #ff4d4f;
            color: white;
            padding: 2px 6px;
            font-size: 12px;
            border-radius: 999px;
            margin-top: 6px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            animation: pulse 1.6s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.06); opacity: 0.85; }
            100% { transform: scale(1); opacity: 1; }
        }

        /* Drawer positioning */
        .chat-drawer {
            position: fixed;
            right: 20px;
            bottom: 20px;
            width: 360px;
            max-height: 60vh;
            z-index: 9999;
        }

        .chat-messages {
            overflow-y: auto;
            max-height: 44vh;
            padding-bottom: 8px;
        }

        .chat-msg { margin: 6px 0; display: flex; }
        .chat-msg-user { justify-content: flex-end; }
        .chat-msg-assistant { justify-content: flex-start; }
        .chat-bubble { padding: 8px 12px; border-radius: 12px; max-width: 78%; }
        .chat-msg-user .chat-bubble { background: var(--st-color-primary); color: white; border-bottom-right-radius: 4px; }
        .chat-msg-assistant .chat-bubble { background: var(--st-color-background-secondary); color: var(--st-color-text); border-bottom-left-radius: 4px; }

        /* Drawer chat flottant (bottom-right) */
        .chat-drawer {
            position: fixed;
            right: 24px;
            bottom: 24px;
            width: 360px;
            max-width: calc(100% - 48px);
            max-height: 60vh;
            overflow: auto;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .chat-messages { display: flex; flex-direction: column; gap: 8px; }

        .chat-msg { display: flex; }
        .chat-msg-assistant { justify-content: flex-start; }
        .chat-msg-user { justify-content: flex-end; }

        .chat-bubble {
            padding: 8px 12px;
            border-radius: 12px;
            max-width: 78%;
            background: var(--st-color-surface-muted, #f3f4f6);
            color: var(--st-color-primary-700, #111827);
            box-shadow: 0 4px 10px rgba(0,0,0,0.04);
            word-break: break-word;
        }

        .chat-msg-user .chat-bubble { background: var(--st-color-primary, #60a5fa); color: white; }
        .chat-msg-assistant .chat-bubble { background: var(--st-color-surface, #ffffff); color: inherit; }

        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        st.markdown(
            f"<div class='main-header' role='banner' aria-label='En-tête application'>"
            f"<h1 style='white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>🤖 {echapper_html(parametres.APP_NAME)}</h1>"
            f"<p style='color: var(--sem-on-surface-muted, {Couleur.SECONDARY}); margin: 0;'>"
            f"Assistant familial intelligent"
            f"</p></div>",
            unsafe_allow_html=True,
        )

    with col2:
        if etat.agent_ia:
            badge("🤖 IA Active", variante=Variante.SUCCESS)
        else:
            badge("🤖 IA Indispo", variante=Variante.WARNING)

    with col3:
        # Recherche globale + undo — affichés sans sous-colonnes pour éviter les boutons trop étroits
        btn_cols = st.columns([1, 1, 1])
        with btn_cols[0]:
            try:
                from src.ui.components import afficher_recherche_globale_popover

                afficher_recherche_globale_popover()
            except ImportError:
                pass
        with btn_cols[1]:
            try:
                from src.ui.components import afficher_bouton_undo

                afficher_bouton_undo()
            except ImportError:
                pass
        with btn_cols[2]:
            if etat.notifications_non_lues > 0:
                if st.button(f"🔔 {etat.notifications_non_lues}", key="_header_notif"):
                    st.session_state.show_notifications = True
