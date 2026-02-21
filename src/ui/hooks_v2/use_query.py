"""
use_query - Hook de data fetching avec cache et loading states.

Inspiré de TanStack Query (React Query), adapté pour Streamlit.
Gère automatiquement le cache, les états de chargement et les erreurs.

Inclut également use_mutation pour les opérations d'écriture avec
invalidation automatique des queries liées.

Usage:
    from src.ui.hooks_v2 import use_query, use_mutation

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
    elif result.is_empty:
        st.info("Aucune donnée")
    else:
        for recette in result.data:
            st.write(recette.nom)

    # Mutation avec invalidation
    mutation = use_mutation(
        "create_recette",
        lambda data: service.create(data),
        invalidate_queries=["recettes"],
    )
    if st.button("Créer"):
        mutation.mutate(form_data)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Callable, Generic, TypeVar

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

    @property
    def is_empty(self) -> bool:
        """True si data est None ou vide (liste, dict, etc.).

        Example:
            if result.is_empty:
                st.info("Aucune donnée")
        """
        if self.data is None:
            return True
        if hasattr(self.data, "__len__"):
            return len(self.data) == 0
        return False


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


@dataclass
class MutationState(Generic[T]):
    """État d'une mutation avec loading/error/data et invalidation de queries.

    Combine l'API riche par dataclass avec l'invalidation automatique
    des queries liées après succès.

    Attributes:
        is_loading: True si la mutation est en cours.
        is_error: True si la dernière mutation a échoué.
        is_success: True si la dernière mutation a réussi.
        data: Données retournées par la mutation.
        error: Exception si erreur, None sinon.

    Example:
        mutation = use_mutation("save", save_fn, invalidate_queries=["items"])
        if st.button("Sauvegarder"):
            mutation.mutate({"name": "test"})
        if mutation.is_success:
            st.success("Sauvegardé!")
    """

    is_loading: bool = False
    is_error: bool = False
    is_success: bool = False
    data: T | None = None
    error: Exception | None = None
    _key: str = field(default="", repr=False)
    _mutate_fn: Callable[..., T] | None = field(default=None, repr=False)
    _invalidate_queries: list[str] = field(default_factory=list, repr=False)
    _on_success: Callable[[], None] | None = field(default=None, repr=False)
    _on_error: Callable[[Exception], None] | None = field(default=None, repr=False)

    def mutate(self, *args: Any, **kwargs: Any) -> T | None:
        """Exécute la mutation de manière synchrone.

        Après succès, invalide automatiquement les queries listées
        dans ``invalidate_queries`` pour forcer leur rechargement.

        Returns:
            Le résultat de la mutation ou None si erreur.
        """
        if self._mutate_fn is None:
            return None

        # Set loading state
        st.session_state[f"{self._key}_loading"] = True
        st.session_state[f"{self._key}_error"] = None

        try:
            result = self._mutate_fn(*args, **kwargs)
            st.session_state[f"{self._key}_data"] = result
            st.session_state[f"{self._key}_success"] = True
            st.session_state[f"{self._key}_loading"] = False

            # Invalider les queries liées
            for query_key in self._invalidate_queries:
                full_key = f"_query_{query_key}"
                if full_key in st.session_state:
                    st.session_state[full_key]["status"] = QueryStatus.IDLE

            if self._on_success:
                self._on_success()

            return result
        except Exception as e:
            st.session_state[f"{self._key}_error"] = e
            st.session_state[f"{self._key}_success"] = False
            st.session_state[f"{self._key}_loading"] = False

            if self._on_error:
                self._on_error(e)

            return None

    def reset(self) -> None:
        """Réinitialise l'état de la mutation."""
        st.session_state[f"{self._key}_loading"] = False
        st.session_state[f"{self._key}_error"] = None
        st.session_state[f"{self._key}_data"] = None
        st.session_state[f"{self._key}_success"] = False


def use_mutation(
    key: str,
    mutation_fn: Callable[..., T],
    *,
    on_success: Callable[[], None] | None = None,
    on_error: Callable[[Exception], None] | None = None,
    invalidate_queries: list[str] | None = None,
) -> MutationState[T]:
    """Hook pour les mutations (create, update, delete) avec invalidation de queries.

    Fournit une API riche via ``MutationState`` avec:
    - États loading/error/success accessibles comme propriétés
    - Méthode ``mutate()`` pour exécuter la mutation
    - Invalidation automatique des queries après succès
    - Méthode ``reset()`` pour réinitialiser l'état

    Args:
        key: Clé unique dans session_state.
        mutation_fn: Fonction à exécuter lors de la mutation.
        on_success: Callback appelé après succès.
        on_error: Callback appelé après erreur.
        invalidate_queries: Liste de clés de queries à invalider après succès.

    Returns:
        MutationState avec méthodes mutate/reset et états loading/error/success.

    Example:
        def save_data(data: dict) -> bool:
            db.save(data)
            return True

        mutation = use_mutation(
            "save",
            save_data,
            invalidate_queries=["items", "stats"],
            on_success=lambda: st.toast("Sauvegardé!"),
        )

        if st.button("Sauvegarder"):
            mutation.mutate({"name": "test"})

        if mutation.is_loading:
            st.spinner("Sauvegarde...")
        elif mutation.is_error:
            st.error(f"Erreur: {mutation.error}")
        elif mutation.is_success:
            st.success("Sauvegardé!")
    """
    # Initialize state keys if not present
    for suffix, default in [
        ("_loading", False),
        ("_error", None),
        ("_data", None),
        ("_success", False),
    ]:
        state_key = f"{key}{suffix}"
        if state_key not in st.session_state:
            st.session_state[state_key] = default

    return MutationState(
        is_loading=st.session_state[f"{key}_loading"],
        is_error=st.session_state[f"{key}_error"] is not None,
        is_success=st.session_state[f"{key}_success"],
        data=st.session_state[f"{key}_data"],
        error=st.session_state[f"{key}_error"],
        _key=key,
        _mutate_fn=mutation_fn,
        _invalidate_queries=invalidate_queries or [],
        _on_success=on_success,
        _on_error=on_error,
    )


__all__ = [
    "QueryStatus",
    "QueryResult",
    "MutationState",
    "use_query",
    "use_mutation",
]
