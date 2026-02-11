"""
UI Core - Point d'entrée
Composants de base réutilisables
"""

from .base_form import ConstructeurFormulaire, FormBuilder
from .base_io import ConfigurationIO, IOConfig, ServiceIOBase, BaseIOService, creer_service_io, create_io_service
from .base_module import ConfigurationModule, ModuleConfig, ModuleUIBase, BaseModuleUI, creer_module_ui, create_module_ui

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
