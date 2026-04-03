"""
Service inter-modules : Documents expirants -> Calendrier.

Bridge inter-modules :
- P5-08: creer un evenement calendrier de renouvellement document
"""

from __future__ import annotations

import logging
from datetime import datetime, time, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class DocumentsCalendrierInteractionService:
    """Bridge documents -> calendrier planning."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def synchroniser_documents_vers_calendrier(
        self,
        *,
        jours_horizon: int = 60,
        rappel_jours_avant: int = 14,
        db=None,
    ) -> dict[str, Any]:
        from src.core.models import DocumentFamille, EvenementPlanning

        aujourd_hui = datetime.now().date()
        limite = aujourd_hui + timedelta(days=jours_horizon)

        documents = (
            db.query(DocumentFamille)
            .filter(
                DocumentFamille.date_expiration.isnot(None),
                DocumentFamille.date_expiration <= limite,
                DocumentFamille.actif.is_(True),
            )
            .all()
        )

        crees = 0
        for doc in documents:
            if not doc.date_expiration:
                continue
            date_evt = doc.date_expiration - timedelta(days=rappel_jours_avant)
            titre = f"Renouveler document: {doc.titre}"

            existe = (
                db.query(EvenementPlanning)
                .filter(EvenementPlanning.titre == titre, EvenementPlanning.type_event == "administratif")
                .first()
            )
            if existe:
                continue

            evenement = EvenementPlanning(
                titre=titre,
                description=f"Document {doc.categorie} ({doc.membre_famille}) expire le {doc.date_expiration.isoformat()}.",
                date_debut=datetime.combine(date_evt, time(hour=9, minute=0)),
                date_fin=datetime.combine(date_evt, time(hour=9, minute=30)),
                type_event="administratif",
                rappel_avant_minutes=24 * 60,
                couleur="#ef4444",
                lieu="Maison",
            )
            db.add(evenement)
            crees += 1

        if crees:
            db.commit()

        return {
            "evenements_crees": crees,
            "documents_traites": len(documents),
            "message": f"{crees} evenement(s) calendrier cree(s).",
        }


@service_factory("documents_calendrier_interaction", tags={"famille", "documents", "calendrier"})
def obtenir_service_documents_calendrier_interaction() -> DocumentsCalendrierInteractionService:
    """Factory pour le bridge documents -> calendrier."""
    return DocumentsCalendrierInteractionService()
