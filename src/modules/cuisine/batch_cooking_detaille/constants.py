"""Constantes UI pour le module Batch Cooking Détaillé."""

from datetime import time

TYPES_DECOUPE = {
    "rondelles": {"label": "Rondelles", "emoji": "⭕", "description": "Tranches circulaires"},
    "cubes": {"label": "Cubes", "emoji": "🔲", "description": "Morceaux cubiques"},
    "julienne": {"label": "Julienne", "emoji": "📝", "description": "Bâtonnets fins 3-4mm"},
    "brunoise": {"label": "Brunoise", "emoji": "🔹", "description": "Petits dés 3mm"},
    "lamelles": {"label": "Lamelles", "emoji": "➖", "description": "Tranches fines plates"},
    "cisele": {"label": "Ciselé", "emoji": "✂️", "description": "Haché finement"},
    "emince": {"label": "Émincé", "emoji": "🔪", "description": "Tranches fines allongées"},
    "rape": {"label": "Râpé", "emoji": "🧀", "description": "Râpé grossier ou fin"},
}

TYPES_SESSION = {
    "dimanche": {
        "label": "🌞 Session Dimanche",
        "duree_type": "2-3h",
        "avec_jules": True,
        "heure_defaut": time(10, 0),
        "description": "Grande session familiale avec Jules",
    },
    "mercredi": {
        "label": "🌙 Session Mercredi",
        "duree_type": "1-1.5h",
        "avec_jules": False,
        "heure_defaut": time(20, 0),
        "description": "Session rapide en solo",
    },
}
