"""
Schémas communs pour l'API REST.

Contient les schémas réutilisables dans plusieurs routes.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Paramètres de pagination standard."""

    page: int = Field(1, ge=1, description="Numéro de page")
    page_size: int = Field(20, ge=1, le=100, description="Taille de page")


class ReponsePaginee(BaseModel, Generic[T]):
    """Réponse paginée générique."""

    items: list[T]
    total: int = Field(description="Nombre total d'éléments")
    page: int = Field(description="Page actuelle")
    page_size: int = Field(description="Taille de page")
    pages: int = Field(description="Nombre total de pages")


class MessageResponse(BaseModel):
    """Réponse avec message simple."""

    message: str
    id: int | None = None
    details: dict[str, Any] | None = None


class ErreurResponse(BaseModel):
    """Réponse d'erreur standard."""

    detail: str
    code: str | None = None
    errors: list[dict[str, Any]] | None = None
