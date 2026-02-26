"""
Constantes pour le module Énergie.
"""

from src.ui.tokens import Couleur

# Types d'énergie avec configuration d'affichage
TYPES_ENERGIE = {
    "electricite": {
        "label": "⚡ Électricité",
        "unite": "kWh",
        "icon": "⚡",
        "color": Couleur.YELLOW_ENERGY,
    },
    "gaz": {"label": "🔥 Gaz", "unite": "m³", "icon": "🔥", "color": Couleur.ORANGE_ENERGY},
    "eau": {"label": "💧 Eau", "unite": "m³", "icon": "💧", "color": Couleur.INFO},
    "fioul": {"label": "🛢️ Fioul", "unite": "L", "icon": "🛢️", "color": Couleur.BROWN},
}

# Constante attendue par les tests — structure avec emoji/couleur/prix_moyen
ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": Couleur.YELLOW_ENERGY,
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": 0.2276,
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": Couleur.ORANGE_ENERGY,
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": 0.1284,
    },
    "eau": {
        "emoji": "💧",
        "couleur": Couleur.INFO,
        "unite": "m³",
        "label": "Eau",
        "prix_moyen": 4.34,
    },
}

# MOIS_FR: index 0 vide, puis abréviations 1-12
MOIS_FR = [
    "",
    "Jan",
    "Fev",
    "Mar",
    "Avr",
    "Mai",
    "Jun",
    "Jul",
    "Aou",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

MOIS_NOMS = [
    "Janvier",
    "Février",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Décembre",
]
