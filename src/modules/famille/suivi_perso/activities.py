"""
Module Suivi Perso - ActivitÃes sportives
"""

from .utils import st


def render_activities(data: dict):
    """Affiche les activitÃes sportives"""
    st.subheader("ðŸƒ ActivitÃes rÃecentes")
    
    activities = data.get("activities", [])
    
    if not activities:
        st.info("Aucune activitÃe enregistrÃee cette semaine")
        return
    
    for act in sorted(activities, key=lambda x: x.date_debut, reverse=True)[:5]:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                emoji = {
                    "running": "ðŸƒ",
                    "cycling": "ðŸš´",
                    "swimming": "ðŸŠ",
                    "walking": "ðŸš¶",
                    "hiking": "ðŸ¥¾",
                    "strength": "ðŸ’ª",
                    "yoga": "ðŸ§˜",
                }.get(act.type_activite.lower(), "ðŸ‹ï¸")
                
                st.markdown(f"**{emoji} {act.nom}**")
                st.caption(act.date_debut.strftime("%d/%m Ã  %H:%M"))
            
            with col2:
                st.write(f"â±ï¸ {act.duree_formatted}")
                if act.distance_metres:
                    st.write(f"ðŸ“ {act.distance_km:.1f} km")
            
            with col3:
                if act.calories:
                    st.write(f"ðŸ”¥ {act.calories} kcal")
                if act.fc_moyenne:
                    st.write(f"â¤ï¸ {act.fc_moyenne} bpm")
