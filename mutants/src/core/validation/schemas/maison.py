"""Schémas de validation pour le module maison."""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class DepenseMaisonInput(BaseModel):
    """
    Validation d'une dépense maison.

    Attributes:
        categorie: Catégorie de dépense (gaz, eau, electricite, loyer, etc.)
        mois: Mois (1-12)
        annee: Année
        montant: Montant de la dépense
        consommation: Consommation énergie (optionnel)
        unite_consommation: Unité de consommation (kWh, m³, L)
        fournisseur: Nom du fournisseur
        numero_contrat: Numéro de contrat
        notes: Notes libres
    """

    categorie: str = Field(..., min_length=1, max_length=50)
    mois: int = Field(..., ge=1, le=12)
    annee: int = Field(..., ge=2020, le=2100)
    montant: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    consommation: float | None = Field(None, ge=0)
    unite_consommation: str | None = Field(None, max_length=20)
    fournisseur: str | None = Field(None, max_length=200)
    numero_contrat: str | None = Field(None, max_length=100)
    notes: str | None = Field(None, max_length=2000)

    @field_validator("categorie")
    @classmethod
    def valider_categorie(cls, v: str) -> str:
        """Normalise la catégorie."""
        return v.strip().lower()

    @field_validator("fournisseur")
    @classmethod
    def nettoyer_fournisseur(cls, v: str | None) -> str | None:
        if v:
            return v.strip()
        return None
