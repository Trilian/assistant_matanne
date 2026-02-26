"""
Fragments - Composants auto-refresh avec isolation pour Streamlit 1.36+.

Les fragments permettent de créer des sections de l'UI qui se rafraîchissent
indépendamment du reste de la page, améliorant les performances.

Patterns disponibles:
- auto_refresh_fragment: Refresh automatique à intervalle
- isolated_fragment: Fragment isolé sans rerun global
- lazy_fragment: Chargement conditionnel
- with_loading_state: Wrapper avec spinner
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _has_fragment_support() -> bool:
    """Vérifie si Streamlit supporte st.fragment."""
    return hasattr(st, "fragment")


def _has_run_every_support() -> bool:
    """Vérifie si st.fragment supporte run_every (Streamlit 1.36+)."""
    if not _has_fragment_support():
        return False
    # Tenter de détecter le support de run_every
    import inspect

    try:
        sig = inspect.signature(st.fragment)
        return "run_every" in sig.parameters
    except (ValueError, TypeError):
        return False


def auto_refresh_fragment(interval_seconds: int = 30) -> Callable[[F], F]:
    """Décorateur pour créer un fragment avec auto-refresh.

    Le fragment se rafraîchit automatiquement à l'intervalle spécifié
    sans rerun de toute la page.

    Args:
        interval_seconds: Intervalle de rafraîchissement en secondes

    Usage:
        @auto_refresh_fragment(interval_seconds=60)
        def widget_alertes():
            alertes = service.get_alertes()
            for a in alertes:
                st.warning(a.message)

    Note: Requiert Streamlit >= 1.36.0 pour st.fragment avec run_every.
          Fallback silencieux sur versions antérieures.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _has_run_every_support():
                try:

                    @st.fragment(run_every=interval_seconds)
                    def _fragment():
                        return func(*args, **kwargs)

                    return _fragment()
                except TypeError as e:
                    logger.debug(f"auto_refresh fallback: {e}")

            # Fallback: exécution normale
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def isolated_fragment(func: F) -> F:
    """Fragment isolé qui ne trigger pas de rerun global.

    Utile pour les formulaires et interactions qui ne doivent
    pas rafraîchir toute la page.

    Usage:
        @isolated_fragment
        def formulaire_ajout():
            with st.form("add_form"):
                nom = st.text_input("Nom")
                if st.form_submit_button("Ajouter"):
                    # Le submit ne rerun pas tout le module
                    service.ajouter(nom)
                    st.success("Ajouté!")

    Note: Fallback transparent si st.fragment non disponible.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if _has_fragment_support():
            try:

                @st.fragment
                def _fragment():
                    return func(*args, **kwargs)

                return _fragment()
            except (TypeError, AttributeError) as e:
                logger.debug(f"isolated_fragment fallback: {e}")

        # Fallback: exécution normale
        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def lazy_fragment(
    fragment_key: str,
    load_condition: Callable[[], bool] | None = None,
) -> Callable[[F], F]:
    """Fragment chargé paresseusement selon une condition.

    Le contenu n'est rendu que si la condition est vraie,
    avec mémorisation pour éviter les recalculs.

    Args:
        fragment_key: Clé unique pour le cache
        load_condition: Fonction qui retourne True si le fragment doit se charger

    Usage:
        @lazy_fragment("details_panel", lambda: st.session_state.get("show_details"))
        def afficher_details():
            # N'est exécuté que si show_details est True
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            should_load = load_condition() if load_condition else True

            if not should_load:
                return None

            cache_key = f"_lazy_{fragment_key}"
            if cache_key not in st.session_state:
                st.session_state[cache_key] = True

            if _has_fragment_support():
                try:

                    @st.fragment
                    def _fragment():
                        return func(*args, **kwargs)

                    return _fragment()
                except (TypeError, AttributeError):
                    pass

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def with_loading_state(
    loading_message: str = "Chargement...",
    show_spinner: bool = True,
    skeleton: bool = False,
) -> Callable[[F], F]:
    """Wrapper qui affiche un état de chargement pendant l'exécution.

    Args:
        loading_message: Message affiché pendant le chargement
        show_spinner: Si True, utilise st.spinner (bloquant visuel)
        skeleton: Si True, affiche un skeleton shimmer au lieu du spinner/texte

    Usage:
        @with_loading_state("Chargement des données...")
        def charger_donnees_lourdes():
            return service.get_big_data()

        @with_loading_state("Recettes", skeleton=True)
        def charger_recettes():
            return service.get_recettes()
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if skeleton:
                from src.ui.components.skeleton import skeleton_pendant_chargement

                placeholder = skeleton_pendant_chargement(loading_message)
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    placeholder.empty()
            elif show_spinner:
                with st.spinner(loading_message):
                    return func(*args, **kwargs)
            else:
                placeholder = st.empty()
                placeholder.info(f"⏳ {loading_message}")
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    placeholder.empty()

        return wrapper  # type: ignore[return-value]

    return decorator


def conditional_render(
    condition: Callable[[], bool],
    fallback: Callable[[], None] | None = None,
) -> Callable[[F], F]:
    """Décorateur pour rendu conditionnel avec fallback optionnel.

    Args:
        condition: Fonction qui retourne True si le rendu doit se faire
        fallback: Fonction appelée si la condition est False

    Usage:
        @conditional_render(
            condition=lambda: st.session_state.get("is_admin"),
            fallback=lambda: st.warning("Accès réservé aux administrateurs")
        )
        def admin_panel():
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if condition():
                return func(*args, **kwargs)
            elif fallback:
                return fallback()
            return None

        return wrapper  # type: ignore[return-value]

    return decorator


def debounced_callback(
    delay_ms: int = 300,
    key: str = "",
) -> Callable[[F], F]:
    """Décorateur pour debouncer les callbacks (évite les appels répétés).

    Args:
        delay_ms: Délai en millisecondes avant exécution
        key: Clé pour identifier le debounce

    Note: Implémentation simplifiée - le vrai debounce nécessite JavaScript.
    Cette version utilise un compteur pour éviter les doubles appels rapides.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import time

            cache_key = f"_debounce_{key or func.__name__}"
            last_call = st.session_state.get(cache_key, 0)
            now = time.time() * 1000  # ms

            if now - last_call > delay_ms:
                st.session_state[cache_key] = now
                return func(*args, **kwargs)

            return None

        return wrapper  # type: ignore[return-value]

    return decorator


__all__ = [
    "auto_refresh_fragment",
    "isolated_fragment",
    "lazy_fragment",
    "with_loading_state",
    "conditional_render",
    "debounced_callback",
]
