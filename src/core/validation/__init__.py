"""
Validation - Module de validation et sanitization.

Ce module fournit:
- Sanitization contre XSS et injections SQL
- Modèles Pydantic pour validation métier
- Schémas de validation pour formulaires
- Helpers et décorateurs de validation
"""

from .sanitizer import InputSanitizer, NettoyeurEntrees
from .schemas import (
    # Constantes
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
    # Alias anglais
    show_validation_errors,
    validate_and_sanitize_form,
    validate_input,
    validate_model,
    validate_streamlit_form,
    valider_entree,
    valider_et_nettoyer_formulaire,
    valider_formulaire_streamlit,
    valider_modele,
)

__all__ = [
    # Sanitizer
    "NettoyeurEntrees",
    "InputSanitizer",
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
    # Alias anglais
    "validate_model",
    "validate_streamlit_form",
    "validate_and_sanitize_form",
    "show_validation_errors",
    "validate_input",
]
