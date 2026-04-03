"""
CQS (Command/Query Separation) — Protocoles et classes de base.

Sépare explicitement les opérations de lecture (Query) des écritures (Command).
Les services existants (BaseService) continuent de fonctionner; ce module
fournit des protocoles typés et des classes Mixin pour migrer progressivement.

Architecture:
    - QueryService[T]: Lecture seule (get, list, count, search)
    - CommandService[T]: Écriture seule (create, update, delete) + émission événements
    - CRUDService[T]: Combine Query + Command (rétrocompatibilité)

Usage:
    from src.services.core.cqs import QueryService, CommandService

    class RecetteQueryService(QueryService[Recette]):
        model = Recette

    class RecetteCommandService(CommandService[Recette]):
        model = Recette
        event_prefix = "recette"

Règle: Les modules UI ne doivent appeler QUE des méthodes Query.
Les commandes passent par les services de commande avec ResultatAction.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.core.dto.base import PaginatedResult, ResultatAction

logger = logging.getLogger(__name__)
T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# PROTOCOLS (Contrats structuraux PEP 544)
# ═══════════════════════════════════════════════════════════


@runtime_checkable
class QueryProtocol(Protocol[T]):
    """Contrat pour les opérations de lecture."""

    def get_by_id(self, entity_id: int, db: Session | None = None) -> T | None: ...
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
        db: Session | None = None,
    ) -> list[T]: ...
    def count(self, filters: dict | None = None, db: Session | None = None) -> int: ...


@runtime_checkable
class CommandProtocol(Protocol[T]):
    """Contrat pour les opérations d'écriture."""

    def create(self, data: dict, db: Session | None = None) -> ResultatAction: ...
    def update(self, entity_id: int, data: dict, db: Session | None = None) -> ResultatAction: ...
    def delete(self, entity_id: int, db: Session | None = None) -> ResultatAction: ...


# ═══════════════════════════════════════════════════════════
# QUERY SERVICE — Lecture seule
# ═══════════════════════════════════════════════════════════


class QueryService(ABC, Generic[T]):
    """
    Service en lecture seule.

    Ne modifie JAMAIS la base de données. Toutes les méthodes sont safe
    pour être appelées depuis l'UI sans effet de bord.

    Sous-classes DOIVENT définir ``model``.
    """

    model: type[T]

    def __init__(self, cache_ttl: int = 60, **kwargs: Any):
        super().__init__(**kwargs)
        self.cache_ttl = cache_ttl
        self.model_name = self.model.__name__

    def get_by_id(self, entity_id: int, db: Session | None = None) -> T | None:
        """Récupère une entité par ID."""
        from src.core.caching import obtenir_cache

        def _execute(session: Session) -> T | None:
            cache_key = f"{self.model_name.lower()}_{entity_id}"
            cached = obtenir_cache().get(cache_key)
            if cached:
                return cached
            entity = session.get(self.model, entity_id)
            if entity:
                obtenir_cache().set(cache_key, entity, ttl=self.cache_ttl)
            return entity

        return self._with_session(_execute, db)

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
        order_by: str = "id",
        desc_order: bool = False,
        db: Session | None = None,
    ) -> list[T]:
        """Liste paginée avec filtres optionnels."""

        def _execute(session: Session) -> list[T]:
            query = session.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            if hasattr(self.model, order_by):
                order_col = getattr(self.model, order_by)
                query = query.order_by(desc(order_col) if desc_order else order_col)
            return query.offset(skip).limit(limit).all()

        return self._with_session(_execute, db)

    def get_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: dict | None = None,
        order_by: str = "id",
        desc_order: bool = False,
        db: Session | None = None,
    ) -> PaginatedResult:
        """Liste paginée avec résultat structuré."""
        skip = (page - 1) * page_size
        items = self.get_all(
            skip=skip,
            limit=page_size,
            filters=filters,
            order_by=order_by,
            desc_order=desc_order,
            db=db,
        )
        total = self.count(filters=filters, db=db)
        return PaginatedResult(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def count(self, filters: dict | None = None, db: Session | None = None) -> int:
        """Nombre d'entités."""

        def _execute(session: Session) -> int:
            query = session.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            return query.count()

        return self._with_session(_execute, db)

    # ───────────────────────────────────────────────────────
    # HELPERS
    # ───────────────────────────────────────────────────────

    def _with_session(self, func: Callable, db: Session | None = None) -> Any:
        """Exécute avec une session DB."""
        from src.core.db import obtenir_contexte_db

        if db:
            return func(db)
        with obtenir_contexte_db() as session:
            return func(session)

    def _apply_filters(self, query: Any, filters: dict) -> Any:
        """Applique des filtres génériques à une requête SQLAlchemy."""
        for field, value in filters.items():
            if not hasattr(self.model, field):
                continue
            column = getattr(self.model, field)
            if not isinstance(value, dict):
                query = query.filter(column == value)
            else:
                for op, val in value.items():
                    if op == "eq":
                        query = query.filter(column == val)
                    elif op == "ne":
                        query = query.filter(column != val)
                    elif op == "gt":
                        query = query.filter(column > val)
                    elif op == "lt":
                        query = query.filter(column < val)
                    elif op == "gte":
                        query = query.filter(column >= val)
                    elif op == "lte":
                        query = query.filter(column <= val)
                    elif op == "in":
                        query = query.filter(column.in_(val))
                    elif op == "like":
                        query = query.filter(column.ilike(f"%{val}%"))
        return query


# ═══════════════════════════════════════════════════════════
# COMMAND SERVICE — Écriture + événements
# ═══════════════════════════════════════════════════════════


class CommandService(ABC, Generic[T]):
    """
    Service d'écriture avec émission automatique d'événements.

    Toute opération de mutation retourne un ``ResultatAction``
    et émet un événement domaine via le bus.

    Sous-classes DOIVENT définir ``model`` et ``event_prefix``.
    """

    model: type[T]
    event_prefix: str = ""  # ex: "recette", "stock", "courses"

    def __init__(self, **kwargs: Any):
        super().__init__(**kwargs)
        self.model_name = self.model.__name__

    def create(self, data: dict, db: Session | None = None) -> ResultatAction:
        """Crée une entité et émet un événement."""

        def _execute(session: Session) -> ResultatAction:
            try:
                entity = self.model(**data)
                session.add(entity)
                session.commit()
                session.refresh(entity)
                logger.info(f"{self.model_name} créé: {entity.id}")
                self._invalider_cache()
                self._emettre(
                    "cree",
                    {"id": entity.id, **self._entity_event_data(entity)},
                )
                return ResultatAction.ok(
                    f"{self.model_name} créé",
                    id=entity.id,
                )
            except Exception as e:
                logger.error(f"Erreur création {self.model_name}: {e}")
                return ResultatAction.erreur(str(e))

        return self._with_session(_execute, db)

    def update(self, entity_id: int, data: dict, db: Session | None = None) -> ResultatAction:
        """Met à jour une entité et émet un événement."""

        def _execute(session: Session) -> ResultatAction:
            entity = session.get(self.model, entity_id)
            if not entity:
                return ResultatAction.erreur(f"{self.model_name} {entity_id} non trouvé")
            try:
                for key, value in data.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                session.commit()
                session.refresh(entity)
                logger.info(f"{self.model_name} {entity_id} mis à jour")
                self._invalider_cache()
                self._emettre(
                    "modifie",
                    {"id": entity_id, **self._entity_event_data(entity)},
                )
                return ResultatAction.ok(
                    f"{self.model_name} mis à jour",
                    id=entity_id,
                )
            except Exception as e:
                logger.error(f"Erreur MAJ {self.model_name} {entity_id}: {e}")
                return ResultatAction.erreur(str(e))

        return self._with_session(_execute, db)

    def delete(self, entity_id: int, db: Session | None = None) -> ResultatAction:
        """Supprime une entité et émet un événement."""

        def _execute(session: Session) -> ResultatAction:
            count = session.query(self.model).filter(self.model.id == entity_id).delete()
            session.commit()
            if count > 0:
                logger.info(f"{self.model_name} {entity_id} supprimé")
                self._invalider_cache()
                self._emettre("supprime", {"id": entity_id})
                return ResultatAction.ok(f"{self.model_name} supprimé", id=entity_id)
            return ResultatAction.erreur(f"{self.model_name} {entity_id} non trouvé")

        return self._with_session(_execute, db)

    # ───────────────────────────────────────────────────────
    # EVENT EMISSION
    # ───────────────────────────────────────────────────────

    def _emettre(self, action: str, data: dict | None = None) -> None:
        """Émet un événement domaine via le bus."""
        if not self.event_prefix:
            return
        try:
            from src.services.core.events import obtenir_bus

            event_type = f"{self.event_prefix}.{action}"
            obtenir_bus().emettre(
                event_type,
                data=data or {},
                source=self.model_name,
            )
        except Exception as e:
            logger.warning(f"Erreur émission événement {self.event_prefix}.{action}: {e}")

    def _entity_event_data(self, entity: Any) -> dict:
        """Extrait les données d'événement depuis une entité.

        Surcharger dans les sous-classes pour personnaliser.
        """
        data: dict[str, Any] = {}
        for attr in ("nom", "titre", "name"):
            if hasattr(entity, attr):
                data[attr] = getattr(entity, attr)
                break
        return data

    # ───────────────────────────────────────────────────────
    # HELPERS
    # ───────────────────────────────────────────────────────

    def _with_session(self, func: Callable, db: Session | None = None) -> Any:
        """Exécute avec une session DB."""
        from src.core.db import obtenir_contexte_db

        if db:
            return func(db)
        with obtenir_contexte_db() as session:
            return func(session)

    def _invalider_cache(self) -> None:
        """Invalide le cache associé à ce modèle."""
        from src.core.caching import obtenir_cache

        obtenir_cache().invalidate(pattern=self.model_name.lower())


# ═══════════════════════════════════════════════════════════
# CRUD SERVICE — Rétrocompatibilité Query + Command
# ═══════════════════════════════════════════════════════════


class CRUDService(QueryService[T], CommandService[T]):
    """
    Service CRUD complet combinant Query + Command.

    Usage pour migration progressive:
    1. Commencer avec CRUDService (remplace BaseService)
    2. Identifier les méthodes appelées par l'UI (→ Query)
    3. Séparer en QueryService + CommandService dédiés
    """

    def __init__(self, cache_ttl: int = 60, **kwargs: Any):
        super().__init__(cache_ttl=cache_ttl, **kwargs)


__all__ = [
    "QueryProtocol",
    "CommandProtocol",
    "QueryService",
    "CommandService",
    "CRUDService",
]
