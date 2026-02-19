"""
Graphiques Plotly pour le tableau de bord.

Fournit des graphiques interactifs:
- Répartition des repas (camembert)
- Inventaire par catégorie (barres)
"""

import logging

import plotly.graph_objects as go
import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)
def graphique_repartition_repas(planning_data: list[dict]) -> go.Figure | None:
    """
    Graphique en camembert de la répartition des repas par type.

    Args:
        planning_data: Liste des repas planifiés

    Returns:
        Figure Plotly ou None si pas de données
    """
    if not planning_data:
        return None

    # Compter par type
    types_count = {}
    for repas in planning_data:
        type_repas = repas.get("type_repas", "autre")
        types_count[type_repas] = types_count.get(type_repas, 0) + 1

    # Couleurs personnalisées
    couleurs = {
        "petit_déjeuner": "#FFB74D",
        "déjeuner": "#4CAF50",
        "dîner": "#2196F3",
        "goûter": "#E91E63",
    }

    labels = list(types_count.keys())
    values = list(types_count.values())
    colors = [couleurs.get(t, "#9E9E9E") for t in labels]

    # Labels français
    labels_fr = {
        "petit_déjeuner": "Petit-déjeuner",
        "déjeuner": "Déjeuner",
        "dîner": "Dîner",
        "goûter": "Goûter",
    }
    labels = [labels_fr.get(label, label.capitalize()) for label in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker_colors=colors,
                textinfo="label+percent",
                textposition="outside",
            )
        ]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=20),
        height=250,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )

    return fig


@st.cache_data(ttl=300)
def graphique_inventaire_categories(inventaire: list[dict]) -> go.Figure | None:
    """
    Graphique en barres horizontales du stock par catégorie.

    Args:
        inventaire: Liste des articles

    Returns:
        Figure Plotly
    """
    if not inventaire:
        return None

    # Grouper par catégorie
    categories = {}
    for article in inventaire:
        cat = article.get("categorie", "Autre")
        if cat not in categories:
            categories[cat] = {"total": 0, "bas": 0}
        categories[cat]["total"] += 1
        if article.get("statut") in ["critique", "sous_seuil"]:
            categories[cat]["bas"] += 1

    # Trier par total décroissant
    sorted_cats = sorted(categories.items(), key=lambda x: x[1]["total"], reverse=True)[:8]

    cat_names = [c[0] for c in sorted_cats]
    totaux = [c[1]["total"] for c in sorted_cats]
    bas = [c[1]["bas"] for c in sorted_cats]

    fig = go.Figure()

    # Barres stock normal
    fig.add_trace(
        go.Bar(
            y=cat_names,
            x=[t - b for t, b in zip(totaux, bas, strict=False)],
            name="Stock OK",
            orientation="h",
            marker_color="#4CAF50",
        )
    )

    # Barres stock bas
    fig.add_trace(
        go.Bar(
            y=cat_names,
            x=bas,
            name="Stock bas",
            orientation="h",
            marker_color="#FF5722",
        )
    )

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=100, r=20, t=40, b=20),
        height=280,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Articles",
    )

    return fig
