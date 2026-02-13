"""
Types et schémas pour le service Garmin.
"""

from dataclasses import dataclass

# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════


@dataclass
class GarminConfig:
    """Configuration Garmin API"""

    consumer_key: str
    consumer_secret: str
    request_token_url: str = "https://connectapi.garmin.com/oauth-service/oauth/request_token"
    authorize_url: str = "https://connect.garmin.com/oauthConfirm"
    access_token_url: str = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    api_base_url: str = "https://apis.garmin.com"


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Types d'activités Garmin
ACTIVITY_TYPE_MAPPING = {
    "running": "course",
    "cycling": "vélo",
    "swimming": "natation",
    "walking": "marche",
    "hiking": "randonnée",
    "strength_training": "musculation",
    "cardio_training": "cardio",
    "yoga": "yoga",
    "other": "autre",
    "multi_sport": "multi-sport",
    "elliptical": "elliptique",
    "stair_climbing": "escaliers",
}

# Icônes par type d'activité
ACTIVITY_ICONS = {
    "running": "ðŸƒ",
    "cycling": "ðŸš´",
    "swimming": "ðŸŠ",
    "walking": "ðŸš¶",
    "hiking": "ðŸ¥¾",
    "strength_training": "ðŸ‹ï¸",
    "cardio_training": "ðŸ’ª",
    "yoga": "ðŸ§˜",
    "other": "ðŸ…",
    "multi_sport": "ðŸ†",
}

# Seuils pour les indicateurs
STEPS_GOAL_DEFAULT = 10000
CALORIES_GOAL_DEFAULT = 500
ACTIVE_MINUTES_GOAL = 30
STREAK_BADGE_THRESHOLDS = [7, 14, 30, 60, 100]

# Facteurs de conversion
METERS_TO_KM = 0.001
SECONDS_TO_MINUTES = 60
SECONDS_TO_HOURS = 3600
