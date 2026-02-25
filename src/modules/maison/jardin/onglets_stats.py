"""Jardin - Onglets statistiques, autonomie et graphiques.

Extrait de onglets.py (Phase 4 Audit, item 18 — split >500 LOC).
"""

import logging
from datetime import datetime

import streamlit as st

from src.ui.fragments import cached_fragment, ui_fragment

from .data import charger_catalogue_plantes
from .logic import (
    calculer_autonomie,
    calculer_stats_jardin,
    calculer_streak_jardin,
    generer_planning_jardin,
    generer_previsions_recoltes,
    generer_taches_jardin,
    obtenir_badges_jardin,
)
from .ui import (
    afficher_badges_jardin,
    afficher_planning_jardin_ui,
    afficher_previsions_recoltes_ui,
    afficher_score_jardin_gamifie,
    afficher_tache,
)

# Import optionnel Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go

    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

logger = logging.getLogger(__name__)


@ui_fragment
def onglet_taches(mes_plantes: list[dict], meteo: dict):
    """Onglet des tâches automatiques."""
    st.subheader("🎯 Tâches du jour")

    taches = generer_taches_jardin(mes_plantes, meteo)

    if not taches:
        st.success("✨ **Rien à faire aujourd'hui !** Votre jardin est à jour.")
        st.info(
            "Les tâches apparaîtront automatiquement selon le calendrier, la météo et vos plantations."
        )
        return

    # Résumé
    urgentes = len([t for t in taches if t["priorite"] in ["urgente", "haute"]])
    temps_total = sum(t["duree_min"] for t in taches)

    col1, col2, col3 = st.columns(3)
    col1.metric("Tâches", len(taches))
    col2.metric("Urgentes", urgentes, delta=None if urgentes == 0 else "⚠️")
    col3.metric("Temps estimé", f"{temps_total} min")

    st.divider()

    # Afficher les tâches
    for i, tache in enumerate(taches):
        done = afficher_tache(tache, f"tache_{i}")
        if done:
            st.toast(f"✅ {tache['titre']} accompli !")
            # Sauvegarder en session_state pour historique
            if "historique_jardin" not in st.session_state:
                st.session_state.historique_jardin = []
            st.session_state.historique_jardin.append(
                {
                    "titre": tache["titre"],
                    "date": datetime.now().isoformat(),
                    "duree_min": tache["duree_min"],
                    "categorie": tache.get("categorie", "autre"),
                }
            )


@cached_fragment(ttl=300)
def onglet_autonomie(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet objectif autonomie gamifié avec badges."""
    st.subheader("🎯 Objectif Autonomie Alimentaire")

    autonomie = calculer_autonomie(mes_plantes, recoltes)
    stats = calculer_stats_jardin(mes_plantes, recoltes)
    badges_obtenus = obtenir_badges_jardin(stats)
    streak = calculer_streak_jardin(recoltes)

    col1, col2 = st.columns([1, 2])

    with col1:
        afficher_score_jardin_gamifie(autonomie, streak)

    with col2:
        # Stats gamifiées
        m1, m2, m3 = st.columns(3)
        m1.metric("Plantes", stats.get("nb_plantes", 0), help="Plantes cultivées")
        m2.metric("Variétés", stats.get("varietes_uniques", 0), help="Diversité du potager")
        m3.metric("Récoltes", f"{stats.get('production_kg', 0)} kg", help="Production totale")

        # Prévisions
        previsions = generer_previsions_recoltes(mes_plantes)
        if previsions:
            afficher_previsions_recoltes_ui(previsions)

    st.divider()

    # Badges collection
    afficher_badges_jardin(badges_obtenus, stats)

    st.divider()

    # Par catégorie
    st.markdown("### Par catégorie")

    for cat, data in autonomie.get("par_categorie", {}).items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.write(f"**{cat.capitalize()}**")
        with col2:
            st.progress(
                data["couverture"] / 100,
                text=f"{data['couverture']}% • {data['prevu']}/{data['besoin']} kg",
            )


@cached_fragment(ttl=300)  # Cache 5 min (graphiques Plotly lourds)
def onglet_graphiques(mes_plantes: list[dict], recoltes: list[dict]):
    """Onglet graphiques Plotly avec visualisations interactives."""
    st.subheader("📈 Graphiques & Analyses")

    if not HAS_PLOTLY:
        st.warning("📦 Plotly non installé. `pip install plotly` pour les graphiques interactifs.")
        return

    if not recoltes and not mes_plantes:
        st.info("📊 Les graphiques apparaîtront avec vos premières plantes et récoltes.")
        return

    # Tab internes
    g1, g2, g3 = st.tabs(["🥕 Récoltes", "🌱 Plantations", "📅 Planning"])

    with g1:
        st.markdown("### Évolution des récoltes")

        if recoltes:
            catalogue = charger_catalogue_plantes()

            # Par mois
            par_mois = {}
            for r in recoltes:
                date_str = r.get("date", "")
                if date_str:
                    try:
                        d = datetime.fromisoformat(date_str).date()
                        mois_key = d.strftime("%Y-%m")
                        par_mois[mois_key] = par_mois.get(mois_key, 0) + r.get("quantite_kg", 0)
                    except Exception:
                        pass

            if par_mois:
                mois_sorted = sorted(par_mois.keys())
                mois_labels = [datetime.strptime(m, "%Y-%m").strftime("%b %Y") for m in mois_sorted]
                quantites = [par_mois[m] for m in mois_sorted]

                fig = go.Figure()
                fig.add_trace(
                    go.Bar(
                        x=mois_labels,
                        y=quantites,
                        marker_color="#27ae60",
                        text=[f"{q:.1f}kg" for q in quantites],
                        textposition="outside",
                    )
                )
                fig.update_layout(
                    title="Récoltes par mois (kg)", template="plotly_dark", height=350
                )
                st.plotly_chart(fig, use_container_width=True)

            # Par plante
            st.markdown("### Répartition par légume")
            par_plante = {}
            for r in recoltes:
                plante_id = r.get("plante_id", "inconnu")
                plante_nom = catalogue.get("plantes", {}).get(plante_id, {}).get("nom", plante_id)
                par_plante[plante_nom] = par_plante.get(plante_nom, 0) + r.get("quantite_kg", 0)

            if par_plante:
                fig = px.pie(
                    values=list(par_plante.values()),
                    names=list(par_plante.keys()),
                    title="Répartition des récoltes",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                    hole=0.4,
                )
                fig.update_layout(template="plotly_dark", height=350)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enregistrez vos récoltes pour voir leur évolution ici.")

    with g2:
        st.markdown("### Mes plantations")

        if mes_plantes:
            catalogue = charger_catalogue_plantes()

            # Par catégorie
            par_cat = {}
            for p in mes_plantes:
                plante_id = p.get("plante_id")
                cat = catalogue.get("plantes", {}).get(plante_id, {}).get("categorie", "Autre")
                par_cat[cat] = par_cat.get(cat, 0) + 1

            fig = px.bar(
                x=list(par_cat.keys()),
                y=list(par_cat.values()),
                color=list(par_cat.keys()),
                labels={"x": "Catégorie", "y": "Nombre"},
                title="Répartition des cultures",
            )
            fig.update_layout(template="plotly_dark", height=350, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Surface par plante
            st.markdown("### Surface cultivée")
            surfaces = {}
            for p in mes_plantes:
                plante_id = p.get("plante_id")
                nom = catalogue.get("plantes", {}).get(plante_id, {}).get("nom", plante_id)
                surfaces[nom] = surfaces.get(nom, 0) + p.get("surface_m2", 0)

            if surfaces:
                fig = px.bar(
                    x=list(surfaces.values()),
                    y=list(surfaces.keys()),
                    orientation="h",
                    color=list(surfaces.values()),
                    color_continuous_scale=["#c6f6d5", "#27ae60"],
                    labels={"x": "Surface (m²)", "y": "Plante"},
                )
                fig.update_layout(template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ajoutez des plantes pour voir les statistiques.")

    with g3:
        st.markdown("### Planning prévisionnel")

        planning = generer_planning_jardin(mes_plantes, horizon_mois=6)

        if planning:
            afficher_planning_jardin_ui(planning)
        else:
            st.success("✨ Aucune activité prévue dans les 6 prochains mois.")
