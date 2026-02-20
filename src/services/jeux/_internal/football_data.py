"""
FootballDataService - Service de récupération des données Football-Data.org.

Fournit:
- Liste des compétitions (Ligue 1, Premier League, etc.)
- Résultats des matchs
- Statistiques mi-temps / fin de match pour tracker les séries

API: https://www.football-data.org/documentation/api
Plan gratuit: 10 requêtes/minute, top 5 ligues européennes
"""

import logging
from datetime import date, datetime, timedelta
from enum import Enum, StrEnum

import httpx
from pydantic import BaseModel, Field

from src.core.config import obtenir_parametres

# Types importés depuis la source unique (plus de duplication)
from src.services.jeux._internal.football_types import (
    BASE_URL,
    COMPETITIONS,
    Match,
    ResultatFinal,
    ResultatMiTemps,
    ScoreMatch,
    StatistiquesMarcheData,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════


class FootballDataService:
    """
    Service de récupération des données Football-Data.org.

    Utilise l'API gratuite (10 req/min, top 5 ligues).
    """

    def __init__(self, api_key: str | None = None):
        """
        Initialise le service.

        Args:
            api_key: Clé API Football-Data.org (optionnel, lit depuis config)
        """
        self.api_key = api_key or self._get_api_key()
        self.http_client = httpx.Client(
            timeout=30.0,
            headers={"X-Auth-Token": self.api_key} if self.api_key else {},
        )

    def _get_api_key(self) -> str:
        """Récupère la clé API depuis la configuration."""
        try:
            config = obtenir_parametres()
            return getattr(config, "FOOTBALL_DATA_API_KEY", "")
        except Exception as e:
            logger.debug("Clé API Football indisponible: %s", e)
            return ""

    def _faire_requete(self, endpoint: str, params: dict | None = None) -> dict | None:
        """
        Effectue une requête à l'API.

        Args:
            endpoint: Endpoint API (ex: "/competitions/FL1/matches")
            params: Paramètres de requête

        Returns:
            Données JSON ou None si erreur
        """
        if not self.api_key:
            logger.warning("Pas de clé API Football-Data configurée")
            return None

        url = f"{BASE_URL}{endpoint}"

        try:
            response = self.http_client.get(url, params=params)
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"Erreur HTTP Football-Data: {e.response.status_code}")
            return None
        except httpx.TimeoutException:
            logger.error("Timeout Football-Data API")
            return None
        except Exception as e:
            logger.error(f"Erreur Football-Data: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────
    # RÉCUPÉRATION DES MATCHS
    # ─────────────────────────────────────────────────────────────────

    def obtenir_matchs_termines(
        self,
        competition: str = "FL1",
        date_debut: date | None = None,
        date_fin: date | None = None,
        limite: int = 100,
    ) -> list[Match]:
        """
        Récupère les matchs terminés d'une compétition.

        Args:
            competition: Code compétition (FL1, PL, BL1, SA, PD)
            date_debut: Date de début (défaut: 30 jours avant)
            date_fin: Date de fin (défaut: aujourd'hui)
            limite: Nombre max de matchs

        Returns:
            Liste de Match
        """
        if date_debut is None:
            date_debut = date.today() - timedelta(days=30)
        if date_fin is None:
            date_fin = date.today()

        params = {
            "dateFrom": date_debut.isoformat(),
            "dateTo": date_fin.isoformat(),
            "status": "FINISHED",
        }

        data = self._faire_requete(f"/competitions/{competition}/matches", params)
        if not data:
            return []

        matchs = []
        for m in data.get("matches", [])[:limite]:
            try:
                match = self._parser_match(m, competition)
                if match:
                    matchs.append(match)
            except Exception as e:
                logger.warning(f"Erreur parsing match: {e}")
                continue

        logger.info(f"Récupéré {len(matchs)} matchs pour {competition}")
        return matchs

    def _parser_match(self, data: dict, competition: str) -> Match | None:
        """Parse les données brutes d'un match."""
        try:
            score_data = data.get("score", {})
            half_time = score_data.get("halfTime", {})
            full_time = score_data.get("fullTime", {})

            score = ScoreMatch(
                domicile_mi_temps=half_time.get("home") or 0,
                exterieur_mi_temps=half_time.get("away") or 0,
                domicile_final=full_time.get("home") or 0,
                exterieur_final=full_time.get("away") or 0,
            )

            # Déterminer les résultats
            resultat_mt = self._determiner_resultat(
                score.domicile_mi_temps, score.exterieur_mi_temps
            )
            resultat_final = self._determiner_resultat(score.domicile_final, score.exterieur_final)

            return Match(
                id=data.get("id", 0),
                competition=competition,
                competition_nom=COMPETITIONS.get(competition, competition),
                date_match=datetime.fromisoformat(
                    data.get("utcDate", "").replace("Z", "+00:00")
                ).date(),
                equipe_domicile=data.get("homeTeam", {}).get("shortName", "Inconnu"),
                equipe_exterieur=data.get("awayTeam", {}).get("shortName", "Inconnu"),
                score=score,
                statut=data.get("status", "SCHEDULED"),
                resultat_mi_temps=resultat_mt,
                resultat_final=resultat_final,
            )
        except Exception as e:
            logger.warning(f"Erreur parsing match: {e}")
            return None

    def _determiner_resultat(
        self, score_dom: int, score_ext: int
    ) -> ResultatMiTemps | ResultatFinal | None:
        """Détermine le résultat selon les scores."""
        if score_dom > score_ext:
            return ResultatMiTemps.DOMICILE
        elif score_ext > score_dom:
            return ResultatMiTemps.EXTERIEUR
        else:
            return ResultatMiTemps.NUL

    # ─────────────────────────────────────────────────────────────────
    # CALCUL DES STATISTIQUES POUR SÉRIES
    # ─────────────────────────────────────────────────────────────────

    def calculer_statistiques_marche(
        self, matchs: list[Match], marche: str
    ) -> StatistiquesMarcheData:
        """
        Calcule les statistiques d'un marché sur une liste de matchs.

        Args:
            matchs: Liste de matchs terminés (triés par date croissante)
            marche: Type de marché à analyser

        Returns:
            Statistiques du marché

        Marchés supportés:
            - domicile_mi_temps: Victoire domicile à la mi-temps
            - exterieur_mi_temps: Victoire extérieur à la mi-temps
            - nul_mi_temps: Match nul à la mi-temps
            - domicile_final: Victoire domicile finale
            - exterieur_final: Victoire extérieur finale
            - nul_final: Match nul final
        """
        if not matchs:
            return StatistiquesMarcheData(marche=marche)

        # Trier par date croissante pour calculer la série
        matchs_tries = sorted(matchs, key=lambda m: m.date_match)

        total = len(matchs_tries)
        occurrences = 0
        derniere_occurrence: date | None = None
        serie_actuelle = 0

        for match in matchs_tries:
            if self._match_correspond_marche(match, marche):
                occurrences += 1
                derniere_occurrence = match.date_match
                serie_actuelle = 0  # Reset série
            else:
                serie_actuelle += 1

        frequence = occurrences / total if total > 0 else 0.0

        return StatistiquesMarcheData(
            marche=marche,
            total_matchs=total,
            nb_occurrences=occurrences,
            frequence=round(frequence, 4),
            serie_actuelle=serie_actuelle,
            derniere_occurrence=derniere_occurrence,
        )

    def _match_correspond_marche(self, match: Match, marche: str) -> bool:
        """Vérifie si un match correspond au marché donné."""
        if marche == "domicile_mi_temps":
            return match.resultat_mi_temps == ResultatMiTemps.DOMICILE
        elif marche == "exterieur_mi_temps":
            return match.resultat_mi_temps == ResultatMiTemps.EXTERIEUR
        elif marche == "nul_mi_temps":
            return match.resultat_mi_temps == ResultatMiTemps.NUL
        elif marche == "domicile_final":
            return match.resultat_final == ResultatFinal.DOMICILE
        elif marche == "exterieur_final":
            return match.resultat_final == ResultatFinal.EXTERIEUR
        elif marche == "nul_final":
            return match.resultat_final == ResultatFinal.NUL
        return False

    def calculer_toutes_statistiques(
        self, competition: str = "FL1", jours: int = 365
    ) -> dict[str, StatistiquesMarcheData]:
        """
        Calcule les statistiques de tous les marchés pour une compétition.

        Args:
            competition: Code compétition
            jours: Nombre de jours d'historique

        Returns:
            Dict marché -> statistiques
        """
        date_debut = date.today() - timedelta(days=jours)
        matchs = self.obtenir_matchs_termines(
            competition=competition,
            date_debut=date_debut,
            limite=500,
        )

        if not matchs:
            return {}

        marches = [
            "domicile_mi_temps",
            "exterieur_mi_temps",
            "nul_mi_temps",
            "domicile_final",
            "exterieur_final",
            "nul_final",
        ]

        return {marche: self.calculer_statistiques_marche(matchs, marche) for marche in marches}

    def close(self):
        """Ferme le client HTTP."""
        self.http_client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# ═══════════════════════════════════════════════════════════
# FACTORY (SINGLETON)
# ═══════════════════════════════════════════════════════════

_football_data_instance: FootballDataService | None = None


def obtenir_service_donnees_football(api_key: str | None = None) -> FootballDataService:
    """
    Factory singleton pour le service Football-Data.

    Args:
        api_key: Clé API optionnelle (utilisée seulement à la première création)

    Returns:
        Instance FootballDataService
    """
    global _football_data_instance
    if _football_data_instance is None:
        _football_data_instance = FootballDataService(api_key)
    return _football_data_instance


def get_football_data_service(api_key: str | None = None) -> FootballDataService:
    """
    Factory pour créer une instance du service (alias anglais).

    Args:
        api_key: Clé API optionnelle

    Returns:
        Instance FootballDataService
    """
    return obtenir_service_donnees_football(api_key)


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE COMPATIBILITÉ (rétro-compat avec api_football.py)
# ═══════════════════════════════════════════════════════════

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


def charger_matchs_termines(championnat: str, jours: int = 7) -> list[dict]:
    """
    Charge les matchs terminés des derniers jours.

    Args:
        championnat: Nom du championnat
        jours: Nombre de jours en arrière

    Returns:
        Liste des matchs avec scores
    """
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


def charger_classement(championnat: str) -> list[dict]:
    """
    Charge le classement d'un championnat.

    Args:
        championnat: Nom du championnat

    Returns:
        Liste des équipes avec classement
    """
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


def charger_historique_equipe(nom_equipe: str, limite: int = 10) -> list[dict]:
    """
    Charge l'historique des matchs d'une équipe.

    Args:
        nom_equipe: Nom de l'équipe
        limite: Nombre de matchs à récupérer

    Returns:
        Liste des matchs récents
    """
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


def chercher_equipe(nom: str) -> dict | None:
    """
    Recherche une équipe par son nom.

    Args:
        nom: Nom de l'équipe à chercher

    Returns:
        Dictionnaire avec infos équipe ou None
    """
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
