"""
Module Suivi Perso - Log alimentation
"""

from src.core.state import rerun
from src.ui.fragments import ui_fragment

from .utils import (
    date,
    get_food_logs_today,
    st,
)


@ui_fragment
def afficher_food_log(username: str):
    """Affiche et permet d'ajouter des logs alimentation"""
    st.subheader("🥗 Alimentation")

    tabs = st.tabs(["📝 Aujourd'hui", "➕ Ajouter"])

    with tabs[0]:
        logs = get_food_logs_today(username)

        if not logs:
            st.caption("Aucun repas enregistre aujourd'hui")
        else:
            total_cal = sum(l.calories_estimees or 0 for l in logs)
            st.metric("Total calories", f"{total_cal} kcal")

            for log in logs:
                repas_emoji = {
                    "petit_dejeuner": "🌅",
                    "dejeuner": "🌞",
                    "diner": "🌙",
                    "snack": "🍎",
                }.get(log.repas, "🍽️")

                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{repas_emoji} {log.repas.replace('_', ' ').title()}**")
                        st.write(log.description)
                    with col2:
                        if log.calories_estimees:
                            st.write(f"~{log.calories_estimees} kcal")
                        if log.qualite:
                            st.write("⭐" * log.qualite)

    with tabs[1]:
        afficher_food_form(username)


def afficher_food_form(username: str):
    """Formulaire d'ajout de repas"""
    with st.form("add_food"):
        repas = st.selectbox(
            "Repas",
            [
                ("petit_dejeuner", "🌅 Petit-dejeuner"),
                ("dejeuner", "🌞 Dejeuner"),
                ("diner", "🌙 Dîner"),
                ("snack", "🍎 Snack"),
            ],
            format_func=lambda x: x[1],
        )

        description = st.text_area("Description *", placeholder="Ex: Salade, poulet, riz...")

        col1, col2 = st.columns(2)
        with col1:
            calories = st.number_input("Calories (estimees)", min_value=0, step=50)
        with col2:
            qualite = st.slider("Qualite", 1, 5, 3)

        notes = st.text_input("Notes (optionnel)")

        if st.form_submit_button("✅ Enregistrer", type="primary"):
            if not description:
                st.error("Description requise")
            else:
                try:
                    from src.services.famille.suivi_perso import obtenir_service_suivi_perso

                    obtenir_service_suivi_perso().ajouter_food_log(
                        username=username,
                        repas=repas[0],
                        description=description,
                        calories=calories if calories > 0 else None,
                        qualite=qualite,
                        notes=notes or None,
                    )
                    st.success("✅ Repas enregistre!")
                    rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
