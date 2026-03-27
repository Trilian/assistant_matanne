"""Module API REST FastAPI.

Le package expose ``app`` pour les integrations externes, mais l'import de
``src.api`` ne doit pas forcer le chargement complet de l'application. Plusieurs
tests et sous-modules importent ``src.api.*`` sans avoir besoin d'initialiser
tous les routeurs.
"""

from __future__ import annotations

__all__ = ["app"]


def __getattr__(name: str):
    if name == "app":
        from .main import app

        return app
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
