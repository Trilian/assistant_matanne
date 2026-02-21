"""
Repository - Pattern Repository générique pour les accès DB.

Encapsule les opérations CRUD courantes de SQLAlchemy
dans une interface propre et réutilisable.

Usage classique::

    >>> class RecetteRepository(Repository[Recette]):
    >>>     pass
    >>>
    >>> repo = RecetteRepository(session, Recette)
    >>> recette = repo.obtenir_par_id(42)
    >>> toutes = repo.lister(filtre={"saison": "été"})
    >>> repo.creer(Recette(nom="Tarte"))

Usage avec Specification::

    >>> from src.core.specifications import par_champ, contient, paginer
    >>>
    >>> spec = par_champ("actif", True) & contient("nom", "tarte") & paginer(1, 20)
    >>> recettes = repo.lister(spec=spec)
"""

import logging
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import DeclarativeBase, Session

from .errors_base import ErreurNonTrouve

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=DeclarativeBase)

__all__ = ["Repository"]


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
        spec: "Specification | None" = None,
    ) -> list[T]:
        """
        Liste les entités avec filtres optionnels ou spécification.

        Args:
            filtre: Dict {colonne: valeur} pour filtrage par égalité
            ordre: Nom de colonne pour tri (préfixer par '-' pour DESC)
            limite: Nombre max de résultats
            offset: Décalage pour pagination
            spec: Spécification composable (prioritaire sur filtre/ordre)

        Returns:
            Liste d'entités
        """
        stmt = select(self.model)

        # Spécification composable (prioritaire)
        if spec is not None:
            stmt = spec.appliquer(stmt, self.model)

        # Filtres classiques (fallback si pas de spec)
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

    def compter(
        self, filtre: dict[str, Any] | None = None, spec: "Specification | None" = None
    ) -> int:
        """
        Compte les entités (avec filtres optionnels ou spécification).

        Args:
            filtre: Dict {colonne: valeur} pour filtrage
            spec: Spécification composable

        Returns:
            Nombre d'entités
        """
        stmt = select(func.count()).select_from(self.model)

        if spec is not None:
            stmt = spec.appliquer(stmt, self.model)

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

    # ── Opérations en masse ──────────────────────────────────

    def creer_en_masse(self, entites: list[T]) -> list[T]:
        """
        Crée plusieurs entités en une seule opération.

        Args:
            entites: Liste d'instances du modèle

        Returns:
            Liste d'entités persistées
        """
        self.session.add_all(entites)
        self.session.flush()
        logger.debug(f"[+] {self.model.__name__} x{len(entites)} créés en masse")
        return entites

    def supprimer_par_spec(self, spec: "Specification") -> int:
        """
        Supprime les entités correspondant à une spécification.

        Args:
            spec: Spécification de filtrage

        Returns:
            Nombre d'entités supprimées
        """
        entites = self.lister(spec=spec)
        for entite in entites:
            self.session.delete(entite)
        self.session.flush()
        logger.debug(f"[-] {self.model.__name__} x{len(entites)} supprimés par spec")
        return len(entites)

    def premier(self, spec: "Specification | None" = None) -> T | None:
        """
        Retourne la première entité correspondant à la spec.

        Args:
            spec: Spécification de filtrage (optionnel)

        Returns:
            Première entité ou None
        """
        stmt = select(self.model)
        if spec is not None:
            stmt = spec.appliquer(stmt, self.model)
        stmt = stmt.limit(1)
        return self.session.scalars(stmt).first()

    # ── Opérations retournant Result ─────────────────────────

    def obtenir_result(self, id: int) -> "Result[T, ErrorInfo]":
        """
        Récupère une entité par ID, retourne Result.

        Returns:
            Ok(entité) ou Err(ErrorInfo NOT_FOUND)
        """
        from .result import ErrorCode, Ok, failure

        entity = self.obtenir_par_id(id)
        if entity is None:
            return failure(
                ErrorCode.NOT_FOUND,
                f"{self.model.__name__} #{id} non trouvé",
                message_utilisateur=f"{self.model.__name__} introuvable",
                details={"model": self.model.__name__, "id": id},
            )
        return Ok(entity)

    def premier_result(self, spec: "Specification | None" = None) -> "Result[T, ErrorInfo]":
        """
        Retourne la première entité correspondant à la spec, ou Err.

        Returns:
            Ok(entité) ou Err(ErrorInfo NOT_FOUND)
        """
        from .result import ErrorCode, Ok, failure

        entity = self.premier(spec)
        if entity is None:
            return failure(
                ErrorCode.NOT_FOUND,
                f"Aucun {self.model.__name__} trouvé",
                message_utilisateur=f"{self.model.__name__} introuvable",
            )
        return Ok(entity)

    def creer_result(self, entite: T) -> "Result[T, ErrorInfo]":
        """
        Crée une entité, retourne Result.

        Returns:
            Ok(entité) ou Err(ErrorInfo) en cas d'erreur DB
        """
        from .result import Ok, from_exception

        try:
            created = self.creer(entite)
            return Ok(created)
        except Exception as e:
            return from_exception(e, source=f"{self.model.__name__}.creer")

    def mettre_a_jour_en_masse(self, spec: "Specification", **valeurs: Any) -> int:
        """
        Met à jour en masse les entités correspondant à la spec.

        Args:
            spec: Spécification de filtrage
            **valeurs: Colonnes à mettre à jour

        Returns:
            Nombre d'entités modifiées
        """
        entites = self.lister(spec=spec)
        for entite in entites:
            for col_name, value in valeurs.items():
                setattr(entite, col_name, value)
        self.session.flush()
        logger.debug(f"[~] {self.model.__name__} x{len(entites)} mis à jour en masse")
        return len(entites)
