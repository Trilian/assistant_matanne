"""
Services Jeux - Infrastructure unifiée pour Paris Sportifs et Loto.

Architecture:
- series_service.py       : Calcul des séries et value (partagé)
- football_data.py        : Récupération données Football-Data.org
- football_types.py       : Types Pydantic pour les données football
- loto_data.py            : Récupération données Loto FDJ (data.gouv.fr)
- sync_service.py         : Orchestration et persistance en base
- scheduler_service.py    : Jobs automatiques APScheduler
- ai_service.py           : Analyse IA Mistral des opportunités
- notification_service.py : Gestion des notifications et alertes
- backtest_service.py     : Backtesting sur données historiques
- prediction_service.py   : Prédictions de résultats et conseils paris
"""

# ═══════════════════════════════════════════════════════════
# SÉRIES (calcul séries & value)
# ═══════════════════════════════════════════════════════════
# ═══════════════════════════════════════════════════════════
# IA (analyse Mistral)
# ═══════════════════════════════════════════════════════════
from ._internal.ai_service import (
    AnalyseIA,
    JeuxAIService,
    OpportuniteAnalysee,
    get_jeux_ai_service,
    obtenir_service_ia_jeux,
)

# ═══════════════════════════════════════════════════════════
# BACKTESTING
# ═══════════════════════════════════════════════════════════
from ._internal.backtest_service import (
    BacktestService,
    Prediction,
    ResultatBacktest,
    ResultatPrediction,
    StatistiquesBacktest,
    get_backtest_service,
    obtenir_service_backtest,
)

# ═══════════════════════════════════════════════════════════
# FOOTBALL (données & types)
# ═══════════════════════════════════════════════════════════
from ._internal.football_data import (
    FootballDataService,
    get_football_data_service,
    obtenir_service_donnees_football,
)
from ._internal.football_types import (
    Match,
    ResultatFinal,
    ResultatMiTemps,
    ScoreMatch,
    StatistiquesMarcheData,
)

# ═══════════════════════════════════════════════════════════
# LOTO (données FDJ)
# ═══════════════════════════════════════════════════════════
from ._internal.loto_data import (
    LotoDataService,
    StatistiqueNumeroLoto,
    StatistiquesGlobalesLoto,
    TirageLoto,
    get_loto_data_service,
    obtenir_service_donnees_loto,
)

# ═══════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════
from ._internal.notification_service import (
    NiveauUrgence,
    NotificationJeux,
    NotificationJeuxService,
    TypeNotification,
    afficher_badge_notifications,
    afficher_liste_notifications,
    afficher_notification,
    get_notification_jeux_service,
    obtenir_service_notifications_jeux,
)

# ═══════════════════════════════════════════════════════════
# PRÉDICTIONS (résultats & conseils paris)
# ═══════════════════════════════════════════════════════════
from ._internal.prediction_service import (
    ConseilPari,
    CotesMatch,
    FormEquipe,
    H2HData,
    PredictionOverUnder,
    PredictionResultat,
    PredictionService,
    generer_conseil_pari,
    generer_conseils_avances,
    get_prediction_service,
    obtenir_service_predictions_jeux,
    predire_over_under,
    predire_resultat_match,
)

# ═══════════════════════════════════════════════════════════
# SCHEDULER (jobs automatiques)
# ═══════════════════════════════════════════════════════════
from ._internal.scheduler_service import (
    APSCHEDULER_AVAILABLE,
    SchedulerService,
    get_scheduler_service,
    obtenir_service_planificateur_jeux,
    reset_scheduler_service,
)
from ._internal.series_service import (
    SeriesService,
    get_series_service,
    obtenir_service_series,
)

# ═══════════════════════════════════════════════════════════
# SYNCHRONISATION
# ═══════════════════════════════════════════════════════════
from ._internal.sync_service import (
    SyncService,
    get_sync_service,
    obtenir_service_sync_jeux,
)

__all__ = [
    # ─────────────────────────────────────────────────────────
    # Séries
    # ─────────────────────────────────────────────────────────
    "SeriesService",
    "get_series_service",
    "obtenir_service_series",
    # ─────────────────────────────────────────────────────────
    # Football - Sources de données
    # ─────────────────────────────────────────────────────────
    "FootballDataService",
    "get_football_data_service",
    "obtenir_service_donnees_football",
    # Football - Types
    "Match",
    "ScoreMatch",
    "ResultatFinal",
    "ResultatMiTemps",
    "StatistiquesMarcheData",
    # ─────────────────────────────────────────────────────────
    # Loto - Sources de données
    # ─────────────────────────────────────────────────────────
    "LotoDataService",
    "get_loto_data_service",
    "obtenir_service_donnees_loto",
    # Loto - Types
    "TirageLoto",
    "StatistiqueNumeroLoto",
    "StatistiquesGlobalesLoto",
    # ─────────────────────────────────────────────────────────
    # Synchronisation
    # ─────────────────────────────────────────────────────────
    "SyncService",
    "get_sync_service",
    "obtenir_service_sync_jeux",
    # ─────────────────────────────────────────────────────────
    # Scheduler
    # ─────────────────────────────────────────────────────────
    "SchedulerService",
    "get_scheduler_service",
    "obtenir_service_planificateur_jeux",
    "reset_scheduler_service",
    "APSCHEDULER_AVAILABLE",
    # ─────────────────────────────────────────────────────────
    # IA
    # ─────────────────────────────────────────────────────────
    "JeuxAIService",
    "AnalyseIA",
    "OpportuniteAnalysee",
    "get_jeux_ai_service",
    "obtenir_service_ia_jeux",
    # ─────────────────────────────────────────────────────────
    # Notifications
    # ─────────────────────────────────────────────────────────
    "NotificationJeuxService",
    "NotificationJeux",
    "TypeNotification",
    "NiveauUrgence",
    "get_notification_jeux_service",
    "obtenir_service_notifications_jeux",
    "afficher_badge_notifications",
    "afficher_notification",
    "afficher_liste_notifications",
    # ─────────────────────────────────────────────────────────
    # Backtesting
    # ─────────────────────────────────────────────────────────
    "BacktestService",
    "ResultatBacktest",
    "StatistiquesBacktest",
    "Prediction",
    "ResultatPrediction",
    "get_backtest_service",
    "obtenir_service_backtest",
    # ─────────────────────────────────────────────────────────
    # Prédictions
    # ─────────────────────────────────────────────────────────
    "PredictionService",
    "get_prediction_service",
    "obtenir_service_predictions_jeux",
    "PredictionResultat",
    "PredictionOverUnder",
    "ConseilPari",
    "FormEquipe",
    "H2HData",
    "CotesMatch",
    "predire_resultat_match",
    "predire_over_under",
    "generer_conseil_pari",
    "generer_conseils_avances",
]
