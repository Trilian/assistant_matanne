"""
Schémas Pydantic pour les documents famille.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    titre: str = Field(..., min_length=1, max_length=200)
    categorie: str = "administratif"
    membre_famille: str | None = None
    fichier_url: str | None = None
    fichier_nom: str | None = None
    date_document: str | None = None
    date_expiration: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    rappel_expiration_jours: int = 30


class DocumentCreate(DocumentBase):
    """Création d'un document famille — hérite tous les champs de DocumentBase."""


class DocumentPatch(BaseModel):
    titre: str | None = Field(None, min_length=1, max_length=200)
    categorie: str | None = None
    membre_famille: str | None = None
    date_expiration: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class DocumentResponse(BaseModel):
    id: int
    titre: str
    categorie: str
    membre_famille: str | None = None
    fichier_url: str | None = None
    fichier_nom: str | None = None
    date_document: str | None = None
    date_expiration: str | None = None
    notes: str | None = None
    tags: list[str] = Field(default_factory=list)
    actif: bool = True
    est_expire: bool = False
    jours_avant_expiration: int | None = None
