"""
UI Components - Point d'Entrée Unifié
Import simplifié de tous les composants
"""

from .components import (
    # Atomiques
    badge, metric_card, empty_state,
    # Formulaires
    form_field, search_bar, filter_panel,
    # Feedback
    toast, Modal,
    # Data
    pagination, metrics_row, export_buttons,
    # Layouts
    grid_layout, item_card
)

from .domain import (
    # Recettes
    recipe_card,
    # Inventaire
    inventory_card,
    # Planning
    meal_card
)

__all__ = [
    # Base
    "badge", "metric_card", "empty_state",
    # Forms
    "form_field", "search_bar", "filter_panel",
    # Feedback
    "toast", "Modal",
    # Data
    "pagination", "metrics_row", "export_buttons",
    # Layouts
    "grid_layout", "item_card",
    # Domain
    "recipe_card", "inventory_card", "meal_card"
]