"""
use_query - Hook de data fetching avec cache et loading states.

Inspiré de TanStack Query (React Query), adapté pour Streamlit.
Gère automatiquement le cache, les états de chargement et les erreurs.

Usage:
    from src.ui.hooks_v2 import use_query

    # Simple query
    result = use_query(
        "recettes",
        lambda: service.get_recettes(),
        stale_time=300,
    )

    if result.is_loading:
        st.spinner("Chargement...")
    elif result.is_error:
        st.error(f"Erreur: {result.error}")
    else:
        for recette in result.data:
            st.write(recette.nom)

    # Refetch manuel
    if st.button("Actualiser"):
        result.refetch()
        st.rerun()
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable, Generic, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

T = TypeVar("T")


class QueryStatus(StrEnum):
    """États possibles d'une query."""

    IDLE = "idle"  # Pas encore exécutée
    LOADING = "loading"  # En cours d'exécution
    SUCCESS = "success"  # Terminée avec succès
    ERROR = "error"  # Terminée avec erreur


@dataclass
class QueryResult(Generic[T]):
    """Résultat d'une query avec metadata.

    Attributes:
        data: Données retournées (None si pas encore chargées ou erreur).
        status: État actuel de la query.
        error: Exception si erreur, None sinon.
        is_loading: True si en cours de chargement.
        is_error: True si erreur.
        is_success: True si succès.
        is_stale: True si les données sont périmées.
        refetch: Fonction pour relancer la query.
        last_updated: Timestamp de la dernière mise à jour.
    """

    data: T | None
    status: QueryStatus
    error: Exception | None
    is_loading: bool
    is_error: bool
    is_success: bool
    is_stale: bool
    refetch: Callable[[], None]
    last_updated: float | None


def use_query(
    key: str,
    query_fn: Callable[[], T],
    *,
    stale_time: int = 300,
    enabled: bool = True,
    on_success: Callable[[T], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
    retry: int = 0,
    retry_delay: float = 1.0,
) -> QueryResult[T]:
    """Hook de data fetching avec cache intégré.

    Caractéristiques:
    - Cache automatique avec TTL configurable
    - États de chargement (loading, success, error)
    - Refetch manuel
    - Callbacks on_success/on_error
    - Retry automatique sur erreur

    Args:
        key: Clé unique pour identifier la query.
        query_fn: Fonction qui retourne les données (synchrone).
        stale_time: Durée en secondes avant que les données soient stale.
        enabled: Si False, la query n'est pas exécutée automatiquement.
        on_success: Callback appelé après succès.
        on_error: Callback appelé après erreur.
        retry: Nombre de tentatives en cas d'erreur.
        retry_delay: Délai entre les tentatives (secondes).

    Returns:
        QueryResult avec les données et métadonnées.

    Example:
        result = use_query(
            "users",
            lambda: api.get_users(),
            stale_time=60,
            on_error=lambda e: logger.error(f"Failed: {e}"),
        )

        if result.is_loading:
            spinner_intelligent("Chargement des utilisateurs...")
        elif result.is_success:
            for user in result.data:
                st.write(user.name)
    """
    state_key = f"_query_{key}"

    # Initialiser l'état de la query
    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "data": None,
            "status": QueryStatus.IDLE,
            "error": None,
            "last_updated": None,
        }

    state = st.session_state[state_key]

    def is_stale() -> bool:
        """Vérifie si les données sont périmées."""
        if state["last_updated"] is None:
            return True
        return (time.time() - state["last_updated"]) > stale_time

    def refetch() -> None:
        """Relance la query."""
        state["status"] = QueryStatus.LOADING
        state["error"] = None

        attempts = 0
        max_attempts = retry + 1

        while attempts < max_attempts:
            try:
                data = query_fn()
                state["data"] = data
                state["status"] = QueryStatus.SUCCESS
                state["error"] = None
                state["last_updated"] = time.time()

                if on_success:
                    on_success(data)

                logger.debug(f"Query '{key}' succeeded")
                break

            except Exception as e:
                attempts += 1
                logger.warning(f"Query '{key}' failed (attempt {attempts}/{max_attempts}): {e}")

                if attempts >= max_attempts:
                    state["status"] = QueryStatus.ERROR
                    state["error"] = e

                    if on_error:
                        on_error(e)
                else:
                    time.sleep(retry_delay)

    # Auto-fetch si enabled et (idle ou stale)
    if enabled and (state["status"] == QueryStatus.IDLE or is_stale()):
        refetch()

    return QueryResult(
        data=state["data"],
        status=state["status"],
        error=state["error"],
        is_loading=state["status"] == QueryStatus.LOADING,
        is_error=state["status"] == QueryStatus.ERROR,
        is_success=state["status"] == QueryStatus.SUCCESS,
        is_stale=is_stale(),
        refetch=refetch,
        last_updated=state["last_updated"],
    )


def use_mutation(
    key: str,
    mutation_fn: Callable[[T], None],
    *,
    on_success: Callable[[], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
    invalidate_queries: list[str] | None = None,
) -> tuple[Callable[[T], None], bool, Exception | None]:
    """Hook pour les mutations (create, update, delete).

    Args:
        key: Clé unique.
        mutation_fn: Fonction de mutation.
        on_success: Callback succès.
        on_error: Callback erreur.
        invalidate_queries: Liste de queries à invalider après succès.

    Returns:
        Tuple (mutate_fn, is_loading, error).

    Example:
        mutate, is_loading, error = use_mutation(
            "create_recette",
            lambda data: service.create(data),
            invalidate_queries=["recettes"],
        )

        if st.button("Créer"):
            mutate(form_data)
            st.rerun()
    """
    state_key = f"_mutation_{key}"

    if state_key not in st.session_state:
        st.session_state[state_key] = {
            "is_loading": False,
            "error": None,
        }

    state = st.session_state[state_key]

    def mutate(data: T) -> None:
        state["is_loading"] = True
        state["error"] = None

        try:
            mutation_fn(data)

            # Invalider les queries liées
            if invalidate_queries:
                for query_key in invalidate_queries:
                    full_key = f"_query_{query_key}"
                    if full_key in st.session_state:
                        st.session_state[full_key]["status"] = QueryStatus.IDLE

            if on_success:
                on_success()

        except Exception as e:
            state["error"] = e
            if on_error:
                on_error(e)

        finally:
            state["is_loading"] = False

    return mutate, state["is_loading"], state["error"]


__all__ = [
    "QueryStatus",
    "QueryResult",
    "use_query",
    "use_mutation",
]
