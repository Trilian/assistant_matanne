"""
Constantes et données statiques pour le module Éco-Tips.
"""

TYPE_LABELS = {
    "lavable": "🧽 Lavable/Réutilisable",
    "energie": "⚡ Énergie",
    "eau": "💧 Eau",
    "dechets": "♻️ Déchets",
    "alimentation": "🍽️ Alimentation",
}

IDEES_ACTIONS = [
    {
        "nom": "Éponges lavables",
        "type": "lavable",
        "economie_estimee": 5.0,
        "cout_nouveau_initial": 15.0,
        "description": "Remplacer les éponges jetables par des éponges lavables en tissu.",
    },
    {
        "nom": "Serviettes en tissu",
        "type": "lavable",
        "economie_estimee": 8.0,
        "cout_nouveau_initial": 25.0,
        "description": "Utiliser des serviettes en tissu au lieu de l'essuie-tout.",
    },
    {
        "nom": "LED partout",
        "type": "energie",
        "economie_estimee": 15.0,
        "cout_nouveau_initial": 40.0,
        "description": "Remplacer toutes les ampoules par des LED basse consommation.",
    },
    {
        "nom": "Mousseurs robinets",
        "type": "eau",
        "economie_estimee": 10.0,
        "cout_nouveau_initial": 12.0,
        "description": "Installer des mousseurs sur tous les robinets (40% économie eau).",
    },
    {
        "nom": "Composteur",
        "type": "dechets",
        "economie_estimee": 5.0,
        "cout_nouveau_initial": 50.0,
        "description": "Composter les déchets organiques pour réduire les poubelles.",
    },
    {
        "nom": "Batch cooking",
        "type": "alimentation",
        "economie_estimee": 40.0,
        "cout_nouveau_initial": 0.0,
        "description": "Cuisiner en lots pour la semaine, réduire le gaspillage et les repas à emporter.",
    },
    {
        "nom": "Thermostat programmable",
        "type": "energie",
        "economie_estimee": 25.0,
        "cout_nouveau_initial": 80.0,
        "description": "Programmer le chauffage: 17°C la nuit, 19°C le jour.",
    },
    {
        "nom": "Récupérateur eau pluie",
        "type": "eau",
        "economie_estimee": 12.0,
        "cout_nouveau_initial": 60.0,
        "description": "Récupérer l'eau de pluie pour l'arrosage du jardin.",
    },
]

ECO_TIPS_DATA = {
    "🔌 Énergie": [
        {
            "tip": "Baisser le chauffage de 1°C = 7% d'économies",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Éteindre les appareils en veille = 10% d'économies",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Utiliser des multiprises à interrupteur",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Privilégier les LED (80% moins gourmandes)",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Programmer le chauffage (17°C la nuit, 19°C le jour)",
            "impact": "haute",
            "difficulte": "moyen",
        },
        {"tip": "Installer un thermostat connecté", "impact": "haute", "difficulte": "moyen"},
    ],
    "💧 Eau": [
        {
            "tip": "Douche de 5 min max = 60L vs 150L pour un bain",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Installer des mousseurs (40% d'économie d'eau)",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Récupérer l'eau de pluie pour le jardin",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {
            "tip": "Lancer le lave-vaisselle uniquement plein",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Réparer les fuites (10L/jour pour un robinet)",
            "impact": "haute",
            "difficulte": "moyen",
        },
    ],
    "🍽️ Cuisine": [
        {
            "tip": "Couvrir les casseroles (4x plus rapide)",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Décongeler au frigo plutôt qu'au micro-ondes",
            "impact": "basse",
            "difficulte": "facile",
        },
        {
            "tip": "Utiliser une bouilloire vs casserole pour l'eau",
            "impact": "moyenne",
            "difficulte": "facile",
        },
        {
            "tip": "Batch cooking = moins de cuissons par semaine",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {"tip": "Composter les déchets organiques", "impact": "haute", "difficulte": "moyen"},
    ],
    "♻️ Déchets": [
        {"tip": "Privilégier les produits en vrac", "impact": "haute", "difficulte": "moyen"},
        {"tip": "Utiliser des sacs réutilisables", "impact": "moyenne", "difficulte": "facile"},
        {
            "tip": "Faire ses produits ménagers (vinaigre + bicarbonate)",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {
            "tip": "Donner/vendre plutôt que jeter (Leboncoin, Vinted)",
            "impact": "haute",
            "difficulte": "facile",
        },
        {
            "tip": "Trier rigoureusement (verre, plastique, papier, bio)",
            "impact": "haute",
            "difficulte": "facile",
        },
    ],
    "🌿 Jardin": [
        {"tip": "Arroser tôt le matin ou tard le soir", "impact": "haute", "difficulte": "facile"},
        {"tip": "Pailler pour conserver l'humidité", "impact": "haute", "difficulte": "facile"},
        {
            "tip": "Planter des espèces locales résistantes",
            "impact": "moyenne",
            "difficulte": "moyen",
        },
        {
            "tip": "Installer un récupérateur d'eau de pluie",
            "impact": "haute",
            "difficulte": "moyen",
        },
    ],
}

IMPACT_COLORS = {
    "haute": "#2e7d32",
    "moyenne": "#e65100",
    "basse": "#616161",
}
