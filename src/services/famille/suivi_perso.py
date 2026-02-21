"""
Service Suivi Perso - Logique métier pour le suivi santé personnel.

Opérations:
- Récupération des données utilisateur (stats, activités, streak)
- Gestion des logs alimentation
"""

import logging
from datetime import date as date_type
from datetime import datetime, timedelta
from typing import Any, TypedDict

from sqlalchemy.orm import Session

from src.core.constants import OBJECTIF_PAS_QUOTIDIEN_DEFAUT
from src.core.decorators import avec_session_db
from src.core.models import FoodLog, GarminActivity, GarminDailySummary, UserProfile
from src.services.core.events.bus import obtenir_bus

logger = logging.getLogger(__name__)


class UserDataDict(TypedDict, total=False):
    """Structure de données pour les infos utilisateur.

    total=False car la structure peut être vide en cas d'erreur.
    """

    user: Any  # UserProfile
    summaries: list[Any]  # list[GarminDailySummary]
    activities: list[Any]  # list[GarminActivity]
    total_pas: int
    total_calories: int
    total_minutes: int
    streak: int
    garmin_connected: bool
    objectif_pas: int
    objectif_calories: int


class ServiceSuiviPerso:
    """Service de suivi santé personnel (alimentation, stats).

    Encapsule toutes les opérations liées au suivi personnel:
    - Données utilisateur agrégées (stats Garmin, streak)
    - Logs alimentation (CRUD)
    """

    # ═══════════════════════════════════════════════════════════
    # USER DATA
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def get_user_data(self, username: str, db: Session | None = None) -> UserDataDict:
        """Récupère les données complètes d'un utilisateur (7 derniers jours).

        Args:
            username: Nom d'utilisateur (ex: "anne", "mathieu").
            db: Session DB (injectée automatiquement).

        Returns:
            UserDataDict contenant:
            - user: UserProfile
            - summaries: Liste GarminDailySummary (7 jours)
            - activities: Liste GarminActivity (7 jours)
            - total_pas: Total des pas
            - total_calories: Total calories actives
            - total_minutes: Total minutes actives
            - streak: Jours consécutifs avec objectif atteint
            - garmin_connected: Connexion Garmin active
            - objectif_pas: Objectif quotidien de pas
            - objectif_calories: Objectif calories brûlées
        """
        assert db is not None

        from src.services.integrations.garmin import get_or_create_user

        try:
            user = db.query(UserProfile).filter_by(username=username).first()

            if not user:
                # Créer l'utilisateur si inexistant
                display_name = "Anne" if username == "anne" else "Mathieu"
                user = get_or_create_user(username, display_name, db=db)

            # Stats des 7 derniers jours
            end_date = date_type.today()
            start_date = end_date - timedelta(days=7)

            summaries = (
                db.query(GarminDailySummary)
                .filter(
                    GarminDailySummary.user_id == user.id,
                    GarminDailySummary.date >= start_date,
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
            streak = self._calculate_streak(user, summaries)

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
            logger.error(f"Erreur chargement données utilisateur {username}: {e}")
            return {}

    def _calculate_streak(self, user: UserProfile, summaries: list) -> int:
        """Calcule le streak actuel (jours consécutifs objectif atteint).

        Args:
            user: Profil utilisateur avec objectif de pas.
            summaries: Liste des résumés quotidiens.

        Returns:
            Nombre de jours consécutifs où l'objectif a été atteint.
        """
        if not summaries:
            return 0

        objectif = user.objectif_pas_quotidien or OBJECTIF_PAS_QUOTIDIEN_DEFAUT
        summary_by_date = {s.date: s for s in summaries}

        streak = 0
        current_date = date_type.today()

        for _ in range(60):  # Max 60 jours de recherche
            summary = summary_by_date.get(current_date)
            if summary and summary.pas >= objectif:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break

        return streak

    # ═══════════════════════════════════════════════════════════
    # FOOD LOGS
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def get_food_logs_today(self, username: str, db: Session | None = None) -> list[FoodLog]:
        """Récupère les logs alimentation du jour.

        Args:
            username: Nom d'utilisateur.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des FoodLog du jour, triée par heure.
        """
        assert db is not None

        try:
            user = db.query(UserProfile).filter_by(username=username).first()
            if not user:
                return []

            return (
                db.query(FoodLog)
                .filter(FoodLog.user_id == user.id, FoodLog.date == date_type.today())
                .order_by(FoodLog.heure)
                .all()
            )
        except Exception as e:
            logger.debug(f"Erreur récupération food logs: {e}")
            return []

    @avec_session_db
    def ajouter_food_log(
        self,
        username: str,
        repas: str,
        description: str,
        calories: int | None = None,
        qualite: int = 3,
        notes: str | None = None,
        db: Session | None = None,
    ) -> FoodLog:
        """Ajoute un log alimentation.

        Args:
            username: Nom d'utilisateur.
            repas: Type de repas ("petit_dejeuner", "dejeuner", "diner", "snack").
            description: Description du repas.
            calories: Calories estimées (optionnel).
            qualite: Note de qualité 1-5 (défaut: 3).
            notes: Notes additionnelles (optionnel).
            db: Session DB (injectée automatiquement).

        Returns:
            FoodLog créé.

        Raises:
            ValueError: Si l'utilisateur n'existe pas et ne peut être créé.
        """
        assert db is not None

        from src.services.integrations.garmin import get_or_create_user

        user = db.query(UserProfile).filter_by(username=username).first()
        if not user:
            display_name = "Anne" if username == "anne" else "Mathieu"
            user = get_or_create_user(username, display_name, db=db)

        log = FoodLog(
            user_id=user.id,
            date=date_type.today(),
            heure=datetime.now(),
            repas=repas,
            description=description,
            calories_estimees=calories if calories and calories > 0 else None,
            qualite=qualite,
            notes=notes or None,
        )
        db.add(log)
        db.commit()
        db.refresh(log)

        logger.info(f"FoodLog ajouté pour {username}: {repas}")

        # Emit event after successful commit
        obtenir_bus().emettre(
            "food_log.ajoute",
            {"id": log.id, "username": username, "repas": repas, "qualite": qualite},
            source="ServiceSuiviPerso",
        )

        return log


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════

_instance: ServiceSuiviPerso | None = None


def obtenir_service_suivi_perso() -> ServiceSuiviPerso:
    """Factory pour le service suivi perso (singleton)."""
    global _instance
    if _instance is None:
        _instance = ServiceSuiviPerso()
    return _instance


# Alias anglais
get_suivi_perso_service = obtenir_service_suivi_perso
