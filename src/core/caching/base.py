"""
Base - Types de base pour le cache multi-niveaux.

Définit:
- EntreeCache: Structure d'une entrée de cache avec métadonnées
- StatistiquesCache: Statistiques globales du cache
"""

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EntreeCache:
    """Entrée de cache avec métadonnées."""

    value: Any
    created_at: float = field(default_factory=time.time)
    ttl: int = 300
    tags: list[str] = field(default_factory=list)
    hits: int = 0

    @property
    def est_expire(self) -> bool:
        """Vérifie si l'entrée est expirée."""
        return time.time() - self.created_at > self.ttl

    @property
    def age_seconds(self) -> float:
        """Âge de l'entrée en secondes."""
        return time.time() - self.created_at


@dataclass
class StatistiquesCache:
    """Statistiques du cache."""

    l1_hits: int = 0
    l2_hits: int = 0
    l3_hits: int = 0
    misses: int = 0
    writes: int = 0
    evictions: int = 0

    @property
    def total_hits(self) -> int:
        return self.l1_hits + self.l2_hits + self.l3_hits

    @property
    def hit_rate(self) -> float:
        total = self.total_hits + self.misses
        return (self.total_hits / total * 100) if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "l1_hits": self.l1_hits,
            "l2_hits": self.l2_hits,
            "l3_hits": self.l3_hits,
            "total_hits": self.total_hits,
            "misses": self.misses,
            "writes": self.writes,
            "evictions": self.evictions,
            "hit_rate": f"{self.hit_rate:.1f}%",
        }
