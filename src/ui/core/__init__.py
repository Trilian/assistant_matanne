"""
UI Core - Point d'entrée
Composants de base réutilisables

Structure:
- module_config.py: ConfigurationModule dataclass
- crud_renderer.py: ModuleUIBase classe de rendu CRUD
- base_form.py: Constructeur de formulaires
- base_io.py: Services import/export
"""

from .base_form import ConstructeurFormulaire, FormBuilder
from .base_io import (
    BaseIOService,
    ConfigurationIO,
    IOConfig,
    ServiceIOBase,
    create_io_service,
    creer_service_io,
)

# ✅ Import depuis nouveaux modules éclatés
from .crud_renderer import (
    BaseModuleUI,
    ModuleUIBase,
    create_module_ui,
    creer_module_ui,
)
from .module_config import ConfigurationModule, ModuleConfig

__all__ = [
    # Module Config (dataclass)
    "ConfigurationModule",
    "ModuleConfig",
    # CRUD Renderer (classe principale)
    "ModuleUIBase",
    "BaseModuleUI",
    "creer_module_ui",
    "create_module_ui",
    # Form
    "ConstructeurFormulaire",
    "FormBuilder",
    # IO
    "ConfigurationIO",
    "ServiceIOBase",
    "creer_service_io",
    "IOConfig",
    "BaseIOService",
    "create_io_service",
]
