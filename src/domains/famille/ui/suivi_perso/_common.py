"""
Module Suivi Perso - Imports et constantes partagés

Dashboard santé/sport pour Anne et Mathieu:
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

from src.core.database import get_db_context
from src.core.models import (
    UserProfile,
    GarminToken,
    GarminActivity,
    GarminDailySummary,
    FoodLog,
    HealthRoutine,
)
from src.services.garmin_sync import (
    GarminService,
    get_garmin_service,
    get_or_create_user,
    get_user_by_username,
)


__all__ = [
    # Standard libs
    "st", "date", "datetime", "timedelta", "go", "px",
    # Database
    "get_db_context",
    # Models
    "UserProfile", "GarminToken", "GarminActivity", 
    "GarminDailySummary", "FoodLog", "HealthRoutine",
    # Services
    "GarminService", "get_garmin_service", 
    "get_or_create_user", "get_user_by_username",
]
