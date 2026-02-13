"""
Intégration des modules jeux dans l'app principale

Ce fichier est importé par app.py pour enregistrer les routes
"""


def configurer_jeux():
    """Configure les APIs et les données initiales du module Jeux"""

    import logging

    logger = logging.getLogger(__name__)

    try:
        # Configurer la clé API Football-Data si disponible
        from src.core.config import obtenir_parametres
        from src.modules.jeux.api_football import configurer_api_key

        config = obtenir_parametres()
        api_key = config.get("FOOTBALL_DATA_API_KEY")

        if api_key:
            configurer_api_key(api_key)
            logger.debug("✅ Football-Data API configurée")
        else:
            logger.debug("⚠️  Football-Data API non configurée (fallback BD utilisé)")

    except Exception as e:
        logger.debug(f"Note: {e}")


# Appeler au démarrage
configurer_jeux()
