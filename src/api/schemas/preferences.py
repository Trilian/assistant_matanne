"""
Schémas Pydantic pour les préférences utilisateur.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


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
    """Création de préférences — hérite tous les champs de PreferencesBase."""


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
# Préférences canaux de notification (W4)
# ─────────────────────────────────────────────────────────

_CANAUX_VALIDES = {"push", "ntfy", "email", "telegram"}
_CATEGORIES_VALIDES = {"rappels", "alertes", "resumes"}


class CanauxParCategorie(BaseModel):
    """Canaux activés par catégorie de notification.

    Chaque clé est une catégorie et la valeur est la liste des canaux actifs.
    Canaux supportés : push, ntfy, email, telegram.
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

    @field_validator("rappels", "alertes", "resumes")
    @classmethod
    def valider_canaux(cls, value: list[str]) -> list[str]:
        propres: list[str] = []
        for canal in value or []:
            if canal in _CANAUX_VALIDES and canal not in propres:
                propres.append(canal)
        if not propres:
            raise ValueError("Au moins un canal valide est requis")
        return propres


class PreferencesNotificationsBase(BaseModel):
    """Champs communs pour les préférences de notification."""

    courses_rappel: bool = True
    repas_suggestion: bool = True
    stock_alerte: bool = True
    meteo_alerte: bool = True
    budget_alerte: bool = True
    canal_prefere: str = Field("push", description="Canal par défaut (push|ntfy|email|telegram)")
    canaux_par_categorie: CanauxParCategorie = Field(default_factory=CanauxParCategorie)
    notifications_par_module: dict[str, bool] = Field(
        default_factory=lambda: {
            "cuisine": True,
            "famille": True,
            "maison": True,
            "planning": True,
            "jeux": True,
        },
        description="Activer ou non les notifications par module",
    )
    quiet_hours_start: str = Field("22:00", description="Heure début silence (HH:MM)")
    quiet_hours_end: str = Field("07:00", description="Heure fin silence (HH:MM)")
    max_par_heure: int = Field(5, ge=1, le=50, description="Limite d'envoi par heure")
    mode_digest: bool = Field(False, description="Activer la consolidation en digest")
    mode_vacances: bool = Field(False, description="Pause les notifications non essentielles")
    checklist_voyage_auto: bool = Field(
        True,
        description="Active la checklist voyage automatique quand le mode vacances est activé",
    )

    @field_validator("canal_prefere")
    @classmethod
    def valider_canal_prefere(cls, value: str) -> str:
        if value not in _CANAUX_VALIDES:
            raise ValueError("canal_prefere invalide")
        return value

    @field_validator("quiet_hours_start", "quiet_hours_end")
    @classmethod
    def valider_heure(cls, value: str) -> str:
        txt = str(value)
        if len(txt) != 5 or txt[2] != ":":
            raise ValueError("Format attendu HH:MM")
        heures, minutes = txt.split(":", 1)
        if not (heures.isdigit() and minutes.isdigit()):
            raise ValueError("Format attendu HH:MM")
        h = int(heures)
        m = int(minutes)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Heure invalide")
        return f"{h:02d}:{m:02d}"


class PreferencesNotificationsUpdate(BaseModel):
    """Mise à jour (complète ou partielle) des préférences de notification."""

    courses_rappel: bool | None = None
    repas_suggestion: bool | None = None
    stock_alerte: bool | None = None
    meteo_alerte: bool | None = None
    budget_alerte: bool | None = None
    canal_prefere: str | None = None
    canaux_par_categorie: CanauxParCategorie | None = None
    notifications_par_module: dict[str, bool] | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    max_par_heure: int | None = Field(default=None, ge=1, le=50)
    mode_digest: bool | None = None
    mode_vacances: bool | None = None
    checklist_voyage_auto: bool | None = None

    @field_validator("canal_prefere")
    @classmethod
    def valider_canal_prefere(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if value not in _CANAUX_VALIDES:
            raise ValueError("canal_prefere invalide")
        return value

    @field_validator("quiet_hours_start", "quiet_hours_end")
    @classmethod
    def valider_heure(cls, value: str | None) -> str | None:
        if value is None:
            return value
        txt = str(value)
        if len(txt) != 5 or txt[2] != ":":
            raise ValueError("Format attendu HH:MM")
        heures, minutes = txt.split(":", 1)
        if not (heures.isdigit() and minutes.isdigit()):
            raise ValueError("Format attendu HH:MM")
        h = int(heures)
        m = int(minutes)
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Heure invalide")
        return f"{h:02d}:{m:02d}"


class PreferencesNotificationsResponse(PreferencesNotificationsBase):
    """Réponse des préférences de notification."""

    user_id: str | None = None
