"""
Package Service Inventaire.

Ce package gère l'inventaire des articles avec:
- CRUD optimisé avec cache
- Alertes stock et péremption
- Suggestions IA pour courses
- Import/Export de données
- Historique des modifications

Utilisation:
    from src.services.inventaire import obtenir_service_inventaire

    service = obtenir_service_inventaire()
    inventaire = service.get_inventaire_complet()
"""

from .service import (
    # Constantes
    CATEGORIES,
    EMPLACEMENTS,
    # Aliases rétrocompatibilité
    InventaireService,
    # Service principal
    ServiceInventaire,
    get_inventaire_service,
    # Variable globale
    inventaire_service,
    obtenir_service_inventaire,
)
from .types import (
    ArticleImport,
    SuggestionCourses,
)

__all__ = [
    # Types Pydantic
    "SuggestionCourses",
    "ArticleImport",
    # Service principal
    "ServiceInventaire",
    "obtenir_service_inventaire",
    # Aliases rétrocompatibilité
    "InventaireService",
    "get_inventaire_service",
    # Constantes
    "CATEGORIES",
    "EMPLACEMENTS",
    # Variable globale
    "inventaire_service",
]
