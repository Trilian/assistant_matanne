"""
Module Achats Famille - Imports et constantes partages

Categories:
- 👶 Jules (vêtements, jouets, equipement)
- 👨‍👩‍👧 Nous (jeux, loisirs, equipement)
- 📋 Wishlist & priorites
"""

from datetime import date
from typing import Optional

import streamlit as st

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
    "st",
    "date",
    "Optional",
    # Database
    "obtenir_contexte_db",
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
        with obtenir_contexte_db() as db:
            return db.query(FamilyPurchase).filter_by(achete=achete).all()
    except:
        return []


def get_purchases_by_category(categorie: str, achete: bool = False) -> list:
    """Recupère les achats par categorie"""
    try:
        with obtenir_contexte_db() as db:
            return (
                db.query(FamilyPurchase)
                .filter(FamilyPurchase.categorie == categorie, FamilyPurchase.achete == achete)
                .order_by(FamilyPurchase.priorite)
                .all()
            )
    except:
        return []


def get_purchases_by_groupe(groupe: str, achete: bool = False) -> list:
    """Recupère les achats par groupe (jules, nous, maison)"""
    categories = [k for k, v in CATEGORIES.items() if v["groupe"] == groupe]
    try:
        with obtenir_contexte_db() as db:
            return (
                db.query(FamilyPurchase)
                .filter(FamilyPurchase.categorie.in_(categories), FamilyPurchase.achete == achete)
                .order_by(FamilyPurchase.priorite)
                .all()
            )
    except:
        return []


def get_stats() -> dict:
    """Calcule les statistiques des achats"""
    try:
        with obtenir_contexte_db() as db:
            en_attente = db.query(FamilyPurchase).filter_by(achete=False).all()
            achetes = db.query(FamilyPurchase).filter_by(achete=True).all()

            total_estime = sum(p.prix_estime or 0 for p in en_attente)
            total_depense = sum(p.prix_reel or p.prix_estime or 0 for p in achetes)
            urgents = len([p for p in en_attente if p.priorite in ["urgent", "haute"]])

            return {
                "en_attente": len(en_attente),
                "achetes": len(achetes),
                "total_estime": total_estime,
                "total_depense": total_depense,
                "urgents": urgents,
            }
    except:
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
        with obtenir_contexte_db() as db:
            purchase = db.get(FamilyPurchase, purchase_id)
            if purchase:
                purchase.achete = True
                purchase.date_achat = date.today()
                if prix_reel:
                    purchase.prix_reel = prix_reel
                db.commit()
    except:
        pass


def delete_purchase(purchase_id: int):
    """Supprime un achat"""
    try:
        with obtenir_contexte_db() as db:
            purchase = db.get(FamilyPurchase, purchase_id)
            if purchase:
                db.delete(purchase)
                db.commit()
    except:
        pass
