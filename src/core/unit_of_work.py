"""
Unit of Work — Pattern UoW pour transactions atomiques.

Encapsule une transaction DB complète avec commit/rollback
automatique et accès aux repositories typés.

Usage::

    with UnitOfWork() as uow:
        # Obtenir un repository typé
        repo = uow.repository(Recette)

        # Opérations multiples dans une seule transaction
        recette = repo.creer(Recette(nom="Tarte"))
        repo.supprimer_par_id(42)

        # Commit automatique en sortie du with
        # (rollback automatique sur exception)

Usage avancé::

    with UnitOfWork() as uow:
        recettes = uow.repository(Recette)
        courses = uow.repository(ArticleCourses)

        recette = recettes.creer(Recette(nom="Soupe"))
        courses.creer(ArticleCourses(nom="Carottes", recette_id=recette.id))

        uow.commit()  # Commit explicite (optionnel — commit aussi en sortie)
"""

from __future__ import annotations

import logging
from typing import Any, TypeVar

from sqlalchemy.orm import Session

from .repository import Repository

logger = logging.getLogger(__name__)

T = TypeVar("T")


class UnitOfWork:
    """
    Unit of Work — Gère une transaction atomique.

    Encapsule la création de session, le commit et le rollback.
    Fournit un accès aux repositories typés via :meth:`repository`.

    La session est créée lazily au premier accès.
    """

    def __init__(self, session: Session | None = None):
        """
        Args:
            session: Session SQLAlchemy existante (optionnel).
                Si None, une nouvelle session est créée via ``obtenir_contexte_db()``.
        """
        self._session_externe = session
        self._session: Session | None = None
        self._repositories: dict[type, Repository] = {}
        self._committed = False
        self._owns_session = False

    def __enter__(self) -> UnitOfWork:
        if self._session_externe:
            self._session = self._session_externe
        else:
            from src.core.db import obtenir_fabrique_session

            # Créer la session directement via la factory (pas via obtenir_contexte_db)
            # pour éviter le double-commit: UoW gère commit/rollback lui-même.
            fabrique = obtenir_fabrique_session()
            self._session = fabrique()
            self._owns_session = True

        return self

    def __exit__(self, exc_type: type | None, exc_val: Exception | None, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()
            logger.warning(f"UnitOfWork rollback: {exc_type.__name__}: {exc_val}")
        elif not self._committed:
            self.commit()

        # Fermer la session si on l'a créée
        if getattr(self, "_owns_session", False) and self._session is not None:
            self._session.close()

        self._repositories.clear()
        self._session = None

    @property
    def session(self) -> Session:
        """Session SQLAlchemy active."""
        if self._session is None:
            raise RuntimeError("UnitOfWork non initialisé. Utilisez 'with UnitOfWork() as uow:'")
        return self._session

    def repository(self, model: type[T]) -> Repository[T]:
        """
        Obtient un repository typé pour le modèle donné.

        Les repositories sont réutilisés au sein d'un même UoW
        (un seul repository par type de modèle).

        Args:
            model: Classe du modèle SQLAlchemy

        Returns:
            Repository typé pour ce modèle
        """
        if model not in self._repositories:
            self._repositories[model] = Repository(self.session, model)
        return self._repositories[model]

    def commit(self) -> None:
        """
        Commit la transaction en cours.

        Peut être appelé explicitement, sinon appelé automatiquement
        en sortie du context manager (si pas d'exception).
        """
        self.session.commit()
        self._committed = True
        logger.debug("UnitOfWork committed")

    def rollback(self) -> None:
        """
        Rollback la transaction en cours.

        Appelé automatiquement en cas d'exception dans le context manager.
        """
        try:
            self.session.rollback()
            logger.debug("UnitOfWork rolled back")
        except Exception:
            pass  # Session potentiellement déjà fermée

    def flush(self) -> None:
        """
        Flush les changements sans commit.

        Utile pour obtenir les IDs auto-générés avant le commit.
        """
        self.session.flush()


__all__ = ["UnitOfWork"]
