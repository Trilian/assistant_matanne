"""
Services Base - Classes et types de base pour les services

Ce package regroupe les classes fondamentales des services:
- BaseAIService: Service IA avec rate limiting et cache automatiques
- BaseService: Service CRUD générique avec ORM
- IOService: Import/Export universel (CSV, JSON)
- Mixins IA: RecipeAIMixin, PlanningAIMixin, InventoryAIMixin
- Async utils: sync_wrapper pour conversion async→sync
- Protocols: Contrats d'interface (PEP 544)

Imports paresseux (__getattr__) pour performance au démarrage.
"""

# ═══════════════════════════════════════════════════════════
# LAZY IMPORTS — Mapping symbol → (module, attr_name)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ─── Async utils ───
    "sync_wrapper": (".async_utils", "sync_wrapper"),
    "make_sync_alias": (".async_utils", "make_sync_alias"),
    "ServiceMeta": (".async_utils", "ServiceMeta"),
    "dual_api": (".async_utils", "dual_api"),
    "run_sync": (".async_utils", "run_sync"),
    "is_async_method": (".async_utils", "is_async_method"),
    "get_sync_name": (".async_utils", "get_sync_name"),
    # ─── AI Service ───
    "BaseAIService": (".ai_service", "BaseAIService"),
    "create_base_ai_service": (".ai_service", "create_base_ai_service"),
    # ─── AI Mixins ───
    "RecipeAIMixin": (".ai_mixins", "RecipeAIMixin"),
    "PlanningAIMixin": (".ai_mixins", "PlanningAIMixin"),
    "InventoryAIMixin": (".ai_mixins", "InventoryAIMixin"),
    # ─── CRUD Service ───
    "BaseService": (".types", "BaseService"),
    "T": (".types", "T"),
    # ─── IO Service ───
    "IOService": (".io_service", "IOService"),
    "RECETTE_FIELD_MAPPING": (".io_service", "RECETTE_FIELD_MAPPING"),
    "INVENTAIRE_FIELD_MAPPING": (".io_service", "INVENTAIRE_FIELD_MAPPING"),
    "COURSES_FIELD_MAPPING": (".io_service", "COURSES_FIELD_MAPPING"),
    # ─── Types de santé ───
    "ServiceStatus": (".protocols", "ServiceStatus"),
    "ServiceHealth": (".protocols", "ServiceHealth"),
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
