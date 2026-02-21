"""
Specifications — Pattern Specification pour requêtes composables.

Permet de construire des critères de filtrage composables et
réutilisables pour les requêtes de base de données.

Usage::

    from src.core.specifications import Specification, Et, Ou, Non

    # Spécifications basiques
    active = Spec(lambda q, m: q.where(m.actif == True))
    saison = Spec(lambda q, m: q.where(m.saison == "été"))

    # Composition
    recettes_ete = active & saison  # ET logique
    pas_ete = ~saison               # NON logique
    tout = active | saison          # OU logique

    # Utilisation avec Repository
    repo.lister(spec=recettes_ete)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy import Select

T = TypeVar("T")

# Type d'une fonction qui modifie un statement SELECT
SpecFn = Callable[[Select, type[Any]], Select]


class Specification(ABC):
    """
    Spécification abstraite composable.

    Chaque spécification sait comment modifier un ``Select`` SQLAlchemy
    pour ajouter ses contraintes. Les spécifications peuvent être
    composées via les opérateurs ``&`` (ET), ``|`` (OU) et ``~`` (NON).
    """

    @abstractmethod
    def appliquer(self, stmt: Select, model: type[Any]) -> Select:
        """
        Applique la spécification au statement SELECT.

        Args:
            stmt: Statement SQLAlchemy à modifier
            model: Classe du modèle ORM

        Returns:
            Statement modifié avec les contraintes ajoutées
        """
        ...

    def __and__(self, other: Specification) -> Et:
        """Composition ET: ``spec_a & spec_b``."""
        return Et(self, other)

    def __or__(self, other: Specification) -> Ou:
        """Composition OU: ``spec_a | spec_b``."""
        return Ou(self, other)

    def __invert__(self) -> Non:
        """Négation: ``~spec``."""
        return Non(self)


class Spec(Specification):
    """
    Spécification à partir d'une fonction lambda.

    Wrapper pratique pour créer des spécifications inline::

        active = Spec(lambda q, m: q.where(m.actif == True))

    Args:
        fn: Fonction (stmt, model) → stmt modifié
        description: Description lisible (pour debug)
    """

    def __init__(self, fn: SpecFn, description: str = ""):
        self._fn = fn
        self._description = description

    def appliquer(self, stmt: Select, model: type[Any]) -> Select:
        return self._fn(stmt, model)

    def __repr__(self) -> str:
        return f"Spec({self._description or '?'})"


class Et(Specification):
    """Composition ET de deux spécifications."""

    def __init__(self, gauche: Specification, droite: Specification):
        self._gauche = gauche
        self._droite = droite

    def appliquer(self, stmt: Select, model: type[Any]) -> Select:
        stmt = self._gauche.appliquer(stmt, model)
        stmt = self._droite.appliquer(stmt, model)
        return stmt

    def __repr__(self) -> str:
        return f"({self._gauche!r} & {self._droite!r})"


class Ou(Specification):
    """
    Composition OU de deux spécifications.

    Extrait les clauses WHERE individuelles de chaque spec et les combine
    avec ``or_()`` SQLAlchemy pour un vrai OU logique SQL.
    """

    def __init__(self, gauche: Specification, droite: Specification):
        self._gauche = gauche
        self._droite = droite

    def appliquer(self, stmt: Select, model: type[Any]) -> Select:
        from sqlalchemy import or_, select

        # Créer des statements vierges pour capturer les clauses WHERE de chaque spec
        stmt_gauche = select(model)
        stmt_droite = select(model)

        stmt_gauche = self._gauche.appliquer(stmt_gauche, model)
        stmt_droite = self._droite.appliquer(stmt_droite, model)

        # Extraire les clauses whereclause de chaque statement
        clauses = []
        if stmt_gauche.whereclause is not None:
            clauses.append(stmt_gauche.whereclause)
        if stmt_droite.whereclause is not None:
            clauses.append(stmt_droite.whereclause)

        if len(clauses) == 2:
            return stmt.where(or_(*clauses))
        elif len(clauses) == 1:
            return stmt.where(clauses[0])
        return stmt

    def __repr__(self) -> str:
        return f"({self._gauche!r} | {self._droite!r})"


class Non(Specification):
    """
    Négation d'une spécification.

    Applique la spec sur un statement vierge, extrait la clause WHERE,
    puis l'inverse avec ``not_()`` SQLAlchemy.
    """

    def __init__(self, spec: Specification):
        self._spec = spec

    def appliquer(self, stmt: Select, model: type[Any]) -> Select:
        from sqlalchemy import not_, select

        # Créer un statement vierge pour capturer la clause WHERE de la spec
        stmt_inner = select(model)
        stmt_inner = self._spec.appliquer(stmt_inner, model)

        # Extraire et nier la clause
        if stmt_inner.whereclause is not None:
            return stmt.where(not_(stmt_inner.whereclause))
        return stmt

    def __repr__(self) -> str:
        return f"~{self._spec!r}"


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════


def par_champ(nom_champ: str, valeur: Any) -> Spec:
    """
    Spécification: filtre par égalité sur un champ.

    Usage:
        actif = par_champ("actif", True)

    Args:
        nom_champ: Nom de la colonne
        valeur: Valeur attendue
    """
    return Spec(
        lambda q, m: q.where(getattr(m, nom_champ) == valeur),
        description=f"{nom_champ}=={valeur!r}",
    )


def par_champs(**kwargs: Any) -> Spec:
    """
    Spécification: filtre par égalité sur plusieurs champs.

    Usage:
        spec = par_champs(actif=True, saison="été")
    """

    def appliquer(q: Select, m: type) -> Select:
        for nom, val in kwargs.items():
            col = getattr(m, nom, None)
            if col is not None:
                q = q.where(col == val)
        return q

    return Spec(appliquer, description=f"champs={kwargs}")


def contient(nom_champ: str, texte: str) -> Spec:
    """
    Spécification: recherche textuelle (ILIKE).

    Usage:
        chercher = contient("nom", "tarte")
    """
    return Spec(
        lambda q, m: q.where(getattr(m, nom_champ).ilike(f"%{texte}%")),
        description=f"{nom_champ} ILIKE '%{texte}%'",
    )


def entre(nom_champ: str, min_val: Any, max_val: Any) -> Spec:
    """
    Spécification: valeur dans un intervalle.

    Usage:
        prix_abordable = entre("prix", 5, 20)
    """
    return Spec(
        lambda q, m: q.where(getattr(m, nom_champ).between(min_val, max_val)),
        description=f"{nom_champ} BETWEEN {min_val} AND {max_val}",
    )


def ordre_par(nom_champ: str, descendant: bool = False) -> Spec:
    """
    Spécification: tri par colonne.

    Usage:
        recent = ordre_par("created_at", descendant=True)
    """

    def appliquer(q: Select, m: type) -> Select:
        col = getattr(m, nom_champ, None)
        if col is not None:
            return q.order_by(col.desc() if descendant else col.asc())
        return q

    return Spec(appliquer, description=f"ORDER BY {nom_champ} {'DESC' if descendant else 'ASC'}")


def limite(n: int) -> Spec:
    """Spécification: limite le nombre de résultats."""
    return Spec(
        lambda q, m: q.limit(n),
        description=f"LIMIT {n}",
    )


def paginer(page: int, par_page: int = 20) -> Spec:
    """
    Spécification: pagination.

    Usage:
        page_2 = paginer(page=2, par_page=20)
    """
    offset = (page - 1) * par_page
    return Spec(
        lambda q, m: q.limit(par_page).offset(offset),
        description=f"PAGE {page} ({par_page}/page)",
    )


__all__ = [
    "Specification",
    "Spec",
    "Et",
    "Ou",
    "Non",
    "par_champ",
    "par_champs",
    "contient",
    "entre",
    "ordre_par",
    "limite",
    "paginer",
]
