"""
Base Service Optimisé - Architecture Finale
Fusionne BaseService + EnhancedCRUDService avec toutes les optimisations
"""
from typing import TypeVar, Generic, List, Dict, Optional, Any, Callable, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from src.core.database import get_db_context
from src.core.cache import Cache
from src.core.errors import handle_errors, NotFoundError, DatabaseError
from src.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class BaseServiceOptimized(Generic[T]):
    """
    Service CRUD Ultra-Optimisé - Version Finale

    Combine :
    - CRUD de base (create, read, update, delete)
    - Bulk operations intelligentes
    - Statistiques génériques
    - Auto-cleanup
    - Recherche avancée multi-critères
    - Cache automatique
    - Error handling intégré
    - Logging structuré

    Usage:
        class RecetteService(BaseServiceOptimized[Recette]):
            def __init__(self):
                super().__init__(Recette, cache_ttl=60)
    """

    def __init__(
            self,
            model: type[T],
            cache_ttl: int = 60,
            auto_cache: bool = True,
            auto_log: bool = True
    ):
        """
        Args:
            model: Modèle SQLAlchemy
            cache_ttl: TTL du cache par défaut (secondes)
            auto_cache: Cache automatique sur get_by_id/get_all
            auto_log: Logging automatique des opérations
        """
        self.model = model
        self.model_name = model.__name__
        self.cache_ttl = cache_ttl
        self.auto_cache = auto_cache
        self.auto_log = auto_log

    # ═══════════════════════════════════════════════════════════════
    # CRUD DE BASE (avec cache & error handling auto)
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def create(self, data: Dict, db: Session = None) -> T:
        """
        Crée une entité

        ✅ Error handling auto
        ✅ Logging auto
        ✅ Invalidation cache auto
        """
        def _execute(session: Session) -> T:
            entity = self.model(**data)
            session.add(entity)
            session.commit()
            session.refresh(entity)

            if self.auto_log:
                logger.info(f"{self.model_name} créé: {entity.id}")

            self._invalidate_cache()
            return entity

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=False, fallback_value=None)
    def get_by_id(self, entity_id: int, db: Session = None) -> Optional[T]:
        """
        Récupère par ID

        ✅ Cache auto (si auto_cache=True)
        """
        cache_key = f"{self.model_name.lower()}_{entity_id}"

        if self.auto_cache:
            cached = Cache.get(cache_key, ttl=self.cache_ttl)
            if cached:
                return cached

        def _execute(session: Session) -> Optional[T]:
            entity = session.query(self.model).get(entity_id)

            if entity and self.auto_cache:
                Cache.set(cache_key, entity, ttl=self.cache_ttl)

            return entity

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=False, fallback_value=[])
    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = "id",
            desc_order: bool = False,
            filters: Optional[Dict] = None,
            db: Session = None
    ) -> List[T]:
        """
        Liste toutes les entités

        ✅ Cache auto
        ✅ Filtres génériques
        """
        cache_key = f"{self.model_name.lower()}_all_{skip}_{limit}_{order_by}_{desc_order}"

        if self.auto_cache and not filters:
            cached = Cache.get(cache_key, ttl=self.cache_ttl)
            if cached:
                return cached

        def _execute(session: Session) -> List[T]:
            query = session.query(self.model)

            # Filtres
            if filters:
                query = self._apply_filters(query, filters)

            # Tri
            if hasattr(self.model, order_by):
                order_col = getattr(self.model, order_by)
                query = query.order_by(
                    desc(order_col) if desc_order else order_col
                )

            results = query.offset(skip).limit(limit).all()

            if self.auto_cache and not filters:
                Cache.set(cache_key, results, ttl=self.cache_ttl)

            return results

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=True, fallback_value=None)
    def update(self, entity_id: int, data: Dict, db: Session = None) -> Optional[T]:
        """
        Met à jour une entité

        ✅ Error handling auto
        ✅ Invalidation cache
        """
        def _execute(session: Session) -> Optional[T]:
            entity = session.query(self.model).get(entity_id)

            if not entity:
                raise NotFoundError(
                    f"{self.model_name} {entity_id} non trouvé",
                    user_message=f"{self.model_name} introuvable"
                )

            for key, value in data.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)

            session.commit()
            session.refresh(entity)

            if self.auto_log:
                logger.info(f"{self.model_name} {entity_id} mis à jour")

            self._invalidate_cache()
            return entity

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=True, fallback_value=False)
    def delete(self, entity_id: int, db: Session = None) -> bool:
        """
        Supprime une entité

        ✅ Error handling auto
        ✅ Invalidation cache
        """
        def _execute(session: Session) -> bool:
            count = session.query(self.model).filter(
                self.model.id == entity_id
            ).delete()

            session.commit()

            if count > 0:
                if self.auto_log:
                    logger.info(f"{self.model_name} {entity_id} supprimé")
                self._invalidate_cache()
                return True

            return False

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=False, fallback_value=0)
    def count(self, filters: Optional[Dict] = None, db: Session = None) -> int:
        """Compte les entités"""
        def _execute(session: Session) -> int:
            query = session.query(self.model)

            if filters:
                query = self._apply_filters(query, filters)

            return query.count()

        return self._with_session(_execute, db)

    # ═══════════════════════════════════════════════════════════════
    # BULK OPERATIONS OPTIMISÉES
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def bulk_create_with_merge(
            self,
            items_data: List[Dict],
            merge_key: str,
            merge_strategy: Callable[[Dict, Dict], Dict],
            db: Session = None
    ) -> Tuple[int, int]:
        """
        Création en masse avec stratégie de fusion intelligente

        Args:
            items_data: Liste de dicts à créer
            merge_key: Champ pour détecter doublons (ex: "nom")
            merge_strategy: Fonction(existing_dict, new_dict) -> merged_dict

        Returns:
            (nb_created, nb_merged)
        """
        def _execute(session: Session) -> Tuple[int, int]:
            created = 0
            merged = 0

            for data in items_data:
                merge_value = data.get(merge_key)
                if not merge_value:
                    continue

                # Chercher existant
                existing = session.query(self.model).filter(
                    getattr(self.model, merge_key) == merge_value
                ).first()

                if existing:
                    # Fusionner
                    existing_dict = self._model_to_dict(existing)
                    merged_data = merge_strategy(existing_dict, data)

                    # Mettre à jour
                    for key, value in merged_data.items():
                        if hasattr(existing, key):
                            setattr(existing, key, value)

                    merged += 1
                else:
                    # Créer
                    entity = self.model(**data)
                    session.add(entity)
                    created += 1

            session.commit()

            if self.auto_log:
                logger.info(f"Bulk: {created} créés, {merged} fusionnés")

            self._invalidate_cache()
            return created, merged

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=True)
    def bulk_update(
            self,
            updates: List[Dict],  # [{"id": 1, "data": {...}}, ...]
            db: Session = None
    ) -> int:
        """
        Mise à jour en masse

        Returns:
            Nombre mis à jour
        """
        def _execute(session: Session) -> int:
            count = 0

            for item in updates:
                if "id" not in item or "data" not in item:
                    continue

                obj = session.query(self.model).get(item["id"])
                if obj:
                    for key, value in item["data"].items():
                        if hasattr(obj, key):
                            setattr(obj, key, value)
                    count += 1

            session.commit()

            if self.auto_log:
                logger.info(f"Bulk updated: {count} items")

            self._invalidate_cache()
            return count

        return self._with_session(_execute, db)

    @handle_errors(show_in_ui=True)
    def bulk_delete(
            self,
            entity_ids: List[int],
            db: Session = None
    ) -> int:
        """
        Suppression en masse

        Returns:
            Nombre supprimé
        """
        def _execute(session: Session) -> int:
            count = session.query(self.model).filter(
                self.model.id.in_(entity_ids)
            ).delete(synchronize_session=False)

            session.commit()

            if self.auto_log:
                logger.info(f"Bulk deleted: {count} items")

            self._invalidate_cache()
            return count

        return self._with_session(_execute, db)

    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES GÉNÉRIQUES
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value={})
    def get_stats(
            self,
            group_by_fields: Optional[List[str]] = None,
            count_filters: Optional[Dict[str, Dict]] = None,
            aggregate_fields: Optional[Dict[str, str]] = None,
            date_field: Optional[str] = None,
            days_back: int = 30,
            additional_filters: Optional[Dict] = None,
            db: Session = None
    ) -> Dict:
        """
        Statistiques génériques ultra-flexibles

        Args:
            group_by_fields: ["categorie", "priorite"]
            count_filters: {"critiques": {"statut": "critique"}}
            aggregate_fields: {"quantite_moyenne": "quantite"} (avg)
            date_field: "cree_le" (filtre temporel)
            days_back: 30 jours
            additional_filters: {"actif": True}

        Returns:
            {
                "total": 150,
                "by_categorie": {"Legumes": 50},
                "critiques": 5,
                "quantite_moyenne": 12.5
            }
        """
        def _execute(session: Session) -> Dict:
            query = session.query(self.model)

            # Filtre temporel
            if date_field and hasattr(self.model, date_field):
                date_limit = datetime.now() - timedelta(days=days_back)
                query = query.filter(
                    getattr(self.model, date_field) >= date_limit
                )

            # Filtres additionnels
            if additional_filters:
                query = self._apply_filters(query, additional_filters)

            stats = {}

            # Total
            stats["total"] = query.count()

            # Groupements
            if group_by_fields:
                for field in group_by_fields:
                    if hasattr(self.model, field):
                        grouped = session.query(
                            getattr(self.model, field),
                            func.count(self.model.id)
                        ).group_by(getattr(self.model, field)).all()

                        stats[f"by_{field}"] = dict(grouped)

            # Compteurs conditionnels
            if count_filters:
                for name, filters in count_filters.items():
                    count_query = query
                    for k, v in filters.items():
                        if hasattr(self.model, k):
                            count_query = count_query.filter(
                                getattr(self.model, k) == v
                            )
                    stats[name] = count_query.count()

            # Agrégations
            if aggregate_fields:
                for agg_name, field_name in aggregate_fields.items():
                    if hasattr(self.model, field_name):
                        avg_value = session.query(
                            func.avg(getattr(self.model, field_name))
                        ).scalar()
                        stats[agg_name] = round(float(avg_value or 0), 2)

            return stats

        return self._with_session(_execute, db)

    # ═══════════════════════════════════════════════════════════════
    # RECHERCHE AVANCÉE
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=[])
    def advanced_search(
            self,
            search_term: Optional[str] = None,
            search_fields: Optional[List[str]] = None,
            filters: Optional[Dict] = None,
            sort_by: Optional[str] = None,
            sort_desc: bool = False,
            limit: int = 100,
            offset: int = 0,
            db: Session = None
    ) -> List[T]:
        """
        Recherche multi-critères ultra-flexible

        Args:
            search_term: "tomates"
            search_fields: ["nom", "description"]
            filters: {
                "categorie": "Legumes",
                "quantite": {"gte": 5}
            }
            sort_by: "nom"
            sort_desc: True

        Returns:
            Liste d'entités
        """
        def _execute(session: Session) -> List[T]:
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
                query = query.order_by(
                    desc(order_col) if sort_desc else order_col
                )

            return query.offset(offset).limit(limit).all()

        return self._with_session(_execute, db)

    # ═══════════════════════════════════════════════════════════════
    # AUTO-CLEANUP
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def auto_cleanup(
            self,
            date_field: str,
            days_old: int,
            additional_filters: Optional[Dict] = None,
            dry_run: bool = False,
            db: Session = None
    ) -> Dict[str, Any]:
        """
        Nettoyage automatique avec preview

        Args:
            date_field: Champ date à vérifier
            days_old: Supprimer si > X jours
            additional_filters: {"achete": True}
            dry_run: Si True, retourne liste sans supprimer

        Returns:
            {"count": 10, "preview": [...] if dry_run}
        """
        def _execute(session: Session) -> Dict:
            date_limit = datetime.now() - timedelta(days=days_old)

            query = session.query(self.model).filter(
                getattr(self.model, date_field) < date_limit
            )

            if additional_filters:
                query = self._apply_filters(query, additional_filters)

            if dry_run:
                items = query.limit(100).all()
                return {
                    "count": query.count(),
                    "preview": [self._model_to_dict(item) for item in items]
                }

            count = query.delete(synchronize_session=False)
            session.commit()

            if self.auto_log:
                logger.info(f"Auto-cleanup: {count} items supprimés")

            self._invalidate_cache()
            return {"count": count}

        return self._with_session(_execute, db)

    # ═══════════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════════

    def _with_session(self, func: Callable, db: Optional[Session]) -> Any:
        """Exécute fonction avec session (fournie ou nouvelle)"""
        if db:
            return func(db)

        with get_db_context() as session:
            return func(session)

    def _apply_filters(self, query, filters: Dict):
        """Applique filtres génériques à query"""
        for field, value in filters.items():
            if not hasattr(self.model, field):
                continue

            column = getattr(self.model, field)

            # Filtre simple
            if not isinstance(value, dict):
                query = query.filter(column == value)
            else:
                # Filtres avancés
                for op, val in value.items():
                    if op == "gte":
                        query = query.filter(column >= val)
                    elif op == "lte":
                        query = query.filter(column <= val)
                    elif op == "gt":
                        query = query.filter(column > val)
                    elif op == "lt":
                        query = query.filter(column < val)
                    elif op == "in":
                        query = query.filter(column.in_(val))
                    elif op == "not_in":
                        query = query.filter(~column.in_(val))
                    elif op == "like":
                        query = query.filter(column.ilike(f"%{val}%"))

        return query

    def _model_to_dict(self, obj: Any) -> Dict:
        """Convertit modèle SQLAlchemy en dict"""
        result = {}

        for column in obj.__table__.columns:
            value = getattr(obj, column.name)

            # Convertir datetime
            if isinstance(value, (datetime,)):
                value = value.isoformat()

            result[column.name] = value

        return result

    def _invalidate_cache(self):
        """Invalide le cache pour ce modèle"""
        Cache.invalidate(self.model_name.lower())