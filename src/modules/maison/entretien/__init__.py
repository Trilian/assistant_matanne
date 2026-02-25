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

from src.core.ai import ClientIA
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

__all__ = [
    "app",
    "EntretienService",
    "get_entretien_service",
    "creer_routine",
    "ajouter_tache_routine",
    "marquer_tache_faite",
    "desactiver_routine",
    "get_stats_entretien",
    "charger_routines",
    "get_taches_today",
    "ClientIA",
]

_keys = KeyNamespace("entretien")
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE IA
# ═══════════════════════════════════════════════════════════


class EntretienService:
    """Service IA pour l'entretien de la maison."""

    service_name: str = "entretien"
    cache_prefix: str = "entretien"

    def __init__(self, client=None):
        if client is None:
            try:
                self.client = ClientIA()
            except Exception:
                self.client = None
        else:
            self.client = client

    async def call_with_cache(self, prompt: str, **kwargs) -> str:
        """Appel IA avec cache."""
        if self.client is None:
            return ""
        return await self.client.generer(prompt=prompt, **kwargs)

    async def creer_routine(self, nom: str, description: str = "") -> str:
        """Crée des suggestions de routine."""
        prompt = f"Crée une routine d'entretien '{nom}' pour: {description}. Liste les tâches."
        return await self.call_with_cache(prompt=prompt)

    async def optimiser_semaine(self, routines: str) -> str:
        """Optimise le planning de la semaine."""
        prompt = f"Optimise ce planning d'entretien hebdomadaire: {routines}. Répartis par jour."
        return await self.call_with_cache(prompt=prompt)

    async def conseil_temps_estime(self, tache: str) -> str:
        """Estime le temps pour une tâche."""
        prompt = f"Estime le temps nécessaire pour la tâche d'entretien: {tache}."
        return await self.call_with_cache(prompt=prompt)

    async def conseil_efficacite(self, tache: str = "") -> str:
        """Donne des astuces d'efficacité."""
        prompt = f"Donne des astuces pour réaliser efficacement: {tache}."
        return await self.call_with_cache(prompt=prompt)


_service_instance: EntretienService | None = None


def get_entretien_service() -> EntretienService:
    """Factory pour le service entretien (singleton)."""
    global _service_instance
    if _service_instance is None:
        _service_instance = EntretienService()
    return _service_instance


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
