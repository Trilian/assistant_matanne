"""
Package recettes - Services de gestion des recettes.

Ce package regroupe:
- types.py: Schemas Pydantic (RecetteSuggestion, VersionBebeGeneree, etc.)
- utils.py: Fonctions utilitaires pures (export/import, calculs, filtres)
- service.py: ServiceRecettes - CRUD, génération IA, import/export
- import_url.py: Import de recettes depuis URL (avec IA)

Imports paresseux (__getattr__) pour performance au démarrage.

Exemple d'utilisation:
    from src.services.cuisine.recettes import obtenir_service_recettes, ServiceRecettes

    service = obtenir_service_recettes()
"""

# ═══════════════════════════════════════════════════════════
# LAZY IMPORTS — Mapping symbol → (module, attr_name)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ─── Service Principal ───
    "ServiceRecettes": (".service", "ServiceRecettes"),
    "obtenir_service_recettes": (".service", "obtenir_service_recettes"),
    # ─── Types Pydantic ───
    "RecetteSuggestion": (".types", "RecetteSuggestion"),
    "VersionBebeGeneree": (".types", "VersionBebeGeneree"),
    "VersionBatchCookingGeneree": (".types", "VersionBatchCookingGeneree"),
    "VersionRobotGeneree": (".types", "VersionRobotGeneree"),
    # ─── Import URL (scraping + IA) ───
    "ImportedIngredient": (".import_url", "ImportedIngredient"),
    "ImportedRecipe": (".import_url", "ImportedRecipe"),
    "ImportResult": (".import_url", "ImportResult"),
    "RecipeParser": (".import_url", "RecipeParser"),
    "MarmitonParser": (".import_url", "MarmitonParser"),
    "CuisineAZParser": (".import_url", "CuisineAZParser"),
    "GenericRecipeParser": (".import_url", "GenericRecipeParser"),
    "RecipeImportService": (".import_url", "RecipeImportService"),
    "get_recipe_import_service": (".import_url", "get_recipe_import_service"),
    # ─── Constantes (utils.py) ───
    "DIFFICULTES": (".utils", "DIFFICULTES"),
    "TYPES_REPAS": (".utils", "TYPES_REPAS"),
    "SAISONS": (".utils", "SAISONS"),
    "ROBOTS_COMPATIBLES": (".utils", "ROBOTS_COMPATIBLES"),
    # ─── Utilitaires Export/Import ───
    "export_recettes_to_csv": (".utils", "export_recettes_to_csv"),
    "parse_csv_to_recettes": (".utils", "parse_csv_to_recettes"),
    "export_recettes_to_json": (".utils", "export_recettes_to_json"),
    "parse_json_to_recettes": (".utils", "parse_json_to_recettes"),
    # ─── Utilitaires Conversion ───
    "recette_to_dict": (".utils", "recette_to_dict"),
    "ingredient_to_dict": (".utils", "ingredient_to_dict"),
    "etape_to_dict": (".utils", "etape_to_dict"),
    # ─── Utilitaires Temps ───
    "calculer_temps_total": (".utils", "calculer_temps_total"),
    "estimer_temps_robot": (".utils", "estimer_temps_robot"),
    "formater_temps": (".utils", "formater_temps"),
    # ─── Utilitaires Portions ───
    "ajuster_quantite_ingredient": (".utils", "ajuster_quantite_ingredient"),
    "ajuster_ingredients": (".utils", "ajuster_ingredients"),
    # ─── Utilitaires Filtres ───
    "filtrer_recettes_par_temps": (".utils", "filtrer_recettes_par_temps"),
    "filtrer_recettes_par_difficulte": (".utils", "filtrer_recettes_par_difficulte"),
    "filtrer_recettes_par_type": (".utils", "filtrer_recettes_par_type"),
    "filtrer_recettes_par_saison": (".utils", "filtrer_recettes_par_saison"),
    "rechercher_par_nom": (".utils", "rechercher_par_nom"),
    "rechercher_par_ingredient": (".utils", "rechercher_par_ingredient"),
    # ─── Utilitaires Statistiques ───
    "calculer_stats_recettes": (".utils", "calculer_stats_recettes"),
    "calculer_score_recette": (".utils", "calculer_score_recette"),
    # ─── Utilitaires Validation ───
    "valider_difficulte": (".utils", "valider_difficulte"),
    "valider_type_repas": (".utils", "valider_type_repas"),
    "valider_temps": (".utils", "valider_temps"),
    "valider_portions": (".utils", "valider_portions"),
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
