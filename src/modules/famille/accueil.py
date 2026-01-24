"""
Accueil Module Famille - Hub central pour la gestion de famille
"""

import streamlit as st

from src.core.database import get_db_context
from src.core.models import ChildProfile, FamilyActivity, HealthEntry, FamilyBudget
from src.modules.famille import jules, sante, activites, shopping


# ===================================
# HELPERS
# ===================================


def get_resume_famille() -> dict:
    """Calcule un résumé de la situation famille"""
    with get_db_context() as db:
        # Jules info
        child = db.query(ChildProfile).filter(ChildProfile.name == "Jules").first()

        # Activités semaine
        from datetime import date, timedelta
        today = date.today()
        semaine_fin = today + timedelta(days=7)

        activites_semaine = db.query(FamilyActivity).filter(
            FamilyActivity.date_prevue >= today,
            FamilyActivity.date_prevue <= semaine_fin,
            FamilyActivity.statut == "planifié",
        ).count()

        # Séances santé semaine
        health_entries = db.query(HealthEntry).filter(
            HealthEntry.date >= (today - timedelta(days=7))
        ).count()

        # Budget mois
        month_start = date(today.year, today.month, 1)
        if today.month == 12:
            month_end = date(today.year + 1, 1, 1)
        else:
            month_end = date(today.year, today.month + 1, 1)

        budget_month = sum([
            b.montant for b in db.query(FamilyBudget).filter(
                FamilyBudget.date >= month_start,
                FamilyBudget.date < month_end,
            ).all()
        ])

        return {
            "child": child,
            "activites_semaine": activites_semaine,
            "health_entries": health_entries,
            "budget_month": budget_month,
        }


# ===================================
# MODULE PRINCIPAL
# ===================================


def app():
    """Hub central Famille"""

    st.set_page_config(
        page_title="🏠 Famille",
        page_icon="🏠",
        layout="wide",
    )

    st.title("🏠 Module Famille")
    st.caption("Hub de vie familiale - Jules, santé, activités et shopping")

    st.markdown("---")

    # Récupérer résumé
    resume = get_resume_famille()

    # ===================================
    # HEADER RÉSUMÉ
    # ===================================

    col_h1, col_h2, col_h3, col_h4 = st.columns(4)

    with col_h1:
        st.metric("👶 Jules", "19 mois", "en pleine forme! 💪")

    with col_h2:
        st.metric("📅 Activités", resume["activites_semaine"], "cette semaine")

    with col_h3:
        st.metric("🏃 Séances santé", resume["health_entries"], "dernière semaine")

    with col_h4:
        st.metric("💰 Budget", f"{resume['budget_month']:.0f}€", "ce mois-ci")

    st.markdown("---")

    # ===================================
    # NAVIGATION PRINCIPALE
    # ===================================

    st.subheader("📱 Choisir une section")

    col_nav1, col_nav2 = st.columns(2)

    with col_nav1:
        col_nav1a, col_nav1b = st.columns(2)

        with col_nav1a:
            if st.button(
                "👶 Jules (19 mois)\nJalons & Activités",
                use_container_width=True,
                help="Jalons, apprentissages, activités adaptées",
            ):
                st.session_state["page"] = "jules"

        with col_nav1b:
            if st.button(
                "💪 Santé & Sport\nObjectifs & Bien-être",
                use_container_width=True,
                help="Sport, nutrition saine, objectifs",
            ):
                st.session_state["page"] = "sante"

    with col_nav2:
        col_nav2a, col_nav2b = st.columns(2)

        with col_nav2a:
            if st.button(
                "🎨 Activités Famille\nSorties & Moments ensemble",
                use_container_width=True,
                help="Planifier sorties et activités",
            ):
                st.session_state["page"] = "activites"

        with col_nav2b:
            if st.button(
                "🛍️ Shopping\nAchats centralisés",
                use_container_width=True,
                help="Liste d'achats pour Jules, Nous et Maison",
            ):
                st.session_state["page"] = "shopping"

    st.markdown("---")

    # ===================================
    # AFFICHER PAGE SÉLECTIONNÉE
    # ===================================

    page = st.session_state.get("page", "accueil")

    if page == "jules":
        jules.app()
    elif page == "sante":
        sante.app()
    elif page == "activites":
        activites.app()
    elif page == "shopping":
        shopping.app()
    else:
        # Page d'accueil
        st.markdown("---")

        st.markdown("### 🎯 Prochaines étapes")

        col_next1, col_next2 = st.columns(2)

        with col_next1:
            st.markdown("**👶 Jules (19 mois)**")
            st.write("• Ajouter ses jalons (premiers mots, etc.)")
            st.write("• Planifier activités adaptées")
            st.write("• Tracker ses apprentissages")

        with col_next2:
            st.markdown("**💪 Santé & Bien-être**")
            st.write("• Créer routines de sport (3x/semaine?)")
            st.write("• Fixer objectifs santé")
            st.write("• Planifier repas sains")

        col_next3, col_next4 = st.columns(2)

        with col_next3:
            st.markdown("**🎨 Activités Famille**")
            st.write("• Planifier sortie semaine")
            st.write("• Explorer idées d'activités")
            st.write("• Tracker budget")

        with col_next4:
            st.markdown("**🛍️ Shopping**")
            st.write("• Créer liste d'achats")
            st.write("• Ajouter jouets/vêtements Jules")
            st.write("• Équipement sport")

        st.markdown("---")

        st.info(
            "💡 **Astuce**: Toutes les sections sont intégrées entre elles!"
            "\n\n"
            "📅 Les activités apparaissent dans le planning global"
            "\n"
            "🍽️ Les recettes saines se couplent avec le suivi sport"
            "\n"
            "🛒 Les achats se synchronisent avec les courses"
        )


if __name__ == "__main__":
    app()
