"""
Fonctions utilitaires pures pour le service de synchronisation Garmin.

Ces fonctions peuvent être testées sans base de données ni connexions API.
Elles représentent la logique métier pure extraite de garmin_sync.py.
"""

from datetime import date, datetime, timedelta
from typing import Any

from .types import (
    ACTIVITY_TYPE_MAPPING,
    ACTIVITY_ICONS,
    STEPS_GOAL_DEFAULT,
    METERS_TO_KM,
)


# ═══════════════════════════════════════════════════════════
# PARSING DES DONNÉES API
# ═══════════════════════════════════════════════════════════


def parse_garmin_timestamp(timestamp: int | float | None) -> datetime | None:
    """
    Convertit un timestamp Garmin (secondes) en datetime.
    
    Args:
        timestamp: Timestamp en secondes
        
    Returns:
        datetime ou None si invalide
        
    Examples:
        >>> parse_garmin_timestamp(1700000000)
        datetime(2023, 11, 14, 22, 13, 20)
    """
    if not timestamp:
        return None
    
    try:
        return datetime.fromtimestamp(int(timestamp))
    except (ValueError, OSError):
        return None


def parse_garmin_date(date_str: str | None) -> date | None:
    """
    Parse une date au format Garmin (YYYY-MM-DD).
    
    Args:
        date_str: Chaîne de date
        
    Returns:
        date ou None si invalide
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_activity_data(raw_data: dict) -> dict:
    """
    Parse les données brutes d'une activité Garmin.
    
    Args:
        raw_data: Données brutes de l'API
        
    Returns:
        Dict avec les données normalisées
        
    Examples:
        >>> parse_activity_data({"activityId": "123", "durationInSeconds": 3600})
        {"garmin_id": "123", "duree_secondes": 3600, ...}
    """
    garmin_id = str(raw_data.get("activityId") or raw_data.get("summaryId") or "unknown")
    
    # Type d'activité
    activity_type = raw_data.get("activityType", "other")
    if isinstance(activity_type, dict):
        activity_type = activity_type.get("typeKey", "other")
    activity_type = str(activity_type).lower()
    
    # Timestamp de début
    start_time = raw_data.get("startTimeInSeconds", 0)
    date_debut = parse_garmin_timestamp(start_time) or datetime.utcnow()
    
    # Durée avec fallback minimum
    duree = raw_data.get("durationInSeconds", 0) or 1
    
    return {
        "garmin_id": garmin_id,
        "type_activite": activity_type,
        "type_activite_fr": translate_activity_type(activity_type),
        "nom": raw_data.get("activityName") or f"Activité {translate_activity_type(activity_type)}",
        "description": raw_data.get("description"),
        "date_debut": date_debut,
        "duree_secondes": duree,
        "distance_metres": raw_data.get("distanceInMeters"),
        "calories": raw_data.get("activeKilocalories") or raw_data.get("calories"),
        "fc_moyenne": raw_data.get("averageHeartRateInBeatsPerMinute"),
        "fc_max": raw_data.get("maxHeartRateInBeatsPerMinute"),
        "vitesse_moyenne": raw_data.get("averageSpeedInMetersPerSecond"),
        "elevation_gain": raw_data.get("totalElevationGainInMeters"),
        "icon": get_activity_icon(activity_type),
    }


def parse_daily_summary(raw_data: dict) -> dict:
    """
    Parse les données brutes d'un résumé quotidien Garmin.
    
    Args:
        raw_data: Données brutes de l'API
        
    Returns:
        Dict avec les données normalisées
    """
    # Date
    calendar_date = raw_data.get("calendarDate")
    if calendar_date:
        summary_date = parse_garmin_date(calendar_date)
    else:
        start_time = raw_data.get("startTimeInSeconds", 0)
        dt = parse_garmin_timestamp(start_time)
        summary_date = dt.date() if dt else date.today()
    
    return {
        "date": summary_date,
        "pas": raw_data.get("steps", 0),
        "distance_metres": raw_data.get("distanceInMeters", 0),
        "calories_totales": raw_data.get("totalKilocalories", 0),
        "calories_actives": raw_data.get("activeKilocalories", 0),
        "minutes_actives": raw_data.get("moderateIntensityMinutes", 0),
        "minutes_tres_actives": raw_data.get("vigorousIntensityMinutes", 0),
        "fc_repos": raw_data.get("restingHeartRateInBeatsPerMinute"),
        "fc_min": raw_data.get("minHeartRateInBeatsPerMinute"),
        "fc_max": raw_data.get("maxHeartRateInBeatsPerMinute"),
        "stress_moyen": raw_data.get("averageStressLevel"),
        "body_battery_max": raw_data.get("bodyBatteryChargedValue"),
        "body_battery_min": raw_data.get("bodyBatteryDrainedValue"),
    }


# ═══════════════════════════════════════════════════════════
# TRADUCTION ET AFFICHAGE
# ═══════════════════════════════════════════════════════════


def translate_activity_type(activity_type: str) -> str:
    """
    Traduit un type d'activité Garmin en français.
    
    Args:
        activity_type: Type d'activité en anglais
        
    Returns:
        Type d'activité en français
        
    Examples:
        >>> translate_activity_type("running")
        'course'
    """
    return ACTIVITY_TYPE_MAPPING.get(activity_type.lower(), activity_type)


def get_activity_icon(activity_type: str) -> str:
    """
    Retourne l'icône pour un type d'activité.
    
    Args:
        activity_type: Type d'activité
        
    Returns:
        Emoji représentant l'activité
    """
    return ACTIVITY_ICONS.get(activity_type.lower(), "🏅")


def format_duration(seconds: int | float) -> str:
    """
    Formate une durée en secondes pour l'affichage.
    
    Args:
        seconds: Durée en secondes
        
    Returns:
        Chaîne formatée (ex: "1h 30m" ou "45m")
        
    Examples:
        >>> format_duration(5400)
        '1h 30m'
        >>> format_duration(1800)
        '30m'
    """
    if not seconds or seconds <= 0:
        return "0m"
    
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def format_distance(meters: float | None) -> str:
    """
    Formate une distance en mètres pour l'affichage.
    
    Args:
        meters: Distance en mètres
        
    Returns:
        Chaîne formatée (km ou m selon la valeur)
        
    Examples:
        >>> format_distance(5000)
        '5.00 km'
        >>> format_distance(500)
        '500 m'
    """
    if not meters:
        return "0 m"
    
    if meters >= 1000:
        return f"{meters / 1000:.2f} km"
    return f"{int(meters)} m"


def format_pace(seconds_per_meter: float | None) -> str:
    """
    Formate une allure en min/km.
    
    Args:
        seconds_per_meter: Vitesse en secondes par mètre
        
    Returns:
        Allure formatée (min:sec /km)
    """
    if not seconds_per_meter or seconds_per_meter <= 0:
        return "N/A"
    
    # Convertir en secondes par km
    seconds_per_km = seconds_per_meter * 1000
    
    minutes = int(seconds_per_km // 60)
    seconds = int(seconds_per_km % 60)
    
    return f"{minutes}:{seconds:02d} /km"


def format_speed(meters_per_second: float | None) -> str:
    """
    Formate une vitesse en km/h.
    
    Args:
        meters_per_second: Vitesse en m/s
        
    Returns:
        Vitesse formatée en km/h
    """
    if not meters_per_second or meters_per_second <= 0:
        return "0 km/h"
    
    kmh = meters_per_second * 3.6
    return f"{kmh:.1f} km/h"


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
    reference_date: date | None = None
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
        return "✨", "1 semaine"
    
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
    activity_type: str,
    duration_seconds: int,
    weight_kg: float = 70.0
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
    # MET values (approximations)
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
    
    # Calories = MET * weight_kg * hours
    return int(met * weight_kg * hours)


def calculate_weekly_summary(
    daily_summaries: list[dict],
    week_start: date | None = None
) -> dict:
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
        s for s in daily_summaries
        if s.get("date") and week_start <= s["date"] <= week_end
    ]
    
    stats = calculate_daily_stats(week_summaries)
    
    # Jours avec objectif atteint
    days_goal_reached = sum(
        1 for s in week_summaries
        if s.get("pas", 0) >= STEPS_GOAL_DEFAULT
    )
    
    return {
        **stats,
        "semaine_debut": week_start,
        "semaine_fin": week_end,
        "jours_objectif_atteint": days_goal_reached,
        "jours_manquants": 7 - len(week_summaries),
    }


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def validate_oauth_config(config: dict) -> tuple[bool, list[str]]:
    """
    Valide la configuration OAuth Garmin.
    
    Args:
        config: Dict avec les clés de configuration
        
    Returns:
        Tuple (is_valid, list_of_errors)
    """
    errors = []
    
    required_keys = [
        "consumer_key",
        "consumer_secret",
        "request_token_url",
        "access_token_url",
        "authorize_url",
    ]
    
    for key in required_keys:
        if not config.get(key):
            errors.append(f"Clé manquante: {key}")
    
    # Vérifier les URLs
    url_keys = ["request_token_url", "access_token_url", "authorize_url", "api_base_url"]
    for key in url_keys:
        url = config.get(key, "")
        if url and not url.startswith("https://"):
            errors.append(f"URL non sécurisée: {key} doit commencer par https://")
    
    return len(errors) == 0, errors


def validate_garmin_token(token_data: dict) -> tuple[bool, str]:
    """
    Valide qu'un token Garmin est utilisable.
    
    Args:
        token_data: Dict avec oauth_token, oauth_token_secret
        
    Returns:
        Tuple (is_valid, error_message)
    """
    if not token_data:
        return False, "Aucun token fourni"
    
    if not token_data.get("oauth_token"):
        return False, "oauth_token manquant"
    
    if not token_data.get("oauth_token_secret"):
        return False, "oauth_token_secret manquant"
    
    # Vérifier l'expiration si présente
    expires_at = token_data.get("expires_at")
    if expires_at:
        if isinstance(expires_at, datetime):
            if expires_at < datetime.utcnow():
                return False, "Token expiré"
        elif isinstance(expires_at, (int, float)):
            if datetime.fromtimestamp(expires_at) < datetime.utcnow():
                return False, "Token expiré"
    
    return True, ""


def is_sync_needed(
    last_sync: datetime | None,
    min_interval_minutes: int = 30
) -> bool:
    """
    Détermine si une synchronisation est nécessaire.
    
    Args:
        last_sync: Date/heure de la dernière sync
        min_interval_minutes: Intervalle minimum entre syncs
        
    Returns:
        True si une sync est nécessaire
    """
    if last_sync is None:
        return True
    
    elapsed = datetime.utcnow() - last_sync
    return elapsed > timedelta(minutes=min_interval_minutes)


# ═══════════════════════════════════════════════════════════
# GÉNÉRATION DE DATES ET PÉRIODES
# ═══════════════════════════════════════════════════════════


def get_sync_date_range(days_back: int = 7) -> tuple[date, date]:
    """
    Calcule la plage de dates pour la synchronisation.
    
    Args:
        days_back: Nombre de jours en arrière
        
    Returns:
        Tuple (start_date, end_date)
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date


def date_to_garmin_timestamp(d: date) -> int:
    """
    Convertit une date en timestamp Garmin (début de journée).
    
    Args:
        d: Date à convertir
        
    Returns:
        Timestamp en secondes
    """
    return int(datetime.combine(d, datetime.min.time()).timestamp())


def build_api_params(start_date: date, end_date: date) -> dict:
    """
    Construit les paramètres de requête API Garmin.
    
    Args:
        start_date: Date de début
        end_date: Date de fin
        
    Returns:
        Dict de paramètres pour l'API
    """
    return {
        "uploadStartTimeInSeconds": date_to_garmin_timestamp(start_date),
        "uploadEndTimeInSeconds": int(
            datetime.combine(end_date, datetime.max.time()).timestamp()
        ),
    }
