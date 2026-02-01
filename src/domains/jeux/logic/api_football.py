"""
Intégration API Football-Data.org pour les matchs de foot

API gratuite avec limitation:
- 10 requêtes par minute
- Dernières 10 années d'historique
- Tous les championnats majeurs

Docs: https://www.football-data.org/client/register
"""

import requests
from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "https://api.football-data.org/v4"
API_KEY = None  # À configurer dans .env

# Mapping des championnats vers Football-Data codes
CHAMP_MAPPING = {
    "Ligue 1": "FL1",
    "Premier League": "PL",
    "La Liga": "SA",
    "Serie A": "IT",
    "Bundesliga": "BL1",
}

# IDs des compétitions Football-Data (API gratuite v4 - 5 grands championnats)
COMP_IDS = {
    "FL1": 445,      # Ligue 1
    "PL": 39,        # Premier League
    "SA": 141,       # La Liga (Spain)
    "IT": 135,       # Serie A (Italy)
    "BL1": 25,       # Bundesliga
    # Note: CL (8) et EL non disponibles avec API gratuite
}


def configurer_api_key(api_key: str):
    """Configure la clé API Football-Data"""
    global API_KEY
    API_KEY = api_key
    logger.info("✅ Clé API Football-Data configurée")


def obtenir_cle_api() -> Optional[str]:
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


def faire_requete(endpoint: str, params: Dict[str, Any] = None) -> Optional[Dict]:
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
    logger.info(f"🔑 faire_requete: api_key présente = {bool(api_key)}")
    
    if not api_key:
        logger.warning("⚠️ Clé API Football-Data non configurée")
        return None
    
    url = f"{API_BASE_URL}{endpoint}"
    headers = {"X-Auth-Token": api_key}
    
    try:
        logger.info(f"📡 Appel API: {endpoint}")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        # Log la réponse même en cas d'erreur
        if response.status_code != 200:
            logger.warning(f"⚠️ Statut HTTP {response.status_code} pour {endpoint}")
            try:
                error_detail = response.json()
                logger.debug(f"   Détail erreur API: {error_detail}")
            except:
                logger.debug(f"   Réponse brute: {response.text[:200]}")
        
        response.raise_for_status()
        logger.info(f"✅ Réponse API OK")
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logger.warning("⚠️ Limite de requêtes API dépassée (10/min)")
        elif e.response.status_code == 404:
            logger.error(f"❌ Endpoint non trouvé (404): {endpoint}")
        else:
            logger.error(f"❌ Erreur API Football-Data: {e.response.status_code}")
        return None
    except Exception as e:
        logger.error(f"❌ Erreur requête API: {e}")
        return None


def charger_matchs_a_venir(
    championnat: str,
    jours: int = 7,
    statut: str = "SCHEDULED,LIVE"
) -> List[Dict[str, Any]]:
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
            matchs.append({
                "id": m.get("id"),
                "date": m.get("utcDate", "").split("T")[0],
                "heure": m.get("utcDate", "").split("T")[1][:5] if "T" in m.get("utcDate", "") else None,
                "championnat": championnat,
                "equipe_domicile": m.get("homeTeam", {}).get("name"),
                "equipe_domicile_id": m.get("homeTeam", {}).get("id"),
                "equipe_exterieur": m.get("awayTeam", {}).get("name"),
                "equipe_exterieur_id": m.get("awayTeam", {}).get("id"),
                "statut": m.get("status"),
                "score_domicile": m.get("score", {}).get("fullTime", {}).get("home"),
                "score_exterieur": m.get("score", {}).get("fullTime", {}).get("away"),
                "odds": m.get("odds", {}),
            })
        except Exception as e:
            logger.debug(f"Erreur parsing match: {e}")
            continue
    
    return matchs


def charger_historique_equipe(nom_equipe: str, limite: int = 10) -> List[Dict[str, Any]]:
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
    params = {
        "limit": limite,
        "status": "FINISHED"
    }
    
    data = faire_requete(f"/teams/{equipe_id}/matches", params)
    
    if not data:
        return []
    
    matchs = []
    for m in data.get("matches", []):
        try:
            matchs.append({
                "date": m.get("utcDate", "").split("T")[0],
                "equipe_domicile": m.get("homeTeam", {}).get("name"),
                "equipe_domicile_id": m.get("homeTeam", {}).get("id"),
                "equipe_exterieur": m.get("awayTeam", {}).get("name"),
                "equipe_exterieur_id": m.get("awayTeam", {}).get("id"),
                "score_domicile": m.get("score", {}).get("fullTime", {}).get("home"),
                "score_exterieur": m.get("score", {}).get("fullTime", {}).get("away"),
            })
        except Exception as e:
            logger.debug(f"Erreur parsing match: {e}")
            continue
    
    return matchs


def charger_classement(championnat: str) -> List[Dict[str, Any]]:
    """
    Charge le classement d'un championnat
    
    Args:
        championnat: Nom du championnat
        
    Returns:
        Liste des équipes avec classement
    """
    code_champ = CHAMP_MAPPING.get(championnat)
    if not code_champ:
        return []
    
    comp_id = COMP_IDS.get(code_champ)
    if not comp_id:
        return []
    
    data = faire_requete(f"/competitions/{comp_id}/standings")
    
    if not data:
        return []
    
    equipes = []
    standings = data.get("standings", [])
    
    if standings:
        for table in standings:
            for i, equipe in enumerate(table.get("table", []), 1):
                equipes.append({
                    "position": i,
                    "nom": equipe.get("team", {}).get("name"),
                    "matchs_joues": equipe.get("playedGames"),
                    "victoires": equipe.get("won"),
                    "nuls": equipe.get("draw"),
                    "defaites": equipe.get("lost"),
                    "buts_marques": equipe.get("goalsFor"),
                    "buts_encaisses": equipe.get("goalsAgainst"),
                    "points": equipe.get("points")
                })
    
    return equipes


def chercher_equipe(nom: str) -> Optional[Dict[str, Any]]:
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
        "logo_url": equipe.get("crest")
    }


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
