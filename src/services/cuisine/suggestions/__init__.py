"""
Package de suggestions IA pour la planification de repas.

Ce package fournit des suggestions intelligentes basées sur:
- Historique des recettes consultées/préparées
- Préférences détectées automatiquement
- Saisons et disponibilité des ingrédients
- Retours utilisateur (likes/dislikes)

Imports paresseux (__getattr__) pour performance au démarrage.

Exemple d'utilisation:
    >>> from src.services.cuisine.suggestions import obtenir_service_suggestions
    >>> service = obtenir_service_suggestions()
    >>> suggestions = service.suggerer_recettes(nb_suggestions=5)
"""

# ═══════════════════════════════════════════════════════════
# LAZY IMPORTS — Mapping symbol → (module, attr_name)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ─── Types / Schémas ───
    "ProfilCulinaire": (".types", "ProfilCulinaire"),
    "ContexteSuggestion": (".types", "ContexteSuggestion"),
    "SuggestionRecette": (".types", "SuggestionRecette"),
    # ─── Service principal ───
    "ServiceSuggestions": (".service", "ServiceSuggestions"),
    "obtenir_service_suggestions": (".service", "obtenir_service_suggestions"),
    # ─── Constantes ───
    "SAISONS": (".constantes_suggestions", "SAISONS"),
    "INGREDIENTS_SAISON": (".constantes_suggestions", "INGREDIENTS_SAISON"),
    "PROTEINES_POISSON": (".constantes_suggestions", "PROTEINES_POISSON"),
    "PROTEINES_VIANDE_ROUGE": (".constantes_suggestions", "PROTEINES_VIANDE_ROUGE"),
    "PROTEINES_VOLAILLE": (".constantes_suggestions", "PROTEINES_VOLAILLE"),
    "PROTEINES_VEGETARIEN": (".constantes_suggestions", "PROTEINES_VEGETARIEN"),
    "SCORE_INGREDIENT_DISPONIBLE": (".constantes_suggestions", "SCORE_INGREDIENT_DISPONIBLE"),
    "SCORE_INGREDIENT_PRIORITAIRE": (".constantes_suggestions", "SCORE_INGREDIENT_PRIORITAIRE"),
    "SCORE_INGREDIENT_SAISON": (".constantes_suggestions", "SCORE_INGREDIENT_SAISON"),
    "SCORE_CATEGORIE_PREFEREE": (".constantes_suggestions", "SCORE_CATEGORIE_PREFEREE"),
    "SCORE_JAMAIS_PREPAREE": (".constantes_suggestions", "SCORE_JAMAIS_PREPAREE"),
    "SCORE_DIFFICULTE_ADAPTEE": (".constantes_suggestions", "SCORE_DIFFICULTE_ADAPTEE"),
    "SCORE_TEMPS_ADAPTE": (".constantes_suggestions", "SCORE_TEMPS_ADAPTE"),
    "SCORE_VARIETE": (".constantes_suggestions", "SCORE_VARIETE"),
    # ─── Fonctions saison ───
    "get_current_season": (".saisons", "get_current_season"),
    "get_seasonal_ingredients": (".saisons", "get_seasonal_ingredients"),
    "is_ingredient_in_season": (".saisons", "is_ingredient_in_season"),
    # ─── Analyse historique ───
    "analyze_categories": (".analyse_historique", "analyze_categories"),
    "analyze_frequent_ingredients": (".analyse_historique", "analyze_frequent_ingredients"),
    "calculate_average_difficulty": (".analyse_historique", "calculate_average_difficulty"),
    "calculate_average_time": (".analyse_historique", "calculate_average_time"),
    "calculate_average_portions": (".analyse_historique", "calculate_average_portions"),
    "identify_favorites": (".analyse_historique", "identify_favorites"),
    "days_since_last_preparation": (".analyse_historique", "days_since_last_preparation"),
    # ─── Scoring ───
    "calculate_recipe_score": (".scoring", "calculate_recipe_score"),
    "rank_recipes": (".scoring", "rank_recipes"),
    "generate_suggestion_reason": (".scoring", "generate_suggestion_reason"),
    # ─── Équilibre et variété ───
    "detect_protein_type": (".equilibre", "detect_protein_type"),
    "calculate_week_protein_balance": (".equilibre", "calculate_week_protein_balance"),
    "is_week_balanced": (".equilibre", "is_week_balanced"),
    "calculate_variety_score": (".equilibre", "calculate_variety_score"),
    "get_least_prepared_recipes": (".equilibre", "get_least_prepared_recipes"),
    # ─── Formatage ───
    "format_suggestion": (".formatage", "format_suggestion"),
    "format_profile_summary": (".formatage", "format_profile_summary"),
    "filter_by_constraints": (".formatage", "filter_by_constraints"),
    # ─── Prédictions ML ───
    "PredictionArticle": (".predictions", "PredictionArticle"),
    "AnalysePrediction": (".predictions", "AnalysePrediction"),
    "PredictionService": (".predictions", "PredictionService"),
    "obtenir_service_predictions": (".predictions", "obtenir_service_predictions"),
}


def __getattr__(name: str):
    """Lazy import pour performance au démarrage."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        import importlib

        mod = importlib.import_module(module_path, package=__name__)
        return getattr(mod, attr_name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
