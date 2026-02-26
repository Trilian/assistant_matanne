"""
Service de suivi des cotes en temps réel — The Odds API

API gratuite: 500 requêtes/mois (the-odds-api.com)
Fournit les cotes de 20+ bookmakers, pré-match et in-play.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx

from src.core.decorators import avec_resilience, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# The Odds API configuration
BASE_URL = "https://api.the-odds-api.com/v4"
SPORTS_FOOTBALL = [
    "soccer_france_ligue_one",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_italy_serie_a",
    "soccer_germany_bundesliga",
    "soccer_uefa_champs_league",
]

# Mapping vers nos championnats internes
MAPPING_CHAMPIONNATS = {
    "soccer_france_ligue_one": "Ligue 1",
    "soccer_epl": "Premier League",
    "soccer_spain_la_liga": "La Liga",
    "soccer_italy_serie_a": "Serie A",
    "soccer_germany_bundesliga": "Bundesliga",
    "soccer_uefa_champs_league": "Champions League",
}

# Marchés supportés
MARCHES = ["h2h", "totals", "spreads"]


@dataclass
class CoteMatch:
    """Cote d'un match par bookmaker."""

    match_id: str
    bookmaker: str
    marche: str  # "1", "N", "2", "over_2.5", "under_2.5"
    cote: float
    probabilite_implicite: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MeilleureCote:
    """Meilleure cote disponible pour un marché."""

    marche: str
    cote: float
    bookmaker: str
    probabilite_implicite: float


@dataclass
class MouvementCote:
    """Détection d'un mouvement significatif de cote."""

    match_id: str
    bookmaker: str
    marche: str
    ancienne_cote: float
    nouvelle_cote: float
    variation_pct: float
    type_mouvement: str  # "steam_move", "drift", "stable"


class OddsDataService:
    """Service de récupération et analyse des cotes sportives."""

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key
        self._client: httpx.Client | None = None
        self._cache_cotes: dict[str, list[CoteMatch]] = {}
        self._historique: dict[str, list[CoteMatch]] = {}

    def __enter__(self):
        self._client = httpx.Client(timeout=30)
        return self

    def __exit__(self, *args):
        if self._client:
            self._client.close()

    @avec_resilience(retry=2, timeout_s=30, fallback=None)
    def obtenir_cotes_match(
        self, sport: str = "soccer_france_ligue_one", marche: str = "h2h"
    ) -> list[dict[str, Any]]:
        """
        Récupère les cotes pour un sport donné.

        Args:
            sport: Identifiant du sport (The Odds API)
            marche: Type de marché (h2h, totals, spreads)

        Returns:
            Liste des matchs avec cotes par bookmaker
        """
        if not self._api_key:
            logger.warning("Pas de clé API The Odds API configurée")
            return []

        url = f"{BASE_URL}/sports/{sport}/odds"
        params = {
            "apiKey": self._api_key,
            "regions": "eu",
            "markets": marche,
            "oddsFormat": "decimal",
        }

        if not self._client:
            self._client = httpx.Client(timeout=30)

        response = self._client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        # Parser et normaliser
        resultats = []
        for event in data:
            match_info = {
                "id": event.get("id"),
                "sport": sport,
                "championnat": MAPPING_CHAMPIONNATS.get(sport, sport),
                "equipe_domicile": event.get("home_team"),
                "equipe_exterieur": event.get("away_team"),
                "date_match": event.get("commence_time"),
                "bookmakers": [],
            }

            for bm in event.get("bookmakers", []):
                bm_info = {
                    "nom": bm.get("title"),
                    "cotes": {},
                }
                for market in bm.get("markets", []):
                    for outcome in market.get("outcomes", []):
                        nom = outcome.get("name")
                        prix = outcome.get("price", 0)
                        if nom == event.get("home_team"):
                            bm_info["cotes"]["1"] = prix
                        elif nom == event.get("away_team"):
                            bm_info["cotes"]["2"] = prix
                        elif nom == "Draw":
                            bm_info["cotes"]["N"] = prix
                        elif nom == "Over":
                            point = outcome.get("point", 2.5)
                            bm_info["cotes"][f"over_{point}"] = prix
                        elif nom == "Under":
                            point = outcome.get("point", 2.5)
                            bm_info["cotes"][f"under_{point}"] = prix

                match_info["bookmakers"].append(bm_info)

            resultats.append(match_info)

        return resultats

    def trouver_meilleures_cotes(
        self, matchs_data: list[dict[str, Any]]
    ) -> dict[str, list[MeilleureCote]]:
        """
        Pour chaque match, trouve la meilleure cote par marché.

        Returns:
            Dict {match_id: [MeilleureCote, ...]}
        """
        resultats: dict[str, list[MeilleureCote]] = {}

        for match in matchs_data:
            match_id = match.get("id", "")
            best: dict[str, MeilleureCote] = {}

            for bm in match.get("bookmakers", []):
                nom_bm = bm.get("nom", "")
                for marche, cote in bm.get("cotes", {}).items():
                    if cote <= 0:
                        continue
                    prob = 1.0 / cote
                    if marche not in best or cote > best[marche].cote:
                        best[marche] = MeilleureCote(
                            marche=marche,
                            cote=cote,
                            bookmaker=nom_bm,
                            probabilite_implicite=prob,
                        )

            resultats[match_id] = list(best.values())

        return resultats

    def detecter_mouvements(
        self,
        anciennes: list[CoteMatch],
        nouvelles: list[CoteMatch],
        seuil_pct: float = 5.0,
    ) -> list[MouvementCote]:
        """
        Détecte les mouvements de cotes significatifs (steam moves).

        Args:
            anciennes: Cotes précédentes
            nouvelles: Cotes actuelles
            seuil_pct: Seuil de variation en % pour alerter

        Returns:
            Liste des mouvements détectés
        """
        mouvements = []

        # Indexer les anciennes cotes
        index_ancien: dict[tuple[str, str, str], CoteMatch] = {}
        for c in anciennes:
            key = (c.match_id, c.bookmaker, c.marche)
            index_ancien[key] = c

        for nouvelle in nouvelles:
            key = (nouvelle.match_id, nouvelle.bookmaker, nouvelle.marche)
            ancienne = index_ancien.get(key)
            if not ancienne:
                continue

            if ancienne.cote == 0:
                continue

            variation = ((nouvelle.cote - ancienne.cote) / ancienne.cote) * 100

            if abs(variation) >= seuil_pct:
                type_mvt = "steam_move" if abs(variation) >= 10 else "drift"
                mouvements.append(
                    MouvementCote(
                        match_id=nouvelle.match_id,
                        bookmaker=nouvelle.bookmaker,
                        marche=nouvelle.marche,
                        ancienne_cote=ancienne.cote,
                        nouvelle_cote=nouvelle.cote,
                        variation_pct=variation,
                        type_mouvement=type_mvt,
                    )
                )

        return mouvements

    def calculer_edge(
        self,
        cote_bookmaker: float,
        proba_estimee: float,
    ) -> dict[str, float]:
        """
        Calcule l'edge entre la probabilité estimée et la cote du bookmaker.

        Args:
            cote_bookmaker: Cote décimale du bookmaker
            proba_estimee: Notre probabilité estimée (0-1)

        Returns:
            Dict avec edge, EV, cote_juste
        """
        proba_implicite = 1.0 / cote_bookmaker if cote_bookmaker > 0 else 1.0
        cote_juste = 1.0 / proba_estimee if proba_estimee > 0 else float("inf")
        ev = (proba_estimee * cote_bookmaker) - 1.0
        edge = proba_estimee - proba_implicite

        return {
            "cote_bookmaker": cote_bookmaker,
            "probabilite_implicite": proba_implicite,
            "proba_estimee": proba_estimee,
            "cote_juste": cote_juste,
            "ev": ev,
            "edge": edge,
            "est_value_bet": ev > 0.05,
        }

    @avec_session_db
    def sauvegarder_cotes(
        self,
        match_id: int,
        bookmaker: str,
        marche: str,
        cote: float,
        db=None,
    ) -> None:
        """Persiste une cote en base pour l'historique."""
        from src.core.models.jeux import CoteHistorique

        entry = CoteHistorique(
            match_id=match_id,
            bookmaker=bookmaker,
            marche=marche,
            cote=cote,
            probabilite_implicite=1.0 / cote if cote > 0 else None,
        )
        db.add(entry)
        db.commit()

    @avec_session_db
    def charger_historique_cotes(
        self,
        match_id: int,
        limite: int = 100,
        db=None,
    ) -> list[dict[str, Any]]:
        """Charge l'historique des cotes pour un match."""
        from src.core.models.jeux import CoteHistorique

        cotes = (
            db.query(CoteHistorique)
            .filter_by(match_id=match_id)
            .order_by(CoteHistorique.timestamp.desc())
            .limit(limite)
            .all()
        )

        return [
            {
                "bookmaker": c.bookmaker,
                "marche": c.marche,
                "cote": c.cote,
                "probabilite_implicite": c.probabilite_implicite,
                "timestamp": c.timestamp,
            }
            for c in cotes
        ]


@service_factory("odds_data", tags={"jeux", "data", "cotes"})
def get_odds_data_service() -> OddsDataService:
    """Factory pour le service de cotes."""
    from src.core.config import obtenir_parametres

    params = obtenir_parametres()
    api_key = getattr(params, "ODDS_API_KEY", None)
    return OddsDataService(api_key=api_key)
