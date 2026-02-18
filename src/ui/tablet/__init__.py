"""
Mode Tablette - Module complet pour interfaces tactiles.

Fournit:
- Configuration et gestion du mode tablette
- CSS adapté aux écrans tactiles
- Composants UI optimisés tactiles
- Mode cuisine (recettes step-by-step)
"""

# Configuration et état
from .config import TabletMode, get_tablet_mode, set_tablet_mode

# Mode cuisine
from .kitchen import render_kitchen_recipe_view, render_mode_selector

# Styles CSS
from .styles import KITCHEN_MODE_CSS, TABLET_CSS, apply_tablet_mode, close_tablet_mode

# Widgets tactiles
from .widgets import (
    tablet_button,
    tablet_checklist,
    tablet_number_input,
    tablet_select_grid,
)

__all__ = [
    # Config
    "TabletMode",
    "get_tablet_mode",
    "set_tablet_mode",
    # Styles
    "TABLET_CSS",
    "KITCHEN_MODE_CSS",
    "apply_tablet_mode",
    "close_tablet_mode",
    # Widgets
    "tablet_button",
    "tablet_select_grid",
    "tablet_number_input",
    "tablet_checklist",
    # Kitchen
    "render_kitchen_recipe_view",
    "render_mode_selector",
]
