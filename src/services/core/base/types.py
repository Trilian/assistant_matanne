"""
Service Types - Types et classes de base partagés.
Point d'entrée sans dépendances circulaires.

``BaseService`` compose deux mixins (advanced, pipeline) pour garder
chaque fichier à taille raisonnable tout en conservant la même API publique.
"""

import logging
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from sqlalchemy import desc
from sqlalchemy.orm import Session

from .advanced import AdvancedQueryMixin
from .pipeline import PipelineMixin

logger = logging.getLogger(__name__)
T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# BASE SERVICE (Sans dépendances UI)
# ═══════════════════════════════════════════════════════════


class BaseService(PipelineMixin, AdvancedQueryMixin, Generic[T]):
    """
    Service CRUD Universel avec toutes les fonctionnalités.

    Inclut:
    - CRUD complet avec cache automatique
    - Bulk operations avec stratégies de fusion (``AdvancedQueryMixin``)
    - Statistiques génériques (``AdvancedQueryMixin``)
    - Recherche avancée multi-critères (``AdvancedQueryMixin``)
    - Pipeline middleware optionnel (``PipelineMixin``)

    ⚠️ ATTENTION : Ce fichier ne doit JAMAIS importer depuis src.ui

    Note:
        Utilise le MRO coopératif avec **kwargs pour permettre
        l'héritage multiple avec BaseAIService.
    """

    def __init__(self, model: type[T], cache_ttl: int = 60, **kwargs: Any):
        # MRO coopératif: passer les kwargs restants aux classes parentes
        super().__init__(**kwargs)
        self.model = model
        self.model_name = model.__name__
        self.cache_ttl = cache_ttl

    # ════════════════════════════════════════════════════════════
    # CRUD DE BASE
    # ════════════════════════════════════════════════════════════

    def create(self, data: dict, db: Session | None = None) -> T:
        """Crée une entité"""

        def _execute(session: Session) -> T:
            entity = self.model(**data)
            session.add(entity)
            session.commit()
            session.refresh(entity)
            logger.info(f"{self.model_name} créé: {entity.id}")
            self._invalider_cache()
            return entity

        return self._with_session(_execute, db)

    def get_by_id(self, entity_id: int, db: Session | None = None) -> T | None:
        """Récupère par ID avec cache"""
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
        """Liste avec filtres et tri"""

        def _execute(session: Session) -> list[T]:
            query = session.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            if hasattr(self.model, order_by):
                order_col = getattr(self.model, order_by)
                query = query.order_by(desc(order_col) if desc_order else order_col)
            return query.offset(skip).limit(limit).all()

        return self._with_session(_execute, db)

    def update(self, entity_id: int, data: dict, db: Session | None = None) -> T | None:
        """Met à jour une entité"""
        from src.core.exceptions import ErreurNonTrouve

        def _execute(session: Session) -> T | None:
            entity = session.get(self.model, entity_id)
            if not entity:
                raise ErreurNonTrouve(f"{self.model_name} {entity_id} non trouvé")
            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            session.commit()
            session.refresh(entity)
            logger.info(f"{self.model_name} {entity_id} mis à jour")
            self._invalider_cache()
            return entity

        return self._with_session(_execute, db)

    def delete(self, entity_id: int, db: Session | None = None) -> bool:
        """Supprime une entité"""

        def _execute(session: Session) -> bool:
            count = session.query(self.model).filter(self.model.id == entity_id).delete()
            session.commit()
            if count > 0:
                logger.info(f"{self.model_name} {entity_id} supprimé")
                self._invalider_cache()
                return True
            return False

        return self._with_session(_execute, db)

    def count(self, filters: dict | None = None, db: Session | None = None) -> int:
        """Compte les entités"""

        def _execute(session: Session) -> int:
            query = session.query(self.model)
            if filters:
                query = self._apply_filters(query, filters)
            return query.count()

        return self._with_session(_execute, db)

    # ════════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ════════════════════════════════════════════════════════════

    def _with_session(self, func: Callable, db: Session | None = None) -> Any:
        """Exécute une fonction avec une session DB.

        Si une session est fournie, l'utilise directement.
        Sinon, crée une nouvelle session via le context manager.
        """
        from src.core.db import obtenir_contexte_db

        if db:
            return func(db)
        with obtenir_contexte_db() as session:
            return func(session)

    def _apply_filters(self, query, filters: dict):
        """Applique des filtres génériques à une requête SQLAlchemy.

        Supporte les opérateurs: eq, ne, gt, lt, gte, lte, in, like.
        """
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
                    else:
                        import logging as _log

                        _log.getLogger(__name__).warning(
                            "Opérateur de filtre inconnu '%s' pour '%s'", op, field
                        )
        return query

    def _model_to_dict(self, obj: Any) -> dict:
        """Convertit un objet modèle SQLAlchemy en dictionnaire."""
        from src.services.core.backup.utils_serialization import model_to_dict

        return model_to_dict(obj)

    def _invalider_cache(self):
        """Invalide le cache associé à ce modèle."""
        from src.core.caching import obtenir_cache

        obtenir_cache().invalidate(pattern=self.model_name.lower())


__all__ = ["BaseService", "T"]
