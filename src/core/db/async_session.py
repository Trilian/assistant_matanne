"""
Session Async - Gestion asynchrone des sessions SQLAlchemy.

Support AsyncIO complet pour les opérations de base de données,
utilisant asyncpg comme driver asynchrone.

Fonctions pour:
- Créer l'engine async PostgreSQL avec retry automatique
- Context managers asynchrones pour les sessions
- Décorateurs pour les fonctions async utilisant la DB

Usage::

    from src.core.db.async_session import (
        obtenir_contexte_db_async,
        obtenir_moteur_async,
        avec_session_db_async,
    )

    # Context manager async
    async with obtenir_contexte_db_async() as db:
        result = await db.execute(select(Recette))
        recettes = result.scalars().all()

    # Décorateur
    @avec_session_db_async
    async def charger_recettes(db: AsyncSession) -> list[Recette]:
        result = await db.execute(select(Recette))
        return result.scalars().all()
"""

from __future__ import annotations

import asyncio
import functools
import logging
import threading
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Callable, ParamSpec, TypeVar

from sqlalchemy.exc import DatabaseError, OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from ..config import obtenir_parametres
from ..constants import DB_CONNECTION_RETRY, DB_CONNECTION_TIMEOUT
from ..exceptions import ErreurBaseDeDonnees

logger = logging.getLogger(__name__)

__all__ = [
    "obtenir_moteur_async",
    "reinitialiser_moteur_async",
    "obtenir_fabrique_session_async",
    "obtenir_contexte_db_async",
    "obtenir_db_async_securise",
    "avec_session_db_async",
    "verifier_connexion_async",
]

# ═══════════════════════════════════════════════════════════
# SINGLETON ASYNC ENGINE
# ═══════════════════════════════════════════════════════════

_async_engine_lock = threading.Lock()
_async_engine_instance: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None

P = ParamSpec("P")
T = TypeVar("T")


def _convertir_url_async(database_url: str) -> str:
    """Convertit une URL PostgreSQL sync vers async (asyncpg)."""
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql+psycopg2://"):
        return database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql+asyncpg://"):
        return database_url
    else:
        # Pour SQLite (tests), utiliser aiosqlite
        if database_url.startswith("sqlite://"):
            return database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return database_url


async def _creer_engine_async_impl(
    database_url: str,
    debug: bool = False,
    nombre_tentatives: int = DB_CONNECTION_RETRY,
    delai_tentative: float = 2.0,
) -> AsyncEngine:
    """Implémentation interne de création d'engine async avec retry.

    Args:
        database_url: URL de connexion PostgreSQL (sera convertie en async)
        debug: Active l'echo SQL
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        AsyncEngine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    async_url = _convertir_url_async(database_url)
    derniere_erreur: Exception | None = None

    for tentative in range(nombre_tentatives):
        try:
            # Configuration des connect_args pour asyncpg
            connect_args: dict[str, Any] = {}
            if "postgresql" in async_url:
                connect_args = {
                    "timeout": DB_CONNECTION_TIMEOUT,
                    "command_timeout": DB_CONNECTION_TIMEOUT,
                }

            moteur = create_async_engine(
                async_url,
                poolclass=NullPool,  # NullPool recommandé pour async
                echo=debug,
                connect_args=connect_args,
            )

            # Test de connexion
            async with moteur.connect() as conn:
                from sqlalchemy import text

                await conn.execute(text("SELECT 1"))

            logger.info(f"[OK] Connexion DB async établie (tentative {tentative + 1})")
            return moteur

        except (OperationalError, DatabaseError) as e:
            derniere_erreur = e
            logger.warning(
                f"[ERROR] Tentative async {tentative + 1}/{nombre_tentatives} échouée: {e}"
            )

            if tentative < nombre_tentatives - 1:
                await asyncio.sleep(delai_tentative)
                continue

        except Exception as e:
            # Pour les autres erreurs (ex: module asyncpg non installé)
            derniere_erreur = e
            logger.warning(
                f"[ERROR] Tentative async {tentative + 1}/{nombre_tentatives} échouée: {e}"
            )

            if tentative < nombre_tentatives - 1:
                await asyncio.sleep(delai_tentative)
                continue

    message_erreur = (
        f"Impossible de se connecter async après {nombre_tentatives} tentatives: {derniere_erreur}"
    )
    logger.error(message_erreur)
    raise ErreurBaseDeDonnees(
        message_erreur,
        message_utilisateur="Impossible de se connecter à la base de données",
    )


async def obtenir_moteur_async(
    nombre_tentatives: int = DB_CONNECTION_RETRY,
    delai_tentative: float = 2.0,
) -> AsyncEngine:
    """
    Crée l'engine PostgreSQL async avec retry automatique.

    Utilise un singleton thread-safe pour réutiliser l'engine existant.

    Args:
        nombre_tentatives: Nombre de tentatives de reconnexion
        delai_tentative: Délai entre les tentatives en secondes

    Returns:
        AsyncEngine SQLAlchemy configuré

    Raises:
        ErreurBaseDeDonnees: Si connexion impossible après toutes les tentatives
    """
    global _async_engine_instance

    if _async_engine_instance is not None:
        return _async_engine_instance

    with _async_engine_lock:
        # Double-check locking
        if _async_engine_instance is not None:
            return _async_engine_instance

        parametres = obtenir_parametres()
        moteur = await _creer_engine_async_impl(
            parametres.DATABASE_URL,
            parametres.DEBUG,
            nombre_tentatives,
            delai_tentative,
        )
        _async_engine_instance = moteur
        return moteur


async def reinitialiser_moteur_async() -> None:
    """Réinitialise le cache du moteur async (utile pour les tests)."""
    global _async_engine_instance, _async_session_factory

    with _async_engine_lock:
        if _async_engine_instance is not None:
            try:
                await _async_engine_instance.dispose()
            except Exception:
                pass
            _async_engine_instance = None
        _async_session_factory = None


# ═══════════════════════════════════════════════════════════
# SESSION FACTORY ASYNC
# ═══════════════════════════════════════════════════════════


async def obtenir_fabrique_session_async() -> async_sessionmaker[AsyncSession]:
    """
    Retourne une session factory async (cachée au niveau module).

    La factory est créée une seule fois puis réutilisée.

    Returns:
        Async session factory configurée
    """
    global _async_session_factory

    if _async_session_factory is not None:
        return _async_session_factory

    with _async_engine_lock:
        if _async_session_factory is None:
            moteur = await obtenir_moteur_async()
            _async_session_factory = async_sessionmaker(
                moteur,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
    return _async_session_factory


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGERS ASYNC
# ═══════════════════════════════════════════════════════════


@asynccontextmanager
async def obtenir_contexte_db_async() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager async avec gestion d'erreurs robuste.

    Enrichit automatiquement les logs avec le correlation_id du contexte
    d'observabilité, permettant de tracer chaque transaction DB.

    Yields:
        AsyncSession SQLAlchemy active

    Raises:
        ErreurBaseDeDonnees: En cas d'erreur de connexion ou requête

    Example:
        >>> async with obtenir_contexte_db_async() as db:
        >>>     result = await db.execute(select(Recette))
        >>>     recettes = result.scalars().all()
    """
    fabrique = await obtenir_fabrique_session_async()
    db = fabrique()

    # Récupérer le correlation_id pour tracer cette transaction
    try:
        from ..observability import obtenir_contexte

        ctx = obtenir_contexte()
        cid = ctx.correlation_id
    except Exception:
        cid = "--------"

    try:
        logger.debug("[%s] Session DB async ouverte", cid)
        yield db
        await db.commit()
        logger.debug("[%s] Session DB async commit OK", cid)

    except OperationalError as e:
        await db.rollback()
        logger.error("[%s] Erreur opérationnelle DB async: %s", cid, e)
        raise ErreurBaseDeDonnees(
            f"Erreur réseau/connexion: {e}",
            message_utilisateur="Problème de connexion à la base de données",
        ) from e

    except DatabaseError as e:
        await db.rollback()
        logger.error("[%s] Erreur base de données async: %s", cid, e)
        raise ErreurBaseDeDonnees(
            str(e), message_utilisateur="Erreur lors de l'opération en base de données"
        ) from e

    except Exception as e:
        await db.rollback()
        logger.error("[%s] Erreur inattendue async: %s", cid, e)
        raise

    finally:
        await db.close()


@asynccontextmanager
async def obtenir_db_async_securise() -> AsyncGenerator[AsyncSession | None, None]:
    """
    Version sécurisée qui n'interrompt pas l'application.

    Yields:
        AsyncSession ou None si erreur

    Example:
        >>> async with obtenir_db_async_securise() as db:
        >>>     if db:
        >>>         result = await db.execute(select(Recette))
    """
    try:
        async with obtenir_contexte_db_async() as db:
            yield db
    except ErreurBaseDeDonnees:
        logger.warning("DB async non disponible, fallback")
        yield None
    except Exception as e:
        logger.error(f"Erreur DB async: {e}")
        yield None


# ═══════════════════════════════════════════════════════════
# DECORATEUR ASYNC
# ═══════════════════════════════════════════════════════════


def avec_session_db_async(func: Callable[P, T]) -> Callable[P, T]:
    """
    Décorateur qui injecte automatiquement une session async.

    Attend un paramètre ``db: AsyncSession`` dans la signature de la fonction.
    Gère automatiquement le cycle de vie de la session (commit/rollback/close).

    Example:
        >>> @avec_session_db_async
        >>> async def creer_recette(data: dict, db: AsyncSession) -> Recette:
        >>>     recette = Recette(**data)
        >>>     db.add(recette)
        >>>     return recette
    """

    @functools.wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        # Si 'db' est déjà fourni, utiliser celui-là
        if "db" in kwargs and kwargs["db"] is not None:
            return await func(*args, **kwargs)

        # Sinon, créer un nouveau contexte
        async with obtenir_contexte_db_async() as db:
            kwargs["db"] = db
            return await func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


# ═══════════════════════════════════════════════════════════
# UTILS ASYNC
# ═══════════════════════════════════════════════════════════


async def verifier_connexion_async() -> tuple[bool, str]:
    """
    Vérifie la connexion asynchrone à la base de données.

    Returns:
        Tuple (succès, message)
    """
    try:
        moteur = await obtenir_moteur_async()

        async with moteur.connect() as conn:
            from sqlalchemy import text

            await conn.execute(text("SELECT 1"))

        return True, "Connexion async OK"

    except ErreurBaseDeDonnees as e:
        return False, f"Erreur connexion async: {e.message}"

    except Exception as e:
        logger.error(f"[ERROR] Test connexion async échoué: {e}")
        return False, f"Erreur: {str(e)}"


async def executer_dans_transaction_async(
    operations: list[Callable[[AsyncSession], Any]],
) -> list[Any]:
    """
    Exécute plusieurs opérations dans une seule transaction async.

    Toutes les opérations sont commitées ensemble ou rollback ensemble.

    Args:
        operations: Liste de fonctions async prenant une session

    Returns:
        Liste des résultats de chaque opération

    Raises:
        ErreurBaseDeDonnees: Si une opération échoue

    Example:
        >>> async def op1(db): ...
        >>> async def op2(db): ...
        >>> results = await executer_dans_transaction_async([op1, op2])
    """
    async with obtenir_contexte_db_async() as db:
        resultats = []
        for operation in operations:
            if asyncio.iscoroutinefunction(operation):
                resultat = await operation(db)
            else:
                resultat = operation(db)
            resultats.append(resultat)
        return resultats
