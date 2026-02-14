"""
Module Accueil - Dashboard Central
Vue d'ensemble de l'application avec stats, alertes et raccourcis
"""

from datetime import date

import streamlit as st

# Cache
# State
from src.core.state import GestionnaireEtat, obtenir_etat

# Logique metier pure
from src.services.courses import get_courses_service
from src.services.inventaire import get_inventaire_service
from src.services.planning import get_planning_service

# Services
from src.services.recettes import get_recette_service
from src.ui.components.alertes import alerte_stock

# Dashboard widgets enrichis
try:
    from src.ui.components.dashboard_widgets import (
        afficher_sante_systeme,
        graphique_inventaire_categories,
        graphique_repartition_repas,
        widget_jules_apercu,
    )

    WIDGETS_DISPONIBLES = True
except ImportError:
    WIDGETS_DISPONIBLES = False

# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# MODULE PRINCIPAL
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def app():
    """Point d'entree module accueil"""

    # Header
    state = obtenir_etat()

    st.markdown(
        f"<h1 style='text-align: center;'>ð¤ Bienvenue {state.nom_utilisateur} !</h1>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p style='text-align: center; color: #6c757d; font-size: 1.1rem;'>"
        "Ton assistant familial intelligent"
        "</p>",
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Alertes critiques en haut
    render_critical_alerts()

    st.markdown("---")

    # Stats globales
    render_global_stats()

    st.markdown("---")

    # Raccourcis rapides
    render_quick_actions()

    st.markdown("---")

    # Graphiques enrichis (si widgets disponibles)
    if WIDGETS_DISPONIBLES:
        render_graphiques_enrichis()
        st.markdown("---")

    # Vue par module
    col1, col2 = st.columns(2)

    with col1:
        render_cuisine_summary()
        st.markdown("")
        render_planning_summary()

    with col2:
        render_inventaire_summary()
        st.markdown("")
        render_courses_summary()

    # Footer avec sante système
    st.markdown("---")
    if WIDGETS_DISPONIBLES:
        col_footer1, col_footer2 = st.columns([3, 1])
        with col_footer1:
            afficher_sante_systeme()
        with col_footer2:
            widget_jules_apercu()


def render_graphiques_enrichis():
    """Affiche les graphiques Plotly enrichis."""

    st.markdown("### ð Visualisations")

    col1, col2 = st.columns(2)

    with col1:
        # Graphique inventaire par categorie
        inventaire = get_inventaire_service().get_inventaire_complet()
        fig = graphique_inventaire_categories(inventaire)
        if fig:
            st.markdown("**ð¦ Stock par Categorie**")
            st.plotly_chart(fig, width="stretch", key="chart_inventaire")
        else:
            st.info("Pas de donnees d'inventaire")

    with col2:
        # Graphique repartition repas
        planning = get_planning_service().get_planning()
        if planning and planning.repas:
            repas_data = [{"type_repas": getattr(r, "type_repas", "autre")} for r in planning.repas]
            fig = graphique_repartition_repas(repas_data)
            if fig:
                st.markdown("**ð¡ Repartition des Repas**")
                st.plotly_chart(fig, width="stretch", key="chart_repas")
            else:
                st.info("Pas de planning cette semaine")
        else:
            st.info("Pas de planning cette semaine")


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# ALERTES CRITIQUES
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def render_critical_alerts():
    """Affiche les alertes importantes"""

    alerts = []

    # Inventaire critique
    inventaire = get_inventaire_service().get_inventaire_complet()
    critiques = [art for art in inventaire if art.get("statut") in ["critique", "sous_seuil"]]

    if critiques:
        alerts.append(
            {
                "type": "warning",
                "icon": "⚠ï¸",
                "title": f"{len(critiques)} article(s) en stock bas",
                "action": "Voir l'inventaire",
                "module": "cuisine.inventaire",
            }
        )

    # Peremption proche
    peremption = [art for art in inventaire if art.get("statut") == "peremption_proche"]

    if peremption:
        alerts.append(
            {
                "type": "warning",
                "icon": "â³",
                "title": f"{len(peremption)} article(s) periment bientôt",
                "action": "Voir l'inventaire",
                "module": "cuisine.inventaire",
            }
        )

    # Planning vide
    planning = get_planning_service().get_planning()

    if not planning or not planning.repas:
        alerts.append(
            {
                "type": "info",
                "icon": "ï¿½",
                "title": "Aucun planning pour cette semaine",
                "action": "Creer un planning",
                "module": "cuisine.planning_semaine",
            }
        )

    # Tâches menage en retard
    try:
        from src.core.database import obtenir_contexte_db
        from src.core.models import MaintenanceTask

        with obtenir_contexte_db() as db:
            taches_retard = (
                db.query(MaintenanceTask)
                .filter(
                    MaintenanceTask.prochaine_fois < date.today(),
                    MaintenanceTask.fait.is_(False),
                )
                .limit(10)
                .all()
            )

            if taches_retard:
                alerts.append(
                    {
                        "type": "warning",
                        "icon": "ð§¹",
                        "title": f"{len(taches_retard)} tâche(s) menage en retard!",
                        "action": "Voir Maison",
                        "module": "maison.entretien",
                    }
                )

                # Detail des tâches critiques
                for t in taches_retard[:3]:
                    jours_retard = (date.today() - t.prochaine_fois).days
                    alerts.append(
                        {
                            "type": "error" if jours_retard > 7 else "warning",
                            "icon": "⚠ï¸",
                            "title": f"{t.nom} ({jours_retard}j de retard)",
                            "action": "Marquer fait",
                            "module": "maison.entretien",
                        }
                    )
    except Exception:
        pass  # Table pas encore creee

    # Afficher alertes
    if not alerts:
        st.success("â Tout est en ordre !")
        return

    st.markdown("### â° Alertes")

    for alert in alerts:
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                if alert["type"] == "warning":
                    st.warning(f"{alert['icon']} **{alert['title']}**")
                elif alert["type"] == "info":
                    st.info(f"{alert['icon']} **{alert['title']}**")
                else:
                    st.error(f"{alert['icon']} **{alert['title']}**")

            with col2:
                if st.button(alert["action"], key=f"alert_{alert['module']}", width="stretch"):
                    GestionnaireEtat.naviguer_vers(alert["module"])
                    st.rerun()


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# STATS GLOBALES
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def render_global_stats():
    """Stats globales de l'application"""

    st.markdown("### ð Vue d'Ensemble")

    # Charger stats
    stats_recettes = get_recette_service().get_stats()
    stats_inventaire = get_inventaire_service().get_stats()
    stats_courses = get_courses_service().get_stats()

    inventaire = get_inventaire_service().get_inventaire_complet()

    # Afficher metriques
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_recettes = stats_recettes.get("total", 0)
        st.metric("ð¡ Recettes", total_recettes, help="Nombre total de recettes")

    with col2:
        total_inventaire = stats_inventaire.get("total", 0)
        stock_bas = len([a for a in inventaire if a.get("statut") in ["critique", "sous_seuil"]])

        st.metric(
            "ð¦ Inventaire",
            total_inventaire,
            delta=f"-{stock_bas} stock bas" if stock_bas > 0 else None,
            delta_color="inverse",
        )

    with col3:
        total_courses = stats_courses.get("total", 0)
        st.metric("ð Courses", total_courses, help="Articles dans la liste")

    with col4:
        # Planning semaine
        planning = get_planning_service().get_planning()
        nb_repas = len(planning.repas) if planning else 0

        st.metric("ð§¹ Repas Planifies", nb_repas, help="Cette semaine")


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# RACCOURCIS RAPIDES
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def render_quick_actions():
    """Raccourcis d'actions rapides"""

    st.markdown("### â¡ Actions Rapides")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("â Ajouter Recette", key="quick_add_recette", width="stretch", type="primary"):
            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            st.session_state.show_add_form = True
            st.rerun()

    with col2:
        if st.button("ð Voir Courses", key="quick_view_courses", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.courses")
            st.rerun()

    with col3:
        if st.button("ð¦ Gerer Inventaire", key="quick_view_inventaire", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.inventaire")
            st.rerun()

    with col4:
        if st.button("ð§¹ Planning Semaine", key="quick_view_planning", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            st.rerun()


# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ
# RÃSUMÃS PAR MODULE
# âââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ


def render_cuisine_summary():
    """Resume module Cuisine"""

    with st.container():
        st.markdown(
            '<div style="background: #f8f9fa; padding: 1.5rem; '
            'border-radius: 12px; border-left: 4px solid #4CAF50;">',
            unsafe_allow_html=True,
        )

        st.markdown("### ð¡ Recettes")

        stats = get_recette_service().get_stats(
            count_filters={
                "rapides": {"temps_preparation": {"lte": 30}},
                "bebe": {"compatible_bebe": True},
            }
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total", stats.get("total", 0))

        with col2:
            st.metric("â¡ Rapides", stats.get("rapides", 0))

        with col3:
            st.metric("ð¯ Bebe", stats.get("bebe", 0))

        if st.button("ð¶ Voir les recettes", key="nav_recettes", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_inventaire_summary():
    """Resume inventaire"""

    with st.container():
        st.markdown(
            '<div style="background: #f8f9fa; padding: 1.5rem; '
            'border-radius: 12px; border-left: 4px solid #2196F3;">',
            unsafe_allow_html=True,
        )

        st.markdown("### ð¦ Inventaire")

        inventaire = get_inventaire_service().get_inventaire_complet()

        stock_bas = len([a for a in inventaire if a.get("statut") == "sous_seuil"])
        critiques = len([a for a in inventaire if a.get("statut") == "critique"])
        peremption = len([a for a in inventaire if a.get("statut") == "peremption_proche"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Articles", len(inventaire))

        with col2:
            st.metric("⚠ï¸ Stock Bas", stock_bas, delta=None if stock_bas == 0 else "Ã commander")

        with col3:
            st.metric("â Critiques", critiques, delta=None if critiques == 0 else "Urgent")

        # Alertes
        if critiques > 0 or peremption > 0:
            articles_alert = [
                a for a in inventaire if a.get("statut") in ["critique", "peremption_proche"]
            ]

            alerte_stock(articles_alert[:3], cle="home_inventory_alert")  # Max 3

        if st.button("ð¦ Gerer l'inventaire", key="nav_inventaire", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.inventaire")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_courses_summary():
    """Resume courses"""

    with st.container():
        st.markdown(
            '<div style="background: #f8f9fa; padding: 1.5rem; '
            'border-radius: 12px; border-left: 4px solid #FF9800;">',
            unsafe_allow_html=True,
        )
        st.markdown("### ð Courses")

        liste = get_courses_service().get_liste_courses()

        haute = len([a for a in liste if a.get("priorite") == "haute"])
        moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total", len(liste))

        with col2:
            st.metric("â Haute", haute)

        with col3:
            st.metric("ð½ï¸ Moyenne", moyenne)

        # Top priorites
        if haute > 0:
            st.markdown("**Ã acheter en priorite:**")
            prioritaires = [a for a in liste if a.get("priorite") == "haute"]

            for art in prioritaires[:3]:
                st.caption(
                    f"â¢ {art.get('ingredient_nom', 'Article')} ({art.get('quantite_necessaire', 0)} {art.get('unite', '')})"
                )

            if len(prioritaires) > 3:
                st.caption(f"... et {len(prioritaires) - 3} autre(s)")

        if st.button("ð Voir la liste", key="nav_courses", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.courses")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_planning_summary():
    """Resume planning"""

    with st.container():
        st.markdown(
            '<div style="background: #f8f9fa; padding: 1.5rem; '
            'border-radius: 12px; border-left: 4px solid #9C27B0;">',
            unsafe_allow_html=True,
        )

        st.markdown("### ð§¹ Planning Semaine")

        planning = get_planning_service().get_planning()

        if planning and planning.repas:
            total_repas = len(planning.repas)

            # Repas adaptes bebe
            repas_bebe = len([r for r in planning.repas if getattr(r, "compatible_bebe", False)])

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Repas", total_repas)

            with col2:
                st.metric("ð¯ Bebe", repas_bebe)

            # Repas d'aujourd'hui
            aujourd_hui = date.today()
            repas_aujourdhui = [
                r for r in planning.repas if hasattr(r, "date") and r.date == aujourd_hui
            ]

            if repas_aujourdhui:
                st.markdown("**Aujourd'hui:**")
                for repas in repas_aujourdhui[:2]:
                    type_repas = getattr(repas, "type_repas", "Repas")
                    nom_recette = getattr(repas, "recette_nom", None) or "Non defini"
                    st.caption(f"â¢ {type_repas}: {nom_recette}")

        else:
            st.info("Aucun planning cette semaine")

        if st.button("ð§¹ Voir le planning", key="nav_planning", width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
