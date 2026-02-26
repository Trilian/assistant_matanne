"""
Utilitaires d'integration pour les pages UI
Fourni des wrappers simples avec fallback automatique BD <-> API
"""

import logging
from datetime import date, timedelta
from typing import Any

import streamlit as st

from src.core.caching import obtenir_cache
from src.core.decorators import avec_cache
from src.core.state import rerun

logger = logging.getLogger(__name__)


@avec_cache(ttl=1800)  # 30 min
def charger_matchs_avec_fallback(
    championnat: str, jours: int = 7, prefer_api: bool = True
) -> tuple[list[dict[str, Any]], str]:
    """
    Charge les matchs avec fallback BD si API echoue

    Args:
        championnat: Nom du championnat
        jours: Nombre de jours
        prefer_api: Preferer l'API si disponible

    Returns:
        (liste_matchs, source) où source = "API" ou "BD"
    """
    matchs = []
    source = "BD"

    if prefer_api:
        try:
            from src.services.jeux import (
                charger_matchs_a_venir as charger_matchs_depuis_api,
            )

            matchs = charger_matchs_depuis_api(championnat, jours)
            source = "API"
            logger.info(f"✅ {len(matchs)} matchs depuis API")
        except Exception as e:
            logger.warning(f"⚠️ API echouee: {e}, passage à la BD")

    # Fallback à la BD
    if not matchs:
        try:
            from src.services.jeux import get_paris_crud_service

            service = get_paris_crud_service()
            matchs = service.charger_matchs_fallback(championnat, jours)
            source = "BD"
            logger.info(f"✅ {len(matchs)} matchs depuis BD")

        except Exception as e:
            logger.error(f"❌ Erreur fallback BD: {e}")

    return (matchs, source)


@avec_cache(ttl=3600)  # 1 heure
def charger_classement_avec_fallback(championnat: str) -> tuple[list[dict], str]:
    """
    Charge le classement avec fallback API -> BD
    """
    classement = []
    source = "BD"

    # Essayer API d'abord
    try:
        from src.services.jeux import (
            charger_classement as charger_classement_depuis_api,
        )

        classement = charger_classement_depuis_api(championnat)
        if classement:
            source = "API"
            return (classement, source)
    except Exception as e:
        logger.debug(f"API classement echouee: {e}")

    # Fallback BD
    try:
        from src.services.jeux import get_paris_crud_service

        service = get_paris_crud_service()
        classement = service.charger_classement_fallback(championnat)
        if classement:
            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur classement BD: {e}")

    return (classement, source)


@avec_cache(ttl=1800)  # 30 min
def charger_historique_equipe_avec_fallback(nom_equipe: str) -> tuple[list[dict], str]:
    """
    Charge l'historique d'une equipe avec fallback API -> BD
    """
    historique = []
    source = "BD"

    # Essayer API
    try:
        from src.services.jeux import (
            charger_historique_equipe as charger_historique_equipe_depuis_api,
        )

        historique = charger_historique_equipe_depuis_api(nom_equipe)
        if historique:
            source = "API"
            return (historique, source)
    except Exception as e:
        logger.debug(f"API historique echouee: {e}")

    # Fallback BD
    try:
        from src.services.jeux import get_paris_crud_service

        service = get_paris_crud_service()
        historique = service.charger_historique_equipe_fallback(nom_equipe)
        if historique:
            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur historique BD: {e}")

    return (historique, source)


@avec_cache(ttl=3600)  # 1 heure
def charger_tirages_loto_avec_fallback(limite: int = 50) -> tuple[list[dict], str]:
    """
    Charge les tirages Loto avec fallback Scraper -> BD
    """
    tirages = []
    source = "BD"

    # Essayer le scraper
    try:
        from src.modules.jeux.scraper_loto import charger_tirages_loto

        tirages = charger_tirages_loto(limite)
        if tirages:
            source = "Scraper FDJ"
            return (tirages, source)
    except Exception as e:
        logger.debug(f"⚠️ Scraper FDJ echoue: {e}")

    # Fallback BD
    try:
        from src.services.jeux import get_loto_crud_service

        service = get_loto_crud_service()
        tirages = service.charger_tirages_fallback(limite)
        if tirages:
            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur tirages BD: {e}")

    return (tirages, source)


@avec_cache(ttl=3600)  # 1 heure
def charger_stats_loto_avec_fallback(limite: int = 50) -> tuple[dict, str]:
    """
    Charge les stats Loto (frequences, paires, etc)
    """
    stats = {}
    source = "BD"

    # Essayer le scraper
    try:
        from src.modules.jeux.scraper_loto import obtenir_statistiques_loto

        stats = obtenir_statistiques_loto(limite)
        if stats:
            source = "Scraper FDJ"
            return (stats, source)
    except Exception as e:
        logger.debug(f"⚠️ Stats scraper echouees: {e}")

    # Fallback BD
    try:
        from src.services.jeux import get_loto_crud_service

        service = get_loto_crud_service()
        stats = service.charger_stats_fallback()
        if stats:
            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur stats BD: {e}")

    return (stats, source)


def bouton_actualiser_api(cle: str):
    """
    Affiche un bouton "Actualiser" et nettoie le cache si clique

    Usage:
        if bouton_actualiser_api("matchs_ligue1"):
            rerun()
    """
    if st.button("🔄 Actualiser depuis API"):
        obtenir_cache().invalidate(pattern="charger_")
        st.session_state[f"{cle}_updated"] = True
        return True
    return False


def message_source_donnees(source: str):
    """Affiche le badge de source des donnees"""
    emoji = "🌐" if source == "API" else "💾" if source == "BD" else "🕷️"
    st.caption(f"{emoji} Donnees depuis: **{source}**")
