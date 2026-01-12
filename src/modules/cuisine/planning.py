"""
Module Planning - Gestion du planning hebdomadaire
"""

import streamlit as st
from datetime import date, timedelta
from src.services.planning import get_planning_service


def app():
    """Point d'entrée module planning"""
    st.title("📅 Planning Semaine")
    st.caption("Gérez vos repas de la semaine")

    tab_planning, tab_generer, tab_historique = st.tabs(["📋 Planning", "✨ Générer", "📚 Historique"])

    with tab_planning:
        render_planning()

    with tab_generer:
        st.info("✨ Générer un planning avec IA - À implémenter")

    with tab_historique:
        st.info("📚 Historique des plannings - À implémenter")


def render_planning():
    """Affiche le planning actuel"""
    service = get_planning_service()
    
    if service is None:
        st.error("❌ Service planning indisponible")
        return
    
    planning = service.get_planning()
    
    if not planning:
        st.warning("Aucun planning pour cette semaine")
        st.button("➕ Créer un planning", use_container_width=True)
        return
    
    # Afficher le planning
    st.success(f"📅 Planning: {planning.nom}")
    st.write(f"Semaine du {planning.semaine_debut} au {planning.semaine_fin}")
    
    # Afficher les repas par jour
    if planning.repas:
        st.info(f"📊 {len(planning.repas)} repas planifiés cette semaine")
        
        for repas in planning.repas[:7]:
            with st.container(border=True):
                st.write(f"**{repas.date_repas}** - {repas.type_repas}")
                if repas.recette:
                    st.write(f"🍽️ {repas.recette.nom}")
    else:
        st.info("Aucun repas planifié")
