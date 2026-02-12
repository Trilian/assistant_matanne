"""
Module Suivi Perso - Imports et constantes partages

Dashboard sante/sport pour Anne et Mathieu:
- Switch utilisateur (Anne / Mathieu)
- Dashboard perso (stats Garmin, streak, objectifs)
- Routines sport
- Log alimentation
- Progression (graphiques)
- Sync Garmin
"""

import streamlit as st
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

from src.core.database import obtenir_contexte_db
from src.core.models import (
    UserProfile,
    GarminToken,
    GarminActivity,
    GarminDailySummary,
    FoodLog,
    HealthRoutine,
)
from src.services.garmin import (
    GarminService,
    get_garmin_service,
    get_or_create_user,
    get_user_by_username,
)


__all__ = [
    # Standard libs
    "st", "date", "datetime", "timedelta", "go", "px",
    # Database
    "obtenir_contexte_db",
    # Models
    "UserProfile", "GarminToken", "GarminActivity", 
    "GarminDailySummary", "FoodLog", "HealthRoutine",
    # Services
    "GarminService", "get_garmin_service", 
    "get_or_create_user", "get_user_by_username",
]

