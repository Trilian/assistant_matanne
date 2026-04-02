"""
Bus d'événements domaine — Pub/Sub synchrone in-process.

Bus d'événements léger pour découpler les services entre eux.
Synchrone (pas besoin de message broker pour cette app).
Thread-safe via threading.Lock.

Fonctionnalités:
- Souscription par type d'événement (string)
- Wildcards: "recette.*" match "recette.planifiee", "recette.importee"
- Historique des N derniers événements
- Métriques par type d'événement
- Handlers prioritaires (order)
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class EvenementDomaine:
    """
    Événement domaine immutable.

    Attributes:
        type: Type de l'événement (ex: "recette.planifiee")
        data: Données associées (dict libre)
        source: Service émetteur
        timestamp: Horodatage
        event_id: ID unique auto-généré
    """

    type: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = ""

    def __post_init__(self):
        if not self.event_id:
            # Générer un ID unique basé sur le timestamp
            object.__setattr__(
                self,
                "event_id",
                f"{self.type}_{int(time.time() * 1000)}",
            )


@runtime_checkable
class HandlerEvenement(Protocol):
    """Protocol pour les handlers d'événements."""

    def __call__(self, event: EvenementDomaine) -> None: ...


@dataclass
class _Souscription:
    """Souscription interne avec priorité."""

    handler: HandlerEvenement
    priority: int = 0  # Plus élevé = exécuté en premier
    handler_name: str = ""

    def __post_init__(self):
        if not self.handler_name:
            self.handler_name = getattr(
                self.handler,
                "__qualname__",
                getattr(self.handler, "__name__", str(self.handler)),
            )


@dataclass
class _MetriquesEvenement:
    """Métriques pour un type d'événement."""

    emissions: int = 0
    handlers_executes: int = 0
    erreurs: int = 0
    duree_totale_ms: float = 0.0
    dernier_emission: datetime | None = None


# ═══════════════════════════════════════════════════════════
# BUS D'ÉVÉNEMENTS — Singleton thread-safe
# ═══════════════════════════════════════════════════════════


class BusEvenements:
    """
    Bus d'événements synchrone in-process.

    Thread-safe via Lock. Supporte les wildcards et les priorités.

    Usage:
        bus = BusEvenements()

        # Souscrire
        bus.souscrire("stock.modifie", lambda e: print(e.data))
        bus.souscrire("stock.*", global_handler)  # Wildcard

        # Émettre
        bus.emettre("stock.modifie", {"article_id": 1, "quantite": -2})

        # Métriques
        stats = bus.obtenir_metriques()
    """

    def __init__(self, historique_taille: int = 100):
        self._souscriptions: dict[str, list[_Souscription]] = defaultdict(list)
        self._lock = threading.Lock()
        self._historique: list[EvenementDomaine] = []
        self._historique_taille = historique_taille
        self._metriques: dict[str, _MetriquesEvenement] = defaultdict(_MetriquesEvenement)
        self._actif = True

    # ───────────────────────────────────────────────────────
    # SOUSCRIPTION
    # ───────────────────────────────────────────────────────

    def souscrire(
        self,
        type_evenement: str,
        handler: HandlerEvenement,
        priority: int = 0,
    ) -> None:
        """
        Souscrit à un type d'événement.

        Args:
            type_evenement: Type d'événement (ex: "recette.planifiee", "stock.*")
            handler: Callable(EvenementDomaine) → None
            priority: Priorité (plus élevé = exécuté en premier)
        """
        with self._lock:
            sub = _Souscription(handler=handler, priority=priority)
            self._souscriptions[type_evenement].append(sub)
            # Trier par priorité décroissante
            self._souscriptions[type_evenement].sort(key=lambda s: s.priority, reverse=True)
            logger.debug(
                f"📡 Souscription: {sub.handler_name} → {type_evenement} (priorité: {priority})"
            )

    def desouscrire(
        self,
        type_evenement: str,
        handler: HandlerEvenement,
    ) -> bool:
        """
        Retire une souscription.

        Returns:
            True si la souscription a été retirée
        """
        with self._lock:
            subs = self._souscriptions.get(type_evenement, [])
            for i, sub in enumerate(subs):
                if sub.handler is handler:
                    subs.pop(i)
                    logger.debug(f"📡 Désouscription: {sub.handler_name} ← {type_evenement}")
                    return True
        return False

    # Alias anglais
    subscribe = souscrire
    unsubscribe = desouscrire

    # ───────────────────────────────────────────────────────
    # ÉMISSION
    # ───────────────────────────────────────────────────────

    def emettre(
        self,
        type_evenement: str,
        data: dict[str, Any] | None = None,
        source: str = "",
    ) -> int:
        """
        Émet un événement vers tous les handlers souscris.

        Args:
            type_evenement: Type d'événement
            data: Données de l'événement
            source: Service émetteur

        Returns:
            Nombre de handlers notifiés
        """
        if not self._actif:
            return 0

        event = EvenementDomaine(
            type=type_evenement,
            data=data or {},
            source=source,
        )

        # Enregistrer dans l'historique
        with self._lock:
            self._historique.append(event)
            if len(self._historique) > self._historique_taille:
                self._historique = self._historique[-self._historique_taille :]

        # Persister l'événement en base (best-effort, non bloquant)
        self._persister_evenement(event)

        # Trouver les handlers correspondants
        handlers = self._trouver_handlers(type_evenement)

        if not handlers:
            logger.debug(f"📡 Événement {type_evenement} émis (0 handlers)")
            return 0

        # Exécuter les handlers
        start = time.perf_counter()
        nb_executes = 0
        nb_erreurs = 0

        for sub in handlers:
            try:
                sub.handler(event)
                nb_executes += 1
            except Exception as e:
                nb_erreurs += 1
                logger.error(
                    f"❌ Erreur handler {sub.handler_name} pour {type_evenement}: {e}",
                    exc_info=True,
                )

        duration_ms = (time.perf_counter() - start) * 1000

        # Mettre à jour les métriques
        with self._lock:
            m = self._metriques[type_evenement]
            m.emissions += 1
            m.handlers_executes += nb_executes
            m.erreurs += nb_erreurs
            m.duree_totale_ms += duration_ms
            m.dernier_emission = datetime.now()

        logger.debug(
            f"📡 {type_evenement}: {nb_executes} handlers, "
            f"{duration_ms:.1f}ms" + (f", {nb_erreurs} erreurs" if nb_erreurs else "")
        )

        return nb_executes

    # Alias anglais
    emit = emettre

    # ───────────────────────────────────────────────────────
    # WILDCARDS
    # ───────────────────────────────────────────────────────

    def _trouver_handlers(self, type_evenement: str) -> list[_Souscription]:
        """Trouve tous les handlers correspondants, y compris wildcards."""
        handlers: list[_Souscription] = []

        with self._lock:
            # Handlers exacts
            handlers.extend(self._souscriptions.get(type_evenement, []))

            # Handlers wildcards
            parts = type_evenement.split(".")
            for pattern, subs in self._souscriptions.items():
                if pattern == type_evenement:
                    continue  # Déjà ajouté
                if self._match_wildcard(pattern, parts):
                    handlers.extend(subs)

            # Handler global "*"
            handlers.extend(self._souscriptions.get("*", []))

        # Trier par priorité
        handlers.sort(key=lambda s: s.priority, reverse=True)
        return handlers

    @staticmethod
    def _match_wildcard(pattern: str, event_parts: list[str]) -> bool:
        """Vérifie si un pattern wildcard matche un type d'événement."""
        if not pattern.endswith(".*"):
            return False

        prefix = pattern[:-2]  # Retirer ".*"
        event_prefix = ".".join(event_parts[: prefix.count(".") + 1])
        return event_prefix == prefix

    # ───────────────────────────────────────────────────────
    # MÉTRIQUES & DEBUG
    # ───────────────────────────────────────────────────────

    def obtenir_metriques(self) -> dict[str, Any]:
        """Retourne les métriques globales du bus."""
        with self._lock:
            return {
                "actif": self._actif,
                "souscriptions": {k: len(v) for k, v in self._souscriptions.items()},
                "total_souscriptions": sum(len(v) for v in self._souscriptions.values()),
                "historique_taille": len(self._historique),
                "metriques_par_type": {
                    k: {
                        "emissions": v.emissions,
                        "handlers_executes": v.handlers_executes,
                        "erreurs": v.erreurs,
                        "duree_moyenne_ms": (
                            v.duree_totale_ms / v.emissions if v.emissions > 0 else 0
                        ),
                        "dernier_emission": (
                            v.dernier_emission.isoformat() if v.dernier_emission else None
                        ),
                    }
                    for k, v in self._metriques.items()
                },
            }

    def obtenir_historique(
        self,
        type_evenement: str | None = None,
        limite: int = 20,
    ) -> list[EvenementDomaine]:
        """Retourne les derniers événements."""
        with self._lock:
            events = self._historique
            if type_evenement:
                events = [e for e in events if e.type == type_evenement]
            return events[-limite:]

    def reinitialiser(self) -> None:
        """Réinitialise le bus (souscriptions, historique, métriques)."""
        with self._lock:
            self._souscriptions.clear()
            self._historique.clear()
            self._metriques.clear()
            logger.info("📡 Bus d'événements réinitialisé")

    def suspendre(self) -> None:
        """Suspend temporairement l'émission d'événements."""
        self._actif = False
        logger.info("📡 Bus d'événements suspendu")

    def reprendre(self) -> None:
        """Reprend l'émission d'événements."""
        self._actif = True
        logger.info("📡 Bus d'événements repris")

    # ───────────────────────────────────────────────────────
    # PERSISTENCE 
    # ───────────────────────────────────────────────────────

    def _persister_evenement(self, event: EvenementDomaine) -> None:
        """Persiste un événement en base de données (best-effort).

        Ne bloque pas l'émission si la DB est indisponible.
        Utilise la table etats_persistants avec namespace="event_bus".
        """
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.persistent_state import EtatPersistantDB

            with obtenir_contexte_db() as session:
                session.add(
                    EtatPersistantDB(
                        namespace="event_bus",
                        user_id=event.event_id,
                        data={
                            "type": event.type,
                            "data": event.data,
                            "source": event.source,
                            "timestamp": event.timestamp.isoformat(),
                            "event_id": event.event_id,
                        },
                    )
                )
                session.commit()
        except Exception as e:
            # Best-effort: ne pas bloquer le bus si la DB est down
            logger.debug(f"Persistance événement échouée (best-effort): {e}")

    def rejouer_historique_db(
        self,
        type_evenement: str | None = None,
        limite: int = 50,
    ) -> list[EvenementDomaine]:
        """Recharge les événements persistés depuis la base de données.

        Utilise la table etats_persistants (namespace="event_bus")
        pour récupérer l'historique post-redémarrage.
        Ne ré-émet PAS les événements (lecture seule).

        Returns:
            Liste des événements retrouvés
        """
        try:
            from src.core.db import obtenir_contexte_db
            from src.core.models.persistent_state import EtatPersistantDB

            with obtenir_contexte_db() as session:
                query = session.query(EtatPersistantDB).filter(
                    EtatPersistantDB.namespace == "event_bus",
                )
                rows = query.order_by(EtatPersistantDB.id.desc()).limit(limite).all()

                events = []
                for row in reversed(rows):
                    val = row.data or {}
                    evt_type = val.get("type", "")
                    if type_evenement and evt_type != type_evenement:
                        continue
                    events.append(
                        EvenementDomaine(
                            type=evt_type,
                            data=val.get("data", {}),
                            source=val.get("source", ""),
                            event_id=val.get("event_id", ""),
                        )
                    )
                logger.info(f"📡 {len(events)} événements rechargés depuis la DB")
                return events
        except Exception as e:
            logger.warning(f"Impossible de recharger l'historique événements: {e}")
            return []


# ═══════════════════════════════════════════════════════════
# SINGLETON — Thread-safe
# ═══════════════════════════════════════════════════════════

_bus_lock = threading.Lock()
_bus_instance: BusEvenements | None = None


def obtenir_bus() -> BusEvenements:
    """Obtient l'instance singleton du bus d'événements (thread-safe)."""
    global _bus_instance
    if _bus_instance is None:
        with _bus_lock:
            if _bus_instance is None:
                _bus_instance = BusEvenements()
                logger.info("📡 Bus d'événements initialisé")
    return _bus_instance


def get_event_bus() -> BusEvenements:
    """Alias anglais pour obtenir_bus."""
    return obtenir_bus()


__all__ = [
    "BusEvenements",
    "EvenementDomaine",
    "HandlerEvenement",
    "obtenir_bus",
    "get_event_bus",
]
