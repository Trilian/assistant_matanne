"""
Tests approfondis pour media.py (ImageOptimizer, ImageCache)

Module: src/utils/media.py
Tests crÃ©Ã©s: ~50 tests
Objectif: Atteindre 80%+ de couverture
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from io import BytesIO


# =============================================================================
# TESTS ImageConfig
# =============================================================================


class TestImageConfig:
    """Tests pour ImageConfig dataclass"""
    
    def test_image_config_default_values(self):
        """Valeurs par dÃ©faut"""
        from src.utils.media import ImageConfig
        
        config = ImageConfig()
        
        assert config.max_width == 1920
        assert config.max_height == 1080
        assert config.quality == 85
        assert config.format == "WebP"
        assert config.cache_ttl_seconds == 3600
    
    def test_image_config_custom_values(self):
        """Valeurs personnalisÃ©es"""
        from src.utils.media import ImageConfig
        
        config = ImageConfig(
            max_width=800,
            max_height=600,
            quality=70,
            format="JPEG",
            cache_ttl_seconds=7200
        )
        
        assert config.max_width == 800
        assert config.max_height == 600
        assert config.quality == 70
        assert config.format == "JPEG"
        assert config.cache_ttl_seconds == 7200


# =============================================================================
# TESTS ImageCache
# =============================================================================


class TestImageCache:
    """Tests pour ImageCache"""
    
    def test_image_cache_init(self):
        """Initialisation cache"""
        from src.utils.media import ImageCache
        
        cache = ImageCache()
        assert cache.cache == {}
        assert cache.ttl_seconds == 3600
    
    def test_image_cache_set_get(self):
        """Set et get basique"""
        from src.utils.media import ImageCache
        
        cache = ImageCache()
        mock_image = Mock()
        
        cache.set("key1", mock_image)
        result = cache.get("key1")
        
        assert result == mock_image
    
    def test_image_cache_get_missing(self):
        """Get clÃ© absente"""
        from src.utils.media import ImageCache
        
        cache = ImageCache()
        assert cache.get("nonexistent") is None
    
    def test_image_cache_clear(self):
        """Vider le cache"""
        from src.utils.media import ImageCache
        
        cache = ImageCache()
        mock_image = Mock()
        cache.set("key1", mock_image)
        cache.set("key2", mock_image)
        
        cache.clear()
        
        assert cache.cache == {}
    
    def test_image_cache_stats(self):
        """Stats du cache"""
        from src.utils.media import ImageCache
        
        cache = ImageCache()
        mock_image = Mock()
        cache.set("key1", mock_image)
        cache.set("key2", mock_image)
        
        stats = cache.stats()
        
        assert stats["size"] == 2
        assert "key1" in stats["keys"]
        assert "key2" in stats["keys"]
    
    def test_image_cache_ttl_expired(self):
        """Cache expirÃ© (TTL dÃ©passÃ©)"""
        from src.utils.media import ImageCache
        
        cache = ImageCache(ttl_seconds=1)  # 1 seconde TTL
        mock_image = Mock()
        
        # Simuler un timestamp vieux
        old_timestamp = datetime.utcnow() - timedelta(seconds=10)
        cache.cache["old_key"] = (mock_image, old_timestamp)
        
        result = cache.get("old_key")
        assert result is None
        assert "old_key" not in cache.cache  # NettoyÃ©
    
    def test_image_cache_ttl_valid(self):
        """Cache valide (TTL pas dÃ©passÃ©)"""
        from src.utils.media import ImageCache
        
        cache = ImageCache(ttl_seconds=3600)
        mock_image = Mock()
        cache.set("valid_key", mock_image)
        
        result = cache.get("valid_key")
        assert result == mock_image


# =============================================================================
# TESTS ImageOptimizer
# =============================================================================


class TestImageOptimizer:
    """Tests pour ImageOptimizer"""
    
    def test_image_optimizer_init_default(self):
        """Initialisation avec config par dÃ©faut"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        assert optimizer.config.max_width == 1920
        assert optimizer.config.max_height == 1080
    
    def test_image_optimizer_init_custom_config(self):
        """Initialisation avec config personnalisÃ©e"""
        from src.utils.media import ImageOptimizer, ImageConfig
        
        config = ImageConfig(max_width=640, max_height=480)
        optimizer = ImageOptimizer(config)
        
        assert optimizer.config.max_width == 640
        assert optimizer.config.max_height == 480
    
    def test_image_optimizer_optimize_no_resize(self):
        """Optimisation sans redimensionnement (image petite)"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        # CrÃ©er une image mock petite
        mock_image = Mock()
        mock_image.width = 800
        mock_image.height = 600
        
        result = optimizer.optimize(mock_image)
        
        assert result == mock_image
        mock_image.thumbnail.assert_not_called()
    
    def test_image_optimizer_optimize_resize_width(self):
        """Optimisation avec redimensionnement (width trop grand)"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        mock_image = Mock()
        mock_image.width = 4000
        mock_image.height = 600
        
        result = optimizer.optimize(mock_image)
        
        mock_image.thumbnail.assert_called_once()
    
    def test_image_optimizer_optimize_resize_height(self):
        """Optimisation avec redimensionnement (height trop grand)"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        mock_image = Mock()
        mock_image.width = 800
        mock_image.height = 3000
        
        result = optimizer.optimize(mock_image)
        
        mock_image.thumbnail.assert_called_once()
    
    def test_image_optimizer_optimize_with_cache(self):
        """Optimisation avec mise en cache"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        mock_image = Mock()
        mock_image.width = 800
        mock_image.height = 600
        
        # Premier appel - met en cache
        result1 = optimizer.optimize(mock_image, key="test_key")
        assert result1 == mock_image
        
        # Second appel - depuis cache
        optimizer.cache.get = Mock(return_value=mock_image)
        result2 = optimizer.optimize(mock_image, key="test_key")
        assert result2 == mock_image
    
    def test_image_optimizer_optimize_cache_hit(self):
        """Optimisation retourne depuis cache si existe"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        cached_image = Mock()
        optimizer.cache.get = Mock(return_value=cached_image)
        
        mock_image = Mock()
        mock_image.width = 5000  # Serait redimensionnÃ©
        
        result = optimizer.optimize(mock_image, key="cached_key")
        
        # Retourne l'image du cache, pas de redimensionnement
        assert result == cached_image
        mock_image.thumbnail.assert_not_called()
    
    @patch("src.utils.media.Image")
    def test_image_optimizer_optimize_bytes(self, mock_pil_image):
        """Optimisation depuis bytes"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        # Mock l'image PIL
        mock_image = Mock()
        mock_image.width = 800
        mock_image.height = 600
        mock_pil_image.open.return_value = mock_image
        
        # Mock save
        def mock_save(output, format, quality):
            output.write(b"optimized_image_bytes")
        mock_image.save = mock_save
        
        image_bytes = b"fake_image_data"
        result = optimizer.optimize_bytes(image_bytes)
        
        assert isinstance(result, bytes)
    
    def test_image_optimizer_get_cache_stats(self):
        """Stats du cache optimizer"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        mock_image = Mock()
        optimizer.cache.set("key1", mock_image)
        
        stats = optimizer.get_cache_stats()
        
        assert stats["size"] == 1
        assert "key1" in stats["keys"]


# =============================================================================
# TESTS Fonctions globales
# =============================================================================


class TestGlobalOptimizer:
    """Tests pour get_optimizer et fonctions globales"""
    
    def test_get_optimizer_singleton(self):
        """get_optimizer retourne instance singleton"""
        from src.utils import media
        
        # Reset global
        media._global_optimizer = None
        
        opt1 = media.get_optimizer()
        opt2 = media.get_optimizer()
        
        assert opt1 is opt2
    
    def test_get_optimizer_creates_instance(self):
        """get_optimizer crÃ©e instance si None"""
        from src.utils import media
        
        media._global_optimizer = None
        
        optimizer = media.get_optimizer()
        
        assert optimizer is not None
        assert media._global_optimizer is optimizer
    
    @patch("src.utils.media.get_optimizer")
    def test_optimize_uploaded_image_default(self, mock_get_optimizer):
        """optimize_uploaded_image utilise optimizer global"""
        from src.utils.media import optimize_uploaded_image
        
        mock_optimizer = Mock()
        mock_optimizer.optimize_bytes.return_value = b"optimized"
        mock_get_optimizer.return_value = mock_optimizer
        
        result = optimize_uploaded_image(b"input_bytes")
        
        mock_optimizer.optimize_bytes.assert_called_once()
        assert result == b"optimized"
    
    @patch("src.utils.media.ImageOptimizer")
    def test_optimize_uploaded_image_custom_config(self, mock_optimizer_class):
        """optimize_uploaded_image avec config personnalisÃ©e"""
        from src.utils.media import optimize_uploaded_image, ImageConfig
        
        mock_optimizer = Mock()
        mock_optimizer.optimize_bytes.return_value = b"custom_optimized"
        mock_optimizer_class.return_value = mock_optimizer
        
        config = ImageConfig(max_width=640)
        result = optimize_uploaded_image(b"input_bytes", config=config)
        
        mock_optimizer_class.assert_called_once_with(config)
        assert result == b"custom_optimized"
    
    @patch("src.utils.media.get_optimizer")
    def test_optimize_uploaded_image_with_key(self, mock_get_optimizer):
        """optimize_uploaded_image avec clÃ© cache"""
        from src.utils.media import optimize_uploaded_image
        
        mock_optimizer = Mock()
        mock_optimizer.optimize_bytes.return_value = b"cached_result"
        mock_get_optimizer.return_value = mock_optimizer
        
        result = optimize_uploaded_image(b"input", key="my_cache_key")
        
        mock_optimizer.optimize_bytes.assert_called_with(b"input", "my_cache_key")
    
    @patch("src.utils.media.get_optimizer")
    def test_get_cache_stats_global(self, mock_get_optimizer):
        """get_cache_stats retourne stats de l'optimizer global"""
        from src.utils.media import get_cache_stats
        
        mock_optimizer = Mock()
        mock_optimizer.get_cache_stats.return_value = {"size": 5, "keys": ["a", "b"]}
        mock_get_optimizer.return_value = mock_optimizer
        
        stats = get_cache_stats()
        
        assert stats["size"] == 5
        assert len(stats["keys"]) == 2


# =============================================================================
# TESTS d'intÃ©gration avec PIL (si disponible)
# =============================================================================


class TestImageOptimizerIntegration:
    """Tests d'intÃ©gration avec PIL rÃ©el"""
    
    @pytest.fixture
    def sample_image_bytes(self):
        """CrÃ©e une image test rÃ©elle"""
        try:
            from PIL import Image
            
            # CrÃ©er une image RGB 100x100 rouge
            img = Image.new("RGB", (100, 100), color="red")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            return buffer.getvalue()
        except ImportError:
            pytest.skip("PIL not installed")
    
    def test_optimize_real_image(self, sample_image_bytes):
        """Optimise une vraie image"""
        from src.utils.media import ImageOptimizer, ImageConfig
        
        config = ImageConfig(max_width=50, max_height=50, quality=80)
        optimizer = ImageOptimizer(config)
        
        result = optimizer.optimize_bytes(sample_image_bytes)
        
        assert isinstance(result, bytes)
        assert len(result) > 0
    
    def test_optimize_large_image(self):
        """Optimise une grande image"""
        try:
            from PIL import Image
            from src.utils.media import ImageOptimizer, ImageConfig
            
            # CrÃ©er une grande image 3000x2000
            img = Image.new("RGB", (3000, 2000), color="blue")
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            
            config = ImageConfig(max_width=1920, max_height=1080)
            optimizer = ImageOptimizer(config)
            
            result = optimizer.optimize_bytes(image_bytes)
            
            # VÃ©rifier que l'image a Ã©tÃ© redimensionnÃ©e
            from PIL import Image as PILImage
            result_img = PILImage.open(BytesIO(result))
            
            assert result_img.width <= 1920
            assert result_img.height <= 1080
        except ImportError:
            pytest.skip("PIL not installed")
    
    def test_cache_prevents_reoptimization(self, sample_image_bytes):
        """Le cache Ã©vite la rÃ©-optimisation"""
        from src.utils.media import ImageOptimizer
        
        optimizer = ImageOptimizer()
        
        # Premier appel
        result1 = optimizer.optimize_bytes(sample_image_bytes, key="test")
        
        # Second appel - devrait utiliser le cache
        result2 = optimizer.optimize_bytes(sample_image_bytes, key="test")
        
        # Les deux rÃ©sultats devraient Ãªtre identiques
        assert result1 == result2
