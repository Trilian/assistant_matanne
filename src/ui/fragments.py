"""
Décorateurs fragments pour rerenders partiels optimisés.

Abstraction au-dessus de st.fragment avec fallbacks gracieux et
patterns spécialisés (auto-refresh, lazy, isolated).

Usage:
    from src.ui.fragments import ui_fragment, auto_refresh, isolated, lazy

    @ui_fragment
    def widget_meteo():
        # Ne rerender que ce fragment
        data = get_meteo()
        st.metric("Température", f"{data['temp']}°C")

    @auto_refresh(seconds=60)
    def widget_alertes():
        # Refresh automatique sans rerun page complète
        alertes = service.get_alertes()
        for a in alertes:
            st.warning(a.message)

    @lazy(condition=lambda: st.session_state.get("show_details"))
    def panneau_details():
        # Chargé uniquement si condition vraie
        st.write("Détails...")

    @cached_fragment(ttl=300)
    def graphique_stats():
        # Cache + fragment pour performances maximales
        return create_heavy_chart()
"""

from __future__ import annotations

import logging
from functools import wraps
from typing import Any, Callable, TypeVar

import streamlit as st

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def _has_fragment() -> bool:
    """Vérifie support st.fragment (Streamlit 1.33+)."""
    if not hasattr(st, "fragment"):
        return False
    # st.fragment ne fonctionne pas sans ScriptRunContext (tests, CLI)
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except ImportError:
        return False


def _has_run_every() -> bool:
    """Vérifie support run_every (Streamlit 1.36+)."""
    if not _has_fragment():
        return False
    import inspect

    try:
        sig = inspect.signature(st.fragment)
        return "run_every" in sig.parameters
    except (ValueError, TypeError):
        return False


def ui_fragment(func: F) -> F:
    """Décorateur de base pour fragments isolés.

    Le composant décoré se rerender indépendamment du reste
    de la page, améliorant significativement les performances.

    Usage:
        @ui_fragment
        def widget_statistiques():
            data = compute_stats()  # Ne recalcule que si ce fragment change
            st.metric("Total", data["total"])

    Note:
        Fallback transparent si st.fragment non disponible.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if _has_fragment():
            try:

                @st.fragment
                def _frag():
                    return func(*args, **kwargs)

                return _frag()
            except Exception as e:
                logger.debug(f"ui_fragment fallback: {e}")

        return func(*args, **kwargs)

    return wrapper  # type: ignore[return-value]


def auto_refresh(seconds: int = 30) -> Callable[[F], F]:
    """Fragment avec auto-refresh périodique.

    Le composant se rafraîchit automatiquement à l'intervalle
    spécifié sans rerun de la page entière. Idéal pour:
    - Notifications en temps réel
    - Métriques live (stocks, alertes)
    - Indicateurs de statut

    Args:
        seconds: Intervalle de rafraîchissement en secondes

    Usage:
        @auto_refresh(seconds=60)
        def widget_notifications():
            notifs = NotificationService().get_unread()
            for n in notifs:
                st.info(n.message)

    Note:
        Requiert Streamlit >= 1.36.0 pour run_every.
        Fallback silencieux sur versions antérieures.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _has_run_every():
                try:

                    @st.fragment(run_every=seconds)
                    def _auto():
                        return func(*args, **kwargs)

                    return _auto()
                except Exception as e:
                    logger.debug(f"auto_refresh fallback: {e}")

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def isolated(func: F) -> F:
    """Fragment isolé qui ne trigger pas de rerun global.

    Parfait pour formulaires et interactions locales qui
    ne doivent pas rafraîchir toute la page.

    Usage:
        @isolated
        def formulaire_commentaire():
            with st.form("comment"):
                texte = st.text_area("Commentaire")
                if st.form_submit_button("Envoyer"):
                    save_comment(texte)
                    st.success("Envoyé!")

    Note:
        Alias pour ui_fragment avec sémantique claire.
    """
    return ui_fragment(func)


def lazy(
    condition: Callable[[], bool] | None = None,
    placeholder: str = "",
    show_skeleton: bool = False,
) -> Callable[[F], F]:
    """Fragment chargé conditionnellement (lazy loading).

    Le contenu n'est rendu que si la condition est vraie,
    avec un placeholder ou skeleton optionnel sinon.

    Args:
        condition: Fonction retournant True si le fragment doit charger
        placeholder: Texte affiché pendant l'attente (optionnel)
        show_skeleton: Afficher un skeleton loader au lieu du placeholder

    Usage:
        @lazy(condition=lambda: st.session_state.get("show_advanced"))
        def options_avancees():
            st.slider("Paramètre expert", 0, 100)

        @lazy(condition=lambda: data_loaded(), show_skeleton=True)
        def tableau_donnees():
            st.dataframe(heavy_data)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            should_load = condition() if condition else True

            if not should_load:
                if show_skeleton:
                    _render_skeleton()
                elif placeholder:
                    st.caption(placeholder)
                return None

            if _has_fragment():
                try:

                    @st.fragment
                    def _lazy():
                        return func(*args, **kwargs)

                    return _lazy()
                except (TypeError, AttributeError):
                    pass

            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def with_loading(
    message: str = "⏳ Chargement...",
    spinner: bool = True,
) -> Callable[[F], F]:
    """Wrapper affichant un état de chargement.

    Args:
        message: Message pendant le chargement
        spinner: Afficher un spinner animé

    Usage:
        @with_loading("Calcul des statistiques...")
        def compute_heavy_stats():
            return expensive_computation()
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if spinner:
                with st.spinner(message):
                    return func(*args, **kwargs)
            else:
                st.info(message)
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def cached_fragment(ttl: int = 300) -> Callable[[F], F]:
    """Combine fragment + cache pour performances optimales.

    Le résultat est mis en cache ET le fragment est isolé,
    offrant le meilleur des deux mondes pour les composants
    coûteux en calcul.

    Args:
        ttl: Durée de vie du cache en secondes (défaut: 5 min)

    Usage:
        @cached_fragment(ttl=600)
        def graphique_evolution():
            data = load_heavy_data()  # Mis en cache
            return create_chart(data)

    Note:
        Le cache est partagé entre tous les utilisateurs.
        Utiliser avec précaution pour données personnalisées.
    """

    def decorator(func: F) -> F:
        # Appliquer cache d'abord
        cached_func = st.cache_data(ttl=ttl)(func)

        # Puis fragment
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if _has_fragment():
                try:

                    @st.fragment
                    def _cached_frag():
                        return cached_func(*args, **kwargs)

                    return _cached_frag()
                except (TypeError, AttributeError):
                    pass

            return cached_func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def _render_skeleton() -> None:
    """Rend un skeleton loader simple."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
            background-size: 200% 100%;
            animation: shimmer 1.5s infinite;
            height: 100px;
            border-radius: 8px;
        "></div>
        <style>
        @keyframes shimmer {
            0% { background-position: -200% 0; }
            100% { background-position: 200% 0; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════
# FRAGMENT GROUP - Coordination de plusieurs fragments
# ═══════════════════════════════════════════════════════════


class FragmentGroup:
    """Groupe de fragments avec refresh coordonné.

    Permet de rafraîchir plusieurs fragments ensemble
    tout en les gardant isolés du reste de la page.

    Usage:
        group = FragmentGroup("dashboard")

        @group.register("metrics")
        def metrics_panel():
            st.metric("Ventes", 1234)

        @group.register("charts")
        def charts_panel():
            st.line_chart(data)

        # Rendre tous les fragments
        group.render_all()

        # Ou refresh tout le groupe
        if st.button("Actualiser"):
            group.refresh_all()
    """

    def __init__(self, name: str):
        """
        Args:
            name: Identifiant unique du groupe
        """
        self.name = name
        self._fragments: dict[str, Callable[..., Any]] = {}
        self._version_key = f"_frag_group_{name}_version"

    def register(self, fragment_name: str) -> Callable[[F], F]:
        """Enregistre un fragment dans le groupe.

        Args:
            fragment_name: Nom unique du fragment dans le groupe
        """

        def decorator(func: F) -> F:
            self._fragments[fragment_name] = func

            @wraps(func)
            @ui_fragment
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                # Inclure la version pour invalider le cache
                _ = st.session_state.get(self._version_key, 0)
                return func(*args, **kwargs)

            return wrapper  # type: ignore[return-value]

        return decorator

    def refresh_all(self) -> None:
        """Force le refresh de tous les fragments du groupe."""
        current = st.session_state.get(self._version_key, 0)
        st.session_state[self._version_key] = current + 1
        st.rerun()

    def render_all(self) -> None:
        """Rend tous les fragments enregistrés dans l'ordre."""
        for name, func in self._fragments.items():
            with st.container():
                func()

    def render(self, fragment_name: str) -> Any:
        """Rend un fragment spécifique par son nom."""
        if fragment_name not in self._fragments:
            raise KeyError(f"Fragment '{fragment_name}' non trouvé dans le groupe '{self.name}'")
        return self._fragments[fragment_name]()

    @property
    def fragment_names(self) -> list[str]:
        """Liste des noms de fragments enregistrés."""
        return list(self._fragments.keys())


# ═══════════════════════════════════════════════════════════
# HELPERS UTILITAIRES
# ═══════════════════════════════════════════════════════════


def rerun_fragment_only() -> None:
    """Rerun uniquement le fragment courant, pas la page entière.

    À appeler depuis l'intérieur d'un fragment pour forcer
    son refresh sans affecter le reste de la page.

    Usage:
        @ui_fragment
        def mon_widget():
            if st.button("Refresh"):
                rerun_fragment_only()  # Ou st.rerun() dans un fragment
    """
    # Dans un fragment, st.rerun() ne rerun que le fragment
    st.rerun()


def fragment_key(base: str, *args: Any) -> str:
    """Génère une clé unique pour un fragment avec arguments.

    Utile pour créer des fragments dynamiques avec état isolé.

    Args:
        base: Nom de base du fragment
        *args: Arguments pour rendre la clé unique

    Returns:
        Clé unique pour session_state

    Usage:
        @ui_fragment
        def item_card(item_id: int):
            key = fragment_key("item_card", item_id)
            expanded = st.session_state.get(f"{key}_expanded", False)
            ...
    """
    suffix = "_".join(str(a) for a in args)
    return f"_frag_{base}_{suffix}" if suffix else f"_frag_{base}"
