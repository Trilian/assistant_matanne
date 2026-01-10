"""
UI Core - Point d'entrée
Composants de base réutilisables
"""

from .base_module import BaseModuleUI, ModuleConfig, create_module_ui
from .base_form import FormBuilder
from .base_io import BaseIOService, IOConfig, create_io_service

__all__ = [
    # Module
    "BaseModuleUI",
    "ModuleConfig",
    "create_module_ui",

    # Form
    "FormBuilder",

    # IO
    "BaseIOService",
    "IOConfig",
    "create_io_service"
]