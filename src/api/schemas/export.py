"""
Schémas Pydantic pour l'export PDF.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

TYPES_EXPORT_VALIDES = {"courses", "planning", "recette", "budget"}


class ExportPDFRequest(BaseModel):
    type_export: str = Field(pattern=r"^(courses|planning|recette|budget)$", max_length=20)
    id_ressource: int | None = None

    model_config = {
        "json_schema_extra": {"example": {"type_export": "planning", "id_ressource": 12}}
    }


class ExportPDFResponse(BaseModel):
    nom_fichier: str = Field(max_length=255)
    content_type: str = Field("application/pdf", max_length=50)

    model_config = {
        "json_schema_extra": {
            "example": {"nom_fichier": "planning-semaine-15.pdf", "content_type": "application/pdf"}
        }
    }
