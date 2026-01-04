"""
Core - Point d'Entrée Unifié
Tous les composants essentiels en français
"""

# Config
from .config import obtenir_parametres, Parametres

# Database
from .database import (
    obtenir_contexte_db,
    obtenir_db_securise,
    verifier_connexion,
    obtenir_infos_db,
    verifier_sante,
    initialiser_database,
    creer_toutes_tables,
    GestionnaireMigrations
)

# Models
from .models import (
    Base,
    Ingredient,
    Recette,
    RecetteIngredient,
    EtapeRecette,
    ArticleInventaire,
    ArticleCourses,
    PlanningHebdomadaire,
    RepasPlanning,
    VersionRecette,
    ProfilEnfant,
    EntreeBienEtre,
    Routine,
    TacheRoutine,
    Projet,
    TacheProjet,
    ElementJardin,
    LogJardin,
    EvenementCalendrier,
    Utilisateur,
    ProfilUtilisateur,
    Notification
)

# AI
from .ai import (
    ClientIA,
    obtenir_client_ia,
    AnalyseurIA,
    analyser_liste_reponse,
    CacheIA
)

# Cache
from .cache import Cache, LimiteDebit

# Errors
from .errors import (
    ExceptionApp,
    ErreurValidation,
    ErreurNonTrouve,
    ErreurBaseDeDonnees,
    ErreurServiceIA,
    ErreurLimiteDebit,
    gerer_erreurs
)

# Validation
from .validation import (
    # Sanitization
    NettoyeurEntrees,

    # Pydantic Models
    IngredientInput,
    EtapeInput,
    RecetteInput,
    ArticleInventaireInput,
    ArticleCoursesInput,

    # Schémas Dict
    SCHEMA_RECETTE,
    SCHEMA_INVENTAIRE,
    SCHEMA_COURSES,

    # Helpers
    valider_modele,
    valider_formulaire_streamlit,
    valider_et_nettoyer_formulaire,
    afficher_erreurs_validation,

    # Decorator
    valider_entree,
)

# Logging
from .logging import GestionnaireLog, obtenir_logger

# State
from .state import (
    GestionnaireEtat,
    EtatApp,
    obtenir_etat,
    naviguer,
    revenir,
    obtenir_fil_ariane,
    est_mode_debug,
    nettoyer_etats_ui
)

__all__ = [
    # Config
    "obtenir_parametres",
    "Parametres",

    # Database
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "verifier_connexion",
    "obtenir_infos_db",
    "verifier_sante",
    "initialiser_database",
    "creer_toutes_tables",
    "GestionnaireMigrations",

    # Models
    "Base",
    "Ingredient",
    "Recette",
    "RecetteIngredient",
    "EtapeRecette",
    "ArticleInventaire",
    "ArticleCourses",
    "PlanningHebdomadaire",
    "RepasPlanning",
    "VersionRecette",
    "ProfilEnfant",
    "EntreeBienEtre",
    "Routine",
    "TacheRoutine",
    "Projet",
    "TacheProjet",
    "ElementJardin",
    "LogJardin",
    "EvenementCalendrier",
    "Utilisateur",
    "ProfilUtilisateur",
    "Notification",

    # AI
    "ClientIA",
    "obtenir_client_ia",
    "AnalyseurIA",
    "analyser_liste_reponse",
    "CacheIA",

    # Cache
    "Cache",
    "LimiteDebit",

    # Errors
    "ExceptionApp",
    "ErreurValidation",
    "ErreurNonTrouve",
    "ErreurBaseDeDonnees",
    "ErreurServiceIA",
    "ErreurLimiteDebit",
    "gerer_erreurs",

    # Validation
    "NettoyeurEntrees",
    "IngredientInput",
    "EtapeInput",
    "RecetteInput",
    "ArticleInventaireInput",
    "ArticleCoursesInput",
    "SCHEMA_RECETTE",
    "SCHEMA_INVENTAIRE",
    "SCHEMA_COURSES",
    "valider_modele",
    "valider_formulaire_streamlit",
    "valider_et_nettoyer_formulaire",
    "afficher_erreurs_validation",
    "valider_entree",

    # Logging
    "GestionnaireLog",
    "obtenir_logger",

    # State
    "GestionnaireEtat",
    "EtatApp",
    "obtenir_etat",
    "naviguer",
    "revenir",
    "obtenir_fil_ariane",
    "est_mode_debug",
    "nettoyer_etats_ui",
]