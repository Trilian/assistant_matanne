"""
Service inter-modules : Voyages → Budget.

IM-P2-8: Intégrer automatiquement les dépenses voyage dans le budget.
"""

import logging
from datetime import date as date_type
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class VoyagesBudgetInteractionService:
    """Service inter-modules Voyages → Budget."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_voyages_vers_budget(
        self,
        *,
        inclure_planifies: bool = True,
        db=None,
    ) -> dict[str, Any]:
        """Crée des lignes budget à partir des voyages et de leur budget prévu/réel.

        Args:
            inclure_planifies: inclut les voyages planifiés (budget_prevu)
            db: Session DB

        Returns:
            Dict de synthèse
        """
        from src.core.models import BudgetFamille
        from src.core.models.voyage import Voyage

        statuts = ["en_cours", "termine"]
        if inclure_planifies:
            statuts.append("planifie")
            statuts.append("planifié")

        voyages = db.query(Voyage).filter(Voyage.statut.in_(statuts)).all()

        depenses_creees = 0
        total_sync = 0.0
        details = []

        for voyage in voyages:
            montant = float(voyage.budget_reel or 0)
            if montant <= 0:
                montant = float(voyage.budget_prevu or 0)
            if montant <= 0:
                continue

            description = f"Voyage {voyage.titre} ({voyage.destination})"

            # Déduplication simple par description
            existe = db.query(BudgetFamille).filter(BudgetFamille.description == description).first()
            if existe:
                continue

            depense = BudgetFamille(
                date=voyage.date_depart or date_type.today(),
                montant=montant,
                categorie="loisirs",
                description=description,
                magasin="voyage",
                est_recurrent=False,
            )
            db.add(depense)
            depenses_creees += 1
            total_sync += montant
            details.append(
                {
                    "voyage_id": voyage.id,
                    "titre": voyage.titre,
                    "destination": voyage.destination,
                    "montant": montant,
                    "statut": voyage.statut,
                }
            )

        db.commit()

        if depenses_creees > 0:
            try:
                from src.services.core.events import obtenir_bus

                obtenir_bus().emettre(
                    "budget.modifie",
                    {
                        "action": "synchronisation_voyages",
                        "nb_depenses": depenses_creees,
                        "montant_total": round(total_sync, 2),
                    },
                    source="voyages_budget",
                )
            except Exception:
                logger.debug("Échec émission event budget voyages", exc_info=True)

        return {
            "ok": True,
            "depenses_creees": depenses_creees,
            "montant_total": round(total_sync, 2),
            "details": details,
            "message": f"{depenses_creees} dépense(s) voyage synchronisée(s)",
        }


@service_factory("voyages_budget_interaction", tags={"famille", "budget", "voyage"})
def obtenir_service_voyages_budget_interaction() -> VoyagesBudgetInteractionService:
    """Factory pour le service Voyages → Budget."""
    return VoyagesBudgetInteractionService()
