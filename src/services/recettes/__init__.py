"""
Services Recettes - Point d'Entrée Module

Regroupe tous les services liés aux recettes :
- CRUD recettes
- IA (génération, adaptation)
- Versions (bébé, batch cooking)
- Scraping web
- Import/Export
"""

# Service CRUD principal
from .recette_service import RecetteService, recette_service

# Service IA
from .recette_ai_service import RecetteAIService, recette_ai_service

# Service Versions (Bébé/Batch)
from .recette_version_service import (
    RecetteVersionService,
    recette_version_service,
)

# Service Scraping Web
from .recette_scraper_service import (
    RecipeWebScraper,
    RecipeImageGenerator,
)

# Service Import/Export
from .recette_io_service import (
    RecetteExporter,
    RecetteImporter,
)

__all__ = [
    # Classes
    "RecetteService",
    "RecetteAIService",
    "RecetteVersionService",
    "RecipeWebScraper",
    "RecipeImageGenerator",
    "RecetteExporter",
    "RecetteImporter",

    # Instances (singletons)
    "recette_service",
    "recette_ai_service",
    "recette_version_service",
]