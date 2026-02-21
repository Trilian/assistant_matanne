"""Mixin: API Safe — retourne Result[T, ErrorInfo] au lieu d'exceptions."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SafeOperationsMixin:
    """Fournit safe_create/get_by_id/get_all/update/delete/count, event bus, error mapper.

    Attend sur ``self``: model_name, create, get_by_id, get_all, update, delete, count.
    """

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
        from src.core.result import (
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
        from src.core.result import (
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
        from src.core.result import from_exception, success

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
        from src.core.result import (
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
        from src.core.result import (
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
        from src.core.result import from_exception, success

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
        from src.core.result import ErrorCode

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
