"""
Schemas Pydantic pour le Jardin.

Modèles de validation pour:
- Conseils jardin contextuels
- Plans d'arrosage
- Diagnostics de plantes
- Zones jardin, plans, plantes et actions
"""

from datetime import date as date_type

from pydantic import BaseModel, Field

from .schemas_enums import EtatPlante, NiveauUrgence, TypeZoneJardin

__all__ = [
    "ConseilJardin",
    "PlanArrosage",
    "DiagnosticPlante",
    "ZoneJardinCreate",
    "PlanJardinCreate",
    "PlanteJardinCreate",
    "ActionPlanteCreate",
    "PlanteCreate",
]


# ═══════════════════════════════════════════════════════════
# JARDIN
# ═══════════════════════════════════════════════════════════


class ConseilJardin(BaseModel):
    """Conseil jardin contextuel."""

    titre: str
    contenu: str
    priorite: NiveauUrgence = NiveauUrgence.MOYENNE
    type_conseil: str  # saison, meteo, plante, general
    plantes_concernees: list[str] = Field(default_factory=list)


class PlanArrosage(BaseModel):
    """Plan d'arrosage pour une zone/plante."""

    zone_ou_plante: str
    frequence: str  # quotidien, tous_2_jours, hebdo
    quantite_litres: float | None = None
    meilleur_moment: str  # matin, soir
    ajuste_meteo: bool = True
    prochaine_date: date_type | None = None
    notes: str | None = None


class DiagnosticPlante(BaseModel):
    """Diagnostic d'une plante (via photo IA)."""

    plante_identifiee: str | None = None
    etat: EtatPlante
    problemes_detectes: list[str] = Field(default_factory=list)
    traitements_suggeres: list[str] = Field(default_factory=list)
    confiance: float = 0.0  # 0-1


class ZoneJardinCreate(BaseModel):
    """Création d'une zone jardin."""

    nom: str
    type_zone: TypeZoneJardin
    superficie_m2: float | None = None
    exposition: str | None = None  # N, S, E, O, NE...
    type_sol: str | None = None
    coordonnees: list[list[float]] | None = None  # Polygone [[x,y], ...]
    arrosage_auto: bool = False
    notes: str | None = None


class PlanJardinCreate(BaseModel):
    """Création d'un plan de jardin."""

    nom: str
    largeur: float  # mètres
    hauteur: float  # mètres
    description: str | None = None


class PlanteJardinCreate(BaseModel):
    """Ajout d'une plante sur le plan jardin (avec position)."""

    nom: str
    variete: str | None = None
    zone_id: int
    position_x: float
    position_y: float
    date_plantation: date_type | None = None
    etat: EtatPlante = EtatPlante.BON
    notes: str | None = None


class ActionPlanteCreate(BaseModel):
    """Action effectuée sur une plante."""

    plante_id: int
    type_action: str  # arrosage, taille, recolte, traitement, etc.
    date_action: date_type | None = None
    notes: str | None = None
    quantite: float | None = None  # Pour récoltes


class PlanteCreate(BaseModel):
    """Création d'une plante dans le jardin."""

    nom: str
    variete: str | None = None
    zone_id: int
    position_x: float | None = None
    position_y: float | None = None
    date_plantation: date_type | None = None
    arrosage_frequence: str | None = None
    exposition_ideale: str | None = None
    notes: str | None = None
