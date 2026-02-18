"""
Core - Module central de l'application.

Expose les composants essentiels pour l'ensemble de l'application.
Convention : Noms en français uniquement.

Refactorisé en sous-modules thématiques:
- config/: Configuration Pydantic
- db/: Base de données et migrations
- caching/: Cache multi-niveaux
- validation/: Sanitization et schémas Pydantic
- monitoring/: Performance et métriques
"""

# ═══════════════════════════════════════════════════════════
# AI
# ═══════════════════════════════════════════════════════════
# Rate limiting (source de vérité: ai/rate_limit.py)
from .ai import AnalyseurIA, CacheIA, ClientIA, LimiteDebit, RateLimitIA, obtenir_client_ia

# ═══════════════════════════════════════════════════════════
# CACHE (ancien module pour compatibilité)
# ═══════════════════════════════════════════════════════════
from .cache import (
    Cache,
    cached,
)

# ═══════════════════════════════════════════════════════════
# CACHE MULTI-NIVEAUX (nouveau sous-module caching/)
# ═══════════════════════════════════════════════════════════
from .caching import (
    CacheMultiNiveau,
    EntreeCache,
    StatistiquesCache,
    avec_cache_multi,
    obtenir_cache,
)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION (nouveau sous-module config/)
# ═══════════════════════════════════════════════════════════
from .config import Parametres, obtenir_parametres

# ═══════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════
from .constants import *

# ═══════════════════════════════════════════════════════════
# DATABASE (nouveau sous-module db/)
# ═══════════════════════════════════════════════════════════
from .db import (
    GestionnaireMigrations,
    creer_toutes_tables,
    get_db_context,
    initialiser_database,
    obtenir_contexte_db,
    obtenir_db_securise,
    obtenir_fabrique_session,
    obtenir_infos_db,
    obtenir_moteur,
    obtenir_moteur_securise,
    vacuum_database,
    verifier_connexion,
    verifier_sante,
)

# ═══════════════════════════════════════════════════════════
# DECORATORS
# ═══════════════════════════════════════════════════════════
from .decorators import (
    avec_cache,
    avec_gestion_erreurs,
    avec_session_db,
    avec_validation,
)

# ═══════════════════════════════════════════════════════════
# ERRORS (avec UI Streamlit)
# ═══════════════════════════════════════════════════════════
from .errors import (
    GestionnaireErreurs,
    afficher_erreur_streamlit,
    gerer_erreurs,
)

# ═══════════════════════════════════════════════════════════
# ERRORS BASE (pures, sans UI)
# ═══════════════════════════════════════════════════════════
from .errors_base import (
    ErreurBaseDeDonnees,
    ErreurConfiguration,
    ErreurLimiteDebit,
    ErreurNonTrouve,
    ErreurServiceExterne,
    ErreurServiceIA,
    ErreurValidation,
    ExceptionApp,
    exiger_champs,
    valider_plage,
    valider_type,
)

# ═══════════════════════════════════════════════════════════
# LAZY LOADER
# ═══════════════════════════════════════════════════════════
from .lazy_loader import (
    ChargeurModuleDiffere,
    RouteurOptimise,
    afficher_stats_chargement_differe,
)

# ═══════════════════════════════════════════════════════════
# LOGGING
# ═══════════════════════════════════════════════════════════
from .logging import (
    GestionnaireLog,
    obtenir_logger,
)

# ═══════════════════════════════════════════════════════════
# MONITORING (nouveau sous-module monitoring/)
# ═══════════════════════════════════════════════════════════
from .monitoring import (
    ChargeurComposant,
    MoniteurMemoire,
    OptimiseurSQL,
    ProfileurFonction,
    TableauBordPerformance,
    afficher_badge_mini_performance,
    afficher_panneau_performance,
    antirrebond,
    limiter_debit,
    mesurer_temps,
    profiler,
    suivre_requete,
)

# ═══════════════════════════════════════════════════════════
# MULTI-TENANT
# ═══════════════════════════════════════════════════════════
from .multi_tenant import (
    ContexteUtilisateur,
    RequeteMultiLocataire,
    ServiceMultiLocataire,
    creer_multi_tenant_service,
    definir_utilisateur_from_auth,
    initialiser_contexte_utilisateur_streamlit,
)

# Mode hors ligne
from .offline import (
    FileAttenteHorsLigne,
    GestionnaireConnexion,
    OperationEnAttente,
    StatutConnexion,
    SynchroniseurHorsLigne,
    TypeOperation,
    afficher_panneau_sync,
    afficher_statut_connexion,
    avec_mode_hors_ligne,
)

# ═══════════════════════════════════════════════════════════
# REDIS CACHE
# ═══════════════════════════════════════════════════════════
from .redis_cache import (
    CacheMemoire,
    CacheRedis,
    ConfigurationRedis,
    avec_cache_redis,
    obtenir_cache_redis,
)

# ═══════════════════════════════════════════════════════════
# SQL OPTIMIZER
# ═══════════════════════════════════════════════════════════
from .sql_optimizer import (
    ChargeurParLots,
    ConstructeurRequeteOptimisee,
    DetecteurN1,
    EcouteurSQLAlchemy,
    afficher_analyse_sql,
)

# ═══════════════════════════════════════════════════════════
# STATE
# ═══════════════════════════════════════════════════════════
from .state import EtatApp, GestionnaireEtat, naviguer, obtenir_etat, revenir

# ═══════════════════════════════════════════════════════════
# VALIDATION (nouveau sous-module validation/)
# ═══════════════════════════════════════════════════════════
from .validation import (
    EntreeJournalInput,
    EtapeInput,
    IngredientInput,
    IngredientStockInput,
    NettoyeurEntrees,
    ProjetInput,
    RecetteInput,
    RepasInput,
    RoutineInput,
    TacheRoutineInput,
    valider_modele,
)

# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Config
    "Parametres",
    "obtenir_parametres",
    # Logging
    "GestionnaireLog",
    "obtenir_logger",
    # Database
    "obtenir_moteur",
    "obtenir_moteur_securise",
    "obtenir_contexte_db",
    "get_db_context",  # Alias anglais
    "obtenir_db_securise",
    "obtenir_fabrique_session",
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "creer_toutes_tables",
    "verifier_sante",
    "vacuum_database",
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
    "LimiteDebit",  # Alias vers RateLimitIA
    "RateLimitIA",  # Source de vérité pour rate limiting
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
