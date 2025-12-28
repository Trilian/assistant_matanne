"""
UI Components - Point d'Entrée Unifié
Import simplifié de tous les composants UI
"""

# ═══════════════════════════════════════════════════════════════
# BASE (Composants atomiques)
# ═══════════════════════════════════════════════════════════════

from .base import (
    badge,
    metric_card,
    progress_bar,
    divider,
    icon_text,
    empty_state,
    loading_spinner,
    card,
    info_box,
    image_with_fallback,
    breadcrumb,
    tabs_styled,
    key_value_list,
    countdown
)

# ═══════════════════════════════════════════════════════════════
# FORMS (Formulaires et inputs)
# ═══════════════════════════════════════════════════════════════

from .forms import (
    form_field,
    search_bar,
    filter_panel,
    DynamicList,
    date_selector,
    time_range_selector
)

# ═══════════════════════════════════════════════════════════════
# DATA (Tables, pagination, stats)
# ═══════════════════════════════════════════════════════════════

from .data import (
    pagination,
    data_table,
    simple_table,
    metrics_row,
    stat_cards,
    advanced_search,
    export_buttons
)

# ═══════════════════════════════════════════════════════════════
# FEEDBACK (Toasts, modals, confirmations)
# ═══════════════════════════════════════════════════════════════

from .feedback import (
    toast,
    notification_banner,
    Modal,
    confirmation_dialog,
    alert_box,
    loading_message,
    progress_tracker,
    step_indicator,
    validation_error,
    success_message,
    error_message,
    info_tooltip,
    status_badge
)

# ═══════════════════════════════════════════════════════════════
# LAYOUTS (Grilles, listes, cartes)
# ═══════════════════════════════════════════════════════════════

from .layouts import (
    grid_layout,
    masonry_layout,
    action_list,
    card_list,
    item_card,
    timeline,
    quick_actions
)

# ═══════════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Base
    "badge", "metric_card", "progress_bar", "divider", "icon_text",
    "empty_state", "loading_spinner", "card", "info_box",
    "image_with_fallback", "breadcrumb", "tabs_styled",
    "key_value_list", "countdown",

    # Forms
    "form_field", "search_bar", "filter_panel", "DynamicList",
    "date_selector", "time_range_selector",

    # Data
    "pagination", "data_table", "simple_table", "metrics_row",
    "stat_cards", "advanced_search", "export_buttons",

    # Feedback
    "toast", "notification_banner", "Modal", "confirmation_dialog",
    "alert_box", "loading_message", "progress_tracker", "step_indicator",
    "validation_error", "success_message", "error_message",
    "info_tooltip", "status_badge",

    # Layouts
    "grid_layout", "masonry_layout", "action_list", "card_list",
    "item_card", "timeline", "quick_actions"
]


# ═══════════════════════════════════════════════════════════════
# HELPERS D'IMPORT SIMPLIFIÉ
# ═══════════════════════════════════════════════════════════════

class UI:
    """
    Namespace pour accès groupé aux composants

    Usage:
        from src.ui import UI

        UI.badge("Actif", "#4CAF50")
        UI.toast("Succès !", "success")
    """

    # Base
    badge = badge
    metric_card = metric_card
    progress_bar = progress_bar
    divider = divider
    icon_text = icon_text
    empty_state = empty_state
    loading_spinner = loading_spinner
    card = card
    info_box = info_box
    image_with_fallback = image_with_fallback
    breadcrumb = breadcrumb
    key_value_list = key_value_list
    countdown = countdown

    # Forms
    form_field = form_field
    search_bar = search_bar
    filter_panel = filter_panel
    DynamicList = DynamicList
    date_selector = date_selector
    time_range_selector = time_range_selector

    # Data
    pagination = pagination
    data_table = data_table
    simple_table = simple_table
    metrics_row = metrics_row
    stat_cards = stat_cards
    advanced_search = advanced_search
    export_buttons = export_buttons

    # Feedback
    toast = toast
    notification_banner = notification_banner
    Modal = Modal
    confirmation_dialog = confirmation_dialog
    alert_box = alert_box
    loading_message = loading_message
    progress_tracker = progress_tracker
    step_indicator = step_indicator
    validation_error = validation_error
    success_message = success_message
    error_message = error_message
    info_tooltip = info_tooltip
    status_badge = status_badge

    # Layouts
    grid_layout = grid_layout
    masonry_layout = masonry_layout
    action_list = action_list
    card_list = card_list
    item_card = item_card
    timeline = timeline
    quick_actions = quick_actions