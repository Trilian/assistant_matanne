"""
Reactive Services — Invalidation de cache intelligente via Event Bus.

Ce module fournit un système réactif adapté à Streamlit où les services
peuvent déclarer des dépendances entre événements et caches. Quand un
événement de mutation est émis, les caches dépendants sont automatiquement
invalidés.

Architecture:
    1. Service A émet "recettes.created" via Event Bus
    2. ReactiveServiceMixin sur Service B reçoit l'événement
    3. Les caches liés (ex: "planning.suggestions") sont invalidés
    4. Optionnel: callback st.rerun() pour rafraîchir l'UI

Usage:
    class ServicePlanning(BaseService, ReactiveServiceMixin):
        # Déclare les invalidations automatiques
        _invalidation_rules = {
            "recettes.created": ["planning_suggestions", "courses_listes"],
            "recettes.updated": ["planning_suggestions"],
            "inventaire.updated": ["courses_suggestions"],
        }

        def __init__(self):
            super().__init__()
            self._setup_reactive()  # Active l'écoute Event Bus

        @reactive_cache(depends_on=["recettes.*", "inventaire.*"])
        def get_suggestions(self) -> list:
            ...

    # Dans l'UI Streamlit, on peut aussi déclencher un rerun:
    service.on_invalidation(lambda: st.rerun())

Patterns supportés:
    - Wildcards: "recettes.*" matche "recettes.created", "recettes.updated"
    - Multi-sources: plusieurs événements peuvent invalider le même cache
    - Callback UI: notification vers Streamlit pour rafraîchir

Thread-safety:
    - Les handlers Event Bus sont thread-safe (via Lock dans BusEvenements)
    - Le cache est thread-safe (via CacheMultiNiveau)
"""

from __future__ import annotations

import functools
import logging
import re
import threading
from collections.abc import Callable
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# CONFIGURATION — Règles d'invalidation par défaut
# ═══════════════════════════════════════════════════════════

# Mapping global: event_type → liste de cache_keys à invalider
# Les services peuvent surcharger via _invalidation_rules
DEFAULT_INVALIDATION_MAP: dict[str, list[str]] = {
    # Événements recettes
    "recettes.created": ["planning_suggestions", "courses_agregation"],
    "recettes.updated": ["planning_suggestions", "recettes_favoris"],
    "recettes.deleted": ["planning_suggestions", "recettes_favoris"],
    # Événements inventaire
    "inventaire.created": ["courses_suggestions", "recettes_disponibles"],
    "inventaire.updated": ["courses_suggestions", "recettes_disponibles"],
    "inventaire.deleted": ["courses_suggestions"],
    # Événements planning
    "planning.validated": ["courses_agregation", "courses_listes"],
    "planning.updated": ["courses_agregation"],
    # Événements courses
    "courses.completed": ["inventaire_stock", "courses_historique"],
}


# ═══════════════════════════════════════════════════════════
# REACTIVE SERVICE MIXIN
# ═══════════════════════════════════════════════════════════


class ReactiveServiceMixin:
    """
    Mixin pour services réactifs avec invalidation de cache automatique.

    Ajoute la capacité d'écouter l'Event Bus et d'invalider les caches
    quand des événements de mutation sont reçus.

    Attributes:
        _invalidation_rules: Dict des règles d'invalidation (à surcharger)
        _invalidation_callbacks: Callbacks appelés après invalidation
        _reactive_active: Flag pour activer/désactiver les réactions

    Usage:
        class MonService(BaseService, ReactiveServiceMixin):
            _invalidation_rules = {
                "stock.updated": ["mes_caches"],
            }

            def __init__(self):
                super().__init__()
                self._setup_reactive()
    """

    # Règles d'invalidation par défaut (à surcharger dans les sous-classes)
    _invalidation_rules: dict[str, list[str]] = {}

    # Callbacks appelés après invalidation (UI refresh, etc.)
    _invalidation_callbacks: list[Callable[[], None]] = []

    # Flag pour activer/désactiver les réactions
    _reactive_active: bool = True

    # Lock pour thread-safety des callbacks
    _reactive_lock: threading.Lock = threading.Lock()

    def _setup_reactive(self) -> None:
        """Configure l'écoute des événements pour invalidation automatique.

        Doit être appelé dans __init__ des sous-classes.
        """
        try:
            from src.services.core.events import obtenir_bus
        except ImportError:
            logger.debug("Event bus non disponible, réactivité désactivée")
            return

        bus = obtenir_bus()

        # Fusionner règles par défaut avec règles de la classe
        rules = {**DEFAULT_INVALIDATION_MAP, **self._invalidation_rules}

        # Collecter tous les patterns d'événements uniques
        event_patterns = set(rules.keys())

        # Souscrire à chaque pattern
        for pattern in event_patterns:
            handler = self._create_invalidation_handler(pattern, rules[pattern])
            bus.souscrire(pattern, handler, priority=10)  # Priorité haute

        service_name = getattr(self, "service_name", self.__class__.__name__)
        logger.debug(f"🔄 ReactiveService: {service_name} écoute {len(event_patterns)} patterns")

    def _create_invalidation_handler(self, pattern: str, cache_keys: list[str]) -> Callable:
        """Crée un handler d'invalidation pour un pattern donné."""

        def handler(event) -> None:
            if not self._reactive_active:
                return

            service_name = getattr(self, "service_name", self.__class__.__name__)
            logger.info(f"🔄 {service_name}: Invalidation déclenchée par {event.type}")

            # Invalider les caches
            invalidated = self._invalidate_caches(cache_keys)

            if invalidated:
                logger.info(f"🗑️  Caches invalidés: {', '.join(invalidated)}")

                # Appeler les callbacks (UI refresh, etc.)
                self._trigger_callbacks()

        return handler

    def _invalidate_caches(self, cache_keys: list[str]) -> list[str]:
        """Invalide une liste de clés de cache.

        Returns:
            Liste des clés effectivement invalidées.
        """
        invalidated = []

        try:
            from src.core.caching import cache_multi_niveau
        except ImportError:
            logger.debug("Cache multi-niveau non disponible")
            return invalidated

        cache = cache_multi_niveau()

        for key in cache_keys:
            try:
                # Invalider avec pattern (si wildcard)
                if "*" in key:
                    pattern = key.replace("*", ".*")
                    # Le cache supporte-t-il les patterns?
                    if hasattr(cache, "invalider_pattern"):
                        cache.invalider_pattern(pattern)
                        invalidated.append(key)
                else:
                    cache.invalider(key)
                    invalidated.append(key)
            except Exception as e:
                logger.debug(f"Erreur invalidation {key}: {e}")

        return invalidated

    def _trigger_callbacks(self) -> None:
        """Appelle tous les callbacks d'invalidation enregistrés."""
        with self._reactive_lock:
            callbacks = self._invalidation_callbacks.copy()

        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.warning(f"Erreur callback invalidation: {e}")

    def on_invalidation(self, callback: Callable[[], None]) -> None:
        """Enregistre un callback appelé après chaque invalidation.

        Utile pour déclencher st.rerun() dans l'UI.

        Args:
            callback: Fonction sans arguments à appeler
        """
        with self._reactive_lock:
            self._invalidation_callbacks.append(callback)

    def pause_reactive(self) -> None:
        """Pause temporaire des réactions (pour batch updates)."""
        self._reactive_active = False
        logger.debug("ReactiveService: réactions pausées")

    def resume_reactive(self) -> None:
        """Reprend les réactions après pause."""
        self._reactive_active = True
        logger.debug("ReactiveService: réactions reprises")


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR @reactive_cache — Cache avec dépendances déclaratives
# ═══════════════════════════════════════════════════════════


_reactive_registry: dict[str, set[str]] = {}  # cache_key → event_patterns


def reactive_cache(
    key: str | None = None,
    ttl: int = 300,
    depends_on: list[str] | None = None,
) -> Callable:
    """
    Décorateur pour cache avec dépendances d'invalidation déclaratives.

    La clé de cache est automatiquement invalidée quand un des événements
    déclarés dans `depends_on` est émis.

    Usage:
        @reactive_cache(key="planning_suggestions", depends_on=["recettes.*"])
        def get_suggestions(self) -> list:
            ...

    Args:
        key: Clé de cache (auto-générée si None)
        ttl: Durée de vie du cache (secondes)
        depends_on: Liste de patterns d'événements qui invalident ce cache

    Note:
        Les dépendances sont enregistrées globalement et utilisées par
        ReactiveServiceMixin pour l'invalidation automatique.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Générer la clé de cache si non fournie
        cache_key = key or f"{func.__module__}.{func.__qualname__}"

        # Enregistrer les dépendances
        if depends_on:
            _reactive_registry[cache_key] = set(depends_on)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            # Import tardif pour éviter les imports circulaires
            try:
                from src.core.caching import Cache
            except ImportError:
                return func(*args, **kwargs)

            # Check cache
            cached = Cache.obtenir(cache_key, ttl=ttl)
            if cached is not None:
                return cached

            # Execute et cache
            result = func(*args, **kwargs)
            if result is not None:
                Cache.definir(cache_key, result, ttl=ttl)

            return result

        # Stocker les métadonnées sur la fonction
        wrapper._cache_key = cache_key
        wrapper._depends_on = depends_on or []
        wrapper._ttl = ttl

        return wrapper

    return decorator


# ═══════════════════════════════════════════════════════════
# HELPERS — Utilitaires pour la réactivité
# ═══════════════════════════════════════════════════════════


def emit_mutation(
    event_type: str,
    data: dict[str, Any] | None = None,
    source: str = "",
) -> None:
    """
    Émet un événement de mutation via l'Event Bus.

    Raccourci pour les services qui veulent notifier d'une modification.

    Usage:
        # Dans un service après création
        emit_mutation("recettes.created", {"id": new_recipe.id})

    Args:
        event_type: Type d'événement (ex: "recettes.created")
        data: Données associées
        source: Service émetteur (auto-détecté si vide)
    """
    try:
        from src.services.core.events import obtenir_bus
    except ImportError:
        logger.debug("Event bus non disponible")
        return

    bus = obtenir_bus()
    bus.emettre(event_type, data or {}, source=source)


def get_reactive_dependencies(cache_key: str) -> set[str]:
    """Retourne les dépendances enregistrées pour une clé de cache."""
    return _reactive_registry.get(cache_key, set())


def get_all_reactive_caches() -> dict[str, set[str]]:
    """Retourne toutes les clés de cache réactives et leurs dépendances."""
    return _reactive_registry.copy()


__all__ = [
    "ReactiveServiceMixin",
    "reactive_cache",
    "emit_mutation",
    "get_reactive_dependencies",
    "get_all_reactive_caches",
    "DEFAULT_INVALIDATION_MAP",
]
