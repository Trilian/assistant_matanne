"""
Package de synchronisation Garmin Connect.

Exports:
- ServiceGarmin: Service principal de synchronisation
- GarminService: Alias pour rétrocompatibilité
- obtenir_service_garmin: Factory (convention française)
- get_garmin_service, get_garmin_sync_service: Factory (alias anglais)
- Types: GarminConfig
- Utils: Fonctions utilitaires pures
"""

from .types import (
    GarminConfig,
    # Constantes
    ACTIVITY_TYPE_MAPPING,
    ACTIVITY_ICONS,
    STEPS_GOAL_DEFAULT,
    CALORIES_GOAL_DEFAULT,
    ACTIVE_MINUTES_GOAL,
    STREAK_BADGE_THRESHOLDS,
    METERS_TO_KM,
    SECONDS_TO_MINUTES,
    SECONDS_TO_HOURS,
)

from .utils import (
    # Parsing
    parse_garmin_timestamp,
    parse_garmin_date,
    parse_activity_data,
    parse_daily_summary,
    # Traduction et affichage
    translate_activity_type,
    get_activity_icon,
    format_duration,
    format_distance,
    format_pace,
    format_speed,
    # Calculs et statistiques
    calculate_daily_stats,
    calculate_activity_stats,
    calculate_streak,
    get_streak_badge,
    calculate_goal_progress,
    estimate_calories_burned,
    calculate_weekly_summary,
    # Validation
    validate_oauth_config,
    validate_garmin_token,
    is_sync_needed,
    # Dates et périodes
    get_sync_date_range,
    date_to_garmin_timestamp,
    build_api_params,
)

from .service import (
    # Service principal
    ServiceGarmin,
    GarminService,  # Alias
    # Factories
    obtenir_service_garmin,
    get_garmin_service,
    get_garmin_sync_service,  # Alias rétrocompatibilité
    # Helpers utilisateurs
    get_or_create_user,
    init_family_users,
    get_user_by_username,
    list_all_users,
    # Configuration
    get_garmin_config,
)


__all__ = [
    # Types
    "GarminConfig",
    # Constantes
    "ACTIVITY_TYPE_MAPPING",
    "ACTIVITY_ICONS",
    "STEPS_GOAL_DEFAULT",
    "CALORIES_GOAL_DEFAULT",
    "ACTIVE_MINUTES_GOAL",
    "STREAK_BADGE_THRESHOLDS",
    "METERS_TO_KM",
    "SECONDS_TO_MINUTES",
    "SECONDS_TO_HOURS",
    # Service
    "ServiceGarmin",
    "GarminService",
    # Factories
    "obtenir_service_garmin",
    "get_garmin_service",
    "get_garmin_sync_service",
    # Helpers
    "get_or_create_user",
    "init_family_users",
    "get_user_by_username",
    "list_all_users",
    "get_garmin_config",
    # Utils - Parsing
    "parse_garmin_timestamp",
    "parse_garmin_date",
    "parse_activity_data",
    "parse_daily_summary",
    # Utils - Affichage
    "translate_activity_type",
    "get_activity_icon",
    "format_duration",
    "format_distance",
    "format_pace",
    "format_speed",
    # Utils - Calculs
    "calculate_daily_stats",
    "calculate_activity_stats",
    "calculate_streak",
    "get_streak_badge",
    "calculate_goal_progress",
    "estimate_calories_burned",
    "calculate_weekly_summary",
    # Utils - Validation
    "validate_oauth_config",
    "validate_garmin_token",
    "is_sync_needed",
    # Utils - Dates
    "get_sync_date_range",
    "date_to_garmin_timestamp",
    "build_api_params",
]
