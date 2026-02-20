"""
Container - Conteneur d'injection de dépendances (IoC).

Conteneur léger, typé, sans dépendance externe.
Remplace les 6+ singletons ``global _var`` dispersés dans le core.

Scopes:
- SINGLETON : Une seule instance par process (ex: Engine, Config)
- SESSION   : Une instance par session Streamlit (future extension)
- TRANSIENT : Nouvelle instance à chaque résolution

Usage:
    >>> from src.core.container import conteneur
    >>> conteneur.singleton(Parametres, factory=lambda: Parametres())
    >>> params = conteneur.resolve(Parametres)

    # Enregistrement avec dépendances
    >>> conteneur.singleton(ClientIA, factory=lambda c: ClientIA(c.resolve(Parametres)))

    # Lifecycle
    >>> conteneur.initialiser()   # Crée tous les singletons eagerly
    >>> conteneur.fermer()        # Cleanup propre (dispose engines, etc.)
"""

from __future__ import annotations

import enum
import logging
import threading
from collections.abc import Callable
from typing import Any, TypeVar, overload

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Scope(enum.StrEnum):
    """Scope de vie d'un composant."""

    SINGLETON = "singleton"
    """Une seule instance pour tout le process."""

    SESSION = "session"
    """Une instance par session utilisateur (future extension)."""

    TRANSIENT = "transient"
    """Nouvelle instance à chaque résolution."""


class _Registration:
    """Enregistrement interne d'un composant."""

    __slots__ = ("scope", "factory", "instance", "cleanup_fn", "alias")

    def __init__(
        self,
        scope: Scope,
        factory: Callable[..., Any],
        cleanup_fn: Callable[[Any], None] | None = None,
        alias: str | None = None,
    ) -> None:
        self.scope = scope
        self.factory = factory
        self.instance: Any = None
        self.cleanup_fn = cleanup_fn
        self.alias = alias


class Conteneur:
    """
    Conteneur IoC léger et thread-safe.

    Supporte l'enregistrement par type ou alias, avec résolution
    automatique des dépendances via factory functions.
    """

    def __init__(self) -> None:
        self._registrations: dict[type | str, _Registration] = {}
        self._lock = threading.RLock()
        self._initialized = False

    # ─── Enregistrement ───────────────────────────────

    def singleton(
        self,
        service_type: type[T],
        *,
        factory: Callable[..., T],
        cleanup: Callable[[T], None] | None = None,
        alias: str | None = None,
    ) -> None:
        """
        Enregistre un composant en scope SINGLETON.

        Args:
            service_type: Type du service à enregistrer
            factory: Factory function (reçoit ``conteneur`` en argument si nécessaire)
            cleanup: Fonction de nettoyage appelée lors de ``fermer()``
            alias: Alias string alternatif pour la résolution
        """
        with self._lock:
            reg = _Registration(
                scope=Scope.SINGLETON,
                factory=factory,
                cleanup_fn=cleanup,
                alias=alias,
            )
            self._registrations[service_type] = reg
            if alias:
                self._registrations[alias] = reg
            logger.debug(f"Enregistré SINGLETON: {service_type.__name__}")

    def factory(
        self,
        service_type: type[T],
        *,
        factory: Callable[..., T],
        alias: str | None = None,
    ) -> None:
        """
        Enregistre un composant en scope TRANSIENT (nouvelle instance à chaque appel).

        Args:
            service_type: Type du service
            factory: Factory function
            alias: Alias string
        """
        with self._lock:
            reg = _Registration(
                scope=Scope.TRANSIENT,
                factory=factory,
                alias=alias,
            )
            self._registrations[service_type] = reg
            if alias:
                self._registrations[alias] = reg
            logger.debug(f"Enregistré TRANSIENT: {service_type.__name__}")

    def instance(self, service_type: type[T], value: T, *, alias: str | None = None) -> None:
        """
        Enregistre une instance existante (SINGLETON pré-créé).

        Args:
            service_type: Type du service
            value: Instance à enregistrer
            alias: Alias string
        """
        with self._lock:
            reg = _Registration(
                scope=Scope.SINGLETON,
                factory=lambda: value,
            )
            reg.instance = value
            self._registrations[service_type] = reg
            if alias:
                self._registrations[alias] = reg
            logger.debug(f"Enregistré INSTANCE: {service_type.__name__}")

    # ─── Résolution ───────────────────────────────────

    @overload
    def resolve(self, service_type: type[T]) -> T: ...

    @overload
    def resolve(self, service_type: str) -> Any: ...

    def resolve(self, service_type: type[T] | str) -> T | Any:
        """
        Résout un composant enregistré.

        Args:
            service_type: Type ou alias à résoudre

        Returns:
            Instance du composant

        Raises:
            KeyError: Si le composant n'est pas enregistré
        """
        with self._lock:
            if service_type not in self._registrations:
                type_name = (
                    service_type.__name__ if isinstance(service_type, type) else service_type
                )
                raise KeyError(
                    f"Composant non enregistré: {type_name}. "
                    f"Utilisez conteneur.singleton() ou conteneur.factory() d'abord."
                )

            reg = self._registrations[service_type]

            if reg.scope == Scope.SINGLETON:
                if reg.instance is None:
                    reg.instance = self._create_instance(reg)
                return reg.instance

            # TRANSIENT : nouvelle instance à chaque fois
            return self._create_instance(reg)

    def try_resolve(self, service_type: type[T] | str) -> T | None:
        """
        Résout un composant ou retourne None si non enregistré.

        Args:
            service_type: Type ou alias

        Returns:
            Instance ou None
        """
        try:
            return self.resolve(service_type)
        except KeyError:
            return None

    def est_enregistre(self, service_type: type | str) -> bool:
        """Vérifie si un composant est enregistré."""
        return service_type in self._registrations

    # ─── Lifecycle ────────────────────────────────────

    def initialiser(self) -> None:
        """
        Initialise tous les singletons de manière eager.

        Utile pour détecter les erreurs de configuration au démarrage
        plutôt qu'à la première utilisation.
        """
        if self._initialized:
            return

        with self._lock:
            erreurs: list[str] = []

            for key, reg in self._registrations.items():
                if isinstance(key, str):
                    continue  # Sauter les alias
                if reg.scope == Scope.SINGLETON and reg.instance is None:
                    try:
                        reg.instance = self._create_instance(reg)
                        logger.debug(f"Singleton initialisé: {key.__name__}")
                    except Exception as e:
                        erreurs.append(f"{key.__name__}: {e}")
                        logger.warning(f"Échec init singleton {key.__name__}: {e}")

            self._initialized = True

            if erreurs:
                logger.warning(
                    f"Conteneur initialisé avec {len(erreurs)} erreur(s): " f"{', '.join(erreurs)}"
                )
            else:
                n_singletons = sum(
                    1
                    for k, r in self._registrations.items()
                    if isinstance(k, type) and r.scope == Scope.SINGLETON
                )
                logger.info(f"Conteneur initialisé ({n_singletons} singletons)")

    def fermer(self) -> None:
        """
        Ferme et nettoie tous les composants avec cleanup.

        Appelle les fonctions ``cleanup`` enregistrées dans l'ordre
        inverse de création.
        """
        with self._lock:
            cleanups = [
                (key, reg)
                for key, reg in self._registrations.items()
                if isinstance(key, type) and reg.instance is not None and reg.cleanup_fn is not None
            ]

            for key, reg in reversed(cleanups):
                try:
                    reg.cleanup_fn(reg.instance)
                    logger.debug(f"Cleanup OK: {key.__name__}")
                except Exception as e:
                    logger.error(f"Cleanup échoué pour {key.__name__}: {e}")

            # Réinitialiser
            for reg in self._registrations.values():
                reg.instance = None

            self._initialized = False
            logger.info("Conteneur fermé")

    def reinitialiser(self) -> None:
        """Ferme puis réinitialise le conteneur."""
        self.fermer()
        self._registrations.clear()

    # ─── Introspection ────────────────────────────────

    def lister_composants(self) -> dict[str, dict[str, Any]]:
        """
        Retourne la liste des composants enregistrés.

        Returns:
            Dict {nom: {scope, instancié, alias}}
        """
        result: dict[str, dict[str, Any]] = {}

        for key, reg in self._registrations.items():
            if isinstance(key, str):
                continue  # Sauter les alias

            name = key.__name__
            result[name] = {
                "scope": reg.scope.value,
                "instancie": reg.instance is not None,
                "alias": reg.alias,
                "a_cleanup": reg.cleanup_fn is not None,
            }

        return result

    def obtenir_statistiques(self) -> dict[str, Any]:
        """Retourne les statistiques du conteneur."""
        composants = self.lister_composants()
        return {
            "total_enregistres": len(composants),
            "singletons": sum(1 for c in composants.values() if c["scope"] == "singleton"),
            "transients": sum(1 for c in composants.values() if c["scope"] == "transient"),
            "instancies": sum(1 for c in composants.values() if c["instancie"]),
            "initialise": self._initialized,
        }

    # ─── Private ──────────────────────────────────────

    def _create_instance(self, reg: _Registration) -> Any:
        """Crée une instance via la factory."""
        import inspect

        sig = inspect.signature(reg.factory)

        # Si la factory accepte un argument (le conteneur), le passer
        if len(sig.parameters) >= 1:
            param = next(iter(sig.parameters.values()))
            if param.annotation in (Conteneur, "Conteneur") or param.name in (
                "c",
                "conteneur",
                "container",
            ):
                return reg.factory(self)

        return reg.factory()

    def __repr__(self) -> str:
        n = sum(1 for k in self._registrations if isinstance(k, type))
        return f"<Conteneur({n} composants, init={self._initialized})>"


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════

conteneur = Conteneur()
"""Instance globale du conteneur IoC."""

__all__ = [
    "Conteneur",
    "Scope",
    "conteneur",
]
