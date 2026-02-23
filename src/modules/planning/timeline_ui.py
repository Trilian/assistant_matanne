"""
Vue Timeline pour le planning.

Visualisation chronologique des événements avec graphique Plotly
interactif montrant les événements sur une timeline horizontale.
"""

from datetime import date, datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.constants import JOURS_SEMAINE
from src.core.date_utils import obtenir_debut_semaine
from src.modules._framework import error_boundary
from src.ui import etat_vide
from src.ui.tokens import Couleur

# Couleurs par type d'événement
COULEURS_TYPES = {
    "rdv": Couleur.DANGER,
    "activité": Couleur.SUCCESS,
    "fête": Couleur.WARNING,
    "repas": Couleur.INFO,
    "routine": Couleur.ACCENT,
    "autre": Couleur.TEXT_SECONDARY,
}

# Accesseur lazy pour le service (singleton)
_service = None


def _get_service():
    global _service
    if _service is None:
        from src.services.famille.calendrier_planning import (
            obtenir_service_calendrier_planning,
        )

        _service = obtenir_service_calendrier_planning()
    return _service


def charger_events_periode(date_debut: date, date_fin: date) -> list[dict]:
    """Charge tous les événements pour une période donnée.

    Délègue au ServiceCalendrierPlanning.

    Returns:
        Liste de dicts avec {titre, date_debut, date_fin, type, couleur}
    """
    return _get_service().charger_events_periode(date_debut, date_fin)


def creer_timeline_jour(events: list[dict], jour: date) -> go.Figure:
    """
    Crée un graphique timeline pour une journée.

    Axe Y = heures de la journée, barres horizontales = événements
    """
    # Filtrer les events du jour
    events_jour = [e for e in events if e["date_debut"].date() == jour]

    if not events_jour:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucun événement ce jour",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=200)
        return fig

    # Préparer les données pour le graphique
    y_positions = []
    colors = []
    texts = []
    hovers = []

    for i, event in enumerate(events_jour):
        y_positions.append(i)
        colors.append(event.get("couleur", "#757575"))
        texts.append(event["titre"][:30])
        lieu_str = f"<br>📍 {event['lieu']}" if event.get("lieu") else ""
        hovers.append(
            f"<b>{event['titre']}</b><br>"
            f"⏰ {event['date_debut'].strftime('%H:%M')} - {event['date_fin'].strftime('%H:%M')}"
            f"{lieu_str}"
        )

    fig = go.Figure()

    for i, event in enumerate(events_jour):
        debut_h = event["date_debut"].hour + event["date_debut"].minute / 60
        fin_h = event["date_fin"].hour + event["date_fin"].minute / 60

        fig.add_trace(
            go.Bar(
                x=[fin_h - debut_h],
                y=[event["titre"][:25]],
                base=[debut_h],
                orientation="h",
                marker_color=event.get("couleur", "#757575"),
                text=f"{event['date_debut'].strftime('%H:%M')}",
                textposition="inside",
                hovertemplate=hovers[i] + "<extra></extra>",
                showlegend=False,
            )
        )

    fig.update_layout(
        title=f"📅 {JOURS_SEMAINE[jour.weekday()]} {jour.strftime('%d/%m/%Y')}",
        xaxis=dict(
            title="Heure",
            range=[6, 23],
            tickvals=list(range(6, 24, 2)),
            ticktext=[f"{h}h" for h in range(6, 24, 2)],
            gridcolor="rgba(0,0,0,0.1)",
        ),
        yaxis=dict(
            title="",
            autorange="reversed",
        ),
        height=max(200, 60 * len(events_jour)),
        margin=dict(l=10, r=10, t=60, b=40),
        bargap=0.3,
        plot_bgcolor="white",
    )

    return fig


def creer_timeline_semaine(events: list[dict], date_lundi: date) -> go.Figure:
    """
    Crée un graphique timeline Gantt pour une semaine entière.
    """
    import pandas as pd

    # Filtrer les events de la semaine
    date_fin = date_lundi + timedelta(days=6)
    events_semaine = [e for e in events if date_lundi <= e["date_debut"].date() <= date_fin]

    if not events_semaine:
        fig = go.Figure()
        fig.add_annotation(
            text="Aucun événement cette semaine",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray"),
        )
        fig.update_layout(height=200)
        return fig

    # Préparer les données pour Plotly Express timeline
    df_data = []
    for event in events_semaine:
        jour = JOURS_SEMAINE[event["date_debut"].weekday()]
        df_data.append(
            {
                "Task": event["titre"][:30],
                "Start": event["date_debut"],
                "Finish": event["date_fin"],
                "Type": event["type"],
                "Jour": jour,
                "Couleur": event.get("couleur", "#757575"),
            }
        )

    df = pd.DataFrame(df_data)

    # Créer le Gantt chart
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Jour",
        color="Type",
        hover_name="Task",
        color_discrete_map=COULEURS_TYPES,
        category_orders={"Jour": JOURS_SEMAINE},
    )

    fig.update_layout(
        title=f"📅 Semaine du {date_lundi.strftime('%d/%m')} au {date_fin.strftime('%d/%m/%Y')}",
        xaxis_title="",
        yaxis_title="",
        height=400,
        margin=dict(l=10, r=10, t=60, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )

    # Ajuster le format de l'axe X pour afficher les heures
    fig.update_xaxes(
        tickformat="%a %H:%M",
        dtick=86400000 / 4,  # Toutes les 6h
    )

    return fig


def afficher_legende():
    """Affiche la légende des types d'événements."""
    cols = st.columns(len(COULEURS_TYPES))
    for i, (type_event, couleur) in enumerate(COULEURS_TYPES.items()):
        with cols[i]:
            st.markdown(
                f'<div style="display:flex;align-items:center;">'
                f'<span style="background:{couleur};width:12px;height:12px;'
                f'border-radius:50%;margin-right:6px;"></span>'
                f"<small>{type_event.title()}</small></div>",
                unsafe_allow_html=True,
            )


def app():
    """Point d'entrée du module timeline."""
    st.title("📊 Vue Timeline")
    st.caption("Visualisation chronologique de vos événements")

    with error_boundary("timeline_ui"):
        # Sélection de la période
        col1, col2 = st.columns([1, 2])

        with col1:
            vue_mode = st.radio(
                "Mode de vue",
                ["📅 Jour", "📆 Semaine"],
                horizontal=True,
            )

        with col2:
            date_ref = st.date_input("Date de référence", value=date.today())

        st.divider()

        # Légende
        afficher_legende()

        st.divider()

        # Charger les événements
        if vue_mode == "📅 Jour":
            # Vue journalière
            events = charger_events_periode(date_ref, date_ref)
            fig = creer_timeline_jour(events, date_ref)
            st.plotly_chart(fig, use_container_width=True)

            # Stats du jour
            if events:
                events_jour = [e for e in events if e["date_debut"].date() == date_ref]
                with st.expander("📊 Statistiques du jour", expanded=False):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Événements", len(events_jour))
                    with col2:
                        types = set(e["type"] for e in events_jour)
                        st.metric("Types", len(types))
                    with col3:
                        duree_totale = sum(
                            (e["date_fin"] - e["date_debut"]).seconds / 3600 for e in events_jour
                        )
                        st.metric("Durée totale", f"{duree_totale:.1f}h")

        else:
            # Vue semaine
            lundi = obtenir_debut_semaine(date_ref)
            dimanche = lundi + timedelta(days=6)

            events = charger_events_periode(lundi, dimanche)
            fig = creer_timeline_semaine(events, lundi)
            st.plotly_chart(fig, use_container_width=True)

            # Stats de la semaine
            if events:
                events_semaine = [e for e in events if lundi <= e["date_debut"].date() <= dimanche]
                with st.expander("📊 Statistiques de la semaine", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total événements", len(events_semaine))
                    with col2:
                        # Jour le plus chargé
                        from collections import Counter

                        jours = Counter(e["date_debut"].weekday() for e in events_semaine)
                        if jours:
                            jour_max = max(jours, key=jours.get)
                            st.metric("Jour chargé", JOURS_SEMAINE[jour_max][:3])
                    with col3:
                        types = Counter(e["type"] for e in events_semaine)
                        if types:
                            type_max = max(types, key=types.get)
                            st.metric("Type dominant", type_max.title())
                    with col4:
                        duree_totale = sum(
                            (e["date_fin"] - e["date_debut"]).seconds / 3600 for e in events_semaine
                        )
                        st.metric("Durée totale", f"{duree_totale:.0f}h")

        # Liste détaillée
        st.divider()
        with st.expander("📋 Liste détaillée", expanded=False):
            if vue_mode == "📅 Jour":
                events_afficher = [e for e in events if e["date_debut"].date() == date_ref]
            else:
                lundi = obtenir_debut_semaine(date_ref)
                dimanche = lundi + timedelta(days=6)
                events_afficher = [e for e in events if lundi <= e["date_debut"].date() <= dimanche]

            if not events_afficher:
                etat_vide("Aucun événement", "📅")
            else:
                events_afficher.sort(key=lambda e: e["date_debut"])
                for event in events_afficher:
                    jour = JOURS_SEMAINE[event["date_debut"].weekday()][:3]
                    heure = event["date_debut"].strftime("%H:%M")
                    lieu = f" • 📍 {event['lieu']}" if event.get("lieu") else ""
                    couleur = event.get("couleur", "#757575")

                    st.markdown(
                        f'<div style="padding:8px;margin:4px 0;background:#f8f9fa;'
                        f'border-left:4px solid {couleur};border-radius:4px;">'
                        f"<strong>{jour} {heure}</strong> - {event['titre']}"
                        f'<span style="color:#666;">{lieu}</span></div>',
                        unsafe_allow_html=True,
                    )


__all__ = ["app"]
