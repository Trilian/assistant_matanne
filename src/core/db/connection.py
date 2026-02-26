"""
st.connection pour Supabase — Connection pooling natif Streamlit.

Innovation 1.2 du rapport d'audit — Impact immédiat.

Migre de obtenir_moteur() vers st.connection("supabase") pour bénéficier:
- Connection pooling natif Streamlit
- Retry automatique
- Intégration secrets.toml
- Health check intégré

IMPORTANT: Ce module est COMPLÉMENTAIRE à obtenir_moteur().
    L'ancienne API reste fonctionnelle pour les tests et le CLI.
    En mode Streamlit, utiliser obtenir_connexion_supabase().

Usage:
    from src.core.db.connection import obtenir_connexion_supabase, requete_sql

    # Connexion Streamlit-native (avec cache et retry)
    conn = obtenir_connexion_supabase()

    # Requête simple avec retour DataFrame
    df = requete_sql("SELECT * FROM recettes WHERE categorie = :cat", params={"cat": "dessert"})

    # Requête avec session SQLAlchemy (pour ORM)
    with obtenir_session_supabase() as session:
        recettes = session.query(Recette).all()
"""

from __future__ import annotations

import logging
import threading
from contextlib import contextmanager
from typing import Any, Generator

import streamlit as st
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

__all__ = [
    "SupabaseConnection",
    "obtenir_connexion_supabase",
    "requete_sql",
    "obtenir_session_supabase",
]


# ═══════════════════════════════════════════════════════════
# SUPABASE CONNECTION CLASS — Hérite de st.connection
# ═══════════════════════════════════════════════════════════


class SupabaseConnection(st.connections.SQLConnection):
    """Connection Supabase via st.connection avec pooling Streamlit natif.

    Étend SQLConnection avec:
    - Configuration automatique depuis settings ou secrets.toml
    - Health check spécifique PostgreSQL
    - Session factory ORM intégrée
    - Retry automatique Streamlit

    Usage:
        conn = st.connection("supabase", type=SupabaseConnection)
        df = conn.query("SELECT * FROM recettes LIMIT 10")
    """

    _session_factory: sessionmaker | None = None
    _factory_lock = threading.Lock()

    def _connect(self, **kwargs) -> Any:
        """Connexion avec configuration automatique Supabase.

        Résout l'URL de connexion depuis (par priorité):
        1. secrets.toml → [connections.supabase].url
        2. Paramètres application → DATABASE_URL
        3. Variable d'environnement → DATABASE_URL
        """
        # Tenter de charger l'URL depuis la config applicative
        if "url" not in kwargs:
            try:
                from src.core.config import obtenir_parametres

                params = obtenir_parametres()
                kwargs["url"] = params.DATABASE_URL
            except Exception:
                pass

        return super()._connect(**kwargs)

    def health_check(self) -> dict[str, Any]:
        """Vérifie la santé de la connexion PostgreSQL.

        Returns:
            Dict avec statut, version, tables, etc.
        """
        try:
            df = self.query(
                "SELECT version(), current_database(), pg_size_pretty(pg_database_size(current_database())) as size",
                ttl=60,
            )
            row = df.iloc[0] if len(df) > 0 else {}

            return {
                "status": "healthy",
                "version": row.get("version", "unknown"),
                "database": row.get("current_database", "unknown"),
                "size": row.get("size", "unknown"),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    def get_session(self) -> Session:
        """Obtient une Session SQLAlchemy ORM depuis la connexion Streamlit.

        Lazy-creates la session factory une seule fois.

        Returns:
            Session SQLAlchemy liée au pool Streamlit
        """
        if self._session_factory is None:
            with self._factory_lock:
                if self._session_factory is None:
                    engine = self._instance  # Engine sous-jacent de SQLConnection
                    self._session_factory = sessionmaker(
                        autocommit=False,
                        autoflush=False,
                        bind=engine,
                        expire_on_commit=False,
                    )

        return self._session_factory()

    @contextmanager
    def session_context(self) -> Generator[Session, None, None]:
        """Context manager pour session ORM avec auto-commit/rollback.

        Usage:
            conn = obtenir_connexion_supabase()
            with conn.session_context() as session:
                recettes = session.query(Recette).all()
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def table_count(self, table_name: str) -> int:
        """Compte le nombre de lignes dans une table.

        Args:
            table_name: Nom de la table

        Returns:
            Nombre de lignes
        """
        df = self.query(f"SELECT count(*) as cnt FROM {table_name}", ttl=30)
        return int(df.iloc[0]["cnt"]) if len(df) > 0 else 0


# ═══════════════════════════════════════════════════════════
# HELPERS PUBLICS — API simplifiée
# ═══════════════════════════════════════════════════════════


def _is_streamlit_context() -> bool:
    """Vérifie si on est dans un contexte Streamlit (script run)."""
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except ImportError:
        return False


@st.cache_resource
def _creer_connexion() -> SupabaseConnection:
    """Crée la connexion Supabase (cachée par Streamlit).

    Appelé une seule fois grâce à @st.cache_resource.
    """
    try:
        # Tenter d'obtenir l'URL depuis la config
        from src.core.config import obtenir_parametres

        params = obtenir_parametres()
        url = params.DATABASE_URL
    except Exception:
        url = None

    if url:
        conn = st.connection(
            "supabase",
            type=SupabaseConnection,
            url=url,
        )
    else:
        # Fallback: laisser Streamlit résoudre depuis secrets.toml
        conn = st.connection("supabase", type=SupabaseConnection)

    logger.info("[OK] Connexion Supabase via st.connection établie")
    return conn


def obtenir_connexion_supabase() -> SupabaseConnection:
    """Obtient la connexion Supabase (thread-safe, pooled).

    En mode Streamlit: utilise st.connection avec pooling natif.
    Hors Streamlit: fallback vers obtenir_moteur() classique.

    Returns:
        SupabaseConnection instance

    Usage:
        conn = obtenir_connexion_supabase()
        df = conn.query("SELECT * FROM recettes LIMIT 10", ttl=300)
    """
    if _is_streamlit_context():
        return _creer_connexion()

    # Hors Streamlit — lever une erreur informative
    raise RuntimeError(
        "obtenir_connexion_supabase() nécessite un contexte Streamlit. "
        "Utiliser obtenir_moteur() / obtenir_contexte_db() en dehors de Streamlit."
    )


def requete_sql(
    query: str,
    params: dict[str, Any] | None = None,
    ttl: int = 300,
) -> pd.DataFrame:
    """Exécute une requête SQL et retourne un DataFrame.

    Utilise le cache Streamlit automatique (ttl).

    Args:
        query: Requête SQL (format :param pour les paramètres)
        params: Paramètres de la requête
        ttl: Durée de cache en secondes

    Returns:
        pandas DataFrame avec les résultats

    Usage:
        df = requete_sql(
            "SELECT * FROM recettes WHERE categorie = :cat",
            params={"cat": "dessert"},
            ttl=600,
        )
    """
    conn = obtenir_connexion_supabase()
    return conn.query(query, params=params, ttl=ttl)


@contextmanager
def obtenir_session_supabase() -> Generator[Session, None, None]:
    """Context manager pour session ORM via le pool Streamlit.

    Alternative à obtenir_contexte_db() quand on veut bénéficier
    du connection pooling natif Streamlit.

    Usage:
        with obtenir_session_supabase() as session:
            recettes = session.query(Recette).filter_by(categorie="dessert").all()

    Raises:
        RuntimeError: Si hors contexte Streamlit
    """
    conn = obtenir_connexion_supabase()
    with conn.session_context() as session:
        yield session
