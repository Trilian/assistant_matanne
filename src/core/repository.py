"""
Repository - Pattern Repository générique pour les accès DB.

Encapsule les opérations CRUD courantes de SQLAlchemy
dans une interface propre et réutilisable.

Usage:
    >>> class RecetteRepository(Repository[Recette]):
    >>>     pass
    >>>
    >>> repo = RecetteRepository(session, Recette)
    >>> recette = repo.obtenir_par_id(42)
    >>> toutes = repo.lister(filtre={"saison": "été"})
    >>> repo.creer(Recette(nom="Tarte"))
"""

import logging
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .errors_base import ErreurNonTrouve

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Repository(Generic[T]):
    """
    Repository générique pour opérations CRUD.

    Args:
        session: Session SQLAlchemy
        model: Classe du modèle ORM

    Type Parameters:
        T: Type du modèle SQLAlchemy
    """

    def __init__(self, session: Session, model: type[T]) -> None:
        self.session = session
        self.model = model

    def obtenir_par_id(self, id: int) -> T | None:
        """
        Récupère une entité par son ID.

        Args:
            id: Identifiant unique

        Returns:
            Entité ou None si non trouvée
        """
        return self.session.get(self.model, id)

    def obtenir_ou_erreur(self, id: int) -> T:
        """
        Récupère une entité par ID ou lève une erreur.

        Args:
            id: Identifiant unique

        Returns:
            Entité

        Raises:
            ErreurNonTrouve: Si l'entité n'existe pas
        """
        entity = self.obtenir_par_id(id)
        if entity is None:
            raise ErreurNonTrouve(
                f"{self.model.__name__} #{id} non trouvé",
                details={"model": self.model.__name__, "id": id},
                message_utilisateur=f"{self.model.__name__} introuvable",
            )
        return entity

    def lister(
        self,
        filtre: dict[str, Any] | None = None,
        ordre: str | None = None,
        limite: int | None = None,
        offset: int | None = None,
    ) -> list[T]:
        """
        Liste les entités avec filtres optionnels.

        Args:
            filtre: Dict {colonne: valeur} pour filtrage par égalité
            ordre: Nom de colonne pour tri (préfixer par '-' pour DESC)
            limite: Nombre max de résultats
            offset: Décalage pour pagination

        Returns:
            Liste d'entités
        """
        stmt = select(self.model)

        # Appliquer les filtres
        if filtre:
            for col_name, value in filtre.items():
                col = getattr(self.model, col_name, None)
                if col is not None:
                    stmt = stmt.where(col == value)

        # Appliquer le tri
        if ordre:
            if ordre.startswith("-"):
                col = getattr(self.model, ordre[1:], None)
                if col is not None:
                    stmt = stmt.order_by(col.desc())
            else:
                col = getattr(self.model, ordre, None)
                if col is not None:
                    stmt = stmt.order_by(col.asc())

        # Pagination
        if limite is not None:
            stmt = stmt.limit(limite)
        if offset is not None:
            stmt = stmt.offset(offset)

        return list(self.session.scalars(stmt).all())

    def compter(self, filtre: dict[str, Any] | None = None) -> int:
        """
        Compte les entités (avec filtres optionnels).

        Args:
            filtre: Dict {colonne: valeur} pour filtrage

        Returns:
            Nombre d'entités
        """
        stmt = select(func.count()).select_from(self.model)

        if filtre:
            for col_name, value in filtre.items():
                col = getattr(self.model, col_name, None)
                if col is not None:
                    stmt = stmt.where(col == value)

        return self.session.scalar(stmt) or 0

    def creer(self, entite: T) -> T:
        """
        Crée une nouvelle entité.

        Args:
            entite: Instance du modèle

        Returns:
            Entité persistée (avec ID)
        """
        self.session.add(entite)
        self.session.flush()
        logger.debug(f"[+] {self.model.__name__} créé (id={getattr(entite, 'id', '?')})")
        return entite

    def mettre_a_jour(self, entite: T) -> T:
        """
        Met à jour une entité existante.

        Args:
            entite: Entité modifiée

        Returns:
            Entité mise à jour
        """
        self.session.merge(entite)
        self.session.flush()
        logger.debug(f"[~] {self.model.__name__} mis à jour (id={getattr(entite, 'id', '?')})")
        return entite

    def supprimer(self, entite: T) -> None:
        """
        Supprime une entité.

        Args:
            entite: Entité à supprimer
        """
        self.session.delete(entite)
        self.session.flush()
        logger.debug(f"[-] {self.model.__name__} supprimé (id={getattr(entite, 'id', '?')})")

    def supprimer_par_id(self, id: int) -> bool:
        """
        Supprime une entité par ID.

        Args:
            id: Identifiant unique

        Returns:
            True si supprimé, False si non trouvé
        """
        entite = self.obtenir_par_id(id)
        if entite is None:
            return False
        self.supprimer(entite)
        return True

    def existe(self, id: int) -> bool:
        """Vérifie si une entité existe par ID."""
        return self.obtenir_par_id(id) is not None
