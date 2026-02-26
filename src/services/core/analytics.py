"""
Service d'analytics — Métriques d'usage utilisateur transversal.

Suit le comportement utilisateur dans l'application:
- Pages visitées et temps passé
- Fonctionnalités les plus utilisées
- Parcours utilisateur (navigation)
- Statistiques d'adoption des modules

Architecture:
- Buffer mémoire haute performance (deque)
- Souscription automatique au bus d'événements
- Agrégation statistique intégrée
- Export pour dashboard (Plotly)

Usage:
    from src.services.core.analytics import obtenir_analytics

    analytics = obtenir_analytics()

    # Tracking manuel
    analytics.suivre_page("cuisine.recettes")
    analytics.suivre_action("recette.favori", {"recette_id": 42})

    # Consultation
    stats = analytics.obtenir_statistiques()
    top_pages = analytics.top_pages(limite=10)
    parcours = analytics.parcours_recent()
"""

from __future__ import annotations

import logging
import time
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class EvenementUsage(BaseModel):
    """Un événement d'usage applicatif."""

    timestamp: datetime = Field(default_factory=datetime.now)
    type: str = ""  # "page_vue", "action", "erreur", "session"
    cible: str = ""  # Page ou action (ex: "cuisine.recettes")
    duree_ms: float | None = None  # Temps passé (pour pages)
    details: dict[str, Any] = Field(default_factory=dict)
    session_id: str | None = None


class StatistiquesUsage(BaseModel):
    """Statistiques agrégées d'usage."""

    periode_debut: datetime | None = None
    periode_fin: datetime | None = None
    total_pages_vues: int = 0
    total_actions: int = 0
    pages_uniques: int = 0
    temps_moyen_page_ms: float = 0
    top_pages: list[dict[str, Any]] = Field(default_factory=list)
    top_actions: list[dict[str, Any]] = Field(default_factory=list)
    repartition_modules: dict[str, int] = Field(default_factory=dict)
    heures_actives: dict[int, int] = Field(default_factory=dict)


class MesureTemps:
    """Context manager pour mesurer le temps passé sur une page/action."""

    def __init__(self, service: ServiceAnalytics, cible: str):
        self._service = service
        self._cible = cible
        self._debut: float = 0

    def __enter__(self) -> MesureTemps:
        self._debut = time.monotonic()
        return self

    def __exit__(self, *args: Any) -> None:
        duree_ms = (time.monotonic() - self._debut) * 1000
        self._service.suivre_page(self._cible, duree_ms=duree_ms)


# ═══════════════════════════════════════════════════════════
# SERVICE
# ═══════════════════════════════════════════════════════════


TAILLE_BUFFER = 50_000  # Max événements en mémoire


class ServiceAnalytics:
    """Service d'analytics d'usage utilisateur.

    Collecte et agrège les métriques de comportement utilisateur
    pour comprendre l'adoption des modules et optimiser l'UX.
    """

    def __init__(self, taille_buffer: int = TAILLE_BUFFER):
        self._buffer: deque[EvenementUsage] = deque(maxlen=taille_buffer)
        self._souscrit: bool = False

        # Compteurs rapides (O(1) lookup)
        self._compteur_pages: Counter = Counter()
        self._compteur_actions: Counter = Counter()
        self._temps_pages: defaultdict[str, list[float]] = defaultdict(list)

        # Session tracking
        self._page_courante: str | None = None
        self._debut_page: float | None = None

    # ─── Souscription bus ───

    def souscrire_bus(self) -> None:
        """Souscrit au bus d'événements pour tracking automatique."""
        if self._souscrit:
            return

        try:
            from src.services.core.events import obtenir_bus

            bus = obtenir_bus()
            bus.souscrire("*", self._on_evenement)
            self._souscrit = True
            logger.info("ServiceAnalytics souscrit au bus d'événements")
        except Exception as e:
            logger.debug(f"Analytics: souscription bus échouée: {e}")

    def _on_evenement(self, type_evenement: str, data: dict, **kwargs: Any) -> None:
        """Handler pour les événements du bus."""
        # Ignorer les événements système
        if type_evenement.startswith("service.") or type_evenement.startswith("cache."):
            return

        self._enregistrer(
            type_evt="action",
            cible=type_evenement,
            details=data,
        )

    # ─── API publique : Tracking ───

    def suivre_page(
        self,
        page: str,
        duree_ms: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Enregistre une vue de page.

        Args:
            page: Identifiant de la page (ex: "cuisine.recettes")
            duree_ms: Temps passé sur la page en ms
            details: Métadonnées additionnelles
        """
        self._compteur_pages[page] += 1

        if duree_ms is not None:
            self._temps_pages[page].append(duree_ms)
            # Limiter la mémoire des temps
            if len(self._temps_pages[page]) > 1000:
                self._temps_pages[page] = self._temps_pages[page][-500:]

        self._enregistrer(
            type_evt="page_vue",
            cible=page,
            duree_ms=duree_ms,
            details=details or {},
        )

    def suivre_action(
        self,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Enregistre une action utilisateur.

        Args:
            action: Type d'action (ex: "recette.favori", "courses.valider")
            details: Métadonnées additionnelles
        """
        self._compteur_actions[action] += 1
        self._enregistrer(
            type_evt="action",
            cible=action,
            details=details or {},
        )

    def mesurer_temps(self, cible: str) -> MesureTemps:
        """Retourne un context manager pour mesurer le temps passé.

        Usage:
            with analytics.mesurer_temps("cuisine.recettes"):
                afficher_recettes()

        Args:
            cible: Identifiant de la page/action

        Returns:
            MesureTemps context manager
        """
        return MesureTemps(self, cible)

    # ─── API publique : Consultation ───

    def top_pages(self, limite: int = 10) -> list[dict[str, Any]]:
        """Retourne les pages les plus visitées.

        Args:
            limite: Nombre max de résultats

        Returns:
            Liste de dicts {page, vues, temps_moyen_ms}
        """
        resultats = []
        for page, count in self._compteur_pages.most_common(limite):
            temps = self._temps_pages.get(page, [])
            temps_moyen = sum(temps) / len(temps) if temps else 0

            resultats.append(
                {
                    "page": page,
                    "vues": count,
                    "temps_moyen_ms": round(temps_moyen, 1),
                }
            )

        return resultats

    def top_actions(self, limite: int = 10) -> list[dict[str, Any]]:
        """Retourne les actions les plus effectuées.

        Args:
            limite: Nombre max de résultats

        Returns:
            Liste de dicts {action, count}
        """
        return [
            {"action": action, "count": count}
            for action, count in self._compteur_actions.most_common(limite)
        ]

    def repartition_modules(self) -> dict[str, int]:
        """Retourne la répartition d'usage par module.

        Agrège les pages par préfixe de module (ex: "cuisine", "famille").

        Returns:
            Dict {module: nombre_vues}
        """
        modules: Counter = Counter()
        for page, count in self._compteur_pages.items():
            # Extraire le module (premier segment: "cuisine.recettes" → "cuisine")
            module = page.split(".")[0] if "." in page else page
            modules[module] += count

        return dict(modules.most_common())

    def heures_actives(self) -> dict[int, int]:
        """Retourne la distribution d'activité par heure de la journée.

        Returns:
            Dict {heure (0-23): nombre_événements}
        """
        heures: Counter = Counter()
        for evt in self._buffer:
            heures[evt.timestamp.hour] += 1
        return dict(sorted(heures.items()))

    def parcours_recent(self, limite: int = 20) -> list[dict[str, Any]]:
        """Retourne les derniers événements (parcours utilisateur).

        Args:
            limite: Nombre max d'événements

        Returns:
            Liste d'événements récents
        """
        recents = list(self._buffer)[-limite:]
        return [
            {
                "timestamp": evt.timestamp.isoformat(),
                "type": evt.type,
                "cible": evt.cible,
                "duree_ms": evt.duree_ms,
            }
            for evt in reversed(recents)
        ]

    def obtenir_statistiques(
        self,
        depuis: datetime | None = None,
        jusqu_a: datetime | None = None,
    ) -> StatistiquesUsage:
        """Retourne les statistiques agrégées d'usage.

        Args:
            depuis: Date de début (défaut: début du buffer)
            jusqu_a: Date de fin (défaut: maintenant)

        Returns:
            StatistiquesUsage complètes
        """
        evenements = list(self._buffer)

        # Filtrer par période
        if depuis:
            evenements = [e for e in evenements if e.timestamp >= depuis]
        if jusqu_a:
            evenements = [e for e in evenements if e.timestamp <= jusqu_a]

        pages_vues = [e for e in evenements if e.type == "page_vue"]
        actions = [e for e in evenements if e.type == "action"]

        # Temps moyen sur les pages
        temps = [e.duree_ms for e in pages_vues if e.duree_ms is not None]
        temps_moyen = sum(temps) / len(temps) if temps else 0

        return StatistiquesUsage(
            periode_debut=evenements[0].timestamp if evenements else None,
            periode_fin=evenements[-1].timestamp if evenements else None,
            total_pages_vues=len(pages_vues),
            total_actions=len(actions),
            pages_uniques=len({e.cible for e in pages_vues}),
            temps_moyen_page_ms=round(temps_moyen, 1),
            top_pages=self.top_pages(10),
            top_actions=self.top_actions(10),
            repartition_modules=self.repartition_modules(),
            heures_actives=self.heures_actives(),
        )

    def vider(self) -> int:
        """Vide le buffer d'analytics.

        Returns:
            Nombre d'événements supprimés
        """
        n = len(self._buffer)
        self._buffer.clear()
        self._compteur_pages.clear()
        self._compteur_actions.clear()
        self._temps_pages.clear()
        logger.info(f"Analytics buffer vidé ({n} événements)")
        return n

    # ─── Interne ───

    def _enregistrer(
        self,
        type_evt: str,
        cible: str,
        duree_ms: float | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Enregistre un événement dans le buffer."""
        evt = EvenementUsage(
            timestamp=datetime.now(),
            type=type_evt,
            cible=cible,
            duree_ms=duree_ms,
            details=details or {},
        )
        self._buffer.append(evt)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("analytics", tags={"core", "analytics", "transversal"})
def obtenir_analytics() -> ServiceAnalytics:
    """Factory singleton pour le service d'analytics d'usage."""
    service = ServiceAnalytics()
    service.souscrire_bus()
    return service


__all__ = [
    "ServiceAnalytics",
    "EvenementUsage",
    "StatistiquesUsage",
    "MesureTemps",
    "obtenir_analytics",
]
