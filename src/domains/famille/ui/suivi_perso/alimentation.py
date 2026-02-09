"""
Module Suivi Perso - Log alimentation
"""

from ._common import (
    st, date, datetime,
    get_db_context, UserProfile, FoodLog,
    get_or_create_user
)
from .helpers import get_food_logs_today


def render_food_log(username: str):
    """Affiche et permet d'ajouter des logs alimentation"""
    st.subheader("🥗 Alimentation")
    
    tabs = st.tabs(["📝 Aujourd'hui", "➕ Ajouter"])
    
    with tabs[0]:
        logs = get_food_logs_today(username)
        
        if not logs:
            st.caption("Aucun repas enregistré aujourd'hui")
        else:
            total_cal = sum(l.calories_estimees or 0 for l in logs)
            st.metric("Total calories", f"{total_cal} kcal")
            
            for log in logs:
                repas_emoji = {
                    "petit_dejeuner": "🌅",
                    "dejeuner": "🌞",
                    "diner": "🌙",
                    "snack": "🍎"
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
        render_food_form(username)


def render_food_form(username: str):
    """Formulaire d'ajout de repas"""
    with st.form("add_food"):
        repas = st.selectbox("Repas", [
            ("petit_dejeuner", "🌅 Petit-déjeuner"),
            ("dejeuner", "🌞 Déjeuner"),
            ("diner", "🌙 Dîner"),
            ("snack", "🍎 Snack"),
        ], format_func=lambda x: x[1])
        
        description = st.text_area("Description *", placeholder="Ex: Salade, poulet, riz...")
        
        col1, col2 = st.columns(2)
        with col1:
            calories = st.number_input("Calories (estimées)", min_value=0, step=50)
        with col2:
            qualite = st.slider("Qualité", 1, 5, 3)
        
        notes = st.text_input("Notes (optionnel)")
        
        if st.form_submit_button("✅ Enregistrer", type="primary"):
            if not description:
                st.error("Description requise")
            else:
                try:
                    with get_db_context() as db:
                        user = db.query(UserProfile).filter_by(username=username).first()
                        if not user:
                            user = get_or_create_user(
                                username,
                                "Anne" if username == "anne" else "Mathieu",
                                db=db
                            )
                        
                        log = FoodLog(
                            user_id=user.id,
                            date=date.today(),
                            heure=datetime.now(),
                            repas=repas[0],
                            description=description,
                            calories_estimees=calories if calories > 0 else None,
                            qualite=qualite,
                            notes=notes or None
                        )
                        db.add(log)
                        db.commit()
                        st.success("✅ Repas enregistré!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
