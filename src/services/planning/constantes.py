"""
Constantes pour le service de planning.

Définit les valeurs de référence pour:
- Jours de la semaine
- Types de repas
- Types de protéines
"""

# ═══════════════════════════════════════════════════════════
# JOURS DE LA SEMAINE
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]

JOURS_SEMAINE_LOWER = [j.lower() for j in JOURS_SEMAINE]


# ═══════════════════════════════════════════════════════════
# TYPES DE REPAS
# ═══════════════════════════════════════════════════════════


TYPES_REPAS = ["petit-dejeuner", "dejeuner", "gouter", "diner"]


# ═══════════════════════════════════════════════════════════
# TYPES DE PROTÉINES
# ═══════════════════════════════════════════════════════════


TYPES_PROTEINES = {
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
    "JOURS_SEMAINE_LOWER",
    "TYPES_REPAS",
    "TYPES_PROTEINES",
]
