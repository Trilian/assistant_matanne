"""Module Planning - Calendrier et organisation avec lazy loading."""

__all__ = ["calendrier"]


def __getattr__(name: str):
    """Import differé pour éviter les imports circulaires."""
    if name in __all__:
        from importlib import import_module

        module = import_module(f".{name}", __package__)
        globals()[name] = module
        return module
    raise AttributeError(f"module 'src.modules.planning' has no attribute '{name}'")
