"""
Services Jeux - Infrastructure unifiée pour Paris Sportifs et Loto.

Architecture:
- series_service.py      : Calcul des séries et value (partagé)
- football_data.py       : Récupération données Football-Data.org
- loto_data.py           : Récupération données Loto FDJ (data.gouv.fr)
- sync_service.py        : Orchestration et persistance en base
- scheduler_service.py   : Jobs automatiques APScheduler
- ai_service.py          : Analyse IA Mistral des opportunités
- notification_service.py: Gestion des notifications et alertes
- backtest_service.py    : Backtesting sur données historiques
"""

from .ai_service import (
    AnalyseIA,
    JeuxAIService,
    OpportuniteAnalysee,
    get_jeux_ai_service,
)
from .backtest_service import (
    BacktestService,
    Prediction,
    ResultatBacktest,
    ResultatPrediction,
    get_backtest_service,
)
from .football_data import FootballDataService, get_football_data_service
from .loto_data import LotoDataService, get_loto_data_service
from .notification_service import (
    NiveauUrgence,
    NotificationJeux,
    NotificationJeuxService,
    TypeNotification,
    afficher_badge_notifications,
    afficher_liste_notifications,
    afficher_notification,
    get_notification_jeux_service,
)
from .scheduler_service import (
    APSCHEDULER_AVAILABLE,
    SchedulerService,
    get_scheduler_service,
    reset_scheduler_service,
)
from .series_service import SeriesService, get_series_service
from .sync_service import SyncService, get_sync_service

__all__ = [
    # Séries
    "SeriesService",
    "get_series_service",
    # Sources de données
    "FootballDataService",
    "get_football_data_service",
    "LotoDataService",
    "get_loto_data_service",
    # Synchronisation
    "SyncService",
    "get_sync_service",
    # Scheduler
    "SchedulerService",
    "get_scheduler_service",
    "reset_scheduler_service",
    "APSCHEDULER_AVAILABLE",
    # IA
    "JeuxAIService",
    "AnalyseIA",
    "OpportuniteAnalysee",
    "get_jeux_ai_service",
    # Notifications
    "NotificationJeuxService",
    "NotificationJeux",
    "TypeNotification",
    "NiveauUrgence",
    "get_notification_jeux_service",
    "afficher_badge_notifications",
    "afficher_notification",
    "afficher_liste_notifications",
    # Backtesting
    "BacktestService",
    "ResultatBacktest",
    "Prediction",
    "ResultatPrediction",
    "get_backtest_service",
]
