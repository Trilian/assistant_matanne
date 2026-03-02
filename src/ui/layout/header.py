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

        /* ── Sidebar : titre application non tronqué ── */
        [data-testid="stSidebarHeader"] span,
        [data-testid="stSidebarHeader"] a {
            white-space: normal !important;
            overflow: visible !important;
            text-overflow: unset !important;
            font-size: 1rem !important;
            font-weight: 700 !important;
            line-height: 1.3 !important;
        }

        /* ── Bouton recherche globale (popover) ── */
        [data-testid="stPopover"] > button {
            border-radius: 20px !important;
            border: 1px solid var(--sem-border, #ced4da) !important;
            background: transparent !important;
            color: var(--sem-on-surface, #212529) !important;
            padding: 6px 16px !important;
            font-size: 0.9rem !important;
            transition: background 0.15s ease, border-color 0.15s ease !important;
            white-space: nowrap !important;
            min-width: 40px !important;
        }
        [data-testid="stPopover"] > button:hover {
            background: var(--sem-surface-alt, #f0f0f0) !important;
            border-color: var(--sem-interactive, #2E7D32) !important;
        }

        /* ══════════════════════════════════════════════════════
           STYLE GLOBAL UNIFORME — look professionnel & moderne
           ══════════════════════════════════════════════════════ */

        /* ── Metric cards : ombres douces, arrondis ── */
        [data-testid="stMetric"] {
            background: var(--sem-surface-alt, #f8f9fa) !important;
            border: 1px solid var(--sem-border-subtle, #e9ecef) !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
            transition: box-shadow 0.15s ease !important;
        }
        [data-testid="stMetric"]:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.04em !important;
            color: var(--sem-on-surface-secondary, #6c757d) !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            line-height: 1.2 !important;
            color: var(--sem-on-surface, #212529) !important;
        }
        [data-testid="stMetricDelta"] {
            font-size: 0.8rem !important;
            font-weight: 500 !important;
        }

        /* ── En-têtes de section ── */
        h2 {
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.6rem !important;
            color: var(--sem-on-surface, #212529) !important;
            border-bottom: 2px solid var(--sem-interactive, #2E7D32) !important;
            padding-bottom: 6px !important;
        }
        h3 {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.5rem !important;
            color: var(--sem-on-surface, #212529) !important;
        }
        h4 {
            font-size: 1rem !important;
            font-weight: 600 !important;
            margin-top: 1rem !important;
            margin-bottom: 0.4rem !important;
            color: var(--sem-on-surface-secondary, #495057) !important;
        }

        /* ── Onglets (tabs) ── */
        [data-testid="stTabs"] [role="tab"] {
            border-radius: 8px 8px 0 0 !important;
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            padding: 8px 16px !important;
            transition: background 0.15s ease !important;
        }
        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            font-weight: 700 !important;
            color: var(--sem-interactive, #2E7D32) !important;
            border-bottom: 2px solid var(--sem-interactive, #2E7D32) !important;
        }

        /* ── Expanders ── */
        [data-testid="stExpander"] > details {
            border: 1px solid var(--sem-border-subtle, #e9ecef) !important;
            border-radius: 10px !important;
            overflow: hidden !important;
        }
        [data-testid="stExpander"] summary {
            background: var(--sem-surface-alt, #f8f9fa) !important;
            padding: 10px 14px !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }

        /* ── Info / Warning / Error boxes ── */
        [data-testid="stAlert"] {
            border-radius: 10px !important;
            border-left-width: 4px !important;
        }

        /* ── Sidebar : espacement réduit, style épuré ── */
        [data-testid="stSidebar"] {
            border-right: 1px solid var(--sem-border-subtle, #e9ecef) !important;
        }
        [data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
            padding-top: 0.5rem !important;
        }
        /* Réduction du gap entre le dernier nav item et le profil */
        [data-testid="stSidebar"] .stSelectbox {
            margin-top: 2px !important;
        }
        /* Nav items ─ taille, poids */
        [data-testid="stSidebarNav"] a {
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            padding: 6px 14px !important;
            border-radius: 8px !important;
            transition: background 0.15s ease !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"],
        [data-testid="stSidebarNav"] a:hover {
            background: var(--sem-interactive-subtle, #e8f5e9) !important;
            color: var(--sem-interactive, #2E7D32) !important;
            font-weight: 700 !important;
        }

        /* ── Header principal ── */
        .main-header h1 {
            font-size: 1.6rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.01em !important;
            color: var(--sem-on-surface, #1a202c) !important;
        }

        /* ── Boutons : uniformes, arrondis, transition ── */
        button[data-testid="stBaseButton-secondary"],
        button[data-testid="stBaseButton-primary"] {
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            transition: transform 0.1s ease, box-shadow 0.15s ease !important;
        }
        button[data-testid="stBaseButton-primary"] {
            background: var(--sem-interactive, #2E7D32) !important;
            color: #fff !important;
            border: none !important;
            box-shadow: 0 2px 8px rgba(46,125,50,0.25) !important;
        }
        button[data-testid="stBaseButton-primary"]:hover {
            box-shadow: 0 4px 16px rgba(46,125,50,0.35) !important;
            transform: translateY(-1px) !important;
        }

        /* ── Scrollbar esthétique (Webkit) ── */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb {
            background: var(--sem-border, #ced4da);
            border-radius: 999px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--sem-on-surface-secondary, #6c757d);
        }

        /* ── Séparateurs hr ── */
        hr {
            border: none !important;
            border-top: 1px solid var(--sem-border-subtle, #e9ecef) !important;
            margin: 12px 0 !important;
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

    # Flat layout: title | badge | search | undo | notifications
    col1, col_badge, col_search, col_undo, col_notif = st.columns([5, 2, 1, 1, 1])

    with col1:
        st.markdown(
            f"<div class='main-header' role='banner' aria-label='En-tête application'>"
            f"<h1 style='white-space: nowrap; margin-bottom: 2px;'>🤖 {echapper_html(parametres.APP_NAME)}</h1>"
            f"<p style='color: var(--sem-on-surface-muted, {Couleur.SECONDARY}); margin: 0; font-size: 0.9rem;'>"
            f"Assistant familial intelligent"
            f"</p></div>",
            unsafe_allow_html=True,
        )

    with col_badge:
        st.markdown('<div style="padding-top: 14px;">', unsafe_allow_html=True)
        if etat.agent_ia:
            badge("🤖 IA Active", variante=Variante.SUCCESS)
        else:
            badge("🤖 IA Indispo", variante=Variante.WARNING)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_search:
        try:
            from src.ui.components import afficher_recherche_globale_popover

            afficher_recherche_globale_popover()
        except ImportError:
            pass

    with col_undo:
        try:
            from src.ui.components import afficher_bouton_undo

            afficher_bouton_undo()
        except ImportError:
            pass

    with col_notif:
        if etat.notifications_non_lues > 0:
            if st.button(f"🔔 {etat.notifications_non_lues}", key="_header_notif"):
                st.session_state.show_notifications = True
