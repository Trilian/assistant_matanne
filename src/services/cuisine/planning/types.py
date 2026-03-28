"""
Types et schémas Pydantic pour le service de planning.

Centralise tous les modèles de validation pour:
- Planning hebdomadaire (JourPlanning, ParametresEquilibre)
- Vue complète semaine (JourCompletSchema, SemaineCompleSchema)
- Génération IA (SemaineGenereeIASchema)
"""

from datetime import date

from pydantic import BaseModel, Field, model_validator

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

    poisson_blanc_jours: list[str] = Field(
        default_factory=lambda: ["lundi"]
    )  # Jours avec poisson blanc
    poisson_gras_jours: list[str] = Field(
        default_factory=lambda: ["jeudi"]
    )  # Jours avec poisson gras
    viande_rouge_jours: list[str] = Field(
        default_factory=lambda: ["mardi"]
    )  # Jours avec viande rouge
    vegetarien_jours: list[str] = Field(default_factory=lambda: ["mercredi"])  # Jours végé
    pates_riz_count: int = Field(default=3, ge=1, le=5)  # Combien de fois pâtes/riz
    ingredients_exclus: list[str] = Field(default_factory=list)  # Allergies, phobies
    preferences_extras: dict = Field(default_factory=dict)  # Autres contraintes

    @model_validator(mode="before")
    @classmethod
    def _mapper_poisson_jours_legacy(cls, data):
        """Compatibilité avec l'ancien champ `poisson_jours` utilisé par les tests."""
        if not isinstance(data, dict):
            return data

        poisson_jours = data.get("poisson_jours")
        if poisson_jours and "poisson_blanc_jours" not in data and "poisson_gras_jours" not in data:
            if len(poisson_jours) == 1:
                data["poisson_blanc_jours"] = list(poisson_jours)
                data["poisson_gras_jours"] = []
            else:
                data["poisson_blanc_jours"] = [poisson_jours[0]]
                data["poisson_gras_jours"] = list(poisson_jours[1:])
        return data

    @property
    def poisson_jours(self) -> list[str]:
        """Tous les jours poisson (blanc + gras) pour compatibilité."""
        return self.poisson_blanc_jours + self.poisson_gras_jours


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
