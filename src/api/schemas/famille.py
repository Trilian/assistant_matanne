"""
Schémas Pydantic pour la famille (anniversaires, événements familiaux).
"""

from __future__ import annotations

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# ANNIVERSAIRES
# ═══════════════════════════════════════════════════════════


class AnniversaireBase(BaseModel):
    nom_personne: str = Field(..., min_length=1, max_length=200)
    date_naissance: str = Field(..., description="Date au format YYYY-MM-DD")
    relation: str = Field(
        ..., description="parent, enfant, grand_parent, oncle_tante, cousin, ami, collegue"
    )
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = None
    notes: str | None = None


class AnniversaireCreate(AnniversaireBase):
    pass


class AnniversairePatch(BaseModel):
    nom_personne: str | None = Field(None, min_length=1, max_length=200)
    date_naissance: str | None = None
    relation: str | None = None
    rappel_jours_avant: list[int] | None = None
    idees_cadeaux: str | None = None
    notes: str | None = None
    actif: bool | None = None


class AnniversaireResponse(BaseModel):
    id: int
    nom_personne: str
    date_naissance: str
    relation: str
    rappel_jours_avant: list[int] = Field(default=[7, 1, 0])
    idees_cadeaux: str | None = None
    historique_cadeaux: list[dict] | None = None
    notes: str | None = None
    actif: bool = True
    age: int | None = None
    jours_restants: int | None = None
    cree_le: str | None = None


# ═══════════════════════════════════════════════════════════
# ÉVÉNEMENTS FAMILIAUX
# ═══════════════════════════════════════════════════════════


class EvenementFamilialBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    date_evenement: str = Field(..., description="Date au format YYYY-MM-DD")
    type_evenement: str = Field(
        ..., description="anniversaire, fete, vacances, rentree, tradition"
    )
    recurrence: str = Field(default="unique", description="annuelle, mensuelle, unique")
    rappel_jours_avant: int = 7
    notes: str | None = None
    participants: list[str] | None = None


class EvenementFamilialCreate(EvenementFamilialBase):
    pass


class EvenementFamilialPatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    date_evenement: str | None = None
    type_evenement: str | None = None
    recurrence: str | None = None
    rappel_jours_avant: int | None = None
    notes: str | None = None
    participants: list[str] | None = None
    actif: bool | None = None


class EvenementFamilialResponse(BaseModel):
    id: int
    titre: str
    date_evenement: str
    type_evenement: str
    recurrence: str = "unique"
    rappel_jours_avant: int = 7
    notes: str | None = None
    participants: list[str] | None = None
    actif: bool = True
    cree_le: str | None = None
