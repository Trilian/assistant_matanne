"""
Fonctions de parsing et traduction pour les données Garmin.

Parsing des timestamps, dates, activités et résumés quotidiens,
ainsi que la traduction des types d'activité et icônes associées.
"""

from datetime import date, datetime

from .types import (
    ACTIVITY_ICONS,
    ACTIVITY_TYPE_MAPPING,
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
