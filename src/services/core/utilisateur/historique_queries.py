"""
Requêtes et statistiques pour l'historique des actions.

Extrait du service principal pour réduire sa taille.
Contient:
- Consultation de l'historique (filtrage, pagination)
- Statistiques d'activité
- Fonctionnalité Undo
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from .historique_types import ActionEntry, ActionFilter, ActionStats, ActionType

logger = logging.getLogger(__name__)


class HistoriqueQueriesMixin:
    """
    Mixin fournissant les requêtes d'historique.

    Contient les méthodes de consultation, filtrage et statistiques.
    """

    def get_history(self, filters: ActionFilter | None = None) -> list[ActionEntry]:
        """
        Récupère l'historique filtré.

        Args:
            filters: Critères de filtrage

        Returns:
            Liste d'entrées d'historique
        """
        filters = filters or ActionFilter()

        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models import HistoriqueAction

            with obtenir_contexte_db() as session:
                query = session.query(HistoriqueAction)

                if filters.user_id:
                    query = query.filter(HistoriqueAction.user_id == filters.user_id)

                if filters.action_types:
                    query = query.filter(
                        HistoriqueAction.action_type.in_([a.value for a in filters.action_types])
                    )

                if filters.entity_type:
                    query = query.filter(HistoriqueAction.entity_type == filters.entity_type)

                if filters.entity_id:
                    query = query.filter(HistoriqueAction.entity_id == filters.entity_id)

                if filters.date_from:
                    query = query.filter(HistoriqueAction.cree_le >= filters.date_from)

                if filters.date_to:
                    query = query.filter(HistoriqueAction.cree_le <= filters.date_to)

                if filters.search_text:
                    query = query.filter(
                        HistoriqueAction.description.ilike(f"%{filters.search_text}%")
                    )

                entries = (
                    query.order_by(HistoriqueAction.cree_le.desc())
                    .offset(filters.offset)
                    .limit(filters.limit)
                    .all()
                )

                return [ActionEntry.model_validate(e) for e in entries]

        except Exception as e:
            logger.error(f"Erreur lecture historique: {e}")
            # Fallback sur le cache
            return self._recent_cache[: filters.limit]

    def get_user_history(self, user_id: str, limit: int = 20) -> list[ActionEntry]:
        """Récupère l'historique d'un utilisateur."""
        return self.get_history(ActionFilter(user_id=user_id, limit=limit))

    def get_entity_history(
        self, entity_type: str, entity_id: int, limit: int = 20
    ) -> list[ActionEntry]:
        """Récupère l'historique d'une entité spécifique."""
        return self.get_history(
            ActionFilter(entity_type=entity_type, entity_id=entity_id, limit=limit)
        )

    def get_recent_actions(self, limit: int = 10) -> list[ActionEntry]:
        """Récupère les actions récentes (toutes utilisateurs)."""
        return self.get_history(ActionFilter(limit=limit))


class HistoriqueStatsMixin:
    """
    Mixin fournissant les statistiques d'activité.
    """

    def get_stats(self, days: int = 7) -> ActionStats:
        """
        Calcule les statistiques d'activité.

        Args:
            days: Nombre de jours à analyser

        Returns:
            Statistiques d'activité
        """
        try:
            from sqlalchemy import func

            from src.core.db import obtenir_contexte_db
            from src.core.models import HistoriqueAction

            with obtenir_contexte_db() as session:
                now = datetime.now()
                week_ago = now - timedelta(days=days)
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

                # Total actions
                total = session.query(func.count(HistoriqueAction.id)).scalar() or 0

                # Actions aujourd'hui
                today_count = (
                    session.query(func.count(HistoriqueAction.id))
                    .filter(HistoriqueAction.cree_le >= today_start)
                    .scalar()
                    or 0
                )

                # Actions cette semaine
                week_count = (
                    session.query(func.count(HistoriqueAction.id))
                    .filter(HistoriqueAction.cree_le >= week_ago)
                    .scalar()
                    or 0
                )

                # Utilisateurs les plus actifs
                top_users = (
                    session.query(
                        HistoriqueAction.user_name, func.count(HistoriqueAction.id).label("count")
                    )
                    .filter(HistoriqueAction.cree_le >= week_ago)
                    .group_by(HistoriqueAction.user_name)
                    .order_by(func.count(HistoriqueAction.id).desc())
                    .limit(5)
                    .all()
                )

                # Actions les plus fréquentes
                top_actions = (
                    session.query(
                        HistoriqueAction.action_type, func.count(HistoriqueAction.id).label("count")
                    )
                    .filter(HistoriqueAction.cree_le >= week_ago)
                    .group_by(HistoriqueAction.action_type)
                    .order_by(func.count(HistoriqueAction.id).desc())
                    .limit(5)
                    .all()
                )

                return ActionStats(
                    total_actions=total,
                    actions_today=today_count,
                    actions_this_week=week_count,
                    most_active_users=[{"name": u[0], "count": u[1]} for u in top_users],
                    most_common_actions=[{"type": a[0], "count": a[1]} for a in top_actions],
                )

        except Exception as e:
            logger.error(f"Erreur stats: {e}")
            return ActionStats()


class HistoriqueUndoMixin:
    """
    Mixin fournissant la fonctionnalité Undo.
    """

    def can_undo(self, action_id: int) -> bool:
        """
        Vérifie si une action peut être annulée.

        Args:
            action_id: ID de l'action

        Returns:
            True si l'action peut être annulée
        """
        # Types d'actions réversibles
        reversible_types = {
            ActionType.RECETTE_DELETED,
            ActionType.INVENTAIRE_CONSUMED,
            ActionType.COURSES_ITEM_CHECKED,
            ActionType.PLANNING_REPAS_DELETED,
        }

        history = self.get_history(ActionFilter(limit=100))
        for entry in history:
            if entry.id == action_id:
                return entry.action_type in reversible_types and entry.old_value is not None

        return False

    def undo_action(self, action_id: int) -> bool:
        """
        Annule une action en restaurant l'ancienne valeur.

        Fonctionne pour les types réversibles qui ont un old_value sauvegardé:
        - Recettes (updated, deleted, favorited)
        - Inventaire (updated, consumed)
        - Courses (item_checked)
        - Planning (repas_deleted)

        Args:
            action_id: ID de l'action à annuler

        Returns:
            True si l'annulation a réussi
        """
        from src.core.db import obtenir_contexte_db
        from src.core.models import HistoriqueAction

        try:
            with obtenir_contexte_db() as session:
                # Récupérer l'action en DB
                action = (
                    session.query(HistoriqueAction).filter(HistoriqueAction.id == action_id).first()
                )

                if not action:
                    logger.warning(f"Action {action_id} non trouvée")
                    return False

                if not action.old_value:
                    logger.warning(f"Action {action_id} n'a pas de old_value pour restauration")
                    return False

                entity_type = action.entity_type
                entity_id = action.entity_id
                old_data = action.old_value

                # Restaurer selon le type d'entité
                restored = self._restore_entity(session, entity_type, entity_id, old_data)

                if restored:
                    # Logger l'action d'annulation
                    undo_entry = HistoriqueAction(
                        user_id=action.user_id,
                        user_name=action.user_name,
                        action_type="system.undo",
                        entity_type=entity_type,
                        entity_id=entity_id,
                        entity_name=action.entity_name,
                        description=f"Annulation de: {action.description}",
                        details={"undo_of_action_id": action_id},
                        old_value=action.new_value,
                        new_value=action.old_value,
                    )
                    session.add(undo_entry)
                    session.commit()
                    logger.info(f"Action {action_id} annulée avec succès")

                return restored

        except Exception as e:
            logger.error(f"Erreur undo action {action_id}: {e}")
            return False

    def _restore_entity(
        self, session: Session, entity_type: str, entity_id: int | None, old_data: dict
    ) -> bool:
        """Restaure une entité à partir des données sauvegardées.

        Args:
            session: Session DB active
            entity_type: Type d'entité (recette, inventaire, etc.)
            entity_id: ID de l'entité
            old_data: Données à restaurer

        Returns:
            True si restauration réussie
        """
        if not entity_id:
            logger.warning("Pas d'entity_id pour la restauration")
            return False

        try:
            model_class = self._get_model_class(entity_type)
            if not model_class:
                logger.warning(f"Type d'entité inconnu: {entity_type}")
                return False

            entity = session.query(model_class).filter(model_class.id == entity_id).first()

            if entity:
                # Mettre à jour les champs avec les anciennes valeurs
                for key, value in old_data.items():
                    if hasattr(entity, key) and key != "id":
                        setattr(entity, key, value)
                return True
            else:
                logger.warning(f"{entity_type} {entity_id} non trouvé, impossible de restaurer")
                return False

        except Exception as e:
            logger.error(f"Erreur restauration {entity_type} {entity_id}: {e}")
            return False

    @staticmethod
    def _get_model_class(entity_type: str):
        """Retourne la classe de modèle SQLAlchemy pour un type d'entité."""
        try:
            from src.core.models import (
                ArticleCourses,
                Ingredient,
                PlanningRepas,
                Recette,
            )

            mapping = {
                "recette": Recette,
                "inventaire": Ingredient,
                "courses": ArticleCourses,
                "planning": PlanningRepas,
            }
            return mapping.get(entity_type)
        except ImportError:
            return None


__all__ = [
    "HistoriqueQueriesMixin",
    "HistoriqueStatsMixin",
    "HistoriqueUndoMixin",
]
