"""
Base Service - Service CRUD générique optimisé
Utilise les nouveaux decorators et cache
"""
from typing import TypeVar, Generic, List, Dict, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.core.database import get_db_context
from src.core.cache import Cache
from src.core.errors import handle_errors, NotFoundError, DatabaseError
from src.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class BaseService(Generic[T]):
    """
    Service CRUD de base avec decorators modernes

    Fonctionnalités:
    - CRUD complet avec cache
    - Error handling automatique
    - Logging intégré
    - Pagination
    """

    def __init__(self, model: type[T]):
        """
        Args:
            model: Modèle SQLAlchemy
        """
        self.model = model
        self.model_name = model.__name__

    # ═══════════════════════════════════════════════════════════
    # CREATE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def create(self, data: Dict, db: Session = None) -> T:
        """
        Crée une entité

        Args:
            data: Données
            db: Session (optionnelle)

        Returns:
            Entité créée
        """
        def _execute(session: Session) -> T:
            entity = self.model(**data)
            session.add(entity)
            session.commit()
            session.refresh(entity)

            logger.info(f"{self.model_name} créé: {entity.id}")
            Cache.invalidate(self.model_name.lower())

            return entity

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════
    # READ
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=None)
    @Cache.cached(ttl=60)
    def get_by_id(self, entity_id: int, db: Session = None) -> Optional[T]:
        """
        Récupère par ID (avec cache)

        Args:
            entity_id: ID
            db: Session (optionnelle)

        Returns:
            Entité ou None
        """
        def _execute(session: Session) -> Optional[T]:
            return session.query(self.model).get(entity_id)

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    @handle_errors(show_in_ui=False, fallback_value=[])
    @Cache.cached(ttl=60)
    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = "id",
            desc_order: bool = False,
            db: Session = None
    ) -> List[T]:
        """
        Liste toutes les entités (avec cache)

        Args:
            skip: Offset
            limit: Limite
            order_by: Champ de tri
            desc_order: Tri descendant
            db: Session (optionnelle)

        Returns:
            Liste d'entités
        """
        def _execute(session: Session) -> List[T]:
            query = session.query(self.model)

            # Tri
            if hasattr(self.model, order_by):
                order_col = getattr(self.model, order_by)
                query = query.order_by(
                    desc(order_col) if desc_order else order_col
                )

            return query.offset(skip).limit(limit).all()

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    @handle_errors(show_in_ui=False, fallback_value=0)
    def count(self, filters: Optional[Dict] = None, db: Session = None) -> int:
        """
        Compte les entités

        Args:
            filters: Filtres (optionnel)
            db: Session (optionnelle)

        Returns:
            Nombre d'entités
        """
        def _execute(session: Session) -> int:
            query = session.query(self.model)

            if filters:
                query = self._apply_filters(query, filters)

            return query.count()

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════
    # UPDATE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=None)
    def update(
            self,
            entity_id: int,
            data: Dict,
            db: Session = None
    ) -> Optional[T]:
        """
        Met à jour une entité

        Args:
            entity_id: ID
            data: Données à mettre à jour
            db: Session (optionnelle)

        Returns:
            Entité mise à jour ou None
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

            logger.info(f"{self.model_name} {entity_id} mis à jour")
            Cache.invalidate(self.model_name.lower())

            return entity

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════
    # DELETE
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True, fallback_value=False)
    def delete(self, entity_id: int, db: Session = None) -> bool:
        """
        Supprime une entité

        Args:
            entity_id: ID
            db: Session (optionnelle)

        Returns:
            True si supprimé
        """
        def _execute(session: Session) -> bool:
            count = session.query(self.model).filter(
                self.model.id == entity_id
            ).delete()

            session.commit()

            if count > 0:
                logger.info(f"{self.model_name} {entity_id} supprimé")
                Cache.invalidate(self.model_name.lower())
                return True

            return False

        if db:
            return _execute(db)

        with get_db_context() as db:
            return _execute(db)

    # ═══════════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════════

    def _apply_filters(self, query, filters: Dict):
        """Applique des filtres à une query"""
        for field, value in filters.items():
            if hasattr(self.model, field):
                column = getattr(self.model, field)

                # Filtre simple
                if not isinstance(value, dict):
                    query = query.filter(column == value)
                else:
                    # Filtres avancés
                    for op, val in value.items():
                        if op == "in":
                            query = query.filter(column.in_(val))
                        elif op == "gte":
                            query = query.filter(column >= val)
                        elif op == "lte":
                            query = query.filter(column <= val)

        return query