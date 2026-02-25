"""
Service Registry — Registre centralisé de services thread-safe.

Remplace les singletons globaux non thread-safe (_service: X | None = None)
par un registre centralisé avec:
- Double-checked locking pour la création lazy
- Découverte automatique des services
- Health checks centralisés
- Métriques d'utilisation

Usage:
    from src.services.core.registry import registre, ServiceRegistry

    # Enregistrer une factory
    registre.enregistrer("inventaire", ServiceInventaire)

    # Obtenir un service (lazy, thread-safe)
    service = registre.obtenir("inventaire")

    # Health check global
    health = registre.health_check_global()
"""

from __future__ import annotations

import functools
import logging
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class _ServiceEntry:
    """Entrée dans le registre pour un service."""

    name: str
    factory: type | None = None
    instance: Any = None
    lock: threading.Lock = field(default_factory=threading.Lock)
    created_at: datetime | None = None
    access_count: int = 0
    last_accessed: datetime | None = None
    tags: set[str] = field(default_factory=set)


# ═══════════════════════════════════════════════════════════
# SERVICE REGISTRY — Thread-safe avec double-checked locking
# ═══════════════════════════════════════════════════════════


class ServiceRegistry:
    """
    Registre centralisé de services.

    Thread-safe via double-checked locking pattern.
    Chaque service n'est instancié qu'une seule fois (lazy singleton).

    Usage:
        registry = ServiceRegistry()

        # Enregistrer
        registry.enregistrer("recettes", ServiceRecettes, tags={"cuisine", "ia"})
        registry.enregistrer("inventaire", ServiceInventaire, tags={"cuisine"})

        # Obtenir (lazy, thread-safe)
        service = registry.obtenir("recettes")

        # Obtenir avec type
        service = registry.obtenir_type("recettes", ServiceRecettes)

        # Lister par tag
        cuisine_services = registry.par_tag("cuisine")
    """

    # Mapping tag → Protocol pour validation automatique (PEP 544)
    # Note: Protocols retirés (dead code). Mapping conservé pour compatibilité
    # si des protocols sont réintroduits à l'avenir.
    _PROTOCOL_PAR_TAG: dict[str, str] = {}

    def __init__(self):
        self._entries: dict[str, _ServiceEntry] = {}
        self._global_lock = threading.Lock()

    # ───────────────────────────────────────────────────────
    # ENREGISTREMENT
    # ───────────────────────────────────────────────────────

    def enregistrer(
        self,
        nom: str,
        factory: type | Callable[[], Any],
        tags: set[str] | None = None,
    ) -> None:
        """
        Enregistre une factory de service.

        Le service ne sera instancié que lors du premier appel à obtenir().
        Accepte une classe (appelée sans arguments) ou une callable factory.

        Args:
            nom: Nom unique du service
            factory: Classe ou callable qui crée le service
            tags: Tags pour la catégorisation (optionnel)
        """
        with self._global_lock:
            if nom in self._entries and self._entries[nom].instance is not None:
                logger.warning(f"⚠️ Service '{nom}' déjà instancié, ré-enregistrement ignoré")
                return

            factory_name = getattr(factory, "__name__", type(factory).__name__)
            self._entries[nom] = _ServiceEntry(
                name=nom,
                factory=factory,
                tags=tags or set(),
            )
            logger.debug(f"📦 Service enregistré: {nom} ({factory_name})")

    def enregistrer_instance(
        self,
        nom: str,
        instance: Any,
        tags: set[str] | None = None,
    ) -> None:
        """
        Enregistre une instance pré-créée.

        Utile pour les services qui nécessitent une configuration spéciale.

        Args:
            nom: Nom unique du service
            instance: Instance du service
            tags: Tags pour la catégorisation
        """
        with self._global_lock:
            self._entries[nom] = _ServiceEntry(
                name=nom,
                instance=instance,
                created_at=datetime.now(),
                tags=tags or set(),
            )
            logger.debug(f"📦 Instance enregistrée: {nom} ({type(instance).__name__})")

    # Alias anglais
    register = enregistrer
    register_instance = enregistrer_instance

    # ───────────────────────────────────────────────────────
    # OBTENTION — Double-checked locking
    # ───────────────────────────────────────────────────────

    def obtenir(self, nom: str) -> Any:
        """
        Obtient un service par son nom (lazy, thread-safe).

        Utilise le pattern double-checked locking :
        1. Check rapide sans lock (fast path)
        2. Si pas d'instance, lock + re-check + create

        Args:
            nom: Nom du service

        Returns:
            Instance du service

        Raises:
            KeyError: Si le service n'est pas enregistré
        """
        entry = self._entries.get(nom)
        if entry is None:
            raise KeyError(
                f"Service '{nom}' non enregistré. "
                f"Services disponibles: {list(self._entries.keys())}"
            )

        # Fast path — vérification sans lock
        if entry.instance is not None:
            with entry.lock:
                entry.access_count += 1
                entry.last_accessed = datetime.now()
            return entry.instance

        # Slow path — double-checked locking
        with entry.lock:
            # Re-vérifier après obtention du lock
            if entry.instance is None:
                if entry.factory is None:
                    raise ValueError(f"Service '{nom}' n'a ni instance ni factory")

                start = time.perf_counter()
                try:
                    entry.instance = entry.factory()
                    entry.created_at = datetime.now()
                    duration_ms = (time.perf_counter() - start) * 1000
                    logger.info(
                        f"📦 Service créé: {nom} ({entry.factory.__name__}) — {duration_ms:.1f}ms"
                    )
                except Exception as e:
                    logger.error(
                        f"❌ Erreur création service '{nom}': {e}",
                        exc_info=True,
                    )
                    raise

            entry.access_count += 1
            entry.last_accessed = datetime.now()
            return entry.instance

    def obtenir_type(self, nom: str, type_attendu: type[T]) -> T:
        """
        Obtient un service avec vérification de type.

        Args:
            nom: Nom du service
            type_attendu: Type attendu du service

        Returns:
            Instance typée du service
        """
        instance = self.obtenir(nom)
        if not isinstance(instance, type_attendu):
            raise TypeError(
                f"Service '{nom}' est {type(instance).__name__}, attendu {type_attendu.__name__}"
            )
        return instance

    # Alias anglais
    get = obtenir
    get_typed = obtenir_type

    # ───────────────────────────────────────────────────────
    # REQUÊTES
    # ───────────────────────────────────────────────────────

    def par_tag(self, tag: str) -> dict[str, Any]:
        """Retourne tous les services avec un tag donné."""
        return {
            name: self.obtenir(name) for name, entry in self._entries.items() if tag in entry.tags
        }

    def est_enregistre(self, nom: str) -> bool:
        """Vérifie si un service est enregistré."""
        return nom in self._entries

    def est_instancie(self, nom: str) -> bool:
        """Vérifie si un service est déjà instancié."""
        entry = self._entries.get(nom)
        return entry is not None and entry.instance is not None

    def lister(self) -> list[str]:
        """Liste les noms de tous les services enregistrés."""
        return list(self._entries.keys())

    # Alias anglais
    by_tag = par_tag
    is_registered = est_enregistre
    is_instantiated = est_instancie

    # ───────────────────────────────────────────────────────
    # HEALTH CHECK
    # ───────────────────────────────────────────────────────

    def health_check_global(self) -> dict[str, Any]:
        """
        Health check de tous les services instanciés.

        Retourne un résumé avec statut global + détails par service.
        """
        results: dict[str, Any] = {}
        total = 0
        healthy = 0
        erreurs = 0

        for name, entry in self._entries.items():
            if entry.instance is None:
                results[name] = {"status": "not_instantiated"}
                continue

            total += 1

            # Vérifier si le service a un health_check
            if hasattr(entry.instance, "health_check"):
                try:
                    health = entry.instance.health_check()
                    results[name] = {
                        "status": health.status.value if hasattr(health, "status") else "healthy",
                        "details": health,
                    }
                    healthy += 1
                except Exception as e:
                    results[name] = {
                        "status": "unhealthy",
                        "error": str(e),
                    }
                    erreurs += 1
            else:
                results[name] = {"status": "healthy", "note": "no health_check method"}
                healthy += 1

        return {
            "global_status": "healthy" if erreurs == 0 else "degraded",
            "total_services": len(self._entries),
            "instantiated": total,
            "healthy": healthy,
            "erreurs": erreurs,
            "services": results,
        }

    # ───────────────────────────────────────────────────────
    # MÉTRIQUES
    # ───────────────────────────────────────────────────────

    def obtenir_metriques(self) -> dict[str, Any]:
        """Retourne les métriques d'utilisation du registre."""
        return {
            "total_enregistres": len(self._entries),
            "total_instancies": sum(1 for e in self._entries.values() if e.instance is not None),
            "services": {
                name: {
                    "instancié": entry.instance is not None,
                    "créé_le": (entry.created_at.isoformat() if entry.created_at else None),
                    "accès": entry.access_count,
                    "dernier_accès": (
                        entry.last_accessed.isoformat() if entry.last_accessed else None
                    ),
                    "tags": list(entry.tags),
                }
                for name, entry in self._entries.items()
            },
        }

    # ───────────────────────────────────────────────────────
    # GESTION DU CYCLE DE VIE
    # ───────────────────────────────────────────────────────

    def reinitialiser(self, nom: str | None = None) -> None:
        """
        Réinitialise un service ou tous les services.

        Détruit l'instance et force la recréation au prochain appel.

        Args:
            nom: Nom du service (None = tous)
        """
        if nom:
            entry = self._entries.get(nom)
            if entry:
                with entry.lock:
                    entry.instance = None
                    entry.created_at = None
                    logger.info(f"📦 Service réinitialisé: {nom}")
        else:
            with self._global_lock:
                for entry in self._entries.values():
                    entry.instance = None
                    entry.created_at = None
                logger.info("📦 Tous les services réinitialisés")

    # Alias anglais
    reset = reinitialiser

    # ───────────────────────────────────────────────────────
    # VALIDATION PROTOCOLS (PEP 544)
    # ───────────────────────────────────────────────────────

    def valider_protocols(
        self,
        validations: dict[str, list[type]] | None = None,
    ) -> dict[str, list[str]]:
        """
        Valide que les services instanciés respectent les Protocols attendus.

        Utilise @runtime_checkable isinstance() pour vérifier la conformité
        structurelle des services au démarrage.

        Args:
            validations: Mapping {nom_service: [Protocol1, Protocol2, ...]}.
                         Si None, vérifie HealthCheckProtocol et CacheableProtocol
                         sur tous les services instanciés.

        Returns:
            Dict des violations: {nom_service: ["ne satisfait pas Protocol1"]}
            Dict vide = tous conformes.

        Usage:
            from src.services.core.base.protocols import (
                CRUDProtocol, AIServiceProtocol, HealthCheckProtocol
            )

            violations = registre.valider_protocols({
                "recettes": [CRUDProtocol, AIServiceProtocol],
                "inventaire": [CRUDProtocol],
            })
            if violations:
                logger.warning(f"Services non conformes: {violations}")
        """
        violations: dict[str, list[str]] = {}

        if validations is None:
            # Validation par défaut: pas de protocols communs à vérifier
            # (les protocols PEP 544 ont été retirés car jamais utilisés)
            common_checks: list[type] = []

            # Résoudre les Protocols liés aux tags (Audit §9.3 — ADOPTER PEP 544)
            _tag_protocol_map: dict[str, type] = {}
            try:
                from src.services.core.base import protocols as _proto_mod

                for tag, proto_name in self._PROTOCOL_PAR_TAG.items():
                    proto_cls = getattr(_proto_mod, proto_name, None)
                    if proto_cls is not None:
                        _tag_protocol_map[tag] = proto_cls
            except ImportError:
                pass

            for nom, entry in self._entries.items():
                if entry.instance is None:
                    continue
                service_violations = []
                for proto in common_checks:
                    if not isinstance(entry.instance, proto):
                        service_violations.append(f"ne satisfait pas {proto.__name__}")
                # Vérifier les Protocols par tag
                for tag in entry.tags:
                    proto_cls = _tag_protocol_map.get(tag)
                    if proto_cls is not None and not isinstance(entry.instance, proto_cls):
                        service_violations.append(f"tag '{tag}' requiert {proto_cls.__name__}")
                if service_violations:
                    violations[nom] = service_violations
        else:
            for nom, protocols in validations.items():
                if not self.est_enregistre(nom):
                    violations[nom] = [f"service '{nom}' non enregistré"]
                    continue
                if not self.est_instancie(nom):
                    continue  # Pas encore instancié, skip
                service = self.obtenir(nom)
                service_violations = []
                for proto in protocols:
                    if not isinstance(service, proto):
                        service_violations.append(f"ne satisfait pas {proto.__name__}")
                if service_violations:
                    violations[nom] = service_violations

        if violations:
            for nom, msgs in violations.items():
                logger.warning(f"⚠️ Service '{nom}': {', '.join(msgs)}")
        else:
            logger.debug("✅ Tous les services valident leurs Protocols")

        return violations

    # Alias anglais
    validate_protocols = valider_protocols


# ═══════════════════════════════════════════════════════════
# SINGLETON GLOBAL — Le registre principal
# ═══════════════════════════════════════════════════════════

_registre_lock = threading.Lock()
_registre_instance: ServiceRegistry | None = None


def obtenir_registre() -> ServiceRegistry:
    """Obtient le registre global de services (thread-safe)."""
    global _registre_instance
    if _registre_instance is None:
        with _registre_lock:
            if _registre_instance is None:
                _registre_instance = ServiceRegistry()
    return _registre_instance


def get_registry() -> ServiceRegistry:
    """Alias anglais pour obtenir_registre."""
    return obtenir_registre()


# Raccourci pour accès direct
registre = obtenir_registre()


# ═══════════════════════════════════════════════════════════
# DÉCORATEUR — Auto-enregistrement des factories
# ═══════════════════════════════════════════════════════════


def service_factory(
    nom: str,
    tags: set[str] | None = None,
) -> Callable:
    """Décorateur pour enregistrer une factory dans le registre.

    Transforme une fonction factory en singleton géré par le registre.
    La factory originale est enregistrée et sera appelée une seule fois
    lors du premier accès.

    **Comportement avec arguments (S8):**
    Si la factory décorée est appelée avec des arguments explicites,
    le singleton registre est bypassé et une nouvelle instance est créée.
    C'est un design voulu pour permettre la configuration custom
    (ex: client IA spécifique, config de test), mais attention : l'instance
    retournée n'est PAS celle du registre et ne sera pas réutilisée.

    Args:
        nom: Nom unique du service dans le registre
        tags: Tags de catégorisation (optionnel)

    Usage:
        @service_factory("mon_service", tags={"domaine", "ia"})
        def _creer_mon_service() -> MonService:
            return MonService()

        # Accès singleton (via registre)
        service = _creer_mon_service()

        # Bypass singleton (nouvelle instance dédiée)
        service_custom = _creer_mon_service(client=custom_client)

        # Ou via le registre directement
        service = registre.obtenir("mon_service")
    """

    def decorator(func: Callable) -> Callable:
        # Enregistrer la factory dans le registre global
        _registre = obtenir_registre()
        _registre.enregistrer(nom, func, tags=tags)

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if args or kwargs:
                # Appel avec arguments explicites — bypass singleton registre
                return func(*args, **kwargs)
            # Appel sans arguments — singleton via registre
            return _registre.obtenir(nom)

        return wrapper

    return decorator


__all__ = [
    "ServiceRegistry",
    "registre",
    "obtenir_registre",
    "get_registry",
    "service_factory",
]
