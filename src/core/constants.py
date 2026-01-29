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

DB_POOL_SIZE = 5
"""Taille du pool de connexions."""

DB_MAX_OVERFLOW = 10
"""Nombre maximum de connexions en overflow."""

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

AI_RATE_LIMIT_PER_MINUTE = 10
"""Limite d'appels IA par minute."""

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
# UI / FEEDBACK
# ═══════════════════════════════════════════════════════════

TOAST_DURATION_SHORT = 2
"""Durée d'affichage toast courte (secondes)."""

TOAST_DURATION_MEDIUM = 3
"""Durée d'affichage toast moyenne (secondes)."""

TOAST_DURATION_LONG = 5
"""Durée d'affichage toast longue (secondes)."""

SPINNER_ESTIMATED_SECONDS_SHORT = 2
"""Estimation spinner courte (secondes)."""

SPINNER_ESTIMATED_SECONDS_MEDIUM = 5
"""Estimation spinner moyenne (secondes)."""

SPINNER_ESTIMATED_SECONDS_LONG = 10
"""Estimation spinner longue (secondes)."""

MAX_NAVIGATION_HISTORY = 50
"""Taille maximale de l'historique de navigation."""

MAX_BREADCRUMB_ITEMS = 5
"""Nombre maximum d'items dans le fil d'Ariane."""

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
# IMAGES
# ═══════════════════════════════════════════════════════════

IMAGE_MAX_WIDTH = 800
"""Largeur maximale d'image (pixels)."""

IMAGE_MAX_HEIGHT = 600
"""Hauteur maximale d'image (pixels)."""

IMAGE_THUMBNAIL_SIZE = 200
"""Taille des miniatures (pixels)."""

IMAGE_JPEG_QUALITY = 85
"""Qualité JPEG (0-100)."""

IMAGE_WEBP_QUALITY = 80
"""Qualité WebP (0-100)."""

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

LOG_LEVEL_DEVELOPMENT = "DEBUG"
"""Niveau de log en développement."""

LOG_MAX_SIZE_MB = 10
"""Taille maximale des fichiers de log (MB)."""

LOG_BACKUP_COUNT = 5
"""Nombre de fichiers de log à conserver."""

# ═══════════════════════════════════════════════════════════
# SÉCURITÉ
# ═══════════════════════════════════════════════════════════

PASSWORD_MIN_LENGTH = 8
"""Longueur minimale de mot de passe."""

PASSWORD_MAX_LENGTH = 128
"""Longueur maximale de mot de passe."""

SESSION_TIMEOUT_MINUTES = 60
"""Durée de session en minutes."""

SANITIZE_MAX_LENGTH_DEFAULT = 1000
"""Longueur maximale par défaut pour sanitization."""

# ═══════════════════════════════════════════════════════════
# MONITORING
# ═══════════════════════════════════════════════════════════

HEALTH_CHECK_INTERVAL_SECONDS = 60
"""Intervalle de health check (secondes)."""

METRICS_FLUSH_INTERVAL_SECONDS = 30
"""Intervalle de flush des métriques (secondes)."""

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

# ═══════════════════════════════════════════════════════════
# MESSAGES UTILISATEUR
# ═══════════════════════════════════════════════════════════

MSG_SUCCESS_CREATE = "✅ {item} créé avec succès"
"""Message de succès création."""

MSG_SUCCESS_UPDATE = "✅ {item} mis à jour"
"""Message de succès mise à jour."""

MSG_SUCCESS_DELETE = "🗑️ {item} supprimé"
"""Message de succès suppression."""

MSG_ERROR_NOT_FOUND = "❌ {item} introuvable"
"""Message d'erreur élément non trouvé."""

MSG_ERROR_INVALID_DATA = "❌ Données invalides"
"""Message d'erreur données invalides."""

MSG_ERROR_REQUIRED_FIELD = "⚠️ {field} est requis"
"""Message d'erreur champ requis."""

MSG_ERROR_DB_CONNECTION = "❌ Erreur de connexion à la base de données"
"""Message d'erreur connexion DB."""

MSG_ERROR_AI_SERVICE = "🤖 Service IA temporairement indisponible"
"""Message d'erreur service IA."""

MSG_ERROR_RATE_LIMIT = "⏳ Limite d'appels atteinte, réessayez plus tard"
"""Message d'erreur rate limit."""

MSG_WARNING_STOCK_BAS = "⚠️ Stock bas : {item}"
"""Message d'alerte stock bas."""

MSG_WARNING_PEREMPTION = "⏳ {item} périme bientôt"
"""Message d'alerte péremption proche."""

MSG_INFO_EMPTY_LIST = "Aucun élément à afficher"
"""Message d'information liste vide."""

MSG_INFO_LOADING = "⏳ Chargement en cours..."
"""Message d'information chargement."""

# ═══════════════════════════════════════════════════════════
# FONCTIONS HELPERS
# ═══════════════════════════════════════════════════════════


def obtenir_cache_ttl(module: str) -> int:
    """
    Retourne le TTL de cache selon le module.

    Args:
        module: Nom du module (ex: "recettes", "inventaire")

    Returns:
        TTL en secondes
    """
    ttl_map = {
        "recettes": CACHE_TTL_RECETTES,
        "inventaire": CACHE_TTL_INVENTAIRE,
        "courses": CACHE_TTL_COURSES,
        "planning": CACHE_TTL_PLANNING,
        "ia": CACHE_TTL_IA,
    }
    return ttl_map.get(module, CACHE_TTL_RECETTES)


def obtenir_items_par_page(module: str) -> int:
    """
    Retourne le nombre d'items par page selon le module.

    Args:
        module: Nom du module

    Returns:
        Nombre d'items par page
    """
    pagination_map = {
        "recettes": ITEMS_PER_PAGE_RECETTES,
        "inventaire": ITEMS_PER_PAGE_INVENTAIRE,
        "courses": ITEMS_PER_PAGE_COURSES,
        "planning": ITEMS_PER_PAGE_PLANNING,
    }
    return pagination_map.get(module, ITEMS_PER_PAGE_DEFAULT)


def est_temps_rapide(temps_minutes: int) -> bool:
    """
    Vérifie si le temps de recette est considéré comme rapide.

    Args:
        temps_minutes: Temps en minutes

    Returns:
        True si rapide
    """
    return temps_minutes <= RECETTE_TEMPS_RAPIDE_MAX


def est_stock_critique(quantite: float, seuil: float) -> bool:
    """
    Vérifie si le stock est critique.

    Args:
        quantite: Quantité actuelle
        seuil: Seuil minimum

    Returns:
        True si critique
    """
    return quantite < (seuil * INVENTAIRE_SEUIL_CRITIQUE_RATIO)
