# src/services/recettes/__init__.py
"""
Services Recettes - Point d'entrée unifié
Remplace les anciens fichiers éparpillés
"""
from .recette_service import recette_service
from .recette_ai_service import ai_recette_service
from .recette_io_service import RecetteExporter, RecetteImporter
from .recette_scraper_service import RecipeWebScraper, RecipeImageGenerator
from .recette_version_service import create_recette_version_service

__all__ = [
    "recette_service",
    "ai_recette_service",
    "RecetteExporter",
    "RecetteImporter",
    "RecipeWebScraper",
    "RecipeImageGenerator",
    "create_recette_version_service"
]