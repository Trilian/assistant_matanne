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
"""TTL cache recettes (1h)."""

CACHE_TTL_INVENTAIRE = 1800
"""TTL cache inventaire (30min)."""

CACHE_TTL_COURSES = 1800
"""TTL cache courses (30min)."""

CACHE_TTL_PLANNING = 7200
"""TTL cache planning (2h)."""

CACHE_TTL_IA = 3600
"""TTL cache réponses IA (1h)."""

CACHE_MAX_SIZE = 100
"""Nombre maximum d'entrées en cache."""

CACHE_MAX_ITEMS_PER_KEY = 1000
"""Nombre maximum d'items par clé de cache."""

# ═══════════════════════════════════════════════════════════
# IA / API
# ═══════════════════════════════════════════════════════════

AI_RATE_LIMIT_DAILY = 100
"""Limite d'appels IA par jour."""

AI_RATE_LIMIT_HOURLY = 30
"""Limite d'appels IA par heure."""

AI_API_TIMEOUT = 60
"""Timeout API IA en secondes."""

AI_API_RETRY_DELAY = 2
"""Délai entre retries API en secondes."""

AI_API_MAX_RETRIES = 3
"""Nombre maximum de retries API."""

AI_MAX_TOKENS_DEFAULT = 1000
"""Nombre de tokens par défaut."""

AI_MAX_TOKENS_LONG = 3000
"""Nombre de tokens pour réponses longues."""

AI_MAX_TOKENS_SHORT = 500
"""Nombre de tokens pour réponses courtes."""

AI_TEMPERATURE_CREATIVE = 0.9
"""Température pour génération créative."""

AI_TEMPERATURE_DEFAULT = 0.7
"""Température par défaut."""

AI_TEMPERATURE_PRECISE = 0.3
"""Température pour génération précise."""

AI_SEMANTIC_SIMILARITY_THRESHOLD = 0.85
"""Seuil de similarité pour cache sémantique."""

AI_SEMANTIC_CACHE_MAX_SIZE = 100
"""Taille maximale du cache sémantique."""

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

MAX_QUANTITE_MIN = 1000
"""Seuil minimal maximum."""

MIN_INGREDIENTS = 1
"""Nombre minimum d'ingrédients par recette."""

MAX_INGREDIENTS = 50
"""Nombre maximum d'ingrédients par recette."""

MIN_ETAPES = 1
"""Nombre minimum d'étapes par recette."""

MAX_ETAPES = 50
"""Nombre maximum d'étapes par recette."""

# ═══════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════

ITEMS_PER_PAGE_DEFAULT = 20
"""Nombre d'items par page par défaut."""

ITEMS_PER_PAGE_RECETTES = 12
"""Nombre de recettes par page."""

ITEMS_PER_PAGE_INVENTAIRE = 20
"""Nombre d'articles inventaire par page."""

ITEMS_PER_PAGE_COURSES = 30
"""Nombre d'articles courses par page."""

ITEMS_PER_PAGE_PLANNING = 10
"""Nombre de plannings par page."""

MAX_ITEMS_SEARCH = 100
"""Nombre maximum de résultats de recherche."""

MAX_ITEMS_EXPORT = 1000
"""Nombre maximum d'items à exporter."""

# ═══════════════════════════════════════════════════════════
# RÈGLES MÉTIER - CUISINE
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE = 7
"""Nombre de jours dans une semaine."""

PLANNING_SEMAINE_DEBUT_JOUR = 0
"""Jour de début de semaine (0 = lundi)."""

INVENTAIRE_SEUIL_CRITIQUE_RATIO = 0.5
"""Ratio pour stock critique (50% du seuil)."""

INVENTAIRE_JOURS_PEREMPTION_ALERTE = 7
"""Nombre de jours avant péremption pour alerter."""

COURSES_PRIORITE_DEFAULT = "moyenne"
"""Priorité par défaut pour courses."""

RECETTE_TEMPS_RAPIDE_MAX = 30
"""Temps maximum pour une recette rapide (minutes)."""

RECETTE_PORTIONS_DEFAULT = 4
"""Nombre de portions par défaut."""

# ═══════════════════════════════════════════════════════════
# EXPORT
# ═══════════════════════════════════════════════════════════

EXPORT_CSV_ENCODING = "utf-8"
"""Encodage pour export CSV."""

EXPORT_JSON_INDENT = 2
"""Indentation pour export JSON."""

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

LOG_LEVEL_PRODUCTION = "INFO"
"""Niveau de log en production."""

# ═══════════════════════════════════════════════════════════
# CATÉGORIES & ENUMS (Constantes métier)
# ═══════════════════════════════════════════════════════════

DIFFICULTES = ["facile", "moyen", "difficile"]
"""Niveaux de difficulté des recettes."""

SAISONS = ["printemps", "été", "automne", "hiver", "toute_année"]
"""Saisons disponibles."""

TYPES_REPAS = ["petit_déjeuner", "déjeuner", "dîner", "goûter"]
"""Types de repas."""

CATEGORIES_INVENTAIRE = [
    "Légumes",
    "Fruits",
    "Féculents",
    "Protéines",
    "Laitier",
    "Épices & Condiments",
    "Conserves",
    "Surgelés",
    "Autre",
]
"""Catégories d'articles inventaire."""

EMPLACEMENTS_INVENTAIRE = ["Frigo", "Congélateur", "Placard", "Cave", "Garde-manger"]
"""Emplacements de stockage."""

PRIORITES = ["haute", "moyenne", "basse"]
"""Niveaux de priorité."""

MAGASINS = ["Grand Frais", "Thiriet", "Cora", "Carrefour", "Auchan", "Lidl", "Autre"]
"""Liste des magasins."""

STATUTS_REPAS = ["planifié", "en_cours", "terminé", "annulé"]
"""Statuts possibles pour un repas."""

STATUTS_PLANNING = ["brouillon", "actif", "archivé"]
"""Statuts possibles pour un planning."""

STATUTS_PROJET = ["à faire", "en cours", "terminé", "annulé"]
"""Statuts possibles pour un projet."""

PRIORITES_PROJET = ["basse", "moyenne", "haute", "urgente"]
"""Priorités possibles pour un projet."""

CATEGORIES_JARDIN = ["Légumes", "Fruits", "Herbes aromatiques", "Fleurs", "Arbres", "Autre"]
"""Catégories d'éléments de jardin."""
