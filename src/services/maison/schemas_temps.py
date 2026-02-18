"""
Schemas Pydantic pour le Suivi du Temps.

Modèles de validation pour:
- Types d'activités d'entretien/jardinage
- Sessions de travail (création, mise à jour, complète)
- Statistiques de temps (par activité, par zone, hebdo)
- Suggestions d'optimisation IA
- Recommandations matériel
- Analyse complète du temps
"""

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from .schemas_enums import NiveauUrgence, PrioriteRemplacement

__all__ = [
    "TypeActiviteEntretien",
    "SessionTravailCreate",
    "SessionTravailUpdate",
    "SessionTravail",
    "StatistiqueTempsActivite",
    "StatistiqueTempsZone",
    "ResumeTempsHebdo",
    "SuggestionOptimisation",
    "RecommandationMateriel",
    "AnalyseTempsIA",
    "AnalyseTempsRequest",
]


# ═══════════════════════════════════════════════════════════
# SUIVI DU TEMPS - ENTRETIEN & JARDINAGE
# ═══════════════════════════════════════════════════════════


class TypeActiviteEntretien(StrEnum):
    """Types d'activités d'entretien/jardinage."""

    # Jardin
    ARROSAGE = "arrosage"
    TONTE = "tonte"
    TAILLE = "taille"
    DESHERBAGE = "desherbage"
    PLANTATION = "plantation"
    RECOLTE = "recolte"
    COMPOST = "compost"
    TRAITEMENT = "traitement"

    # Ménage intérieur
    MENAGE_GENERAL = "menage_general"
    ASPIRATEUR = "aspirateur"
    LAVAGE_SOL = "lavage_sol"
    POUSSIERE = "poussiere"
    VITRES = "vitres"
    LESSIVE = "lessive"
    REPASSAGE = "repassage"

    # Entretien maison
    BRICOLAGE = "bricolage"
    PEINTURE = "peinture"
    PLOMBERIE = "plomberie"
    ELECTRICITE = "electricite"
    NETTOYAGE_EXTERIEUR = "nettoyage_exterieur"

    # Autres
    RANGEMENT = "rangement"
    ADMINISTRATIF = "administratif"
    AUTRE = "autre"


class SessionTravailCreate(BaseModel):
    """Création d'une session de travail."""

    type_activite: TypeActiviteEntretien
    zone_id: int | None = None  # Zone jardin si applicable
    piece_id: int | None = None  # Pièce si applicable
    description: str | None = None
    debut: datetime = Field(default_factory=datetime.now)


class SessionTravailUpdate(BaseModel):
    """Mise à jour d'une session (arrêt)."""

    fin: datetime = Field(default_factory=datetime.now)
    notes: str | None = None
    difficulte: int | None = Field(None, ge=1, le=5)  # 1-5
    satisfaction: int | None = Field(None, ge=1, le=5)  # 1-5


class SessionTravail(BaseModel):
    """Session de travail complète."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type_activite: TypeActiviteEntretien
    zone_id: int | None = None
    piece_id: int | None = None
    description: str | None = None
    debut: datetime
    fin: datetime | None = None
    duree_minutes: int | None = None
    notes: str | None = None
    difficulte: int | None = None
    satisfaction: int | None = None
    date_creation: datetime


class StatistiqueTempsActivite(BaseModel):
    """Statistiques de temps par type d'activité."""

    type_activite: TypeActiviteEntretien
    icone: str = "⏱️"
    temps_total_minutes: int = 0
    nb_sessions: int = 0
    temps_moyen_minutes: float = 0.0
    derniere_session: datetime | None = None
    tendance: str = "stable"  # hausse, baisse, stable


class StatistiqueTempsZone(BaseModel):
    """Statistiques de temps par zone/pièce."""

    zone_nom: str
    zone_type: str  # jardin, piece
    temps_total_minutes: int = 0
    nb_sessions: int = 0
    activites_principales: list[str] = Field(default_factory=list)


class ResumeTempsHebdo(BaseModel):
    """Résumé hebdomadaire du temps passé."""

    semaine_debut: date_type
    semaine_fin: date_type
    temps_total_minutes: int = 0
    temps_jardin_minutes: int = 0
    temps_menage_minutes: int = 0
    temps_bricolage_minutes: int = 0
    nb_sessions: int = 0
    jour_plus_actif: str | None = None
    activite_plus_frequente: TypeActiviteEntretien | None = None
    comparaison_semaine_precedente: float = 0.0  # % difference


class SuggestionOptimisation(BaseModel):
    """Suggestion IA pour optimiser le temps."""

    titre: str
    description: str
    type_suggestion: str  # regroupement, planification, materiel, delegation
    temps_economise_estime_min: int | None = None
    activites_concernees: list[TypeActiviteEntretien] = Field(default_factory=list)
    priorite: NiveauUrgence = NiveauUrgence.MOYENNE
    action_directe: str | None = None  # Lien ou action à effectuer


class RecommandationMateriel(BaseModel):
    """Recommandation IA d'achat de matériel pour gagner du temps."""

    nom_materiel: str
    description: str
    categorie: str  # jardin, menage, bricolage
    prix_estime_min: Decimal | None = None
    prix_estime_max: Decimal | None = None
    temps_economise_par_session_min: int | None = None
    retour_investissement_semaines: int | None = None
    activites_ameliorees: list[TypeActiviteEntretien] = Field(default_factory=list)
    priorite_achat: PrioriteRemplacement = PrioriteRemplacement.NORMALE
    lien_produit: str | None = None
    notes: str | None = None


class AnalyseTempsIA(BaseModel):
    """Analyse complète du temps par l'IA."""

    periode_analysee: str  # "semaine", "mois", "trimestre"
    resume_textuel: str
    temps_total_minutes: int = 0
    repartition_par_categorie: dict[str, int] = Field(default_factory=dict)
    suggestions_optimisation: list[SuggestionOptimisation] = Field(default_factory=list)
    recommandations_materiel: list[RecommandationMateriel] = Field(default_factory=list)
    objectif_temps_suggere_min: int | None = None  # Temps hebdo optimal suggéré
    score_efficacite: int | None = Field(None, ge=0, le=100)  # 0-100


class AnalyseTempsRequest(BaseModel):
    """Demande d'analyse IA du temps."""

    periode: str = "mois"  # semaine, mois, trimestre, annee
    inclure_suggestions: bool = True
    inclure_materiel: bool = True
    budget_materiel_max: Decimal | None = None
    objectif_temps_hebdo_min: int | None = None  # Objectif utilisateur
