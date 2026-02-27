"""
🏘️ Visualisation Maison — Plan 2D/3D des pièces et travaux.

Vue interactive de la maison avec :
- Plan 2D : pièces positionnées et colorées par état
- Vue 3D : extrusion des pièces en volumes
- Détails : historique travaux, meubles, entretien par pièce
"""

import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

_keys = KeyNamespace("maison_visu")

ETAGE_LABELS = {-1: "Sous-sol", 0: "RDC", 1: "1er étage", 2: "2ème étage"}


def _get_service():
    """Retourne le service visualisation singleton."""
    from src.services.maison.visualisation_service import get_visualisation_service

    return get_visualisation_service()


@profiler_rerun("maison_visualisation")
def app():
    """Point d'entrée du module Visualisation Maison."""
    with error_boundary(titre="Erreur visualisation maison"):
        st.title("🏘️ Plan de la Maison")
        st.caption("Visualisez vos pièces, travaux et équipements.")

        service = _get_service()

        # Initialiser les pièces par défaut si table vide
        service.initialiser_pieces_defaut()

        # Stats rapides en header
        stats = service.obtenir_stats_globales()
        cols = st.columns(4)
        with cols[0]:
            st.metric("🏠 Pièces", stats["nb_pieces"])
        with cols[1]:
            st.metric("📦 Objets", stats["nb_objets"])
        with cols[2]:
            st.metric("🔨 Travaux", stats["nb_travaux"])
        with cols[3]:
            st.metric("💰 Budget", f"{stats['budget_total']:.0f}€")

        st.divider()

        # Onglets
        TAB_LABELS = ["🗺️ Plan 2D", "🏔️ Vue 3D", "📋 Détails"]
        tabs_with_url(TAB_LABELS, param="vtab")
        tab_2d, tab_3d, tab_details = st.tabs(TAB_LABELS)

        # Sélection étage
        etages = service.obtenir_etages_disponibles()

        with tab_2d:
            from .ui_2d import afficher_plan_2d

            etage_sel = None
            if len(etages) > 1:
                etage_sel = st.selectbox(
                    "Étage",
                    options=etages,
                    format_func=lambda e: ETAGE_LABELS.get(e, f"Étage {e}"),
                    key=_keys("etage_2d"),
                )

            pieces = service.obtenir_pieces_avec_details(etage=etage_sel)
            piece_selectionnee = afficher_plan_2d(pieces, service, key_prefix=_keys("plan"))

            # Si une pièce est sélectionnée, l'enregistrer pour l'onglet détails
            if piece_selectionnee:
                st.session_state[_keys("piece_sel_id")] = piece_selectionnee

        with tab_3d:
            from .ui_3d import afficher_vue_3d

            pieces_all = service.obtenir_pieces_avec_details()
            afficher_vue_3d(pieces_all)

        with tab_details:
            from .ui_details import afficher_details_piece

            piece_id = st.session_state.get(_keys("piece_sel_id"))
            pieces_all = service.obtenir_pieces_avec_details()

            if pieces_all:
                options = {
                    p["id"]: f"{p['nom']} ({ETAGE_LABELS.get(p['etage'], 'Ét.' + str(p['etage']))})"
                    for p in pieces_all
                }

                default_idx = 0
                if piece_id and piece_id in options:
                    default_idx = list(options.keys()).index(piece_id)

                sel = st.selectbox(
                    "Sélectionner une pièce",
                    options=list(options.keys()),
                    format_func=lambda x: options[x],
                    index=default_idx,
                    key=_keys("sel_piece_details"),
                )
                if sel:
                    afficher_details_piece(sel, service)
            else:
                st.info("Aucune pièce enregistrée.")
