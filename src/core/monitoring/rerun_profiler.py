"""
Rerun Profiler — DEPRECATED.

Ce module n'est plus utilisé depuis la migration vers FastAPI + Next.js.
Stubs conservés uniquement pour rétrocompatibilité des imports.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@dataclass(slots=True)
class RerunRecord:
    """Stub — DEPRECATED."""

    module: str = ""
    timestamp: float = 0.0
    duree_ms: float = 0.0
    state_changes: list[str] = field(default_factory=list)


class RerunProfiler:
    """Stub — DEPRECATED."""

    def enregistrer(self, record: RerunRecord) -> None:
        pass

    def stats(self) -> dict[str, Any]:
        return {"total_reruns": 0, "duree_moyenne_ms": 0.0, "dernier_rerun": None, "reruns_par_module": {}, "reruns_lents": 0}

    def reset(self) -> None:
        pass


def profiler_rerun(module_name: str) -> Callable[[F], F]:
    """Stub — DEPRECATED."""
    def decorator(func: F) -> F:
        return func
    return decorator


def obtenir_stats_rerun() -> dict[str, Any]:
    """Stub — DEPRECATED."""
    return {"total_reruns": 0, "duree_moyenne_ms": 0.0, "dernier_rerun": None, "reruns_par_module": {}, "reruns_lents": 0}


def reset_profiler() -> None:
    """Stub — DEPRECATED."""
    pass
