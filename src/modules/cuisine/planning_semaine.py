import streamlit as st
from src.services.planning.planning_service import planning_service, repas_service
from src.ui import empty_state, meal_card
from datetime import date

def app():
    st.title("🗓️ Planning Hebdomadaire")

    # Semaine actuelle
    if "semaine_actuelle" not in st.session_state:
        st.session_state.semaine_actuelle = planning_service.get_semaine_debut()

    semaine = st.session_state.semaine_actuelle

    # Navigation semaine
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Préc"):
            st.session_state.semaine_actuelle = semaine - timedelta(days=7)
            st.rerun()
    with col2:
        st.markdown(f"**Semaine du {semaine.strftime('%d/%m/%Y')}**")
    with col3:
        if st.button("Suiv ➡️"):
            st.session_state.semaine_actuelle = semaine + timedelta(days=7)
            st.rerun()

    # Charger planning
    planning = planning_service.get_planning_semaine(semaine)

    if not planning:
        empty_state("Aucun planning", "📅")
        if st.button("➕ Créer"):
            planning_service.create({"semaine_debut": semaine, "nom": f"Semaine {semaine.strftime('%d/%m')}"})
            st.rerun()
        return

    # Structure
    structure = planning_service.get_planning_structure(planning.id)

    # Affichage par jour
    for jour_data in structure["jours"]:
        with st.expander(f"{jour_data['nom_jour']} {jour_data['date'].strftime('%d/%m')}"):
            if jour_data["repas"]:
                for repas in jour_data["repas"]:
                    meal_card(repas, key=f"meal_{repas['id']}")
            else:
                st.info("Aucun repas")