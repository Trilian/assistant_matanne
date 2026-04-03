"""
DTOs de base — Types fondamentaux réutilisables.

Tous les DTOs héritent de ``BaseDTO`` qui configure la conversion
depuis les attributs ORM (``from_attributes=True``).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# BASE DTO
# ═══════════════════════════════════════════════════════════


class BaseDTO(BaseModel):
    """DTO de base avec config ORM-compatible.

    ``from_attributes=True`` permet:
        dto = MonDTO.model_validate(orm_instance)
    """

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True,  # Immuable par défaut
    )


class TimestampedDTO(BaseDTO):
    """DTO avec timestamps de création/modification."""

    created_at: datetime | None = None
    updated_at: datetime | None = None


class IdentifiedDTO(TimestampedDTO):
    """DTO avec ID + timestamps."""

    id: int


# ═══════════════════════════════════════════════════════════
# RÉSULTATS GÉNÉRIQUES
# ═══════════════════════════════════════════════════════════


class ResultatAction(BaseDTO):
    """Résultat d'une action (commande) retourné par les services.

    Usage:
        return ResultatAction(succes=True, message="Recette créée", id=42)
    """

    model_config = ConfigDict(frozen=False)

    succes: bool = True
    message: str = ""
    id: int | None = None
    donnees: dict[str, Any] | None = None

    @classmethod
    def ok(cls, message: str = "", **kwargs: Any) -> ResultatAction:
        """Crée un résultat de succès."""
        return cls(succes=True, message=message, **kwargs)

    @classmethod
    def erreur(cls, message: str, **kwargs: Any) -> ResultatAction:
        """Crée un résultat d'erreur."""
        return cls(succes=False, message=message, **kwargs)


class PaginatedResult(BaseDTO, Generic[T]):
    """Résultat paginé générique.

    Usage:
        return PaginatedResult(
            items=recettes_dto,
            total=total_count,
            page=1,
            page_size=20,
        )
    """

    model_config = ConfigDict(frozen=False, arbitrary_types_allowed=True)

    items: list[Any] = []
    total: int = 0
    page: int = 1
    page_size: int = 20

    @property
    def has_next(self) -> bool:
        """Vérifie s'il y a une page suivante."""
        return (self.page * self.page_size) < self.total

    @property
    def total_pages(self) -> int:
        """Nombre total de pages."""
        if self.page_size <= 0:
            return 0
        return (self.total + self.page_size - 1) // self.page_size


__all__ = [
    "BaseDTO",
    "TimestampedDTO",
    "IdentifiedDTO",
    "ResultatAction",
    "PaginatedResult",
]
