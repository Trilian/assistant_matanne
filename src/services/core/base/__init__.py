"""
Services Base - Classes et types de base pour les services

Ce package regroupe les classes fondamentales des services:
- BaseAIService: Service IA avec rate limiting et cache automatiques
- BaseService: Service CRUD générique avec ORM
- IOService: Import/Export universel (CSV, JSON)
- Mixins IA: RecipeAIMixin, PlanningAIMixin, InventoryAIMixin
- Async utils: sync_wrapper pour conversion async→sync
- Protocols: Contrats d'interface (PEP 544)
- Result: Pattern Result[T, E] pour contrôle de flux

Imports paresseux (__getattr__) pour performance au démarrage.
"""

# ═══════════════════════════════════════════════════════════
# LAZY IMPORTS — Mapping symbol → (module, attr_name)
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # ─── Async utils ───
    "sync_wrapper": (".async_utils", "sync_wrapper"),
    "make_sync_alias": (".async_utils", "make_sync_alias"),
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
    # ─── Protocols (PEP 544) ───
    "CRUDProtocol": (".protocols", "CRUDProtocol"),
    "AIServiceProtocol": (".protocols", "AIServiceProtocol"),
    "IOProtocol": (".protocols", "IOProtocol"),
    "CacheableProtocol": (".protocols", "CacheableProtocol"),
    "HealthCheckProtocol": (".protocols", "HealthCheckProtocol"),
    "ObservableProtocol": (".protocols", "ObservableProtocol"),
    "ServiceStatus": (".protocols", "ServiceStatus"),
    "ServiceHealth": (".protocols", "ServiceHealth"),
    # ─── Result Pattern ───
    "Result": (".result", "Result"),
    "Success": (".result", "Success"),
    "Failure": (".result", "Failure"),
    "ErrorInfo": (".result", "ErrorInfo"),
    "ErrorCode": (".result", "ErrorCode"),
    "success": (".result", "success"),
    "failure": (".result", "failure"),
    "from_exception": (".result", "from_exception"),
    "safe": (".result", "safe"),
    "result_api": (".result", "result_api"),
    "register_error_mapping": (".result", "register_error_mapping"),
    "collect": (".result", "collect"),
    "collect_all": (".result", "collect_all"),
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
