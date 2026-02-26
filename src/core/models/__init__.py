"""
Models - Point d'entrée unifié pour tous les modèles SQLAlchemy.

Architecture modulaire avec chargement paresseux (PEP 562).
Auto-discovery des sous-modules et symboles via AST parsing.
Seuls ``Base`` et ``metadata`` sont chargés eagerly (nécessaires
pour la création de tables et les migrations).

Usage recommandé par domaine (imports explicites):
    # Recettes
    from src.core.models.recettes import Recette, Ingredient, EtapeRecette
    # Planning
    from src.core.models.planning import Planning, Repas, EvenementPlanning
    # Famille
    from src.core.models.famille import ProfilEnfant, Jalon
    # Santé
    from src.core.models.sante import RoutineSante, EntreeSante
    # Courses
    from src.core.models.courses import ArticleCourses, ListeCourses

Usage général (chargement lazy à la demande):
    from src.core.models import Recette, Ingredient, Planning
    from src.core.models import Base, metadata
"""

from __future__ import annotations

import ast
import importlib
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════
# EAGER: Base & metadata — requis pour la création de tables
# ═══════════════════════════════════════════════════════════
from .base import (
    Base,
    PrioriteEnum,
    SaisonEnum,
    TypeRepasEnum,
    TypeVersionRecetteEnum,
    metadata,
    utc_now,
)
from .mixins import (
    CreeLeMixin,
    TimestampMixin,
)

# ═══════════════════════════════════════════════════════════
# AUTO-DISCOVERY: Sous-modules et symboles via AST parsing
# ═══════════════════════════════════════════════════════════
_PACKAGE_DIR = Path(__file__).parent
_EXCLUDED_FILES = frozenset({"__init__.py", "base.py", "mixins.py"})


def _discover_model_modules() -> tuple[str, ...]:
    """Auto-discover model submodules from directory listing.

    Scans ``src/core/models/`` for ``.py`` files (excluding base, mixins,
    __init__ and private files) and returns relative import paths.
    """
    return tuple(
        f".{f.stem}"
        for f in sorted(_PACKAGE_DIR.glob("*.py"))
        if f.name not in _EXCLUDED_FILES and not f.name.startswith("_")
    )


def _build_lazy_imports(modules: tuple[str, ...]) -> dict[str, tuple[str, str]]:
    """Build symbol → (module, name) mapping via AST parsing.

    Scans each submodule file for:
    - Top-level class definitions (SQLAlchemy models, Enums)
    - PascalCase module-level name assignments (aliases like ``Project = Projet``)

    No imports are performed — only source files are read and parsed.
    This keeps the package import fast (~1-2ms for 20 files).
    """
    mapping: dict[str, tuple[str, str]] = {}

    for mod_name in modules:
        file_name = f"{mod_name.lstrip('.')}.py"
        file_path = _PACKAGE_DIR / file_name

        if not file_path.exists():
            continue

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(file_path))
        except Exception:
            logger.warning(f"AST parsing failed for {file_path}, skipping")
            continue

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                # Class definitions (SQLAlchemy models, Enums)
                mapping[node.name] = (mod_name, node.name)
            elif isinstance(node, ast.Assign):
                # Module-level assignments (aliases like Project = Projet)
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and not target.id.startswith("_")
                        and target.id[0].isupper()  # Only PascalCase symbols
                    ):
                        mapping[target.id] = (mod_name, target.id)

    return mapping


# Build at import time (fast — AST parsing only, no module imports)
_MODEL_MODULES = _discover_model_modules()
_LAZY_IMPORTS = _build_lazy_imports(_MODEL_MODULES)

# Export explicite de tous les symboles
__all__ = [
    # Base (eager)
    "Base",
    "metadata",
    "utc_now",
    "PrioriteEnum",
    "SaisonEnum",
    "TypeRepasEnum",
    "TypeVersionRecetteEnum",
    # Mixins (eager)
    "CreeLeMixin",
    "TimestampMixin",
    # Helper
    "charger_tous_modeles",
    # Tous les symboles lazy (auto-discovered)
    *_LAZY_IMPORTS.keys(),
]


def charger_tous_modeles() -> None:
    """Force le chargement de tous les fichiers modèles.

    Nécessaire avant ``Base.metadata.create_all()`` pour que
    SQLAlchemy connaisse toutes les tables.

    Usage::

        from src.core.models import charger_tous_modeles, Base
        charger_tous_modeles()
        Base.metadata.create_all(bind=engine)
    """
    for mod in _MODEL_MODULES:
        importlib.import_module(mod, __name__)


def __getattr__(name: str) -> Any:
    """Chargement paresseux des modèles (PEP 562)."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __name__)
        value = getattr(module, attr_name)
        # Cache dans le namespace du package pour éviter les appels répétés
        globals()[name] = value
        return value
    raise AttributeError(f"module 'src.core.models' has no attribute {name!r}")
