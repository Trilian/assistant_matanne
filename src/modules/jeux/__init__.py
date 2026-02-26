"""Module Jeux - Paris sportifs, Loto, Euromillions et modules transversaux."""

__all__ = [
    "loto",
    "paris",
    "euromillions",
    "bilan",
    "comparatif_roi",
    "alertes",
    "biais",
    "calendrier",
    "educatif",
]


def __getattr__(name: str):
    """Import differé pour éviter les imports circulaires."""
    if name in __all__:
        from importlib import import_module

        module = import_module(f".{name}", __package__)
        globals()[name] = module
        return module
    raise AttributeError(f"module 'src.modules.jeux' has no attribute '{name}'")
