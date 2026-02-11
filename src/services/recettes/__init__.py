"""
Package recettes - Services de gestion des recettes.

Ce package regroupe:
- types.py: Schemas Pydantic (RecetteSuggestion, VersionBebeGeneree, etc.)
- utils.py: Fonctions utilitaires pures (export/import, calculs, filtres)
- service.py: ServiceRecettes - CRUD, génération IA, import/export

Exemple d'utilisation:
    from src.services.recettes import obtenir_service_recettes, ServiceRecettes
    
    # Obtenir le service singleton
    service = obtenir_service_recettes()
    
    # Créer une recette
    recette = service.create_complete({
        "nom": "Poulet rôti",
        "temps_preparation": 15,
        "temps_cuisson": 60,
        "portions": 4,
        "difficulte": "facile",
        "type_repas": "diner",
    })
    
    # Générer des suggestions IA
    suggestions = service.generer_recettes_ia(
        type_repas="diner",
        saison="hiver",
        nb_recettes=3,
    )
"""

# Types et schemas Pydantic
from .types import (
    RecetteSuggestion,
    VersionBebeGeneree,
    VersionBatchCookingGeneree,
    VersionRobotGeneree,
    # Aliases anglais
    RecipeSuggestion,
    BabyVersionGenerated,
    BatchCookingVersionGenerated,
    RobotVersionGenerated,
)

# Fonctions utilitaires
from .utils import (
    # Constantes
    DIFFICULTES,
    TYPES_REPAS,
    SAISONS,
    ROBOTS_COMPATIBLES,
    # Export CSV
    export_recettes_to_csv,
    parse_csv_to_recettes,
    # Export JSON
    export_recettes_to_json,
    parse_json_to_recettes,
    # Conversion
    recette_to_dict,
    ingredient_to_dict,
    etape_to_dict,
    # Temps
    calculer_temps_total,
    estimer_temps_robot,
    formater_temps,
    # Portions
    ajuster_quantite_ingredient,
    ajuster_ingredients,
    # Filtres
    filtrer_recettes_par_temps,
    filtrer_recettes_par_difficulte,
    filtrer_recettes_par_type,
    filtrer_recettes_par_saison,
    rechercher_par_nom,
    rechercher_par_ingredient,
    # Stats
    calculer_stats_recettes,
    calculer_score_recette,
    # Validation
    valider_difficulte,
    valider_type_repas,
    valider_temps,
    valider_portions,
)

# Service principal
from .service import (
    ServiceRecettes,
    obtenir_service_recettes,
    # Aliases pour compatibilité
    RecetteService,
    get_recette_service,
    recette_service,
)

# Import URL (scraping)
from .import_url import (
    # Schemas
    ImportedIngredient,
    ImportedRecipe,
    ImportResult,
    # Parsers
    RecipeParser,
    MarmitonParser,
    CuisineAZParser,
    GenericRecipeParser,
    # Service
    RecipeImportService,
    get_recipe_import_service,
    render_import_recipe_ui,
)


__all__ = [
    # ═══════════════════════════════════════════════════════════
    # SERVICE PRINCIPAL
    # ═══════════════════════════════════════════════════════════
    "ServiceRecettes",
    "obtenir_service_recettes",
    # Aliases pour compatibilité
    "RecetteService",
    "get_recette_service",
    "recette_service",
    
    # ═══════════════════════════════════════════════════════════
    # TYPES PYDANTIC
    # ═══════════════════════════════════════════════════════════
    "RecetteSuggestion",
    "VersionBebeGeneree",
    "VersionBatchCookingGeneree",
    "VersionRobotGeneree",
    # Aliases anglais
    "RecipeSuggestion",
    "BabyVersionGenerated",
    "BatchCookingVersionGenerated",
    "RobotVersionGenerated",
    
    # ═══════════════════════════════════════════════════════════
    # CONSTANTES
    # ═══════════════════════════════════════════════════════════
    "DIFFICULTES",
    "TYPES_REPAS",
    "SAISONS",
    "ROBOTS_COMPATIBLES",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - EXPORT/IMPORT
    # ═══════════════════════════════════════════════════════════
    "export_recettes_to_csv",
    "parse_csv_to_recettes",
    "export_recettes_to_json",
    "parse_json_to_recettes",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - CONVERSION
    # ═══════════════════════════════════════════════════════════
    "recette_to_dict",
    "ingredient_to_dict",
    "etape_to_dict",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - TEMPS
    # ═══════════════════════════════════════════════════════════
    "calculer_temps_total",
    "estimer_temps_robot",
    "formater_temps",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - PORTIONS
    # ═══════════════════════════════════════════════════════════
    "ajuster_quantite_ingredient",
    "ajuster_ingredients",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - FILTRES
    # ═══════════════════════════════════════════════════════════
    "filtrer_recettes_par_temps",
    "filtrer_recettes_par_difficulte",
    "filtrer_recettes_par_type",
    "filtrer_recettes_par_saison",
    "rechercher_par_nom",
    "rechercher_par_ingredient",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - STATISTIQUES
    # ═══════════════════════════════════════════════════════════
    "calculer_stats_recettes",
    "calculer_score_recette",
    
    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES - VALIDATION
    # ═══════════════════════════════════════════════════════════
    "valider_difficulte",
    "valider_type_repas",
    "valider_temps",
    "valider_portions",
    
    # ═══════════════════════════════════════════════════════════
    # IMPORT URL (SCRAPING)
    # ═══════════════════════════════════════════════════════════
    # Schemas
    "ImportedIngredient",
    "ImportedRecipe",
    "ImportResult",
    # Parsers
    "RecipeParser",
    "MarmitonParser",
    "CuisineAZParser",
    "GenericRecipeParser",
    # Service
    "RecipeImportService",
    "get_recipe_import_service",
    "render_import_recipe_ui",
]
