"""
Package de suggestions IA pour la planification de repas.

Ce package fournit des suggestions intelligentes basées sur:
- Historique des recettes consultées/préparées
- Préférences détectées automatiquement
- Saisons et disponibilité des ingrédients
- Retours utilisateur (likes/dislikes)

Structure:
- types.py: Schémas Pydantic (ProfilCulinaire, ContexteSuggestion, SuggestionRecette)
- utils.py: Fonctions utilitaires pures (saison, scoring, protéines, variété)
- service.py: ServiceSuggestions avec intégration IA

Exemple d'utilisation:
    >>> from src.services.suggestions import obtenir_service_suggestions
    >>> service = obtenir_service_suggestions()
    >>> suggestions = service.suggerer_recettes(nb_suggestions=5)
"""

# Types/Schémas
# Prédictions ML (inventaire)
from .predictions import (
    AnalysePrediction,
    PredictionArticle,
    PredictionService,
    obtenir_service_predictions,
)

# Service principal
from .service import (
    ServiceSuggestions,
    # Alias de compatibilité
    SuggestionsIAService,
    get_suggestions_ia_service,
    obtenir_service_suggestions,
)
from .types import (
    ContexteSuggestion,
    ProfilCulinaire,
    SuggestionRecette,
)

# Fonctions utilitaires
from .utils import (
    INGREDIENTS_SAISON,
    PROTEINES_POISSON,
    PROTEINES_VEGETARIEN,
    PROTEINES_VIANDE_ROUGE,
    PROTEINES_VOLAILLE,
    # Constantes
    SAISONS,
    SCORE_CATEGORIE_PREFEREE,
    SCORE_DIFFICULTE_ADAPTEE,
    SCORE_INGREDIENT_DISPONIBLE,
    SCORE_INGREDIENT_PRIORITAIRE,
    SCORE_INGREDIENT_SAISON,
    SCORE_JAMAIS_PREPAREE,
    SCORE_TEMPS_ADAPTE,
    SCORE_VARIETE,
    # Fonctions profil
    analyze_categories,
    analyze_frequent_ingredients,
    calculate_average_difficulty,
    calculate_average_portions,
    calculate_average_time,
    # Fonctions scoring
    calculate_recipe_score,
    # Fonctions variété
    calculate_variety_score,
    calculate_week_protein_balance,
    days_since_last_preparation,
    # Fonctions protéines
    detect_protein_type,
    filter_by_constraints,
    format_profile_summary,
    # Fonctions formatage
    format_suggestion,
    generate_suggestion_reason,
    # Fonctions saison
    get_current_season,
    get_least_prepared_recipes,
    get_seasonal_ingredients,
    identify_favorites,
    is_ingredient_in_season,
    is_week_balanced,
    rank_recipes,
)

__all__ = [
    # Types/Schémas
    "ProfilCulinaire",
    "ContexteSuggestion",
    "SuggestionRecette",
    # Service principal
    "ServiceSuggestions",
    "obtenir_service_suggestions",
    # Alias de compatibilité
    "SuggestionsIAService",
    "get_suggestions_ia_service",
    # Constantes
    "SAISONS",
    "INGREDIENTS_SAISON",
    "PROTEINES_POISSON",
    "PROTEINES_VIANDE_ROUGE",
    "PROTEINES_VOLAILLE",
    "PROTEINES_VEGETARIEN",
    "SCORE_INGREDIENT_DISPONIBLE",
    "SCORE_INGREDIENT_PRIORITAIRE",
    "SCORE_INGREDIENT_SAISON",
    "SCORE_CATEGORIE_PREFEREE",
    "SCORE_JAMAIS_PREPAREE",
    "SCORE_DIFFICULTE_ADAPTEE",
    "SCORE_TEMPS_ADAPTE",
    "SCORE_VARIETE",
    # Fonctions saison
    "get_current_season",
    "get_seasonal_ingredients",
    "is_ingredient_in_season",
    # Fonctions profil
    "analyze_categories",
    "analyze_frequent_ingredients",
    "calculate_average_difficulty",
    "calculate_average_time",
    "calculate_average_portions",
    "identify_favorites",
    "days_since_last_preparation",
    # Fonctions scoring
    "calculate_recipe_score",
    "rank_recipes",
    "generate_suggestion_reason",
    # Fonctions protéines
    "detect_protein_type",
    "calculate_week_protein_balance",
    "is_week_balanced",
    # Fonctions variété
    "calculate_variety_score",
    "get_least_prepared_recipes",
    # Fonctions formatage
    "format_suggestion",
    "format_profile_summary",
    "filter_by_constraints",
    # Prédictions ML
    "PredictionArticle",
    "AnalysePrediction",
    "PredictionService",
    "obtenir_service_predictions",
]
