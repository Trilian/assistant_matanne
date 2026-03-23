"""
Schémas Pydantic pour les préférences utilisateur.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class PreferencesBase(BaseModel):
    """Champs communs pour les préférences."""

    nb_adultes: int = Field(2, ge=1, le=10)
    jules_present: bool = True
    jules_age_mois: int | None = None
    temps_semaine: int = Field(30, ge=5, le=180, description="Minutes de préparation max semaine")
    temps_weekend: int = Field(60, ge=5, le=300, description="Minutes de préparation max weekend")
    aliments_exclus: list[str] = Field(default_factory=list)
    aliments_favoris: list[str] = Field(default_factory=list)
    poisson_par_semaine: int = Field(2, ge=0, le=7)
    vegetarien_par_semaine: int = Field(1, ge=0, le=7)
    viande_rouge_max: int = Field(2, ge=0, le=7)
    robots: list[str] = Field(default_factory=list)
    magasins_preferes: list[str] = Field(default_factory=list)


class PreferencesCreate(PreferencesBase):
    """Création de préférences."""

    pass


class PreferencesPatch(BaseModel):
    """Mise à jour partielle des préférences."""

    nb_adultes: int | None = None
    jules_present: bool | None = None
    jules_age_mois: int | None = None
    temps_semaine: int | None = None
    temps_weekend: int | None = None
    aliments_exclus: list[str] | None = None
    aliments_favoris: list[str] | None = None
    poisson_par_semaine: int | None = None
    vegetarien_par_semaine: int | None = None
    viande_rouge_max: int | None = None
    robots: list[str] | None = None
    magasins_preferes: list[str] | None = None


class PreferencesResponse(PreferencesBase):
    """Réponse des préférences utilisateur."""

    user_id: str
