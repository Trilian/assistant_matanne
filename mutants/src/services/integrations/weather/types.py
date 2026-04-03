"""
Types et schémas Pydantic pour le service météo jardin.

Contient les enums et modèles de données utilisés par le service météo,
le mixin jardin et le mixin persistence.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field

__all__ = [
    "TypeAlertMeteo",
    "NiveauAlerte",
    "MeteoJour",
    "AlerteMeteo",
    "ConseilJardin",
    "PlanArrosage",
]


# ═══════════════════════════════════════════════════════════
# ENUMS
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


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


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
    uv_index: float = 0.0
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
