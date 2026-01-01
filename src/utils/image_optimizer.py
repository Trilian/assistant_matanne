"""
Image Optimizer - Compression automatique images recettes
Réduit taille de 70-80% sans perte visible
"""
from PIL import Image
import io
import logging
from typing import Optional, Tuple
import streamlit as st
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════

class ImageConfig:
    """Configuration compression images"""

    # Tailles cibles
    MAX_WIDTH = 800  # Largeur max
    MAX_HEIGHT = 600  # Hauteur max
    THUMBNAIL_SIZE = (200, 200)  # Miniatures

    # Qualité compression
    JPEG_QUALITY = 85  # 85 = bon compromis qualité/taille
    WEBP_QUALITY = 80  # WebP encore plus efficace

    # Formats
    ALLOWED_FORMATS = ['JPEG', 'PNG', 'WEBP']
    OUTPUT_FORMAT = 'WEBP'  # WebP par défaut (meilleure compression)

    # Cache
    CACHE_DIR = Path("cache/images")


# ═══════════════════════════════════════════════════════════
# OPTIMISEUR PRINCIPAL
# ═══════════════════════════════════════════════════════════

class ImageOptimizer:
    """
    Optimise images recettes

    Features:
    - Redimensionnement intelligent
    - Compression avec qualité préservée
    - Génération miniatures
    - Cache local
    - Conversion WebP
    """

    @staticmethod
    def optimize(
            image_data: bytes,
            max_width: int = ImageConfig.MAX_WIDTH,
            max_height: int = ImageConfig.MAX_HEIGHT,
            quality: int = ImageConfig.JPEG_QUALITY,
            output_format: str = ImageConfig.OUTPUT_FORMAT
    ) -> bytes:
        """
        Optimise une image

        Args:
            image_data: Données image brutes
            max_width: Largeur max
            max_height: Hauteur max
            quality: Qualité compression (0-100)
            output_format: Format sortie (JPEG, PNG, WEBP)

        Returns:
            Données image optimisée
        """
        try:
            # Ouvrir image
            img = Image.open(io.BytesIO(image_data))

            # Logs taille originale
            original_size = len(image_data)
            logger.info(f"Image originale: {img.size}, {original_size/1024:.1f}KB")

            # Convertir en RGB si nécessaire (pour JPEG/WEBP)
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')

            # Redimensionner si trop grande
            img = ImageOptimizer._resize(img, max_width, max_height)

            # Optimiser selon format
            optimized_data = ImageOptimizer._compress(
                img,
                quality,
                output_format
            )

            # Logs résultat
            optimized_size = len(optimized_data)
            reduction = (1 - optimized_size / original_size) * 100

            logger.info(
                f"Image optimisée: {img.size}, "
                f"{optimized_size/1024:.1f}KB "
                f"(-{reduction:.0f}%)"
            )

            return optimized_data

        except Exception as e:
            logger.error(f"Erreur optimisation image: {e}")
            # Retourner original si échec
            return image_data

    @staticmethod
    def _resize(
            img: Image.Image,
            max_width: int,
            max_height: int
    ) -> Image.Image:
        """Redimensionne image en préservant ratio"""

        width, height = img.size

        # Calculer ratio
        ratio = min(max_width / width, max_height / height)

        # Redimensionner uniquement si trop grand
        if ratio < 1:
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            img = img.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS  # Haute qualité
            )

        return img

    @staticmethod
    def _compress(
            img: Image.Image,
            quality: int,
            output_format: str
    ) -> bytes:
        """Compresse image au format cible"""

        output = io.BytesIO()

        if output_format == 'WEBP':
            # WebP (meilleure compression)
            img.save(
                output,
                format='WEBP',
                quality=quality,
                method=6  # Compression max (lent mais efficace)
            )

        elif output_format == 'JPEG':
            # JPEG classique
            if img.mode == 'RGBA':
                # Convertir RGBA en RGB pour JPEG
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background

            img.save(
                output,
                format='JPEG',
                quality=quality,
                optimize=True,
                progressive=True
            )

        else:  # PNG
            img.save(
                output,
                format='PNG',
                optimize=True
            )

        return output.getvalue()

    @staticmethod
    def generate_thumbnail(
            image_data: bytes,
            size: Tuple[int, int] = ImageConfig.THUMBNAIL_SIZE
    ) -> bytes:
        """
        Génère miniature

        Args:
            image_data: Image originale
            size: Taille miniature (width, height)

        Returns:
            Miniature optimisée
        """
        try:
            img = Image.open(io.BytesIO(image_data))

            # Créer miniature (crop centré)
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Compresser
            output = io.BytesIO()
            img.save(output, format='WEBP', quality=75)

            return output.getvalue()

        except Exception as e:
            logger.error(f"Erreur génération miniature: {e}")
            return image_data


# ═══════════════════════════════════════════════════════════
# CACHE LOCAL IMAGES
# ═══════════════════════════════════════════════════════════

class ImageCache:
    """Cache local images optimisées"""

    @staticmethod
    def _get_hash(image_data: bytes) -> str:
        """Génère hash unique image"""
        return hashlib.md5(image_data).hexdigest()

    @staticmethod
    def get(image_data: bytes) -> Optional[bytes]:
        """Récupère image du cache"""
        cache_dir = ImageConfig.CACHE_DIR

        if not cache_dir.exists():
            return None

        image_hash = ImageCache._get_hash(image_data)
        cache_file = cache_dir / f"{image_hash}.webp"

        if cache_file.exists():
            logger.debug(f"Cache HIT: {image_hash[:8]}")
            return cache_file.read_bytes()

        return None

    @staticmethod
    def set(image_data: bytes, optimized_data: bytes):
        """Sauvegarde image dans cache"""
        cache_dir = ImageConfig.CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)

        image_hash = ImageCache._get_hash(image_data)
        cache_file = cache_dir / f"{image_hash}.webp"

        cache_file.write_bytes(optimized_data)
        logger.debug(f"Cache SET: {image_hash[:8]}")

    @staticmethod
    def clear():
        """Vide le cache"""
        cache_dir = ImageConfig.CACHE_DIR

        if cache_dir.exists():
            for file in cache_dir.glob("*.webp"):
                file.unlink()

            logger.info("Cache images vidé")


# ═══════════════════════════════════════════════════════════
# HELPERS STREAMLIT
# ═══════════════════════════════════════════════════════════

def optimize_uploaded_image(uploaded_file) -> Tuple[bytes, str]:
    """
    Optimise image uploadée dans Streamlit

    Usage:
        uploaded = st.file_uploader("Image recette")
        if uploaded:
            optimized, url = optimize_uploaded_image(uploaded)

    Returns:
        (données_optimisées, url_display)
    """
    # Lire données
    image_data = uploaded_file.read()

    # Vérifier cache
    cached = ImageCache.get(image_data)

    if cached:
        return cached, "data:image/webp;base64,..."

    # Optimiser
    optimized = ImageOptimizer.optimize(image_data)

    # Cacher
    ImageCache.set(image_data, optimized)

    # Convertir en data URL pour affichage
    import base64
    b64 = base64.b64encode(optimized).decode()
    data_url = f"data:image/webp;base64,{b64}"

    return optimized, data_url


def display_optimized_image(image_data: bytes, caption: str = None):
    """
    Affiche image optimisée dans Streamlit

    Usage:
        display_optimized_image(recette.image_data, "Tarte aux pommes")
    """
    import base64

    # Vérifier si déjà optimisée
    cached = ImageCache.get(image_data)

    if cached:
        data = cached
    else:
        data = ImageOptimizer.optimize(image_data)
        ImageCache.set(image_data, data)

    # Afficher
    b64 = base64.b64encode(data).decode()

    st.markdown(
        f'<img src="data:image/webp;base64,{b64}" '
        f'style="width:100%; border-radius:8px;" '
        f'alt="{caption or ""}" />',
        unsafe_allow_html=True
    )

    if caption:
        st.caption(caption)


# ═══════════════════════════════════════════════════════════
# BATCH OPTIMIZATION
# ═══════════════════════════════════════════════════════════

def batch_optimize_images(image_paths: list[Path], show_progress: bool = True):
    """
    Optimise plusieurs images en batch

    Usage:
        images = Path("images/recettes").glob("*.jpg")
        batch_optimize_images(list(images))
    """
    from src.ui.feedback import ProgressTracker

    if show_progress:
        progress = ProgressTracker("Optimisation images", total=len(image_paths))

    results = {
        "optimized": 0,
        "skipped": 0,
        "errors": 0,
        "total_saved": 0
    }

    for i, image_path in enumerate(image_paths):
        try:
            # Lire image
            original_data = image_path.read_bytes()
            original_size = len(original_data)

            # Optimiser
            optimized_data = ImageOptimizer.optimize(original_data)
            optimized_size = len(optimized_data)

            # Sauvegarder (écraser original ou nouveau fichier)
            output_path = image_path.with_suffix('.webp')
            output_path.write_bytes(optimized_data)

            # Stats
            saved = original_size - optimized_size
            results["total_saved"] += saved
            results["optimized"] += 1

            if show_progress:
                progress.update(
                    i + 1,
                    f"✅ {image_path.name} (-{saved/1024:.1f}KB)"
                )

        except Exception as e:
            logger.error(f"Erreur {image_path}: {e}")
            results["errors"] += 1

            if show_progress:
                progress.update(i + 1, f"❌ {image_path.name}")

    if show_progress:
        progress.complete(
            f"✅ {results['optimized']} images optimisées "
            f"(-{results['total_saved']/1024/1024:.1f}MB)"
        )

    return results


# ═══════════════════════════════════════════════════════════
# STATS & MAINTENANCE
# ═══════════════════════════════════════════════════════════

def get_cache_stats() -> dict:
    """Retourne stats cache images"""
    cache_dir = ImageConfig.CACHE_DIR

    if not cache_dir.exists():
        return {
            "cached_images": 0,
            "total_size": 0
        }

    files = list(cache_dir.glob("*.webp"))
    total_size = sum(f.stat().st_size for f in files)

    return {
        "cached_images": len(files),
        "total_size": total_size,
        "total_size_mb": total_size / 1024 / 1024
    }


def render_image_cache_stats():
    """Affiche stats dans Streamlit"""
    import streamlit as st

    stats = get_cache_stats()

    with st.expander("🖼️ Cache Images"):
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Images Cachées", stats["cached_images"])

        with col2:
            st.metric("Taille Cache", f"{stats['total_size_mb']:.1f}MB")

        if st.button("🗑️ Vider Cache Images"):
            ImageCache.clear()
            st.success("Cache vidé !")
            st.rerun()