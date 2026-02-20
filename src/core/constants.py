"""
Constantes - Toutes les constantes de l'application.

Ce module centralise tous les "magic numbers" et chaînes constantes
pour faciliter la maintenance et éviter la duplication.
"""

# ═══════════════════════════════════════════════════════════
# BASE DE DONNÉES
# ═══════════════════════════════════════════════════════════

DB_CONNECTION_RETRY = 3
"""Nombre de tentatives de reconnexion DB."""

DB_CONNECTION_TIMEOUT = 10
"""Timeout de connexion DB en secondes."""

# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════

CACHE_TTL_RECETTES = 3600
"""TTL cache recettes (1h). Utilisé comme défaut dans config/settings.py."""

CACHE_TTL_IA = 3600
"""TTL cache réponses IA (1h)."""

CACHE_MAX_SIZE = 100
"""Nombre maximum d'entrées en cache."""

# ═══════════════════════════════════════════════════════════
# IA / API
# ═══════════════════════════════════════════════════════════

AI_RATE_LIMIT_DAILY = 100
"""Limite d'appels IA par jour."""

AI_RATE_LIMIT_HOURLY = 30
"""Limite d'appels IA par heure."""

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

MAX_LENGTH_SHORT = 100
"""Longueur maximale pour chaînes courtes."""

MAX_LENGTH_MEDIUM = 200
"""Longueur maximale pour chaînes moyennes."""

MAX_LENGTH_LONG = 1000
"""Longueur maximale pour chaînes longues."""

MAX_LENGTH_TEXT = 2000
"""Longueur maximale pour texte."""

MAX_PORTIONS = 20
"""Nombre maximum de portions."""

MAX_TEMPS_PREPARATION = 300
"""Temps de préparation maximum en minutes."""

MAX_TEMPS_CUISSON = 300
"""Temps de cuisson maximum en minutes."""

MAX_QUANTITE = 10000
"""Quantité maximale pour articles."""

MIN_INGREDIENTS = 1
"""Nombre minimum d'ingrédients par recette."""

MAX_INGREDIENTS = 50
"""Nombre maximum d'ingrédients par recette."""

MIN_ETAPES = 1
"""Nombre minimum d'étapes par recette."""

MAX_ETAPES = 50
"""Nombre maximum d'étapes par recette."""

# ═══════════════════════════════════════════════════════════
# JOURS DE LA SEMAINE / MOIS
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE: list[str] = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]
"""Noms des jours de la semaine."""

JOURS_SEMAINE_COURT: list[str] = [
    "Lun",
    "Mar",
    "Mer",
    "Jeu",
    "Ven",
    "Sam",
    "Dim",
]
"""Noms courts des jours de la semaine."""

JOURS_SEMAINE_LOWER: list[str] = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]
"""Noms des jours en minuscule (pour sélecteurs UI)."""

MOIS_FRANCAIS: list[str] = [
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Decembre",
]
"""Noms des mois en français."""

MOIS_FRANCAIS_COURT: list[str] = [
    "Jan",
    "Fev",
    "Mar",
    "Avr",
    "Mai",
    "Juin",
    "Juil",
    "Août",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
"""Noms courts des mois."""

TYPES_REPAS_KEYS: list[str] = [
    "petit_dejeuner",
    "dejeuner",
    "gouter",
    "diner",
]
"""Clés techniques pour types de repas."""

TYPES_PROTEINES: dict[str, list[str]] = {
    "poisson": ["poisson", "saumon", "thon", "cabillaud", "sardine", "crevette"],
    "viande_rouge": ["boeuf", "veau", "agneau", "viande rouge"],
    "volaille": ["poulet", "dinde", "canard", "volaille"],
    "vegetarien": ["légumes", "tofu", "seitan", "légumineuses"],
}
"""Types de protéines avec mots-clés associés."""

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

LOG_LEVEL_PRODUCTION = "INFO"
"""Niveau de log en production."""

# ═══════════════════════════════════════════════════════════
# FAMILLE
# ═══════════════════════════════════════════════════════════

from datetime import date as _date  # noqa: E402

JULES_NAISSANCE: _date = _date(2024, 6, 22)
"""Date de naissance de Jules (22 juin 2024)."""

OBJECTIF_PAS_QUOTIDIEN_DEFAUT: int = 10_000
"""Objectif de pas quotidien par défaut."""

OBJECTIF_CALORIES_BRULEES_DEFAUT: int = 500
"""Objectif de calories brûlées par défaut."""
