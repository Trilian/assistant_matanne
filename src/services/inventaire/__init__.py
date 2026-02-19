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
    # Service principal
    ServiceInventaire,
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
    # Constantes
    "CATEGORIES",
    "EMPLACEMENTS",
]
