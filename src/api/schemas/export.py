"""
Schémas Pydantic pour l'export PDF.
"""

from __future__ import annotations

from pydantic import BaseModel


TYPES_EXPORT_VALIDES = {"courses", "planning", "recette", "budget"}


class ExportPDFRequest(BaseModel):
    type_export: str
    id_ressource: int | None = None


class ExportPDFResponse(BaseModel):
    nom_fichier: str
    content_type: str = "application/pdf"
