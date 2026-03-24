"""
Schémas Pydantic pour les jeux (paris sportifs et loto).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════
# ÉQUIPES
# ═══════════════════════════════════════════════════════════


class EquipeResponse(BaseModel):
    id: int
    nom: str
    nom_court: str | None = None
    championnat: str | None = None
    pays: str | None = None
    matchs_joues: int = 0
    victoires: int = 0
    nuls: int = 0
    defaites: int = 0
    buts_marques: int = 0
    buts_encaisses: int = 0
    points: int = 0


class EquipeDetailResponse(EquipeResponse):
    logo_url: str | None = None
    forme_recente: str | None = None


# ═══════════════════════════════════════════════════════════
# MATCHS
# ═══════════════════════════════════════════════════════════


class MatchResponse(BaseModel):
    id: int
    equipe_domicile: str | None = None
    equipe_exterieur: str | None = None
    championnat: str | None = None
    journee: int | None = None
    date_match: str
    heure: str | None = None
    score_domicile: int | None = None
    score_exterieur: int | None = None
    resultat: str | None = None
    joue: bool = False
    cote_domicile: float | None = None
    cote_nul: float | None = None
    cote_exterieur: float | None = None


class MatchEquipeRef(BaseModel):
    id: int
    nom: str


class CotesMatch(BaseModel):
    domicile: float | None = None
    nul: float | None = None
    exterieur: float | None = None


class PredictionMatch(BaseModel):
    resultat: str | None = None
    proba_dom: float | None = None
    proba_nul: float | None = None
    proba_ext: float | None = None
    confiance: float | None = None
    raison: str | None = None


class PariResume(BaseModel):
    id: int
    type_pari: str | None = None
    prediction: str | None = None
    cote: float | None = None
    mise: float = 0
    statut: str | None = None
    est_virtuel: bool = True


class MatchDetailResponse(BaseModel):
    id: int
    equipe_domicile: MatchEquipeRef | None = None
    equipe_exterieur: MatchEquipeRef | None = None
    championnat: str | None = None
    journee: int | None = None
    date_match: str
    heure: str | None = None
    score_domicile: int | None = None
    score_exterieur: int | None = None
    resultat: str | None = None
    joue: bool = False
    cotes: CotesMatch | None = None
    prediction: PredictionMatch | None = None
    paris: list[PariResume] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# PARIS SPORTIFS
# ═══════════════════════════════════════════════════════════


class PariCreate(BaseModel):
    match_id: int
    type_pari: str = "1N2"
    prediction: str
    cote: float
    mise: float = 0
    est_virtuel: bool = True
    notes: str | None = None


class PariPatch(BaseModel):
    statut: str | None = None
    gain: float | None = None
    notes: str | None = None


class PariResponse(BaseModel):
    id: int
    match_id: int | None = None
    type_pari: str | None = None
    prediction: str | None = None
    cote: float | None = None
    mise: float = 0
    statut: str | None = None
    gain: float | None = None
    est_virtuel: bool = True
    confiance_prediction: float | None = None


class StatistiquesParis(BaseModel):
    total_paris: int = 0
    total_mise: float = 0
    total_gain: float = 0
    benefice: float = 0
    taux_reussite: float = 0
    par_statut: dict[str, int] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════
# LOTO
# ═══════════════════════════════════════════════════════════


class TirageLotoResponse(BaseModel):
    id: int
    date_tirage: str
    numeros: list[int] | None = None
    numero_chance: int | None = None
    numeros_str: str | None = None
    jackpot_euros: int | None = None
    gagnants_rang1: int | None = None


class GrilleLotoResponse(BaseModel):
    id: int
    tirage_id: int | None = None
    numeros: list[int] = Field(default_factory=list)
    numero_chance: int | None = None
    est_virtuelle: bool = True
    source_prediction: str | None = None
