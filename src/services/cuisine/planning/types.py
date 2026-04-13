"""
Types et schémas Pydantic pour le service de planning.

Centralise tous les modèles de validation pour:
- Planning hebdomadaire (JourPlanning, ParametresEquilibre)
- Vue complète semaine (JourCompletSchema, SemaineCompleSchema)
- Génération IA (SemaineGenereeIASchema)
"""

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

# ═══════════════════════════════════════════════════════════
# SCHÉMAS PLANNING DE BASE
# ═══════════════════════════════════════════════════════════


class JourPlanning(BaseModel):
    """Jour du planning généré par l'IA.

    Structure complète par slot:
    - petit_dejeuner: texte simple en semaine, peut être recette le weekend (est_recette=True)
    - dejeuner/diner: plat = toujours recette; entrée/laitage/dessert optionnels selon complexité
    - gouter: texte ou recette si préparation réelle
    - *_est_recette: True si l'IA juge que c'est une vraie préparation à lier à une recette
    - laitage: texte seul uniquement (yaourt, fromage blanc, fromage...) — jamais une recette
    """

    jour: str = Field(..., min_length=4, max_length=12)
    dejeuner: str = Field(..., min_length=3)
    diner: str = Field(..., min_length=3)

    # Petit-déjeuner: texte simple (tartines, céréales...) ou recette si complexe (crêpes, gaufres...)
    petit_dejeuner: str | None = None
    petit_dejeuner_est_recette: bool = False

    # Déjeuner — entrée optionnelle
    dejeuner_entree: str | None = None
    dejeuner_entree_est_recette: bool = False
    # Déjeuner — laitage texte uniquement (pas de flag est_recette)
    dejeuner_laitage: str | None = None
    # Déjeuner — dessert optionnel
    dejeuner_dessert: str | None = None
    dejeuner_dessert_est_recette: bool = False

    # Goûter — obligatoire, fallback "Fruit de saison" si l'IA renvoie null
    gouter: str | None = None  # None accepté en entrée mais normalisé avant persistance
    gouter_est_recette: bool = False

    # Dîner — entrée optionnelle
    diner_entree: str | None = None
    diner_entree_est_recette: bool = False
    # Dîner — laitage texte uniquement
    diner_laitage: str | None = None
    # Dîner — dessert optionnel
    diner_dessert: str | None = None
    diner_dessert_est_recette: bool = False

    # Restes réchauffés — déjeuner ou dîner peut être un reste du repas précédent
    dejeuner_est_reste: bool = False
    dejeuner_reste_source: str | None = None  # ex: "dîner de lundi"
    diner_est_reste: bool = False
    diner_reste_source: str | None = None  # ex: "déjeuner de mercredi"


class RecetteEnrichieIA(BaseModel):
    """Recette enrichie par l'IA lors de la génération du planning (étapes + ingrédients)."""

    nom: str = Field(..., min_length=1, max_length=200)
    temps_preparation: int = Field(20, ge=1, le=300)
    temps_cuisson: int = Field(20, ge=0, le=300)
    portions: int = Field(4, ge=1, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    ingredients: list[dict] = Field(default_factory=list)
    etapes: list[str] = Field(default_factory=list)

    @field_validator("temps_preparation", "temps_cuisson", "portions", mode="before")
    @classmethod
    def convert_float_to_int(cls, v):
        if isinstance(v, float):
            return int(v)
        return v


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
