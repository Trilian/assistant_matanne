"""
Images - Package de génération et manipulation d'images.

Ce package fournit des services pour:
- Génération d'images de recettes via APIs (Leonardo, Unsplash, Pexels, Pixabay, IA)
- Téléchargement d'images depuis URLs
"""

from .generator import (
    LEONARDO_API_KEY,
    PEXELS_API_KEY,
    PIXABAY_API_KEY,
    UNSPLASH_API_KEY,
    ServiceGenerateurImages,
    get_image_generator_service,
    obtenir_image_generator_service,
    obtenir_service_generateur_images,
)

__all__ = [
    "ServiceGenerateurImages",
    "get_image_generator_service",
    "obtenir_image_generator_service",
    "obtenir_service_generateur_images",
    "LEONARDO_API_KEY",
    "PEXELS_API_KEY",
    "PIXABAY_API_KEY",
    "UNSPLASH_API_KEY",
]
