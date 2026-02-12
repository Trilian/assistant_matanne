"""
IntÃegration des modules jeux dans l'app principale

Ce fichier est importÃe par app.py pour enregistrer les routes
"""

def configurer_jeux():
    """Configure les APIs et les donnÃees initiales du module Jeux"""
    
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        # Configurer la clÃe API Football-Data si disponible
        from src.core.config import obtenir_parametres
        from src.modules.jeux.api_football import configurer_api_key
        
        config = obtenir_parametres()
        api_key = config.get("FOOTBALL_DATA_API_KEY")
        
        if api_key:
            configurer_api_key(api_key)
            logger.debug("âœ… Football-Data API configurÃee")
        else:
            logger.debug("âš ï¸  Football-Data API non configurÃee (fallback BD utilisÃe)")
    
    except Exception as e:
        logger.debug(f"Note: {e}")


# Appeler au dÃemarrage
configurer_jeux()
