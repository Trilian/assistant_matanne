"""
Documentation UI — Guides et outils interactifs.

Ce package contient la documentation et les outils pour
le Design System Assistant Matanne.

Modules:
- component_explorer: Playground interactif style Storybook
"""

from __future__ import annotations

from src.ui.docs.component_explorer import (
    ComponentExplorer,
    afficher_component_explorer,
)

__all__ = [
    "ComponentExplorer",
    "afficher_component_explorer",
]
