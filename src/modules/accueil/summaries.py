"""
Dashboard - Résumés par module
Cartes de résumé pour chaque module métier sur le tableau de bord
"""

from datetime import date

import streamlit as st

from src.ui.keys import KeyNamespace
from src.ui.tokens import Couleur
from src.ui.tokens_semantic import Sem

_keys = KeyNamespace("accueil")


def afficher_cuisine_summary():
    """Resume module Cuisine"""
    from src.core.state import GestionnaireEtat, rerun
    from src.services.cuisine.recettes import obtenir_service_recettes

    with st.container():
        st.markdown(
            f'<div style="background: {Sem.SURFACE_ALT}; padding: 1.5rem; '
            f'border-radius: 12px; border-left: 4px solid {Couleur.SUCCESS};">',
            unsafe_allow_html=True,
        )

        st.markdown("### 💡 Recettes")

        stats = obtenir_service_recettes().get_stats(
            count_filters={
                "rapides": {"temps_preparation": {"lte": 30}},
                "bebe": {"compatible_bebe": True},
            }
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total", stats.get("total", 0))

        with col2:
            st.metric("⚡ Rapides", stats.get("rapides", 0))

        with col3:
            st.metric("🎯 Bebe", stats.get("bebe", 0))

        if st.button("👶 Voir les recettes", key=_keys("nav_recettes"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def afficher_inventaire_summary():
    """Resume inventaire"""
    from src.core.state import GestionnaireEtat
    from src.services.inventaire import obtenir_service_inventaire
    from src.ui import alerte_stock

    with st.container():
        st.markdown(
            f'<div style="background: {Sem.SURFACE_ALT}; padding: 1.5rem; '
            f'border-radius: 12px; border-left: 4px solid {Couleur.INFO};">',
            unsafe_allow_html=True,
        )

        st.markdown("### 📦 Inventaire")

        inventaire = obtenir_service_inventaire().get_inventaire_complet()

        stock_bas = len([a for a in inventaire if a.get("statut") == "sous_seuil"])
        critiques = len([a for a in inventaire if a.get("statut") == "critique"])
        peremption = len([a for a in inventaire if a.get("statut") == "peremption_proche"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Articles", len(inventaire))

        with col2:
            st.metric("⚠️ Stock Bas", stock_bas, delta=None if stock_bas == 0 else "À commander")

        with col3:
            st.metric("❌ Critiques", critiques, delta=None if critiques == 0 else "Urgent")

        # Alertes
        if critiques > 0 or peremption > 0:
            articles_alert = [
                a for a in inventaire if a.get("statut") in ["critique", "peremption_proche"]
            ]

            alerte_stock(articles_alert[:3])  # Max 3

        if st.button("📦 Gerer l'inventaire", key=_keys("nav_inventaire"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.inventaire")
            rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def afficher_courses_summary():
    """Resume courses"""
    from src.core.state import GestionnaireEtat
    from src.services.cuisine.courses import obtenir_service_courses

    with st.container():
        st.markdown(
            f'<div style="background: {Sem.SURFACE_ALT}; padding: 1.5rem; '
            f'border-radius: 12px; border-left: 4px solid {Couleur.WARNING};">',
            unsafe_allow_html=True,
        )
        st.markdown("### 📅 Courses")

        liste = obtenir_service_courses().get_liste_courses()

        haute = len([a for a in liste if a.get("priorite") == "haute"])
        moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total", len(liste))

        with col2:
            st.metric("❌ Haute", haute)

        with col3:
            st.metric("🍽️ Moyenne", moyenne)

        # Top priorites
        if haute > 0:
            st.markdown("**À acheter en priorite:**")
            prioritaires = [a for a in liste if a.get("priorite") == "haute"]

            for art in prioritaires[:3]:
                st.caption(
                    f"• {art.get('ingredient_nom', 'Article')} "
                    f"({art.get('quantite_necessaire', 0)} {art.get('unite', '')})"
                )

            if len(prioritaires) > 3:
                st.caption(f"... et {len(prioritaires) - 3} autre(s)")

        if st.button("📅 Voir la liste", key=_keys("nav_courses"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.courses")
            rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def afficher_planning_summary():
    """Resume planning"""
    from src.core.state import GestionnaireEtat
    from src.services.cuisine.planning import obtenir_service_planning
    from src.ui import etat_vide

    with st.container():
        st.markdown(
            f'<div style="background: {Sem.SURFACE_ALT}; padding: 1.5rem; '
            f'border-radius: 12px; border-left: 4px solid {Couleur.ACCENT};">',
            unsafe_allow_html=True,
        )

        st.markdown("### 🧹 Planning Semaine")

        planning = obtenir_service_planning().get_planning()

        if planning and planning.repas:
            total_repas = len(planning.repas)

            # Repas adaptes bebe
            repas_bebe = len([r for r in planning.repas if getattr(r, "compatible_bebe", False)])

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Repas", total_repas)

            with col2:
                st.metric("🎯 Bebe", repas_bebe)

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
                    st.caption(f"• {type_repas}: {nom_recette}")

        else:
            etat_vide("Aucun planning cette semaine", "🍽️", "Planifiez vos repas pour la semaine")

        if st.button("🧹 Voir le planning", key=_keys("nav_planning"), width="stretch"):
            GestionnaireEtat.naviguer_vers("cuisine.planning_semaine")
            rerun()

        st.markdown("</div>", unsafe_allow_html=True)
