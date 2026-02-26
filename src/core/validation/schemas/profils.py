"""Schémas de validation pour les profils utilisateurs et la configuration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator


class SchemaPIN(BaseModel):
    """Validation d'un code PIN (4-6 chiffres)."""

    pin: str = Field(..., min_length=4, max_length=6)

    @field_validator("pin")
    @classmethod
    def valider_pin(cls, v: str) -> str:
        """Le PIN doit contenir uniquement des chiffres."""
        if not v.isdigit():
            msg = "Le PIN doit contenir uniquement des chiffres"
            raise ValueError(msg)
        return v


class SchemaProfilEdition(BaseModel):
    """Validation des données d'édition d'un profil utilisateur."""

    display_name: str = Field(..., min_length=1, max_length=100)
    email: str | None = Field(None, max_length=200)
    avatar_emoji: str = Field(default="👤", max_length=10)
    taille_cm: int | None = Field(None, ge=100, le=250)
    poids_kg: float | None = Field(None, ge=30.0, le=200.0)
    objectif_poids_kg: float | None = Field(None, ge=30.0, le=200.0)
    objectif_pas_quotidien: int = Field(default=10000, ge=1000, le=50000)
    objectif_calories_brulees: int = Field(default=500, ge=100, le=3000)
    objectif_minutes_actives: int = Field(default=30, ge=10, le=300)
    theme_prefere: str = Field(default="auto", max_length=20)

    @field_validator("email")
    @classmethod
    def valider_email(cls, v: str | None) -> str | None:
        """Validation basique du format email."""
        if v is not None and v.strip():
            if "@" not in v or "." not in v:
                msg = "Format email invalide"
                raise ValueError(msg)
            return v.strip().lower()
        return None

    @field_validator("display_name")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        """Nettoie le nom affiché."""
        return v.strip()


class SchemaPreferencesModule(BaseModel):
    """Validation de la structure JSON des préférences par module."""

    cuisine: dict[str, Any] = Field(default_factory=dict)
    famille: dict[str, Any] = Field(default_factory=dict)
    maison: dict[str, Any] = Field(default_factory=dict)
    planning: dict[str, Any] = Field(default_factory=dict)
    budget: dict[str, Any] = Field(default_factory=dict)

    @field_validator("cuisine")
    @classmethod
    def valider_cuisine(cls, v: dict) -> dict:
        """Valide les préférences cuisine."""
        if "nb_suggestions_ia" in v:
            nb = v["nb_suggestions_ia"]
            if not isinstance(nb, int) or nb < 1 or nb > 20:
                msg = "nb_suggestions_ia doit être entre 1 et 20"
                raise ValueError(msg)
        if "duree_max_batch_min" in v:
            duree = v["duree_max_batch_min"]
            if not isinstance(duree, int) or duree < 30 or duree > 300:
                msg = "duree_max_batch_min doit être entre 30 et 300"
                raise ValueError(msg)
        return v

    @field_validator("budget")
    @classmethod
    def valider_budget(cls, v: dict) -> dict:
        """Valide les préférences budget."""
        if "seuils_alerte_pct" in v:
            seuil = v["seuils_alerte_pct"]
            if not isinstance(seuil, int) or seuil < 50 or seuil > 100:
                msg = "seuils_alerte_pct doit être entre 50 et 100"
                raise ValueError(msg)
        return v


class SchemaImportConfiguration(BaseModel):
    """Validation du fichier JSON d'import de configuration."""

    version: str = Field(..., min_length=1, max_length=10)
    timestamp: str | None = None
    profil: dict[str, Any] = Field(default_factory=dict)
    sante: dict[str, Any] = Field(default_factory=dict)
    notifications: dict[str, Any] = Field(default_factory=dict)

    @field_validator("version")
    @classmethod
    def valider_version(cls, v: str) -> str:
        """Seules les versions connues sont acceptées."""
        versions_acceptees = {"1.0"}
        if v not in versions_acceptees:
            msg = f"Version non supportée: {v}. Versions acceptées: {versions_acceptees}"
            raise ValueError(msg)
        return v

    @field_validator("profil")
    @classmethod
    def valider_profil(cls, v: dict) -> dict:
        """Le profil doit contenir au minimum un username."""
        if v and "username" not in v:
            msg = "Le champ 'username' est requis dans le profil"
            raise ValueError(msg)
        return v
