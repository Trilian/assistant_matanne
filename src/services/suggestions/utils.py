"""
Hub de réexportation pour les utilitaires de suggestions de recettes.

Ce module regroupe et réexporte toutes les fonctions et constantes depuis
les sous-modules spécialisés pour maintenir la rétrocompatibilité des imports.

Sous-modules:
    - constantes_suggestions: Constantes (saisons, protéines, scores)
    - saisons: Fonctions de saisonnalité
    - analyse_historique: Analyse du profil culinaire
    - scoring: Scoring et classement des recettes
    - equilibre: Équilibre protéique et variété
    - formatage: Formatage et filtrage
"""

from src.services.suggestions.analyse_historique import (  # noqa: F401
    analyze_categories,
    analyze_frequent_ingredients,
    calculate_average_difficulty,
    calculate_average_portions,
    calculate_average_time,
    days_since_last_preparation,
    identify_favorites,
)
from src.services.suggestions.constantes_suggestions import (  # noqa: F401
    INGREDIENTS_SAISON,
    PROTEINES_POISSON,
    PROTEINES_VEGETARIEN,
    PROTEINES_VIANDE_ROUGE,
    PROTEINES_VOLAILLE,
    SAISONS,
    SCORE_CATEGORIE_PREFEREE,
    SCORE_DIFFICULTE_ADAPTEE,
    SCORE_INGREDIENT_DISPONIBLE,
    SCORE_INGREDIENT_PRIORITAIRE,
    SCORE_INGREDIENT_SAISON,
    SCORE_JAMAIS_PREPAREE,
    SCORE_TEMPS_ADAPTE,
    SCORE_VARIETE,
)
from src.services.suggestions.equilibre import (  # noqa: F401
    calculate_variety_score,
    calculate_week_protein_balance,
    detect_protein_type,
    get_least_prepared_recipes,
    is_week_balanced,
)
from src.services.suggestions.formatage import (  # noqa: F401
    filter_by_constraints,
    format_profile_summary,
    format_suggestion,
)
from src.services.suggestions.saisons import (  # noqa: F401
    get_current_season,
    get_seasonal_ingredients,
    is_ingredient_in_season,
)
from src.services.suggestions.scoring import (  # noqa: F401
    calculate_recipe_score,
    generate_suggestion_reason,
    rank_recipes,
)

__all__ = [
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
]
