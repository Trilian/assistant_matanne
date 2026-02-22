"""
Fonctions de synchronisation avec l'API Football-Data.

Délègue au service ParisCrudService pour la persistance DB.
"""

from src.services.jeux import get_paris_crud_service

from .utils import (
    CHAMPIONNATS,
    Dict,
    api_charger_classement,
    api_charger_matchs_a_venir,
    charger_matchs_termines,
    date,
    logger,
    st,
)


def sync_equipes_depuis_api(championnat: str) -> int:
    """
    Synchronise TOUTES les equipes d'un championnat depuis l'API.
    Ajoute les nouvelles, met à jour les existantes.

    Returns:
        Nombre d'equipes ajoutees/mises à jour
    """
    try:
        logger.info(f"🔄 Synchronisation des equipes: {championnat}")

        classement = api_charger_classement(championnat)
        if not classement:
            msg = f"⚠️ Impossible de charger {championnat} via API.\n💡 Conseil: Configurer FOOTBALL_DATA_API_KEY dans .env pour synchroniser depuis l'API Football-Data.org"
            logger.warning(msg)
            return 0

        service = get_paris_crud_service()
        return service.sync_equipes_depuis_api(championnat, classement)

    except Exception as e:
        logger.error(f"❌ Erreur sync equipes: {e}")
        return 0


def sync_tous_championnats() -> Dict[str, int]:
    """Synchronise TOUS les championnats d'un coup."""
    resultats = {}
    for champ in CHAMPIONNATS:
        count = sync_equipes_depuis_api(champ)
        resultats[champ] = count
    return resultats


def sync_matchs_a_venir(jours: int = 7) -> Dict[str, int]:
    """
    Synchronise les matchs à venir depuis l'API pour tous les championnats.

    Returns:
        Dictionnaire {championnat: nb_matchs_ajoutes}
    """
    resultats = {}
    service = get_paris_crud_service()

    try:
        for champ in CHAMPIONNATS:
            try:
                matchs_api = api_charger_matchs_a_venir(champ, jours=jours)
                count = service.sync_matchs_a_venir(champ, matchs_api)
                resultats[champ] = count
            except Exception as e:
                logger.debug(f"Erreur sync {champ}: {e}")
                resultats[champ] = 0

        total = sum(resultats.values())
        logger.info(f"✅ {total} nouveaux matchs synchronises")

    except Exception as e:
        logger.error(f"❌ Erreur sync matchs: {e}")

    return resultats


def refresh_scores_matchs() -> int:
    """
    Met à jour les scores des matchs termines depuis l'API Football-Data.

    Returns:
        Nombre de matchs mis à jour
    """
    try:
        # Récupérer les matchs terminés pour chaque championnat
        matchs_api_par_champ = {}
        for champ in CHAMPIONNATS:
            try:
                matchs_api_par_champ[champ] = charger_matchs_termines(champ, jours=14)
            except Exception as e:
                logger.debug(f"Erreur API {champ}: {e}")

        service = get_paris_crud_service()
        count = service.refresh_scores_matchs(matchs_api_par_champ)

        if count > 0:
            logger.info(f"✅ {count} matchs mis à jour avec scores")
        else:
            logger.info("ℹ️ Aucun score trouve dans l'API")

        return count

    except Exception as e:
        logger.error(f"❌ Erreur refresh scores: {e}")
        return 0


__all__ = [
    "sync_equipes_depuis_api",
    "sync_tous_championnats",
    "sync_matchs_a_venir",
    "refresh_scores_matchs",
]
