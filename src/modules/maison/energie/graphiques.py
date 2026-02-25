"""
Graphiques Plotly pour le module Énergie.
"""

from datetime import date

import plotly.graph_objects as go
import streamlit as st

from .constants import ENERGIES
from .data import charger_historique_energie, get_stats_energie


@st.cache_data(ttl=300)
def graphique_evolution(type_energie: str, afficher_conso: bool = True) -> go.Figure:
    """Crée un graphique d'évolution des consommations.

    Args:
        type_energie: Type d'énergie.
        afficher_conso: Afficher la consommation en plus du montant.

    Returns:
        Figure Plotly.
    """
    historique = charger_historique_energie(type_energie)
    labels = [h["label"] for h in historique]
    montants = [h["montant"] or 0 for h in historique]

    config = ENERGIES.get(type_energie, {})
    couleur = config.get("couleur", "#333")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=labels,
            y=montants,
            mode="lines+markers",
            name="Montant (€)",
            line={"color": couleur},
        )
    )

    if afficher_conso:
        consos = [h["consommation"] or 0 for h in historique]
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=consos,
                mode="lines+markers",
                name=f"Consommation ({config.get('unite', '')})",
                yaxis="y2",
            )
        )
        fig.update_layout(
            yaxis2={"title": config.get("unite", ""), "overlaying": "y", "side": "right"}
        )

    fig.update_layout(
        title=f"Évolution {config.get('label', type_energie)}",
        xaxis_title="Mois",
        yaxis_title="€",
    )

    return fig


@st.cache_data(ttl=300)
def graphique_comparaison_annees(type_energie: str) -> go.Figure:
    """Crée un graphique de comparaison N vs N-1.

    Args:
        type_energie: Type d'énergie.

    Returns:
        Figure Plotly.
    """
    historique = charger_historique_energie(type_energie, nb_mois=24)
    config = ENERGIES.get(type_energie, {})

    annee_courante = date.today().year
    donnees_n = [h for h in historique if h["annee"] == annee_courante]
    donnees_n1 = [h for h in historique if h["annee"] == annee_courante - 1]

    fig = go.Figure()

    if donnees_n:
        fig.add_trace(
            go.Bar(
                x=[h["label"] for h in donnees_n],
                y=[h["montant"] or 0 for h in donnees_n],
                name=str(annee_courante),
            )
        )

    if donnees_n1:
        fig.add_trace(
            go.Bar(
                x=[h["label"] for h in donnees_n1],
                y=[h["montant"] or 0 for h in donnees_n1],
                name=str(annee_courante - 1),
            )
        )

    fig.update_layout(
        title=f"Comparaison {config.get('label', type_energie)} — {annee_courante} vs {annee_courante - 1}",
        barmode="group",
    )

    return fig


@st.cache_data(ttl=300)
def graphique_repartition() -> go.Figure:
    """Crée un graphique de répartition des coûts par type d'énergie.

    Returns:
        Figure Plotly (camembert).
    """
    labels = []
    values = []
    colors = []

    for type_id, config in ENERGIES.items():
        stats = get_stats_energie(type_id)
        if stats["total_annuel"] > 0:
            labels.append(config["label"])
            values.append(stats["total_annuel"])
            colors.append(config["couleur"])

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker={"colors": colors},
                textinfo="label+percent",
            )
        ]
    )
    fig.update_layout(title="Répartition des coûts énergétiques")

    return fig
