"""
Core - Module central de l'application.

Expose les composants essentiels via chargement paresseux (PEP 562).
Convention : Noms en français uniquement.

Usage recommandé (imports directs depuis les sous-modules):
    from src.core.config import obtenir_parametres
    from src.core.db import obtenir_contexte_db
    from src.core.errors_base import ErreurValidation

Usage général (lazy, via __getattr__):
    from src.core import obtenir_parametres  # charge config/ à la demande

Sous-modules thématiques:
- config/: Configuration Pydantic
- db/: Base de données et migrations
- caching/: Cache multi-niveaux
- validation/: Sanitization et schémas Pydantic
- ai/: Client IA, rate limiting, cache sémantique
"""

from __future__ import annotations

import importlib
from typing import Any

# Mapping: nom de symbole → (sous-module relatif, nom dans le module)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # Container (IoC)
    "Conteneur": (".container", "Conteneur"),
    "Scope": (".container", "Scope"),
    "conteneur": (".container", "conteneur"),
    # AI
    "AnalyseurIA": (".ai", "AnalyseurIA"),
    "CacheIA": (".ai", "CacheIA"),
    "CircuitBreaker": (".ai", "CircuitBreaker"),
    "ClientIA": (".ai", "ClientIA"),
    "EtatCircuit": (".ai", "EtatCircuit"),
    "RateLimitIA": (".ai", "RateLimitIA"),
    "avec_circuit_breaker": (".ai", "avec_circuit_breaker"),
    "obtenir_circuit": (".ai", "obtenir_circuit"),
    "obtenir_client_ia": (".ai", "obtenir_client_ia"),
    # Cache
    "Cache": (".caching", "Cache"),
    "CacheMultiNiveau": (".caching", "CacheMultiNiveau"),
    "EntreeCache": (".caching", "EntreeCache"),
    "StatistiquesCache": (".caching", "StatistiquesCache"),
    "obtenir_cache": (".caching", "obtenir_cache"),
    "reinitialiser_cache": (".caching", "reinitialiser_cache"),
    # Config
    "Parametres": (".config", "Parametres"),
    "obtenir_parametres": (".config", "obtenir_parametres"),
    "reinitialiser_parametres": (".config", "reinitialiser_parametres"),
    # Database
    "GestionnaireMigrations": (".db", "GestionnaireMigrations"),
    "creer_toutes_tables": (".db", "creer_toutes_tables"),
    "initialiser_database": (".db", "initialiser_database"),
    "obtenir_contexte_db": (".db", "obtenir_contexte_db"),
    "obtenir_db_securise": (".db", "obtenir_db_securise"),
    "obtenir_fabrique_session": (".db", "obtenir_fabrique_session"),
    "obtenir_infos_db": (".db", "obtenir_infos_db"),
    "obtenir_moteur": (".db", "obtenir_moteur"),
    "obtenir_moteur_securise": (".db", "obtenir_moteur_securise"),
    "vacuum_database": (".db", "vacuum_database"),
    "verifier_connexion": (".db", "verifier_connexion"),
    "verifier_sante": (".db", "verifier_sante"),
    # Repository
    "Repository": (".repository", "Repository"),
    # Specifications
    "Spec": (".specifications", "Spec"),
    "Specification": (".specifications", "Specification"),
    "contient": (".specifications", "contient"),
    "entre": (".specifications", "entre"),
    "limite": (".specifications", "limite"),
    "ordre_par": (".specifications", "ordre_par"),
    "paginer": (".specifications", "paginer"),
    "par_champ": (".specifications", "par_champ"),
    "par_champs": (".specifications", "par_champs"),
    "avec_chargement": (".specifications", "avec_chargement"),
    "par_date_range": (".specifications", "par_date_range"),
    "actif": (".specifications", "actif"),
    "recent": (".specifications", "recent"),
    # Unit of Work
    "UnitOfWork": (".unit_of_work", "UnitOfWork"),
    # Result (Pattern Monad)
    "Result": (".result", "Result"),
    "Ok": (".result", "Ok"),
    "Err": (".result", "Err"),
    "Success": (".result", "Success"),
    "Failure": (".result", "Failure"),
    "ErrorCode": (".result", "ErrorCode"),
    "ErrorInfo": (".result", "ErrorInfo"),
    "capturer": (".result", "capturer"),
    "capturer_async": (".result", "capturer_async"),
    "depuis_option": (".result", "depuis_option"),
    "depuis_bool": (".result", "depuis_bool"),
    "combiner": (".result", "combiner"),
    "premier_ok": (".result", "premier_ok"),
    "collect": (".result", "collect"),
    "collect_all": (".result", "collect_all"),
    "avec_result": (".result", "avec_result"),
    "safe": (".result", "safe"),
    "result_api": (".result", "result_api"),
    "success": (".result", "success"),
    "failure": (".result", "failure"),
    "from_exception": (".result", "from_exception"),
    "register_error_mapping": (".result", "register_error_mapping"),
    # Resilience Policies
    "Policy": (".resilience", "Policy"),
    "RetryPolicy": (".resilience", "RetryPolicy"),
    "TimeoutPolicy": (".resilience", "TimeoutPolicy"),
    "BulkheadPolicy": (".resilience", "BulkheadPolicy"),
    "FallbackPolicy": (".resilience", "FallbackPolicy"),
    "PolicyComposee": (".resilience", "PolicyComposee"),
    "politique_api_externe": (".resilience", "politique_api_externe"),
    "politique_base_de_donnees": (".resilience", "politique_base_de_donnees"),
    "politique_cache": (".resilience", "politique_cache"),
    "politique_ia": (".resilience", "politique_ia"),
    # Observability (Correlation ID)
    "ContexteExecution": (".observability", "ContexteExecution"),
    "obtenir_contexte": (".observability", "obtenir_contexte"),
    "contexte_operation": (".observability", "contexte_operation"),
    "FiltreCorrelation": (".observability", "FiltreCorrelation"),
    "configurer_logging_avec_correlation": (
        ".observability",
        "configurer_logging_avec_correlation",
    ),
    # Bootstrap
    "demarrer_application": (".bootstrap", "demarrer_application"),
    "arreter_application": (".bootstrap", "arreter_application"),
    "est_demarree": (".bootstrap", "est_demarree"),
    "resoudre_service": (".bootstrap", "resoudre_service"),
    "RapportDemarrage": (".bootstrap", "RapportDemarrage"),
    # Config Validator
    "ValidateurConfiguration": (".config.validator", "ValidateurConfiguration"),
    "NiveauValidation": (".config.validator", "NiveauValidation"),
    "RapportValidation": (".config.validator", "RapportValidation"),
    "creer_validateur_defaut": (".config.validator", "creer_validateur_defaut"),
    # Decorators
    "avec_cache": (".decorators", "avec_cache"),
    "avec_gestion_erreurs": (".decorators", "avec_gestion_erreurs"),
    "avec_resilience": (".decorators", "avec_resilience"),
    "avec_session_db": (".decorators", "avec_session_db"),
    "avec_validation": (".decorators", "avec_validation"),
    # Errors (UI)
    "GestionnaireErreurs": (".errors", "GestionnaireErreurs"),
    "afficher_erreur_streamlit": (".errors", "afficher_erreur_streamlit"),
    "gerer_erreurs": (".errors", "gerer_erreurs"),
    # Errors Base (pures)
    "ErreurBaseDeDonnees": (".errors_base", "ErreurBaseDeDonnees"),
    "ErreurConfiguration": (".errors_base", "ErreurConfiguration"),
    "ErreurLimiteDebit": (".errors_base", "ErreurLimiteDebit"),
    "ErreurNonTrouve": (".errors_base", "ErreurNonTrouve"),
    "ErreurServiceExterne": (".errors_base", "ErreurServiceExterne"),
    "ErreurServiceIA": (".errors_base", "ErreurServiceIA"),
    "ErreurValidation": (".errors_base", "ErreurValidation"),
    "ExceptionApp": (".errors_base", "ExceptionApp"),
    "exiger_champs": (".errors_base", "exiger_champs"),
    "exiger_existence": (".errors_base", "exiger_existence"),
    "exiger_longueur": (".errors_base", "exiger_longueur"),
    "exiger_plage": (".errors_base", "exiger_plage"),
    "exiger_positif": (".errors_base", "exiger_positif"),
    "valider_plage": (".errors_base", "valider_plage"),
    "valider_type": (".errors_base", "valider_type"),
    # Lazy Loader
    "ChargeurModuleDiffere": (".lazy_loader", "ChargeurModuleDiffere"),
    "RouteurOptimise": (".lazy_loader", "RouteurOptimise"),
    "afficher_stats_chargement_differe": (".lazy_loader", "afficher_stats_chargement_differe"),
    # Logging
    "GestionnaireLog": (".logging", "GestionnaireLog"),
    "obtenir_logger": (".logging", "obtenir_logger"),
    # Middleware
    "CacheMiddleware": (".middleware", "CacheMiddleware"),
    "CircuitBreakerMiddleware": (".middleware", "CircuitBreakerMiddleware"),
    "Contexte": (".middleware", "Contexte"),
    "ErrorHandlerMiddleware": (".middleware", "ErrorHandlerMiddleware"),
    "LogMiddleware": (".middleware", "LogMiddleware"),
    "Middleware": (".middleware", "Middleware"),
    "Pipeline": (".middleware", "Pipeline"),
    "RateLimitMiddleware": (".middleware", "RateLimitMiddleware"),
    "RetryMiddleware": (".middleware", "RetryMiddleware"),
    "SessionMiddleware": (".middleware", "SessionMiddleware"),
    "TimingMiddleware": (".middleware", "TimingMiddleware"),
    "ValidationMiddleware": (".middleware", "ValidationMiddleware"),
    # Monitoring
    "CollecteurMetriques": (".monitoring", "CollecteurMetriques"),
    "SanteSysteme": (".monitoring", "SanteSysteme"),
    "chronometre": (".monitoring", "chronometre"),
    "collecteur": (".monitoring", "collecteur"),
    "enregistrer_metrique": (".monitoring", "enregistrer_metrique"),
    "obtenir_snapshot": (".monitoring", "obtenir_snapshot"),
    "verifier_sante_globale": (".monitoring", "verifier_sante_globale"),
    # State
    "EtatApp": (".state", "EtatApp"),
    "EtatNavigation": (".state", "EtatNavigation"),
    "EtatCuisine": (".state", "EtatCuisine"),
    "EtatUI": (".state", "EtatUI"),
    "GestionnaireEtat": (".state", "GestionnaireEtat"),
    "naviguer": (".state", "naviguer"),
    "obtenir_etat": (".state", "obtenir_etat"),
    "revenir": (".state", "revenir"),
    # Storage
    "MemorySessionStorage": (".storage", "MemorySessionStorage"),
    "SessionStorage": (".storage", "SessionStorage"),
    "StreamlitSessionStorage": (".storage", "StreamlitSessionStorage"),
    "configurer_storage": (".storage", "configurer_storage"),
    "obtenir_storage": (".storage", "obtenir_storage"),
    # Validation
    "EntreeJournalInput": (".validation", "EntreeJournalInput"),
    "EtapeInput": (".validation", "EtapeInput"),
    "IngredientInput": (".validation", "IngredientInput"),
    "IngredientStockInput": (".validation", "IngredientStockInput"),
    "NettoyeurEntrees": (".validation", "NettoyeurEntrees"),
    "ProjetInput": (".validation", "ProjetInput"),
    "RecetteInput": (".validation", "RecetteInput"),
    "RepasInput": (".validation", "RepasInput"),
    "RoutineInput": (".validation", "RoutineInput"),
    "TacheRoutineInput": (".validation", "TacheRoutineInput"),
    "valider_modele": (".validation", "valider_modele"),
}

__all__ = list(_LAZY_IMPORTS.keys())


def __getattr__(name: str) -> Any:
    """Chargement paresseux des symboles (PEP 562)."""
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        module = importlib.import_module(module_path, __name__)
        value = getattr(module, attr_name)
        # Cache dans le namespace du module pour éviter les appels répétés
        globals()[name] = value
        return value
    raise AttributeError(f"module 'src.core' has no attribute {name!r}")
