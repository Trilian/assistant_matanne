"""
Constants - Toutes les Constantes de l'Application
Centralise les magic numbers et strings
"""

# ═══════════════════════════════════════════════════════════
# DATABASE
# ═══════════════════════════════════════════════════════════

DB_CONNECTION_RETRY = 3
DB_CONNECTION_TIMEOUT = 10
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10

# ═══════════════════════════════════════════════════════════
# CACHE
# ═══════════════════════════════════════════════════════════

# TTL par module (secondes)
CACHE_TTL_RECETTES = 3600  # 1h
CACHE_TTL_INVENTAIRE = 1800  # 30min
CACHE_TTL_COURSES = 1800  # 30min
CACHE_TTL_PLANNING = 7200  # 2h
CACHE_TTL_AI = 3600  # 1h

# Tailles max
CACHE_MAX_SIZE = 100
CACHE_MAX_ITEMS_PER_KEY = 1000

# ═══════════════════════════════════════════════════════════
# AI / API
# ═══════════════════════════════════════════════════════════

# Rate Limiting
AI_RATE_LIMIT_DAILY = 100
AI_RATE_LIMIT_HOURLY = 30
AI_RATE_LIMIT_PER_MINUTE = 10

# Timeouts (secondes)
AI_API_TIMEOUT = 60
AI_API_RETRY_DELAY = 2
AI_API_MAX_RETRIES = 3

# Tokens
AI_MAX_TOKENS_DEFAULT = 1000
AI_MAX_TOKENS_LONG = 3000
AI_MAX_TOKENS_SHORT = 500

# Température
AI_TEMPERATURE_CREATIVE = 0.9
AI_TEMPERATURE_DEFAULT = 0.7
AI_TEMPERATURE_PRECISE = 0.3

# Cache Sémantique
AI_SEMANTIC_SIMILARITY_THRESHOLD = 0.85
AI_SEMANTIC_CACHE_MAX_SIZE = 100

# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

# Longueurs max
MAX_LENGTH_SHORT = 100
MAX_LENGTH_MEDIUM = 200
MAX_LENGTH_LONG = 1000
MAX_LENGTH_TEXT = 2000

# Limites numériques
MAX_PORTIONS = 20
MAX_TEMPS_PREPARATION = 300  # minutes
MAX_TEMPS_CUISSON = 300
MAX_QUANTITE = 10000
MAX_QUANTITE_MIN = 1000

# Recettes
MIN_INGREDIENTS = 1
MAX_INGREDIENTS = 50
MIN_ETAPES = 1
MAX_ETAPES = 50

# ═══════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════

ITEMS_PER_PAGE_DEFAULT = 20
ITEMS_PER_PAGE_RECETTES = 12
ITEMS_PER_PAGE_INVENTAIRE = 20
ITEMS_PER_PAGE_COURSES = 30
ITEMS_PER_PAGE_PLANNING = 10

MAX_ITEMS_SEARCH = 100
MAX_ITEMS_EXPORT = 1000

# ═══════════════════════════════════════════════════════════
# UI
# ═══════════════════════════════════════════════════════════

# Feedback
TOAST_DURATION_SHORT = 2  # secondes
TOAST_DURATION_MEDIUM = 3
TOAST_DURATION_LONG = 5

SPINNER_ESTIMATED_SECONDS_SHORT = 2
SPINNER_ESTIMATED_SECONDS_MEDIUM = 5
SPINNER_ESTIMATED_SECONDS_LONG = 10

# Navigation
MAX_NAVIGATION_HISTORY = 50
MAX_BREADCRUMB_ITEMS = 5

# ═══════════════════════════════════════════════════════════
# BUSINESS RULES
# ═══════════════════════════════════════════════════════════

# Planning
JOURS_SEMAINE = 7
PLANNING_SEMAINE_DEBUT_JOUR = 0  # Lundi

# Inventaire
INVENTAIRE_SEUIL_CRITIQUE_RATIO = 0.5  # 50% du seuil
INVENTAIRE_JOURS_PEREMPTION_ALERTE = 7

# Courses
COURSES_PRIORITE_DEFAULT = "moyenne"

# Recettes
RECETTE_TEMPS_RAPIDE_MAX = 30  # minutes
RECETTE_PORTIONS_DEFAULT = 4

# Jardin
JARDIN_FREQUENCE_ARROSAGE_DEFAULT = 2  # jours

# Projets
PROJET_PROGRESSION_MIN = 0  # %
PROJET_PROGRESSION_MAX = 100

# ═══════════════════════════════════════════════════════════
# FILES & IMAGES
# ═══════════════════════════════════════════════════════════

# Images
IMAGE_MAX_WIDTH = 800  # pixels
IMAGE_MAX_HEIGHT = 600
IMAGE_THUMBNAIL_SIZE = 200
IMAGE_JPEG_QUALITY = 85
IMAGE_WEBP_QUALITY = 80

# Export
EXPORT_CSV_ENCODING = "utf-8"
EXPORT_JSON_INDENT = 2

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════

LOG_LEVEL_PRODUCTION = "INFO"
LOG_LEVEL_DEVELOPMENT = "DEBUG"
LOG_MAX_SIZE_MB = 10
LOG_BACKUP_COUNT = 5

# ═══════════════════════════════════════════════════════════
# SECURITY
# ═══════════════════════════════════════════════════════════

# Password (si auth ajoutée)
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

# Session
SESSION_TIMEOUT_MINUTES = 60

# Input Sanitization
SANITIZE_MAX_LENGTH_DEFAULT = 1000

# ═══════════════════════════════════════════════════════════
# MONITORING
# ═══════════════════════════════════════════════════════════

HEALTH_CHECK_INTERVAL_SECONDS = 60
METRICS_FLUSH_INTERVAL_SECONDS = 30

# ═══════════════════════════════════════════════════════════
# CATEGORIES & ENUMS (Business Constants)
# ═══════════════════════════════════════════════════════════

# Recettes
DIFFICULTES = ["facile", "moyen", "difficile"]
SAISONS = ["printemps", "été", "automne", "hiver", "toute_année"]
TYPES_REPAS = ["petit_déjeuner", "déjeuner", "dîner", "goûter"]

# Inventaire
CATEGORIES_INVENTAIRE = [
    "Légumes",
    "Fruits",
    "Féculents",
    "Protéines",
    "Laitier",
    "Épices & Condiments",
    "Conserves",
    "Surgelés",
    "Autre"
]

EMPLACEMENTS_INVENTAIRE = [
    "Frigo",
    "Congélateur",
    "Placard",
    "Cave",
    "Garde-manger"
]

# Courses
PRIORITES = ["haute", "moyenne", "basse"]

MAGASINS = [
    "Grand Frais",
    "Thiriet",
    "Cora",
    "Carrefour",
    "Auchan",
    "Lidl",
    "Autre"
]

# Planning
STATUTS_REPAS = ["planifié", "en_cours", "terminé", "annulé"]
STATUTS_PLANNING = ["brouillon", "actif", "archivé"]

# Projets
STATUTS_PROJET = ["à faire", "en cours", "terminé", "annulé"]
PRIORITES_PROJET = ["basse", "moyenne", "haute", "urgente"]

# Jardin
CATEGORIES_JARDIN = [
    "Légumes",
    "Fruits",
    "Herbes aromatiques",
    "Fleurs",
    "Arbres",
    "Autre"
]

# ═══════════════════════════════════════════════════════════
# MESSAGES UTILISATEUR
# ═══════════════════════════════════════════════════════════

MSG_SUCCESS_CREATE = "✅ {item} créé avec succès"
MSG_SUCCESS_UPDATE = "✅ {item} mis à jour"
MSG_SUCCESS_DELETE = "🗑️ {item} supprimé"

MSG_ERROR_NOT_FOUND = "❌ {item} introuvable"
MSG_ERROR_INVALID_DATA = "❌ Données invalides"
MSG_ERROR_REQUIRED_FIELD = "⚠️ {field} est requis"
MSG_ERROR_DB_CONNECTION = "❌ Erreur de connexion à la base de données"
MSG_ERROR_AI_SERVICE = "🤖 Service IA temporairement indisponible"
MSG_ERROR_RATE_LIMIT = "⏳ Limite d'appels atteinte, réessayez plus tard"

MSG_WARNING_STOCK_BAS = "⚠️ Stock bas : {item}"
MSG_WARNING_PEREMPTION = "⏳ {item} périme bientôt"

MSG_INFO_EMPTY_LIST = "Aucun élément à afficher"
MSG_INFO_LOADING = "⏳ Chargement en cours..."

# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════

def get_cache_ttl(module: str) -> int:
    """Retourne TTL cache selon module"""
    ttl_map = {
        "recettes": CACHE_TTL_RECETTES,
        "inventaire": CACHE_TTL_INVENTAIRE,
        "courses": CACHE_TTL_COURSES,
        "planning": CACHE_TTL_PLANNING,
        "ai": CACHE_TTL_AI,
    }
    return ttl_map.get(module, CACHE_TTL_RECETTES)


def get_items_per_page(module: str) -> int:
    """Retourne pagination selon module"""
    pagination_map = {
        "recettes": ITEMS_PER_PAGE_RECETTES,
        "inventaire": ITEMS_PER_PAGE_INVENTAIRE,
        "courses": ITEMS_PER_PAGE_COURSES,
        "planning": ITEMS_PER_PAGE_PLANNING,
    }
    return pagination_map.get(module, ITEMS_PER_PAGE_DEFAULT)


def is_temps_rapide(temps_minutes: int) -> bool:
    """Vérifie si temps de recette est rapide"""
    return temps_minutes <= RECETTE_TEMPS_RAPIDE_MAX


def is_stock_critique(quantite: float, seuil: float) -> bool:
    """Vérifie si stock est critique"""
    return quantite < (seuil * INVENTAIRE_SEUIL_CRITIQUE_RATIO)