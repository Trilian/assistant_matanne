"""
Dashboard drill-down Plotly — Graphiques interactifs avec on_select.

Fournit des graphiques Plotly qui réagissent aux clics utilisateur
pour afficher des détails contextuels (drill-down).

Graphiques disponibles:
- Budget par catégorie → clic → détails des dépenses
- Fréquence recettes → clic → fiche recette
- Heatmap activités → clic → détails du jour
- Répartition inventaire → clic → articles catégorie

Usage:
    from src.ui.components.plotly_drilldown import (
        graphique_budget_drilldown,
        graphique_recettes_drilldown,
        graphique_activites_heatmap,
        graphique_inventaire_drilldown,
    )
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.registry import composant_ui

logger = logging.getLogger(__name__)

_keys = KeyNamespace("drilldown")


# ═══════════════════════════════════════════════════════════
# BUDGET DRILL-DOWN
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "charts",
    exemple="graphique_budget_drilldown(depenses)",
    tags=("plotly", "drilldown", "budget"),
)
def graphique_budget_drilldown(
    depenses: list[dict[str, Any]],
    *,
    key_suffix: str = "",
) -> None:
    """
    Graphique budget par catégorie avec drill-down on_select.

    Cliquer sur une catégorie affiche le détail des dépenses
    de cette catégorie.

    Args:
        depenses: Liste de dicts avec 'categorie', 'montant', 'description', 'date'
        key_suffix: Suffixe pour la clé du widget
    """
    if not depenses:
        st.info("💰 Aucune dépense à afficher.")
        return

    # Agréger par catégorie
    par_categorie: dict[str, float] = {}
    for dep in depenses:
        cat = dep.get("categorie", "Autre")
        montant = float(dep.get("montant", 0))
        par_categorie[cat] = par_categorie.get(cat, 0) + montant

    categories = list(par_categorie.keys())
    montants = list(par_categorie.values())

    # Couleurs par catégorie
    couleurs = px.colors.qualitative.Set2[: len(categories)]

    fig = go.Figure(
        data=[
            go.Bar(
                x=categories,
                y=montants,
                marker_color=couleurs,
                text=[f"{m:.0f}€" for m in montants],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Montant: %{y:.2f}€<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="💰 Dépenses par Catégorie (cliquez pour détails)",
        xaxis_title="Catégorie",
        yaxis_title="Montant (€)",
        height=400,
        showlegend=False,
        clickmode="event+select",
    )

    # Afficher avec on_select
    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=_keys(f"budget_drilldown{key_suffix}"),
        on_select="rerun",
    )

    # Traiter la sélection
    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        categorie_selectionnee = categories[point["point_index"]]

        st.markdown(f"### 📋 Détails — {categorie_selectionnee}")

        # Filtrer les dépenses de cette catégorie
        depenses_cat = [d for d in depenses if d.get("categorie") == categorie_selectionnee]

        if depenses_cat:
            for dep in sorted(
                depenses_cat,
                key=lambda d: d.get("date", ""),
                reverse=True,
            ):
                col1, col2, col3 = st.columns([2, 1, 2])
                with col1:
                    st.write(f"📅 {dep.get('date', 'N/A')}")
                with col2:
                    st.write(f"**{float(dep.get('montant', 0)):.2f}€**")
                with col3:
                    st.write(dep.get("description", ""))

            total_cat = sum(float(d.get("montant", 0)) for d in depenses_cat)
            st.markdown(f"**Total {categorie_selectionnee}: {total_cat:.2f}€**")


# ═══════════════════════════════════════════════════════════
# RECETTES DRILL-DOWN
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "charts",
    exemple="graphique_recettes_drilldown(recettes_freq)",
    tags=("plotly", "drilldown", "recettes"),
)
def graphique_recettes_drilldown(
    recettes_freq: list[dict[str, Any]],
    *,
    key_suffix: str = "",
) -> str | None:
    """
    Graphique de fréquence des recettes avec drill-down.

    Cliquer sur une recette affiche ses détails et permet
    de naviguer vers la fiche recette.

    Args:
        recettes_freq: Liste de dicts avec 'nom', 'count', 'id', 'categorie'
        key_suffix: Suffixe pour la clé du widget

    Returns:
        Nom de la recette sélectionnée ou None
    """
    if not recettes_freq:
        st.info("🍽 Aucune recette à afficher.")
        return None

    # Top 15 recettes
    top_recettes = sorted(recettes_freq, key=lambda r: r.get("count", 0), reverse=True)[:15]

    noms = [r.get("nom", "?") for r in top_recettes]
    counts = [r.get("count", 0) for r in top_recettes]

    fig = go.Figure(
        data=[
            go.Bar(
                y=noms,
                x=counts,
                orientation="h",
                marker_color=px.colors.sequential.Tealgrn[: len(noms)],
                text=counts,
                textposition="auto",
                hovertemplate="<b>%{y}</b><br>Préparée %{x} fois<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="🍽️ Fréquence des Recettes (cliquez pour détails)",
        xaxis_title="Nombre de préparations",
        height=max(300, len(noms) * 30),
        showlegend=False,
        clickmode="event+select",
        yaxis=dict(autorange="reversed"),
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=_keys(f"recettes_drilldown{key_suffix}"),
        on_select="rerun",
    )

    # Traiter la sélection
    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        idx = point["point_index"]
        recette = top_recettes[idx]
        nom = recette.get("nom", "?")

        st.markdown(f"### 🍽️ {nom}")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Préparations", recette.get("count", 0))
        with col2:
            st.write(f"**Catégorie:** {recette.get('categorie', 'N/A')}")
        with col3:
            recette_id = recette.get("id")
            if recette_id:
                if st.button(
                    "📖 Voir la recette",
                    key=_keys(f"voir_recette_{recette_id}{key_suffix}"),
                ):
                    from src.core.state import GestionnaireEtat

                    GestionnaireEtat.definir_recette_visualisation(recette_id)
                    GestionnaireEtat.naviguer_vers("cuisine.recettes")

        return nom

    return None


# ═══════════════════════════════════════════════════════════
# ACTIVITÉS HEATMAP DRILL-DOWN
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "charts",
    exemple="graphique_activites_heatmap(activites)",
    tags=("plotly", "drilldown", "heatmap"),
)
def graphique_activites_heatmap(
    activites: list[dict[str, Any]],
    *,
    nb_semaines: int = 4,
    key_suffix: str = "",
) -> dict | None:
    """
    Heatmap des activités avec drill-down par jour.

    Cliquer sur une cellule affiche les détails du jour sélectionné.

    Args:
        activites: Liste de dicts avec 'date', 'nom', 'duree_minutes'
        nb_semaines: Nombre de semaines à afficher
        key_suffix: Suffixe clé widget

    Returns:
        Dict du jour sélectionné ou None
    """
    if not activites:
        st.info("🎯 Aucune activité à afficher.")
        return None

    # Construire la matrice heatmap (7 jours x N semaines)
    today = date.today()
    debut = today - timedelta(days=today.weekday() + (nb_semaines - 1) * 7)

    # Compter les activités par jour
    par_jour: dict[date, int] = {}
    for act in activites:
        d = act.get("date")
        if isinstance(d, str):
            from datetime import datetime as dt

            try:
                d = dt.strptime(d, "%Y-%m-%d").date()
            except ValueError:
                continue
        if isinstance(d, date):
            par_jour[d] = par_jour.get(d, 0) + 1

    # Construire les données pour le heatmap
    jours_names = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
    semaines_labels = []
    z_data = []
    dates_map: dict[tuple[int, int], date] = {}  # (semaine_idx, jour_idx) -> date

    for sem_idx in range(nb_semaines):
        semaine_debut = debut + timedelta(weeks=sem_idx)
        semaines_labels.append(semaine_debut.strftime("S%W"))
        row = []
        for jour_idx in range(7):
            d = semaine_debut + timedelta(days=jour_idx)
            count = par_jour.get(d, 0)
            row.append(count)
            dates_map[(sem_idx, jour_idx)] = d
        z_data.append(row)

    fig = go.Figure(
        data=go.Heatmap(
            z=z_data,
            x=jours_names,
            y=semaines_labels,
            colorscale="Greens",
            hovertemplate="<b>%{y} %{x}</b><br>%{z} activité(s)<extra></extra>",
            showscale=True,
            colorbar=dict(title="Activités"),
        )
    )

    fig.update_layout(
        title="🗓️ Activités par jour (cliquez pour détails)",
        height=max(200, nb_semaines * 50 + 100),
        clickmode="event+select",
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=_keys(f"heatmap_activites{key_suffix}"),
        on_select="rerun",
    )

    # Traiter la sélection
    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        sem_idx = point.get("point_index", [0, 0])
        # point_index contains z, x, y indices depending on trace type
        x_idx = point.get("x", 0)
        y_idx = point.get("y", 0)

        # Trouver la date correspondante
        try:
            jour_idx = jours_names.index(x_idx) if isinstance(x_idx, str) else int(x_idx)
            sem_label_idx = semaines_labels.index(y_idx) if isinstance(y_idx, str) else int(y_idx)
            date_select = dates_map.get((sem_label_idx, jour_idx))
        except (ValueError, IndexError):
            date_select = None

        if date_select:
            st.markdown(f"### 📅 {date_select.strftime('%A %d %B %Y')}")

            # Filtrer les activités du jour
            activites_jour = [a for a in activites if _extraire_date(a.get("date")) == date_select]

            if activites_jour:
                for act in activites_jour:
                    duree = act.get("duree_minutes", 0)
                    st.markdown(
                        f"- **{act.get('nom', 'Activité')}** ({duree} min)"
                        if duree
                        else f"- **{act.get('nom', 'Activité')}**"
                    )
            else:
                st.info("Aucune activité ce jour")

            return {"date": date_select, "activites": activites_jour}

    return None


# ═══════════════════════════════════════════════════════════
# INVENTAIRE DRILL-DOWN (PIE)
# ═══════════════════════════════════════════════════════════


@composant_ui(
    "charts",
    exemple="graphique_inventaire_drilldown(inventaire)",
    tags=("plotly", "drilldown", "inventaire"),
)
def graphique_inventaire_drilldown(
    inventaire: list[dict[str, Any]],
    *,
    key_suffix: str = "",
) -> None:
    """
    Graphique stock par catégorie avec drill-down.

    Cliquer sur un secteur affiche les articles de cette catégorie.

    Args:
        inventaire: Liste de dicts d'articles
        key_suffix: Suffixe clé widget
    """
    if not inventaire:
        st.info("📦 Aucun article en stock.")
        return

    # Agréger par catégorie
    par_categorie: dict[str, list] = {}
    for article in inventaire:
        cat = article.get("ingredient_categorie", "Autre")
        par_categorie.setdefault(cat, []).append(article)

    categories = list(par_categorie.keys())
    counts = [len(articles) for articles in par_categorie.values()]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=categories,
                values=counts,
                hole=0.4,
                textinfo="label+value",
                hovertemplate="<b>%{label}</b><br>%{value} articles<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title="📦 Stock par Catégorie (cliquez pour détails)",
        height=400,
        clickmode="event+select",
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=_keys(f"inventaire_drilldown{key_suffix}"),
        on_select="rerun",
    )

    # Traiter la sélection
    if event and event.selection and event.selection.points:
        point = event.selection.points[0]
        idx = point["point_index"]
        categorie = categories[idx]

        st.markdown(f"### 📦 Articles — {categorie}")

        articles_cat = par_categorie.get(categorie, [])
        if articles_cat:
            for article in sorted(
                articles_cat,
                key=lambda a: a.get("quantite", 0),
            ):
                statut_icon = {
                    "critique": "❌",
                    "stock_bas": "⚠️",
                    "peremption_proche": "⏰",
                    "ok": "✅",
                }.get(article.get("statut", "ok"), "❓")

                qte = article.get("quantite", 0)
                unite = article.get("unite", "")
                nom = article.get("ingredient_nom", "?")

                st.markdown(
                    f"- {statut_icon} **{nom}** — {qte:.1f} {unite} "
                    f"({article.get('emplacement', '')})"
                )

            st.caption(f"Total: {len(articles_cat)} article(s) dans {categorie}")


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def _extraire_date(val: Any) -> date | None:
    """Extrait une date depuis une valeur string ou date."""
    if isinstance(val, date):
        return val
    if isinstance(val, str):
        from datetime import datetime as dt

        try:
            return dt.strptime(val, "%Y-%m-%d").date()
        except ValueError:
            return None
    return None


__all__ = [
    "graphique_budget_drilldown",
    "graphique_recettes_drilldown",
    "graphique_activites_heatmap",
    "graphique_inventaire_drilldown",
]
