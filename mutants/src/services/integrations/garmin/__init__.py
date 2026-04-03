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

from .service import (
    # Service principal
    ServiceGarmin,
    # Configuration
    get_garmin_config,
    get_garmin_service,
    # Helpers utilisateurs
    get_or_create_user,
    get_user_by_username,
    init_family_users,
    list_all_users,
    # Factories
    obtenir_service_garmin,
)
from .types import (
    ACTIVE_MINUTES_GOAL,
    ACTIVITY_ICONS,
    # Constantes
    ACTIVITY_TYPE_MAPPING,
    CALORIES_GOAL_DEFAULT,
    METERS_TO_KM,
    SECONDS_TO_HOURS,
    SECONDS_TO_MINUTES,
    STEPS_GOAL_DEFAULT,
    STREAK_BADGE_THRESHOLDS,
    GarminConfig,
)
from .utils_format import (
    format_distance,
    format_duration,
    format_pace,
    format_speed,
)
from .utils_parsing import (
    get_activity_icon,
    parse_activity_data,
    parse_daily_summary,
    parse_garmin_date,
    parse_garmin_timestamp,
    translate_activity_type,
)
from .utils_stats import (
    calculate_activity_stats,
    calculate_daily_stats,
    calculate_goal_progress,
    calculate_streak,
    calculate_weekly_summary,
    estimate_calories_burned,
    get_streak_badge,
)
from .utils_sync import (
    build_api_params,
    date_to_garmin_timestamp,
    get_sync_date_range,
    is_sync_needed,
    validate_garmin_token,
    validate_oauth_config,
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
    # Factories
    "obtenir_service_garmin",
    "get_garmin_service",
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
