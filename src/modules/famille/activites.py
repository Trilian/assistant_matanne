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
from src.modules._framework import error_boundary
from src.modules.famille.utils import (
    clear_famille_cache,
    get_activites_semaine,
    get_budget_activites_mois,
    get_budget_par_period,
)
from src.ui import etat_vide
from src.ui.state.url import tabs_with_url

if TYPE_CHECKING:
    from src.services.famille.activites import ServiceActivites


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
    with tabs[0]:
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
                                jour = act["date"].strftime("%a")
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
                    etat_vide("Aucune activité cette semaine", "📅", "Planifiez une activité !")

            except Exception as e:
                st.error(f"❌ Erreur chargement: {str(e)}")

        with col2:
            st.subheader("➕ Ajouter Activite")

            # Récupérer pré-remplissage depuis suggestion
            prefill_titre = st.session_state.pop("activite_prefill_titre", "")
            prefill_type = st.session_state.pop("activite_prefill_type", "parc")

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
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur ajout activite: {e}")

    # ═══════════════════════════════════════════════════════════
    # TAB 2: IDÉES ACTIVITÉS
    # ═══════════════════════════════════════════════════════════
    with tabs[1]:
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
                        suggestion, key=f"suggest_{type_key}_{suggestion}", use_container_width=True
                    ):
                        st.session_state["activite_prefill_titre"] = suggestion
                        st.session_state["activite_prefill_type"] = type_key
                        st.toast(f"✏️ '{suggestion}' pré-rempli dans le formulaire")
                        st.rerun()

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
                        suggestion, key=f"suggest_{type_key}_{suggestion}", use_container_width=True
                    ):
                        st.session_state["activite_prefill_titre"] = suggestion
                        st.session_state["activite_prefill_type"] = type_key
                        st.toast(f"✏️ '{suggestion}' pré-rempli dans le formulaire")
                        st.rerun()

    # ═══════════════════════════════════════════════════════════
    # TAB 3: BUDGET
    # ═══════════════════════════════════════════════════════════
    with tabs[2]:
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
                    if act.date_prevue and act.date_prevue >= date.today() - timedelta(days=30):
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
                    df = pd.DataFrame(data)
                    df["date"] = pd.to_datetime(df["date"])

                    # Graphique 1: Timeline
                    fig1 = go.Figure()
                    fig1.add_trace(
                        go.Scatter(
                            x=df["date"],
                            y=df["cout_estime"],
                            mode="lines+markers",
                            name="Coût estime",
                            line_color="blue",
                        )
                    )
                    fig1.add_trace(
                        go.Scatter(
                            x=df["date"],
                            y=df["cout_reel"],
                            mode="lines+markers",
                            name="Coût reel",
                            line_color="red",
                        )
                    )

                    fig1.update_layout(
                        title="Depenses par Date",
                        xaxis_title="Date",
                        yaxis_title="Montant (€)",
                        height=400,
                        hovermode="x unified",
                    )
                    st.plotly_chart(fig1, width="stretch", key="activities_budget_timeline")

                    # Graphique 2: Par type d'activite
                    type_budget = df.groupby("type")["cout_estime"].sum().reset_index()
                    type_budget.columns = ["Type", "Budget"]

                    fig2 = go.Figure(
                        data=[
                            go.Bar(
                                x=type_budget["Type"],
                                y=type_budget["Budget"],
                                marker_color="lightblue",
                            )
                        ]
                    )
                    fig2.update_layout(
                        title="Budget par Type d'Activite",
                        xaxis_title="Type",
                        yaxis_title="Budget (€)",
                        height=400,
                    )
                    st.plotly_chart(fig2, width="stretch", key="activities_budget_by_type")
                else:
                    etat_vide("Aucune activité sur 30 jours", "📊")
            else:
                etat_vide("Aucune activité sur 30 jours", "📊")

        except Exception as e:
            st.error(f"❌ Erreur graphiques: {e}")
