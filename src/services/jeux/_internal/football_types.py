"""
Types et schémas pour le service Football-Data.org.

Contient les enums, modèles Pydantic et constantes partagés
par football_data.py et football_helpers.py.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

BASE_URL = "https://api.football-data.org/v4"

# Codes des compétitions (plan gratuit)
COMPETITIONS = {
    "PL": "Premier League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "PD": "La Liga",
    "FL1": "Ligue 1",
}

# Mapping des championnats (nom -> code API)
CHAMP_MAPPING = {
    "Ligue 1": "FL1",
    "Premier League": "PL",
    "La Liga": "PD",
    "Serie A": "SA",
    "Bundesliga": "BL1",
}


# ═══════════════════════════════════════════════════════════
# ENUMS
# ═══════════════════════════════════════════════════════════


class ResultatMiTemps(StrEnum):
    """Résultat à la mi-temps."""

    DOMICILE = "domicile"
    EXTERIEUR = "exterieur"
    NUL = "nul"


class ResultatFinal(StrEnum):
    """Résultat final."""

    DOMICILE = "domicile"
    EXTERIEUR = "exterieur"
    NUL = "nul"


# ═══════════════════════════════════════════════════════════
# MODÈLES PYDANTIC
# ═══════════════════════════════════════════════════════════


class ScoreMatch(BaseModel):
    """Score d'un match."""

    domicile_mi_temps: int = 0
    exterieur_mi_temps: int = 0
    domicile_final: int = 0
    exterieur_final: int = 0


class Match(BaseModel):
    """Données d'un match."""

    id: int
    competition: str
    competition_nom: str = ""
    date_match: date
    equipe_domicile: str
    equipe_exterieur: str
    score: ScoreMatch = Field(default_factory=ScoreMatch)
    statut: str = "SCHEDULED"  # SCHEDULED, LIVE, FINISHED, POSTPONED, etc.
    resultat_mi_temps: ResultatMiTemps | None = None
    resultat_final: ResultatFinal | None = None

    @property
    def est_termine(self) -> bool:
        """Vérifie si le match est terminé."""
        return self.statut == "FINISHED"


class StatistiquesMarcheData(BaseModel):
    """Statistiques pour un marché donné."""

    marche: str  # ex: "domicile_mi_temps", "nul_final"
    total_matchs: int = 0
    nb_occurrences: int = 0
    frequence: float = 0.0  # nb_occurrences / total_matchs
    serie_actuelle: int = 0  # Matchs depuis dernière occurrence
    derniere_occurrence: date | None = None
