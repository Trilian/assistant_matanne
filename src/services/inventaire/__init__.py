"""
Services Inventaire - Point d'Entrée Module

Regroupe tous les services liés à l'inventaire :
- CRUD inventaire
- IA (analyse, suggestions)
- Import/Export
- Constantes métier
"""

# Service CRUD principal
from .inventaire_service import (
    InventaireService,
    inventaire_service,
    CATEGORIES,
    EMPLACEMENTS,
)

# Service IA
from .inventaire_ai_service import (
    InventaireAIService,
    inventaire_ai_service,
)

# Service Import/Export
from .inventaire_io_service import (
    InventaireExporter,
    InventaireImporter,
)

__all__ = [
    # Classes
    "InventaireService",
    "InventaireAIService",
    "InventaireExporter",
    "InventaireImporter",

    # Instances (singletons)
    "inventaire_service",
    "inventaire_ai_service",

    # Constantes métier
    "CATEGORIES",
    "EMPLACEMENTS",
]