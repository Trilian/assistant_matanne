"""
UI Core - Point d'entrée
Composants de base réutilisables

Structure:
- module_config.py: ConfigurationModule dataclass
- crud_renderer.py: ModuleUIBase classe de rendu CRUD
- base_form.py: Constructeur de formulaires
- base_io.py: Services import/export
"""

from .base_form import ConstructeurFormulaire
from .base_io import (
    ConfigurationIO,
    ServiceIOBase,
    creer_service_io,
)

# ✅ Import depuis nouveaux modules éclatés
from .crud_renderer import (
    ModuleUIBase,
    creer_module_ui,
)
from .module_config import ConfigurationModule

__all__ = [
    # Module Config (dataclass)
    "ConfigurationModule",
    # CRUD Renderer (classe principale)
    "ModuleUIBase",
    "creer_module_ui",
    # Form
    "ConstructeurFormulaire",
    # IO
    "ConfigurationIO",
    "ServiceIOBase",
    "creer_service_io",
]
