"""
Core - Module central de l'application.

Expose les composants essentiels pour l'ensemble de l'application.
Convention : Noms en français uniquement.
"""

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONFIGURATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .config import Parametres, obtenir_parametres

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LOGGING
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .logging import (
    GestionnaireLog,
    obtenir_logger,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DATABASE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .database import (
    GestionnaireMigrations,
    initialiser_database,
    obtenir_contexte_db,
    obtenir_db_securise,
    obtenir_infos_db,
    obtenir_moteur,
    verifier_connexion,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .state import EtatApp, GestionnaireEtat, naviguer, obtenir_etat, revenir

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .cache import (
    Cache,
    LimiteDebit,
    cached,
)

# Cache multi-niveaux
from .cache_multi import (
    CacheMultiNiveau,
    obtenir_cache,
    avec_cache_multi,
    EntreeCache,
    StatistiquesCache,
)

# Mode hors ligne
from .offline import (
    StatutConnexion,
    GestionnaireConnexion,
    TypeOperation,
    OperationEnAttente,
    FileAttenteHorsLigne,
    SynchroniseurHorsLigne,
    avec_mode_hors_ligne,
    afficher_statut_connexion,
    afficher_panneau_sync,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ERRORS BASE (pures, sans UI)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .errors_base import (
    ExceptionApp,
    ErreurValidation,
    ErreurNonTrouve,
    ErreurBaseDeDonnees,
    ErreurServiceIA,
    ErreurLimiteDebit,
    ErreurServiceExterne,
    ErreurConfiguration,
    exiger_champs,
    valider_type,
    valider_plage,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ERRORS (avec UI Streamlit)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .errors import (
    gerer_erreurs,
    afficher_erreur_streamlit,
    GestionnaireErreurs,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# DECORATORS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .decorators import (
    avec_session_db,
    avec_cache,
    avec_gestion_erreurs,
    avec_validation,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATORS PYDANTIC (depuis validation.py)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .validation import (
    RecetteInput,
    IngredientInput,
    EtapeInput,
    IngredientStockInput,
    RepasInput,
    RoutineInput,
    TacheRoutineInput,
    EntreeJournalInput,
    ProjetInput,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .validation import (
    NettoyeurEntrees,
    valider_modele,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# AI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .ai import AnalyseurIA, CacheIA, ClientIA, obtenir_client_ia

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .constants import *

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PERFORMANCE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .performance import (
    ProfileurFonction,
    MoniteurMemoire,
    OptimiseurSQL,
    TableauBordPerformance,
    ChargeurComposant,
    profiler,
    antirrebond,
    limiter_debit,
    mesurer_temps,
    suivre_requete,
    afficher_panneau_performance,
    afficher_badge_mini_performance,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SQL OPTIMIZER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .sql_optimizer import (
    EcouteurSQLAlchemy,
    DetecteurN1,
    ChargeurParLots,
    ConstructeurRequeteOptimisee,
    afficher_analyse_sql,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# REDIS CACHE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .redis_cache import (
    ConfigurationRedis,
    CacheMemoire,
    CacheRedis,
    avec_cache_redis,
    obtenir_cache_redis,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# LAZY LOADER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .lazy_loader import (
    ChargeurModuleDiffere,
    RouteurOptimise,
    afficher_stats_chargement_differe,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MULTI-TENANT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

from .multi_tenant import (
    ContexteUtilisateur,
    RequeteMultiLocataire,
    ServiceMultiLocataire,
    initialiser_contexte_utilisateur_streamlit,
    definir_utilisateur_from_auth,
    creer_multi_tenant_service,
)

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

__all__ = [
    # Config
    "Parametres",
    "obtenir_parametres",
    # Logging
    "GestionnaireLog",
    "obtenir_logger",
    # Database
    "obtenir_moteur",
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "GestionnaireMigrations",
    # State
    "EtatApp",
    "GestionnaireEtat",
    "obtenir_etat",
    "naviguer",
    "revenir",
    # Cache
    "Cache",
    "cached",
    "LimiteDebit",
    # Cache multi-niveaux
    "CacheMultiNiveau",
    "obtenir_cache",
    "avec_cache_multi",
    "EntreeCache",
    "StatistiquesCache",
    # Mode hors ligne
    "StatutConnexion",
    "GestionnaireConnexion",
    "TypeOperation",
    "OperationEnAttente",
    "FileAttenteHorsLigne",
    "SynchroniseurHorsLigne",
    "avec_mode_hors_ligne",
    "afficher_statut_connexion",
    "afficher_panneau_sync",
    # Errors Base (pures)
    "ExceptionApp",
    "ErreurValidation",
    "ErreurNonTrouve",
    "ErreurBaseDeDonnees",
    "ErreurServiceIA",
    "ErreurLimiteDebit",
    "ErreurServiceExterne",
    "ErreurConfiguration",
    "exiger_champs",
    "valider_type",
    "valider_plage",
    # Errors (avec UI)
    "gerer_erreurs",
    "afficher_erreur_streamlit",
    "GestionnaireErreurs",
    # Decorators
    "avec_session_db",
    "avec_cache",
    "avec_gestion_erreurs",
    "avec_validation",
    # Validators Pydantic
    "RecetteInput",
    "IngredientInput",
    "EtapeInput",
    "IngredientStockInput",
    "RepasInput",
    "RoutineInput",
    "TacheRoutineInput",
    "EntreeJournalInput",
    "ProjetInput",
    # Validation
    "NettoyeurEntrees",
    "valider_modele",
    # AI
    "ClientIA",
    "obtenir_client_ia",
    "AnalyseurIA",
    "CacheIA",
    # Performance
    "ProfileurFonction",
    "MoniteurMemoire",
    "OptimiseurSQL",
    "TableauBordPerformance",
    "ChargeurComposant",
    "profiler",
    "antirrebond",
    "limiter_debit",
    "mesurer_temps",
    "suivre_requete",
    "afficher_panneau_performance",
    "afficher_badge_mini_performance",
    # SQL Optimizer
    "EcouteurSQLAlchemy",
    "DetecteurN1",
    "ChargeurParLots",
    "ConstructeurRequeteOptimisee",
    "afficher_analyse_sql",
    # Redis Cache
    "ConfigurationRedis",
    "CacheMemoire",
    "CacheRedis",
    "avec_cache_redis",
    "obtenir_cache_redis",
    # Lazy Loader
    "ChargeurModuleDiffere",
    "RouteurOptimise",
    "afficher_stats_chargement_differe",
    # Multi-Tenant
    "ContexteUtilisateur",
    "RequeteMultiLocataire",
    "ServiceMultiLocataire",
    "initialiser_contexte_utilisateur_streamlit",
    "definir_utilisateur_from_auth",
    "creer_multi_tenant_service",
]
