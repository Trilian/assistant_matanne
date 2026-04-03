"""
Schemas - Modèles Pydantic pour validation métier.

Usage:
    from src.core.validation.schemas import RecetteInput, ArticleCoursesInput
"""

from ._helpers import nettoyer_texte
from .courses import (
    SCHEMA_COURSES,
    ArticleCoursesInput,
)
from .famille import (
    EntreeJournalInput,
    RoutineInput,
    TacheRoutineInput,
)
from .inventaire import (
    SCHEMA_INVENTAIRE,
    ArticleInventaireInput,
    IngredientStockInput,
)
from .maison import DepenseMaisonInput
from .planning import RepasInput
from .projets import ProjetInput
from .recettes import (
    SCHEMA_RECETTE,
    EtapeInput,
    IngredientInput,
    RecetteInput,
)

__all__ = [
    # Recettes
    "IngredientInput",
    "EtapeInput",
    "RecetteInput",
    "SCHEMA_RECETTE",
    # Inventaire
    "ArticleInventaireInput",
    "IngredientStockInput",
    "SCHEMA_INVENTAIRE",
    # Courses
    "ArticleCoursesInput",
    "SCHEMA_COURSES",
    # Planning
    "RepasInput",
    # Famille
    "RoutineInput",
    "TacheRoutineInput",
    "EntreeJournalInput",
    # Projets
    "ProjetInput",
    # Maison
    "DepenseMaisonInput",
    # Helper
    "nettoyer_texte",
]
