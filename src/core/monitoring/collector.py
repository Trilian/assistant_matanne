"""
Collecteur de métriques centralisé — thread-safe, en mémoire.

Trois types de métriques:
  COMPTEUR     – valeur incrémentale (ex: nb d'appels IA)
  JAUGE        – valeur instantanée (ex: taille du cache)
  HISTOGRAMME  – distribution de valeurs (ex: latences en ms)

Le collecteur maintient un historique glissant configurable (par défaut
les 500 derniers points par métrique) et offre un *snapshot* structuré
pour l'affichage dans un tableau de bord.
"""

from __future__ import annotations

import statistics
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

# ───────────────────────────────────────────────────────────
# TYPES PUBLICS
# ───────────────────────────────────────────────────────────


class MetriqueType(Enum):
    """Types de métriques supportés."""

    COMPTEUR = auto()
    JAUGE = auto()
    HISTOGRAMME = auto()


@dataclass(slots=True, frozen=True)
class PointMetrique:
    """Un point de métrique individuel, immutable."""

    nom: str
    valeur: float
    type: MetriqueType
    timestamp: float
    labels: dict[str, str] = field(default_factory=dict)


# ───────────────────────────────────────────────────────────
# STOCKAGE INTERNE
# ───────────────────────────────────────────────────────────


@dataclass
class _SerieMetrique:
    """Série temporelle pour une métrique nommée."""

    type: MetriqueType
    points: deque[PointMetrique]
    total: float = 0.0  # somme cumulée (compteur) / dernière valeur (jauge)

    def ajouter(self, point: PointMetrique) -> None:
        self.points.append(point)
        if self.type == MetriqueType.COMPTEUR:
            self.total += point.valeur
        elif self.type == MetriqueType.JAUGE:
            self.total = point.valeur
        # Histogramme: total = somme des valeurs
        elif self.type == MetriqueType.HISTOGRAMME:
            self.total += point.valeur


# ───────────────────────────────────────────────────────────
# COLLECTEUR
# ───────────────────────────────────────────────────────────


class CollecteurMetriques:
    """Collecteur de métriques centralisé et thread-safe.

    Chaque métrique est identifiée par un *nom* hiérarchique
    (ex: ``ia.appel``, ``cache.hit.l1``, ``db.requete.duree_ms``).

    Parameters
    ----------
    taille_historique : int
        Nombre maximal de points conservés par métrique (FIFO).
    """

    def __init__(self, taille_historique: int = 500) -> None:
        self._lock = threading.RLock()
        self._series: dict[str, _SerieMetrique] = {}
        self._taille = taille_historique
        self._heure_creation = time.monotonic()
        self._labels_globaux: dict[str, str] = {}

    # ── Enregistrement ──────────────────────────────────────

    def enregistrer(
        self,
        nom: str,
        valeur: float,
        type_metrique: MetriqueType = MetriqueType.COMPTEUR,
        labels: dict[str, str] | None = None,
    ) -> PointMetrique:
        """Enregistre un point de métrique.

        Parameters
        ----------
        nom : str
            Nom hiérarchique (``ia.appel``, ``cache.hit.l1``).
        valeur : float
            Valeur du point.
        type_metrique : MetriqueType
            Type de la métrique.
        labels : dict, optional
            Labels additionnels (service, module, etc.).

        Returns
        -------
        PointMetrique
            Le point enregistré.
        """
        merged_labels = {**self._labels_globaux, **(labels or {})}
        point = PointMetrique(
            nom=nom,
            valeur=valeur,
            type=type_metrique,
            timestamp=time.time(),
            labels=merged_labels,
        )

        with self._lock:
            if nom not in self._series:
                self._series[nom] = _SerieMetrique(
                    type=type_metrique,
                    points=deque(maxlen=self._taille),
                )
            serie = self._series[nom]
            serie.ajouter(point)

        return point

    def incrementer(
        self, nom: str, increment: float = 1.0, labels: dict[str, str] | None = None
    ) -> None:
        """Raccourci pour incrémenter un compteur."""
        self.enregistrer(nom, increment, MetriqueType.COMPTEUR, labels)

    def jauge(self, nom: str, valeur: float, labels: dict[str, str] | None = None) -> None:
        """Raccourci pour définir une jauge."""
        self.enregistrer(nom, valeur, MetriqueType.JAUGE, labels)

    def histogramme(self, nom: str, valeur: float, labels: dict[str, str] | None = None) -> None:
        """Raccourci pour enregistrer une valeur d'histogramme."""
        self.enregistrer(nom, valeur, MetriqueType.HISTOGRAMME, labels)

    # ── Labels globaux ──────────────────────────────────────

    def definir_labels_globaux(self, labels: dict[str, str]) -> None:
        """Définit des labels appliqués à tous les futurs points."""
        with self._lock:
            self._labels_globaux.update(labels)

    # ── Snapshot ────────────────────────────────────────────

    def snapshot(self) -> dict[str, Any]:
        """Retourne un snapshot complet de toutes les métriques.

        Returns
        -------
        dict
            Structure::

                {
                    "timestamp": float,
                    "uptime_seconds": float,
                    "metriques": {
                        "nom.metrique": {
                            "type": "COMPTEUR",
                            "total": 42.0,
                            "nb_points": 42,
                            "dernier_point": {...},
                            "statistiques": {...},  # histogramme uniquement
                        }
                    }
                }
        """
        with self._lock:
            resultat: dict[str, Any] = {
                "timestamp": time.time(),
                "uptime_seconds": time.monotonic() - self._heure_creation,
                "metriques": {},
            }

            for nom, serie in self._series.items():
                info: dict[str, Any] = {
                    "type": serie.type.name,
                    "total": serie.total,
                    "nb_points": len(serie.points),
                }

                if serie.points:
                    dernier = serie.points[-1]
                    info["dernier_point"] = {
                        "valeur": dernier.valeur,
                        "timestamp": dernier.timestamp,
                        "labels": dernier.labels,
                    }

                    # Statistiques détaillées pour les histogrammes
                    if serie.type == MetriqueType.HISTOGRAMME and len(serie.points) >= 2:
                        valeurs = [p.valeur for p in serie.points]
                        info["statistiques"] = {
                            "min": min(valeurs),
                            "max": max(valeurs),
                            "moyenne": statistics.mean(valeurs),
                            "mediane": statistics.median(valeurs),
                            "ecart_type": statistics.stdev(valeurs),
                            "p95": _percentile(valeurs, 0.95),
                            "p99": _percentile(valeurs, 0.99),
                        }

                resultat["metriques"][nom] = info

            return resultat

    def obtenir_serie(self, nom: str) -> list[PointMetrique]:
        """Retourne la série complète pour une métrique."""
        with self._lock:
            serie = self._series.get(nom)
            if serie is None:
                return []
            return list(serie.points)

    def obtenir_total(self, nom: str) -> float:
        """Retourne le total/dernière valeur d'une métrique."""
        with self._lock:
            serie = self._series.get(nom)
            return serie.total if serie else 0.0

    def lister_metriques(self) -> list[str]:
        """Retourne la liste des noms de métriques enregistrées."""
        with self._lock:
            return list(self._series.keys())

    def reinitialiser(self) -> None:
        """Réinitialise toutes les métriques."""
        with self._lock:
            self._series.clear()
            self._heure_creation = time.monotonic()

    def filtrer_par_prefixe(self, prefixe: str) -> dict[str, Any]:
        """Retourne un snapshot filtré par préfixe de nom."""
        snap = self.snapshot()
        snap["metriques"] = {k: v for k, v in snap["metriques"].items() if k.startswith(prefixe)}
        return snap


# ───────────────────────────────────────────────────────────
# HELPERS
# ───────────────────────────────────────────────────────────


def _percentile(valeurs: list[float], p: float) -> float:
    """Calcule le percentile *p* (0-1) d'une liste triée."""
    sorted_vals = sorted(valeurs)
    k = (len(sorted_vals) - 1) * p
    f = int(k)
    c = f + 1
    if c >= len(sorted_vals):
        return sorted_vals[-1]
    return sorted_vals[f] + (k - f) * (sorted_vals[c] - sorted_vals[f])


# ───────────────────────────────────────────────────────────
# INSTANCE GLOBALE & FONCTIONS MODULE-LEVEL
# ───────────────────────────────────────────────────────────

collecteur = CollecteurMetriques()
"""Instance globale du collecteur de métriques."""


def enregistrer_metrique(
    nom: str,
    valeur: float,
    type_metrique: MetriqueType = MetriqueType.COMPTEUR,
    labels: dict[str, str] | None = None,
) -> PointMetrique:
    """Enregistre une métrique via l'instance globale."""
    return collecteur.enregistrer(nom, valeur, type_metrique, labels)


def obtenir_snapshot() -> dict[str, Any]:
    """Retourne un snapshot via l'instance globale."""
    return collecteur.snapshot()


def reinitialiser_collecteur() -> None:
    """Réinitialise le collecteur global."""
    collecteur.reinitialiser()
