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

from typing import TYPE_CHECKING

# ═══════════════════════════════════════════════════════════
# LAZY LOADING pour performance au démarrage
# ═══════════════════════════════════════════════════════════

_LAZY_IMPORTS: dict[str, str] = {
    # ── Séries ──
    "SeriesService": "series_service",
    "get_series_service": "series_service",
    "obtenir_service_series": "series_service",
    "SEUIL_VALUE_ALERTE": "series_service",
    "SEUIL_VALUE_HAUTE": "series_service",
    "SEUIL_SERIES_MINIMUM": "series_service",
    # ── IA ──
    "JeuxAIService": "ai_service",
    "AnalyseIA": "ai_service",
    "OpportuniteAnalysee": "ai_service",
    "get_jeux_ai_service": "ai_service",
    "obtenir_service_ia_jeux": "ai_service",
    # ── Backtesting ──
    "BacktestService": "backtest_service",
    "Prediction": "backtest_service",
    "ResultatBacktest": "backtest_service",
    "ResultatPrediction": "backtest_service",
    "StatistiquesBacktest": "backtest_service",
    "get_backtest_service": "backtest_service",
    "obtenir_service_backtest": "backtest_service",
    # ── Football - Données ──
    "FootballDataService": "football_data",
    "COMPETITIONS": "football_data",
    "charger_classement": "football_data",
    "charger_historique_equipe": "football_data",
    "charger_matchs_a_venir": "football_data",
    "charger_matchs_termines": "football_data",
    "chercher_equipe": "football_data",
    "configurer_api_key": "football_data",
    "get_football_data_service": "football_data",
    "obtenir_service_donnees_football": "football_data",
    "vider_cache": "football_data",
    # ── Football - Types ──
    "Match": "football_types",
    "ResultatFinal": "football_types",
    "ResultatMiTemps": "football_types",
    "ScoreMatch": "football_types",
    "StatistiquesMarcheData": "football_types",
    # ── Loto ──
    "LotoDataService": "loto_data",
    "NB_NUMEROS_CHANCE": "loto_data",
    "NB_NUMEROS_PRINCIPAUX": "loto_data",
    "NUMEROS_PAR_TIRAGE": "loto_data",
    "StatistiqueNumeroLoto": "loto_data",
    "StatistiquesGlobalesLoto": "loto_data",
    "TirageLoto": "loto_data",
    "get_loto_data_service": "loto_data",
    "obtenir_service_donnees_loto": "loto_data",
    # ── Notifications ──
    "NotificationJeuxService": "notification_service",
    "NotificationJeux": "notification_service",
    "TypeNotification": "notification_service",
    "NiveauUrgence": "notification_service",
    "afficher_badge_notifications": "notification_service",
    "afficher_liste_notifications": "notification_service",
    "afficher_notification": "notification_service",
    "get_notification_jeux_service": "notification_service",
    "obtenir_service_notifications_jeux": "notification_service",
    # ── Prédictions ──
    "PredictionService": "prediction_service",
    "ConseilPari": "prediction_service",
    "CotesMatch": "prediction_service",
    "FormEquipe": "prediction_service",
    "H2HData": "prediction_service",
    "PredictionOverUnder": "prediction_service",
    "PredictionResultat": "prediction_service",
    "generer_conseil_pari": "prediction_service",
    "generer_conseils_avances": "prediction_service",
    "get_prediction_service": "prediction_service",
    "obtenir_service_predictions_jeux": "prediction_service",
    "predire_over_under": "prediction_service",
    "predire_resultat_match": "prediction_service",
    # ── Scheduler ──
    "SchedulerService": "scheduler_service",
    "APSCHEDULER_AVAILABLE": "scheduler_service",
    "HEURE_LOTO": "scheduler_service",
    "INTERVALLE_PARIS_HEURES": "scheduler_service",
    "MINUTE_LOTO": "scheduler_service",
    "get_scheduler_service": "scheduler_service",
    "obtenir_service_planificateur_jeux": "scheduler_service",
    "reset_scheduler_service": "scheduler_service",
    # ── Synchronisation ──
    "SyncService": "sync_service",
    "get_sync_service": "sync_service",
    "obtenir_service_sync_jeux": "sync_service",
    # ── Loto CRUD ──
    "LotoCrudService": "loto_crud_service",
    "get_loto_crud_service": "loto_crud_service",
    "obtenir_service_loto_crud": "loto_crud_service",
    # ── Paris CRUD ──
    "ParisCrudService": "paris_crud_service",
    "get_paris_crud_service": "paris_crud_service",
    "obtenir_service_paris_crud": "paris_crud_service",
}


def __getattr__(name: str):
    """Lazy loading des services jeux."""
    if name in _LAZY_IMPORTS:
        module_name = _LAZY_IMPORTS[name]
        module = __import__(f"src.services.jeux._internal.{module_name}", fromlist=[name])
        return getattr(module, name)
    raise AttributeError(f"module 'src.services.jeux' has no attribute '{name}'")


def __dir__():
    """Liste tous les exports disponibles."""
    return list(_LAZY_IMPORTS.keys())


# Type hints pour IDE sans charger les modules
if TYPE_CHECKING:
    from ._internal.ai_service import (
        AnalyseIA,
        JeuxAIService,
        OpportuniteAnalysee,
        get_jeux_ai_service,
        obtenir_service_ia_jeux,
    )
    from ._internal.backtest_service import (
        BacktestService,
        Prediction,
        ResultatBacktest,
        ResultatPrediction,
        StatistiquesBacktest,
        get_backtest_service,
        obtenir_service_backtest,
    )
    from ._internal.football_data import (
        COMPETITIONS,
        FootballDataService,
        charger_classement,
        charger_historique_equipe,
        charger_matchs_a_venir,
        charger_matchs_termines,
        chercher_equipe,
        configurer_api_key,
        get_football_data_service,
        obtenir_service_donnees_football,
        vider_cache,
    )
    from ._internal.football_types import (
        Match,
        ResultatFinal,
        ResultatMiTemps,
        ScoreMatch,
        StatistiquesMarcheData,
    )
    from ._internal.loto_crud_service import (
        LotoCrudService,
        get_loto_crud_service,
        obtenir_service_loto_crud,
    )
    from ._internal.loto_data import (
        NB_NUMEROS_CHANCE,
        NB_NUMEROS_PRINCIPAUX,
        NUMEROS_PAR_TIRAGE,
        LotoDataService,
        StatistiqueNumeroLoto,
        StatistiquesGlobalesLoto,
        TirageLoto,
        get_loto_data_service,
        obtenir_service_donnees_loto,
    )
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
    from ._internal.paris_crud_service import (
        ParisCrudService,
        get_paris_crud_service,
        obtenir_service_paris_crud,
    )
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
    from ._internal.scheduler_service import (
        APSCHEDULER_AVAILABLE,
        HEURE_LOTO,
        INTERVALLE_PARIS_HEURES,
        MINUTE_LOTO,
        SchedulerService,
        get_scheduler_service,
        obtenir_service_planificateur_jeux,
        reset_scheduler_service,
    )
    from ._internal.series_service import (
        SEUIL_SERIES_MINIMUM,
        SEUIL_VALUE_ALERTE,
        SEUIL_VALUE_HAUTE,
        SeriesService,
        get_series_service,
        obtenir_service_series,
    )
    from ._internal.sync_service import (
        SyncService,
        get_sync_service,
        obtenir_service_sync_jeux,
    )
