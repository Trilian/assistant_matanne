"""
Module Jules - Imports et constantes partagés

Activités adaptées, achats suggérés, conseils développement:
- 📊 Dashboard: âge, prochains achats suggérés
- 🎨 Activités du jour (adaptées 19 mois)
- 🛒 Shopping Jules (vêtements taille actuelle, jouets recommandés)
- 💡 Conseils (propreté, sommeil, alimentation) - IA
"""

import streamlit as st
from datetime import date, timedelta
from typing import Optional

from src.core.database import get_db_context
from src.core.models import ChildProfile, Milestone, FamilyPurchase
from src.services.base_ai_service import BaseAIService
from src.core.ai import ClientIA


# Activités par tranche d'âge (mois)
ACTIVITES_PAR_AGE = {
    (18, 24): [
        {"nom": "Pâte à modeler", "emoji": "🎨", "duree": "20min", "interieur": True, "description": "Développe la motricité fine"},
        {"nom": "Lecture interactive", "emoji": "📚", "duree": "15min", "interieur": True, "description": "Pointer les images, nommer les objets"},
        {"nom": "Jeux d'eau", "emoji": "💧", "duree": "30min", "interieur": False, "description": "Transvaser, verser, éclabousser"},
        {"nom": "Cache-cache simplifié", "emoji": "🙈", "duree": "15min", "interieur": True, "description": "Se cacher derrière un rideau"},
        {"nom": "Danse et musique", "emoji": "🎵", "duree": "15min", "interieur": True, "description": "Bouger sur des comptines"},
        {"nom": "Dessin au doigt", "emoji": "✋", "duree": "20min", "interieur": True, "description": "Peinture au doigt sur grande feuille"},
        {"nom": "Tour de cubes", "emoji": "🧱", "duree": "15min", "interieur": True, "description": "Empiler et faire tomber"},
        {"nom": "Bulles de savon", "emoji": "🫧", "duree": "15min", "interieur": False, "description": "Attraper les bulles"},
        {"nom": "Promenade nature", "emoji": "🌳", "duree": "30min", "interieur": False, "description": "Observer, ramasser des feuilles"},
        {"nom": "Jeu de ballon", "emoji": "⚽", "duree": "15min", "interieur": False, "description": "Rouler, lancer doucement"},
    ],
    (24, 36): [
        {"nom": "Puzzle simple", "emoji": "🧩", "duree": "20min", "interieur": True, "description": "3-6 pièces"},
        {"nom": "Jeu de rôle", "emoji": "🎭", "duree": "20min", "interieur": True, "description": "Dînette, poupées, voitures"},
        {"nom": "Parcours moteur", "emoji": "🏃", "duree": "20min", "interieur": True, "description": "Coussins, tunnels, cerceaux"},
    ],
}

# Tailles vêtements par âge
TAILLES_PAR_AGE = {
    (12, 18): {"vetements": "80-86", "chaussures": "20-21"},
    (18, 24): {"vetements": "86-92", "chaussures": "22-23"},
    (24, 36): {"vetements": "92-98", "chaussures": "24-25"},
}

# Catégories de conseils
CATEGORIES_CONSEILS = {
    "proprete": {"emoji": "🚽", "titre": "Propreté", "description": "Apprentissage du pot"},
    "sommeil": {"emoji": "😴", "titre": "Sommeil", "description": "Routines et astuces"},
    "alimentation": {"emoji": "🍽️", "titre": "Alimentation", "description": "Diversification, autonomie"},
    "langage": {"emoji": "💬", "titre": "Langage", "description": "Stimuler la parole"},
    "motricite": {"emoji": "🏃", "titre": "Motricité", "description": "Développement physique"},
    "social": {"emoji": "👥", "titre": "Social", "description": "Interactions, émotions"},
}


__all__ = [
    # Standard libs
    "st", "date", "timedelta", "Optional",
    # Database
    "get_db_context", "ChildProfile", "Milestone", "FamilyPurchase",
    # AI
    "BaseAIService", "ClientIA",
    # Constants
    "ACTIVITES_PAR_AGE", "TAILLES_PAR_AGE", "CATEGORIES_CONSEILS",
]
