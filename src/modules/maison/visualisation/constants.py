"""Constantes pour la visualisation maison 2D/3D."""

# Couleurs par état des pièces
COULEURS_ETATS = {
    "ok": {
        "fill": "rgba(76, 175, 80, 0.3)",
        "border": "#4CAF50",
        "label": "✅ OK",
    },
    "attention": {
        "fill": "rgba(255, 152, 0, 0.3)",
        "border": "#FF9800",
        "label": "⚠️ Attention",
    },
    "critique": {
        "fill": "rgba(244, 67, 54, 0.3)",
        "border": "#F44336",
        "label": "🔴 Critique",
    },
    "travaux_recents": {
        "fill": "rgba(33, 150, 243, 0.3)",
        "border": "#2196F3",
        "label": "🔵 Travaux récents",
    },
}

# Emojis par type de pièce
EMOJIS_PIECES = {
    "salon": "🛋️",
    "cuisine": "🍳",
    "chambre_parentale": "🛏️",
    "chambre_jules": "👶",
    "chambre_amis": "🛏️",
    "salle_de_bain": "🚿",
    "wc": "🚽",
    "entree": "🚪",
    "couloir": "🏃",
    "garage": "🔧",
    "buanderie": "🧺",
    "bureau": "💻",
    "terrasse": "🌿",
    "jardin": "🌳",
    "autre": "🏠",
}

# Couleurs par type de pièce (pour la 3D)
COULEURS_TYPE_PIECE = {
    "salon": "#8BC34A",
    "cuisine": "#FF9800",
    "chambre_parentale": "#9C27B0",
    "chambre_jules": "#E91E63",
    "chambre_amis": "#AB47BC",
    "salle_de_bain": "#00BCD4",
    "wc": "#00ACC1",
    "entree": "#795548",
    "couloir": "#9E9E9E",
    "garage": "#607D8B",
    "buanderie": "#78909C",
    "bureau": "#3F51B5",
    "terrasse": "#4CAF50",
    "jardin": "#2E7D32",
    "autre": "#BDBDBD",
}

# Hauteur 3D par type (en mètres pour l'extrusion)
HAUTEUR_3D_PIECE = {
    "salon": 2.5,
    "cuisine": 2.5,
    "chambre_parentale": 2.5,
    "chambre_jules": 2.5,
    "chambre_amis": 2.5,
    "salle_de_bain": 2.5,
    "wc": 2.5,
    "entree": 2.5,
    "couloir": 2.5,
    "garage": 3.0,
    "buanderie": 2.5,
    "bureau": 2.5,
    "terrasse": 1.0,
    "jardin": 0.5,
    "autre": 2.5,
}

ETAGE_LABELS = {
    -1: "Sous-sol",
    0: "RDC",
    1: "1er étage",
    2: "2ème étage",
    3: "3ème étage",
}

# Labels de statut objet
STATUT_OBJET_LABELS = {
    "fonctionne": "✅ Fonctionne",
    "a_reparer": "🔧 À réparer",
    "a_changer": "🔄 À changer",
    "a_acheter": "🛒 À acheter",
    "en_commande": "📦 En commande",
    "hors_service": "❌ Hors service",
    "a_donner": "🎁 À donner",
    "archive": "📁 Archivé",
}
