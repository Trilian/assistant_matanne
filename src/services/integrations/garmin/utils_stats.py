"""
Fonctions de calcul statistique pour les données Garmin.

Calculs de statistiques quotidiennes, par activité, streaks,
progression vers les objectifs, estimation de calories et résumés hebdomadaires.
"""

from datetime import date, timedelta

from .types import (
    METERS_TO_KM,
    STEPS_GOAL_DEFAULT,
)

# ═══════════════════════════════════════════════════════════
# CALCULS ET STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculate_daily_stats(summaries: list[dict]) -> dict:
    """
    Calcule les statistiques agrégées à partir des résumés quotidiens.

    Args:
        summaries: Liste de résumés quotidiens (dict)

    Returns:
        Dict avec totaux et moyennes
    """
    if not summaries:
        return {
            "total_pas": 0,
            "total_calories": 0,
            "total_distance_km": 0.0,
            "moyenne_pas_jour": 0,
            "moyenne_calories_jour": 0,
            "jours_avec_donnees": 0,
        }

    total_pas = sum(s.get("pas", 0) for s in summaries)
    total_calories = sum(s.get("calories_actives", 0) for s in summaries)
    total_distance = sum(s.get("distance_metres", 0) for s in summaries)

    days_with_data = len(summaries)

    return {
        "total_pas": total_pas,
        "total_calories": total_calories,
        "total_distance_km": round(total_distance * METERS_TO_KM, 2),
        "moyenne_pas_jour": total_pas // days_with_data,
        "moyenne_calories_jour": total_calories // days_with_data,
        "jours_avec_donnees": days_with_data,
    }


def calculate_activity_stats(activities: list[dict]) -> dict:
    """
    Calcule les statistiques agrégées des activités.

    Args:
        activities: Liste d'activités (dict)

    Returns:
        Dict avec totaux par type
    """
    if not activities:
        return {
            "total_activites": 0,
            "par_type": {},
            "total_duree_minutes": 0,
            "total_calories": 0,
        }

    par_type = {}
    total_duree = 0
    total_calories = 0

    for act in activities:
        activity_type = act.get("type_activite", "other")
        if activity_type not in par_type:
            par_type[activity_type] = {"count": 0, "duree": 0, "calories": 0}

        par_type[activity_type]["count"] += 1
        par_type[activity_type]["duree"] += act.get("duree_secondes", 0)
        par_type[activity_type]["calories"] += act.get("calories", 0) or 0

        total_duree += act.get("duree_secondes", 0)
        total_calories += act.get("calories", 0) or 0

    return {
        "total_activites": len(activities),
        "par_type": par_type,
        "total_duree_minutes": total_duree // 60,
        "total_calories": total_calories,
    }


def calculate_streak(
    summaries_by_date: dict[date, dict],
    goal_steps: int = STEPS_GOAL_DEFAULT,
    max_days: int = 100,
    reference_date: date | None = None,
) -> int:
    """
    Calcule le nombre de jours consécutifs avec objectif atteint.

    Args:
        summaries_by_date: Dict {date: summary_dict}
        goal_steps: Objectif quotidien de pas
        max_days: Nombre max de jours à vérifier
        reference_date: Date de référence (défaut: aujourd'hui)

    Returns:
        Nombre de jours de streak

    Examples:
        >>> summaries = {date(2024,1,1): {"pas": 12000}, date(2024,1,2): {"pas": 11000}}
        >>> calculate_streak(summaries, goal_steps=10000, reference_date=date(2024,1,2))
        2
    """
    if reference_date is None:
        reference_date = date.today()

    streak = 0
    current_date = reference_date
    end_date = reference_date - timedelta(days=max_days)

    while current_date > end_date:
        summary = summaries_by_date.get(current_date)
        if summary and summary.get("pas", 0) >= goal_steps:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

    return streak


def get_streak_badge(streak: int) -> tuple[str, str] | None:
    """
    Détermine le badge à afficher pour un streak.

    Args:
        streak: Nombre de jours de streak

    Returns:
        Tuple (emoji, label) ou None si pas de badge
    """
    if streak >= 100:
        return "🏆", "Champion du mois"
    elif streak >= 60:
        return "💎", "Diamant"
    elif streak >= 30:
        return "🔥", "On fire!"
    elif streak >= 14:
        return "⭐", "Star"
    elif streak >= 7:
        return "⏰", "1 semaine"

    return None


def calculate_goal_progress(current: int, goal: int) -> tuple[float, str]:
    """
    Calcule le pourcentage de progression vers un objectif.

    Args:
        current: Valeur actuelle
        goal: Objectif

    Returns:
        Tuple (pourcentage 0-100, couleur CSS)
    """
    if goal <= 0:
        return 100.0, "green"

    percentage = min(100.0, (current / goal) * 100)

    if percentage >= 100:
        color = "green"
    elif percentage >= 75:
        color = "blue"
    elif percentage >= 50:
        color = "orange"
    else:
        color = "red"

    return round(percentage, 1), color


def estimate_calories_burned(
    activity_type: str, duration_seconds: int, weight_kg: float = 70.0
) -> int:
    """
    Estime les calories brûlées pour une activité.

    Utilise les valeurs MET approximatives.

    Args:
        activity_type: Type d'activité
        duration_seconds: Durée en secondes
        weight_kg: Poids de l'utilisateur

    Returns:
        Estimation des calories brûlées
    """
    # Valeurs MET (approximations)
    met_values = {
        "running": 10.0,
        "cycling": 7.5,
        "swimming": 7.0,
        "walking": 3.5,
        "hiking": 6.0,
        "strength_training": 5.0,
        "cardio_training": 6.0,
        "yoga": 2.5,
        "elliptical": 5.5,
        "stair_climbing": 9.0,
        "other": 4.0,
    }

    met = met_values.get(activity_type.lower(), 4.0)
    hours = duration_seconds / 3600

    # Calories = MET * poids_kg * heures
    return int(met * weight_kg * hours)


def calculate_weekly_summary(daily_summaries: list[dict], week_start: date | None = None) -> dict:
    """
    Calcule un résumé hebdomadaire.

    Args:
        daily_summaries: Résumés quotidiens de la semaine
        week_start: Début de la semaine (défaut: lundi de la semaine courante)

    Returns:
        Dict avec le résumé hebdomadaire
    """
    if week_start is None:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

    week_end = week_start + timedelta(days=6)

    # Filtrer les résumés de la semaine
    week_summaries = [
        s for s in daily_summaries if s.get("date") and week_start <= s["date"] <= week_end
    ]

    stats = calculate_daily_stats(week_summaries)

    # Jours avec objectif atteint
    days_goal_reached = sum(1 for s in week_summaries if s.get("pas", 0) >= STEPS_GOAL_DEFAULT)

    return {
        **stats,
        "semaine_debut": week_start,
        "semaine_fin": week_end,
        "jours_objectif_atteint": days_goal_reached,
        "jours_manquants": 7 - len(week_summaries),
    }
