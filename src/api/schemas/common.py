"""
Schémas communs pour l'API REST.

Contient les schémas réutilisables dans plusieurs routes.
"""

import base64
import json
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


# ═══════════════════════════════════════════════════════════
# PAGINATION CURSEUR
# ═══════════════════════════════════════════════════════════


class CursorPaginationParams(BaseModel):
    """Paramètres de pagination par curseur."""

    cursor: str | None = Field(None, description="Curseur opaque pour la page suivante")
    limit: int = Field(20, ge=1, le=100, description="Nombre d'éléments par page")


class ReponseCurseur(BaseModel, Generic[T]):
    """Réponse paginée avec curseur."""

    items: list[T]
    next_cursor: str | None = Field(None, description="Curseur pour la page suivante")
    has_more: bool = Field(description="Indique s'il y a plus de résultats")


def encode_cursor(data: dict[str, Any]) -> str:
    """Encode un dictionnaire en curseur base64."""
    json_str = json.dumps(data, default=str)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_cursor(cursor: str) -> dict[str, Any]:
    """Décode un curseur base64 en dictionnaire."""
    try:
        json_str = base64.urlsafe_b64decode(cursor.encode()).decode()
        return json.loads(json_str)
    except Exception:
        return {}
