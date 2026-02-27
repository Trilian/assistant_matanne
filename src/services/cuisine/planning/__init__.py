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
    # ─── Service Rappels (delegated to central planning) ───
    "OPTIONS_RAPPEL": (".rappels", "OPTIONS_RAPPEL"),
    "ServiceRappels": ("src.services.planning.rappels", "ServiceRappels"),
    "format_rappel": (".rappels", "format_rappel"),
    "obtenir_service_rappels": ("src.services.planning.rappels", "obtenir_service_rappels"),
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
    # ─── Utilitaires dates (src.core.date_utils) ───
    "obtenir_noms_jours_semaine": ("src.core.date_utils.helpers", "obtenir_noms_jours_semaine"),
    "obtenir_nom_jour_semaine": ("src.core.date_utils.helpers", "obtenir_nom_jour_semaine"),
    "obtenir_index_jour_semaine": ("src.core.date_utils.helpers", "obtenir_index_jour_semaine"),
    "get_weekday_names": ("src.core.date_utils.helpers", "get_weekday_names"),  # Alias rétrocompat
    "get_weekday_name": ("src.core.date_utils.helpers", "get_weekday_name"),  # Alias rétrocompat
    "get_weekday_index": ("src.core.date_utils.helpers", "get_weekday_index"),  # Alias rétrocompat
    "calculate_week_dates": ("src.core.date_utils.semaines", "obtenir_jours_semaine"),
    "get_week_range": ("src.core.date_utils.semaines", "obtenir_bornes_semaine"),
    "get_monday_of_week": ("src.core.date_utils.semaines", "obtenir_debut_semaine"),
    "formater_label_semaine": ("src.core.date_utils.formatage", "formater_label_semaine"),
    "format_week_label": (
        "src.core.date_utils.formatage",
        "format_week_label",
    ),  # Alias rétrocompat
    # ─── Nutrition ───
    "determine_protein_type": (".nutrition", "determine_protein_type"),
    "get_default_protein_schedule": (".nutrition", "get_default_protein_schedule"),
    "calculate_week_balance": (".nutrition", "calculate_week_balance"),
    "is_balanced_week": (".nutrition", "is_balanced_week"),
    # ─── Formatters ───
    "format_meal_for_display": (".formatters", "format_meal_for_display"),
    "format_planning_summary": (".formatters", "format_planning_summary"),
    "group_meals_by_type": (".formatters", "group_meals_by_type"),
    # ─── Agrégation ───
    "aggregate_ingredients": (".agregation", "aggregate_ingredients"),
    "sort_ingredients_by_rayon": (".agregation", "sort_ingredients_by_rayon"),
    "get_rayon_order": (".agregation", "get_rayon_order"),
    # ─── Validation ───
    "validate_planning_dates": (".validators", "validate_planning_dates"),
    "validate_meal_selection": (".validators", "validate_meal_selection"),
    # ─── Prompts IA ───
    "build_planning_prompt_context": (".prompts", "build_planning_prompt_context"),
    "parse_ai_planning_response": (".prompts", "parse_ai_planning_response"),
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
