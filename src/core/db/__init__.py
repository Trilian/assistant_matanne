"""
Database - Module de gestion de la base de données.

Ce module fournit:
- Création et gestion de l'engine SQLAlchemy (sync et async)
- Gestion des sessions avec context managers (sync et async)
- Gestionnaire de migrations
- Health checks et utilitaires
"""

from .engine import obtenir_moteur, obtenir_moteur_securise
from .migrations import GestionnaireMigrations
from .session import (
    obtenir_contexte_db,
    obtenir_db_securise,
    obtenir_fabrique_session,
)
from .utils import (
    creer_toutes_tables,
    initialiser_database,
    obtenir_infos_db,
    vacuum_database,
    verifier_connexion,
    verifier_sante,
)

# Support AsyncIO (lazy import pour éviter dépendances optionnelles)
try:
    from .async_session import (
        avec_session_db_async,
        executer_dans_transaction_async,
        obtenir_contexte_db_async,
        obtenir_db_async_securise,
        obtenir_fabrique_session_async,
        obtenir_moteur_async,
        reinitialiser_moteur_async,
        verifier_connexion_async,
    )
except ImportError:
    # asyncpg/aiosqlite non installé
    pass

# st.connection Supabase (lazy import pour éviter dépendance Streamlit en tests)
try:
    from .connection import (
        SupabaseConnection,
        obtenir_connexion_supabase,
        obtenir_session_supabase,
        requete_sql,
    )
except ImportError:
    pass

# Connections unifiées v11 (Redis, APIs, WebSocket)
try:
    from .connections import (
        ExternalAPIConnection,
        RedisConnection,
        WebSocketConnection,
        obtenir_connexion_api,
        obtenir_connexion_redis,
        obtenir_connexion_websocket,
    )
except ImportError:
    pass

__all__ = [
    # Engine sync
    "obtenir_moteur",
    "obtenir_moteur_securise",
    # Session sync
    "obtenir_contexte_db",
    "obtenir_db_securise",
    "obtenir_fabrique_session",
    # Migrations
    "GestionnaireMigrations",
    # Utils
    "verifier_connexion",
    "obtenir_infos_db",
    "initialiser_database",
    "creer_toutes_tables",
    "verifier_sante",
    "vacuum_database",
    # st.connection Supabase
    "SupabaseConnection",
    "obtenir_connexion_supabase",
    "obtenir_session_supabase",
    "requete_sql",
    # Connections unifiées v11
    "RedisConnection",
    "ExternalAPIConnection",
    "WebSocketConnection",
    "obtenir_connexion_redis",
    "obtenir_connexion_api",
    "obtenir_connexion_websocket",
    # AsyncIO (si disponible)
    "obtenir_moteur_async",
    "reinitialiser_moteur_async",
    "obtenir_fabrique_session_async",
    "obtenir_contexte_db_async",
    "obtenir_db_async_securise",
    "avec_session_db_async",
    "verifier_connexion_async",
    "executer_dans_transaction_async",
]
