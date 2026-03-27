"""Briques communes de scoring pour services metier."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScoreContexte:
    """Resultat standard de scoring contextuel."""

    score: float = 0.5
    raison: str = "Suggestion generale"
    sources: list[str] = field(default_factory=list)


class BaseScoringService:
    """Base minimale pour mutualiser la forme des resultats de scoring."""

    @staticmethod
    def construire_score(score: float, sources: list[str]) -> ScoreContexte:
        score_borne = min(max(score, 0.0), 1.0)
        raison = ", ".join(sources) if sources else "Suggestion generale"
        return ScoreContexte(score=round(score_borne, 2), raison=raison, sources=sources)
