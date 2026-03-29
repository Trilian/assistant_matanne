"""
Service pour les interactions inter-modules Planning × Voyages.

IM4: Pause automatique planning lors voyage
"""

import logging

from src.core.decorators import avec_session_db
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class PlanningVoyageInteractionService(EventBusMixin):
    """Service pour les interactions Planning × Voyages."""

    _event_source = "planning"

    @avec_session_db
    def suspendre_planning_voyage(
        self,
        voyage_id: int,
        date_debut: str,
        date_fin: str,
        db=None,
    ) -> dict:
        """Suspend la génération auto du planning pendant un voyage (IM4).

        Écoute l'événement voyage.en_cours et suspend le planning automatique.

        Args:
            voyage_id: ID du voyage
            date_debut: Date de début du voyage (ISO format)
            date_fin: Date de fin du voyage (ISO format)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec message et nombre de plannings suspendus
        """
        from datetime import datetime
        from src.core.models import Planning

        try:
            # Convertir les dates
            debut = datetime.fromisoformat(date_debut).date()
            fin = datetime.fromisoformat(date_fin).date()

            # Trouver les plannings actifs pendant cette période
            plannings_suspendre = (
                db.query(Planning)
                .filter(
                    Planning.semaine_debut >= debut,
                    Planning.semaine_debut <= fin,
                    Planning.statut == "actif",
                )
                .all()
            )

            # Suspendre chaque planning
            for planning in plannings_suspendre:
                planning.statut = "suspendu"
                planning.notes = (
                    f"Suspendu automatiquement - Voyage {voyage_id} "
                    f"({debut} au {fin})"
                )
                logger.info(f"📅 Planning {planning.id} suspendu pour voyage")

            db.commit()

            # Émettre événement
            nb_suspendus = len(plannings_suspendre)
            self.emettre_evenement(
                "planning.suspendu_voyage",
                {
                    "voyage_id": voyage_id,
                    "date_debut": date_debut,
                    "date_fin": date_fin,
                    "nb_plannings": nb_suspendus,
                    "message": f"Planning mis en pause — {nb_suspendus} semaine(s) suspendue(s)",
                },
            )

            return {
                "message": f"Planning en pause pour voyage {voyage_id}",
                "nb_plannings_suspendus": nb_suspendus,
                "date_debut": date_debut,
                "date_fin": date_fin,
            }

        except Exception as e:
            logger.error(f"Erreur suspension planning voyage: {e}")
            db.rollback()
            return {"error": str(e)}

    @avec_session_db
    def reprendre_planning_apres_voyage(
        self,
        voyage_id: int,
        db=None,
    ) -> dict:
        """Reprend la génération du planning après le voyage.

        Args:
            voyage_id: ID du voyage
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec message et nombre de plannings repris
        """
        from src.core.models import Planning

        try:
            # Trouver les plannings suspendus pour ce voyage
            plannings_reprendre = (
                db.query(Planning)
                .filter(
                    Planning.statut == "suspendu",
                    Planning.notes.like(f"%Voyage {voyage_id}%"),
                )
                .all()
            )

            # Reprendre chaque planning
            for planning in plannings_reprendre:
                planning.statut = "actif"
                planning.notes = f"Repris après voyage {voyage_id}"
                logger.info(f"📅 Planning {planning.id} repris après voyage")

            db.commit()

            nb_repris = len(plannings_reprendre)
            self.emettre_evenement(
                "planning.repris_apres_voyage",
                {
                    "voyage_id": voyage_id,
                    "nb_plannings": nb_repris,
                },
            )

            return {
                "message": f"Planning repris après voyage {voyage_id}",
                "nb_plannings_repris": nb_repris,
            }

        except Exception as e:
            logger.error(f"Erreur reprise planning: {e}")
            db.rollback()
            return {"error": str(e)}

    def emettre_evenement(self, event_type: str, data: dict) -> None:
        """Émet un événement via le bus.

        Args:
            event_type: Type d'événement
            data: Données de l'événement
        """
        try:
            from src.services.core.event_bus import obtenir_bus

            obtenir_bus().emettre(event_type, data, source=self._event_source)
        except Exception as e:
            logger.error(f"Erreur émission événement {event_type}: {e}")


@service_factory("planning_voyage_interaction", tags={"planning", "voyages"})
def obtenir_service_planning_voyage_interaction() -> PlanningVoyageInteractionService:
    """Factory pour le service Planning × Voyages."""
    return PlanningVoyageInteractionService()
