"""
Module Achats Famille - Imports et constantes partages

Categories:
- 👶 Jules (vêtements, jouets, equipement)
- 👨‍👩‍👧 Nous (jeux, loisirs, equipement)
- 📋 Wishlist & priorites
"""

import logging
from datetime import date
from typing import Optional

import streamlit as st

from src.core.models import FamilyPurchase
from src.services.famille.achats import obtenir_service_achats_famille

logger = logging.getLogger(__name__)

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
    "date",
    "Optional",
    # Database
    "FamilyPurchase",
    # Constants
    "CATEGORIES",
    "PRIORITES",
]

# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def get_all_purchases(achete: bool = False) -> list:
    """Recupère tous les achats"""
    try:
        return obtenir_service_achats_famille().lister_achats(achete=achete)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return []


def get_purchases_by_category(categorie: str, achete: bool = False) -> list:
    """Recupère les achats par categorie"""
    try:
        return obtenir_service_achats_famille().lister_par_categorie(categorie, achete=achete)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return []


def get_purchases_by_groupe(groupe: str, achete: bool = False) -> list:
    """Recupère les achats par groupe (jules, nous, maison)"""
    categories = [k for k, v in CATEGORIES.items() if v["groupe"] == groupe]
    try:
        return obtenir_service_achats_famille().lister_par_groupe(categories, achete=achete)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return []


def get_stats() -> dict:
    """Calcule les statistiques des achats"""
    try:
        return obtenir_service_achats_famille().get_stats()
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
        return {
            "en_attente": 0,
            "achetes": 0,
            "total_estime": 0,
            "total_depense": 0,
            "urgents": 0,
        }


def mark_as_bought(purchase_id: int, prix_reel: float = None):
    """Marque un achat comme effectue"""
    try:
        obtenir_service_achats_famille().marquer_achete(purchase_id, prix_reel=prix_reel)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")


def delete_purchase(purchase_id: int):
    """Supprime un achat"""
    try:
        obtenir_service_achats_famille().supprimer_achat(purchase_id)
    except Exception as e:
        logger.debug(f"Erreur ignorée: {e}")
