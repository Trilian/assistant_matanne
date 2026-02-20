"""
Specifications Recettes — Filtres métier pour les recettes.

Spécifications prêtes à l'emploi pour filtrer les recettes
par temps, type, difficulté, saison, ingrédients, etc.

Usage:
    from src.services.core.specifications.recettes import (
        RecetteRapideSpec, RecetteParTypeSpec
    )

    # Recettes rapides pour le dîner
    spec = RecetteRapideSpec(30) & RecetteParTypeSpec("dîner")
    query = spec.to_query(db.query(Recette))
    recettes = query.all()
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Any

from .base import Specification

if TYPE_CHECKING:
    from sqlalchemy.orm import Query

    from src.core.models import Recette


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR TEMPS
# ═══════════════════════════════════════════════════════════


@dataclass
class RecetteRapideSpec(Specification["Recette"]):
    """
    Recettes préparables en moins de N minutes (prep + cuisson).

    Attributes:
        temps_max: Temps total maximum en minutes (défaut: 30).
    """

    temps_max: int = 30

    def is_satisfied_by(self, entity: Recette) -> bool:
        temps_prep = entity.temps_preparation or 0
        temps_cuisson = entity.temps_cuisson or 0
        return (temps_prep + temps_cuisson) <= self.temps_max

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import func

        from src.core.models import Recette

        # Calculer temps total avec COALESCE pour gérer les NULL
        temps_total = func.coalesce(Recette.temps_preparation, 0) + func.coalesce(
            Recette.temps_cuisson, 0
        )
        return query.filter(temps_total <= self.temps_max)

    def __repr__(self) -> str:
        return f"RecetteRapideSpec(temps_max={self.temps_max})"


@dataclass
class RecettePrepMaxSpec(Specification["Recette"]):
    """Recettes avec temps de préparation max."""

    temps_prep_max: int = 20

    def is_satisfied_by(self, entity: Recette) -> bool:
        return (entity.temps_preparation or 0) <= self.temps_prep_max

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import func

        from src.core.models import Recette

        return query.filter(func.coalesce(Recette.temps_preparation, 0) <= self.temps_prep_max)


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR TYPE
# ═══════════════════════════════════════════════════════════


@dataclass
class RecetteParTypeSpec(Specification["Recette"]):
    """
    Recettes d'un type de repas spécifique.

    Attributes:
        type_repas: Type de repas (petit_déjeuner, déjeuner, dîner, goûter, etc.)
    """

    type_repas: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        return entity.type_repas == self.type_repas

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Recette

        return query.filter(Recette.type_repas == self.type_repas)

    def __repr__(self) -> str:
        return f"RecetteParTypeSpec(type_repas='{self.type_repas}')"


@dataclass
class RecetteParDifficulteSpec(Specification["Recette"]):
    """
    Recettes d'un niveau de difficulté.

    Attributes:
        difficulte: Niveau (facile, moyen, difficile).
    """

    difficulte: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        return entity.difficulte == self.difficulte

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Recette

        return query.filter(Recette.difficulte == self.difficulte)


@dataclass
class RecetteParSaisonSpec(Specification["Recette"]):
    """
    Recettes adaptées à une saison.

    Attributes:
        saison: Saison (printemps, été, automne, hiver, toutes).
    """

    saison: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        if self.saison == "toutes":
            return True
        return entity.saison == self.saison or entity.saison == "toutes"

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import or_

        from src.core.models import Recette

        if self.saison == "toutes":
            return query

        return query.filter(
            or_(
                Recette.saison == self.saison,
                Recette.saison == "toutes",
                Recette.saison.is_(None),
            )
        )


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR CARACTÉRISTIQUES
# ═══════════════════════════════════════════════════════════


@dataclass
class RecetteCompatibleBebeSpec(Specification["Recette"]):
    """Recettes compatibles pour bébé."""

    compatible: bool = True

    def is_satisfied_by(self, entity: Recette) -> bool:
        if self.compatible:
            return entity.compatible_bebe is True
        return entity.compatible_bebe is not True

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Recette

        if self.compatible:
            return query.filter(Recette.compatible_bebe == True)
        return query.filter(
            (Recette.compatible_bebe == False) | (Recette.compatible_bebe.is_(None))
        )


@dataclass
class RecetteFavoriteSpec(Specification["Recette"]):
    """Recettes marquées comme favorites.

    Note: Si le champ est_favori n'existe pas dans le modèle,
    cette spec retourne toutes les recettes.
    """

    def is_satisfied_by(self, entity: Recette) -> bool:
        return getattr(entity, "est_favori", False) is True

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Recette

        # est_favori peut ne pas exister dans certains modèles
        if hasattr(Recette, "est_favori"):
            return query.filter(Recette.est_favori == True)  # noqa: E712
        return query


@dataclass
class RecetteCompatibleRobotSpec(Specification["Recette"]):
    """
    Recettes compatibles avec un robot spécifique.

    Attributes:
        robot: Nom du robot (Cookeo, Monsieur Cuisine, Airfryer, Multicooker)
    """

    robot: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        robots = entity.robots_compatibles or []
        return self.robot.lower() in [r.lower() for r in robots]

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Recette

        # Mapping robot -> colonne booléenne
        robot_columns = {
            "cookeo": "compatible_cookeo",
            "monsieur cuisine": "compatible_monsieur_cuisine",
            "airfryer": "compatible_airfryer",
            "multicooker": "compatible_multicooker",
        }

        col_name = robot_columns.get(self.robot.lower())
        if col_name and hasattr(Recette, col_name):
            return query.filter(getattr(Recette, col_name) == True)  # noqa: E712
        return query


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR INGRÉDIENTS
# ═══════════════════════════════════════════════════════════


@dataclass
class RecetteAvecIngredientSpec(Specification["Recette"]):
    """
    Recettes contenant un ingrédient spécifique.

    Attributes:
        ingredient_nom: Nom de l'ingrédient (recherche partielle).
    """

    ingredient_nom: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        # Cherche dans les ingrédients de la recette
        for ri in entity.ingredients or []:
            if self.ingredient_nom.lower() in ri.ingredient.nom.lower():
                return True
        return False

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from src.core.models import Ingredient, RecetteIngredient

        return (
            query.join(RecetteIngredient)
            .join(Ingredient)
            .filter(Ingredient.nom.ilike(f"%{self.ingredient_nom}%"))
        )


@dataclass
class RecetteSansIngredientSpec(Specification["Recette"]):
    """
    Recettes NE contenant PAS un ingrédient.

    Utile pour les allergies ou préférences.
    """

    ingredient_nom: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        for ri in entity.ingredients or []:
            if self.ingredient_nom.lower() in ri.ingredient.nom.lower():
                return False
        return True

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import not_, select

        from src.core.models import Ingredient, Recette, RecetteIngredient

        # Sous-requête: recettes qui ONT l'ingrédient
        subquery = (
            select(RecetteIngredient.recette_id)
            .join(Ingredient)
            .where(Ingredient.nom.ilike(f"%{self.ingredient_nom}%"))
        )

        return query.filter(not_(Recette.id.in_(subquery)))


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS PAR RECHERCHE TEXTUELLE
# ═══════════════════════════════════════════════════════════


@dataclass
class RecetteRechercheSpec(Specification["Recette"]):
    """
    Recherche textuelle dans nom et description.

    Attributes:
        terme: Terme de recherche.
    """

    terme: str

    def is_satisfied_by(self, entity: Recette) -> bool:
        terme = self.terme.lower()
        nom_match = terme in (entity.nom or "").lower()
        desc_match = terme in (entity.description or "").lower()
        return nom_match or desc_match

    def to_query(self, query: Query[Any]) -> Query[Any]:
        from sqlalchemy import or_

        from src.core.models import Recette

        pattern = f"%{self.terme}%"
        return query.filter(
            or_(
                Recette.nom.ilike(pattern),
                Recette.description.ilike(pattern),
            )
        )


# ═══════════════════════════════════════════════════════════
# SPÉCIFICATIONS COMPOSÉES PRÉDÉFINIES
# ═══════════════════════════════════════════════════════════


def recettes_semaine_spec(saison: str | None = None) -> Specification[Recette]:
    """
    Spécification pour les recettes du quotidien de la semaine.

    Critères: rapide (< 45 min), difficulté facile/moyen.

    Args:
        saison: Saison optionnelle pour filtrer.

    Returns:
        Specification composée.
    """
    from .base import combine_and

    specs: list[Specification[Recette]] = [
        RecetteRapideSpec(temps_max=45),
    ]

    if saison:
        specs.append(RecetteParSaisonSpec(saison))

    return combine_and(*specs)


def recettes_bebe_spec(age_mois: int = 12) -> Specification[Recette]:
    """
    Spécification pour les recettes adaptées à bébé.

    Args:
        age_mois: Âge du bébé en mois (pour filtres futurs).

    Returns:
        Specification pour recettes bébé.
    """
    return RecetteCompatibleBebeSpec(compatible=True) & RecetteRapideSpec(temps_max=30)


def obtenir_saison_actuelle() -> str:
    """Retourne la saison actuelle."""
    mois = date.today().month
    if mois in (3, 4, 5):
        return "printemps"
    elif mois in (6, 7, 8):
        return "été"
    elif mois in (9, 10, 11):
        return "automne"
    else:
        return "hiver"
