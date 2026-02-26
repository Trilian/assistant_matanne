"""
Score de popularité des recettes — Analytics cuisine.

Calcule un score composite basé sur fréquence de préparation,
notes, ajouts aux favoris, et tendance récente.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class ScorePopularite:
    """Score de popularité d'une recette."""

    recette_id: int
    nom_recette: str
    score_total: float = 0.0  # 0-100

    # Sous-scores
    frequence_preparation: float = 0.0  # Nb fois préparée
    note_moyenne: float = 0.0  # Note utilisateur (0-5)
    tendance: str = "stable"  # hausse, baisse, stable, nouveau
    derniere_preparation: date | None = None
    nb_preparations: int = 0
    nb_preparations_30j: int = 0


@dataclass
class ClassementRecettes:
    """Classement des recettes par popularité."""

    recettes: list[ScorePopularite]
    top_3: list[ScorePopularite] = field(default_factory=list)
    flop_3: list[ScorePopularite] = field(default_factory=list)
    nouvelles: list[ScorePopularite] = field(default_factory=list)
    periode_analyse: int = 90  # jours


# ═══════════════════════════════════════════════════════════
# FONCTIONS
# ═══════════════════════════════════════════════════════════


@avec_session_db
def calculer_popularite(
    periode_jours: int = 90,
    *,
    db: Session,
) -> ClassementRecettes:
    """
    Calcule le score de popularité de toutes les recettes.

    Méthode:
    - 40% fréquence de préparation (normalisée)
    - 30% tendance récente (30 derniers jours)
    - 20% note utilisateur
    - 10% récence (dernier usage)

    Returns:
        ClassementRecettes complet
    """
    from src.core.models.planning import PlanningRepas
    from src.core.models.recettes import Recette

    date_debut = date.today() - timedelta(days=periode_jours)
    date_30j = date.today() - timedelta(days=30)

    # Récupérer toutes les recettes
    recettes = db.query(Recette).all()
    if not recettes:
        return ClassementRecettes(recettes=[])

    scores = []

    for recette in recettes:
        # Nombre total de préparations (via planning)
        nb_total = (
            db.query(func.count(PlanningRepas.id))
            .filter(
                PlanningRepas.recette_id == recette.id,
                PlanningRepas.date >= date_debut,
            )
            .scalar()
            or 0
        )

        # Préparations 30 derniers jours
        nb_30j = (
            db.query(func.count(PlanningRepas.id))
            .filter(
                PlanningRepas.recette_id == recette.id,
                PlanningRepas.date >= date_30j,
            )
            .scalar()
            or 0
        )

        # Dernière préparation
        derniere = (
            db.query(func.max(PlanningRepas.date))
            .filter(PlanningRepas.recette_id == recette.id)
            .scalar()
        )

        # Note (si disponible dans le modèle)
        note = getattr(recette, "note", None) or 0

        scores.append(
            ScorePopularite(
                recette_id=recette.id,
                nom_recette=recette.nom,
                nb_preparations=nb_total,
                nb_preparations_30j=nb_30j,
                note_moyenne=float(note),
                derniere_preparation=derniere,
            )
        )

    # Normaliser et calculer les scores composites
    max_preps = max(s.nb_preparations for s in scores) if scores else 1
    max_30j = max(s.nb_preparations_30j for s in scores) if scores else 1

    for s in scores:
        # Fréquence normalisée (40%)
        freq_norm = s.nb_preparations / max(max_preps, 1) * 40

        # Tendance 30j (30%)
        trend_norm = s.nb_preparations_30j / max(max_30j, 1) * 30

        # Note (20%)
        note_norm = s.note_moyenne / 5 * 20

        # Récence (10%)
        if s.derniere_preparation:
            jours_depuis = (date.today() - s.derniere_preparation).days
            recence = max(0, (1 - jours_depuis / max(periode_jours, 1))) * 10
        else:
            recence = 0

        s.score_total = round(freq_norm + trend_norm + note_norm + recence, 1)
        s.frequence_preparation = round(freq_norm, 1)

        # Tendance
        if s.nb_preparations == 0:
            s.tendance = "nouveau"
        elif s.nb_preparations_30j > s.nb_preparations / max(periode_jours / 30, 1) * 1.3:
            s.tendance = "hausse"
        elif s.nb_preparations_30j < s.nb_preparations / max(periode_jours / 30, 1) * 0.7:
            s.tendance = "baisse"
        else:
            s.tendance = "stable"

    # Trier par score
    scores.sort(key=lambda s: s.score_total, reverse=True)

    return ClassementRecettes(
        recettes=scores,
        top_3=scores[:3],
        flop_3=sorted(scores[-3:], key=lambda s: s.score_total) if len(scores) >= 3 else [],
        nouvelles=[s for s in scores if s.tendance == "nouveau"][:5],
        periode_analyse=periode_jours,
    )


def generer_resume_popularite(classement: ClassementRecettes) -> str:
    """Génère un résumé textuel du classement."""
    lignes = ["🏆 Top recettes du moment\n"]

    for i, s in enumerate(classement.top_3, 1):
        emoji = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"#{i}"
        tendance_emoji = {"hausse": "📈", "baisse": "📉", "stable": "➡️", "nouveau": "🆕"}.get(
            s.tendance, ""
        )
        lignes.append(f"{emoji} {s.nom_recette} — Score: {s.score_total}/100 {tendance_emoji}")
        lignes.append(f"   Préparé {s.nb_preparations}× (dont {s.nb_preparations_30j} ce mois)")

    if classement.nouvelles:
        lignes.append("\n🆕 Pas encore testées:")
        for s in classement.nouvelles[:3]:
            lignes.append(f"  • {s.nom_recette}")

    return "\n".join(lignes)


__all__ = [
    "ScorePopularite",
    "ClassementRecettes",
    "calculer_popularite",
    "generer_resume_popularite",
]
