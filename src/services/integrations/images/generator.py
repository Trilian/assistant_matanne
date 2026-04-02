"""
Générateur d'images pour les recettes
Utilise plusieurs APIs gratuites pour générer des images réelles de haute qualité

Orchestrateur principal — les providers et prompts sont dans:
- providers.py: Fonctions de recherche/génération par API
- prompts.py: Construction de requêtes et prompts IA
"""

import logging
import os

import requests

from src.core.decorators import avec_resilience
from src.services.core.registry import service_factory

# Ré-exports pour backward compatibility (tests importent depuis generator.py)
from .prompts import _construire_prompt_detaille, _construire_query_optimisee  # noqa: F401
from .providers import (  # noqa: F401
    _generer_via_huggingface,
    _generer_via_leonardo,
    _generer_via_pollinations,
    _generer_via_replicate,
)
from .providers import (
    _rechercher_image_pexels as _rechercher_image_pexels_impl,
)
from .providers import (
    _rechercher_image_pixabay as _rechercher_image_pixabay_impl,
)
from .providers import (
    _rechercher_image_unsplash as _rechercher_image_unsplash_impl,
)

logger = logging.getLogger(__name__)


# ─── Chargement centralisé des clés API via le système de config ───


def _get_api_key(key_name: str) -> str | None:
    """Charge une clé API via obtenir_parametres() (cascade .env.local → .env).

    Centralise la résolution en passant par le système de configuration
    du projet plutôt qu'accéder directement aux variables d'environnement.
    """
    try:
        from src.core.config import obtenir_parametres

        params = obtenir_parametres()
        # Tenter d'obtenir la clé depuis les Pydantic settings
        value = getattr(params, key_name, None)
        if value:
            return value
    except Exception as e:
        logger.debug("Config non disponible pour %s: %s", key_name, e)

    # Fallback ultime à os.getenv (pour dev local sans config chargée)
    return os.getenv(key_name)


# APIs configurables
LEONARDO_API_KEY = _get_api_key("LEONARDO_API_KEY")  # Gratuit: https://app.leonardo.ai
PEXELS_API_KEY = _get_api_key("PEXELS_API_KEY")  # Gratuit: https://www.pexels.com/api/
PIXABAY_API_KEY = _get_api_key("PIXABAY_API_KEY")  # Gratuit: https://pixabay.com/api/
UNSPLASH_API_KEY = _get_api_key(
    "UNSPLASH_API_KEY"
)  # Gratuit: https://unsplash.com/oauth/applications

# API status logging (sans leak de clés)
logger.info(
    "Image generator initialisé — Leonardo=%s, Unsplash=%s, Pexels=%s, Pixabay=%s",
    "OK" if LEONARDO_API_KEY else "NON",
    "OK" if UNSPLASH_API_KEY else "NON",
    "OK" if PEXELS_API_KEY else "NON",
    "OK" if PIXABAY_API_KEY else "NON",
)

if UNSPLASH_API_KEY:
    logger.info("Clé Unsplash chargée")
else:
    logger.warning(
        "Clé Unsplash non trouvée - vérifiez UNSPLASH_API_KEY dans .env.local"
    )


# ═══════════════════════════════════════════════════════════
# SERVICE GÉNÉRATEUR D'IMAGES
# ═══════════════════════════════════════════════════════════


class ServiceGenerateurImages:
    """Service de génération/recherche d'images pour les recettes.

    Encapsule la logique de recherche multi-provider avec fallback en cascade.
    Utilise les clés API chargées au niveau du module.

    Example:
        >>> service = get_image_generator_service()
        >>> url = service.generer_image_recette("Tarte aux pommes")
    """

    @avec_resilience(retry=2, timeout_s=60, fallback=None)
    def generer_image_recette(
        self,
        nom_recette: str,
        description: str = "",
        ingredients_list: list | None = None,
        type_plat: str = "",
    ) -> str | None:
        """Génère une image pour une recette avec fallback multi-provider.

        Stratégie optimisée (priorité):
        1. Hugging Face SDXL (gratuit si clé configurée)
        2. Leonardo.AI (spécialisé culinaire)
        3. Banques d'images (Unsplash > Pexels > Pixabay)
        4. Pollinations.ai (génération rapide)
        5. Replicate SDXL (haute qualité)

        Args:
            nom_recette: Nom de la recette
            description: Description courte
            ingredients_list: Liste des ingrédients pour améliorer le contexte
            type_plat: Type de plat (entrée, plat, dessert, etc.)

        Returns:
            URL de l'image ou None
        """
        logger.info(f"🎨 Génération image pour: {nom_recette}")

        search_query = _construire_query_optimisee(nom_recette, ingredients_list, type_plat)

        # Priorité 1: Hugging Face
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            try:
                url = _generer_via_huggingface(
                    nom_recette, description, ingredients_list, type_plat
                )
                if url:
                    logger.info(f"✅ Image générée via Hugging Face pour '{nom_recette}'")
                    return url
            except Exception as e:
                logger.debug(f"HuggingFace failed: {e}")
        else:
            logger.debug("HUGGINGFACE_API_KEY non configurée, passage au fallback")

        # Priorité 2: Leonardo.AI
        if LEONARDO_API_KEY:
            try:
                url = _generer_via_leonardo(nom_recette, description, ingredients_list, type_plat)
                if url:
                    logger.info(f"✅ Image générée via Leonardo.AI pour '{nom_recette}'")
                    return url
            except Exception as e:
                logger.debug(f"Leonardo.AI failed: {e}")

        # Priorité 3: Unsplash
        if UNSPLASH_API_KEY:
            try:
                url = _rechercher_image_unsplash(nom_recette, search_query)
                if url:
                    logger.info(f"✅ Image trouvée via Unsplash pour '{nom_recette}'")
                    return url
            except Exception as e:
                logger.debug(f"Unsplash API failed: {e}")

        # Priorité 4: Pexels
        if PEXELS_API_KEY:
            try:
                url = _rechercher_image_pexels(nom_recette, search_query)
                if url:
                    logger.info(f"✅ Image trouvée via Pexels pour '{nom_recette}'")
                    return url
            except Exception as e:
                logger.debug(f"Pexels API failed: {e}")

        # Priorité 5: Pixabay
        if PIXABAY_API_KEY:
            try:
                url = _rechercher_image_pixabay(nom_recette, search_query)
                if url:
                    logger.info(f"✅ Image trouvée via Pixabay pour '{nom_recette}'")
                    return url
            except Exception as e:
                logger.debug(f"Pixabay API failed: {e}")

        # Priorité 6: Pollinations.ai
        logger.info(f"Génération IA via Pollinations pour: {nom_recette}")
        try:
            result = _generer_via_pollinations(
                nom_recette, description, ingredients_list, type_plat
            )
            if result:
                return result
        except Exception as e:
            logger.debug(f"Pollinations API failed: {e}")

        # Priorité 7: Replicate API
        logger.info(f"Génération IA via Replicate pour: {nom_recette}")
        try:
            result = _generer_via_replicate(nom_recette, description, ingredients_list, type_plat)
            if result:
                return result
        except Exception as e:
            logger.debug(f"Replicate API failed: {e}")

        logger.error(f"❌ Impossible de générer une image pour '{nom_recette}'")
        return None

    @staticmethod
    def telecharger_image(url: str, nom_fichier: str) -> str | None:
        """Télécharge une image depuis une URL et la sauvegarde localement.

        Args:
            url: URL de l'image
            nom_fichier: Nom du fichier à sauvegarder

        Returns:
            Chemin local de l'image ou None si erreur
        """
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                import tempfile

                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                    f.write(response.content)
                    logger.info(f"✅ Image téléchargée: {f.name}")
                    return f.name
        except Exception as e:
            logger.error(f"Erreur téléchargement image: {e}")

        return None


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("image_generator", tags={"integrations", "images"})
def obtenir_image_generator_service() -> ServiceGenerateurImages:
    """Factory singleton pour le service générateur d'images."""
    return ServiceGenerateurImages()


def obtenir_service_generateur_images() -> ServiceGenerateurImages:
    """Alias français pour get_image_generator_service."""
    return get_image_generator_service()


# ═══════════════════════════════════════════════════════════
# FONCTIONS MODULE-LEVEL — Backward compatibility
# (Ces fonctions délèguent au service singleton)
# ═══════════════════════════════════════════════════════════


@avec_resilience(retry=2, timeout_s=60, fallback=None)
def generer_image_recette(
    nom_recette: str, description: str = "", ingredients_list: list = None, type_plat: str = ""
) -> str | None:
    """Génère une image pour une recette (backward compat, délègue au service)."""
    service = get_image_generator_service()
    return service.generer_image_recette(nom_recette, description, ingredients_list, type_plat)


def telecharger_image_depuis_url(url: str, nom_fichier: str) -> str | None:
    """Télécharge une image depuis une URL (backward compat, délègue au service)."""
    return ServiceGenerateurImages.telecharger_image(url, nom_fichier)


# ═══════════════════════════════════════════════════════════
# WRAPPERS RECHERCHE — Passent la clé API module-level aux providers
# (backward compat: tests importent ces fonctions depuis generator.py)
# ═══════════════════════════════════════════════════════════


def _rechercher_image_pexels(nom_recette: str, search_query: str = "") -> str | None:
    """Recherche image Pexels (délègue à providers.py)."""
    return _rechercher_image_pexels_impl(nom_recette, search_query, api_key=PEXELS_API_KEY)


def _rechercher_image_pixabay(nom_recette: str, search_query: str = "") -> str | None:
    """Recherche image Pixabay (délègue à providers.py)."""
    return _rechercher_image_pixabay_impl(nom_recette, search_query, api_key=PIXABAY_API_KEY)


def _rechercher_image_unsplash(nom_recette: str, search_query: str = "") -> str | None:
    """Recherche image Unsplash (délègue à providers.py)."""
    return _rechercher_image_unsplash_impl(nom_recette, search_query, api_key=UNSPLASH_API_KEY)


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_image_generator_service = obtenir_image_generator_service  # alias rétrocompatibilité 
