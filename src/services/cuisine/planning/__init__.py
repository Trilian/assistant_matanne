"""
Package Planning - Services de gestion du planning familial.

Ce package fournit:
- ServicePlanning: Gestion du planning repas hebdomadaire avec IA
- ServicePlanningUnifie: Agrégation complète (repas, activités, projets, routines)
- Types Pydantic: Schémas de validation pour tous les modèles planning
- Utilitaires: Fonctions pures pour dates, équilibre, formatage

Imports paresseux (__getattr__) pour performance au démarrage.

Utilisation:
    ```python
    from src.services.cuisine.planning import obtenir_service_planning, ServicePlanning

    service = obtenir_service_planning()
    planning = service.get_planning()
    ```
"""

# ═══════════════════════════════════════════════════════════
# LAZY IMPORTS — Mapping symbol → (module, attr_name)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ─── Types & Schémas (types.py) ───
    "JourPlanning": (".types", "JourPlanning"),
    "SuggestionRecettesDay": (".types", "SuggestionRecettesDay"),
    "ParametresEquilibre": (".types", "ParametresEquilibre"),
    "JourCompletSchema": (".types", "JourCompletSchema"),
    "SemaineCompleSchema": (".types", "SemaineCompleSchema"),
    "SemaineGenereeIASchema": (".types", "SemaineGenereeIASchema"),
    # ─── Constantes (src.core.constants) ───
    "JOURS_SEMAINE": ("src.core.constants", "JOURS_SEMAINE"),
    "JOURS_SEMAINE_LOWER": ("src.core.constants", "JOURS_SEMAINE_LOWER"),
    "TYPES_PROTEINES": ("src.core.constants", "TYPES_PROTEINES"),
    "TYPES_REPAS": ("src.core.constants", "TYPES_REPAS_KEYS"),
    # ─── Service Planning (service.py) ───
    "ServicePlanning": (".service", "ServicePlanning"),
    "PlanningService": (".service", "ServicePlanning"),
    "obtenir_service_planning": (".service", "obtenir_service_planning"),
    # ─── Service Planning Unifié (global_planning.py) ───
    "ServicePlanningUnifie": (".global_planning", "ServicePlanningUnifie"),
    "obtenir_service_planning_unifie": (".global_planning", "obtenir_service_planning_unifie"),
    # ─── Service Rappels (rappels.py) ───
    "OPTIONS_RAPPEL": (".rappels", "OPTIONS_RAPPEL"),
    "ServiceRappels": (".rappels", "ServiceRappels"),
    "format_rappel": (".rappels", "format_rappel"),
    "obtenir_service_rappels": (".rappels", "obtenir_service_rappels"),
    # ─── Service Récurrence (recurrence.py) ───
    "JOURS_SEMAINE_RECURRENCE": (".recurrence", "JOURS_SEMAINE_INDEX"),
    "OPTIONS_RECURRENCE": (".recurrence", "OPTIONS_RECURRENCE"),
    "ServiceRecurrence": (".recurrence", "ServiceRecurrence"),
    "TypeRecurrence": (".recurrence", "TypeRecurrence"),
    "format_recurrence": (".recurrence", "format_recurrence"),
    "obtenir_service_recurrence": (".recurrence", "obtenir_service_recurrence"),
    # ─── Service Templates (templates.py) ───
    "ServiceTemplates": (".templates", "ServiceTemplates"),
    "obtenir_service_templates": (".templates", "obtenir_service_templates"),
    # ─── Utilitaires (utils.py) ───
    "get_weekday_names": (".utils", "get_weekday_names"),
    "get_weekday_name": (".utils", "get_weekday_name"),
    "get_weekday_index": (".utils", "get_weekday_index"),
    "calculate_week_dates": (".utils", "calculate_week_dates"),
    "get_week_range": (".utils", "get_week_range"),
    "get_monday_of_week": (".utils", "get_monday_of_week"),
    "format_week_label": (".utils", "format_week_label"),
    "determine_protein_type": (".utils", "determine_protein_type"),
    "get_default_protein_schedule": (".utils", "get_default_protein_schedule"),
    "calculate_week_balance": (".utils", "calculate_week_balance"),
    "is_balanced_week": (".utils", "is_balanced_week"),
    "format_meal_for_display": (".utils", "format_meal_for_display"),
    "format_planning_summary": (".utils", "format_planning_summary"),
    "group_meals_by_type": (".utils", "group_meals_by_type"),
    "aggregate_ingredients": (".utils", "aggregate_ingredients"),
    "sort_ingredients_by_rayon": (".utils", "sort_ingredients_by_rayon"),
    "get_rayon_order": (".utils", "get_rayon_order"),
    "validate_planning_dates": (".utils", "validate_planning_dates"),
    "validate_meal_selection": (".utils", "validate_meal_selection"),
    "build_planning_prompt_context": (".utils", "build_planning_prompt_context"),
    "parse_ai_planning_response": (".utils", "parse_ai_planning_response"),
}


def __getattr__(name: str):
    """Lazy import pour performance au démarrage."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        import importlib

        if module_path.startswith("."):
            mod = importlib.import_module(module_path, package=__name__)
        else:
            mod = importlib.import_module(module_path)
        return getattr(mod, attr_name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = list(_LAZY_IMPORTS.keys())
