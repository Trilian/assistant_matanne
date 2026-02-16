"""
Constantes partagees entre tous les modules.

Centralise les constantes dupliquees pour garantir la coherence.
"""


# ═══════════════════════════════════════════════════════════
# JOURS DE LA SEMAINE
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

JOURS_SEMAINE_COURT: list[str] = [
    "Lun",
    "Mar",
    "Mer",
    "Jeu",
    "Ven",
    "Sam",
    "Dim",
]

# Version minuscule pour les selecteurs UI
JOURS_SEMAINE_LOWER: list[str] = [
    "lundi",
    "mardi",
    "mercredi",
    "jeudi",
    "vendredi",
    "samedi",
    "dimanche",
]

# ═══════════════════════════════════════════════════════════
# MOIS DE L'ANNÉE
# ═══════════════════════════════════════════════════════════

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

# ═══════════════════════════════════════════════════════════
# TYPES DE REPAS
# ═══════════════════════════════════════════════════════════

TYPES_REPAS: list[str] = [
    "petit_dejeuner",
    "dejeuner",
    "gouter",
    "diner",
]

# Alias pour compatibilite avec l'ancien code
TYPES_REPAS_AFFICHAGE = {
    "petit_dejeuner": "Petit-dejeuner",
    "dejeuner": "Dejeuner",
    "gouter": "Goûter",
    "diner": "Dîner",
}

# ═══════════════════════════════════════════════════════════
# TYPES DE PROTÉINES
# ═══════════════════════════════════════════════════════════

TYPES_PROTEINES: dict[str, list[str]] = {
    "poisson": ["poisson", "saumon", "thon", "cabillaud", "sardine", "crevette"],
    "viande_rouge": ["boeuf", "veau", "agneau", "viande rouge"],
    "volaille": ["poulet", "dinde", "canard", "volaille"],
    "vegetarien": ["légumes", "tofu", "seitan", "légumineuses"],
}

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    "JOURS_SEMAINE",
    "JOURS_SEMAINE_COURT",
    "JOURS_SEMAINE_LOWER",
    "MOIS_FRANCAIS",
    "MOIS_FRANCAIS_COURT",
    "TYPES_REPAS",
    "TYPES_REPAS_AFFICHAGE",
    "TYPES_PROTEINES",
]
