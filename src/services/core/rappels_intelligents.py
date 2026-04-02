"""
Service de rappels intelligents contextuels.

Analyse les données de l'application et génère des alertes pertinentes:
- Stock d'inventaire sous le seuil minimum
- Tâches d'entretien en retard
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from src.core.db import obtenir_contexte_db
from src.core.models.inventaire import ArticleInventaire
from src.core.models.habitat import TacheEntretien
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class RappelItem:
    """Représente un rappel contextuel."""

    def __init__(
        self,
        type_rappel: str,
        titre: str,
        description: str,
        priorite: str = "normale",
        date_echeance: date | None = None,
        lien: str | None = None,
    ) -> None:
        self.type_rappel = type_rappel
        self.titre = titre
        self.description = description
        self.priorite = priorite
        self.date_echeance = date_echeance
        self.lien = lien

    def to_dict(self) -> dict:
        return {
            "type": self.type_rappel,
            "titre": self.titre,
            "description": self.description,
            "priorite": self.priorite,
            "date_echeance": self.date_echeance.isoformat() if self.date_echeance else None,
            "lien": self.lien,
        }


class RappelsIntelligentsService:
    """Service d'évaluation et de génération des rappels contextuels."""

    def evaluer_rappels(self) -> list[dict]:
        """
        Évalue l'ensemble des sources de rappels et retourne la liste consolidée.

        Retourne une liste de dicts sérialisables (pour l'API).
        """
        rappels: list[RappelItem] = []

        rappels.extend(self._rappels_inventaire())
        rappels.extend(self._rappels_entretien())

        # Tri: urgents en premier, puis par date d'échéance
        priorite_ordre = {"urgente": 0, "haute": 1, "normale": 2, "basse": 3}
        rappels.sort(
            key=lambda r: (
                priorite_ordre.get(r.priorite, 2),
                r.date_echeance or date.max,
            )
        )

        logger.info(f"✅ {len(rappels)} rappel(s) généré(s)")
        return [r.to_dict() for r in rappels]

    def _rappels_inventaire(self) -> list[RappelItem]:
        """Articles d'inventaire sous le seuil minimum."""
        rappels = []

        try:
            with obtenir_contexte_db() as session:
                articles = (
                    session.query(ArticleInventaire)
                    .filter(ArticleInventaire.quantite < ArticleInventaire.quantite_min)
                    .all()
                )

                for a in articles:
                    nom = a.nom or f"Article #{a.ingredient_id}"
                    critique = a.quantite < (a.quantite_min * 0.5)
                    priorite = "urgente" if critique else "haute"
                    rappels.append(
                        RappelItem(
                            type_rappel="inventaire",
                            titre=f"Stock bas : {nom}",
                            description=(
                                f"Stock actuel : {a.quantite} "
                                f"(seuil minimum : {a.quantite_min}). "
                                "Pensez à réapprovisionner."
                            ),
                            priorite=priorite,
                            lien="/cuisine/inventaire",
                        )
                    )
        except Exception:
            logger.warning("Impossible de vérifier l'inventaire", exc_info=True)

        return rappels

    def _rappels_entretien(self) -> list[RappelItem]:
        """Tâches d'entretien en retard (prochaine_fois dépassée et non faites)."""
        rappels = []
        aujourd_hui = date.today()

        try:
            with obtenir_contexte_db() as session:
                taches = (
                    session.query(TacheEntretien)
                    .filter(
                        TacheEntretien.fait.is_(False),
                        TacheEntretien.prochaine_fois < aujourd_hui,
                        TacheEntretien.prochaine_fois.isnot(None),
                    )
                    .all()
                )

                for t in taches:
                    jours_retard = (aujourd_hui - t.prochaine_fois).days
                    priorite = (
                        "urgente" if jours_retard >= 14
                        else "haute" if jours_retard >= 7
                        else "normale"
                    )
                    rappels.append(
                        RappelItem(
                            type_rappel="entretien",
                            titre=f"Entretien en retard : {t.nom}",
                            description=f"Prévu le {t.prochaine_fois.isoformat()}, retard de {jours_retard} jour(s).",
                            priorite=priorite,
                            date_echeance=t.prochaine_fois,
                            lien="/maison/entretien",
                        )
                    )
        except Exception:
            logger.warning("Impossible de vérifier les tâches d'entretien", exc_info=True)

        return rappels


@service_factory("rappels_intelligents")
def obtenir_rappels_intelligents_service() -> RappelsIntelligentsService:
    return RappelsIntelligentsService()


# ─── Aliases rétrocompatibilité  ───────────────────────────────
get_rappels_intelligents_service = obtenir_rappels_intelligents_service  # alias rétrocompatibilité 
