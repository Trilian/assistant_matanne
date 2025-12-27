"""
Service CRUD Ultra-Générique Enrichi
Élimine TOUTE la duplication entre services (inventaire, courses, recettes)

Version: 2.0.0
"""
from typing import List, Dict, Optional, TypeVar, Generic, Callable, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc
from datetime import datetime, timedelta
from collections import defaultdict
import logging

from src.core.database import get_db_context
from src.core.base_service import BaseService

logger = logging.getLogger(__name__)

T = TypeVar('T')


class EnhancedCRUDService(BaseService[T], Generic[T]):
    """
    Service CRUD enrichi avec fonctionnalités avancées

    Fonctionnalités :
    - Bulk operations avec stratégies de fusion
    - Statistiques génériques (groupby, count, avg)
    - Auto-cleanup avec filtres
    - Recherche avancée multi-critères
    - Export/Import générique
    - Audit trail automatique

    Usage :
        class InventaireService(EnhancedCRUDService[ArticleInventaire]):
            def __init__(self):
                super().__init__(ArticleInventaire)
    """

    # ═══════════════════════════════════════════════════════════════
    # BULK OPERATIONS
    # ═══════════════════════════════════════════════════════════════

    def bulk_create_with_merge(
            self,
            items_data: List[Dict],
            merge_key: str,
            merge_strategy: Callable[[Dict, Dict], Dict],
            db: Session = None
    ) -> Tuple[int, int]:
        """
        Création en masse SANS doublons

        Args:
            items_data: Liste de dicts à créer
            merge_key: Champ pour détecter doublons (ex: "nom")
            merge_strategy: Fonction(existing_dict, new_dict) -> merged_dict

        Returns:
            (nb_created, nb_merged)

        Example:
            def merge_max_quantity(existing, new):
                return {
                    **existing,
                    "quantite": max(existing["quantite"], new["quantite"])
                }

            created, merged = service.bulk_create_with_merge(
                items_data=[{"nom": "Tomates", "quantite": 5}, ...],
                merge_key="nom",
                merge_strategy=merge_max_quantity
            )
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
                    logger.debug(f"Merged: {merge_key}={merge_value}")
                else:
                    # Créer
                    self.create(data, db=session)
                    created += 1
                    logger.debug(f"Created: {merge_key}={merge_value}")

            session.commit()
            logger.info(f"Bulk operation: {created} created, {merged} merged")
            return created, merged

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    def bulk_update(
            self,
            updates: List[Dict],  # [{"id": 1, "data": {...}}, ...]
            db: Session = None
    ) -> int:
        """
        Mise à jour en masse

        Args:
            updates: Liste de {"id": int, "data": dict}

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
            logger.info(f"Bulk updated: {count} items")
            return count

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # STATISTIQUES GÉNÉRIQUES
    # ═══════════════════════════════════════════════════════════════

    def get_generic_stats(
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
                "by_categorie": {"Legumes": 50, "Fruits": 30},
                "critiques": 5,
                "quantite_moyenne": 12.5
            }
        """
        def _execute(session: Session) -> Dict:
            # Query de base
            query = session.query(self.model)

            # Filtre temporel
            if date_field and hasattr(self.model, date_field):
                date_limit = datetime.now() - timedelta(days=days_back)
                query = query.filter(
                    getattr(self.model, date_field) >= date_limit
                )

            # Filtres additionnels
            if additional_filters:
                for key, value in additional_filters.items():
                    if hasattr(self.model, key):
                        query = query.filter(getattr(self.model, key) == value)

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

            # Agrégations (moyenne, somme, etc.)
            if aggregate_fields:
                for agg_name, field_name in aggregate_fields.items():
                    if hasattr(self.model, field_name):
                        avg_value = session.query(
                            func.avg(getattr(self.model, field_name))
                        ).scalar()
                        stats[agg_name] = round(float(avg_value or 0), 2)

            logger.debug(f"Stats computed: {stats}")
            return stats

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # AUTO-CLEANUP
    # ═══════════════════════════════════════════════════════════════

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
            {
                "count": 10,
                "preview": [items...] if dry_run
            }
        """
        def _execute(session: Session) -> Dict:
            date_limit = datetime.now() - timedelta(days=days_old)

            query = session.query(self.model).filter(
                getattr(self.model, date_field) < date_limit
            )

            if additional_filters:
                for k, v in additional_filters.items():
                    if hasattr(self.model, k):
                        query = query.filter(getattr(self.model, k) == v)

            if dry_run:
                items = query.limit(100).all()
                return {
                    "count": query.count(),
                    "preview": [self._model_to_dict(item) for item in items]
                }

            count = query.delete(synchronize_session=False)
            session.commit()

            logger.info(f"Auto-cleanup: {count} items supprimés")
            return {"count": count}

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # RECHERCHE AVANCÉE
    # ═══════════════════════════════════════════════════════════════

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
            filters: {"categorie": "Legumes", "quantite": {"gte": 5}}
            sort_by: "nom"
            sort_desc: True
            limit: 100
            offset: 0

        Returns:
            Liste de modèles
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
                for field, value in filters.items():
                    if not hasattr(self.model, field):
                        continue

                    column = getattr(self.model, field)

                    # Filtre simple
                    if not isinstance(value, dict):
                        query = query.filter(column == value)
                    else:
                        # Filtres avancés (gte, lte, in, etc.)
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

            # Tri
            if sort_by and hasattr(self.model, sort_by):
                order_col = getattr(self.model, sort_by)
                query = query.order_by(
                    desc(order_col) if sort_desc else order_col
                )

            # Pagination
            return query.offset(offset).limit(limit).all()

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # EXPORT / IMPORT
    # ═══════════════════════════════════════════════════════════════

    def export_to_dict(
            self,
            filters: Optional[Dict] = None,
            exclude_fields: Optional[List[str]] = None,
            db: Session = None
    ) -> List[Dict]:
        """
        Export vers liste de dicts

        Args:
            filters: Filtres pour sélection
            exclude_fields: ["id", "created_at"]

        Returns:
            Liste de dicts prêts pour JSON/CSV
        """
        def _execute(session: Session) -> List[Dict]:
            query = session.query(self.model)

            if filters:
                query = self._apply_filters(query, filters)

            items = query.all()

            result = []
            for item in items:
                item_dict = self._model_to_dict(item)

                if exclude_fields:
                    for field in exclude_fields:
                        item_dict.pop(field, None)

                result.append(item_dict)

            return result

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    def import_from_dict(
            self,
            items: List[Dict],
            update_existing: bool = True,
            match_field: str = "id",
            db: Session = None
    ) -> Dict[str, int]:
        """
        Import depuis liste de dicts

        Args:
            items: Liste de dicts
            update_existing: Si True, update si existe
            match_field: Champ pour détecter existant

        Returns:
            {"created": 5, "updated": 3, "skipped": 2}
        """
        def _execute(session: Session) -> Dict[str, int]:
            stats = {"created": 0, "updated": 0, "skipped": 0}

            for item_data in items:
                try:
                    match_value = item_data.get(match_field)

                    if not match_value:
                        stats["skipped"] += 1
                        continue

                    # Chercher existant
                    existing = session.query(self.model).filter(
                        getattr(self.model, match_field) == match_value
                    ).first()

                    if existing:
                        if update_existing:
                            for key, value in item_data.items():
                                if hasattr(existing, key):
                                    setattr(existing, key, value)
                            stats["updated"] += 1
                        else:
                            stats["skipped"] += 1
                    else:
                        self.create(item_data, db=session)
                        stats["created"] += 1

                except Exception as e:
                    logger.error(f"Import error: {e}")
                    stats["skipped"] += 1

            session.commit()
            logger.info(f"Import: {stats}")
            return stats

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # AUDIT TRAIL
    # ═══════════════════════════════════════════════════════════════

    def get_recent_changes(
            self,
            days: int = 7,
            date_field: str = "modifie_le",
            limit: int = 100,
            db: Session = None
    ) -> List[Dict]:
        """
        Récupère les changements récents

        Args:
            days: Nombre de jours
            date_field: Champ date de modification
            limit: Max résultats

        Returns:
            Liste des items modifiés récemment
        """
        def _execute(session: Session) -> List[Dict]:
            if not hasattr(self.model, date_field):
                return []

            date_limit = datetime.now() - timedelta(days=days)

            items = session.query(self.model).filter(
                getattr(self.model, date_field) >= date_limit
            ).order_by(
                desc(getattr(self.model, date_field))
            ).limit(limit).all()

            return [self._model_to_dict(item) for item in items]

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════════
    # HELPERS PRIVÉS
    # ═══════════════════════════════════════════════════════════════

    def _model_to_dict(self, obj: Any) -> Dict:
        """Convertit modèle SQLAlchemy en dict"""
        result = {}

        for column in obj.__table__.columns:
            value = getattr(obj, column.name)

            # Convertir datetime en string
            if isinstance(value, (datetime, )):
                value = value.isoformat()

            result[column.name] = value

        return result

    def _apply_filters(self, query, filters: Dict):
        """Applique filtres à query (hérité de BaseService)"""
        return super()._apply_filters(query, filters)


# ═══════════════════════════════════════════════════════════════
# MIXINS SPÉCIALISÉS
# ═══════════════════════════════════════════════════════════════

class StatusTrackingMixin:
    """
    Mixin pour tracking de statut
    Usage: class CoursesService(EnhancedCRUDService, StatusTrackingMixin)
    """

    def count_by_status(
            self,
            status_field: str = "statut",
            db: Session = None
    ) -> Dict[str, int]:
        """Compte par statut"""
        stats = self.get_generic_stats(
            group_by_fields=[status_field],
            db=db
        )
        return stats.get(f"by_{status_field}", {})

    def mark_as(
            self,
            item_id: int,
            status_field: str,
            status_value: str,
            db: Session = None
    ) -> bool:
        """Marque un item avec un statut"""
        return self.update(
            item_id,
            {status_field: status_value},
            db=db
        ) is not None


class SoftDeleteMixin:
    """
    Mixin pour soft delete
    """

    def soft_delete(
            self,
            item_id: int,
            deleted_field: str = "deleted",
            db: Session = None
    ) -> bool:
        """Marque comme supprimé sans supprimer"""
        return self.update(
            item_id,
            {deleted_field: True, "deleted_at": datetime.now()},
            db=db
        ) is not None

    def restore(
            self,
            item_id: int,
            deleted_field: str = "deleted",
            db: Session = None
    ) -> bool:
        """Restaure un item supprimé"""
        return self.update(
            item_id,
            {deleted_field: False, "deleted_at": None},
            db=db
        ) is not None