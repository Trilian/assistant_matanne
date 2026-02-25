"""
Module Projets Maison - Gestion des projets domestiques.

Sous-module pour planifier, estimer et suivre les projets de la maison:
- Création de projets avec estimation IA (budget, matériaux, tâches)
- Suivi de l'avancement avec timeline
- Gestion des tâches par projet
- Calcul ROI rénovations énergétiques
"""

from __future__ import annotations

import asyncio
import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

import pandas as pd
import plotly.express as px
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models.maison import Projet, TacheProjet
from src.core.monitoring.rerun_profiler import profiler_rerun
from src.modules._framework import error_boundary
from src.modules.maison.utils import (
    charger_projets,
    clear_maison_cache,
    get_projets_urgents,
    get_stats_projets,
)
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

if TYPE_CHECKING:
    from src.services.maison import ProjetsService

__all__ = [
    "app",
    "creer_projet",
    "ajouter_tache",
    "marquer_tache_done",
    "marquer_projet_done",
    "run_ia_suggerer_taches",
    "run_ia_estimer_duree",
    "run_ia_analyser_risques",
    "creer_graphique_progression",
]

_keys = KeyNamespace("projets")
logger = logging.getLogger(__name__)


# Navigation helper
def go(page: str) -> None:
    """Navigation helper."""
    from src.core.state import naviguer, rerun

    naviguer(page)


# NOTE: Pour l'accès au service IA projets, utilisez:
# from src.services.maison import get_projets_service


# ═══════════════════════════════════════════════════════════
# CRUD FONCTIONS
# ═══════════════════════════════════════════════════════════


def creer_projet(
    nom: str,
    description: str,
    categorie: str,
    priorite: str,
    db=None,
    date_fin: date | None = None,
) -> int | None:
    """Crée un nouveau projet.

    Returns:
        ID du projet créé, ou None en cas d'erreur.
    """

    def _do(session):
        projet = Projet(
            nom=nom,
            description=description,
            priorite=priorite,
            statut="en_cours",
        )
        if date_fin:
            projet.date_fin_prevue = date_fin
        session.add(projet)
        session.commit()
        session.refresh(projet)
        clear_maison_cache()
        return projet.id

    try:
        if db is None:
            with obtenir_contexte_db() as session:
                return _do(session)
        return _do(db)
    except Exception as e:
        logger.error(f"Erreur création projet: {e}")
        st.error(f"Erreur lors de la création du projet: {e}")
        return None


def ajouter_tache(
    project_id: int,
    nom: str,
    description: str | None = None,
    priorite: str | None = None,
    date_echeance: date | None = None,
    db=None,
) -> bool:
    """Ajoute une tâche à un projet.

    Returns:
        True si la tâche a été ajoutée.
    """
    try:
        kwargs = {
            "project_id": project_id,
            "nom": nom,
            "statut": "a_faire",
        }
        if description:
            kwargs["description"] = description
        if priorite:
            kwargs["priorite"] = priorite
        if date_echeance:
            kwargs["date_echeance"] = date_echeance
        tache = TacheProjet(**kwargs)
        db.add(tache)
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        logger.error(f"Erreur ajout tâche: {e}")
        st.error(f"Erreur lors de l'ajout de la tâche: {e}")
        return False


def marquer_tache_done(task_id: int, db) -> bool:
    """Marque une tâche comme terminée."""
    try:
        tache = db.query(TacheProjet).get(task_id)
        if tache is None:
            return False
        tache.statut = "termine"
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        logger.error(f"Erreur marquage tâche: {e}")
        st.error(f"Erreur: {e}")
        return False


def marquer_projet_done(project_id: int, db=None) -> bool:
    """Marque un projet comme terminé."""
    try:
        if db is None:
            with obtenir_contexte_db() as db:
                projet = db.query(Projet).get(project_id)
                if projet is None:
                    return False
                projet.statut = "termine"
                db.commit()
                clear_maison_cache()
                return True
        projet = db.query(Projet).get(project_id)
        if projet is None:
            return False
        projet.statut = "termine"
        db.commit()
        clear_maison_cache()
        return True
    except Exception as e:
        logger.error(f"Erreur marquage projet: {e}")
        st.error(f"Erreur: {e}")
        return False


# ═══════════════════════════════════════════════════════════
# HELPERS IA
# ═══════════════════════════════════════════════════════════


def run_ia_suggerer_taches(service: ProjetsService, nom: str, description: str) -> tuple[bool, str]:
    """Exécute la suggestion IA de tâches (sync wrapper)."""
    try:
        result = asyncio.run(service.suggerer_taches(nom, description))
        if not result:
            return (False, "Aucune suggestion disponible.")
        return (True, result)
    except Exception as e:
        logger.error(f"Erreur IA suggestion: {e}")
        return (False, "IA indisponible.")


def run_ia_estimer_duree(service: ProjetsService, nom: str, complexite: str) -> tuple[bool, str]:
    """Exécute l'estimation IA de la durée (sync wrapper)."""
    try:
        result = asyncio.run(service.estimer_duree(nom, complexite))
        if not result:
            return (False, "Estimation non disponible.")
        return (True, result)
    except Exception as e:
        logger.error(f"Erreur IA durée: {e}")
        return (False, "IA indisponible.")


def run_ia_analyser_risques(service: ProjetsService, description: str) -> tuple[bool, str]:
    """Analyse les risques d'un projet via IA (sync wrapper)."""
    try:
        result = asyncio.run(service.conseil_blocages("Projet", description))
        if not result:
            return (False, "Aucun risque identifié.")
        return (True, result)
    except Exception as e:
        logger.error(f"Erreur IA risques: {e}")
        return (False, "IA indisponible.")


# ═══════════════════════════════════════════════════════════
# CHART
# ═══════════════════════════════════════════════════════════


def creer_graphique_progression(df: pd.DataFrame):
    """Crée un graphique de progression des projets.

    Args:
        df: DataFrame avec colonnes 'projet' et 'progression'.

    Returns:
        Plotly Figure.
    """
    fig = px.bar(
        df,
        x="projet",
        y="progression",
        title="Progression des projets",
        labels={"projet": "Projet", "progression": "Progression (%)"},
    )
    fig.update_layout(yaxis_range=[0, 100])
    return fig


# ═══════════════════════════════════════════════════════════
# TEMPLATES
# ═══════════════════════════════════════════════════════════

TEMPLATES_PROJETS = [
    {
        "nom": "Renovation cuisine",
        "description": "Rénovation complète de la cuisine",
        "categorie": "renovation",
        "priorite": "haute",
        "taches": ["Choisir les matériaux", "Faire des devis", "Planifier travaux"],
    },
    {
        "nom": "Rangement garage",
        "description": "Ranger et organiser le garage",
        "categorie": "rangement",
        "priorite": "moyenne",
        "taches": ["Trier", "Acheter rangements", "Organiser"],
    },
]


# ═══════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════


@profiler_rerun("projets")
def app():
    """Point d'entrée du module Projets Maison."""
    with error_boundary(titre="Erreur module Projets"):
        st.title("🏗️ Projets Maison")
        st.caption("Planifiez, estimez et suivez vos projets domestiques.")

        # Alertes urgentes
        urgents = get_projets_urgents()
        for u in urgents:
            st.warning(f"⚠️ {u['message']}")

        # Stats
        stats = get_stats_projets()
        cols = st.columns(4)
        with cols[0]:
            st.metric("Total", stats.get("total", 0))
        with cols[1]:
            st.metric("En cours", stats.get("en_cours", 0))
        with cols[2]:
            st.metric("Terminés", stats.get("termines", 0))
        with cols[3]:
            avg = stats.get("avg_progress", 0)
            st.metric("Progression moy.", f"{avg}%")

        st.divider()

        # Onglets
        TAB_LABELS = ["📋 Projets", "➕ Nouveau", "📊 Graphique", "📝 Templates"]
        tab_index = tabs_with_url(TAB_LABELS, param="tab")
        tab1, tab2, tab3, tab4 = st.tabs(TAB_LABELS)

        with tab1:
            _onglet_projets()

        with tab2:
            _onglet_nouveau()

        with tab3:
            _onglet_graphique()

        with tab4:
            _onglet_templates()


def _onglet_projets():
    """Affiche la liste des projets."""
    df = charger_projets()
    if hasattr(df, "empty") and df.empty:
        st.info("Aucun projet. Créez-en un dans l'onglet 'Nouveau'.")
        return

    for _, row in df.iterrows():
        with st.expander(
            f"{'🔴' if row.get('priorite') == 'urgente' else '📋'} {row['nom']} — {row.get('progress', 0)}%"
        ):
            if row.get("description"):
                st.caption(row["description"])

            jours = row.get("jours_restants")
            if jours is not None:
                if jours < 0:
                    st.caption(f"⚠️ En retard de {abs(jours)} jours")
                elif jours == 0:
                    st.caption("📅 Échéance aujourd'hui")
                else:
                    st.caption(f"📅 {jours} jours restants")

            st.progress(min(row.get("progress", 0) / 100, 1.0))

            # Tâches
            with obtenir_contexte_db() as db:
                taches = db.query(TacheProjet).filter_by(project_id=row["id"]).all()

            if taches:
                for t in taches:
                    icone = "✅" if t.statut == "termine" else "⬜"
                    echeance = f" — {t.date_echeance.strftime('%d/%m')}" if t.date_echeance else ""
                    st.caption(f"{icone} {t.nom}{echeance}")
                    if t.statut != "termine":
                        if st.button("✓ Terminer", key=f"task_done_{t.id}"):
                            with obtenir_contexte_db() as db2:
                                marquer_tache_done(t.id, db2)
                            rerun()

            # Bouton terminer le projet
            if st.button("✅ Terminer le projet", key=f"done_{row['id']}"):
                marquer_projet_done(row["id"])
                rerun()


def _onglet_nouveau():
    """Formulaire de création de projet."""
    st.subheader("➕ Nouveau projet")
    with st.form(key=_keys("form_projet")):
        nom = st.text_input("Nom du projet")
        description = st.text_area("Description")
        priorite = st.selectbox("Priorité", ["basse", "moyenne", "haute", "urgente"])
        date_fin = st.date_input("Date d'échéance", value=None)
        submitted = st.form_submit_button("Créer", use_container_width=True)

    if submitted and nom:
        pid = creer_projet(
            nom=nom,
            description=description,
            categorie="general",
            priorite=priorite,
            date_fin=date_fin,
        )
        if pid:
            st.success(f"✅ Projet créé (ID: {pid})")
            rerun()


def _onglet_graphique():
    """Graphique de progression."""
    df = charger_projets()
    if hasattr(df, "empty") and df.empty:
        st.info("Aucun projet à afficher.")
        return

    chart_df = pd.DataFrame(
        {
            "projet": df["nom"],
            "progression": df.get("progress", 0),
        }
    )
    fig = creer_graphique_progression(chart_df)
    st.plotly_chart(fig, use_container_width=True)


def _onglet_templates():
    """Templates de projets."""
    st.subheader("📝 Templates de projets")
    for tpl in TEMPLATES_PROJETS:
        with st.container(border=True):
            st.markdown(f"**{tpl['nom']}**")
            st.caption(tpl["description"])
            if st.button(f"📋 {tpl['nom']}", key=f"tpl_{tpl['nom']}"):
                pid = creer_projet(
                    nom=tpl["nom"],
                    description=tpl["description"],
                    categorie=tpl["categorie"],
                    priorite=tpl["priorite"],
                )
                if pid:
                    for t_nom in tpl.get("taches", []):
                        ajouter_tache(pid, t_nom)
                    st.success(
                        f"✅ Projet '{tpl['nom']}' créé avec {len(tpl.get('taches', []))} tâches"
                    )
                    rerun()
