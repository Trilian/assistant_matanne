"""
Module Depenses Maison - Imports et constantes partages

Focus sur les depenses recurrentes de la maison avec consommation.
Utilise le service Budget unifie (src/services/budget.py).
"""

import calendar
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Optional

import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models import HouseExpense
from src.core.models.finances import ExpenseCategory
from src.services.famille.budget import (
    CategorieDepense,
    FactureMaison,
    get_budget_service,
)

# Labels des categories de depenses
CATEGORY_LABELS = {
    "gaz": "🔥 Gaz (chauffage)",
    "electricite": "⚡ Électricite",
    "eau": "💧 Eau",
    "internet": "📶 Internet/Box",
    "loyer": "🏠 Loyer",
    "creche": "👶 Crèche Jules",
    "assurance": "🛡️ Assurance habitation",
    "taxe_fonciere": "🏛️ Taxe foncière",
    "entretien": "🔧 Entretien (chaudière...)",
    "autre": "📦 Autre",
}

# Categories avec suivi consommation (kWh, m³)
CATEGORIES_AVEC_CONSO = {"gaz", "electricite", "eau"}

# Noms des mois en français
MOIS_FR = [
    "",
    "Janvier",
    "Fevrier",
    "Mars",
    "Avril",
    "Mai",
    "Juin",
    "Juillet",
    "Août",
    "Septembre",
    "Octobre",
    "Novembre",
    "Decembre",
]


__all__ = [
    # Standard libs
    "st",
    "date",
    "timedelta",
    "Decimal",
    "Optional",
    "List",
    "calendar",
    # Database
    "obtenir_contexte_db",
    "HouseExpense",
    "ExpenseCategory",
    # Budget service
    "get_budget_service",
    "FactureMaison",
    "CategorieDepense",
    # Constants
    "CATEGORY_LABELS",
    "CATEGORIES_AVEC_CONSO",
    "MOIS_FR",
]
