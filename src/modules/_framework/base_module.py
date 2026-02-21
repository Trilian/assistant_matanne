"""
Base Module - Classe de base pour tous les modules Streamlit.

Fournit une architecture standardisée avec:
- Injection de service automatique
- Gestion d'état préfixée
- Error boundary intégré
- Hooks de lifecycle
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Generic, TypeVar

import streamlit as st

from src.modules._framework.error_boundary import error_boundary
from src.modules._framework.state_manager import ModuleState

logger = logging.getLogger(__name__)

T = TypeVar("T")  # Type du service principal


class BaseModule(ABC, Generic[T]):
    """Classe de base pour tous les modules Streamlit.

    Fournit:
    - Initialisation automatique du session_state
    - Gestion d'erreurs unifiée
    - Service injection
    - Hooks de lifecycle

    Usage:
        class InventaireModule(BaseModule[ServiceInventaire]):
            titre = "Inventaire"
            icone = "📦"

            def get_service_factory(self):
                from src.services.inventaire import obtenir_service_inventaire
                return obtenir_service_inventaire

            def get_default_state(self) -> dict:
                return {"show_form": False, "filter": None}

            def render(self):
                self.render_header()
                # ... contenu du module
    """

    # Configuration du module (à surcharger)
    titre: str = "Module"
    icone: str = "📋"
    description: str = ""
    show_refresh_button: bool = True
    show_help_button: bool = False
    help_text: str = ""

    def __init__(self):
        self._service: T | None = None
        self._state: ModuleState | None = None

    @property
    def service(self) -> T:
        """Lazy-loaded service avec cache."""
        if self._service is None:
            factory = self.get_service_factory()
            if factory:
                self._service = factory()
        return self._service  # type: ignore[return-value]

    @property
    def state(self) -> ModuleState:
        """State manager du module."""
        if self._state is None:
            module_name = self._get_module_name()
            self._state = ModuleState(module_name, self.get_default_state())
        return self._state

    def _get_module_name(self) -> str:
        """Génère un nom de module unique basé sur la classe."""
        name = self.__class__.__name__.lower()
        # Retirer les suffixes communs
        for suffix in ("module", "view", "page"):
            if name.endswith(suffix):
                name = name[: -len(suffix)]
        return name or "module"

    @abstractmethod
    def get_service_factory(self) -> Callable[[], T] | None:
        """Retourne la factory du service principal.

        Retourner None si le module n'a pas de service.
        """
        return None

    def get_default_state(self) -> dict[str, Any]:
        """Retourne les valeurs par défaut du state.

        À surcharger pour définir le state initial.
        """
        return {}

    @abstractmethod
    def render(self) -> None:
        """Rendu principal du module.

        À implémenter dans chaque module.
        """
        pass

    def render_header(self, show_divider: bool = True) -> None:
        """Rendu du header avec titre et description."""
        col1, col2, col3 = st.columns([9, 1, 1])

        with col1:
            st.title(f"{self.icone} {self.titre}")
            if self.description:
                st.caption(self.description)

        with col2:
            if self.show_help_button and self.help_text:
                st.markdown(
                    f'<span title="{self.help_text}" style="cursor: help; font-size: 1.5rem;">❓</span>',
                    unsafe_allow_html=True,
                )

        with col3:
            if self.show_refresh_button:
                # Note: Le bouton refresh déclenche un rerun automatique
                # car st.button() avec callback vide rerender la page
                st.button("🔄", help="Rafraîchir", key=f"{self._get_module_name()}_refresh")

        if show_divider:
            st.divider()

    def render_tabs(self, tabs_config: dict[str, Callable[[], None]]) -> None:
        """Rendu d'onglets avec le contenu associé.

        Args:
            tabs_config: Dict {nom_onglet: fonction_render}

        Usage:
            self.render_tabs({
                "📊 Stock": self._render_stock,
                "⚠️ Alertes": self._render_alertes,
            })
        """
        tab_names = list(tabs_config.keys())
        tabs = st.tabs(tab_names)

        for tab, (name, render_fn) in zip(tabs, tabs_config.items(), strict=False):
            with tab:
                with error_boundary(f"Erreur dans l'onglet {name}"):
                    render_fn()

    def on_mount(self) -> None:
        """Hook appelé avant le premier render.

        Utile pour initialiser des données ou vérifier des permissions.
        """
        pass

    def on_unmount(self) -> None:
        """Hook appelé lors de la destruction du module.

        Utile pour cleanup de ressources.
        """
        pass

    def on_error(self, error: Exception) -> None:
        """Hook appelé en cas d'erreur.

        Permet de logger ou notifier des erreurs spécifiques.
        """
        logger.error(f"Erreur dans {self.titre}: {error}", exc_info=True)

    def run(self) -> None:
        """Point d'entrée du module avec error boundary.

        Cette méthode orchestre le lifecycle complet:
        1. on_mount()
        2. render() avec error boundary
        3. on_error() en cas d'exception
        """
        try:
            self.on_mount()

            with error_boundary(
                titre=f"Erreur dans {self.titre}",
                afficher_details=True,
                metadata={"module": self.__class__.__name__},
            ):
                self.render()
        except Exception as e:
            self.on_error(e)
            raise


def module_app(module_class: type[BaseModule]) -> Callable[[], None]:
    """Décorateur/Factory pour créer la fonction app() standard.

    Usage comme décorateur:
        @module_app
        class InventaireModule(BaseModule):
            ...

    Usage comme factory:
        app = module_app(InventaireModule)

    Les deux génèrent automatiquement la fonction app() exportable.
    """

    def app() -> None:
        module_class().run()

    # Préserver le nom et la doc
    app.__name__ = "app"
    app.__doc__ = f"Point d'entrée du module {module_class.__name__}"
    app.__module__ = module_class.__module__

    return app


def create_simple_module(
    titre: str,
    icone: str,
    render_fn: Callable[[], None],
    description: str = "",
    service_factory: Callable | None = None,
    default_state: dict | None = None,
) -> Callable[[], None]:
    """Crée un module simple sans définir une classe.

    Utile pour les modules très simples ou le prototypage rapide.

    Usage:
        app = create_simple_module(
            titre="Mon Module",
            icone="📦",
            render_fn=lambda: st.write("Hello"),
        )
    """

    class SimpleModule(BaseModule):
        pass

    SimpleModule.titre = titre
    SimpleModule.icone = icone
    SimpleModule.description = description

    SimpleModule.get_service_factory = lambda self: service_factory
    SimpleModule.get_default_state = lambda self: default_state or {}
    SimpleModule.render = lambda self: render_fn()

    return module_app(SimpleModule)


__all__ = [
    "BaseModule",
    "module_app",
    "create_simple_module",
]
