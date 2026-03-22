"""
Constantes pour le batch cooking.

Définit les robots de cuisine, les jours de la semaine et autres valeurs de référence.
Source unique pour toutes les constantes robots du projet.
"""

# Réexport de JOURS_SEMAINE depuis core/constants pour compatibilité
from src.core.constants import JOURS_SEMAINE

# Robots de cuisine disponibles avec leurs caractéristiques
# Source unique — importée par batch_cooking_temps.py, utils.py, etc.
ROBOTS_INFO = {
    "cookeo": {
        "nom": "Cookeo",
        "emoji": "🍲",
        "peut_parallele": True,
        "description": "Cuiseur multi-fonction",
    },
    "monsieur_cuisine": {
        "nom": "Monsieur Cuisine",
        "emoji": "🤖",
        "peut_parallele": True,
        "description": "Robot cuiseur",
    },
    "airfryer": {
        "nom": "Airfryer",
        "emoji": "🍟",
        "peut_parallele": True,
        "description": "Friteuse sans huile",
    },
    "multicooker": {
        "nom": "Multicooker",
        "emoji": "♨️",
        "peut_parallele": True,
        "description": "Cuiseur polyvalent",
    },
    "four": {
        "nom": "Four",
        "emoji": "🔥",
        "peut_parallele": True,
        "description": "Four traditionnel",
    },
    "plaques": {
        "nom": "Plaques",
        "emoji": "🍳",
        "peut_parallele": False,
        "description": "Plaques de cuisson",
    },
    "robot_patissier": {
        "nom": "Robot Pâtissier",
        "emoji": "🎂",
        "peut_parallele": True,
        "description": "Pour pâtisserie",
    },
    "mixeur": {
        "nom": "Mixeur",
        "emoji": "🥤",
        "peut_parallele": False,
        "description": "Mixeur/blender",
    },
    "hachoir": {
        "nom": "Hachoir",
        "emoji": "🔪",
        "peut_parallele": False,
        "description": "Hachoir electrique",
    },
}

# Alias pour rétrocompatibilité
ROBOTS_DISPONIBLES = ROBOTS_INFO
ROBOTS_CUISINE = ROBOTS_INFO


__all__ = [
    "JOURS_SEMAINE",
    "ROBOTS_INFO",
    "ROBOTS_DISPONIBLES",
    "ROBOTS_CUISINE",
]
