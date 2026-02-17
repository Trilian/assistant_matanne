"""
Charges - Point d'entrée principal.

Module de suivi des charges et consommations énergétiques.
"""

import streamlit as st

from .onglets import (
    onglet_analyse,
    onglet_conseils,
    onglet_dashboard,
    onglet_factures,
    onglet_simulation,
)
from .styles import CHARGES_CSS
from .ui import afficher_header


def app():
    """Point d'entrée du module Charges gamifié."""
    st.markdown(CHARGES_CSS, unsafe_allow_html=True)

    # Initialiser les données en session
    if "factures_charges" not in st.session_state:
        st.session_state.factures_charges = []

    if "badges_vus" not in st.session_state:
        st.session_state.badges_vus = []

    factures = st.session_state.factures_charges

    # Header
    afficher_header()

    # Onglets enrichis
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Dashboard", "📄 Factures", "📈 Analyse", "💰 Simulation", "💡 Conseils"]
    )

    with tab1:
        onglet_dashboard(factures)

    with tab2:
        onglet_factures(factures)

    with tab3:
        onglet_analyse(factures)

    with tab4:
        onglet_simulation(factures)

    with tab5:
        onglet_conseils()


if __name__ == "__main__":
    app()
