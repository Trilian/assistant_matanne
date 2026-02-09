"""
Module Achats Famille - Imports et constantes partagés

Catégories:
- 👶 Jules (vêtements, jouets, équipement)
- 👨‍👩‍👧 Nous (jeux, loisirs, équipement)
- 📋 Wishlist & priorités
"""

import streamlit as st
from datetime import date
from typing import Optional

from src.core.database import get_db_context
from src.core.models import FamilyPurchase


# Catégories d'achats
CATEGORIES = {
    "jules_vetements": {"emoji": "👕", "label": "Jules - Vêtements", "groupe": "jules"},
    "jules_jouets": {"emoji": "🧸", "label": "Jules - Jouets", "groupe": "jules"},
    "jules_equipement": {"emoji": "🛠️", "label": "Jules - Équipement", "groupe": "jules"},
    "nous_jeux": {"emoji": "🎲", "label": "Nous - Jeux", "groupe": "nous"},
    "nous_loisirs": {"emoji": "🎨", "label": "Nous - Loisirs", "groupe": "nous"},
    "nous_equipement": {"emoji": "🏠", "label": "Nous - Équipement", "groupe": "nous"},
    "maison": {"emoji": "🏡", "label": "Maison", "groupe": "maison"},
}

# Niveaux de priorité
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
    "get_db_context", "FamilyPurchase",
    # Constants
    "CATEGORIES", "PRIORITES",
]
