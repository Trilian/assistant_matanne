"""
Intégration API Football-Data.org pour les matchs de foot

API gratuite avec limitation:
- 10 requêtes par minute
- Dernières 10 années d'historique
- Tous les championnats majeurs

Docs: https://www.football-data.org/client/register
"""

import logging
from datetime import date, timedelta
from functools import lru_cache
from typing import Any

import requests

logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "https://api.football-data.org/v4"
API_KEY = None  # À configurer dans .env

# Mapping des championnats vers Football-Data codes
CHAMP_MAPPING = {
    "Ligue 1": "FL1",
    "Premier League": "PL",
    "La Liga": "PD",  # PD = Primera Division
    "Serie A": "SA",  # SA = Serie A (Italy)
    "Bundesliga": "BL1",
}

# IDs des compétitions Football-Data (API v4 - TIER_ONE = gratuit)
# Source: GET /competitions - vérifiés le 2025-02-01
COMP_IDS = {
    "FL1": 2015,  # Ligue 1 (France)
    "PL": 2021,  # Premier League (England)
    "PD": 2014,  # Primera Division / La Liga (Spain)
    "SA": 2019,  # Serie A (Italy)
    "BL1": 2002,  # Bundesliga (Germany)
    # Autres disponibles gratuit:
    # "CL": 2001,    # UEFA Champions League
    # "ELC": 2016,   # Championship (England 2nd)
    # "DED": 2003,   # Eredivisie (Netherlands)
    # "PPL": 2017,   # Primeira Liga (Portugal)
    # "BSA": 2013,   # BrasileirÃ£o Série A
}


def configurer_api_key(api_key: str):
    """Configure la clé API Football-Data"""
    global API_KEY
    API_KEY = api_key
    logger.info("âœ… Clé API Football-Data configurée")


def obtenir_cle_api() -> str | None:
    """Obtient la clé API depuis la config"""
    global API_KEY
    if API_KEY:
        return API_KEY

    # Essayer depuis les paramètres
    try:
        from src.core.config import obtenir_parametres

        return obtenir_parametres().FOOTBALL_DATA_API_KEY
    except Exception as e:
        logger.debug(f"Erreur récupération clé API: {e}")
        return None


def faire_requete(endpoint: str, params: dict[str, Any] = None) -> dict | None:
    """
    Fait une requête à l'API Football-Data

    Args:
        endpoint: Chemin de l'endpoint (ex: "/competitions/{id}/matches")
        params: Paramètres de la requête

    Returns:
        JSON ou None si erreur
    """
    api_key = obtenir_cle_api()

    # DEBUG: Log ce qu'on trouve
    logger.info(f"ðŸ”‘ faire_requete: api_key présente = {bool(api_key)}")

    if not api_key:
        logger.warning("âš ï¸ Clé API Football-Data non configurée")
        return None

    url = f"{API_BASE_URL}{endpoint}"
    headers = {"X-Auth-Token": api_key}

    try:
        logger.info(f"ðŸ“¡ Appel API: {endpoint}")
        response = requests.get(url, headers=headers, params=params, timeout=10)

        # Log la réponse même en cas d'erreur
        if response.status_code != 200:
            logger.warning(f"âš ï¸ Statut HTTP {response.status_code} pour {endpoint}")
            try:
                error_detail = response.json()
                logger.debug(f"   Détail erreur API: {error_detail}")
            except:
                logger.debug(f"   Réponse brute: {response.text[:200]}")

        response.raise_for_status()
        logger.info("âœ… Réponse API OK")
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("âš ï¸ Limite de requêtes API dépassée (10/min)")
        elif e.response.status_code == 404:
            logger.error(f"âŒ Endpoint non trouvé (404): {endpoint}")
        else:
            logger.error(f"âŒ Erreur API Football-Data: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"âŒ Erreur requête API: {e}")
        return None


def charger_matchs_a_venir(
    championnat: str, jours: int = 7, statut: str = "SCHEDULED,LIVE"
) -> list[dict[str, Any]]:
    """
    Charge les matchs à venir d'un championnat

    Args:
        championnat: Nom du championnat ("Ligue 1", "Premier League", etc)
        jours: Nombre de jours à chercher
        statut: Filtrer par statut ("SCHEDULED", "LIVE", "FINISHED")

    Returns:
        Liste des matchs
    """
    code_champ = CHAMP_MAPPING.get(championnat)
    if not code_champ:
        logger.warning(f"Championnat non supporté: {championnat}")
        return []

    comp_id = COMP_IDS.get(code_champ)
    if not comp_id:
        return []

    # Paramètres de la requête
    debut = date.today()
    fin = debut + timedelta(days=jours)

    params = {
        "status": statut,
        "dateFrom": debut.isoformat(),
        "dateTo": fin.isoformat(),
    }

    data = faire_requete(f"/competitions/{comp_id}/matches", params)

    if not data:
        return []

    matchs = []
    for m in data.get("matches", []):
        try:
            matchs.append(
                {
                    "id": m.get("id"),
                    "date": m.get("utcDate", "").split("T")[0],
                    "heure": m.get("utcDate", "").split("T")[1][:5]
                    if "T" in m.get("utcDate", "")
                    else None,
                    "championnat": championnat,
                    "equipe_domicile": m.get("homeTeam", {}).get("name"),
                    "equipe_domicile_id": m.get("homeTeam", {}).get("id"),
                    "equipe_exterieur": m.get("awayTeam", {}).get("name"),
                    "equipe_exterieur_id": m.get("awayTeam", {}).get("id"),
                    "statut": m.get("status"),
                    "score_domicile": m.get("score", {}).get("fullTime", {}).get("home"),
                    "score_exterieur": m.get("score", {}).get("fullTime", {}).get("away"),
                    "odds": m.get("odds", {}),
                }
            )
        except Exception as e:
            logger.debug(f"Erreur parsing match: {e}")
            continue

    return matchs


def charger_historique_equipe(nom_equipe: str, limite: int = 10) -> list[dict[str, Any]]:
    """
    Charge l'historique des matchs d'une équipe

    Args:
        nom_equipe: Nom de l'équipe
        limite: Nombre de matchs à récupérer

    Returns:
        Liste des matchs récents
    """
    # Chercher l'ID de l'équipe
    data = faire_requete("/teams", {"name": nom_equipe})

    if not data or not data.get("teams"):
        logger.warning(f"Équipe non trouvée: {nom_equipe}")
        return []

    equipe_id = data["teams"][0].get("id")

    if not equipe_id:
        return []

    # Charger les matchs de l'équipe
    params = {"limit": limite, "status": "FINISHED"}

    data = faire_requete(f"/teams/{equipe_id}/matches", params)

    if not data:
        return []

    matchs = []
    for m in data.get("matches", []):
        try:
            matchs.append(
                {
                    "date": m.get("utcDate", "").split("T")[0],
                    "equipe_domicile": m.get("homeTeam", {}).get("name"),
                    "equipe_domicile_id": m.get("homeTeam", {}).get("id"),
                    "equipe_exterieur": m.get("awayTeam", {}).get("name"),
                    "equipe_exterieur_id": m.get("awayTeam", {}).get("id"),
                    "score_domicile": m.get("score", {}).get("fullTime", {}).get("home"),
                    "score_exterieur": m.get("score", {}).get("fullTime", {}).get("away"),
                }
            )
        except Exception as e:
            logger.debug(f"Erreur parsing match: {e}")
            continue

    return matchs


def charger_classement(championnat: str) -> list[dict[str, Any]]:
    """
    Charge le classement d'un championnat

    Note: L'endpoint /standings n'existe pas en version gratuite.
    On essaie /teams en fallback.

    Args:
        championnat: Nom du championnat

    Returns:
        Liste des équipes avec classement (ou juste équipes si pas de standings)
    """
    code_champ = CHAMP_MAPPING.get(championnat)
    if not code_champ:
        return []

    comp_id = COMP_IDS.get(code_champ)
    if not comp_id:
        return []

    # Essayer d'abord les standings
    logger.info(f"ðŸ“¡ Tentative standings pour {championnat} (ID: {comp_id})")
    data = faire_requete(f"/competitions/{comp_id}/standings")

    if data and data.get("standings"):
        equipes = []
        standings = data.get("standings", [])

        if standings:
            for table in standings:
                for i, equipe in enumerate(table.get("table", []), 1):
                    equipes.append(
                        {
                            "position": i,
                            "nom": equipe.get("team", {}).get("name"),
                            "matchs_joues": equipe.get("playedGames"),
                            "victoires": equipe.get("won"),
                            "nuls": equipe.get("draw"),
                            "defaites": equipe.get("lost"),
                            "buts_marques": equipe.get("goalsFor"),
                            "buts_encaisses": equipe.get("goalsAgainst"),
                            "points": equipe.get("points"),
                        }
                    )

        return equipes

    # Fallback: charger juste les équipes sans standings
    logger.info(f"ðŸ“¡ Fallback /teams pour {championnat}")
    data = faire_requete(f"/competitions/{comp_id}/teams")

    if data and data.get("teams"):
        equipes = []
        for i, equipe in enumerate(data.get("teams", []), 1):
            equipes.append(
                {
                    "position": i,
                    "nom": equipe.get("name"),
                    "matchs_joues": 0,
                    "victoires": 0,
                    "nuls": 0,
                    "defaites": 0,
                    "buts_marques": 0,
                    "buts_encaisses": 0,
                    "points": 0,
                }
            )

        logger.info(f"âœ… {len(equipes)} équipes chargées pour {championnat}")
        return equipes

    logger.warning(f"âŒ Pas de données pour {championnat}")
    return []


def chercher_equipe(nom: str) -> dict[str, Any] | None:
    """
    Cherche une équipe par nom

    Args:
        nom: Nom de l'équipe (partiel accepté)

    Returns:
        Infos de l'équipe ou None
    """
    data = faire_requete("/teams", {"name": nom})

    if not data or not data.get("teams"):
        return None

    equipe = data["teams"][0]

    return {
        "id": equipe.get("id"),
        "nom": equipe.get("name"),
        "nom_court": equipe.get("shortName"),
        "pays": equipe.get("area", {}).get("name"),
        "founded": equipe.get("founded"),
        "logo_url": equipe.get("crest"),
    }


# ═══════════════════════════════════════════════════════════
# MATCHS TERMINÉS (pour refresh scores)
# ═══════════════════════════════════════════════════════════


def charger_matchs_termines(championnat: str, jours: int = 7) -> list[dict[str, Any]]:
    """
    Charge les matchs terminés des derniers jours d'un championnat.
    Utilisé pour mettre à jour les scores.

    Args:
        championnat: Nom du championnat
        jours: Nombre de jours en arrière

    Returns:
        Liste des matchs avec scores
    """
    code_champ = CHAMP_MAPPING.get(championnat)
    if not code_champ:
        logger.warning(f"Championnat non supporté: {championnat}")
        return []

    comp_id = COMP_IDS.get(code_champ)
    if not comp_id:
        return []

    # Paramètres: matchs terminés des X derniers jours
    fin = date.today()
    debut = fin - timedelta(days=jours)

    params = {
        "status": "FINISHED",
        "dateFrom": debut.isoformat(),
        "dateTo": fin.isoformat(),
    }

    data = faire_requete(f"/competitions/{comp_id}/matches", params)

    if not data:
        return []

    matchs = []
    for m in data.get("matches", []):
        try:
            score = m.get("score", {}).get("fullTime", {})
            matchs.append(
                {
                    "date": m.get("utcDate", "").split("T")[0],
                    "equipe_domicile": m.get("homeTeam", {}).get("name"),
                    "equipe_exterieur": m.get("awayTeam", {}).get("name"),
                    "score_domicile": score.get("home"),
                    "score_exterieur": score.get("away"),
                }
            )
        except Exception as e:
            logger.debug(f"Erreur parsing match terminé: {e}")
            continue

    logger.info(f"âœ… {len(matchs)} matchs terminés chargés pour {championnat}")
    return matchs


# ═══════════════════════════════════════════════════════════
# CACHE (éviter trop de requêtes)
# ═══════════════════════════════════════════════════════════


@lru_cache(maxsize=128)
def charger_matchs_cache(championnat: str, jours: int = 7) -> tuple:
    """Version cachée de charger_matchs_a_venir"""
    return tuple(charger_matchs_a_venir(championnat, jours))


def vider_cache():
    """Vide le cache des requêtes"""
    charger_matchs_cache.cache_clear()
