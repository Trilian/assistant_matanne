"""
Module Dépenses Maison - Imports et constantes partagés

Focus sur les dépenses récurrentes de la maison avec consommation.
Utilise le service Budget unifié (src/services/budget.py).
"""

import streamlit as st
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional, List
import calendar

from src.core.database import get_db_context
from src.core.models import HouseExpense
from src.core.models.maison_extended import ExpenseCategory
from src.services.budget import (
    get_budget_service,
    FactureMaison,
    CategorieDepense,
)


# Labels des catégories de dépenses
CATEGORY_LABELS = {
    "gaz": "🔥 Gaz (chauffage)",
    "electricite": "⚡ Électricité",
    "eau": "💧 Eau",
    "internet": "📶 Internet/Box",
    "loyer": "🏠 Loyer",
    "creche": "👶 Crèche Jules",
    "assurance": "🛡️ Assurance habitation",
    "taxe_fonciere": "🏛️ Taxe foncière",
    "entretien": "🔧 Entretien (chaudière...)",
    "autre": "📦 Autre"
}

# Catégories avec suivi consommation (kWh, m³)
CATEGORIES_AVEC_CONSO = {"gaz", "electricite", "eau"}

# Noms des mois en français
MOIS_FR = [
    "", "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
    "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
]


__all__ = [
    # Standard libs
    "st", "date", "timedelta", "Decimal", "Optional", "List", "calendar",
    # Database
    "get_db_context", "HouseExpense", "ExpenseCategory",
    # Budget service
    "get_budget_service", "FactureMaison", "CategorieDepense",
    # Constants
    "CATEGORY_LABELS", "CATEGORIES_AVEC_CONSO", "MOIS_FR",
]
