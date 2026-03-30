"""Service métier pour la comparaison des scénarios Habitat."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from src.core.models.habitat_projet import CritereScenarioHabitat


class ScenariosHabitatService:
    """Calcule et agrège les scores de scénarios Habitat."""

    @staticmethod
    def calculer_score_global(db: Session, scenario_id: int) -> Decimal:
        """Calcule le score global pondéré d'un scénario sur 100."""
        criteres = (
            db.query(CritereScenarioHabitat)
            .filter(CritereScenarioHabitat.scenario_id == scenario_id)
            .all()
        )
        if not criteres:
            return Decimal("0")

        somme_ponderee = Decimal("0")
        somme_poids = Decimal("0")
        for critere in criteres:
            poids = Decimal(critere.poids or 0)
            note = Decimal(critere.note or 0)
            somme_ponderee += note * poids
            somme_poids += poids

        if somme_poids <= 0:
            return Decimal("0")

        score_sur_10 = somme_ponderee / somme_poids
        return (score_sur_10 * Decimal("10")).quantize(Decimal("0.01"))
