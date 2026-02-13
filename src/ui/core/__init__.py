"""
UI Core - Point d'entrée
Composants de base réutilisables
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
from .base_module import (
    BaseModuleUI,
    ConfigurationModule,
    ModuleConfig,
    ModuleUIBase,
    create_module_ui,
    creer_module_ui,
)

__all__ = [
    # Module (nouveaux noms français)
    "ConfigurationModule",
    "ModuleUIBase",
    "creer_module_ui",
    # Module (alias compatibilité)
    "ModuleConfig",
    "BaseModuleUI",
    "create_module_ui",
    # Form (nouveau nom français)
    "ConstructeurFormulaire",
    # Form (alias compatibilité)
    "FormBuilder",
    # IO (nouveaux noms français)
    "ConfigurationIO",
    "ServiceIOBase",
    "creer_service_io",
    # IO (alias compatibilité)
    "IOConfig",
    "BaseIOService",
    "create_io_service",
]
