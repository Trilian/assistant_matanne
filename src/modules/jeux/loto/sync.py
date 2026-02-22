"""
Module Loto - Synchronisation des tirages

Délègue au service LotoCrudService pour la persistance DB.
"""

import logging

from src.modules.jeux.scraper_loto import charger_tirages_loto
from src.services.jeux import get_loto_crud_service

logger = logging.getLogger(__name__)


def sync_tirages_loto(limite: int = 50) -> int:
    """
    Synchronise les derniers tirages du Loto FDJ depuis le web.

    Args:
        limite: Nombre de tirages à recuperer (max 100)

    Returns:
        Nombre de nouveaux tirages ajoutes
    """
    try:
        logger.info(f"🔄 Synchronisation Loto: recuperation {limite} derniers tirages")

        # Charger les tirages depuis le web/API FDJ
        tirages_api = charger_tirages_loto(limite=limite)

        if not tirages_api:
            logger.warning("⚠️ Pas de donnees Loto trouvees")
            return 0

        # Déléguer l'insertion au service
        service = get_loto_crud_service()
        count = service.sync_tirages(tirages_api)
        return count

    except Exception as e:
        logger.error(f"❌ Erreur sync Loto: {e}")
        return 0
