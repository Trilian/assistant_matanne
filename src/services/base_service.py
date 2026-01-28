"""
Service CRUD Universel - Version Finale Optimisée
Fusionne base_service.py + base_service_optimized.py + enhanced_service.py + service_mixins.py
"""

import logging
from datetime import datetime
from typing import Any, Generic, TypeVar, Callable

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

from src.core.cache import Cache
from src.core.database import obtenir_contexte_db
from src.core.errors_base import ErreurNonTrouve
from src.core.errors import gerer_erreurs
from src.core.decorators import with_db_session

logger = logging.getLogger(__name__)
T = TypeVar("T")


class BaseService(Generic[T]):
    """
    Service CRUD Universel avec toutes les fonctionnalités

    Inclut:
    - CRUD complet avec cache automatique
    - Bulk operations avec stratégies de fusion
    - Statistiques génériques
    - Recherche avancée multi-critères
    - Mixins intégrés (Status, SoftDelete, etc.)
    """

    def __init__(self, model: type[T], cache_ttl: int = 60):
        self.model = model
        self.model_name = model.__name__
        self.cache_ttl = cache_ttl

    # ════════════════════════════════════════════════════════════
    # CRUD DE BASE
    # ════════════════════════════════════════════════════════════

    @with_db_session
    def create(self, data: dict, db: Session) -> T:
        """Crée une entité"""
        entity = self.model(**data)
        db.add(entity)
        db.commit()
        db.refresh(entity)
        logger.info(f"{self.model_name} créé: {entity.id}")
        self._invalider_cache()
        return entity

    @with_db_session
    def get_by_id(self, entity_id: int, db: Session) -> T | None:
        """Récupère par ID avec cache"""
        cache_key = f"{self.model_name.lower()}_{entity_id}"
        cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
        if cached:
            return cached

        entity = db.query(self.model).get(entity_id)
        if entity:
            Cache.definir(cache_key, entity, ttl=self.cache_ttl)
        return entity

    @with_db_session
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
        query = db.query(self.model)
        if filters:
            query = self._apply_filters(query, filters)
        if hasattr(self.model, order_by):
            order_col = getattr(self.model, order_by)
            query = query.order_by(desc(order_col) if desc_order else order_col)
        return query.offset(skip).limit(limit).all()

    @with_db_session
    def update(self, entity_id: int, data: dict, db: Session | None = None) -> T | None:
        """Met à jour une entité"""
        entity = db.query(self.model).get(entity_id)
        if not entity:
            raise ErreurNonTrouve(f"{self.model_name} {entity_id} non trouvé")
        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        db.commit()
        db.refresh(entity)
        logger.info(f"{self.model_name} {entity_id} mis à jour")
        self._invalider_cache()
        return entity

    @with_db_session
    def delete(self, entity_id: int, db: Session | None = None) -> bool:
        """Supprime une entité"""
        count = db.query(self.model).filter(self.model.id == entity_id).delete()
        db.commit()
        if count > 0:
            logger.info(f"{self.model_name} {entity_id} supprimé")
            self._invalider_cache()
            return True
        return False

    @with_db_session
    def count(self, filters: dict | None = None, db: Session | None = None) -> int:
        """Compte les entités"""
        query = db.query(self.model)
        if filters:
            query = self._apply_filters(query, filters)
        return query.count()

    # ════════════════════════════════════════════════════════════
    # RECHERCHE AVANCÉE
    # ════════════════════════════════════════════════════════════

    @with_db_session
    def advanced_search(
        self,
        search_term: str | None = None,
        search_fields: list[str] | None = None,
        filters: dict | None = None,
        sort_by: str | None = None,
        sort_desc: bool = False,
        limit: int = 100,
        offset: int = 0,
        db: Session | None = None,
    ) -> list[T]:
        """Recherche multi-critères"""
        query = db.query(self.model)

        # Recherche textuelle
        if search_term and search_fields:
            conditions = [
                getattr(self.model, field).ilike(f"%{search_term}%")
                for field in search_fields
                if hasattr(self.model, field)
            ]
            if conditions:
                query = query.filter(or_(*conditions))

        # Filtres
        if filters:
            query = self._apply_filters(query, filters)

        # Tri
        if sort_by and hasattr(self.model, sort_by):
            order_col = getattr(self.model, sort_by)
            query = query.order_by(desc(order_col) if sort_desc else order_col)

        return query.offset(offset).limit(limit).all()

    # ════════════════════════════════════════════════════════════
    # BULK OPERATIONS
    # ════════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=True)
    def bulk_create_with_merge(
        self,
        items_data: list[dict],
        merge_key: str,
        merge_strategy: Callable[[dict, dict], dict],
        db: Session | None = None,
    ) -> tuple[int, int]:
        """Création en masse avec fusion intelligente"""

        def _execute(session: Session) -> tuple[int, int]:
            created = merged = 0
            for data in items_data:
                merge_value = data.get(merge_key)
                if not merge_value:
                    continue

                existing = (
                    session.query(self.model)
                    .filter(getattr(self.model, merge_key) == merge_value)
                    .first()
                )

                if existing:
                    existing_dict = self._model_to_dict(existing)
                    merged_data = merge_strategy(existing_dict, data)
                    for key, value in merged_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    merged += 1
                else:
                    entity = self.model(**data)
                    session.add(entity)
                    created += 1

            session.commit()
            logger.info(f"Bulk: {created} créés, {merged} fusionnés")
            self._invalider_cache()
            return created, merged

        return self._with_session(_execute, db)

    # ════════════════════════════════════════════════════════════
    # STATISTIQUES
    # ════════════════════════════════════════════════════════════

    @gerer_erreurs(afficher_dans_ui=False, valeur_fallback={})
    def get_stats(
        self,
        group_by_fields: list[str] | None = None,
        count_filters: dict[str, dict] | None = None,
        additional_filters: dict | None = None,
        db: Session | None = None,
    ) -> dict:
        """Statistiques génériques"""

        def _execute(session: Session) -> dict:
            query = session.query(self.model)
            if additional_filters:
                query = self._apply_filters(query, additional_filters)

            stats = {"total": query.count()}

            # Groupements
            if group_by_fields:
                for field in group_by_fields:
                    if hasattr(self.model, field):
                        grouped = (
                            session.query(getattr(self.model, field), func.count(self.model.id))
                            .group_by(getattr(self.model, field))
                            .all()
                        )
                        stats[f"by_{field}"] = dict(grouped)

            # Compteurs conditionnels
            if count_filters:
                for name, filters in count_filters.items():
                    count_query = query
                    for k, v in filters.items():
                        if hasattr(self.model, k):
                            count_query = count_query.filter(getattr(self.model, k) == v)
                    stats[name] = count_query.count()

            return stats

        return self._with_session(_execute, db)

    # ════════════════════════════════════════════════════════════
    # MIXINS INTÉGRÉS
    # ════════════════════════════════════════════════════════════

    def count_by_status(self, status_field: str = "statut", db: Session | None = None) -> dict[str, int]:
        """Compte par statut"""
        stats = self.get_stats(group_by_fields=[status_field], db=db)
        return stats.get(f"by_{status_field}", {})

    def mark_as(
        self, item_id: int, status_field: str, status_value: str, db: Session | None = None
    ) -> bool:
        """Marque avec un statut"""
        return self.update(item_id, {status_field: status_value}, db=db) is not None

    # ════════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ════════════════════════════════════════════════════════════

    def _with_session(self, func: Callable, db: Session | None = None) -> Any:
        """Exécute fonction avec session"""
        if db:
            return func(db)
        with obtenir_contexte_db() as session:
            return func(session)

    def _apply_filters(self, query, filters: dict):
        """Applique filtres génériques"""
        for field, value in filters.items():
            if not hasattr(self.model, field):
                continue
            column = getattr(self.model, field)
            if not isinstance(value, dict):
                query = query.filter(column == value)
            else:
                for op, val in value.items():
                    if op == "gte":
                        query = query.filter(column >= val)
                    elif op == "lte":
                        query = query.filter(column <= val)
                    elif op == "in":
                        query = query.filter(column.in_(val))
                    elif op == "like":
                        query = query.filter(column.ilike(f"%{val}%"))
        return query

    def _model_to_dict(self, obj: Any) -> dict:
        """Convertit modèle en dict"""
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def _invalider_cache(self):
        """Invalide le cache"""
        Cache.invalider(pattern=self.model_name.lower())
