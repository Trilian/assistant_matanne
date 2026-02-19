"""
Schemas Pydantic pour les services Maison.

Hub de ré-export — les schemas sont définis dans des sous-modules par domaine:
- schemas_enums: Tous les StrEnum/Enum
- schemas_jardin: Jardin (conseils, arrosage, plantes)


Ce fichier conserve les schemas de:
- Briefings et alertes
- Entretien (routines, tâches)
- Projets (estimation, matériaux)
- Énergie (éco-score, badges)
- Tâches récurrentes & planning

Tous les imports ``from .schemas import X`` restent fonctionnels.
"""

from datetime import date as date_type
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ═══════════════════════════════════════════════════════════
# RÉ-EXPORTS depuis les sous-modules domaine
# ═══════════════════════════════════════════════════════════
from .schemas_enums import *  # noqa: F401,F403

# Imports locaux nécessaires aux classes restantes
from .schemas_enums import NiveauUrgence, TypeAlerteMaison
from .schemas_jardin import *  # noqa: F401,F403

# ═══════════════════════════════════════════════════════════
# BRIEFING & ALERTES
# ═══════════════════════════════════════════════════════════


class AlerteMaison(BaseModel):
    """Alerte maison avec niveau d'urgence."""

    model_config = ConfigDict(from_attributes=True)

    type: TypeAlerteMaison
    niveau: NiveauUrgence
    titre: str
    message: str
    action_suggeree: str | None = None
    date_limite: date_type | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ActionPrioritaire(BaseModel):
    """Action prioritaire pour le briefing quotidien."""

    titre: str
    description: str | None = None
    duree_estimee_min: int | None = None
    module: str  # jardin, entretien, projet
    lien: str | None = None  # Lien vers le module


class BriefingMaison(BaseModel):
    """Briefing quotidien maison généré par l'IA."""

    date: date_type = Field(default_factory=date_type.today)
    resume: str = ""
    taches_jour: list[str] = Field(default_factory=list)
    alertes: list[AlerteMaison] = Field(default_factory=list)
    meteo_impact: str | None = None
    projets_actifs: list[str] = Field(default_factory=list)
    priorites: list[str] = Field(default_factory=list)
    eco_score_jour: int | None = None


# ═══════════════════════════════════════════════════════════
# ENTRETIEN
# ═══════════════════════════════════════════════════════════


class TacheRoutineCreate(BaseModel):
    """Tâche d'une routine."""

    nom: str
    description: str | None = None
    ordre: int = 0
    heure_prevue: str | None = None  # HH:MM
    duree_estimee_min: int | None = None


class RoutineCreate(BaseModel):
    """Création d'une routine d'entretien."""

    nom: str
    description: str | None = None
    categorie: str  # menage, cuisine, jardin, enfant
    frequence: str  # quotidien, hebdo, mensuel, saisonnier
    jour_semaine: int | None = None  # 0=lundi, 6=dimanche
    taches: list[TacheRoutineCreate] = Field(default_factory=list)


class RoutineSuggestionIA(BaseModel):
    """Suggestion de routine par l'IA."""

    nom: str
    description: str
    taches_suggerees: list[str]
    frequence_recommandee: str
    duree_totale_estimee_min: int


# ═══════════════════════════════════════════════════════════
# PROJETS
# ═══════════════════════════════════════════════════════════


class MaterielProjet(BaseModel):
    """Matériel nécessaire pour un projet."""

    nom: str
    quantite: float = 1.0
    unite: str = "unité"
    prix_estime: Decimal | None = None
    magasin_suggere: str | None = None
    url: str | None = None
    alternatif_eco: str | None = None
    alternatif_prix: Decimal | None = None


class TacheProjetCreate(BaseModel):
    """Tâche d'un projet."""

    nom: str
    description: str | None = None
    ordre: int = 0
    duree_estimee_min: int | None = None
    date_echeance: date_type | None = None
    materiels_requis: list[str] = Field(default_factory=list)


class ProjetCreate(BaseModel):
    """Création d'un projet maison."""

    nom: str
    description: str | None = None
    categorie: str  # travaux, renovation, amenagement, reparation
    priorite: str = "moyenne"
    date_fin_prevue: date_type | None = None
    budget_estime: Decimal | None = None


class ProjetEstimation(BaseModel):
    """Estimation complète d'un projet par l'IA."""

    nom_projet: str
    description_analysee: str
    budget_estime_min: Decimal
    budget_estime_max: Decimal
    duree_estimee_jours: int
    taches_suggerees: list[TacheProjetCreate]
    materiels_necessaires: list[MaterielProjet]
    risques_identifies: list[str] = Field(default_factory=list)
    conseils_ia: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# TÂCHES RÉCURRENTES & PLANNING
# ═══════════════════════════════════════════════════════════

from enum import StrEnum  # noqa: E402


class FrequenceTache(StrEnum):
    """Fréquence de récurrence d'une tâche."""

    QUOTIDIEN = "quotidien"
    HEBDOMADAIRE = "hebdomadaire"
    BIHEBDOMADAIRE = "bihebdomadaire"
    MENSUEL = "mensuel"
    TRIMESTRIEL = "trimestriel"
    SEMESTRIEL = "semestriel"
    ANNUEL = "annuel"


class TacheMaisonRecurrente(BaseModel):
    """Tâche maison récurrente à synchroniser avec le planning."""

    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    nom: str
    description: str | None = None
    categorie: str  # entretien, jardin, menage, administratif
    frequence: FrequenceTache
    jour_semaine: int | None = None  # 0=lundi, 6=dimanche (pour hebdo)
    jour_mois: int | None = None  # 1-31 (pour mensuel)
    mois: int | None = None  # 1-12 (pour annuel)
    duree_estimee_min: int | None = None
    priorite: NiveauUrgence = NiveauUrgence.MOYENNE
    actif: bool = True
    derniere_execution: date_type | None = None
    prochaine_execution: date_type | None = None


class SyncPlanningRequest(BaseModel):
    """Demande de synchronisation avec le planning familial."""

    taches_a_synchroniser: list[int] = Field(default_factory=list)  # IDs tâches
    projets_a_synchroniser: list[int] = Field(default_factory=list)  # IDs projets
    periode_debut: date_type = Field(default_factory=date_type.today)
    periode_fin: date_type | None = None
    inclure_recurrentes: bool = True
    notifier_membres: bool = True


class SyncPlanningResult(BaseModel):
    """Résultat de la synchronisation avec le planning."""

    succes: bool
    evenements_crees: int = 0
    evenements_mis_a_jour: int = 0
    evenements_supprimes: int = 0
    conflits_detectes: list[str] = Field(default_factory=list)
    prochains_evenements: list[dict[str, Any]] = Field(default_factory=list)
    message: str = ""
