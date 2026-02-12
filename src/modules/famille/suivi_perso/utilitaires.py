"""
Module Suivi Perso - Fonctions helper
"""

from ._common import (
    st, date, datetime, timedelta,
    obtenir_contexte_db, UserProfile, GarminDailySummary, FoodLog,
    get_or_create_user
)


def get_current_user() -> str:
    """Récupère l'utilisateur courant"""
    return st.session_state.get("suivi_user", "anne")


def set_current_user(username: str):
    """Définit l'utilisateur courant"""
    st.session_state["suivi_user"] = username


def get_user_data(username: str) -> dict:
    """Récupère les données complètes d'un utilisateur"""
    from ._common import GarminActivity
    
    try:
        with obtenir_contexte_db() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            
            if not user:
                # Créer l'utilisateur
                user = get_or_create_user(
                    username, 
                    "Anne" if username == "anne" else "Mathieu",
                    db=db
                )
            
            # Stats des 7 derniers jours
            end_date = date.today()
            start_date = end_date - timedelta(days=7)
            
            summaries = db.query(GarminDailySummary).filter(
                GarminDailySummary.user_id == user.id,
                GarminDailySummary.date >= start_date
            ).all()
            
            activities = db.query(GarminActivity).filter(
                GarminActivity.user_id == user.id,
                GarminActivity.date_debut >= datetime.combine(start_date, datetime.min.time())
            ).all()
            
            # Calculer les stats
            total_pas = sum(s.pas for s in summaries)
            total_calories = sum(s.calories_actives for s in summaries)
            total_minutes = sum(s.minutes_actives for s in summaries)
            
            # Streak
            streak = _calculate_streak(user, summaries)
            
            return {
                "user": user,
                "summaries": summaries,
                "activities": activities,
                "total_pas": total_pas,
                "total_calories": total_calories,
                "total_minutes": total_minutes,
                "streak": streak,
                "garmin_connected": user.garmin_connected,
                "objectif_pas": user.objectif_pas_quotidien,
                "objectif_calories": user.objectif_calories_brulees,
            }
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        return {}


def _calculate_streak(user: UserProfile, summaries: list) -> int:
    """Calcule le streak actuel"""
    if not summaries:
        return 0
    
    objectif = user.objectif_pas_quotidien or 10000
    summary_by_date = {s.date: s for s in summaries}
    
    streak = 0
    current_date = date.today()
    
    for _ in range(60):  # Max 60 jours
        summary = summary_by_date.get(current_date)
        if summary and summary.pas >= objectif:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    return streak


def get_food_logs_today(username: str) -> list:
    """Récupère les logs alimentation du jour"""
    try:
        with obtenir_contexte_db() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            if not user:
                return []
            
            return db.query(FoodLog).filter(
                FoodLog.user_id == user.id,
                FoodLog.date == date.today()
            ).order_by(FoodLog.heure).all()
    except:
        return []

