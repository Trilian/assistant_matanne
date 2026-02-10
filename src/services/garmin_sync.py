"""
Service Garmin - Synchronisation avec Garmin Connect API.

Fonctionnalités:
- OAuth 1.0a pour authentification
- Sync activités sportives
- Sync résumés quotidiens (pas, calories, sommeil)
- Sync fréquence cardiaque

Documentation Garmin API:
https://developer.garmin.com/gc-developer-program/overview/

Note: Nécessite une inscription au Garmin Developer Program
et la création d'une application Consumer pour obtenir les clés OAuth.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional
from dataclasses import dataclass

import httpx
from requests_oauthlib import OAuth1Session
from sqlalchemy.orm import Session

from src.core.database import obtenir_contexte_db
from src.core.decorators import avec_session_db
from src.core.models import (
    UserProfile,
    GarminToken,
    GarminActivity,
    GarminDailySummary,
)
from src.core.config import obtenir_parametres

# Import des fonctions utilitaires pures
from src.services.garmin_sync_utils import (
    parse_garmin_timestamp,
    parse_garmin_date,
    parse_activity_data,
    parse_daily_summary,
    translate_activity_type,
    get_activity_icon,
    format_duration,
    format_distance,
    format_pace,
    format_speed,
    calculate_daily_stats,
    calculate_activity_stats,
    calculate_streak,
    get_streak_badge,
    calculate_goal_progress,
    estimate_calories_burned,
    calculate_weekly_summary,
    validate_oauth_config,
    validate_garmin_token,
    is_sync_needed,
    get_sync_date_range,
    date_to_garmin_timestamp,
    build_api_params,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

@dataclass
class GarminConfig:
    """Configuration Garmin API"""
    consumer_key: str
    consumer_secret: str
    request_token_url: str = "https://connectapi.garmin.com/oauth-service/oauth/request_token"
    authorize_url: str = "https://connect.garmin.com/oauthConfirm"
    access_token_url: str = "https://connectapi.garmin.com/oauth-service/oauth/access_token"
    api_base_url: str = "https://apis.garmin.com"


def get_garmin_config() -> GarminConfig:
    """Récupère la configuration Garmin depuis les variables d'environnement"""
    settings = obtenir_parametres()
    
    return GarminConfig(
        consumer_key=getattr(settings, "GARMIN_CONSUMER_KEY", ""),
        consumer_secret=getattr(settings, "GARMIN_CONSUMER_SECRET", ""),
    )


# ═══════════════════════════════════════════════════════════
# SERVICE GARMIN
# ═══════════════════════════════════════════════════════════


class GarminService:
    """Service de synchronisation avec Garmin Connect.
    
    Workflow OAuth 1.0a:
    1. get_authorization_url() -> URL à ouvrir dans le navigateur
    2. L'utilisateur autorise l'accès
    3. complete_authorization(oauth_verifier) -> Stocke les tokens
    4. sync_data() -> Synchronise les données
    """
    
    def __init__(self, config: GarminConfig | None = None):
        self.config = config or get_garmin_config()
        self._oauth_session: OAuth1Session | None = None
        self._temp_request_token: dict | None = None
    
    # ───────────────────────────────────────────────────────
    # OAUTH 1.0a FLOW
    # ───────────────────────────────────────────────────────
    
    def get_authorization_url(self, callback_url: str = "oob") -> tuple[str, dict]:
        """
        Étape 1: Obtenir l'URL d'autorisation.
        
        Args:
            callback_url: URL de callback après autorisation ("oob" pour out-of-band)
        
        Returns:
            Tuple (authorization_url, request_token_dict)
        """
        if not self.config.consumer_key or not self.config.consumer_secret:
            raise ValueError("Clés Garmin non configurées. Ajoutez GARMIN_CONSUMER_KEY et GARMIN_CONSUMER_SECRET.")
        
        oauth = OAuth1Session(
            self.config.consumer_key,
            client_secret=self.config.consumer_secret,
            callback_uri=callback_url
        )
        
        try:
            # Obtenir le request token
            fetch_response = oauth.fetch_request_token(self.config.request_token_url)
            
            self._temp_request_token = {
                "oauth_token": fetch_response.get("oauth_token"),
                "oauth_token_secret": fetch_response.get("oauth_token_secret"),
            }
            
            # Construire l'URL d'autorisation
            authorization_url = oauth.authorization_url(self.config.authorize_url)
            
            logger.info(f"URL d'autorisation Garmin générée: {authorization_url}")
            return authorization_url, self._temp_request_token
            
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention du request token: {e}")
            raise
    
    @avec_session_db
    def complete_authorization(
        self, 
        user_id: int, 
        oauth_verifier: str,
        request_token: dict | None = None,
        db: Session = None
    ) -> bool:
        """
        Étape 2: Finaliser l'autorisation avec le verifier.
        
        Args:
            user_id: ID de l'utilisateur (UserProfile)
            oauth_verifier: Code verifier fourni par Garmin après autorisation
            request_token: Token de requête (si non stocké en mémoire)
            db: Session DB (injectée)
        
        Returns:
            True si succès
        """
        token = request_token or self._temp_request_token
        if not token:
            raise ValueError("Request token manquant. Appelez get_authorization_url() d'abord.")
        
        oauth = OAuth1Session(
            self.config.consumer_key,
            client_secret=self.config.consumer_secret,
            resource_owner_key=token["oauth_token"],
            resource_owner_secret=token["oauth_token_secret"],
            verifier=oauth_verifier
        )
        
        try:
            # Obtenir l'access token
            oauth_tokens = oauth.fetch_access_token(self.config.access_token_url)
            
            access_token = oauth_tokens.get("oauth_token")
            access_token_secret = oauth_tokens.get("oauth_token_secret")
            
            # Stocker les tokens en DB
            user = db.get(UserProfile, user_id)
            if not user:
                raise ValueError(f"Utilisateur {user_id} non trouvé")
            
            # Créer ou mettre à jour le token
            garmin_token = user.garmin_token
            if not garmin_token:
                garmin_token = GarminToken(user_id=user_id)
                db.add(garmin_token)
            
            garmin_token.oauth_token = access_token
            garmin_token.oauth_token_secret = access_token_secret
            garmin_token.sync_active = True
            garmin_token.derniere_sync = None
            
            # Marquer l'utilisateur comme connecté
            user.garmin_connected = True
            
            db.commit()
            
            logger.info(f"Garmin connecté pour l'utilisateur {user_id}")
            self._temp_request_token = None
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la finalisation OAuth: {e}")
            raise
    
    def _get_authenticated_session(self, garmin_token: GarminToken) -> OAuth1Session:
        """Crée une session OAuth authentifiée"""
        return OAuth1Session(
            self.config.consumer_key,
            client_secret=self.config.consumer_secret,
            resource_owner_key=garmin_token.oauth_token,
            resource_owner_secret=garmin_token.oauth_token_secret
        )
    
    # ───────────────────────────────────────────────────────
    # SYNCHRONISATION
    # ───────────────────────────────────────────────────────
    
    @avec_session_db
    def sync_user_data(
        self, 
        user_id: int, 
        days_back: int = 7,
        db: Session = None
    ) -> dict:
        """
        Synchronise toutes les données Garmin pour un utilisateur.
        
        Args:
            user_id: ID de l'utilisateur
            days_back: Nombre de jours à synchroniser en arrière
            db: Session DB (injectée)
        
        Returns:
            Dict avec les stats de sync {activities_synced, summaries_synced}
        """
        user = db.get(UserProfile, user_id)
        if not user or not user.garmin_token:
            raise ValueError(f"Utilisateur {user_id} non trouvé ou Garmin non connecté")
        
        if not user.garmin_token.sync_active:
            logger.warning(f"Sync Garmin désactivée pour l'utilisateur {user_id}")
            return {"activities_synced": 0, "summaries_synced": 0}
        
        oauth_session = self._get_authenticated_session(user.garmin_token)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days_back)
        
        results = {
            "activities_synced": 0,
            "summaries_synced": 0,
            "errors": []
        }
        
        # Sync activités
        try:
            activities = self._fetch_activities(oauth_session, start_date, end_date)
            for activity_data in activities:
                self._save_activity(db, user_id, activity_data)
                results["activities_synced"] += 1
        except Exception as e:
            logger.error(f"Erreur sync activités: {e}")
            results["errors"].append(f"Activities: {str(e)}")
        
        # Sync résumés quotidiens
        try:
            summaries = self._fetch_daily_summaries(oauth_session, start_date, end_date)
            for summary_data in summaries:
                self._save_daily_summary(db, user_id, summary_data)
                results["summaries_synced"] += 1
        except Exception as e:
            logger.error(f"Erreur sync summaries: {e}")
            results["errors"].append(f"Summaries: {str(e)}")
        
        # Mettre à jour la date de dernière sync
        user.garmin_token.derniere_sync = datetime.utcnow()
        db.commit()
        
        logger.info(f"Sync Garmin terminée pour {user_id}: {results}")
        return results
    
    def _fetch_activities(
        self, 
        session: OAuth1Session, 
        start_date: date, 
        end_date: date
    ) -> list[dict]:
        """Récupère les activités depuis l'API Garmin"""
        url = f"{self.config.api_base_url}/wellness-api/rest/activities"
        
        params = {
            "uploadStartTimeInSeconds": int(datetime.combine(start_date, datetime.min.time()).timestamp()),
            "uploadEndTimeInSeconds": int(datetime.combine(end_date, datetime.max.time()).timestamp()),
        }
        
        try:
            response = session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur API Garmin activities: {e}")
            return []
    
    def _fetch_daily_summaries(
        self, 
        session: OAuth1Session, 
        start_date: date, 
        end_date: date
    ) -> list[dict]:
        """Récupère les résumés quotidiens depuis l'API Garmin"""
        url = f"{self.config.api_base_url}/wellness-api/rest/dailies"
        
        params = {
            "uploadStartTimeInSeconds": int(datetime.combine(start_date, datetime.min.time()).timestamp()),
            "uploadEndTimeInSeconds": int(datetime.combine(end_date, datetime.max.time()).timestamp()),
        }
        
        try:
            response = session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erreur API Garmin dailies: {e}")
            return []
    
    def _save_activity(self, db: Session, user_id: int, data: dict) -> GarminActivity:
        """Sauvegarde une activité en DB"""
        garmin_id = str(data.get("activityId") or data.get("summaryId"))
        
        # Vérifier si existe déjà
        existing = db.query(GarminActivity).filter_by(garmin_activity_id=garmin_id).first()
        if existing:
            return existing
        
        # Convertir le type d'activité
        activity_type = data.get("activityType", "other").lower()
        
        # Convertir le timestamp
        start_time = data.get("startTimeInSeconds", 0)
        if start_time:
            date_debut = datetime.fromtimestamp(start_time)
        else:
            date_debut = datetime.utcnow()
        
        activity = GarminActivity(
            user_id=user_id,
            garmin_activity_id=garmin_id,
            type_activite=activity_type,
            nom=data.get("activityName", f"Activité {activity_type}"),
            description=data.get("description"),
            date_debut=date_debut,
            duree_secondes=data.get("durationInSeconds", 0) or 1,
            distance_metres=data.get("distanceInMeters"),
            calories=data.get("activeKilocalories") or data.get("calories"),
            fc_moyenne=data.get("averageHeartRateInBeatsPerMinute"),
            fc_max=data.get("maxHeartRateInBeatsPerMinute"),
            vitesse_moyenne=data.get("averageSpeedInMetersPerSecond"),
            elevation_gain=data.get("totalElevationGainInMeters"),
            raw_data=data,
        )
        
        db.add(activity)
        return activity
    
    def _save_daily_summary(self, db: Session, user_id: int, data: dict) -> GarminDailySummary:
        """Sauvegarde un résumé quotidien en DB"""
        # Extraire la date
        calendar_date = data.get("calendarDate")
        if calendar_date:
            summary_date = datetime.strptime(calendar_date, "%Y-%m-%d").date()
        else:
            start_time = data.get("startTimeInSeconds", 0)
            summary_date = datetime.fromtimestamp(start_time).date() if start_time else date.today()
        
        # Vérifier si existe déjà
        existing = db.query(GarminDailySummary).filter_by(
            user_id=user_id, 
            date=summary_date
        ).first()
        
        if existing:
            # Mettre à jour
            summary = existing
        else:
            summary = GarminDailySummary(user_id=user_id, date=summary_date)
            db.add(summary)
        
        # Remplir les données
        summary.pas = data.get("steps", 0)
        summary.distance_metres = data.get("distanceInMeters", 0)
        summary.calories_totales = data.get("totalKilocalories", 0)
        summary.calories_actives = data.get("activeKilocalories", 0)
        summary.minutes_actives = data.get("moderateIntensityMinutes", 0)
        summary.minutes_tres_actives = data.get("vigorousIntensityMinutes", 0)
        summary.fc_repos = data.get("restingHeartRateInBeatsPerMinute")
        summary.fc_min = data.get("minHeartRateInBeatsPerMinute")
        summary.fc_max = data.get("maxHeartRateInBeatsPerMinute")
        summary.stress_moyen = data.get("averageStressLevel")
        summary.body_battery_max = data.get("bodyBatteryChargedValue")
        summary.body_battery_min = data.get("bodyBatteryDrainedValue")
        summary.raw_data = data
        
        return summary
    
    # ───────────────────────────────────────────────────────
    # HELPERS
    # ───────────────────────────────────────────────────────
    
    @avec_session_db
    def disconnect_user(self, user_id: int, db: Session = None) -> bool:
        """Déconnecte Garmin pour un utilisateur"""
        user = db.get(UserProfile, user_id)
        if not user:
            return False
        
        if user.garmin_token:
            db.delete(user.garmin_token)
        
        user.garmin_connected = False
        db.commit()
        
        logger.info(f"Garmin déconnecté pour l'utilisateur {user_id}")
        return True
    
    @avec_session_db
    def get_user_stats(self, user_id: int, days: int = 7, db: Session = None) -> dict:
        """
        Récupère les statistiques agrégées d'un utilisateur.
        
        Returns:
            Dict avec stats: total_pas, total_calories, total_activities, streak, etc.
        """
        user = db.get(UserProfile, user_id)
        if not user:
            return {}
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Résumés quotidiens
        summaries = db.query(GarminDailySummary).filter(
            GarminDailySummary.user_id == user_id,
            GarminDailySummary.date >= start_date,
            GarminDailySummary.date <= end_date
        ).all()
        
        # Activités
        activities = db.query(GarminActivity).filter(
            GarminActivity.user_id == user_id,
            GarminActivity.date_debut >= datetime.combine(start_date, datetime.min.time()),
            GarminActivity.date_debut <= datetime.combine(end_date, datetime.max.time())
        ).all()
        
        # Calculer les stats
        total_pas = sum(s.pas for s in summaries)
        total_calories = sum(s.calories_actives for s in summaries)
        total_distance = sum(s.distance_metres for s in summaries)
        
        # Calcul du streak
        streak = self._calculate_streak(user_id, db)
        
        # Moyenne quotidienne
        days_with_data = len(summaries) or 1
        
        return {
            "total_pas": total_pas,
            "total_calories": total_calories,
            "total_distance_km": total_distance / 1000,
            "total_activities": len(activities),
            "streak_jours": streak,
            "moyenne_pas_jour": total_pas // days_with_data,
            "moyenne_calories_jour": total_calories // days_with_data,
            "derniere_sync": user.garmin_token.derniere_sync if user.garmin_token else None,
            "garmin_connected": user.garmin_connected,
            "objectif_pas": user.objectif_pas_quotidien,
            "objectif_calories": user.objectif_calories_brulees,
        }
    
    def _calculate_streak(self, user_id: int, db: Session) -> int:
        """Calcule le nombre de jours consécutifs avec objectif atteint"""
        user = db.get(UserProfile, user_id)
        if not user:
            return 0
        
        objectif_pas = user.objectif_pas_quotidien
        
        # Récupérer les 60 derniers jours
        end_date = date.today()
        start_date = end_date - timedelta(days=60)
        
        summaries = db.query(GarminDailySummary).filter(
            GarminDailySummary.user_id == user_id,
            GarminDailySummary.date >= start_date,
            GarminDailySummary.date <= end_date
        ).order_by(GarminDailySummary.date.desc()).all()
        
        streak = 0
        current_date = end_date
        
        summary_by_date = {s.date: s for s in summaries}
        
        while current_date >= start_date:
            summary = summary_by_date.get(current_date)
            if summary and summary.pas >= objectif_pas:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


def get_garmin_service() -> GarminService:
    """Factory pour obtenir le service Garmin"""
    return GarminService()


# ═══════════════════════════════════════════════════════════
# HELPERS POUR CRÉATION UTILISATEURS
# ═══════════════════════════════════════════════════════════


@avec_session_db
def get_or_create_user(username: str, display_name: str, db: Session = None) -> UserProfile:
    """Récupère ou crée un profil utilisateur"""
    user = db.query(UserProfile).filter_by(username=username).first()
    
    if not user:
        user = UserProfile(
            username=username,
            display_name=display_name,
            avatar_emoji="👩" if username == "anne" else "👨",
        )
        db.add(user)
        db.commit()
        logger.info(f"Utilisateur créé: {username}")
    
    return user


@avec_session_db
def init_family_users(db: Session = None) -> tuple[UserProfile, UserProfile]:
    """Initialise les profils Anne et Mathieu"""
    anne = get_or_create_user("anne", "Anne", db=db)
    mathieu = get_or_create_user("mathieu", "Mathieu", db=db)
    return anne, mathieu


@avec_session_db
def get_user_by_username(username: str, db: Session = None) -> UserProfile | None:
    """Récupère un utilisateur par son username"""
    return db.query(UserProfile).filter_by(username=username).first()


@avec_session_db  
def list_all_users(db: Session = None) -> list[UserProfile]:
    """Liste tous les utilisateurs"""
    return db.query(UserProfile).all()


