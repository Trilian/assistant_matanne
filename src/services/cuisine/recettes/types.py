"""
Types et schémas Pydantic pour le package recettes.

Module unifié avec tous les modèles de données pour les services de recettes.
Inclut les schémas de validation pour la génération IA.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator


class RecetteSuggestion(BaseModel):
    """Recette suggérée par l'IA."""

    # Convertir automatiquement les floats en entiers (Mistral peut retourner 20.0)
    model_config = ConfigDict(coerce_numbers_to_str=False)

    nom: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    temps_preparation: int = Field(..., gt=0, le=300)
    temps_cuisson: int = Field(..., ge=0, le=300)
    portions: int = Field(4, gt=0, le=20)
    difficulte: str = Field("moyen", pattern="^(facile|moyen|difficile)$")
    type_repas: str
    saison: str = "toute_année"
    ingredients: list[dict]
    etapes: list[dict]

    @field_validator("temps_preparation", "temps_cuisson", "portions", mode="before")
    @classmethod
    def convert_float_to_int(cls, v):
        """Convertit les floats en entiers (Mistral peut retourner des floats)."""
        if isinstance(v, float):
            return int(v)
        return v


class VersionBebeGeneree(BaseModel):
    """Version bébé générée par l'IA."""

    instructions_modifiees: str
    notes_bebe: str
    age_minimum_mois: int = Field(6, ge=6, le=36)

    @field_validator("age_minimum_mois", mode="before")
    @classmethod
    def convert_float_to_int_age(cls, v):
        """Convertit les floats en entiers."""
        if isinstance(v, float):
            return int(v)
        return v


class VersionBatchCookingGeneree(BaseModel):
    """Version batch cooking générée par l'IA."""

    instructions_modifiees: str
    nombre_portions_recommande: int = Field(12, ge=4, le=100)
    temps_preparation_total_heures: float = Field(2.0, ge=0.5, le=12)
    conseils_conservation: str
    conseils_congelation: str
    calendrier_preparation: str

    @field_validator("nombre_portions_recommande", mode="before")
    @classmethod
    def convert_float_to_int_portions(cls, v):
        """Convertit les floats en entiers."""
        if isinstance(v, float):
            return int(v)
        return v


class VersionRobotGeneree(BaseModel):
    """Version adaptée pour robot de cuisine générée par l'IA."""

    instructions_modifiees: str
    reglages_robot: str
    temps_cuisson_adapte_minutes: int = Field(30, ge=5, le=300)
    conseils_preparation: str
    etapes_specifiques: list[str] = Field(default_factory=list)

    @field_validator("temps_cuisson_adapte_minutes", mode="before")
    @classmethod
    def convert_float_to_int_temps(cls, v):
        """Convertit les floats en entiers."""
        if isinstance(v, float):
            return int(v)
        return v


# ═══════════════════════════════════════════════════════════
# ALIASES ANGLAIS (pour compatibilité)
# ═══════════════════════════════════════════════════════════

RecipeSuggestion = RecetteSuggestion
BabyVersionGenerated = VersionBebeGeneree
BatchCookingVersionGenerated = VersionBatchCookingGeneree
RobotVersionGenerated = VersionRobotGeneree


__all__ = [
    # Types français
    "RecetteSuggestion",
    "VersionBebeGeneree",
    "VersionBatchCookingGeneree",
    "VersionRobotGeneree",
    # Aliases anglais
    "RecipeSuggestion",
    "BabyVersionGenerated",
    "BatchCookingVersionGenerated",
    "RobotVersionGenerated",
]
