"""
Core - Module central de l'application.

Expose les composants essentiels pour l'ensemble de l'application.
Convention : Noms en français uniquement.

Refactorisé en sous-modules thématiques:
- config/: Configuration Pydantic
- db/: Base de données et migrations
- caching/: Cache multi-niveaux
- validation/: Sanitization et schémas Pydantic
- ai/: Client IA, rate limiting, cache sémantique
"""

# ═══════════════════════════════════════════════════════════
# AI
# ═══════════════════════════════════════════════════════════
from .ai import AnalyseurIA, CacheIA, ClientIA, RateLimitIA, obtenir_client_ia

# ═══════════════════════════════════════════════════════════
# CACHE MULTI-NIVEAUX (sous-module caching/)
# ═══════════════════════════════════════════════════════════
from .caching import (
    Cache,
    CacheMultiNiveau,
    EntreeCache,
    StatistiquesCache,
    avec_cache_multi,
    cached,
    obtenir_cache,
)

# ═══════════════════════════════════════════════════════════
# CONFIGURATION (sous-module config/)
# ═══════════════════════════════════════════════════════════
from .config import Parametres, obtenir_parametres

# Note: Les constantes sont accessibles via `from src.core.constants import ...`
# Ne pas utiliser `from src.core import CONSTANT` - utiliser l'import direct depuis constants
# ═══════════════════════════════════════════════════════════
# DATABASE (nouveau sous-module db/)
# ═══════════════════════════════════════════════════════════
from .db import (
    GestionnaireMigrations,
    creer_toutes_tables,
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
    "RateLimitIA",
    # Cache multi-niveaux
    "CacheMultiNiveau",
    "obtenir_cache",
    "avec_cache_multi",
    "EntreeCache",
    "StatistiquesCache",
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
    # Lazy Loader
    "ChargeurModuleDiffere",
    "RouteurOptimise",
    "afficher_stats_chargement_differe",
]
