"""
Types et schémas Pydantic pour le service de planning.

Centralise tous les modèles de validation pour:
- Planning hebdomadaire (JourPlanning, ParametresEquilibre)
- Vue complète semaine (JourCompletSchema, SemaineCompleSchema)
- Génération IA (SemaineGenereeIASchema)
"""

from datetime import date

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PLANNING DE BASE
# ═══════════════════════════════════════════════════════════


class JourPlanning(BaseModel):
    """Jour du planning généré par l'IA"""

    jour: str = Field(..., min_length=6, max_length=10)
    dejeuner: str = Field(..., min_length=3)
    diner: str = Field(..., min_length=3)


class SuggestionRecettesDay(BaseModel):
    """Suggestions de recettes pour un jour (3 options)"""

    jour_name: str  # Lundi, Mardi, etc.
    type_repas: str  # déjeuner, dîner
    suggestions: list[dict] = Field(
        ..., min_length=1, max_length=3
    )  # [{nom, description, type_proteines}]


class ParametresEquilibre(BaseModel):
    """Paramètres pour l'équilibre de la semaine"""

    poisson_jours: list[str] = Field(
        default_factory=lambda: ["lundi", "jeudi"]
    )  # Jours avec poisson
    viande_rouge_jours: list[str] = Field(
        default_factory=lambda: ["mardi"]
    )  # Jours avec viande rouge
    vegetarien_jours: list[str] = Field(default_factory=lambda: ["mercredi"])  # Jours végé
    pates_riz_count: int = Field(default=3, ge=1, le=5)  # Combien de fois pâtes/riz
    ingredients_exclus: list[str] = Field(default_factory=list)  # Allergies, phobies
    preferences_extras: dict = Field(default_factory=dict)  # Autres contraintes


# ═══════════════════════════════════════════════════════════
# SCHÉMAS PLANNING UNIFIÉ (VUE COMPLÈTE)
# ═══════════════════════════════════════════════════════════


class JourCompletSchema(BaseModel):
    """Vue complète d'un jour du planning"""

    date: date
    charge: str  # "faible" | "normal" | "intense"
    charge_score: int  # 0-100
    repas: list[dict] = Field(default_factory=list)
    activites: list[dict] = Field(default_factory=list)
    projets: list[dict] = Field(default_factory=list)
    routines: list[dict] = Field(default_factory=list)
    events: list[dict] = Field(default_factory=list)
    budget_jour: float = 0.0
    alertes: list[str] = Field(default_factory=list)
    suggestions_ia: list[str] = Field(default_factory=list)


class SemaineCompleSchema(BaseModel):
    """Vue complète d'une semaine"""

    semaine_debut: date
    semaine_fin: date
    jours: dict[str, JourCompletSchema]  # "2026-01-25": JourCompletSchema
    stats_semaine: dict = Field(default_factory=dict)
    charge_globale: str  # "faible" | "normal" | "intense"
    alertes_semaine: list[str] = Field(default_factory=list)


class SemaineGenereeIASchema(BaseModel):
    """Semaine générée par l'IA"""

    repas_proposes: list[dict] = Field(default_factory=list)
    activites_proposees: list[dict] = Field(default_factory=list)
    projets_suggeres: list[dict] = Field(default_factory=list)
    harmonie_description: str = ""
    raisons: list[str] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Schémas planning de base
    "JourPlanning",
    "SuggestionRecettesDay",
    "ParametresEquilibre",
    # Schémas planning unifié
    "JourCompletSchema",
    "SemaineCompleSchema",
    "SemaineGenereeIASchema",
]
