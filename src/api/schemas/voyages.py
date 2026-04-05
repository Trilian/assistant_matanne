"""
Schémas Pydantic pour les voyages.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChecklistVoyageResume(BaseModel):
    """Résumé d'une checklist de voyage."""

    id: int
    nom: str
    membre: str = ""
    articles: list[str] = Field(default_factory=list)
    pourcentage_preparation: int | None = None


class VoyageResume(BaseModel):
    """Résumé d'un voyage dans la liste."""

    id: int
    titre: str
    destination: str = ""
    date_depart: str | None = None
    date_retour: str | None = None
    type_voyage: str = ""
    statut: str = ""


class VoyageDetailResponse(BaseModel):
    """Détail complet d'un voyage."""

    id: int
    titre: str
    destination: str = ""
    date_depart: str | None = None
    date_retour: str | None = None
    type_voyage: str = ""
    statut: str = ""
    budget_prevu: float | None = None
    budget_reel: float | None = None
    participants: list[str] = Field(default_factory=list)
    notes: str | None = None
    checklists: list[ChecklistVoyageResume] = Field(default_factory=list)


class VoyageCreateResponse(BaseModel):
    """Réponse de création de voyage."""

    id: int
    message: str = "Voyage créé"


class VoyageTemplateItem(BaseModel):
    """Template de voyage."""

    id: int
    nom: str
    type_voyage: str = ""
    membre: str = ""
    description: str = ""
    articles: list[str] = Field(default_factory=list)


class VoyagePlanifieIAResponse(BaseModel):
    """Réponse de planification IA d'un voyage."""

    message: str = "Voyage planifié"
    voyage_id: int
    destination: str = ""
    type_sejour: str = ""
    imported_templates: bool = False
    checklists: list[dict[str, Any]] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class VoyageGenererCoursesResponse(BaseModel):
    """Réponse de génération de courses depuis voyage."""

    message: str
    voyage_id: int
    articles_ajoutes: int = 0


class VoyageToggleChecklistResponse(BaseModel):
    """Réponse de cochage/décochage d'un article."""

    success: bool = True
    voyage_id: int
    checklist_id: int
