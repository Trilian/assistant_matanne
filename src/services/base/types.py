"""
Service Types - Types et classes de base partagés
Point d'entrée sans dépendances circulaires
"""

import logging
from datetime import datetime
from typing import Any, Generic, TypeVar, Callable, Optional

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

    ⚠️ ATTENTION : Ce fichier ne doit JAMAIS importer depuis src.ui
    """

    def __init__(self, model: type[T], cache_ttl: int = 60):
        self.model = model
        self.model_name = model.__name__
        self.cache_ttl = cache_ttl

    # ════════════════════════════════════════════════════════════
    # CRUD DE BASE
    # ════════════════════════════════════════════════════════════

    def create(self, data: dict, db: Session | None = None) -> T:
        """Crée une entité"""
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=True)
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
        from src.core.cache import Cache
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
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
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
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
        from src.core.errors import ErreurNonTrouve, gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=None)
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
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=True, valeur_fallback=False)
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
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=0)
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
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=[])
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
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=True)
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
        from src.core.errors import gerer_erreurs

        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback={})
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
                            attr = getattr(self.model, k)
                            # Support pour opérateurs avancés
                            if isinstance(v, dict):
                                # Opérateurs: lte, gte, lt, gt, eq, ne
                                for op, val in v.items():
                                    if op == "lte":
                                        count_query = count_query.filter(attr <= val)
                                    elif op == "gte":
                                        count_query = count_query.filter(attr >= val)
                                    elif op == "lt":
                                        count_query = count_query.filter(attr < val)
                                    elif op == "gt":
                                        count_query = count_query.filter(attr > val)
                                    elif op == "ne":
                                        count_query = count_query.filter(attr != val)
                                    else:  # eq ou défaut
                                        count_query = count_query.filter(attr == val)
                            else:
                                # Comparaison simple
                                count_query = count_query.filter(attr == v)
                    stats[name] = count_query.count()

            return stats

        return self._with_session(_execute, db)

    # ════════════════════════════════════════════════════════════
    # MIXINS INTÉGRÉS
    # ════════════════════════════════════════════════════════════

    def count_by_status(self, status_field: str = "statut", db: Session | None = None) -> dict[str, int]:
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
        from src.core.database import obtenir_contexte_db

        if db:
            return func(db)
        with obtenir_contexte_db() as session:
            return func(session)

    def _apply_filters(self, query, filters: dict):
        """Applique des filtres génériques à une requête SQLAlchemy.
        
        Supporte les opérateurs: gte, lte, in, like.
        
        Args:
            query: Requête SQLAlchemy
            filters: Dict {champ: valeur} ou {champ: {'op': valeur}}
            
        Returns:
            Requête filtrée
            
        Example:
            >>> _apply_filters(query, {'prix': {'lte': 100}, 'actif': True})
        """
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
        """Convertit un objet modèle SQLAlchemy en dictionnaire.
        
        Gère la sérialisation des dates en ISO format.
        
        Args:
            obj: Instance de modèle SQLAlchemy
            
        Returns:
            Dict avec les valeurs des colonnes
        """
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    def _invalider_cache(self):
        """Invalide le cache associé à ce modèle.
        
        Utilise le nom du modèle en minuscules comme pattern de recherche.
        Appelé automatiquement après create, update, delete.
        """
        from src.core.cache import Cache

        Cache.invalider(pattern=self.model_name.lower())


__all__ = ["BaseService", "T"]
