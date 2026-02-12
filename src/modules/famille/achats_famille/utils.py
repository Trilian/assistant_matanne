"""
Module Achats Famille - Imports et constantes partages

Categories:
- 👶 Jules (vêtements, jouets, equipement)
- 👨‍👩‍👧 Nous (jeux, loisirs, equipement)
- 📋 Wishlist & priorites
"""

import streamlit as st
from datetime import date
from typing import Optional

from src.core.database import obtenir_contexte_db
from src.core.models import FamilyPurchase


# Categories d'achats
CATEGORIES = {
    "jules_vetements": {"emoji": "👕", "label": "Jules - Vêtements", "groupe": "jules"},
    "jules_jouets": {"emoji": "🧸", "label": "Jules - Jouets", "groupe": "jules"},
    "jules_equipement": {"emoji": "🛠️", "label": "Jules - Équipement", "groupe": "jules"},
    "nous_jeux": {"emoji": "🎲", "label": "Nous - Jeux", "groupe": "nous"},
    "nous_loisirs": {"emoji": "🎨", "label": "Nous - Loisirs", "groupe": "nous"},
    "nous_equipement": {"emoji": "🏠", "label": "Nous - Équipement", "groupe": "nous"},
    "maison": {"emoji": "🏡", "label": "Maison", "groupe": "maison"},
}

# Niveaux de priorite
PRIORITES = {
    "urgent": {"emoji": "🔴", "label": "Urgent", "order": 1},
    "haute": {"emoji": "🟠", "label": "Haute", "order": 2},
    "moyenne": {"emoji": "🟡", "label": "Moyenne", "order": 3},
    "basse": {"emoji": "🟢", "label": "Basse", "order": 4},
    "optionnel": {"emoji": "⚪", "label": "Optionnel", "order": 5},
}


__all__ = [
    # Standard libs
    "st", "date", "Optional",
    # Database
    "obtenir_contexte_db", "FamilyPurchase",
    # Constants
    "CATEGORIES", "PRIORITES",
]

