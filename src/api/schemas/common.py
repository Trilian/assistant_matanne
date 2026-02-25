"""
Schémas communs pour l'API REST.

Contient les schémas réutilisables dans plusieurs routes.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


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
