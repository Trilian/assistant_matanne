"""
Schémas Pydantic pour les jeux (paris sportifs et loto).
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from enum import Enum

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


# ═══════════════════════════════════════════════════════════
# SÉRIES & ALERTES
# ═══════════════════════════════════════════════════════════


class SerieJeuxResponse(BaseModel):
    id: int
    type_jeu: str
    marche: str
    championnat: str | None = None
    serie_actuelle: int = 0
    frequence: float = 0.0
    value: float = 0.0
    niveau_opportunite: str = ""


class AlerteJeuxResponse(BaseModel):
    id: int
    type_jeu: str
    marche: str
    championnat: str | None = None
    value_alerte: float
    serie_alerte: int
    frequence_alerte: float
    seuil_utilise: float = 2.0
    notifie: bool = False
    date_creation: datetime | None = None


# ═══════════════════════════════════════════════════════════
# PRÉDICTIONS & VALUE BETS
# ═══════════════════════════════════════════════════════════


class PredictionMatchResponse(BaseModel):
    match_id: int
    equipe_domicile: str | None = None
    equipe_exterieur: str | None = None
    resultat: str
    probas: dict[str, float] = Field(default_factory=dict)
    confiance: float = 0.0
    niveau_confiance: str = ""
    raisons: list[str] = Field(default_factory=list)
    conseil: str = ""


class ValueBetResponse(BaseModel):
    match_id: int
    equipe_domicile: str | None = None
    equipe_exterieur: str | None = None
    date_match: str
    cote_bookmaker: float
    proba_estimee: float
    edge_pct: float
    ev: float
    type_pari: str = "1N2"
    prediction: str = ""


# ═══════════════════════════════════════════════════════════
# LOTO STATS & NUMÉROS EN RETARD
# ═══════════════════════════════════════════════════════════


class NumeroRetardResponse(BaseModel):
    numero: int
    type_numero: str = "principal"
    serie_actuelle: int = 0
    frequence: float = 0.0
    derniere_sortie: date | None = None
    value: float = 0.0


class StatsLotoResponse(BaseModel):
    total_tirages: int = 0
    frequences_numeros: dict[int, float] = Field(default_factory=dict)
    numeros_chauds: list[int] = Field(default_factory=list)
    numeros_froids: list[int] = Field(default_factory=list)
    numeros_retard: list[NumeroRetardResponse] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# EUROMILLIONS
# ═══════════════════════════════════════════════════════════


class TirageEuromillionsResponse(BaseModel):
    id: int
    date_tirage: str
    numeros: list[int] = Field(default_factory=list)
    etoiles: list[int] = Field(default_factory=list)
    jackpot_euros: int | None = None
    gagnants_rang1: int | None = None


class GrilleEuromillionsResponse(BaseModel):
    id: int
    tirage_id: int | None = None
    numeros: list[int] = Field(default_factory=list)
    etoiles: list[int] = Field(default_factory=list)
    est_virtuelle: bool = True
    source_prediction: str | None = None
    mise: float = 2.50
    gain: float | None = None
    rang: int | None = None


class StatsEuromillionsResponse(BaseModel):
    total_tirages: int = 0
    frequences_numeros: dict[int, float] = Field(default_factory=dict)
    frequences_etoiles: dict[int, float] = Field(default_factory=dict)
    numeros_chauds: list[int] = Field(default_factory=list)
    numeros_froids: list[int] = Field(default_factory=list)
    numeros_retard: list[NumeroRetardResponse] = Field(default_factory=list)
    etoiles_chaudes: list[int] = Field(default_factory=list)
    etoiles_froides: list[int] = Field(default_factory=list)


# ═══════════════════════════════════════════════════════════
# PERFORMANCE
# ═══════════════════════════════════════════════════════════


class KPIsJeuxResponse(BaseModel):
    roi_mois: float = 0.0
    taux_reussite_mois: float = 0.0
    benefice_mois: float = 0.0
    paris_actifs: int = 0


class PerformanceMoisResponse(BaseModel):
    mois: str
    roi: float = 0.0
    nb_paris: int = 0
    benefice: float = 0.0


class PerformanceResponse(BaseModel):
    roi: float = 0.0
    taux_reussite: float = 0.0
    benefice: float = 0.0
    nb_paris: int = 0
    par_mois: list[PerformanceMoisResponse] = Field(default_factory=list)
    par_championnat: dict[str, dict[str, float]] = Field(default_factory=dict)
    par_type_pari: dict[str, dict[str, float]] = Field(default_factory=dict)
    meilleur_mois: str | None = None
    pire_mois: str | None = None
    serie_gagnante_max: int = 0
    serie_perdante_max: int = 0


# ═══════════════════════════════════════════════════════════
# ANALYSE IA
# ═══════════════════════════════════════════════════════════


class AnalyseIARequest(BaseModel):
    type: str = Field(..., pattern="^(paris|loto)$")
    data: dict = Field(default_factory=dict)


class AnalyseIAResponse(BaseModel):
    resume: str = ""
    points_cles: list[str] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)
    avertissement: str = ""
    confiance: float = 0.0
    genere_le: datetime | None = None


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ MENSUEL
# ═══════════════════════════════════════════════════════════


class ResumeMensuelResponse(BaseModel):
    mois: str
    analyse: str = ""
    points_forts: list[str] = Field(default_factory=list)
    points_faibles: list[str] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)
    kpis: KPIsJeuxResponse = Field(default_factory=KPIsJeuxResponse)


# ═══════════════════════════════════════════════════════════
# GRILLE GÉNÉRATION
# ═══════════════════════════════════════════════════════════


class StrategieGrille(str, Enum):
    STATISTIQUE = "statistique"
    ALEATOIRE = "aleatoire"
    IA = "ia"


class GenererGrilleRequest(BaseModel):
    strategie: StrategieGrille = StrategieGrille.STATISTIQUE
    sauvegarder: bool = False


class GrilleGenereeResponse(BaseModel):
    numeros: list[int] = Field(default_factory=list)
    special: list[int] = Field(default_factory=list)
    strategie: str = "statistique"
    analyse_ia: str | None = None


# ═══════════════════════════════════════════════════════════
# BACKTEST
# ═══════════════════════════════════════════════════════════


class BacktestResponse(BaseModel):
    type_jeu: str
    nb_predictions: int = 0
    nb_correctes: int = 0
    taux_reussite: float = 0.0
    tirages_moyens: float = 0.0
    seuil_value: float = 2.0
    avertissement: str = "Les performances passées ne préjugent pas des résultats futurs."


# ═══════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════


class NotificationJeuxResponse(BaseModel):
    id: str
    type: str
    titre: str
    message: str
    urgence: str = "basse"
    type_jeu: str = "global"
    lue: bool = False
    date_creation: datetime | None = None


# ═══════════════════════════════════════════════════════════
# DASHBOARD AGRÉGÉ
# ═══════════════════════════════════════════════════════════


class BudgetResponsableResponse(BaseModel):
    limite: float = 50.0
    mises_cumulees: float = 0.0
    pourcentage_utilise: float = 0.0
    reste_disponible: float = 50.0
    cooldown_actif: bool = False
    auto_exclusion_jusqu_a: date | None = None


class DashboardJeuxResponse(BaseModel):
    opportunites: list[SerieJeuxResponse] = Field(default_factory=list)
    matchs_jour: list[dict] = Field(default_factory=list)
    value_bets: list[ValueBetResponse] = Field(default_factory=list)
    loto_retard: list[NumeroRetardResponse] = Field(default_factory=list)
    budget: BudgetResponsableResponse = Field(default_factory=BudgetResponsableResponse)
    kpis: KPIsJeuxResponse = Field(default_factory=KPIsJeuxResponse)
    analyse_ia: AnalyseIAResponse | None = None


# ═══════════════════════════════════════════════════════════
# LOTO GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════


class GrilleIAPondereeResponse(BaseModel):
    """Grille loto générée par IA pondérée."""

    numeros: list[int] = Field(default_factory=list)
    numero_chance: int = 0
    mode: str = "equilibre"
    analyse: str = ""
    confiance: float = 0.0
    sauvegardee: bool = False


class AnalyseGrilleLotoResponse(BaseModel):
    """Analyse qualitative d'une grille loto."""

    grille: dict[str, Any] = Field(default_factory=dict)
    note: int = 0
    points_forts: list[str] = Field(default_factory=list)
    points_faibles: list[str] = Field(default_factory=list)
    recommandations: list[str] = Field(default_factory=list)
    appreciation: str = ""


class GrilleExpertEuromillionsResponse(BaseModel):
    """Grille euromillions experte."""

    id: int
    numeros: list[int] = Field(default_factory=list)
    etoiles: list[int] = Field(default_factory=list)
    date_tirage: str | None = None
    strategie: str = ""
    qualite: float = 0.0
    explication: str = ""
    distribution: dict[str, Any] = Field(default_factory=dict)
    backtest: dict[str, Any] | None = None
    statut: str = ""
