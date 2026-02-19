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

from datetime import date, datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.core.db import obtenir_contexte_db
from src.core.models import (
    FoodLog,
    GarminActivity,
    GarminDailySummary,
    GarminToken,
    HealthRoutine,
    UserProfile,
)
from src.services.integrations.garmin import (
    GarminService,
    get_garmin_service,
    get_or_create_user,
    get_user_by_username,
)

__all__ = [
    # Standard libs
    "st",
    "date",
    "datetime",
    "timedelta",
    "go",
    "px",
    # Database
    "obtenir_contexte_db",
    # Models
    "UserProfile",
    "GarminToken",
    "GarminActivity",
    "GarminDailySummary",
    "FoodLog",
    "HealthRoutine",
    # Services
    "GarminService",
    "get_garmin_service",
    "get_or_create_user",
    "get_user_by_username",
]

# ============================================================
# Fonctions importées depuis utilitaires.py
# ============================================================


def get_current_user() -> str:
    """Recupère l'utilisateur courant"""
    return st.session_state.get("suivi_user", "anne")


def set_current_user(username: str):
    """Definit l'utilisateur courant"""
    st.session_state["suivi_user"] = username


def get_user_data(username: str) -> dict:
    """Recupère les donnees complètes d'un utilisateur"""
    from .utils import GarminActivity

    try:
        with obtenir_contexte_db() as db:
            user = db.query(UserProfile).filter_by(username=username).first()

            if not user:
                # Creer l'utilisateur
                user = get_or_create_user(
                    username, "Anne" if username == "anne" else "Mathieu", db=db
                )

            # Stats des 7 derniers jours
            end_date = date.today()
            start_date = end_date - timedelta(days=7)

            summaries = (
                db.query(GarminDailySummary)
                .filter(
                    GarminDailySummary.user_id == user.id, GarminDailySummary.date >= start_date
                )
                .all()
            )

            activities = (
                db.query(GarminActivity)
                .filter(
                    GarminActivity.user_id == user.id,
                    GarminActivity.date_debut >= datetime.combine(start_date, datetime.min.time()),
                )
                .all()
            )

            # Calculer les stats
            total_pas = sum(s.pas for s in summaries)
            total_calories = sum(s.calories_actives for s in summaries)
            total_minutes = sum(s.minutes_actives for s in summaries)

            # Streak
            streak = _calculate_streak(user, summaries)

            return {
                "user": user,
                "summaries": summaries,
                "activities": activities,
                "total_pas": total_pas,
                "total_calories": total_calories,
                "total_minutes": total_minutes,
                "streak": streak,
                "garmin_connected": user.garmin_connected,
                "objectif_pas": user.objectif_pas_quotidien,
                "objectif_calories": user.objectif_calories_brulees,
            }
    except Exception as e:
        st.error(f"Erreur chargement donnees: {e}")
        return {}


def _calculate_streak(user: UserProfile, summaries: list) -> int:
    """Calcule le streak actuel"""
    if not summaries:
        return 0

    objectif = user.objectif_pas_quotidien or 10000
    summary_by_date = {s.date: s for s in summaries}

    streak = 0
    current_date = date.today()

    for _ in range(60):  # Max 60 jours
        summary = summary_by_date.get(current_date)
        if summary and summary.pas >= objectif:
            streak += 1
            current_date -= timedelta(days=1)
        else:
            break

    return streak


def get_food_logs_today(username: str) -> list:
    """Recupère les logs alimentation du jour"""
    try:
        with obtenir_contexte_db() as db:
            user = db.query(UserProfile).filter_by(username=username).first()
            if not user:
                return []

            return (
                db.query(FoodLog)
                .filter(FoodLog.user_id == user.id, FoodLog.date == date.today())
                .order_by(FoodLog.heure)
                .all()
            )
    except:
        return []
