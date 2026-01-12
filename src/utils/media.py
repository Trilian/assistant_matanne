"""
Media utilities - Image handling, caching, and optimization.

Fournit des utilitaires pour gérer les images uploadées, les mettre en cache,
et les optimiser.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import io
from PIL import Image


@dataclass
class ImageConfig:
    """Configuration pour l'optimisation d'images"""
    
    max_width: int = 1920
    max_height: int = 1080
    quality: int = 85
    format: str = "WebP"
    cache_ttl_seconds: int = 3600


@dataclass
class ImageCache:
    """Cache en mémoire pour images"""
    
    cache: Dict[str, tuple[Image.Image, datetime]] = field(default_factory=dict)
    ttl_seconds: int = 3600
    
    def get(self, key: str) -> Optional[Image.Image]:
        """Récupère une image du cache si valide"""
        if key not in self.cache:
            return None
        
        image, timestamp = self.cache[key]
        if datetime.utcnow() - timestamp > timedelta(seconds=self.ttl_seconds):
            del self.cache[key]
            return None
        
        return image
    
    def set(self, key: str, image: Image.Image) -> None:
        """Ajoute une image au cache"""
        self.cache[key] = (image, datetime.utcnow())
    
    def clear(self) -> None:
        """Vide le cache"""
        self.cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Retourne les stats du cache"""
        return {
            "size": len(self.cache),
            "keys": list(self.cache.keys())
        }


class ImageOptimizer:
    """Optimiseur d'images avec redimensionnement et compression"""
    
    def __init__(self, config: Optional[ImageConfig] = None):
        self.config = config or ImageConfig()
        self.cache = ImageCache(ttl_seconds=self.config.cache_ttl_seconds)
    
    def optimize(self, image: Image.Image, key: Optional[str] = None) -> Image.Image:
        """Optimise une image en redimensionnant et compressant"""
        if key:
            cached = self.cache.get(key)
            if cached:
                return cached
        
        # Redimensionner si nécessaire
        if image.width > self.config.max_width or image.height > self.config.max_height:
            image.thumbnail(
                (self.config.max_width, self.config.max_height),
                Image.Resampling.LANCZOS
            )
        
        # Mettre en cache
        if key:
            self.cache.set(key, image)
        
        return image
    
    def optimize_bytes(self, image_bytes: bytes, key: Optional[str] = None) -> bytes:
        """Optimise des bytes d'image"""
        image = Image.open(io.BytesIO(image_bytes))
        optimized = self.optimize(image, key)
        
        output = io.BytesIO()
        optimized.save(output, format=self.config.format, quality=self.config.quality)
        return output.getvalue()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Retourne les stats du cache"""
        return self.cache.stats()


# Instance globale
_global_optimizer: Optional[ImageOptimizer] = None


def get_optimizer() -> ImageOptimizer:
    """Récupère ou crée l'optimiseur global"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = ImageOptimizer()
    return _global_optimizer


def optimize_uploaded_image(
    image_bytes: bytes,
    config: Optional[ImageConfig] = None,
    key: Optional[str] = None
) -> bytes:
    """Optimise une image uploadée
    
    Args:
        image_bytes: Bytes de l'image
        config: Configuration optionnelle
        key: Clé pour le cache
    
    Returns:
        Bytes de l'image optimisée
    """
    optimizer = get_optimizer()
    
    if config:
        # Créer un nouvel optimiseur avec la config donnée
        temp_optimizer = ImageOptimizer(config)
        return temp_optimizer.optimize_bytes(image_bytes, key)
    
    return optimizer.optimize_bytes(image_bytes, key)


def get_cache_stats() -> Dict[str, Any]:
    """Retourne les stats du cache global"""
    optimizer = get_optimizer()
    return optimizer.get_cache_stats()
