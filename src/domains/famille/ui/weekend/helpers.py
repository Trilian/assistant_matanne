"""
Module Sorties Weekend - Fonctions helper
"""

from ._common import (
    date, timedelta,
    get_db_context, WeekendActivity, ChildProfile
)


def get_next_weekend() -> tuple[date, date]:
    """Retourne les dates du prochain weekend"""
    today = date.today()
    days_until_saturday = (5 - today.weekday()) % 7
    
    if today.weekday() == 5:  # Samedi
        saturday = today
    elif today.weekday() == 6:  # Dimanche
        saturday = today + timedelta(days=6)  # Prochain samedi
    else:
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)
    
    sunday = saturday + timedelta(days=1)
    return saturday, sunday


def get_weekend_activities(saturday: date, sunday: date) -> dict:
    """Récupère les activités du weekend"""
    try:
        with get_db_context() as db:
            activities = db.query(WeekendActivity).filter(
                WeekendActivity.date_prevue.in_([saturday, sunday])
            ).order_by(WeekendActivity.heure_debut).all()
            
            return {
                "saturday": [a for a in activities if a.date_prevue == saturday],
                "sunday": [a for a in activities if a.date_prevue == sunday],
            }
    except:
        return {"saturday": [], "sunday": []}


def get_budget_weekend(saturday: date, sunday: date) -> dict:
    """Calcule le budget du weekend"""
    try:
        with get_db_context() as db:
            activities = db.query(WeekendActivity).filter(
                WeekendActivity.date_prevue.in_([saturday, sunday])
            ).all()
            
            estime = sum(a.cout_estime or 0 for a in activities)
            reel = sum(a.cout_reel or 0 for a in activities if a.statut == "terminé")
            
            return {"estime": estime, "reel": reel}
    except:
        return {"estime": 0, "reel": 0}


def get_lieux_testes() -> list:
    """Récupère les lieux déjà testés"""
    try:
        with get_db_context() as db:
            return db.query(WeekendActivity).filter(
                WeekendActivity.statut == "terminé",
                WeekendActivity.note_lieu.isnot(None)
            ).order_by(WeekendActivity.note_lieu.desc()).all()
    except:
        return []


def get_age_jules_mois() -> int:
    """Récupère l'âge de Jules en mois"""
    try:
        with get_db_context() as db:
            jules = db.query(ChildProfile).filter_by(name="Jules", actif=True).first()
            if jules and jules.date_of_birth:
                delta = date.today() - jules.date_of_birth
                return delta.days // 30
    except:
        pass
    return 19  # Valeur par défaut


def mark_activity_done(activity_id: int):
    """Marque une activité comme terminée"""
    try:
        with get_db_context() as db:
            act = db.get(WeekendActivity, activity_id)
            if act:
                act.statut = "terminé"
                db.commit()
    except:
        pass
