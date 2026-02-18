"""
Service d'alertes météo pour le jardin.

Fonctionnalités:
- Récupération des données météo via API
- Alertes gel/canicule/pluie
- Conseils de jardinage contextuels
- Calendrier d'arrosage intelligent
- Prévisions sur 7 jours
"""

import logging
from datetime import date, timedelta
from decimal import Decimal
from enum import Enum, StrEnum
from uuid import UUID

import httpx
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import (
    AlerteMeteo as AlerteMeteoModel,
)
from src.core.models import (
    ConfigMeteo,
)

from .meteo_jardin import MeteoJardinMixin
from .weather_codes import (
    direction_from_degrees,
    weathercode_to_condition,
    weathercode_to_icon,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES ET SCHÉMAS
# ═══════════════════════════════════════════════════════════


class TypeAlertMeteo(StrEnum):
    """Types d'alertes météo."""

    GEL = "gel"
    CANICULE = "canicule"
    PLUIE_FORTE = "pluie_forte"
    SECHERESSE = "sécheresse"
    VENT_FORT = "vent_fort"
    ORAGE = "orage"
    GRELE = "grêle"
    NEIGE = "neige"


class NiveauAlerte(StrEnum):
    """Niveau de gravité de l'alerte."""

    INFO = "info"
    ATTENTION = "attention"
    DANGER = "danger"


class MeteoJour(BaseModel):
    """Données météo pour un jour."""

    date: date
    temperature_min: float
    temperature_max: float
    temperature_moyenne: float
    humidite: int  # %
    precipitation_mm: float
    probabilite_pluie: int  # %
    vent_km_h: float
    direction_vent: str = ""
    uv_index: int = 0
    lever_soleil: str = ""
    coucher_soleil: str = ""
    condition: str = ""  # ensoleillé, nuageux, pluvieux, etc.
    icone: str = ""


class AlerteMeteo(BaseModel):
    """Alerte météo pour le jardin."""

    type_alerte: TypeAlertMeteo
    niveau: NiveauAlerte
    titre: str
    message: str
    conseil_jardin: str
    date_debut: date
    date_fin: date | None = None
    temperature: float | None = None


class ConseilJardin(BaseModel):
    """Conseil de jardinage basé sur la météo."""

    priorite: int = 1  # 1 = haute, 3 = basse
    icone: str = "🌱"
    titre: str
    description: str
    plantes_concernees: list[str] = Field(default_factory=list)
    action_recommandee: str = ""


class PlanArrosage(BaseModel):
    """Plan d'arrosage intelligent."""

    date: date
    besoin_arrosage: bool
    quantite_recommandee_litres: float = 0.0
    raison: str = ""
    plantes_prioritaires: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# SERVICE MÉTÉO JARDIN
# ═══════════════════════════════════════════════════════════


class ServiceMeteo(MeteoJardinMixin):
    """
    Service d'alertes météo pour le jardinage.

    Utilise Open-Meteo API (gratuite, sans clé API).

    NOTE: Les méthodes jardin (generer_conseils, generer_plan_arrosage)
    sont déléguées au MeteoJardinMixin (voir meteo_jardin.py).
    """

    # Seuils d'alerte
    SEUIL_GEL = 2.0  # °C
    SEUIL_CANICULE = 35.0  # °C
    SEUIL_SECHERESSE_JOURS = 7  # jours sans pluie significative
    SEUIL_PLUIE_FORTE = 20.0  # mm/jour
    SEUIL_VENT_FORT = 50.0  # km/h

    # API Open-Meteo (gratuite)
    API_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, latitude: float = 48.8566, longitude: float = 2.3522):
        """
        Initialise le service.

        Args:
            latitude: Latitude (défaut = Paris)
            longitude: Longitude (défaut = Paris)
        """
        self.latitude = latitude
        self.longitude = longitude
        self.http_client = httpx.Client(timeout=30.0)

    def set_location(self, latitude: float, longitude: float):
        """Met à jour la localisation."""
        self.latitude = latitude
        self.longitude = longitude

    def set_location_from_city(self, city: str):
        """
        Met à jour la localisation à partir d'un nom de ville.

        Args:
            city: Nom de la ville
        """
        # Géocodage via Open-Meteo
        try:
            response = self.http_client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "fr"},
            )
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                result = data["results"][0]
                self.latitude = result["latitude"]
                self.longitude = result["longitude"]
                logger.info(f"Localisation mise à jour: {city} ({self.latitude}, {self.longitude})")
                return True
        except Exception as e:
            logger.error(f"Erreur géocodage: {e}")

        return False

    # ═══════════════════════════════════════════════════════════
    # RÉCUPÉRATION MÉTÉO
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=3600)  # Cache 1h
    @avec_gestion_erreurs(default_return=None, afficher_erreur=True)
    def get_previsions(self, nb_jours: int = 7) -> list[MeteoJour] | None:
        """
        Récupère les prévisions météo.

        Args:
            nb_jours: Nombre de jours de prévision (max 16)

        Returns:
            Liste des prévisions journalières
        """
        try:
            response = self.http_client.get(
                self.API_URL,
                params={
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "daily": [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "precipitation_probability_max",
                        "wind_speed_10m_max",
                        "wind_direction_10m_dominant",
                        "uv_index_max",
                        "sunrise",
                        "sunset",
                        "weathercode",
                    ],
                    "timezone": "Europe/Paris",
                    "forecast_days": min(nb_jours, 16),
                },
            )
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            dates = daily.get("time", [])

            previsions = []
            for i, date_str in enumerate(dates):
                temp_min = daily["temperature_2m_min"][i]
                temp_max = daily["temperature_2m_max"][i]

                previsions.append(
                    MeteoJour(
                        date=date.fromisoformat(date_str),
                        temperature_min=temp_min,
                        temperature_max=temp_max,
                        temperature_moyenne=(temp_min + temp_max) / 2,
                        humidite=50,  # Non fourni par Open-Meteo daily
                        precipitation_mm=daily["precipitation_sum"][i] or 0,
                        probabilite_pluie=daily["precipitation_probability_max"][i] or 0,
                        vent_km_h=daily["wind_speed_10m_max"][i] or 0,
                        direction_vent=direction_from_degrees(
                            daily["wind_direction_10m_dominant"][i]
                        ),
                        uv_index=daily["uv_index_max"][i] or 0,
                        lever_soleil=daily["sunrise"][i].split("T")[1]
                        if daily.get("sunrise")
                        else "",
                        coucher_soleil=daily["sunset"][i].split("T")[1]
                        if daily.get("sunset")
                        else "",
                        condition=weathercode_to_condition(daily["weathercode"][i]),
                        icone=weathercode_to_icon(daily["weathercode"][i]),
                    )
                )

            return previsions

        except Exception as e:
            logger.error(f"Erreur récupération météo: {e}")
            return None

    def _direction_from_degrees(self, degrees: float | None) -> str:
        """Convertit des degrés en direction cardinale. Délègue à weather_utils."""
        return direction_from_degrees(degrees)

    def _weathercode_to_condition(self, code: int | None) -> str:
        """Convertit le code météo en description. Délègue à weather_utils."""
        return weathercode_to_condition(code)

    def _weathercode_to_icon(self, code: int | None) -> str:
        """Convertit le code météo en emoji. Délègue à weather_utils."""
        return weathercode_to_icon(code)

    # ═══════════════════════════════════════════════════════════
    # ALERTES
    # ═══════════════════════════════════════════════════════════

    def generer_alertes(self, previsions: list[MeteoJour] | None = None) -> list[AlerteMeteo]:
        """
        Génère les alertes météo basées sur les prévisions.

        Args:
            previsions: Prévisions météo (récupérées si non fournies)

        Returns:
            Liste des alertes
        """
        if previsions is None:
            previsions = self.get_previsions(7)

        if not previsions:
            return []

        alertes = []

        for prev in previsions:
            # Alerte gel
            if prev.temperature_min <= self.SEUIL_GEL:
                niveau = NiveauAlerte.DANGER if prev.temperature_min < 0 else NiveauAlerte.ATTENTION
                alertes.append(
                    AlerteMeteo(
                        type_alerte=TypeAlertMeteo.GEL,
                        niveau=niveau,
                        titre="🥶 Risque de gel",
                        message=f"Température minimale prévue: {prev.temperature_min}°C",
                        conseil_jardin="Protégez vos plantes sensibles avec un voile d'hivernage. Rentrez les pots fragiles.",
                        date_debut=prev.date,
                        temperature=prev.temperature_min,
                    )
                )

            # Alerte canicule
            if prev.temperature_max >= self.SEUIL_CANICULE:
                niveau = (
                    NiveauAlerte.DANGER if prev.temperature_max >= 40 else NiveauAlerte.ATTENTION
                )
                alertes.append(
                    AlerteMeteo(
                        type_alerte=TypeAlertMeteo.CANICULE,
                        niveau=niveau,
                        titre="🔥 Canicule",
                        message=f"Température maximale prévue: {prev.temperature_max}°C",
                        conseil_jardin="Arrosez tôt le matin ou tard le soir. Installez des ombrages. Paillez abondamment.",
                        date_debut=prev.date,
                        temperature=prev.temperature_max,
                    )
                )

            # Alerte pluie forte
            if prev.precipitation_mm >= self.SEUIL_PLUIE_FORTE:
                alertes.append(
                    AlerteMeteo(
                        type_alerte=TypeAlertMeteo.PLUIE_FORTE,
                        niveau=NiveauAlerte.ATTENTION,
                        titre="🌧️ Fortes pluies",
                        message=f"Précipitations prévues: {prev.precipitation_mm}mm",
                        conseil_jardin="Vérifiez le drainage. Protégez les semis. Évitez de marcher sur sol détrempé.",
                        date_debut=prev.date,
                    )
                )

            # Alerte vent fort
            if prev.vent_km_h >= self.SEUIL_VENT_FORT:
                alertes.append(
                    AlerteMeteo(
                        type_alerte=TypeAlertMeteo.VENT_FORT,
                        niveau=NiveauAlerte.ATTENTION,
                        titre="💨 Vent fort",
                        message=f"Vent prévu: {prev.vent_km_h} km/h",
                        conseil_jardin="Tuteurez les plantes hautes. Rentrez ou fixez les pots légers. Reportez les traitements.",
                        date_debut=prev.date,
                    )
                )

            # Alerte orage
            if prev.condition.lower() == "orage" or "orage" in prev.condition.lower():
                alertes.append(
                    AlerteMeteo(
                        type_alerte=TypeAlertMeteo.ORAGE,
                        niveau=NiveauAlerte.ATTENTION,
                        titre="⛈️ Orages",
                        message="Orages prévus",
                        conseil_jardin="Débranchez les systèmes d'arrosage automatique. Protégez les jeunes plants.",
                        date_debut=prev.date,
                    )
                )

        # Vérifier sécheresse (plusieurs jours sans pluie)
        jours_sans_pluie = 0
        for prev in previsions:
            if prev.precipitation_mm < 2 and prev.probabilite_pluie < 20:
                jours_sans_pluie += 1
            else:
                break

        if jours_sans_pluie >= self.SEUIL_SECHERESSE_JOURS:
            alertes.append(
                AlerteMeteo(
                    type_alerte=TypeAlertMeteo.SECHERESSE,
                    niveau=NiveauAlerte.ATTENTION,
                    titre="☀️ Période sèche",
                    message=f"{jours_sans_pluie} jours sans pluie significative prévus",
                    conseil_jardin="Renforcez l'arrosage. Privilégiez le paillage. Arrosez en profondeur moins souvent.",
                    date_debut=previsions[0].date,
                    date_fin=previsions[min(jours_sans_pluie - 1, len(previsions) - 1)].date,
                )
            )

        return alertes

    # NOTE: generer_conseils() et generer_plan_arrosage() sont fournis
    # par MeteoJardinMixin (voir meteo_jardin.py)

    # ═══════════════════════════════════════════════════════════
    # PERSISTANCE BASE DE DONNÉES
    # ═══════════════════════════════════════════════════════════

    @avec_session_db
    def sauvegarder_alerte(
        self,
        alerte: AlerteMeteo,
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> AlerteMeteoModel | None:
        """
        Sauvegarde une alerte météo dans la base de données.

        Args:
            alerte: Alerte Pydantic à sauvegarder
            user_id: UUID de l'utilisateur (optionnel)
            db: Session SQLAlchemy (injectée)

        Returns:
            Modèle AlerteMeteo créé
        """
        try:
            db_alerte = AlerteMeteoModel(
                type_alerte=alerte.type_alerte.value,
                niveau=alerte.niveau.value,
                titre=alerte.titre,
                message=alerte.message,
                conseil_jardin=alerte.conseil_jardin,
                date_debut=alerte.date_debut,
                date_fin=alerte.date_fin,
                temperature=Decimal(str(alerte.temperature)) if alerte.temperature else None,
                user_id=UUID(str(user_id)) if user_id else None,
            )
            db.add(db_alerte)
            db.commit()
            db.refresh(db_alerte)
            logger.info(f"Alerte météo sauvegardée: {db_alerte.id}")
            return db_alerte
        except Exception as e:
            logger.error(f"Erreur sauvegarde alerte météo: {e}")
            db.rollback()
            return None

    @avec_session_db
    def sauvegarder_alertes(
        self,
        alertes: list[AlerteMeteo],
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> list[AlerteMeteoModel]:
        """
        Sauvegarde plusieurs alertes météo.

        Args:
            alertes: Liste d'alertes à sauvegarder
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Liste des modèles créés
        """
        resultats = []
        for alerte in alertes:
            db_alerte = AlerteMeteoModel(
                type_alerte=alerte.type_alerte.value,
                niveau=alerte.niveau.value,
                titre=alerte.titre,
                message=alerte.message,
                conseil_jardin=alerte.conseil_jardin,
                date_debut=alerte.date_debut,
                date_fin=alerte.date_fin,
                temperature=Decimal(str(alerte.temperature)) if alerte.temperature else None,
                user_id=UUID(str(user_id)) if user_id else None,
            )
            db.add(db_alerte)
            resultats.append(db_alerte)

        try:
            db.commit()
            for r in resultats:
                db.refresh(r)
            logger.info(f"{len(resultats)} alertes météo sauvegardées")
        except Exception as e:
            logger.error(f"Erreur sauvegarde alertes: {e}")
            db.rollback()
            return []

        return resultats

    @avec_session_db
    def lister_alertes_actives(
        self,
        user_id: UUID | str | None = None,
        db: Session = None,
    ) -> list[AlerteMeteoModel]:
        """
        Liste les alertes actives (non lues, date pas dépassée).

        Args:
            user_id: UUID de l'utilisateur (filtre optionnel)
            db: Session SQLAlchemy

        Returns:
            Liste des alertes actives
        """
        query = db.query(AlerteMeteoModel).filter(
            AlerteMeteoModel.lu == False,
            AlerteMeteoModel.date_debut >= date.today() - timedelta(days=1),
        )

        if user_id:
            query = query.filter(AlerteMeteoModel.user_id == UUID(str(user_id)))

        return query.order_by(AlerteMeteoModel.date_debut).all()

    @avec_session_db
    def marquer_alerte_lue(
        self,
        alerte_id: int,
        db: Session = None,
    ) -> bool:
        """
        Marque une alerte comme lue.

        Args:
            alerte_id: ID de l'alerte
            db: Session SQLAlchemy

        Returns:
            True si succès
        """
        alerte = db.query(AlerteMeteoModel).filter(AlerteMeteoModel.id == alerte_id).first()
        if alerte:
            alerte.lu = True
            db.commit()
            return True
        return False

    @avec_session_db
    def obtenir_config_meteo(
        self,
        user_id: UUID | str,
        db: Session = None,
    ) -> ConfigMeteo | None:
        """
        Récupère la configuration météo d'un utilisateur.

        Args:
            user_id: UUID de l'utilisateur
            db: Session SQLAlchemy

        Returns:
            Configuration ou None
        """
        return db.query(ConfigMeteo).filter(ConfigMeteo.user_id == UUID(str(user_id))).first()

    @avec_session_db
    def sauvegarder_config_meteo(
        self,
        user_id: UUID | str,
        latitude: float | None = None,
        longitude: float | None = None,
        ville: str | None = None,
        surface_jardin: float | None = None,
        db: Session = None,
    ) -> ConfigMeteo:
        """
        Crée ou met à jour la configuration météo d'un utilisateur.

        Args:
            user_id: UUID de l'utilisateur
            latitude, longitude: Coordonnées
            ville: Nom de la ville
            surface_jardin: Surface en m²
            db: Session SQLAlchemy

        Returns:
            Configuration créée ou mise à jour
        """
        config = db.query(ConfigMeteo).filter(ConfigMeteo.user_id == UUID(str(user_id))).first()

        if not config:
            config = ConfigMeteo(user_id=UUID(str(user_id)))
            db.add(config)

        if latitude is not None:
            config.latitude = Decimal(str(latitude))
        if longitude is not None:
            config.longitude = Decimal(str(longitude))
        if ville is not None:
            config.ville = ville
        if surface_jardin is not None:
            config.surface_jardin_m2 = Decimal(str(surface_jardin))

        db.commit()
        db.refresh(config)
        return config


# Alias pour rétrocompatibilité
WeatherGardenService = ServiceMeteo
WeatherService = ServiceMeteo


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_weather_service: ServiceMeteo | None = None


def obtenir_service_meteo() -> ServiceMeteo:
    """Factory pour le service météo (convention française)."""
    global _weather_service
    if _weather_service is None:
        _weather_service = ServiceMeteo()
    return _weather_service


def get_weather_service() -> ServiceMeteo:
    """Factory pour le service météo (alias anglais)."""
    return obtenir_service_meteo()


def get_weather_garden_service() -> ServiceMeteo:
    """Factory pour le service météo jardin (alias rétrocompatibilité)."""
    return obtenir_service_meteo()


# ═══════════════════════════════════════════════════════════
# ALIAS UI RÉTROCOMPATIBILITÉ
# ═══════════════════════════════════════════════════════════


def render_weather_garden_ui():  # pragma: no cover
    """Alias rétrocompatible — délègue à src.ui.views.meteo."""
    from src.ui.views.meteo import afficher_meteo_jardin

    return afficher_meteo_jardin()
