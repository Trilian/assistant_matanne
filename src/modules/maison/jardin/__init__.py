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

from src.core.db import obtenir_contexte_db
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

# NOTE: Pour l'accès au service IA jardin, utilisez:
# from src.services.maison import get_jardin_service


# ═══════════════════════════════════════════════════════════
# FONCTIONS METIER
# ═══════════════════════════════════════════════════════════


def ajouter_plante(nom: str, type_plante: str, **kwargs) -> bool:
    """Ajoute une plante au jardin."""
    try:
        from src.core.models.maison import ElementJardin

        with obtenir_contexte_db() as db:
            plante = ElementJardin(nom=nom, type_plante=type_plante, **kwargs)
            db.add(plante)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur ajout plante: {e}")
        st.error(f"Erreur: {e}")
        return False


def arroser_plante(plante_id: int) -> bool:
    """Enregistre un arrosage pour une plante."""
    try:
        from src.core.models.maison import JournalJardin

        with obtenir_contexte_db() as db:
            log = JournalJardin(garden_item_id=plante_id, action="arrosage")
            db.add(log)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur arrosage: {e}")
        st.error(f"Erreur: {e}")
        return False


def ajouter_log(plante_id: int, action: str, notes: str = "") -> bool:
    """Ajoute un log d'activité pour une plante."""
    try:
        from src.core.models.maison import JournalJardin

        with obtenir_contexte_db() as db:
            log = JournalJardin(
                garden_item_id=plante_id,
                action=action,
                notes=notes,
            )
            db.add(log)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur log jardin: {e}")
        st.error(f"Erreur: {e}")
        return False


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
