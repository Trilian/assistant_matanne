"""
Constantes globales - Valeurs réutilisées dans toute l'app
"""

# ═══════════════════════════════════════════════════════════
# CUISINE - RECETTES
# ═══════════════════════════════════════════════════════════

DIFFICULTES = ["facile", "moyen", "difficile"]

TYPES_REPAS = [
    "petit_déjeuner",
    "déjeuner",
    "goûter",
    "dîner",
    "bébé"
]

SAISONS = [
    "printemps",
    "été",
    "automne",
    "hiver",
    "toute_année"
]

# ═══════════════════════════════════════════════════════════
# CUISINE - INVENTAIRE
# ═══════════════════════════════════════════════════════════

CATEGORIES_INGREDIENTS = [
    "Fruits & Légumes",
    "Viandes & Poissons",
    "Produits Laitiers",
    "Féculents & Céréales",
    "Épices & Condiments",
    "Conserves",
    "Surgelés",
    "Boulangerie",
    "Boissons",
    "Bébé",
    "Autre"
]

EMPLACEMENTS = [
    "Frigo",
    "Congélateur",
    "Placard",
    "Cave",
    "Garde-manger",
    "Plan de travail"
]

UNITES_MESURE = ["pcs", "kg", "g", "L", "mL", "cl"]

# ═══════════════════════════════════════════════════════════
# CUISINE - COURSES
# ═══════════════════════════════════════════════════════════

PRIORITES_COURSES = ["haute", "moyenne", "basse"]

MAGASINS = {
    "Carrefour": {"couleur": "#0066CC"},
    "Leclerc": "#FF6600",
    "Auchan": "#DD0000",
    "Intermarché": "#FF8800",
    "Casino": "#006633",
    "Lidl": "#0050AA",
    "Aldi": "#0077CC",
    "Biocoop": "#88CC00",
    "Marché": "#44AA44"
}

# ═══════════════════════════════════════════════════════════
# CUISINE - PLANNING
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche"
]

STATUTS_REPAS = ["planifié", "préparé", "terminé", "annulé"]

# ═══════════════════════════════════════════════════════════
# UI - COULEURS
# ═══════════════════════════════════════════════════════════

COLORS = {
    "success": "#4CAF50",
    "warning": "#FFC107",
    "error": "#f44336",
    "info": "#2196F3",
    "primary": "#2d4d36",
    "secondary": "#5e7a6a",
    "accent": "#4caf50"
}

STATUT_COLORS = {
    "ok": "#4CAF50",
    "sous_seuil": "#FFC107",
    "peremption_proche": "#FF9800",
    "critique": "#f44336"
}

# ═══════════════════════════════════════════════════════════
# FORMATS & LIMITES
# ═══════════════════════════════════════════════════════════

DATE_FORMAT_SHORT = "%d/%m"
DATE_FORMAT_MEDIUM = "%d/%m/%Y"
DATE_FORMAT_LONG = "%d %B %Y"

MAX_STRING_LENGTH = 200
MAX_TEXT_LENGTH = 2000
MAX_UPLOAD_SIZE_MB = 10

# ═══════════════════════════════════════════════════════════
# REGEX PATTERNS
# ═══════════════════════════════════════════════════════════

EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$'