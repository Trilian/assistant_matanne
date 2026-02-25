"""
Fonctions de compatibilité rétro-compat avec l'ancien api_football.py.

Extrait de football_data.py pour réduire sa taille.
Contient les fonctions module-level de compatibilité:
- charger_matchs_a_venir
- charger_matchs_termines
- charger_classement
- charger_historique_equipe
- chercher_equipe
- configurer_api_key / obtenir_cle_api
- vider_cache
"""

import logging
from datetime import date, timedelta

from src.core.config import obtenir_parametres
from src.core.decorators import avec_cache

logger = logging.getLogger(__name__)


# Mapping des championnats (nom -> code API)
CHAMP_MAPPING = {
    "Ligue 1": "FL1",
    "Premier League": "PL",
    "La Liga": "PD",
    "Serie A": "SA",
    "Bundesliga": "BL1",
}

# Variable globale pour la clé API (compatibilité)
_API_KEY: str | None = None


def configurer_api_key(api_key: str) -> None:
    """Configure la clé API Football-Data (fonction de compatibilité)."""
    global _API_KEY
    _API_KEY = api_key
    logger.info("✅ Clé API Football-Data configurée")


def obtenir_cle_api() -> str | None:
    """Obtient la clé API depuis la config ou variable globale."""
    global _API_KEY
    if _API_KEY:
        return _API_KEY
    try:
        return obtenir_parametres().FOOTBALL_DATA_API_KEY
    except Exception as e:
        logger.debug("Clé API Football indisponible: %s", e)
        return None


@avec_cache(ttl=300, key_prefix="football_data_matchs_a_venir")
def charger_matchs_a_venir(
    championnat: str, jours: int = 7, statut: str = "SCHEDULED,LIVE"
) -> list[dict]:
    """
    Charge les matchs à venir d'un championnat (fonction de compatibilité).

    Args:
        championnat: Nom du championnat ("Ligue 1", "Premier League", etc)
        jours: Nombre de jours à chercher
        statut: Filtrer par statut

    Returns:
        Liste des matchs au format dict
    """
    from .football_data import get_football_data_service

    code = CHAMP_MAPPING.get(championnat)
    if not code:
        logger.warning(f"Championnat non supporté: {championnat}")
        return []

    service = get_football_data_service()
    date_debut = date.today()
    date_fin = date_debut + timedelta(days=jours)

    params = {
        "dateFrom": date_debut.isoformat(),
        "dateTo": date_fin.isoformat(),
        "status": statut,
    }

    data = service._faire_requete(f"/competitions/{code}/matches", params)
    if not data:
        return []

    matchs = []
    for m in data.get("matches", []):
        try:
            utc_date = m.get("utcDate", "")
            matchs.append(
                {
                    "id": m.get("id"),
                    "date": utc_date.split("T")[0] if "T" in utc_date else utc_date,
                    "heure": utc_date.split("T")[1][:5] if "T" in utc_date else None,
                    "championnat": championnat,
                    "equipe_domicile": m.get("homeTeam", {}).get("name"),
                    "equipe_domicile_id": m.get("homeTeam", {}).get("id"),
                    "equipe_exterieur": m.get("awayTeam", {}).get("name"),
                    "equipe_exterieur_id": m.get("awayTeam", {}).get("id"),
                    "statut": m.get("status"),
                    "score_domicile": m.get("score", {}).get("fullTime", {}).get("home"),
                    "score_exterieur": m.get("score", {}).get("fullTime", {}).get("away"),
                }
            )
        except Exception as e:
            logger.debug(f"Erreur parsing match: {e}")
    return matchs


@avec_cache(ttl=300, key_prefix="football_data_matchs_termines")
def charger_matchs_termines(championnat: str, jours: int = 7) -> list[dict]:
    """
    Charge les matchs terminés des derniers jours.

    Args:
        championnat: Nom du championnat
        jours: Nombre de jours en arrière

    Returns:
        Liste des matchs avec scores
    """
    from .football_data import get_football_data_service

    code = CHAMP_MAPPING.get(championnat)
    if not code:
        return []

    service = get_football_data_service()
    date_fin = date.today()
    date_debut = date_fin - timedelta(days=jours)

    params = {
        "status": "FINISHED",
        "dateFrom": date_debut.isoformat(),
        "dateTo": date_fin.isoformat(),
    }

    data = service._faire_requete(f"/competitions/{code}/matches", params)
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
    return matchs


@avec_cache(ttl=600, key_prefix="football_data_classement")
def charger_classement(championnat: str) -> list[dict]:
    """
    Charge le classement d'un championnat.

    Args:
        championnat: Nom du championnat

    Returns:
        Liste des équipes avec classement
    """
    from .football_data import get_football_data_service

    code = CHAMP_MAPPING.get(championnat)
    if not code:
        return []

    service = get_football_data_service()
    data = service._faire_requete(f"/competitions/{code}/standings")

    if data and data.get("standings"):
        equipes = []
        for table in data.get("standings", []):
            for i, eq in enumerate(table.get("table", []), 1):
                equipes.append(
                    {
                        "position": i,
                        "nom": eq.get("team", {}).get("name"),
                        "matchs_joues": eq.get("playedGames"),
                        "victoires": eq.get("won"),
                        "nuls": eq.get("draw"),
                        "defaites": eq.get("lost"),
                        "buts_marques": eq.get("goalsFor"),
                        "buts_encaisses": eq.get("goalsAgainst"),
                        "points": eq.get("points"),
                    }
                )
        return equipes

    # Fallback: charger les équipes sans classement
    data = service._faire_requete(f"/competitions/{code}/teams")
    if data and data.get("teams"):
        return [
            {"position": i, "nom": eq.get("name"), "matchs_joues": 0, "points": 0}
            for i, eq in enumerate(data.get("teams", []), 1)
        ]
    return []


@avec_cache(ttl=600, key_prefix="football_data_historique")
def charger_historique_equipe(nom_equipe: str, limite: int = 10) -> list[dict]:
    """
    Charge l'historique des matchs d'une équipe.

    Args:
        nom_equipe: Nom de l'équipe
        limite: Nombre de matchs à récupérer

    Returns:
        Liste des matchs récents
    """
    from .football_data import get_football_data_service

    service = get_football_data_service()
    data = service._faire_requete("/teams", {"name": nom_equipe})

    if not data or not data.get("teams"):
        return []

    equipe_id = data["teams"][0].get("id")
    if not equipe_id:
        return []

    data = service._faire_requete(
        f"/teams/{equipe_id}/matches", {"limit": limite, "status": "FINISHED"}
    )
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
    return matchs


@avec_cache(ttl=600, key_prefix="football_data_equipe")
def chercher_equipe(nom: str) -> dict | None:
    """
    Recherche une équipe par son nom.

    Args:
        nom: Nom de l'équipe à chercher

    Returns:
        Dictionnaire avec infos équipe ou None
    """
    from .football_data import get_football_data_service

    service = get_football_data_service()
    data = service._faire_requete("/teams", {"name": nom})

    if not data or not data.get("teams"):
        return None

    eq = data["teams"][0]
    return {
        "id": eq.get("id"),
        "nom": eq.get("name"),
        "nom_court": eq.get("shortName"),
        "tla": eq.get("tla"),
        "crest": eq.get("crest"),
    }


def vider_cache() -> None:
    """Vide le cache des requêtes (no-op, gardé pour compatibilité)."""
    pass
