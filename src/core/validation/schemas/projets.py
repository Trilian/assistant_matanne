"""Schémas de validation pour les projets."""

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator


class ProjetInput(BaseModel):
    """
    Input pour créer/modifier un projet.
    """

    nom: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=1000)
    categorie: str = Field(..., description="Catégorie du projet")
    priorite: str = Field(default="moyenne", description="Priorité")
    date_debut: date | None = Field(None)
    date_fin_estimee: date | None = Field(None, alias="date_fin")

    model_config = {"populate_by_name": True}

    @field_validator("nom")
    @classmethod
    def nettoyer_nom(cls, v: str) -> str:
        return v.strip().capitalize()

    @field_validator("priorite")
    @classmethod
    def valider_priorite(cls, v: str) -> str:
        """Valide la priorité"""
        priorites_valides = {"basse", "moyenne", "haute"}
        if v.lower() not in priorites_valides:
            raise ValueError(f"Priorité invalide. Doit être parmi: {', '.join(priorites_valides)}")
        return v.lower()

    @model_validator(mode="after")
    def valider_dates(self) -> "ProjetInput":
        """Valide que la date de fin est après la date de début"""
        if self.date_debut and self.date_fin_estimee and self.date_fin_estimee < self.date_debut:
            raise ValueError("La date de fin doit être après la date de début")
        return self
