"""Décorateurs: cache multi-niveaux et cache UI Streamlit."""

import hashlib
import inspect
import logging
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def avec_cache(
    ttl: int = 300,
    key_prefix: str | None = None,
    key_func: Callable[..., str] | None = None,
    cache_none: bool = False,
):
    """
    Décorateur pour cache automatique avec TTL.

    Usage:
        @avec_cache(ttl=600, key_prefix="recettes")
        def charger_recettes(page: int = 1) -> list[Recette]:
            # Logique coûteuse
            return recettes

        @avec_cache(ttl=3600, key_func=lambda self, id: f"recette_{id}")
        def charger_recette(self, id: int) -> Recette:
            # Custom key generation
            return recette

        @avec_cache(ttl=300, cache_none=False)  # Ne cache jamais None
        def operation_risquee() -> dict | None:
            return None  # Ne sera PAS mis en cache

    Args:
        ttl: Durée de vie en secondes
        key_prefix: Préfixe pour la clé de cache
        key_func: Fonction personnalisée pour générer la clé (optionnel)
        cache_none: Si False (défaut), les résultats None ne sont PAS mis en cache.
            Empêche le cache poisoning quand un décorateur d'erreur retourne None
            comme valeur de fallback.

    Returns:
        Valeur en cache ou résultat du calcul
    """
    # Sentinelle pour distinguer "pas en cache" de "valeur None en cache"
    _CACHE_MISS = object()

    def decorator(func: F) -> F:
        # Pré-calculer la signature pour optimisation
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())

        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            from src.core.caching import CacheMultiNiveau

            cache = CacheMultiNiveau()

            # Générer clé de cache
            if key_func is not None:
                # Filtrer db des kwargs d'abord
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != "db"}

                # Essayer d'abord de passer les arguments par position
                try:
                    cache_key = key_func(*args, **filtered_kwargs)
                except TypeError:
                    # Reconstruire les kwargs en utilisant les noms de la fonction
                    full_kwargs = {}
                    for i, arg in enumerate(args):
                        if i < len(param_names):
                            param_name = param_names[i]
                            if param_name not in ("self", "db"):
                                full_kwargs[param_name] = arg

                    # Ajouter les kwargs nommés (sauf db)
                    for k, v in filtered_kwargs.items():
                        full_kwargs[k] = v

                    # Remplir les valeurs par défaut manquantes
                    for param_name, param in sig.parameters.items():
                        if param_name in ("self", "db"):
                            continue
                        if (
                            param_name not in full_kwargs
                            and param.default != inspect.Parameter.empty
                        ):
                            full_kwargs[param_name] = param.default

                    # Appeler key_func avec self + tous les kwargs nécessaires
                    if args:
                        cache_key = key_func(args[0], **full_kwargs)
                    else:
                        cache_key = key_func(**full_kwargs)
            else:
                prefix = key_prefix or func.__name__
                # Exclure 'db' des kwargs dans le cache key
                filtered_kwargs = {k: v for k, v in kwargs.items() if k != "db"}
                # Hash déterministe au lieu de str() (plus rapide et fiable)
                raw_key = f"{prefix}:{repr(args)}:{repr(sorted(filtered_kwargs.items()))}"
                cache_key = (
                    f"{prefix}_{hashlib.blake2b(raw_key.encode(), digest_size=16).hexdigest()}"
                )

            # Chercher dans le cache multi-niveaux (L1 → L2 → L3)
            cached_value = cache.get(cache_key, default=_CACHE_MISS)
            if cached_value is not _CACHE_MISS:
                logger.debug(f"Cache HIT: {cache_key}")
                return cached_value

            # Calculer et cacher (L1 + L2)
            logger.debug(f"Cache MISS: {cache_key}")
            result = func(*args, **kwargs)

            # Ne pas cacher None si cache_none=False (évite le cache poisoning
            # quand @avec_gestion_erreurs retourne None comme fallback)
            if result is not None or cache_none:
                cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper  # type: ignore

    return decorator


def cache_ui(
    ttl: int = 1800,
    show_spinner: bool = False,
):
    """
    Décorateur cache pour composants UI (bridge vers st.cache_data).

    Utilise ``st.cache_data`` natif de Streamlit quand disponible,
    sinon tombe en fallback sur ``avec_cache`` pour permettre les tests
    hors contexte Streamlit.

    **Politique de cache**:
    - Services/métier → ``@avec_cache`` (multi-niveaux, fonctionne sans Streamlit)
    - Composants UI → ``@cache_ui`` (optimisé Streamlit, fallback pour tests)

    Usage::

        @cache_ui(ttl=300, show_spinner=False)
        def generer_graphique(data: list[dict]) -> Figure:
            # Génération coûteuse d'un graphique
            return fig

    Args:
        ttl: Durée de vie en secondes (défaut: 30 min)
        show_spinner: Afficher un spinner pendant le calcul (défaut: False)

    Returns:
        Valeur en cache ou résultat du calcul
    """

    def decorator(func: F) -> F:
        try:
            import streamlit as st

            # Streamlit disponible: utiliser st.cache_data natif
            return st.cache_data(ttl=ttl, show_spinner=show_spinner)(func)
        except Exception:
            # Fallback: utiliser avec_cache multi-niveaux
            return avec_cache(ttl=ttl)(func)

    return decorator
