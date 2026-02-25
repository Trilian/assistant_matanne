"""
Constantes pour le module Énergie.
"""

# Types d'énergie avec configuration d'affichage
TYPES_ENERGIE = {
    "electricite": {"label": "⚡ Électricité", "unite": "kWh", "icon": "⚡", "color": "#FFD600"},
    "gaz": {"label": "🔥 Gaz", "unite": "m³", "icon": "🔥", "color": "#FF6D00"},
    "eau": {"label": "💧 Eau", "unite": "m³", "icon": "💧", "color": "#2196F3"},
    "fioul": {"label": "🛢️ Fioul", "unite": "L", "icon": "🛢️", "color": "#795548"},
}

# Constante attendue par les tests — structure avec emoji/couleur/prix_moyen
ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": "#FFD600",
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": 0.2276,
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": "#FF6D00",
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": 0.1284,
    },
    "eau": {
        "emoji": "💧",
        "couleur": "#2196F3",
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
