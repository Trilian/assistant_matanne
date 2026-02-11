"""
Constantes pour le batch cooking.

Définit les robots de cuisine, les jours de la semaine et autres valeurs de référence.
"""

# Jours de la semaine (index 0 = Lundi)
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

# Robots de cuisine disponibles avec leurs caractéristiques
ROBOTS_DISPONIBLES = {
    "cookeo": {"nom": "Cookeo", "emoji": "🍲", "parallele": True},
    "monsieur_cuisine": {"nom": "Monsieur Cuisine", "emoji": "🤖", "parallele": True},
    "airfryer": {"nom": "Airfryer", "emoji": "🍟", "parallele": True},
    "multicooker": {"nom": "Multicooker", "emoji": "♨️", "parallele": True},
    "four": {"nom": "Four", "emoji": "🔥", "parallele": True},
    "plaques": {"nom": "Plaques", "emoji": "🍳", "parallele": False},
    "robot_patissier": {"nom": "Robot Pâtissier", "emoji": "🎂", "parallele": True},
    "mixeur": {"nom": "Mixeur", "emoji": "🥤", "parallele": False},
    "hachoir": {"nom": "Hachoir", "emoji": "🔪", "parallele": False},
}

# Alias pour rétrocompatibilité
ROBOTS_CUISINE = ROBOTS_DISPONIBLES


__all__ = [
    "JOURS_SEMAINE",
    "ROBOTS_DISPONIBLES",
    "ROBOTS_CUISINE",
]
