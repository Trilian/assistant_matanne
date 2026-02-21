"""Mixin: recherche avancée, bulk operations, statistiques et helpers de statut."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from sqlalchemy import desc, func, or_

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class AdvancedQueryMixin:
    """Fournit advanced_search, bulk_create_with_merge, get_stats, count_by_status, mark_as.

    Attend sur ``self``: model, model_name, _with_session, _apply_filters,
    _model_to_dict, _invalider_cache, update.
    """

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
    ) -> list:
        """Recherche multi-critères"""

        def _execute(session: Session) -> list:
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
