"""
Service Types - Types et classes de base partagés
Point d'entrée sans dépendances circulaires
"""

import logging
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from sqlalchemy import desc, func, or_
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# BASE SERVICE (Sans dépendances UI)
# ═══════════════════════════════════════════════════════════


class BaseService(Generic[T]):
    """
    Service CRUD Universel avec toutes les fonctionnalités

    Inclut:
    - CRUD complet avec cache automatique
    - Bulk operations avec stratégies de fusion
    - Statistiques génériques
    - Recherche avancée multi-critères
    - Mixins intégrés (Status, SoftDelete, etc.)
    - Pipeline middleware optionnel (via ``pipeline`` property)

    ⚠️ ATTENTION : Ce fichier ne doit JAMAIS importer depuis src.ui
    """

    _pipeline_instance = None  # Lazy singleton partagé par sous-classes

    def __init__(self, model: type[T], cache_ttl: int = 60):
        self.model = model
        self.model_name = model.__name__
        self.cache_ttl = cache_ttl

    @property
    def pipeline(self):
        """Pipeline middleware minimal (lazy, partagé entre instances).

        Utilisé par ``execute_via_pipeline()`` et ``@service_method``.
        Créé au premier accès uniquement.
        """
        if BaseService._pipeline_instance is None:
            from src.services.core.middleware import ServicePipeline

            BaseService._pipeline_instance = ServicePipeline.default()
        return BaseService._pipeline_instance

    def execute_via_pipeline(
        self,
        func: Callable,
        *args: Any,
        cache: bool = False,
        cache_ttl: int = 300,
        rate_limit: bool = False,
        session: bool = False,
        fallback: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Exécute une callable à travers le pipeline middleware.

        Raccourci pour utiliser le pipeline sans le décorateur
        ``@service_method``.  Pratique pour les appels ponctuels.

        Args:
            func: Fonction à exécuter
            *args: Arguments positionnels passés à func
            cache: Activer le cache
            cache_ttl: TTL du cache (secondes)
            rate_limit: Activer le rate limiting
            session: Injecter une session DB
            fallback: Valeur de retour en cas d'erreur
            **kwargs: Arguments nommés passés à func

        Returns:
            Résultat de func

        Example:
            >>> result = self.execute_via_pipeline(
            ...     self._expensive_query,
            ...     cache=True, cache_ttl=600, session=True
            ... )
        """
        from src.services.core.middleware.pipeline import MiddlewareContext

        ctx = MiddlewareContext(
            service_name=self.model_name,
            method_name=func.__name__,
            args=args,
            kwargs=kwargs,
            use_cache=cache,
            cache_ttl=cache_ttl,
            use_rate_limit=rate_limit,
            use_session=session,
            fallback_value=fallback,
        )
        return self.pipeline.execute(func, ctx)

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
        from src.core.caching import Cache

        def _execute(session: Session) -> T | None:
            cache_key = f"{self.model_name.lower()}_{entity_id}"
            cached = Cache.obtenir(cache_key, ttl=self.cache_ttl)
            if cached:
                return cached

            entity = session.get(self.model, entity_id)
            if entity:
                Cache.definir(cache_key, entity, ttl=self.cache_ttl)
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
        from src.core.errors_base import ErreurNonTrouve

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
    # RECHERCHE AVANCÉE
    # ════════════════════════════════════════════════════════════

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

        def _execute(session: Session) -> list[T]:
            query = session.query(self.model)

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

        return self._with_session(_execute, db)

    # ════════════════════════════════════════════════════════════
    # BULK OPERATIONS
    # ════════════════════════════════════════════════════════════

    def bulk_create_with_merge(
        self,
        items_data: list[dict],
        merge_key: str,
        merge_strategy: Callable[[dict, dict], dict],
        db: Session | None = None,
    ) -> tuple[int, int]:
        """Création en masse avec fusion intelligente.

        Crée ou met à jour des entités en fonction d'une clé de fusion.
        Utile pour l'import de données avec déduplication.

        Args:
            items_data: Liste de dictionnaires de données
            merge_key: Champ utilisé pour identifier les doublons
            merge_strategy: Fonction (existant, nouveau) -> données fusionnées
            db: Session DB (optionnelle)

        Returns:
            Tuple (nombre créés, nombre fusionnés)

        Example:
            >>> def merge(old, new):
            ...     return {**old, **new}
            >>> service.bulk_create_with_merge(data, 'nom', merge)
            (5, 3)  # 5 créés, 3 mis à jour
        """

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

    def get_stats(
        self,
        group_by_fields: list[str] | None = None,
        count_filters: dict[str, dict] | None = None,
        additional_filters: dict | None = None,
        db: Session | None = None,
    ) -> dict:
        """Calcule des statistiques génériques sur les entités.

        Args:
            group_by_fields: Champs pour grouper les comptages
            count_filters: Filtres conditionnels {'nom': {'champ': valeur}}
            additional_filters: Filtres globaux
            db: Session DB (optionnelle)

        Returns:
            Dict avec 'total' et statistiques groupées

        Example:
            >>> service.get_stats(
            ...     group_by_fields=['statut'],
            ...     count_filters={'actifs': {'actif': True}}
            ... )
            {'total': 100, 'by_statut': {'en_cours': 50, 'termine': 50}, 'actifs': 80}
        """

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
                    count_query = self._apply_filters(query, filters)
                    stats[name] = count_query.count()

            return stats

        return self._with_session(_execute, db)

    # ════════════════════════════════════════════════════════════
    # MIXINS INTÉGRÉS
    # ════════════════════════════════════════════════════════════

    def count_by_status(
        self, status_field: str = "statut", db: Session | None = None
    ) -> dict[str, int]:
        """Compte les entités groupées par statut.

        Args:
            status_field: Nom du champ de statut (défaut: 'statut')
            db: Session DB (optionnelle)

        Returns:
            Dict {statut: nombre}

        Example:
            >>> service.count_by_status()
            {'en_cours': 10, 'termine': 5, 'annule': 2}
        """
        stats = self.get_stats(group_by_fields=[status_field], db=db)
        return stats.get(f"by_{status_field}", {})

    def mark_as(
        self, item_id: int, status_field: str, status_value: str, db: Session | None = None
    ) -> bool:
        """Marque une entité avec un statut spécifique.

        Args:
            item_id: ID de l'entité
            status_field: Nom du champ de statut
            status_value: Nouvelle valeur du statut
            db: Session DB (optionnelle)

        Returns:
            True si mis à jour, False sinon

        Example:
            >>> service.mark_as(42, 'statut', 'termine')
            True
        """
        return self.update(item_id, {status_field: status_value}, db=db) is not None

    # ════════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ════════════════════════════════════════════════════════════

    def _with_session(self, func: Callable, db: Session | None = None) -> Any:
        """Exécute une fonction avec une session DB.

        Si une session est fournie, l'utilise directement.
        Sinon, crée une nouvelle session via le context manager.

        Args:
            func: Fonction à exécuter (prend Session en paramètre)
            db: Session DB existante (optionnelle)

        Returns:
            Résultat de la fonction
        """
        from src.core.db import obtenir_contexte_db

        if db:
            return func(db)
        with obtenir_contexte_db() as session:
            return func(session)

    def _apply_filters(self, query, filters: dict):
        """Applique des filtres génériques à une requête SQLAlchemy.

        Supporte les opérateurs: eq, ne, gt, lt, gte, lte, in, like.
        Si la valeur n'est pas un dict, un filtre d'égalité est appliqué.
        Les opérateurs inconnus sont ignorés avec un avertissement.

        Args:
            query: Requête SQLAlchemy
            filters: Dict {champ: valeur} ou {champ: {'op': valeur}}

        Returns:
            Requête filtrée

        Example:
            >>> _apply_filters(query, {'prix': {'lte': 100, 'gt': 0}, 'actif': True})
            >>> _apply_filters(query, {'nom': {'like': 'tart'}, 'cat': {'in': ['A','B']}})
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
        """Convertit un objet modèle SQLAlchemy en dictionnaire.

        Délègue à utils_serialization.model_to_dict (source de vérité unique).

        Args:
            obj: Instance de modèle SQLAlchemy

        Returns:
            Dict avec les valeurs des colonnes sérialisées
        """
        from src.services.core.backup.utils_serialization import model_to_dict

        return model_to_dict(obj)

    def _invalider_cache(self):
        """Invalide le cache associé à ce modèle.

        Utilise le nom du modèle en minuscules comme pattern de recherche.
        Appelé automatiquement après create, update, delete.
        """
        from src.core.caching import Cache

        Cache.invalider(pattern=self.model_name.lower())

    # ════════════════════════════════════════════════════════════
    # API SAFE — Retourne Result[T, ErrorInfo] au lieu d'exceptions
    # ════════════════════════════════════════════════════════════

    def safe_create(self, data: dict, db: Session | None = None):
        """Crée une entité, retourne Result au lieu de lever une exception.

        Returns:
            Success[T] si créé, Failure[ErrorInfo] si erreur

        Example:
            >>> result = service.safe_create({"nom": "Tarte"})
            >>> if result.is_success:
            ...     print(result.value.id)
            >>> else:
            ...     print(result.error.message)
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            entity = self.create(data, db)
            self._emettre_evenement("created", {"id": entity.id})
            return success(entity)
        except Exception as e:
            code = self._mapper_code_erreur(e)
            if code != ErrorCode.INTERNAL_ERROR:
                return failure(code, str(e), source=self.model_name)
            return from_exception(e, source=self.model_name)

    def safe_get_by_id(self, entity_id: int, db: Session | None = None):
        """Récupère par ID, retourne Result (jamais None).

        Returns:
            Success[T] si trouvé, Failure[ErrorInfo] avec NOT_FOUND sinon

        Example:
            >>> result = service.safe_get_by_id(42)
            >>> recette = result.unwrap_or(None)
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            entity = self.get_by_id(entity_id, db)
            if entity is None:
                return failure(
                    ErrorCode.NOT_FOUND,
                    f"{self.model_name} {entity_id} non trouvé",
                    message_utilisateur=f"Élément {entity_id} introuvable",
                    source=self.model_name,
                )
            return success(entity)
        except Exception as e:
            return from_exception(e, source=self.model_name)

    def safe_get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict | None = None,
        order_by: str = "id",
        desc_order: bool = False,
        db: Session | None = None,
    ):
        """Liste avec filtres, retourne Result.

        Returns:
            Success[list[T]] toujours (liste vide si aucun résultat),
            Failure[ErrorInfo] si erreur DB
        """
        from src.services.core.base.result import from_exception, success

        try:
            entities = self.get_all(skip, limit, filters, order_by, desc_order, db)
            return success(entities)
        except Exception as e:
            return from_exception(e, source=self.model_name)

    def safe_update(self, entity_id: int, data: dict, db: Session | None = None):
        """Met à jour une entité, retourne Result.

        Returns:
            Success[T] si mis à jour, Failure[ErrorInfo] si non trouvé ou erreur
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            entity = self.update(entity_id, data, db)
            self._emettre_evenement("updated", {"id": entity_id})
            return success(entity)
        except Exception as e:
            code = self._mapper_code_erreur(e)
            if code == ErrorCode.NOT_FOUND:
                return failure(
                    ErrorCode.NOT_FOUND,
                    str(e),
                    message_utilisateur=f"Élément {entity_id} introuvable",
                    source=self.model_name,
                )
            return from_exception(e, source=self.model_name)

    def safe_delete(self, entity_id: int, db: Session | None = None):
        """Supprime une entité, retourne Result.

        Returns:
            Success[True] si supprimé, Failure[ErrorInfo] si non trouvé ou erreur
        """
        from src.services.core.base.result import (
            ErrorCode,
            failure,
            from_exception,
            success,
        )

        try:
            deleted = self.delete(entity_id, db)
            if not deleted:
                return failure(
                    ErrorCode.NOT_FOUND,
                    f"{self.model_name} {entity_id} non trouvé",
                    message_utilisateur=f"Élément {entity_id} introuvable",
                    source=self.model_name,
                )
            self._emettre_evenement("deleted", {"id": entity_id})
            return success(True)
        except Exception as e:
            return from_exception(e, source=self.model_name)

    def safe_count(self, filters: dict | None = None, db: Session | None = None):
        """Compte les entités, retourne Result.

        Returns:
            Success[int], Failure[ErrorInfo] si erreur
        """
        from src.services.core.base.result import from_exception, success

        try:
            total = self.count(filters, db)
            return success(total)
        except Exception as e:
            return from_exception(e, source=self.model_name)

    # ════════════════════════════════════════════════════════════
    # EVENT BUS — Émission d'événements domaine
    # ════════════════════════════════════════════════════════════

    def _emettre_evenement(self, action: str, data: dict | None = None) -> None:
        """Émet un événement domaine via le bus d'événements.

        Format: entity.{ModelName}.{action}
        Ex: entity.Recette.created, entity.ArticleInventaire.deleted

        Args:
            action: Action (created, updated, deleted)
            data: Données associées à l'événement
        """
        try:
            from src.services.core.events.bus import obtenir_bus

            event_type = f"entity.{self.model_name}.{action}"
            event_data = {"model": self.model_name, **(data or {})}
            obtenir_bus().emettre(event_type, event_data, source=self.model_name)
        except Exception as e:
            # Le bus d'événements ne doit jamais bloquer les opérations
            logger.debug("Émission événement échouée: %s — %s", action, e, exc_info=True)

    @staticmethod
    def _mapper_code_erreur(exc: Exception):
        """Mappe une exception vers un ErrorCode standardisé.

        Args:
            exc: Exception à mapper

        Returns:
            ErrorCode correspondant
        """
        from src.services.core.base.result import ErrorCode

        # Mapper les exceptions métier
        exc_type = type(exc).__name__
        mapping = {
            "ErreurNonTrouve": ErrorCode.NOT_FOUND,
            "ErreurValidation": ErrorCode.VALIDATION_ERROR,
            "ErreurBaseDeDonnees": ErrorCode.DATABASE_ERROR,
            "ErreurServiceIA": ErrorCode.AI_ERROR,
            "ErreurLimiteDebit": ErrorCode.RATE_LIMITED,
            "ErreurConfiguration": ErrorCode.CONFIGURATION_ERROR,
            "IntegrityError": ErrorCode.CONSTRAINT_VIOLATION,
            "DataError": ErrorCode.VALIDATION_ERROR,
        }
        return mapping.get(exc_type, ErrorCode.INTERNAL_ERROR)

    # ════════════════════════════════════════════════════════════
    # HEALTH CHECK — Satisfait HealthCheckProtocol
    # ════════════════════════════════════════════════════════════

    def health_check(self):
        """Vérifie la santé du service (connexion DB, modèle accessible).

        Returns:
            ServiceHealth avec statut et latence
        """
        import time

        from src.services.core.base.protocols import ServiceHealth, ServiceStatus

        start = time.perf_counter()
        try:
            total = self.count()
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                service_name=f"BaseService<{self.model_name}>",
                message=f"{total} entités en base",
                latency_ms=latency,
                details={"model": self.model_name, "count": total},
            )
        except Exception as e:
            latency = (time.perf_counter() - start) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                service_name=f"BaseService<{self.model_name}>",
                message=f"Erreur: {e}",
                latency_ms=latency,
                details={"error": str(e)},
            )


__all__ = ["BaseService", "T"]
