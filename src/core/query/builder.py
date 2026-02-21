"""
Builder - Query builder fluent pour SQLAlchemy.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, and_, delete, func, or_, select
from sqlalchemy.orm import Session

T = TypeVar("T")


@dataclass
class Requete(Generic[T]):
    """
    Query builder fluent et composable pour SQLAlchemy.

    Permet de construire des requêtes de manière déclarative
    et chaînable, avec une API expressive en français.

    Usage::
        recettes = (
            Requete(Recette)
            .et(actif=True)
            .contient("nom", "tarte")
            .entre("temps_preparation", 10, 30)
            .trier_par("-date_creation")
            .paginer(page=1, taille=20)
            .executer(session)
        )

    Type Parameters:
        T: Type du modèle SQLAlchemy
    """

    model: type[T]
    _conditions: list[Any] = field(default_factory=list)
    _conditions_or: list[Any] = field(default_factory=list)
    _ordre: list[Any] = field(default_factory=list)
    _limit: int | None = None
    _offset: int | None = None
    _jointures: list[Any] = field(default_factory=list)

    def et(self, **criteres: Any) -> Requete[T]:
        """
        Ajoute des critères en ET (AND).

        Usage::
            .et(actif=True, categorie="dessert")
        """
        for col_name, value in criteres.items():
            col = getattr(self.model, col_name, None)
            if col is not None:
                self._conditions.append(col == value)
        return self

    def ou(self, **criteres: Any) -> Requete[T]:
        """
        Ajoute des critères en OU (OR).

        Usage::
            .ou(categorie="dessert", categorie="entrée")
        """
        conditions = []
        for col_name, value in criteres.items():
            col = getattr(self.model, col_name, None)
            if col is not None:
                conditions.append(col == value)
        if conditions:
            self._conditions_or.append(or_(*conditions))
        return self

    def ou_parmi(self, champ: str, valeurs: Sequence[Any]) -> Requete[T]:
        """
        OU entre plusieurs valeurs pour un champ (IN).

        Usage::
            .ou_parmi("categorie", ["dessert", "entrée", "plat"])
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            self._conditions.append(col.in_(valeurs))
        return self

    def contient(self, champ: str, valeur: str, insensible_casse: bool = True) -> Requete[T]:
        """
        Filtre par contenance (LIKE %valeur%).

        Args:
            champ: Nom de la colonne
            valeur: Texte à rechercher
            insensible_casse: Ignorer la casse (défaut: True)

        Usage::
            .contient("nom", "tarte")
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            pattern = f"%{valeur}%"
            if insensible_casse:
                self._conditions.append(col.ilike(pattern))
            else:
                self._conditions.append(col.like(pattern))
        return self

    def commence_par(self, champ: str, valeur: str) -> Requete[T]:
        """
        Filtre par préfixe (LIKE valeur%).

        Usage::
            .commence_par("code", "REC-")
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            self._conditions.append(col.like(f"{valeur}%"))
        return self

    def termine_par(self, champ: str, valeur: str) -> Requete[T]:
        """
        Filtre par suffixe (LIKE %valeur).

        Usage::
            .termine_par("email", "@gmail.com")
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            self._conditions.append(col.like(f"%{valeur}"))
        return self

    def entre(
        self,
        champ: str,
        valeur_min: Any,
        valeur_max: Any,
        inclusif: bool = True,
    ) -> Requete[T]:
        """
        Filtre par plage de valeurs (BETWEEN).

        Args:
            champ: Nom de la colonne
            valeur_min: Valeur minimale
            valeur_max: Valeur maximale
            inclusif: Inclure les bornes (défaut: True)

        Usage::
            .entre("prix", 10, 50)
            .entre("date", date(2024, 1, 1), date(2024, 12, 31))
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            if inclusif:
                self._conditions.append(col >= valeur_min)
                self._conditions.append(col <= valeur_max)
            else:
                self._conditions.append(col > valeur_min)
                self._conditions.append(col < valeur_max)
        return self

    def superieur_a(self, champ: str, valeur: Any, strict: bool = True) -> Requete[T]:
        """
        Filtre > ou >= une valeur.

        Usage::
            .superieur_a("prix", 100)
            .superieur_a("prix", 100, strict=False)  # >=
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            if strict:
                self._conditions.append(col > valeur)
            else:
                self._conditions.append(col >= valeur)
        return self

    def inferieur_a(self, champ: str, valeur: Any, strict: bool = True) -> Requete[T]:
        """
        Filtre < ou <= une valeur.

        Usage::
            .inferieur_a("stock", 10)
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            if strict:
                self._conditions.append(col < valeur)
            else:
                self._conditions.append(col <= valeur)
        return self

    def est_null(self, champ: str) -> Requete[T]:
        """
        Filtre les valeurs NULL.

        Usage::
            .est_null("date_suppression")
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            self._conditions.append(col.is_(None))
        return self

    def non_null(self, champ: str) -> Requete[T]:
        """
        Filtre les valeurs non NULL.

        Usage::
            .non_null("email_verifie")
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            self._conditions.append(col.isnot(None))
        return self

    def dans(self, champ: str, valeurs: Sequence[Any]) -> Requete[T]:
        """
        Filtre par liste de valeurs (IN).

        Usage::
            .dans("statut", ["actif", "en_attente"])
        """
        col = getattr(self.model, champ, None)
        if col is not None and valeurs:
            self._conditions.append(col.in_(valeurs))
        return self

    def pas_dans(self, champ: str, valeurs: Sequence[Any]) -> Requete[T]:
        """
        Filtre exclusion de liste (NOT IN).

        Usage::
            .pas_dans("statut", ["supprime", "archive"])
        """
        col = getattr(self.model, champ, None)
        if col is not None and valeurs:
            self._conditions.append(col.notin_(valeurs))
        return self

    def apres(self, champ: str, valeur: date | datetime, inclusif: bool = False) -> Requete[T]:
        """
        Filtre date après.

        Usage::
            .apres("date_creation", date(2024, 1, 1))
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            if inclusif:
                self._conditions.append(col >= valeur)
            else:
                self._conditions.append(col > valeur)
        return self

    def avant(self, champ: str, valeur: date | datetime, inclusif: bool = False) -> Requete[T]:
        """
        Filtre date avant.

        Usage::
            .avant("date_expiration", datetime.now())
        """
        col = getattr(self.model, champ, None)
        if col is not None:
            if inclusif:
                self._conditions.append(col <= valeur)
            else:
                self._conditions.append(col < valeur)
        return self

    def trier_par(self, *champs: str) -> Requete[T]:
        """
        Tri par champs (préfixer par - pour DESC).

        Usage::
            .trier_par("-date_creation", "nom")
            # ORDER BY date_creation DESC, nom ASC
        """
        for champ in champs:
            if champ.startswith("-"):
                col = getattr(self.model, champ[1:], None)
                if col is not None and hasattr(col, "desc"):
                    self._ordre.append(col.desc())
            else:
                col = getattr(self.model, champ, None)
                if col is not None and hasattr(col, "asc"):
                    self._ordre.append(col.asc())
        return self

    def paginer(self, page: int = 1, taille: int = 20) -> Requete[T]:
        """
        Pagination (page commence à 1).

        Usage::
            .paginer(page=2, taille=50)
        """
        self._limit = taille
        self._offset = (max(1, page) - 1) * taille
        return self

    def limite(self, n: int) -> Requete[T]:
        """
        Limite le nombre de résultats.

        Usage::
            .limite(10)
        """
        self._limit = n
        return self

    def decaler(self, n: int) -> Requete[T]:
        """
        Décale les résultats (OFFSET).

        Usage::
            .decaler(20)
        """
        self._offset = n
        return self

    def joindre(self, relation: Any) -> Requete[T]:
        """
        Ajoute une jointure.

        Usage::
            .joindre(Recette.ingredients)
        """
        self._jointures.append(relation)
        return self

    def construire(self) -> Select[tuple[T]]:
        """Construit le statement SQLAlchemy."""
        stmt = select(self.model)

        for jointure in self._jointures:
            stmt = stmt.join(jointure)

        # Combiner conditions AND et OR
        all_conditions = list(self._conditions)
        if self._conditions_or:
            all_conditions.extend(self._conditions_or)

        if all_conditions:
            stmt = stmt.where(and_(*all_conditions))

        for ordre in self._ordre:
            stmt = stmt.order_by(ordre)

        if self._limit is not None:
            stmt = stmt.limit(self._limit)

        if self._offset is not None:
            stmt = stmt.offset(self._offset)

        return stmt

    def executer(self, session: Session) -> list[T]:
        """
        Exécute la requête et retourne les résultats.

        Args:
            session: Session SQLAlchemy

        Returns:
            Liste des entités correspondantes
        """
        return list(session.scalars(self.construire()).all())

    def premier(self, session: Session) -> T | None:
        """
        Retourne le premier résultat ou None.

        Args:
            session: Session SQLAlchemy
        """
        return session.scalars(self.construire()).first()

    def premier_ou_erreur(self, session: Session, message: str = "Non trouvé") -> T:
        """
        Retourne le premier résultat ou lève une erreur.

        Args:
            session: Session SQLAlchemy
            message: Message d'erreur si non trouvé

        Raises:
            ValueError: Si aucun résultat
        """
        result = self.premier(session)
        if result is None:
            raise ValueError(message)
        return result

    def compter(self, session: Session) -> int:
        """
        Compte les résultats (sans les charger).

        Args:
            session: Session SQLAlchemy
        """
        all_conditions = list(self._conditions) + list(self._conditions_or)
        count_stmt = select(func.count()).select_from(self.model)
        if all_conditions:
            count_stmt = count_stmt.where(and_(*all_conditions))
        return session.scalar(count_stmt) or 0

    def existe(self, session: Session) -> bool:
        """
        Vérifie si au moins un résultat existe.

        Args:
            session: Session SQLAlchemy
        """
        return self.limite(1).premier(session) is not None

    def supprimer(self, session: Session) -> int:
        """
        Supprime les entités correspondantes via DELETE SQL direct.

        Utilise un ``DELETE ... WHERE`` au lieu de charger les objets
        en mémoire, ce qui est nettement plus performant sur les
        grandes tables (O(1) mémoire au lieu de O(n)).

        Args:
            session: Session SQLAlchemy

        Returns:
            Nombre d'entités supprimées
        """
        stmt = delete(self.model)

        all_conditions = list(self._conditions)
        if self._conditions_or:
            all_conditions.extend(self._conditions_or)

        if all_conditions:
            stmt = stmt.where(and_(*all_conditions))

        result = session.execute(stmt)
        session.flush()
        return result.rowcount  # type: ignore[return-value]

    def __repr__(self) -> str:
        return (
            f"Requete({self.model.__name__}, "
            f"conditions={len(self._conditions)}, "
            f"ordre={len(self._ordre)}, "
            f"limit={self._limit}, offset={self._offset})"
        )


__all__ = ["Requete"]
