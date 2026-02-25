"""
Schémas Pydantic pour les courses.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .base import NomValidatorMixin, QuantiteValidatorMixin


class CourseItemBase(BaseModel, NomValidatorMixin, QuantiteValidatorMixin):
    """Schéma pour un article de liste de courses."""

    nom: str
    quantite: float = 1.0
    unite: str | None = None
    categorie: str | None = None
    coche: bool = False


class CourseListCreate(BaseModel, NomValidatorMixin):
    """Schéma pour créer une liste de courses."""

    nom: str = Field("Liste de courses", min_length=1)


class ListeCoursesResume(BaseModel):
    """Résumé d'une liste de courses (pour la liste paginée)."""

    id: int
    nom: str
    items_count: int = 0
    created_at: datetime | None = None


class ArticleResponse(BaseModel):
    """Réponse pour un article de liste."""

    id: int
    nom: str
    quantite: float
    coche: bool = False
    categorie: str | None = None


class ListeCoursesResponse(BaseModel):
    """Réponse complète pour une liste de courses."""

    id: int
    nom: str
    archivee: bool = False
    created_at: datetime | None = None
    items: list[ArticleResponse] = Field(default_factory=list)
