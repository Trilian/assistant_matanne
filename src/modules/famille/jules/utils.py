"""
Module Jules - Imports et constantes partages

Activites adaptees, achats suggeres, conseils developpement:
- 📊 Dashboard: âge, prochains achats suggeres
- 🎨 Activites du jour (adaptees 19 mois)
- 🛒 Shopping Jules (vêtements taille actuelle, jouets recommandes)
- 💡 Conseils (proprete, sommeil, alimentation) - IA
"""

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING, Optional

import streamlit as st

from src.core.models import AchatFamille, Jalon, ProfilEnfant
from src.services.famille.achats import obtenir_service_achats_famille

if TYPE_CHECKING:
    from src.core.ai import ClientIA
    from src.services.core.base import BaseAIService

logger = logging.getLogger(__name__)

# Activites par tranche d'âge (mois)
ACTIVITES_PAR_AGE = {
    (18, 24): [
        {
            "nom": "Pâte à modeler",
            "emoji": "🎨",
            "duree": "20min",
            "interieur": True,
            "description": "Developpe la motricite fine",
        },
        {
            "nom": "Lecture interactive",
            "emoji": "📚",
            "duree": "15min",
            "interieur": True,
            "description": "Pointer les images, nommer les objets",
        },
        {
            "nom": "Jeux d'eau",
            "emoji": "💧",
            "duree": "30min",
            "interieur": False,
            "description": "Transvaser, verser, eclabousser",
        },
        {
            "nom": "Cache-cache simplifie",
            "emoji": "🙈",
            "duree": "15min",
            "interieur": True,
            "description": "Se cacher derrière un rideau",
        },
        {
            "nom": "Danse et musique",
            "emoji": "🎵",
            "duree": "15min",
            "interieur": True,
            "description": "Bouger sur des comptines",
        },
        {
            "nom": "Dessin au doigt",
            "emoji": "✋",
            "duree": "20min",
            "interieur": True,
            "description": "Peinture au doigt sur grande feuille",
        },
        {
            "nom": "Tour de cubes",
            "emoji": "🧱",
            "duree": "15min",
            "interieur": True,
            "description": "Empiler et faire tomber",
        },
        {
            "nom": "Bulles de savon",
            "emoji": "🫧",
            "duree": "15min",
            "interieur": False,
            "description": "Attraper les bulles",
        },
        {
            "nom": "Promenade nature",
            "emoji": "🌳",
            "duree": "30min",
            "interieur": False,
            "description": "Observer, ramasser des feuilles",
        },
        {
            "nom": "Jeu de ballon",
            "emoji": "⚽",
            "duree": "15min",
            "interieur": False,
            "description": "Rouler, lancer doucement",
        },
    ],
    (24, 36): [
        {
            "nom": "Puzzle simple",
            "emoji": "🧩",
            "duree": "20min",
            "interieur": True,
            "description": "3-6 pièces",
        },
        {
            "nom": "Jeu de rôle",
            "emoji": "🎭",
            "duree": "20min",
            "interieur": True,
            "description": "Dînette, poupees, voitures",
        },
        {
            "nom": "Parcours moteur",
            "emoji": "🏃",
            "duree": "20min",
            "interieur": True,
            "description": "Coussins, tunnels, cerceaux",
        },
    ],
}

# Tailles vêtements par âge
TAILLES_PAR_AGE = {
    (12, 18): {"vetements": "80-86", "chaussures": "20-21"},
    (18, 24): {"vetements": "86-92", "chaussures": "22-23"},
    (24, 36): {"vetements": "92-98", "chaussures": "24-25"},
}

# Categories de conseils
CATEGORIES_CONSEILS = {
    "proprete": {"emoji": "🚽", "titre": "Proprete", "description": "Apprentissage du pot"},
    "sommeil": {"emoji": "😴", "titre": "Sommeil", "description": "Routines et astuces"},
    "alimentation": {
        "emoji": "🍽️",
        "titre": "Alimentation",
        "description": "Diversification, autonomie",
    },
    "langage": {"emoji": "💬", "titre": "Langage", "description": "Stimuler la parole"},
    "motricite": {"emoji": "🏃", "titre": "Motricite", "description": "Developpement physique"},
    "social": {"emoji": "👥", "titre": "Social", "description": "Interactions, emotions"},
}


__all__ = [
    # Standard libs
    "date",
    "timedelta",
    "Optional",
    # Database
    "ProfilEnfant",
    "Jalon",
    "AchatFamille",
    # AI
    "BaseAIService",
    "ClientIA",
    # Constants
    "ACTIVITES_PAR_AGE",
    "TAILLES_PAR_AGE",
    "CATEGORIES_CONSEILS",
]

# ============================================================
# Fonctions importées depuis age_utils (source de vérité unique)
# ============================================================

from src.modules.famille.age_utils import get_age_jules  # noqa: E402, F401


def get_activites_pour_age(age_mois: int) -> list[dict]:
    """Retourne les activites adaptees à l'âge"""
    for (min_age, max_age), activites in ACTIVITES_PAR_AGE.items():
        if min_age <= age_mois < max_age:
            return activites
    # Par defaut: 18-24 mois
    return ACTIVITES_PAR_AGE.get((18, 24), [])


def get_taille_vetements(age_mois: int) -> dict:
    """Retourne la taille de vêtements pour l'âge"""
    for (min_age, max_age), tailles in TAILLES_PAR_AGE.items():
        if min_age <= age_mois < max_age:
            return tailles
    return {"vetements": "86-92", "chaussures": "22-23"}


def get_achats_jules_en_attente() -> list:
    """Recupère les achats Jules en attente"""
    try:
        categories = ["jules_vetements", "jules_jouets", "jules_equipement"]
        return obtenir_service_achats_famille().lister_par_groupe(categories, achete=False)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return []
