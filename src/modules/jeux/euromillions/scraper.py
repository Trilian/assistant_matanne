"""
Scraper Euromillions - Récupération des tirages via API FDJ / data.gouv.fr
"""

import csv
import io
import logging
from datetime import date, datetime
from typing import Any

import requests

logger = logging.getLogger(__name__)

# URLs de données Euromillions
ENDPOINTS_EUROMILLIONS = [
    # data.gouv.fr - historique complet CSV
    "https://www.fdj.fr/api/jeux/euromillions/resultats",
    "https://media.fdj.fr/generated/euromillions/",
]

# Données démo pour fallback (tirages 2025-2026)
DONNEES_DEMO: list[dict[str, Any]] = [
    {
        "date_tirage": "2026-02-24",
        "numeros": [7, 14, 21, 33, 45],
        "etoiles": [3, 9],
        "jackpot_euros": 42_000_000,
    },
    {
        "date_tirage": "2026-02-21",
        "numeros": [2, 19, 28, 37, 48],
        "etoiles": [5, 11],
        "jackpot_euros": 29_000_000,
    },
    {
        "date_tirage": "2026-02-17",
        "numeros": [5, 11, 23, 39, 50],
        "etoiles": [1, 7],
        "jackpot_euros": 17_000_000,
    },
    {
        "date_tirage": "2026-02-14",
        "numeros": [8, 16, 27, 35, 44],
        "etoiles": [4, 10],
        "jackpot_euros": 130_000_000,
    },
    {
        "date_tirage": "2026-02-10",
        "numeros": [3, 18, 22, 41, 49],
        "etoiles": [2, 8],
        "jackpot_euros": 111_000_000,
    },
    {
        "date_tirage": "2026-02-07",
        "numeros": [10, 15, 30, 38, 47],
        "etoiles": [6, 12],
        "jackpot_euros": 93_000_000,
    },
    {
        "date_tirage": "2026-02-03",
        "numeros": [1, 12, 25, 36, 43],
        "etoiles": [3, 11],
        "jackpot_euros": 74_000_000,
    },
    {
        "date_tirage": "2026-01-31",
        "numeros": [6, 20, 29, 34, 46],
        "etoiles": [5, 9],
        "jackpot_euros": 55_000_000,
    },
    {
        "date_tirage": "2026-01-28",
        "numeros": [4, 17, 24, 40, 50],
        "etoiles": [1, 7],
        "jackpot_euros": 37_000_000,
    },
    {
        "date_tirage": "2026-01-24",
        "numeros": [9, 13, 26, 32, 42],
        "etoiles": [4, 10],
        "jackpot_euros": 17_000_000,
    },
    {
        "date_tirage": "2026-01-21",
        "numeros": [2, 14, 31, 37, 48],
        "etoiles": [2, 8],
        "jackpot_euros": 200_000_000,
    },
    {
        "date_tirage": "2026-01-17",
        "numeros": [7, 19, 28, 35, 45],
        "etoiles": [6, 12],
        "jackpot_euros": 176_000_000,
    },
    {
        "date_tirage": "2026-01-14",
        "numeros": [11, 22, 33, 39, 49],
        "etoiles": [3, 9],
        "jackpot_euros": 152_000_000,
    },
    {
        "date_tirage": "2026-01-10",
        "numeros": [5, 16, 27, 41, 44],
        "etoiles": [5, 11],
        "jackpot_euros": 128_000_000,
    },
    {
        "date_tirage": "2026-01-07",
        "numeros": [3, 18, 23, 36, 47],
        "etoiles": [1, 7],
        "jackpot_euros": 104_000_000,
    },
    {
        "date_tirage": "2025-12-30",
        "numeros": [8, 15, 24, 38, 50],
        "etoiles": [4, 10],
        "jackpot_euros": 80_000_000,
    },
    {
        "date_tirage": "2025-12-27",
        "numeros": [1, 20, 30, 34, 43],
        "etoiles": [2, 8],
        "jackpot_euros": 56_000_000,
    },
    {
        "date_tirage": "2025-12-23",
        "numeros": [6, 12, 25, 40, 46],
        "etoiles": [6, 12],
        "jackpot_euros": 32_000_000,
    },
    {
        "date_tirage": "2025-12-19",
        "numeros": [10, 17, 29, 32, 42],
        "etoiles": [3, 9],
        "jackpot_euros": 17_000_000,
    },
    {
        "date_tirage": "2025-12-16",
        "numeros": [4, 13, 26, 37, 49],
        "etoiles": [5, 11],
        "jackpot_euros": 65_000_000,
    },
]


class ScraperEuromillionsFDJ:
    """Scraper pour récupérer les tirages Euromillions."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (compatible; AssistantMatanne/1.0)",
                "Accept": "application/json, text/csv",
            }
        )

    def charger_tirages(self, limite: int = 100) -> list[dict[str, Any]]:
        """
        Charge les tirages Euromillions.

        Essaie les APIs, puis fallback sur les données démo.
        """
        # Essayer les endpoints
        for endpoint in ENDPOINTS_EUROMILLIONS:
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    tirages = self._parser_reponse(response)
                    if tirages:
                        logger.info(f"Chargé {len(tirages)} tirages Euromillions depuis API")
                        return tirages[:limite]
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} échoué: {e}")
                continue

        # Fallback sur données démo
        logger.info("Utilisation des données démo Euromillions")
        return DONNEES_DEMO[:limite]

    def _parser_reponse(self, response: requests.Response) -> list[dict[str, Any]]:
        """Parse la réponse (JSON ou CSV)."""
        content_type = response.headers.get("Content-Type", "")

        if "json" in content_type:
            return self._parser_json(response.json())
        elif "csv" in content_type or "text" in content_type:
            return self._parser_csv(response.text)
        return []

    def _parser_json(self, data: Any) -> list[dict[str, Any]]:
        """Parse réponse JSON FDJ."""
        tirages = []
        items = data if isinstance(data, list) else data.get("tirages", data.get("results", []))

        for item in items:
            try:
                tirage = self._extraire_tirage_json(item)
                if tirage:
                    tirages.append(tirage)
            except Exception as e:
                logger.debug(f"Erreur parsing tirage JSON: {e}")
        return tirages

    def _extraire_tirage_json(self, item: dict) -> dict[str, Any] | None:
        """Extrait un tirage depuis un item JSON."""
        # Essayer différents formats de clés
        date_str = item.get("date_tirage") or item.get("date") or item.get("draw_date")
        if not date_str:
            return None

        # Extraire les numéros
        numeros = item.get("numeros") or item.get("numbers") or []
        if not numeros:
            numeros = [item.get(f"numero_{i}") or item.get(f"ball_{i}") for i in range(1, 6)]
            numeros = [n for n in numeros if n is not None]

        etoiles = item.get("etoiles") or item.get("stars") or []
        if not etoiles:
            etoiles = [item.get(f"etoile_{i}") or item.get(f"star_{i}") for i in range(1, 3)]
            etoiles = [e for e in etoiles if e is not None]

        if len(numeros) < 5 or len(etoiles) < 2:
            return None

        return {
            "date_tirage": str(date_str)[:10],
            "numeros": sorted([int(n) for n in numeros[:5]]),
            "etoiles": sorted([int(e) for e in etoiles[:2]]),
            "jackpot_euros": item.get("jackpot_euros") or item.get("jackpot"),
            "code_my_million": item.get("code_my_million") or item.get("my_million"),
        }

    def _parser_csv(self, text: str) -> list[dict[str, Any]]:
        """Parse réponse CSV."""
        tirages = []
        reader = csv.DictReader(io.StringIO(text), delimiter=";")

        for row in reader:
            try:
                numeros = []
                etoiles = []
                for key in ["boule_1", "boule_2", "boule_3", "boule_4", "boule_5"]:
                    if key in row:
                        numeros.append(int(row[key]))
                for key in ["etoile_1", "etoile_2"]:
                    if key in row:
                        etoiles.append(int(row[key]))

                if len(numeros) == 5 and len(etoiles) == 2:
                    tirages.append(
                        {
                            "date_tirage": row.get("date_de_tirage", ""),
                            "numeros": sorted(numeros),
                            "etoiles": sorted(etoiles),
                            "jackpot_euros": int(row["rapport_du_rang1"])
                            if row.get("rapport_du_rang1")
                            else None,
                        }
                    )
            except (ValueError, KeyError) as e:
                logger.debug(f"Erreur parsing CSV row: {e}")
        return tirages


def charger_tirages_euromillions(limite: int = 100) -> list[dict[str, Any]]:
    """Fonction utilitaire pour charger les tirages."""
    scraper = ScraperEuromillionsFDJ()
    return scraper.charger_tirages(limite=limite)
