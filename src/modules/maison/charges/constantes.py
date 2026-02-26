"""
Charges - Constantes et définitions.

Contient toutes les constantes métier du module charges:
- ENERGIES: Configuration des types d'énergies
- BADGES_DEFINITIONS: Badges gamifiés
- CONSEILS_ECONOMIES: Conseils d'économies
- NIVEAUX_ECO: Niveaux éco-score
"""

from decimal import Decimal

from src.ui.tokens import Couleur

# =============================================================================
# CONSTANTES ÉNERGIE
# =============================================================================

ENERGIES = {
    "electricite": {
        "emoji": "⚡",
        "couleur": Couleur.YELLOW_ALT,
        "unite": "kWh",
        "label": "Électricité",
        "prix_moyen": Decimal("0.22"),
        "conso_moyenne_mois": 400,
    },
    "gaz": {
        "emoji": "🔥",
        "couleur": Couleur.DANGER,
        "unite": "m³",
        "label": "Gaz",
        "prix_moyen": Decimal("0.11"),
        "conso_moyenne_mois": 150,
    },
    "eau": {
        "emoji": "💧",
        "couleur": Couleur.INFO,
        "unite": "m³",
        "label": "Eau",
        "prix_moyen": Decimal("4.50"),
        "conso_moyenne_mois": 10,
    },
}

# Définitions des badges gamifiés
BADGES_DEFINITIONS = [
    {
        "id": "econome_eau",
        "nom": "Économe en eau",
        "emoji": "💧",
        "description": "Consommation eau -20% vs moyenne",
        "condition": lambda stats: stats.get("eau_ratio", 1) < 0.8,
        "categorie": "eau",
    },
    {
        "id": "econome_elec",
        "nom": "Électricité maîtrisée",
        "emoji": "⚡",
        "description": "Consommation élec -15% vs moyenne",
        "condition": lambda stats: stats.get("elec_ratio", 1) < 0.85,
        "categorie": "energie",
    },
    {
        "id": "econome_gaz",
        "nom": "Chauffage optimisé",
        "emoji": "🔥",
        "description": "Consommation gaz -10% vs moyenne",
        "condition": lambda stats: stats.get("gaz_ratio", 1) < 0.9,
        "categorie": "energie",
    },
    {
        "id": "streak_7",
        "nom": "Série de 7 jours",
        "emoji": "🔥",
        "description": "7 jours consécutifs sous la moyenne",
        "condition": lambda stats: stats.get("streak", 0) >= 7,
        "categorie": "general",
    },
    {
        "id": "streak_30",
        "nom": "Champion du mois",
        "emoji": "🏆",
        "description": "30 jours sous la moyenne",
        "condition": lambda stats: stats.get("streak", 0) >= 30,
        "categorie": "general",
    },
    {
        "id": "premiere_facture",
        "nom": "Premier pas",
        "emoji": "🎯",
        "description": "Première facture enregistrée",
        "condition": lambda stats: stats.get("nb_factures", 0) >= 1,
        "categorie": "general",
    },
    {
        "id": "suivi_complet",
        "nom": "Suivi complet",
        "emoji": "📊",
        "description": "Les 3 énergies suivies",
        "condition": lambda stats: stats.get("energies_suivies", 0) >= 3,
        "categorie": "general",
    },
    {
        "id": "eco_warrior",
        "nom": "Éco-warrior",
        "emoji": "🌿",
        "description": "Score éco ≥ 80",
        "condition": lambda stats: stats.get("eco_score", 0) >= 80,
        "categorie": "general",
    },
]

# Conseils d'économies par énergie
CONSEILS_ECONOMIES = {
    "electricite": [
        {
            "emoji": "💡",
            "titre": "Passez aux LED",
            "desc": "Économie ~80% sur l'éclairage",
            "economie": "40€/an",
        },
        {
            "emoji": "🔌",
            "titre": "Multiprises à interrupteur",
            "desc": "Évitez les appareils en veille",
            "economie": "50€/an",
        },
        {
            "emoji": "🌡️",
            "titre": "Thermostat intelligent",
            "desc": "Chauffage optimisé = -15% facture",
            "economie": "200€/an",
        },
        {
            "emoji": "🧊",
            "titre": "Dégivrez régulièrement",
            "desc": "Un frigo givré consomme +30%",
            "economie": "30€/an",
        },
        {
            "emoji": "🌀",
            "titre": "Lavage froid",
            "desc": "Laver à 30°C au lieu de 60°C",
            "economie": "25€/an",
        },
    ],
    "gaz": [
        {
            "emoji": "🌡️",
            "titre": "Baissez d'1°C",
            "desc": "Économie de 7% sur le chauffage",
            "economie": "150€/an",
        },
        {
            "emoji": "🏠",
            "titre": "Isolation",
            "desc": "30% de pertes par le toit non isolé",
            "economie": "400€/an",
        },
        {
            "emoji": "🚿",
            "titre": "Douche < bain",
            "desc": "50L vs 150L d'eau chaude",
            "economie": "100€/an",
        },
        {
            "emoji": "🔧",
            "titre": "Entretien chaudière",
            "desc": "Une chaudière bien réglée = -10%",
            "economie": "120€/an",
        },
    ],
    "eau": [
        {
            "emoji": "🚿",
            "titre": "Douche courte",
            "desc": "5 min = 60L vs 200L bain",
            "economie": "200€/an",
        },
        {
            "emoji": "💧",
            "titre": "Mousseurs",
            "desc": "Économisez 50% sur les robinets",
            "economie": "50€/an",
        },
        {
            "emoji": "🌧️",
            "titre": "Récupérateur d'eau",
            "desc": "Pour l'arrosage du jardin",
            "economie": "100€/an",
        },
        {
            "emoji": "🔧",
            "titre": "Réparez les fuites",
            "desc": "Un robinet = 120L/jour perdus",
            "economie": "150€/an",
        },
    ],
}

# Niveaux éco-score
NIVEAUX_ECO = [
    {"min": 90, "nom": "Éco-Champion", "emoji": "🏆", "class": "gold"},
    {"min": 75, "nom": "Éco-Expert", "emoji": "🥈", "class": "silver"},
    {"min": 60, "nom": "Éco-Apprenti", "emoji": "🥉", "class": "bronze"},
    {"min": 40, "nom": "Éco-Débutant", "emoji": "🌱", "class": "beginner"},
    {"min": 0, "nom": "À améliorer", "emoji": "📈", "class": "beginner"},
]
