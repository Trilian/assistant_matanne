"""
Modèles SQLAlchemy pour le jardin et la météo.

Contient :
- GardenZone : Zones du jardin (2600mÂ²)
- AlerteMeteo : Alertes météo pour le jardin
- ConfigMeteo : Configuration météo par utilisateur
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ENUMS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class GardenZoneType(str, Enum):
    """Type de zone jardin."""
    PELOUSE = "pelouse"
    POTAGER = "potager"
    ARBRES = "arbres"
    PISCINE = "piscine"
    TERRAIN_BOULES = "terrain_boules"
    TERRASSE = "terrasse"
    ALLEE = "allee"
    AUTRE = "autre"


class NiveauAlerte(str, Enum):
    """Niveaux d'alerte météo."""
    INFO = "info"
    ATTENTION = "attention"
    DANGER = "danger"


class TypeAlerteMeteo(str, Enum):
    """Types d'alertes météo."""
    GEL = "gel"
    CANICULE = "canicule"
    PLUIE_FORTE = "pluie_forte"
    VENT_FORT = "vent_fort"
    GRELE = "grele"
    NEIGE = "neige"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ZONES JARDIN (pour 2600mÂ²)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class GardenZone(Base):
    """Zone du jardin avec état et plan d'action.
    
    Pour gérer un grand jardin (2600mÂ²) par zones.
    """
    __tablename__ = "garden_zones"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Infos zone
    nom: Mapped[str] = mapped_column(String(200), nullable=False)
    type_zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    surface_m2: Mapped[Optional[int]] = mapped_column(Integer)
    
    # État actuel (1-5)
    etat_note: Mapped[int] = mapped_column(Integer, default=1)  # 1=catastrophe, 5=parfait
    etat_description: Mapped[Optional[str]] = mapped_column(Text)  # "Herbe jaune, pas entretenu"
    
    # Plan de remise en état
    objectif: Mapped[Optional[str]] = mapped_column(Text)  # "Pelouse verte et tondue"
    budget_estime: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    
    # Prochaine action
    prochaine_action: Mapped[Optional[str]] = mapped_column(String(200))
    date_prochaine_action: Mapped[Optional[date]] = mapped_column(Date)
    
    # Photos (JSON array: ["avant:url1", "apres:url2"])
    photos_url: Mapped[Optional[list[str]]] = mapped_column(JSON, default=list)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<GardenZone(id={self.id}, nom='{self.nom}', etat={self.etat_note}/5)>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TABLE ALERTES MÉTÉO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class AlerteMeteo(Base):
    """Alerte météo pour le jardin.
    
    Table SQL: alertes_meteo
    Utilisé par: src/services/weather.py
    
    Attributes:
        type_alerte: Type d'alerte (gel, canicule, etc.)
        niveau: Niveau (info, attention, danger)
        titre: Titre de l'alerte
        message: Message détaillé
        conseil_jardin: Conseil pour le jardin
        date_debut: Date de début de l'alerte
        date_fin: Date de fin
        temperature: Température associée
        lu: Si l'alerte a été lue
    """

    __tablename__ = "alertes_meteo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type_alerte: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    niveau: Mapped[str] = mapped_column(String(20), nullable=False, default="info")
    titre: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    conseil_jardin: Mapped[str | None] = mapped_column(Text)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    date_fin: Mapped[date | None] = mapped_column(Date)
    temperature: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lu: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Supabase user
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<AlerteMeteo(id={self.id}, type='{self.type_alerte}', niveau='{self.niveau}')>"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TABLE CONFIGURATION MÉTÉO
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class ConfigMeteo(Base):
    """Configuration météo par utilisateur.
    
    Table SQL: config_meteo
    
    Attributes:
        latitude: Latitude (par défaut Paris)
        longitude: Longitude (par défaut Paris)
        ville: Nom de la ville
        surface_jardin_m2: Surface du jardin en mÂ²
        notifications_*: Préférences de notifications
    """

    __tablename__ = "config_meteo"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), default=Decimal("48.8566"))
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), default=Decimal("2.3522"))
    ville: Mapped[str] = mapped_column(String(100), default="Paris")
    surface_jardin_m2: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("50"))
    
    # Préférences notifications
    notifications_gel: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_canicule: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_pluie: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Supabase user (unique)
    user_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), unique=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<ConfigMeteo(id={self.id}, ville='{self.ville}')>"
