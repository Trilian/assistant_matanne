"""
Utilitaires d'integration pour les pages UI
Fourni des wrappers simples avec fallback automatique BD <-> API
"""

import logging
from datetime import date, timedelta
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)


@st.cache_data(ttl=1800)  # 30 min
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
            from src.services.jeux.football_data import charger_matchs_a_venir as charger_matchs_depuis_api

            matchs = charger_matchs_depuis_api(championnat, jours)
            source = "API"
            logger.info(f"✅ {len(matchs)} matchs depuis API")
        except Exception as e:
            logger.warning(f"⚠️ API echouee: {e}, passage à la BD")

    # Fallback à la BD
    if not matchs:
        try:
            from src.core.database import obtenir_contexte_db
            from src.core.models import Match

            debut = date.today()
            fin = debut + timedelta(days=jours)

            with obtenir_contexte_db() as session:
                matches_bd = (
                    session.query(Match)
                    .filter(
                        Match.date_match >= debut,
                        Match.date_match <= fin,
                        Match.championnat == championnat,
                        Match.joue == False,
                    )
                    .order_by(Match.date_match, Match.heure)
                    .all()
                )

                for m in matches_bd:
                    matchs.append(
                        {
                            "id": m.id,
                            "date": str(m.date_match),
                            "heure": str(m.heure) if m.heure else "",
                            "championnat": m.championnat,
                            "dom_nom": m.equipe_domicile.nom if m.equipe_domicile else "?",
                            "ext_nom": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                            "cote_dom": m.cote_domicile or 1.8,
                            "cote_nul": m.cote_nul or 3.5,
                            "cote_ext": m.cote_exterieur or 4.2,
                            "source": "BD",
                        }
                    )

                source = "BD"
                logger.info(f"✅ {len(matchs)} matchs depuis BD")

        except Exception as e:
            logger.error(f"❌ Erreur fallback BD: {e}")

    return (matchs, source)


@st.cache_data(ttl=3600)  # 1 heure
def charger_classement_avec_fallback(championnat: str) -> tuple[list[dict], str]:
    """
    Charge le classement avec fallback API -> BD
    """
    classement = []
    source = "BD"

    # Essayer API d'abord
    try:
        from src.services.jeux.football_data import charger_classement as charger_classement_depuis_api

        classement = charger_classement_depuis_api(championnat)
        if classement:
            source = "API"
            return (classement, source)
    except Exception as e:
        logger.debug(f"API classement echouee: {e}")

    # Fallback BD
    try:
        from src.core.database import obtenir_contexte_db
        from src.core.models import Equipe

        with obtenir_contexte_db() as session:
            equipes = (
                session.query(Equipe)
                .filter_by(championnat=championnat)
                .order_by(Equipe.points.desc(), Equipe.buts_marques.desc())
                .all()
            )

            for i, e in enumerate(equipes, 1):
                classement.append(
                    {
                        "position": i,
                        "nom": e.nom,
                        "matchs_joues": e.matchs_joues,
                        "victoires": e.victoires,
                        "nuls": e.nuls,
                        "defaites": e.defaites,
                        "buts_marques": e.buts_marques,
                        "buts_encaisses": e.buts_encaisses,
                        "points": e.points,
                    }
                )

            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur classement BD: {e}")

    return (classement, source)


@st.cache_data(ttl=1800)  # 30 min
def charger_historique_equipe_avec_fallback(nom_equipe: str) -> tuple[list[dict], str]:
    """
    Charge l'historique d'une equipe avec fallback API -> BD
    """
    historique = []
    source = "BD"

    # Essayer API
    try:
        from src.services.jeux.football_data import charger_historique_equipe as charger_historique_equipe_depuis_api

        historique = charger_historique_equipe_depuis_api(nom_equipe)
        if historique:
            source = "API"
            return (historique, source)
    except Exception as e:
        logger.debug(f"API historique echouee: {e}")

    # Fallback BD
    try:
        from src.core.database import obtenir_contexte_db
        from src.core.models import Match

        with obtenir_contexte_db() as session:
            matches = (
                session.query(Match)
                .filter(
                    (Match.equipe_domicile.has(nom=nom_equipe))
                    | (Match.equipe_exterieur.has(nom=nom_equipe))
                )
                .filter(Match.joue == True)
                .order_by(Match.date_match.desc())
                .limit(10)
                .all()
            )

            for m in matches:
                historique.append(
                    {
                        "date": str(m.date_match),
                        "equipe_domicile": m.equipe_domicile.nom if m.equipe_domicile else "?",
                        "equipe_exterieur": m.equipe_exterieur.nom if m.equipe_exterieur else "?",
                        "score_domicile": m.score_domicile,
                        "score_exterieur": m.score_exterieur,
                    }
                )

            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur historique BD: {e}")

    return (historique, source)


@st.cache_data(ttl=3600)  # 1 heure
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
        from src.core.database import obtenir_contexte_db
        from src.core.models import TirageLoto

        with obtenir_contexte_db() as session:
            tirages_bd = (
                session.query(TirageLoto).order_by(TirageLoto.date.desc()).limit(limite).all()
            )

            for t in tirages_bd:
                tirages.append(
                    {
                        "date": str(t.date),
                        "numeros": t.numeros,
                        "numero_chance": t.numero_chance,
                        "source": "BD",
                    }
                )

            source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur tirages BD: {e}")

    return (tirages, source)


@st.cache_data(ttl=3600)  # 1 heure
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
        from src.core.database import obtenir_contexte_db
        from src.core.models import StatistiquesLoto

        with obtenir_contexte_db() as session:
            stat_entry = (
                session.query(StatistiquesLoto)
                .filter_by(type_stat="frequences")
                .order_by(StatistiquesLoto.id.desc())
                .first()
            )

            if stat_entry:
                stats = stat_entry.donnees_json
                source = "BD"

    except Exception as e:
        logger.error(f"❌ Erreur stats BD: {e}")

    return (stats, source)


def bouton_actualiser_api(cle: str):
    """
    Affiche un bouton "Actualiser" et nettoie le cache si clique

    Usage:
        if bouton_actualiser_api("matchs_ligue1"):
            st.rerun()
    """
    if st.button("🔄 Actualiser depuis API"):
        st.cache_data.clear()
        st.session_state[f"{cle}_updated"] = True
        return True
    return False


def message_source_donnees(source: str):
    """Affiche le badge de source des donnees"""
    emoji = "🌐" if source == "API" else "💾" if source == "BD" else "🕷️"
    st.caption(f"{emoji} Donnees depuis: **{source}**")
