"""
Queries — Opérations de lecture (cachables, idempotentes).

Les queries:
- Sont immutables (frozen dataclass)
- Ne modifient jamais l'état
- Peuvent être cachées automatiquement
- Retournent un Result[T, ErrorInfo]

Example:
    @dataclass(frozen=True, slots=True)
    class RecetteParIdQuery(Query[Recette | None]):
        recette_id: int

        def execute(self) -> Result[Recette | None, ErrorInfo]:
            with obtenir_contexte_db() as db:
                recette = db.get(Recette, self.recette_id)
                return Success(recette)

    # Usage
    query = RecetteParIdQuery(recette_id=42)
    result = query.execute()  # ou via dispatcher pour cache auto
"""

from __future__ import annotations

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, fields
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from src.core.result import ErrorInfo, Result

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type du résultat de la query


# ═══════════════════════════════════════════════════════════
# QUERY PROTOCOL
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class QueryProtocol(Protocol[T]):
    """Protocol pour les queries (PEP 544 structural subtyping)."""

    def execute(self) -> Result[T, ErrorInfo]: ...

    def cache_key(self) -> str: ...


# ═══════════════════════════════════════════════════════════
# QUERY BASE CLASS
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True)
class Query(ABC, Generic[T]):
    """
    Query de base — Lecture seule, immutable, cachable.

    Attributes:
        Définis par les sous-classes comme champs dataclass.

    Methods:
        execute: Exécute la query. Ne modifie jamais l'état.
        cache_key: Génère une clé de cache unique.
    """

    @abstractmethod
    def execute(self) -> Result[T, ErrorInfo]:
        """
        Exécute la query. Ne doit JAMAIS modifier l'état.

        Returns:
            Result[T, ErrorInfo]: Succès avec la valeur ou Failure avec erreur.
        """
        ...

    def cache_key(self) -> str:
        """
        Génère une clé de cache basée sur le type et les attributs.

        La clé est déterministe: mêmes paramètres = même clé.

        Returns:
            str: Clé de cache MD5 tronquée (16 caractères).
        """
        # Récupérer tous les champs de la dataclass
        try:
            field_values = {f.name: getattr(self, f.name) for f in fields(self)}
        except TypeError:
            # Pas une dataclass, utiliser __dict__
            field_values = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}

        # Construire la clé
        class_name = self.__class__.__name__
        attrs_str = str(sorted(field_values.items()))
        raw_key = f"{class_name}|{attrs_str}"

        return hashlib.md5(raw_key.encode()).hexdigest()[:16]

    def __str__(self) -> str:
        """Représentation lisible de la query."""
        try:
            field_values = {f.name: getattr(self, f.name) for f in fields(self)}
        except TypeError:
            field_values = {}
        return f"{self.__class__.__name__}({field_values})"


# ═══════════════════════════════════════════════════════════
# QUERY HANDLER
# ═══════════════════════════════════════════════════════════


@dataclass
class QueryHandler(ABC, Generic[T]):
    """
    Handler de query avec injection de dépendances.

    Utile pour les queries complexes nécessitant des services externes.
    Pour les queries simples, implémenter directement execute() suffit.

    Example:
        class RecettesQueryHandler(QueryHandler[list[Recette]]):
            def __init__(self, db_session: Session):
                self.db = db_session

            def handle(self, query: RecherchRecettesQuery) -> Result[list[Recette], ErrorInfo]:
                recettes = self.db.query(Recette).filter(...).all()
                return Success(recettes)
    """

    @abstractmethod
    def handle(self, query: Query[T]) -> Result[T, ErrorInfo]:
        """
        Traite la query.

        Args:
            query: La query à traiter.

        Returns:
            Result[T, ErrorInfo]: Résultat de la query.
        """
        ...


# ═══════════════════════════════════════════════════════════
# QUERIES UTILITAIRES
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class PaginationParams:
    """Paramètres de pagination réutilisables."""

    offset: int = 0
    limit: int = 50
    order_by: str = "id"
    desc_order: bool = False

    def __post_init__(self):
        """Validation des paramètres."""
        if self.offset < 0:
            object.__setattr__(self, "offset", 0)
        if self.limit < 1:
            object.__setattr__(self, "limit", 50)
        if self.limit > 1000:
            object.__setattr__(self, "limit", 1000)


@dataclass(frozen=True, slots=True)
class SearchParams:
    """Paramètres de recherche réutilisables."""

    terme: str | None = None
    champs: tuple[str, ...] = ()

    @property
    def has_search(self) -> bool:
        return bool(self.terme and self.champs)


# ═══════════════════════════════════════════════════════════
# QUERY RESULT HELPERS
# ═══════════════════════════════════════════════════════════


def paginated_result(items: list[T], total: int, pagination: PaginationParams) -> dict[str, Any]:
    """
    Encapsule un résultat paginé.

    Args:
        items: Liste des éléments de la page courante.
        total: Nombre total d'éléments (toutes pages confondues).
        pagination: Paramètres de pagination utilisés.

    Returns:
        Dict avec items, total, has_more, page_info.
    """
    return {
        "items": items,
        "total": total,
        "count": len(items),
        "has_more": (pagination.offset + len(items)) < total,
        "page_info": {
            "offset": pagination.offset,
            "limit": pagination.limit,
            "order_by": pagination.order_by,
            "desc": pagination.desc_order,
        },
    }
