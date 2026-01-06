"""
UI - Point d'entrée unifié optimisé
Architecture claire : core/ components/ feedback/
"""

# Core (modules, forms, io)
from .core import (
    BaseModuleUI,
    ModuleConfig,
    create_module_ui,
    FormBuilder,
    BaseIOService,
    IOConfig,
    create_io_service
)

# Components - Atoms
from .components import (
    badge,
    empty_state,
    metric_card,
    toast,
    divider,
    info_box
)

# Components - Forms
from .components import (
    form_field,
    search_bar,
    filter_panel,
    quick_filters
)

# Components - Data
from .components import (
    pagination,
    metrics_row,
    export_buttons,
    data_table,
    progress_bar,
    status_indicator
)

# Components - Layouts
from .components import (
    grid_layout,
    item_card,
    collapsible_section,
    tabs_layout,
    card_container
)

# Components - Dynamic
from .components import (
    Modal,
    DynamicList,
    Stepper
)

# Feedback
from .feedback import (
    smart_spinner,
    loading_indicator,
    skeleton_loader,
    ProgressTracker,
    LoadingState,
    ToastManager,
    show_success,
    show_error,
    show_warning,
    show_info
)

__all__ = [
    # Core
    "BaseModuleUI",
    "ModuleConfig",
    "create_module_ui",
    "FormBuilder",
    "BaseIOService",
    "IOConfig",
    "create_io_service",

    # Components - Atoms
    "badge",
    "empty_state",
    "metric_card",
    "toast",
    "divider",
    "info_box",

    # Components - Forms
    "form_field",
    "search_bar",
    "filter_panel",
    "quick_filters",

    # Components - Data
    "pagination",
    "metrics_row",
    "export_buttons",
    "data_table",
    "progress_bar",
    "status_indicator",

    # Components - Layouts
    "grid_layout",
    "item_card",
    "collapsible_section",
    "tabs_layout",
    "card_container",

    # Components - Dynamic
    "Modal",
    "DynamicList",
    "Stepper",

    # Feedback
    "smart_spinner",
    "loading_indicator",
    "skeleton_loader",
    "ProgressTracker",
    "LoadingState",
    "ToastManager",
    "show_success",
    "show_error",
    "show_warning",
    "show_info"
]