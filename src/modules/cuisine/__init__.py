"""Module Cuisine - Structure Feature-First avec lazy loading."""

__all__ = ['courses', 'inventaire', 'planificateur_repas', 'recettes', 'schemas']


def __getattr__(name: str):
    """Import differe pour eviter les imports circulaires."""
    if name in __all__:
        from importlib import import_module
        module = import_module(f".{name}", __package__)
        globals()[name] = module
        return module
    raise AttributeError(f"module 'src.modules.cuisine' has no attribute '{name}'")
