"""
Dashboard - Statistiques et graphiques
Visualisations de données pour le tableau de bord principal
"""

import logging

import streamlit as st

from src.ui.fragments import auto_refresh, cached_fragment
from src.ui.keys import KeyNamespace

_keys = KeyNamespace("tableau_de_bord")


@cached_fragment(ttl=300)  # Cache 5 min pour graphiques lourds
def afficher_graphiques_enrichis():
    """Affiche les graphiques Plotly enrichis."""
    from src.services.cuisine.planning import obtenir_service_planning
    from src.services.inventaire import obtenir_service_inventaire
    from src.ui.components import graphique_inventaire_categories, graphique_repartition_repas

    st.markdown("### 📈 Visualisations")

    col1, col2 = st.columns(2)

    with col1:
        # Graphique inventaire par categorie
        inventaire = obtenir_service_inventaire().get_inventaire_complet()
        fig = graphique_inventaire_categories(inventaire)
        if fig:
            st.markdown("**📦 Stock par Categorie**")
            st.plotly_chart(fig, width="stretch", key=_keys("chart_inventaire"))
        else:
            st.info("Pas de donnees d'inventaire")

    with col2:
        # Graphique repartition repas
        planning = obtenir_service_planning().get_planning()
        if planning and planning.repas:
            repas_data = [{"type_repas": getattr(r, "type_repas", "autre")} for r in planning.repas]
            fig = graphique_repartition_repas(repas_data)
            if fig:
                st.markdown("**💡 Repartition des Repas**")
                st.plotly_chart(fig, width="stretch", key=_keys("chart_repas"))
            else:
                st.info("Pas de planning cette semaine")
        else:
            st.info("Pas de planning cette semaine")


@auto_refresh(seconds=60)
def afficher_global_stats():
    """Stats globales de l'application (auto-refresh 60s)"""
    from src.services.cuisine.courses import obtenir_service_courses
    from src.services.cuisine.planning import obtenir_service_planning
    from src.services.cuisine.recettes import obtenir_service_recettes
    from src.services.inventaire import obtenir_service_inventaire

    # Charger stats
    logger = logging.getLogger(__name__)

    try:
        stats_recettes = obtenir_service_recettes().get_stats()
    except Exception as e:
        logger.debug("Stats recettes indisponibles: %s", e)
        stats_recettes = {"total": 0}

    try:
        stats_inventaire = obtenir_service_inventaire().get_stats()
    except Exception as e:
        logger.debug("Stats inventaire indisponibles: %s", e)
        stats_inventaire = {"total": 0}

    try:
        stats_courses = obtenir_service_courses().get_stats()
    except Exception as e:
        logger.debug("Stats courses indisponibles: %s", e)
        stats_courses = {"total": 0}

    try:
        inventaire = obtenir_service_inventaire().get_inventaire_complet()
    except Exception as e:
        logger.exception("Erreur lors du chargement de l'inventaire complet")
        inventaire = []

    # Afficher metriques
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_recettes = stats_recettes.get("total", 0)
        st.metric("💡 Recettes", total_recettes, help="Nombre total de recettes")

    with col2:
        total_inventaire = stats_inventaire.get("total", 0)
        stock_bas = len([a for a in inventaire if a.get("statut") in ["critique", "sous_seuil"]])

        st.metric(
            "📦 Inventaire",
            total_inventaire,
            delta=f"-{stock_bas} stock bas" if stock_bas > 0 else None,
            delta_color="inverse",
        )

    with col3:
        total_courses = stats_courses.get("total", 0)
        st.metric("📅 Courses", total_courses, help="Articles dans la liste")

    with col4:
        # Planning semaine
        nb_repas = 0
        try:
            planning = obtenir_service_planning().get_planning()
            nb_repas = len(planning.repas) if planning else 0
        except Exception as e:
            logger.exception("Erreur lors du chargement des repas planifiés")

        st.metric("🧹 Repas Planifiés", nb_repas, help="Cette semaine")
