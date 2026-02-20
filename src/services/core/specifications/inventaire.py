"""
Specifications Inventaire — Filtres métier pour l'inventaire.

Spécifications pour filtrer les articles par stock, péremption,
catégorie, emplacement, alertes, etc.

Usage:
    from src.services.core.specifications.inventaire import (
        ArticleEnAlerteSpec, ArticlePeremptionProcheSpec
    )

    # Articles en alerte (stock bas OU péremption proche)
    spec = ArticleStockBas() | ArticlePeremptionProcheSpec(7)
    query = spec.to_query(db.query(ArticleInventaire))
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any

from .base import Specification

if TYPE_CHECKING:
    from sqlalchemy.orm import Query

    from src.core.models import ArticleInventaire


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR STOCK
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleStockBas(Specification["ArticleInventaire"]):
    """
    Articles avec stock inférieur au minimum.

    Attributes:
        ratio_alerte: Ratio quantite/quantite_min en dessous duquel alerter (défaut: 1.0)
    """

    ratio_alerte: float = 1.0

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        if not entity.quantite_min or entity.quantite_min == 0:  # SQLAlchemy nullable
            return False
        return entity.quantite <= (entity.quantite_min * self.ratio_alerte)

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import and_

        from src.core.models import ArticleInventaire

        return query.filter(
            and_(
                ArticleInventaire.quantite_min.isnot(None),
                ArticleInventaire.quantite_min > 0,
                ArticleInventaire.quantite <= (ArticleInventaire.quantite_min * self.ratio_alerte),
            )
        )

    def __repr__(self) -> str:
        return f"ArticleStockBas(ratio={self.ratio_alerte})"


@dataclass
class ArticleRuptureSpec(Specification["ArticleInventaire"]):
    """Articles en rupture de stock (quantité = 0)."""

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        return entity.quantite <= 0

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import ArticleInventaire

        return query.filter(ArticleInventaire.quantite <= 0)


@dataclass
class ArticleStockAbondantSpec(Specification["ArticleInventaire"]):
    """
    Articles avec stock abondant (> 3x le minimum).

    Utile pour identifier les surstocks.
    """

    ratio_abondant: float = 3.0

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        if not entity.quantite_min or entity.quantite_min == 0:  # SQLAlchemy nullable
            return entity.quantite > 10  # Seuil par défaut si pas de min
        return entity.quantite >= (entity.quantite_min * self.ratio_abondant)

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import and_, or_

        from src.core.models import ArticleInventaire

        return query.filter(
            or_(
                # Pas de min défini mais quantité > 10
                and_(
                    or_(
                        ArticleInventaire.quantite_min.is_(None),
                        ArticleInventaire.quantite_min == 0,
                    ),
                    ArticleInventaire.quantite > 10,
                ),
                # Min défini et quantité abondante
                and_(
                    ArticleInventaire.quantite_min > 0,
                    ArticleInventaire.quantite
                    >= (ArticleInventaire.quantite_min * self.ratio_abondant),
                ),
            )
        )


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR PÉREMPTION
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticlePeremptionProcheSpec(Specification["ArticleInventaire"]):
    """
    Articles avec date de péremption proche.

    Attributes:
        jours_avant: Nombre de jours avant péremption (défaut: 7).
    """

    jours_avant: int = 7

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        if entity.date_peremption is None:
            return False
        today = date.today()
        return entity.date_peremption <= (today + timedelta(days=self.jours_avant))

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import ArticleInventaire

        date_limite = date.today() + timedelta(days=self.jours_avant)
        return query.filter(
            ArticleInventaire.date_peremption.isnot(None),
            ArticleInventaire.date_peremption <= date_limite,
        )

    def __repr__(self) -> str:
        return f"ArticlePeremptionProcheSpec(jours={self.jours_avant})"


@dataclass
class ArticlePerimeSpec(Specification["ArticleInventaire"]):
    """Articles déjà périmés."""

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        if entity.date_peremption is None:
            return False
        return entity.date_peremption < date.today()

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import ArticleInventaire

        return query.filter(
            ArticleInventaire.date_peremption.isnot(None),
            ArticleInventaire.date_peremption < date.today(),
        )


@dataclass
class ArticleSansPeremptionSpec(Specification["ArticleInventaire"]):
    """Articles sans date de péremption définie."""

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        return entity.date_peremption is None

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import ArticleInventaire

        return query.filter(ArticleInventaire.date_peremption.is_(None))


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR CATÉGORIE/EMPLACEMENT
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleParCategorieSpec(Specification["ArticleInventaire"]):
    """
    Articles d'une catégorie spécifique.

    Attributes:
        categorie: Nom de la catégorie.
    """

    categorie: str

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        # La catégorie est sur l'ingrédient lié
        if entity.ingredient:
            return entity.ingredient.categorie == self.categorie
        return False

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Ingredient

        return query.join(Ingredient).filter(Ingredient.categorie == self.categorie)


@dataclass
class ArticleParEmplacementSpec(Specification["ArticleInventaire"]):
    """
    Articles d'un emplacement spécifique.

    Attributes:
        emplacement: Emplacement (Frigo, Congélateur, Placard, etc.)
    """

    emplacement: str

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        return entity.emplacement == self.emplacement

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import ArticleInventaire

        return query.filter(ArticleInventaire.emplacement == self.emplacement)


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS COMBINÉES
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleEnAlerteSpec(Specification["ArticleInventaire"]):
    """
    Articles en alerte (stock bas OU péremption proche).

    Combine ArticleStockBas et ArticlePeremptionProcheSpec.

    Attributes:
        jours_peremption: Jours avant péremption pour alerter (défaut: 7).
    """

    jours_peremption: int = 7

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        # Stock bas
        if entity.quantite_min and entity.quantite <= entity.quantite_min:
            return True

        # Péremption proche
        if entity.date_peremption:
            date_limite = date.today() + timedelta(days=self.jours_peremption)
            if entity.date_peremption <= date_limite:
                return True

        return False

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import and_, or_

        from src.core.models import ArticleInventaire

        date_limite = date.today() + timedelta(days=self.jours_peremption)

        return query.filter(
            or_(
                # Stock bas
                and_(
                    ArticleInventaire.quantite_min.isnot(None),
                    ArticleInventaire.quantite_min > 0,
                    ArticleInventaire.quantite <= ArticleInventaire.quantite_min,
                ),
                # Péremption proche
                and_(
                    ArticleInventaire.date_peremption.isnot(None),
                    ArticleInventaire.date_peremption <= date_limite,
                ),
            )
        )


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS RECHERCHE
# ═══════════════════════════════════════════════════════════


@dataclass
class ArticleRechercheSpec(Specification["ArticleInventaire"]):
    """
    Recherche textuelle dans le nom de l'ingrédient.

    Attributes:
        terme: Terme de recherche.
    """

    terme: str

    def is_satisfied_by(self, entity: ArticleInventaire) -> bool:
        if entity.ingredient:
            return self.terme.lower() in entity.ingredient.nom.lower()
        return False

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Ingredient

        return query.join(Ingredient).filter(Ingredient.nom.ilike(f"%{self.terme}%"))


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


def articles_a_acheter_spec() -> Specification[ArticleInventaire]:
    """
    Spécification pour les articles à acheter.

    Critères: stock bas OU rupture.
    """
    return ArticleStockBas(ratio_alerte=1.2) | ArticleRuptureSpec()


def articles_urgents_spec() -> Specification[ArticleInventaire]:
    """
    Spécification pour les articles urgents.

    Critères: périmé OU rupture OU péremption < 3 jours.
    """
    from .base import combine_or

    return combine_or(
        ArticlePerimeSpec(),
        ArticleRuptureSpec(),
        ArticlePeremptionProcheSpec(jours_avant=3),
    )


def articles_par_zone_spec(zone: str) -> Specification[ArticleInventaire]:
    """
    Spécification pour les articles d'une zone de stockage.

    Args:
        zone: Zone de stockage (frais, sec, congele).

    Returns:
        Specification composée.
    """
    from .base import combine_or

    zones_mapping = {
        "frais": ["Frigo"],
        "sec": ["Placard", "Garde-manger", "Cave"],
        "congele": ["Congélateur"],
    }

    emplacements = zones_mapping.get(zone, [zone])

    if len(emplacements) == 1:
        return ArticleParEmplacementSpec(emplacements[0])

    return combine_or(*[ArticleParEmplacementSpec(e) for e in emplacements])
