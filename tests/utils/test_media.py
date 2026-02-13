"""
Tests pour src/utils/media.py
Tests des classes ImageConfig, ImageCache, ImageOptimizer
"""

from datetime import datetime, timedelta
from io import BytesIO

import pytest
from PIL import Image

from src.utils.media import (
    ImageCache,
    ImageConfig,
    ImageOptimizer,
    get_cache_stats,
    get_optimizer,
    optimize_uploaded_image,
)


@pytest.mark.unit
class TestImageConfig:
    """Tests pour ImageConfig avec config recettes."""

    def test_config_defaut(self):
        """Config par défaut."""
        config = ImageConfig()
        assert config.max_width == 1920
        assert config.max_height == 1080
        assert config.quality == 85
        assert config.format == "WebP"
        assert config.cache_ttl_seconds == 3600

    def test_config_personnalisee_recette(self):
        """Config pour images recettes (thumbnail)."""
        config = ImageConfig(
            max_width=400, max_height=300, quality=75, format="JPEG", cache_ttl_seconds=7200
        )
        assert config.max_width == 400
        assert config.max_height == 300
        assert config.quality == 75
        assert config.format == "JPEG"
        assert config.cache_ttl_seconds == 7200

    def test_config_haute_qualite(self):
        """Config haute qualité pour export."""
        config = ImageConfig(max_width=3840, max_height=2160, quality=95)
        assert config.max_width == 3840
        assert config.quality == 95


@pytest.mark.unit
class TestImageCache:
    """Tests pour ImageCache."""

    def test_cache_vide(self):
        """Cache vide initialement."""
        cache = ImageCache()
        stats = cache.stats()
        assert stats["size"] == 0
        assert stats["keys"] == []

    def test_set_get_image(self):
        """Set et get une image."""
        cache = ImageCache()
        image = Image.new("RGB", (100, 100), color="red")

        cache.set("tarte-pommes", image)
        result = cache.get("tarte-pommes")

        assert result is not None
        assert result.size == (100, 100)

    def test_get_cle_inexistante(self):
        """Get clé inexistante retourne None."""
        cache = ImageCache()
        assert cache.get("gateau-chocolat") is None

    def test_clear_cache(self):
        """Clear vide le cache."""
        cache = ImageCache()
        image = Image.new("RGB", (100, 100))

        cache.set("recette1", image)
        cache.set("recette2", image)
        assert cache.stats()["size"] == 2

        cache.clear()
        assert cache.stats()["size"] == 0

    def test_cache_expiration(self):
        """Cache expire après TTL."""
        cache = ImageCache(ttl_seconds=1)
        image = Image.new("RGB", (100, 100))

        cache.set("test", image)

        # Simuler expiration en modifiant le timestamp
        key = "test"
        img, _ = cache.cache[key]
        cache.cache[key] = (img, datetime.utcnow() - timedelta(seconds=5))

        # Devrait retourner None car expiré
        result = cache.get("test")
        assert result is None

    def test_stats_multiples_images(self):
        """Stats avec plusieurs images."""
        cache = ImageCache()
        for i in range(5):
            image = Image.new("RGB", (50, 50))
            cache.set(f"recette_{i}", image)

        stats = cache.stats()
        assert stats["size"] == 5
        assert len(stats["keys"]) == 5


def _create_test_image(width=200, height=200, mode="RGB"):
    """Helper pour créer une image test."""
    image = Image.new(mode, (width, height), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


@pytest.mark.unit
class TestImageOptimizer:
    """Tests pour ImageOptimizer."""

    def test_optimizer_defaut(self):
        """Optimizer avec config par défaut."""
        optimizer = ImageOptimizer()
        assert optimizer.config.max_width == 1920
        assert optimizer.cache is not None

    def test_optimizer_avec_config(self):
        """Optimizer avec config personnalisée."""
        config = ImageConfig(max_width=800, max_height=600)
        optimizer = ImageOptimizer(config)
        assert optimizer.config.max_width == 800
        assert optimizer.config.max_height == 600

    def test_optimize_petite_image(self):
        """Optimise image plus petite que max."""
        optimizer = ImageOptimizer(ImageConfig(max_width=1000, max_height=1000))
        image = Image.new("RGB", (100, 100), color="green")

        result = optimizer.optimize(image)

        # Pas de redimensionnement
        assert result.size == (100, 100)

    def test_optimize_grande_image(self):
        """Optimise image plus grande que max."""
        optimizer = ImageOptimizer(ImageConfig(max_width=100, max_height=100))
        image = Image.new("RGB", (500, 500), color="green")

        result = optimizer.optimize(image)

        # Redimensionnée
        assert result.width <= 100
        assert result.height <= 100

    def test_optimize_avec_cache(self):
        """Optimize utilise le cache."""
        optimizer = ImageOptimizer()
        image = Image.new("RGB", (100, 100))

        # Premier appel
        result1 = optimizer.optimize(image, key="mon-gateau")

        # Deuxième appel avec la même clé
        result2 = optimizer.optimize(image, key="mon-gateau")

        # Devrait retourner depuis le cache
        assert result1 is not None
        assert result2 is not None

    def test_optimize_bytes(self):
        """Optimize bytes d'image."""
        optimizer = ImageOptimizer(ImageConfig(format="JPEG", quality=80))
        image_bytes = _create_test_image(100, 100)

        result = optimizer.optimize_bytes(image_bytes)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_get_cache_stats(self):
        """Get cache stats."""
        optimizer = ImageOptimizer()
        image = Image.new("RGB", (100, 100))

        optimizer.optimize(image, key="test1")
        optimizer.optimize(image, key="test2")

        stats = optimizer.get_cache_stats()
        assert stats["size"] == 2


@pytest.mark.unit
class TestGetOptimizer:
    """Tests pour get_optimizer global."""

    def test_get_optimizer_cree_instance(self):
        """get_optimizer crée une instance."""
        optimizer = get_optimizer()
        assert isinstance(optimizer, ImageOptimizer)

    def test_get_optimizer_singleton(self):
        """get_optimizer retourne la même instance."""
        optimizer1 = get_optimizer()
        optimizer2 = get_optimizer()
        assert optimizer1 is optimizer2


@pytest.mark.unit
class TestOptimizeUploadedImage:
    """Tests pour optimize_uploaded_image."""

    def test_optimize_simple(self):
        """Optimize image uploadée simple."""
        image_bytes = _create_test_image(100, 100)

        result = optimize_uploaded_image(image_bytes)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_optimize_avec_config(self):
        """Optimize avec config personnalisée."""
        image_bytes = _create_test_image(500, 500)
        config = ImageConfig(max_width=100, max_height=100, quality=50)

        result = optimize_uploaded_image(image_bytes, config=config)

        # Vérifier que l'image est redimensionnée
        result_image = Image.open(BytesIO(result))
        assert result_image.width <= 100
        assert result_image.height <= 100

    def test_optimize_avec_cle_cache(self):
        """Optimize avec clé de cache."""
        image_bytes = _create_test_image()

        result = optimize_uploaded_image(image_bytes, key="pizza-quatre-fromages")

        assert isinstance(result, bytes)


@pytest.mark.unit
class TestGetCacheStats:
    """Tests pour get_cache_stats."""

    def test_stats_format(self):
        """Stats retourne le bon format."""
        stats = get_cache_stats()

        assert "size" in stats
        assert "keys" in stats
        assert isinstance(stats["size"], int)
        assert isinstance(stats["keys"], list)
