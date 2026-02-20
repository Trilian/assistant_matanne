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
    # Events
    "BusEvenements": (".events", "BusEvenements"),
    "bus_evenements": (".events", "bus_evenements"),
    # Repository
    "Repository": (".repository", "Repository"),
    # Decorators
    "avec_cache": (".decorators", "avec_cache"),
    "avec_gestion_erreurs": (".decorators", "avec_gestion_erreurs"),
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
    # State
    "EtatApp": (".state", "EtatApp"),
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
