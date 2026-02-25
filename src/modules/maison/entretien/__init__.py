"""
Module Entretien - Gestion des routines d'entretien de la maison.

Fonctionnalités:
- Routines d'entretien avec tâches récurrentes
- Suivi des tâches quotidiennes
- Conseils IA pour optimisation
- Statistiques et alertes
"""

import logging

import pandas as pd
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models.maison import Routine, TacheRoutine
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.modules.maison.utils import (
    charger_routines,
    get_stats_entretien,
    get_taches_today,
)
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

__all__ = [
    "app",
    "creer_routine",
    "ajouter_tache_routine",
    "marquer_tache_faite",
    "desactiver_routine",
    "get_stats_entretien",
    "charger_routines",
    "get_taches_today",
]

_keys = KeyNamespace("entretien")
logger = logging.getLogger(__name__)

# NOTE: Pour l'accès au service IA entretien, utilisez:
# from src.services.maison import get_entretien_service


# ═══════════════════════════════════════════════════════════
# FONCTIONS METIER
# ═══════════════════════════════════════════════════════════


def creer_routine(nom: str, frequence: str = "quotidien", **kwargs) -> bool:
    """Crée une nouvelle routine d'entretien."""
    try:
        with obtenir_contexte_db() as db:
            routine = Routine(nom=nom, frequence=frequence, **kwargs)
            db.add(routine)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur création routine: {e}")
        st.error(f"Erreur: {e}")
        return False


def ajouter_tache_routine(routine_id: int, nom: str, **kwargs) -> bool:
    """Ajoute une tâche à une routine."""
    try:
        with obtenir_contexte_db() as db:
            tache = TacheRoutine(routine_id=routine_id, nom=nom, **kwargs)
            db.add(tache)
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur ajout tâche: {e}")
        st.error(f"Erreur: {e}")
        return False


def marquer_tache_faite(tache_id: int) -> bool:
    """Marque une tâche de routine comme faite."""
    try:
        with obtenir_contexte_db() as db:
            tache = db.query(TacheRoutine).get(tache_id)
            if tache is None:
                return False
            tache.fait = True
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur marquage tâche: {e}")
        st.error(f"Erreur: {e}")
        return False


def desactiver_routine(routine_id: int) -> bool:
    """Désactive une routine."""
    try:
        with obtenir_contexte_db() as db:
            routine = db.query(Routine).get(routine_id)
            if routine is None:
                return False
            routine.actif = False
            db.commit()
            return True
    except Exception as e:
        logger.error(f"Erreur désactivation routine: {e}")
        st.error(f"Erreur: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════


@profiler_rerun("entretien")
def app():
    """Point d'entrée du module Entretien."""
    with error_boundary(titre="Erreur module Entretien"):
        st.title("🧹 Entretien Maison")
        st.caption("Gérez vos routines d'entretien et tâches ménagères.")

        # Stats
        stats = get_stats_entretien()
        cols = st.columns(3)
        with cols[0]:
            st.metric("Routines", stats.get("total_routines", 0))
        with cols[1]:
            st.metric("Aujourd'hui", stats.get("taches_today", 0))
        with cols[2]:
            st.metric("Accompli", f"{stats.get('taux_completion', 0)}%")

        st.divider()

        # Onglets
        TAB_LABELS = ["📋 Routines", "📅 Aujourd'hui", "➕ Nouvelle"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3 = st.tabs(TAB_LABELS)

        with tab1:
            df = charger_routines()
            if hasattr(df, "empty") and df.empty:
                st.info("Aucune routine. Créez-en une !")
            else:
                for _, row in df.iterrows():
                    with st.container(border=True):
                        st.markdown(f"**{row.get('nom', '')}**")
                        st.caption(row.get("frequence", ""))

        with tab2:
            taches = get_taches_today()
            if not taches:
                st.info("Rien de prévu aujourd'hui !")
            else:
                for t in taches:
                    st.checkbox(t.get("nom", ""), key=f"tache_{t.get('id', 0)}")

        with tab3:
            st.subheader("➕ Nouvelle routine")
            with st.form(key=_keys("form_routine")):
                nom = st.text_input("Nom de la routine")
                freq = st.selectbox("Fréquence", ["quotidien", "hebdomadaire", "mensuel"])
                submitted = st.form_submit_button("Créer")
            if submitted and nom:
                creer_routine(nom, freq)
                st.success(f"✅ Routine '{nom}' créée !")
                st.rerun()
