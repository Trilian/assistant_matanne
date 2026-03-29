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


# ─────────────────────────────────────────────────────────
# Préférences canaux de notification (Sprint 13 — W4)
# ─────────────────────────────────────────────────────────

_CANAUX_VALIDES = {"push", "ntfy", "email", "whatsapp"}
_CATEGORIES_VALIDES = {"rappels", "alertes", "resumes"}


class CanauxParCategorie(BaseModel):
    """Canaux activés par catégorie de notification.

    Chaque clé est une catégorie et la valeur est la liste des canaux actifs.
    Canaux supportés : push, ntfy, email, whatsapp.
    Catégories : rappels, alertes, résumés.
    """

    rappels: list[str] = Field(
        default_factory=lambda: ["push", "ntfy"],
        description="Canaux pour les rappels (courses, entretien, médicaments…)",
    )
    alertes: list[str] = Field(
        default_factory=lambda: ["push", "ntfy", "email"],
        description="Canaux pour les alertes critiques (péremption, garantie…)",
    )
    resumes: list[str] = Field(
        default_factory=lambda: ["email"],
        description="Canaux pour les résumés hebdo/mensuel",
    )


class PreferencesNotificationsBase(BaseModel):
    """Champs communs pour les préférences de notification."""

    courses_rappel: bool = True
    repas_suggestion: bool = True
    stock_alerte: bool = True
    meteo_alerte: bool = True
    budget_alerte: bool = True
    canal_prefere: str = Field("push", description="Canal par défaut (push|ntfy|email|whatsapp)")
    canaux_par_categorie: CanauxParCategorie = Field(default_factory=CanauxParCategorie)
    quiet_hours_start: str = Field("22:00", description="Heure début silence (HH:MM)")
    quiet_hours_end: str = Field("07:00", description="Heure fin silence (HH:MM)")


class PreferencesNotificationsUpdate(BaseModel):
    """Mise à jour (complète ou partielle) des préférences de notification."""

    courses_rappel: bool | None = None
    repas_suggestion: bool | None = None
    stock_alerte: bool | None = None
    meteo_alerte: bool | None = None
    budget_alerte: bool | None = None
    canal_prefere: str | None = None
    canaux_par_categorie: CanauxParCategorie | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None


class PreferencesNotificationsResponse(PreferencesNotificationsBase):
    """Réponse des préférences de notification."""

    user_id: str | None = None
