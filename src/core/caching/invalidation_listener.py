"""Listener PostgreSQL pour invalidation cache automatique.

Écoute le canal NOTIFY `planning_changed` et invalide les clés de cache
susceptibles d'être stales après une modification directe en base.
"""

from __future__ import annotations

import logging
import select
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from src.core.caching import obtenir_cache
from src.core.db import obtenir_moteur

logger = logging.getLogger(__name__)

_CANAL_INVALIDATION = "planning_changed"
_PATTERNS_INVALIDATION = (
    "planning_",
    "planning_full_",
    "semaine_complete_",
    "semaine_ia_",
    "batch_",
)


@dataclass
class _EtatListenerInvalidation:
    thread: threading.Thread | None = None
    stop_event: threading.Event = field(default_factory=threading.Event)


_etat = _EtatListenerInvalidation()
_lock_listener = threading.Lock()


def extraire_payload_notification(notification: object) -> str:
    """Extrait le payload depuis psycopg2/psycopg de façon robuste."""
    payload = getattr(notification, "payload", notification)
    return str(payload or "")


def traiter_notification_cache(payload: str) -> None:
    """Invalide les caches applicatifs impactés par un changement planning."""
    cache = obtenir_cache()

    total_invalide = 0
    for pattern in _PATTERNS_INVALIDATION:
        total_invalide += cache.invalidate(pattern=pattern)

    # Le cache fichier L3 ne matche pas toujours les patterns legacy.
    # On le purge explicitement pour éviter des lectures stales persistantes.
    cache.clear(levels="l3")

    logger.info(
        "🔄 Invalidation cache DB (%s, payload=%s): %s entrées invalidées + L3 purgé",
        _CANAL_INVALIDATION,
        payload or "<vide>",
        total_invalide,
    )


def _boucle_listener(timeout_s: float, delai_reconnexion_s: float) -> None:
    """Boucle de consommation LISTEN/NOTIFY avec reconnexion automatique."""
    while not _etat.stop_event.is_set():
        dbapi_conn = None
        raw_conn = None

        try:
            moteur = obtenir_moteur()
            if moteur.dialect.name != "postgresql":
                logger.info("Listener invalidation cache désactivé: DB non PostgreSQL")
                return

            raw_conn = moteur.raw_connection()
            dbapi_conn = raw_conn.connection if hasattr(raw_conn, "connection") else raw_conn

            try:
                dbapi_conn.set_isolation_level(0)
            except Exception:
                try:
                    setattr(dbapi_conn, "autocommit", True)
                except Exception:
                    logger.debug("Autocommit non modifiable pour LISTEN", exc_info=True)

            cursor = dbapi_conn.cursor()
            try:
                cursor.execute(f"LISTEN {_CANAL_INVALIDATION};")
            finally:
                try:
                    cursor.close()
                except Exception:
                    logger.debug("Fermeture cursor LISTEN échouée", exc_info=True)

            logger.info("✅ Listener cache actif sur canal PostgreSQL '%s'", _CANAL_INVALIDATION)

            while not _etat.stop_event.is_set():
                pret, _, _ = select.select([dbapi_conn], [], [], timeout_s)
                if not pret:
                    continue

                if hasattr(dbapi_conn, "poll"):
                    dbapi_conn.poll()

                notifies = getattr(dbapi_conn, "notifies", None)
                if not isinstance(notifies, list):
                    continue

                while notifies:
                    notification: Any = notifies.pop(0)
                    traiter_notification_cache(extraire_payload_notification(notification))

        except Exception as exc:
            if _etat.stop_event.is_set():
                break
            logger.warning(
                "Listener cache indisponible (%s), reconnexion dans %.1fs",
                exc,
                delai_reconnexion_s,
            )
            time.sleep(delai_reconnexion_s)
        finally:
            try:
                if raw_conn is not None:
                    raw_conn.close()
            except Exception:
                logger.debug("Fermeture raw_connection échouée", exc_info=True)


def demarrer_listener_invalidation_cache(
    timeout_s: float = 1.0,
    delai_reconnexion_s: float = 2.0,
) -> None:
    """Démarre le listener d'invalidation cache si non actif."""
    with _lock_listener:
        if _etat.thread and _etat.thread.is_alive():
            return

        _etat.stop_event.clear()
        _etat.thread = threading.Thread(
            target=_boucle_listener,
            args=(timeout_s, delai_reconnexion_s),
            name="cache-invalidation-listener",
            daemon=True,
        )
        _etat.thread.start()


def arreter_listener_invalidation_cache(join_timeout_s: float = 2.0) -> None:
    """Arrête proprement le listener d'invalidation cache."""
    with _lock_listener:
        _etat.stop_event.set()

        if _etat.thread and _etat.thread.is_alive():
            _etat.thread.join(timeout=join_timeout_s)

        _etat.thread = None
