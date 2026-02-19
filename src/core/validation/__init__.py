"""
Validation - Module de validation et sanitization.

Ce module fournit:
- Sanitization contre XSS et injections SQL
- Modèles Pydantic pour validation métier
- Schémas de validation pour formulaires
- Helpers et décorateurs de validation
"""

from ..constants import (
    MAX_ETAPES,
    MAX_INGREDIENTS,
    MAX_LENGTH_LONG,
    MAX_LENGTH_MEDIUM,
    MAX_LENGTH_SHORT,
    MAX_LENGTH_TEXT,
    MAX_PORTIONS,
    MAX_QUANTITE,
    MAX_TEMPS_CUISSON,
    MAX_TEMPS_PREPARATION,
    MIN_ETAPES,
    MIN_INGREDIENTS,
)
from .sanitizer import NettoyeurEntrees
from .schemas import (
    # Schémas dict
    SCHEMA_COURSES,
    SCHEMA_INVENTAIRE,
    SCHEMA_RECETTE,
    # Courses
    ArticleCoursesInput,
    # Inventaire
    ArticleInventaireInput,
    # Famille
    EntreeJournalInput,
    # Recettes
    EtapeInput,
    IngredientInput,
    IngredientStockInput,
    ProjetInput,
    RecetteInput,
    # Planning
    RepasInput,
    RoutineInput,
    TacheRoutineInput,
    # Helpers
    nettoyer_texte,
)
from .validators import (
    afficher_erreurs_validation,
    valider_entree,
    valider_et_nettoyer_formulaire,
    valider_formulaire_streamlit,
    valider_modele,
)

__all__ = [
    # Sanitizer
    "NettoyeurEntrees",
    # Helpers
    "nettoyer_texte",
    # Constantes
    "MAX_LENGTH_SHORT",
    "MAX_LENGTH_MEDIUM",
    "MAX_LENGTH_LONG",
    "MAX_LENGTH_TEXT",
    # Schemas Pydantic - Recettes
    "IngredientInput",
    "EtapeInput",
    "RecetteInput",
    # Schemas Pydantic - Inventaire
    "ArticleInventaireInput",
    "IngredientStockInput",
    # Schemas Pydantic - Courses
    "ArticleCoursesInput",
    # Schemas Pydantic - Planning
    "RepasInput",
    # Schemas Pydantic - Famille
    "RoutineInput",
    "TacheRoutineInput",
    "EntreeJournalInput",
    "ProjetInput",
    # Schémas dict
    "SCHEMA_RECETTE",
    "SCHEMA_INVENTAIRE",
    "SCHEMA_COURSES",
    # Validators
    "valider_modele",
    "valider_formulaire_streamlit",
    "valider_et_nettoyer_formulaire",
    "afficher_erreurs_validation",
    "valider_entree",
]
