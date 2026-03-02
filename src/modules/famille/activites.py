"""
Module Activites - Planning et budget des activites familiales.

Refactorisé: la logique CRUD est dans ``src.services.famille.activites.ServiceActivites``.
Ce module ne contient que l'UI Streamlit.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.core.monitoring.rerun_profiler import profiler_rerun
from src.core.state import rerun
from src.modules._framework import error_boundary
from src.modules.famille.utils import (
    clear_famille_cache,
    get_activites_semaine,
    get_budget_activites_mois,
    get_budget_par_period,
)
from src.ui import etat_vide
from src.ui.fragments import cached_fragment
from src.ui.keys import KeyNamespace
from src.ui.state.url import tabs_with_url

if TYPE_CHECKING:
    from src.services.famille.activites import ServiceActivites

# Session keys scopées
_keys = KeyNamespace("activites")


def _get_service() -> ServiceActivites:
    """Lazy-load du service activites."""
    from src.services.famille.activites import obtenir_service_activites

    return obtenir_service_activites()


SUGGESTIONS_ACTIVITES = {
    "parc": ["Parc local", "Parc d'attractions (mini)", "Terrain de jeu"],
    "musee": ["Musee enfants", "Exposition interactive", "Aquarium"],
    "eau": ["Piscine", "Plage", "Parc aquatique bebe"],
    "jeu_maison": ["Jeux interieurs", "Chasse au tresor", "Soiree jeux de societe"],
    "sport": ["Cours de gym douce", "Équitation enfant", "Skating"],
    "sortie": ["Restaurant enfant-friendly", "Cinema familial", "Zoo"],
}

_TYPES_ACTIVITES = ["parc", "musee", "eau", "jeu_maison", "sport", "sortie"]


@cached_fragment(ttl=300)
def _graphique_budget_timeline(data: list[dict]) -> go.Figure:
    """Graphique timeline des dépenses (cache 5 min)."""
    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"])

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["cout_estime"],
            mode="lines+markers",
            name="Coût estimé",
            line_color="blue",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["cout_reel"],
            mode="lines+markers",
            name="Coût réel",
            line_color="red",
        )
    )
    fig.update_layout(
        title="Dépenses par Date",
        xaxis_title="Date",
        yaxis_title="Montant (€)",
        height=400,
        hovermode="x unified",
    )
    return fig


@cached_fragment(ttl=300)
def _graphique_budget_par_type(data: list[dict]) -> go.Figure:
    """Graphique budget par type d'activité (cache 5 min)."""
    df = pd.DataFrame(data)
    type_budget = df.groupby("type")["cout_estime"].sum().reset_index()
    type_budget.columns = ["Type", "Budget"]

    fig = go.Figure(
        data=[
            go.Bar(
                x=type_budget["Type"],
                y=type_budget["Budget"],
                marker_color="lightblue",
            )
        ]
    )
    fig.update_layout(
        title="Budget par Type d'Activité",
        xaxis_title="Type",
        yaxis_title="Budget (€)",
        height=400,
    )
    return fig


@profiler_rerun("activites")
def app() -> None:
    """Interface principale du module Activites."""
    svc = _get_service()

    st.title("🎨 Activites Familiales")

    # Tabs avec deep linking URL
    TAB_LABELS = ["📱 Planning Semaine", "👶 Idees Activites", "💡 Budget"]
    tab_index = tabs_with_url(TAB_LABELS, param="tab")
    tabs = st.tabs(TAB_LABELS)

    # ═══════════════════════════════════════════════════════════
    # TAB 1: PLANNING SEMAINE
    # ═══════════════════════════════════════════════════════════
    if tab_index == 0:
        with tabs[0]:
            with error_boundary(titre="Erreur planning semaine"):
                st.header("📱 Planning de la Semaine")

                col1, col2 = st.columns([2, 1])

                with col1:
                    st.subheader("Activites Prevues")

                    try:
                        activites = get_activites_semaine()

                        if activites:
                            # Trier par date
                            activites_sorted = sorted(activites, key=lambda x: x["date"])

                            for act in activites_sorted:
                                with st.container(border=True):
                                    col_date, col_info = st.columns([1, 3])

                                    with col_date:
                                        from src.core.constants import JOURS_SEMAINE

                                        jour_idx = act["date"].weekday()
                                        jour = JOURS_SEMAINE[jour_idx]
                                        jour_num = act["date"].strftime("%d")
                                        st.write(f"**{jour}**")
                                        st.write(f"*{jour_num}*")

                                    with col_info:
                                        st.write(f"**{act['titre']}**")
                                        st.caption(f"{act['type']} • {act.get('lieu', 'TBD')}")
                                        if act.get("participants"):
                                            st.caption(f"📅 {', '.join(act['participants'])}")
                                        st.caption(f"💡 {act.get('cout_estime', 0):.2f}€")
                        else:
                            etat_vide(
                                "Aucune activité cette semaine", "📅", "Planifiez une activité !"
                            )

                    except Exception as e:
                        st.error(f"❌ Erreur chargement: {str(e)}")

                with col2:
                    st.subheader("➕ Ajouter Activite")

                    # Récupérer pré-remplissage depuis suggestion
                    prefill_titre = st.session_state.pop(_keys("prefill_titre"), "")
                    prefill_type = st.session_state.pop(_keys("prefill_type"), "parc")

                    with st.form("form_activite"):
                        titre = st.text_input("Nom", value=prefill_titre)
                        type_act = st.selectbox(
                            "Type",
                            _TYPES_ACTIVITES,
                            index=_TYPES_ACTIVITES.index(prefill_type)
                            if prefill_type in _TYPES_ACTIVITES
                            else 0,
                        )
                        date_act = st.date_input("Date")
                        duree = st.number_input("Duree (h)", 0.5, 8.0, 2.0)
                        lieu = st.text_input("Lieu")
                        cout = st.number_input("Coût estime (€)", 0.0, 500.0, 0.0)

                        if st.form_submit_button("✅ Ajouter", use_container_width=True):
                            if titre and type_act:
                                try:
                                    svc.ajouter_activite(
                                        titre, type_act, date_act, duree, lieu, ["Famille"], cout
                                    )
                                    st.success(f"✅ Activite '{titre}' creee!")
                                    clear_famille_cache()
                                    rerun()
                                except Exception as e:
                                    st.error(f"❌ Erreur ajout activite: {e}")

    # ═══════════════════════════════════════════════════════════
    # TAB 2: IDÉES ACTIVITÉS
    # ═══════════════════════════════════════════════════════════
    if tab_index == 1:
        with tabs[1]:
            with error_boundary(titre="Erreur idées activités"):
                st.header("💡 Idées d'Activités")

                st.subheader("Suggestions par type")

                col1, col2, col3 = st.columns(3)

                cols = [col1, col2, col3]
                type_keys = list(SUGGESTIONS_ACTIVITES.keys())

                for i, type_key in enumerate(type_keys[:3]):
                    with cols[i]:
                        emoji = (
                            "💰"
                            if type_key == "parc"
                            else "🧹"
                            if type_key == "musee"
                            else "📋"
                            if type_key == "eau"
                            else "🎯"
                            if type_key == "jeu_maison"
                            else "⚽"
                            if type_key == "sport"
                            else "🍽️"
                        )
                        title = type_key.replace("_", " ").title()

                        st.subheader(f"{emoji} {title}")
                        for suggestion in SUGGESTIONS_ACTIVITES[type_key]:
                            if st.button(
                                suggestion,
                                key=f"suggest_{type_key}_{suggestion}",
                                use_container_width=True,
                            ):
                                st.session_state[_keys("prefill_titre")] = suggestion
                                st.session_state[_keys("prefill_type")] = type_key
                                st.toast(f"✏️ '{suggestion}' pré-rempli dans le formulaire")
                                rerun()

                col4, col5, col6 = st.columns(3)
                cols2 = [col4, col5, col6]

                for i, type_key in enumerate(type_keys[3:]):
                    with cols2[i]:
                        emoji = (
                            "💰"
                            if type_key == "parc"
                            else "🧹"
                            if type_key == "musee"
                            else "📋"
                            if type_key == "eau"
                            else "🎯"
                            if type_key == "jeu_maison"
                            else "⚽"
                            if type_key == "sport"
                            else "🍽️"
                        )
                        title = type_key.replace("_", " ").title()

                        st.subheader(f"{emoji} {title}")
                        for suggestion in SUGGESTIONS_ACTIVITES[type_key]:
                            if st.button(
                                suggestion,
                                key=f"suggest_{type_key}_{suggestion}",
                                use_container_width=True,
                            ):
                                st.session_state[_keys("prefill_titre")] = suggestion
                                st.session_state[_keys("prefill_type")] = type_key
                                st.toast(f"✏️ '{suggestion}' pré-rempli dans le formulaire")
                                rerun()

    # ═══════════════════════════════════════════════════════════
    # TAB 3: BUDGET
    # ═══════════════════════════════════════════════════════════
    if tab_index == 2:
        with tabs[2]:
            with error_boundary(titre="Erreur budget activités"):
                st.header("💡 Budget Activites")

                # Stats
                col1, col2, col3 = st.columns(3)

                try:
                    budget_mois = get_budget_activites_mois()
                    budget_semaine = get_budget_par_period("week").get("Activites", 0)

                    with col1:
                        st.metric("💡 Ce mois", f"{budget_mois:.2f}€")
                    with col2:
                        st.metric("📊 Cette semaine", f"{budget_semaine:.2f}€")
                    with col3:
                        st.metric("🗑️ Budget moyen", f"{budget_mois / 4:.2f}€ par semaine")

                except Exception as e:
                    st.error(f"❌ Erreur budget: {str(e)}")

                st.divider()

                # Graphique timeline
                st.subheader("🗑️ Graphique Depenses")

                try:
                    activites_list = svc.lister_activites()

                    if activites_list:
                        # Creer DataFrame
                        data = []
                        for act in activites_list:
                            if act.date_prevue and act.date_prevue >= date.today() - timedelta(
                                days=30
                            ):
                                data.append(
                                    {
                                        "date": act.date_prevue,
                                        "titre": act.titre,
                                        "cout_estime": act.cout_estime or 0,
                                        "cout_reel": act.cout_reel or 0,
                                        "type": act.type_activite,
                                    }
                                )

                        if data:
                            # Graphique 1: Timeline (cached)
                            fig1 = _graphique_budget_timeline(data)
                            st.plotly_chart(fig1, width="stretch", key="activities_budget_timeline")

                            # Graphique 2: Par type d'activité (cached)
                            fig2 = _graphique_budget_par_type(data)
                            st.plotly_chart(fig2, width="stretch", key="activities_budget_by_type")
                        else:
                            etat_vide("Aucune activité sur 30 jours", "📊")
                    else:
                        etat_vide("Aucune activité sur 30 jours", "📊")

                except Exception as e:
                    st.error(f"❌ Erreur graphiques: {e}")
