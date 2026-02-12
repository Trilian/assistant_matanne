"""
Constantes partagees entre tous les modules.

Centralise les constantes dupliquees pour garantir la coherence.
"""

from typing import List

# ═══════════════════════════════════════════════════════════
# JOURS DE LA SEMAINE
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE: List[str] = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]

JOURS_SEMAINE_COURT: List[str] = [
    "Lun",
    "Mar",
    "Mer",
    "Jeu",
    "Ven",
    "Sam",
    "Dim",
]

# Version minuscule pour les selecteurs UI
JOURS_SEMAINE_LOWER: List[str] = [
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

MOIS_FRANCAIS: List[str] = [
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

MOIS_FRANCAIS_COURT: List[str] = [
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

TYPES_REPAS: List[str] = [
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
]
