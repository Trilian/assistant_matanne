"""
Constantes pour le batch cooking.

Définit les robots de cuisine, les jours de la semaine et autres valeurs de référence.
"""

# Jours de la semaine (index 0 = Lundi)
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# Robots de cuisine disponibles avec leurs caractéristiques
ROBOTS_DISPONIBLES = {
    "cookeo": {"nom": "Cookeo", "emoji": "ðŸ²", "parallele": True},
    "monsieur_cuisine": {"nom": "Monsieur Cuisine", "emoji": "ðŸ¤–", "parallele": True},
    "airfryer": {"nom": "Airfryer", "emoji": "ðŸŸ", "parallele": True},
    "multicooker": {"nom": "Multicooker", "emoji": "â™¨ï¸", "parallele": True},
    "four": {"nom": "Four", "emoji": "ðŸ”¥", "parallele": True},
    "plaques": {"nom": "Plaques", "emoji": "ðŸ³", "parallele": False},
    "robot_patissier": {"nom": "Robot Pâtissier", "emoji": "ðŸŽ‚", "parallele": True},
    "mixeur": {"nom": "Mixeur", "emoji": "ðŸ¥¤", "parallele": False},
    "hachoir": {"nom": "Hachoir", "emoji": "ðŸ”ª", "parallele": False},
}

# Alias pour rétrocompatibilité
ROBOTS_CUISINE = ROBOTS_DISPONIBLES


__all__ = [
    "JOURS_SEMAINE",
    "ROBOTS_DISPONIBLES",
    "ROBOTS_CUISINE",
]
