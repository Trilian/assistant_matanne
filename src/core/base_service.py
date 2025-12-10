"""
Service de Base Générique pour CRUD
Réduit la duplication de code et standardise les opérations
"""
from abc import ABC
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime

from src.core.database import get_db_context

T = TypeVar('T')


class BaseService(ABC, Generic[T]):
    """
    Service de base avec opérations CRUD standardisées

    Usage:
        class RecetteService(BaseService[Recette]):
            def __init__(self):
                super().__init__(Recette)
    """

    def __init__(self, model: Type[T]):
        self.model = model

    # ===================================
    # LECTURE
    # ===================================

    def get_by_id(self, id: int, db: Session = None) -> Optional[T]:
        """Récupère par ID"""
        if db:
            return db.query(self.model).filter(self.model.id == id).first()

        with get_db_context() as db:
            return db.query(self.model).filter(self.model.id == id).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            db: Session = None
    ) -> List[T]:
        """Récupère tous les enregistrements avec pagination"""
        if db:
            return db.query(self.model).offset(skip).limit(limit).all()

        with get_db_context() as db:
            return db.query(self.model).offset(skip).limit(limit).all()

    def count(self, filters: Dict[str, Any] = None, db: Session = None) -> int:
        """Compte les enregistrements"""
        query = db.query(func.count(self.model.id)) if db else None

        if not db:
            with get_db_context() as db:
                query = db.query(func.count(self.model.id))

                if filters:
                    query = self._apply_filters(query, filters)

                return query.scalar()

        if filters:
            query = self._apply_filters(query, filters)

        return query.scalar()

    def exists(self, id: int, db: Session = None) -> bool:
        """Vérifie si un enregistrement existe"""
        if db:
            return db.query(self.model.id).filter(self.model.id == id).first() is not None

        with get_db_context() as db:
            return db.query(self.model.id).filter(self.model.id == id).first() is not None

    # ===================================
    # CRÉATION
    # ===================================

    def create(self, data: Dict[str, Any], db: Session = None) -> T:
        """Crée un nouvel enregistrement"""
        if db:
            obj = self.model(**data)
            db.add(obj)
            db.flush()
            return obj

        with get_db_context() as db:
            obj = self.model(**data)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj

    def create_many(self, data_list: List[Dict[str, Any]], db: Session = None) -> List[T]:
        """Crée plusieurs enregistrements en batch"""
        if db:
            objects = [self.model(**data) for data in data_list]
            db.add_all(objects)
            db.flush()
            return objects

        with get_db_context() as db:
            objects = [self.model(**data) for data in data_list]
            db.add_all(objects)
            db.commit()
            return objects

    # ===================================
    # MISE À JOUR
    # ===================================

    def update(
            self,
            id: int,
            data: Dict[str, Any],
            db: Session = None
    ) -> Optional[T]:
        """Met à jour un enregistrement"""
        if db:
            obj = self.get_by_id(id, db)
            if not obj:
                return None

            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            # Auto-update modifie_le si existe
            if hasattr(obj, 'modifie_le'):
                obj.modifie_le = datetime.utcnow()

            db.flush()
            return obj

        with get_db_context() as db:
            obj = self.get_by_id(id, db)
            if not obj:
                return None

            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)

            if hasattr(obj, 'modifie_le'):
                obj.modifie_le = datetime.utcnow()

            db.commit()
            db.refresh(obj)
            return obj

    def update_many(
            self,
            updates: List[Dict[str, Any]],  # [{"id": 1, "data": {...}}]
            db: Session = None
    ) -> List[T]:
        """Met à jour plusieurs enregistrements"""
        if db:
            updated = []
            for item in updates:
                obj = self.update(item["id"], item["data"], db)
                if obj:
                    updated.append(obj)
            return updated

        with get_db_context() as db:
            updated = []
            for item in updates:
                obj = self.update(item["id"], item["data"], db)
                if obj:
                    updated.append(obj)
            return updated

    # ===================================
    # SUPPRESSION
    # ===================================

    def delete(self, id: int, db: Session = None) -> bool:
        """Supprime un enregistrement"""
        if db:
            obj = self.get_by_id(id, db)
            if not obj:
                return False

            db.delete(obj)
            db.flush()
            return True

        with get_db_context() as db:
            obj = self.get_by_id(id, db)
            if not obj:
                return False

            db.delete(obj)
            db.commit()
            return True

    def delete_many(self, ids: List[int], db: Session = None) -> int:
        """Supprime plusieurs enregistrements"""
        if db:
            count = db.query(self.model).filter(
                self.model.id.in_(ids)
            ).delete(synchronize_session=False)
            db.flush()
            return count

        with get_db_context() as db:
            count = db.query(self.model).filter(
                self.model.id.in_(ids)
            ).delete(synchronize_session=False)
            db.commit()
            return count

    # ===================================
    # RECHERCHE
    # ===================================

    def search(
            self,
            search_term: str,
            search_fields: List[str],
            filters: Dict[str, Any] = None,
            skip: int = 0,
            limit: int = 100,
            db: Session = None
    ) -> List[T]:
        """
        Recherche full-text

        Args:
            search_term: Terme à rechercher
            search_fields: Champs où chercher (ex: ["nom", "description"])
            filters: Filtres additionnels
        """
        if db:
            query = db.query(self.model)
        else:
            with get_db_context() as db:
                query = db.query(self.model)

                # Recherche
                if search_term:
                    conditions = [
                        getattr(self.model, field).ilike(f"%{search_term}%")
                        for field in search_fields
                        if hasattr(self.model, field)
                    ]
                    query = query.filter(or_(*conditions))

                # Filtres
                if filters:
                    query = self._apply_filters(query, filters)

                return query.offset(skip).limit(limit).all()

        # Recherche
        if search_term:
            conditions = [
                getattr(self.model, field).ilike(f"%{search_term}%")
                for field in search_fields
                if hasattr(self.model, field)
            ]
            query = query.filter(or_(*conditions))

        # Filtres
        if filters:
            query = self._apply_filters(query, filters)

        return query.offset(skip).limit(limit).all()

    # ===================================
    # HELPERS PRIVÉS
    # ===================================

    def _apply_filters(self, query, filters: Dict[str, Any]):
        """Applique des filtres à une query"""
        for field, value in filters.items():
            if not hasattr(self.model, field):
                continue

            if isinstance(value, (list, tuple)):
                # IN clause
                query = query.filter(getattr(self.model, field).in_(value))
            elif isinstance(value, dict):
                # Opérateurs complexes
                for op, val in value.items():
                    column = getattr(self.model, field)
                    if op == "gt":
                        query = query.filter(column > val)
                    elif op == "gte":
                        query = query.filter(column >= val)
                    elif op == "lt":
                        query = query.filter(column < val)
                    elif op == "lte":
                        query = query.filter(column <= val)
                    elif op == "ne":
                        query = query.filter(column != val)
            else:
                # Égalité simple
                query = query.filter(getattr(self.model, field) == value)

        return query


# ===================================
# PAGINATION HELPER
# ===================================

from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    """Résultat paginé"""
    items: List[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    class Config:
        arbitrary_types_allowed = True


def paginate(
        service: BaseService,
        page: int = 1,
        page_size: int = 20,
        filters: Dict[str, Any] = None,
        db: Session = None
) -> Page:
    """
    Helper de pagination

    Usage:
        page = paginate(recette_service, page=2, page_size=10)
    """
    total = service.count(filters=filters, db=db)
    skip = (page - 1) * page_size
    items = service.get_all(skip=skip, limit=page_size, db=db)

    return Page(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )