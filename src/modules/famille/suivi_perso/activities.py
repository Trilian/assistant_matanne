"""
Module Suivi Perso - Activités sportives
"""

from .utils import st


def render_activities(data: dict):
    """Affiche les activités sportives"""
    st.subheader("🏃 Activités récentes")

    activities = data.get("activities", [])

    if not activities:
        st.info("Aucune activité enregistrée cette semaine")
        return

    for act in sorted(activities, key=lambda x: x.date_debut, reverse=True)[:5]:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                emoji = {
                    "running": "🏃",
                    "cycling": "🚴",
                    "swimming": "🏊",
                    "walking": "🚶",
                    "hiking": "🥾",
                    "strength": "💪",
                    "yoga": "🧘",
                }.get(act.type_activite.lower(), "🏋️")

                st.markdown(f"**{emoji} {act.nom}**")
                st.caption(act.date_debut.strftime("%d/%m à %H:%M"))

            with col2:
                st.write(f"⏱️ {act.duree_formatted}")
                if act.distance_metres:
                    st.write(f"📝 {act.distance_km:.1f} km")

            with col3:
                if act.calories:
                    st.write(f"🔥 {act.calories} kcal")
                if act.fc_moyenne:
                    st.write(f"❤️ {act.fc_moyenne} bpm")
