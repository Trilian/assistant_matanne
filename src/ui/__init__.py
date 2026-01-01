"""
UI Components - Point d'Entrée Unifié avec Feedback
"""

# Composants de base
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
    grid_layout, item_card,
    # Dynamique
    DynamicList
)

# Composants métier
from .domain import (
    recipe_card,
    inventory_card,
    stock_alert,
    meal_card,
    week_calendar
)

# 🆕 Feedback Temps Réel
from .feedback import (
    smart_spinner,
    ProgressTracker,
    LoadingState,
    run_with_feedback,
    ToastManager,
    show_success,
    show_error,
    show_warning,
    show_info
)

__all__ = [
    # Base
    "badge", "metric_card", "empty_state",

    # Forms
    "form_field", "search_bar", "filter_panel",

    # Feedback classique
    "toast", "Modal",

    # Data
    "pagination", "metrics_row", "export_buttons",

    # Layouts
    "grid_layout", "item_card", "DynamicList",

    # Domain
    "recipe_card", "inventory_card", "stock_alert",
    "meal_card", "week_calendar",

    # 🆕 Feedback Temps Réel
    "smart_spinner",
    "ProgressTracker",
    "LoadingState",
    "run_with_feedback",
    "ToastManager",
    "show_success",
    "show_error",
    "show_warning",
    "show_info"
]

