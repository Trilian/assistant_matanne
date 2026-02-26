"""
Sous-module Jardin - Gestion intelligente du potager et du jardin.

Fonctionnalités:
- Gestion des plantes (ajout, arrosage, suivi)
- Conseils IA saisonniers
- Suivi des récoltes
- Statistiques et alertes
"""

import logging

import pandas as pd
import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.modules.maison.utils import (
    charger_plantes,
    get_plantes_a_arroser,
    get_recoltes_proches,
    get_saison,
    get_stats_jardin,
)
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

__all__ = [
    "app",
    "ajouter_plante",
    "arroser_plante",
    "ajouter_log",
    "get_saison",
    "get_plantes_a_arroser",
    "get_recoltes_proches",
    "get_stats_jardin",
    "charger_plantes",
]

_keys = KeyNamespace("jardin")
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE LAZY LOADER
# ═══════════════════════════════════════════════════════════


def _get_service():
    """Retourne le service singleton JardinService."""
    from src.services.maison import get_jardin_service

    return get_jardin_service()


# ═══════════════════════════════════════════════════════════
# FONCTIONS METIER (délèguent au service)
# ═══════════════════════════════════════════════════════════


def ajouter_plante(nom: str, type_plante: str, **kwargs) -> bool:
    """Ajoute une plante au jardin."""
    result = _get_service().ajouter_plante(nom, type_plante, **kwargs)
    if result is None:
        st.error("Erreur lors de l'ajout de la plante")
        return False
    return True


def arroser_plante(plante_id: int) -> bool:
    """Enregistre un arrosage pour une plante."""
    return _get_service().arroser_plante(plante_id)


def ajouter_log(plante_id: int, action: str, notes: str = "") -> bool:
    """Ajoute un log d'activité pour une plante."""
    return _get_service().ajouter_log_jardin(plante_id, action, notes)


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════


@profiler_rerun("jardin")
def app():
    """Point d'entrée du module Jardin."""
    with error_boundary(titre="Erreur module Jardin"):
        st.title("🌱 Mon Jardin")
        st.caption("Gérez vos plantes, arrosages et récoltes.")

        # Alertes plantes à arroser
        plantes_arrosage = get_plantes_a_arroser()
        for p in plantes_arrosage:
            st.warning(f"💧 {p.get('nom', 'Plante')} a besoin d'eau !")

        # Stats
        stats = get_stats_jardin()
        saison = get_saison()
        cols = st.columns(4)
        with cols[0]:
            st.metric("🌿 Plantes", stats.get("total_plantes", 0))
        with cols[1]:
            st.metric("💧 À arroser", stats.get("a_arroser", 0))
        with cols[2]:
            st.metric("🥕 Récoltes", stats.get("recoltes_proches", 0))
        with cols[3]:
            st.metric("📅 Saison", saison)

        st.divider()

        # Onglets
        TAB_LABELS = ["🌿 Mes plantes", "➕ Ajouter", "📊 Stats"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            df = charger_plantes()
            if hasattr(df, "empty") and df.empty:
                st.info("Aucune plante enregistrée.")
            else:
                for _, row in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row.get('nom', '')}**")
                        st.caption(row.get("type_plante", ""))

        with tab2:
            st.subheader("➕ Ajouter une plante")
            with st.form(key=_keys("form_plante")):
                nom = st.text_input("Nom de la plante")
                type_p = st.selectbox("Type", ["legume", "fruit", "herbe", "fleur"])
                submitted = st.form_submit_button("Ajouter")
            if submitted and nom:
                ajouter_plante(nom, type_p)
                st.success(f"✅ {nom} ajoutée !")
                rerun()

        with tab3:
            st.subheader("📊 Statistiques")
            recoltes = get_recoltes_proches()
            if recoltes:
                st.markdown(f"**{len(recoltes)} récolte(s) à venir**")
            else:
                st.info("Aucune récolte prochaine.")
