"""
Onglet Historique Rapports - UI Streamlit
"""

import streamlit as st

from src.ui.fragments import cached_fragment, lazy, ui_fragment
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("rapports_historique")


@lazy(condition=lambda: st.session_state.get(_keys("show_guide"), False), show_skeleton=True)
def _afficher_guide_complet():
    """Guide d'utilisation complet (lazy-loaded)."""
    st.markdown("""
    **Rapport Stocks:**
    - Genere chaque semaine
    - Montre articles en faible stock
    - Identifie articles perimes
    - Calcule valeur du stock

    **Rapport Budget:**
    - Analyse depenses par categorie
    - Identifie articles coûteux
    - Compare avec semaines precedentes
    - Aide à budgeter les courses

    **Analyse Gaspillage:**
    - Calcule valeur perdue
    - Identifie patterns de gaspillage
    - Donne recommandations
    - Aide à reduire pertes
    """)


@cached_fragment(ttl=600)
def _afficher_statistiques_rapports():
    """Statistiques rapports (cache 10 min)."""
    # TODO: Récupérer vraies stats depuis service
    st.metric("Rapports generes ce mois", 12)
    st.metric("Articles analyses", 47)
    st.metric("Valeur stock totale", "€1,234.56")


@ui_fragment
def afficher_historique():
    """Historique rapports generes"""

    st.subheader("🗑️ Historique & Planification")

    st.markdown("""
    Planifiez la generation automatique de rapports.
    """)

    # Planification
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📋 Rapports Hebdomadaires")

        st.markdown("""
        - ✅ **Rapport stocks** - chaque lundi
        - ✅ **Rapport budget** - chaque dimanche
        - ✅ **Analyse gaspillage** - chaque vendredi
        """)

        if st.button("⚙️ Configurer planification", key="btn_schedule"):
            with st.expander("📅 Configuration des rapports automatiques", expanded=True):
                st.markdown("""
                Pour configurer les rapports automatiques:
                1. Allez dans le menu **Paramètres**
                2. Activez "Rapports automatiques"
                3. Choisissez les jours et heures de génération
                """)

    with col2:
        st.subheader("📊 Statistiques")
        _afficher_statistiques_rapports()

    # Guide (lazy-loaded)
    st.divider()
    st.subheader("🍽️ Guide d'utilisation")

    show_guide = st.checkbox(
        "ℹ️ Afficher le guide complet",
        key=_keys("show_guide"),
        help="Charge le guide d'utilisation détaillé",
    )
    if show_guide:
        _afficher_guide_complet()
