"""
Specification Pattern — Filtres composables et réutilisables.

Remplace les filtres ad-hoc par des objets typés combinables.
Supporte à la fois le filtrage in-memory et SQLAlchemy queries.

Usage:
    from src.services.core.specifications import Specification
    from src.services.core.specifications.recettes import (
        RecetteRapideSpec, RecetteParTypeSpec, RecetteCompatibleBebeSpec
    )

    # Composition avec opérateurs
    spec = RecetteRapideSpec(20) & RecetteParTypeSpec("dîner")
    spec = spec & ~RecetteCompatibleBebeSpec()  # NOT

    # Application à une query SQLAlchemy
    query = spec.to_query(db.query(Recette))
    recettes = query.all()

    # Ou filtrage in-memory
    recettes_filtrees = [r for r in recettes if spec.is_satisfied_by(r)]
"""

from .base import (
    AndSpecification,
    FalseSpecification,
    NotSpecification,
    OrSpecification,
    Specification,
    TrueSpecification,
)
from .inventaire import (
    ArticleEnAlerteSpec,
    ArticleParCategorieSpec,
    ArticleParEmplacementSpec,
    ArticlePeremptionProcheSpec,
    ArticleStockBas,
)
from .recettes import (
    RecetteAvecIngredientSpec,
    RecetteCompatibleBebeSpec,
    RecetteParDifficulteSpec,
    RecetteParSaisonSpec,
    RecetteParTypeSpec,
    RecetteRapideSpec,
)

__all__ = [
    # Base
    "Specification",
    "AndSpecification",
    "OrSpecification",
    "NotSpecification",
    "TrueSpecification",
    "FalseSpecification",
    # Recettes
    "RecetteRapideSpec",
    "RecetteParTypeSpec",
    "RecetteCompatibleBebeSpec",
    "RecetteParSaisonSpec",
    "RecetteParDifficulteSpec",
    "RecetteAvecIngredientSpec",
    # Inventaire
    "ArticleEnAlerteSpec",
    "ArticlePeremptionProcheSpec",
    "ArticleParCategorieSpec",
    "ArticleParEmplacementSpec",
    "ArticleStockBas",
]
