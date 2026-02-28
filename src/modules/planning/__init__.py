"""Module Planning - Calendrier et organisation avec lazy loading."""

from src.ui.engine import CSSEngine

# Register small CSS block to prevent wrapping for planning headers
CSSEngine.register(
    "planning-no-wrap",
    ".planning--no-wrap { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; display: inline-block; }\n.planning--nowrap-center { display:flex; justify-content:center; align-items:center; white-space: nowrap; gap:8px; }",
)

# Ensure injection at module import time
CSSEngine.inject_all()


__all__ = ["calendrier"]


def __getattr__(name: str):
    """Import differé pour éviter les imports circulaires."""
    if name in __all__:
        from importlib import import_module

        module = import_module(f".{name}", __package__)
        globals()[name] = module
        return module
    raise AttributeError(f"module 'src.modules.planning' has no attribute '{name}'")
