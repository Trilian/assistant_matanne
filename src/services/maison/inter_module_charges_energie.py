"""
Service inter-modules : Charges facture -> Energie analyse.

Phase 5:
- P5-06/P5-17: facture +20% -> declencher analyse anomalie energie
"""

from __future__ import annotations

import logging
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ChargesEnergieInteractionService:
    """Bridge depenses maison -> analyse energie."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def detecter_hausse_et_declencher_analyse(
        self,
        *,
        seuil_hausse_pct: float = 20.0,
        db=None,
    ) -> dict[str, Any]:
        from src.core.models import DepenseMaison

        depenses = (
            db.query(DepenseMaison)
            .filter(DepenseMaison.categorie.in_(["electricite", "gaz", "eau"]))
            .order_by(DepenseMaison.annee.desc(), DepenseMaison.mois.desc())
            .all()
        )

        if len(depenses) < 2:
            return {"anomalie": False, "message": "Historique insuffisant pour analyse."}

        courante = depenses[0]
        precedente = next((d for d in depenses[1:] if d.categorie == courante.categorie), None)
        if not precedente:
            return {"anomalie": False, "message": "Aucune depense precedente comparable."}

        montant_prec = float(precedente.montant or 0)
        montant_courant = float(courante.montant or 0)
        if montant_prec <= 0:
            return {"anomalie": False, "message": "Base de comparaison invalide."}

        hausse_pct = ((montant_courant - montant_prec) / montant_prec) * 100
        anomalie = hausse_pct >= seuil_hausse_pct

        details = {
            "categorie": courante.categorie,
            "mois_courant": courante.mois,
            "annee_courante": courante.annee,
            "montant_courant": montant_courant,
            "montant_precedent": montant_prec,
            "hausse_pct": round(hausse_pct, 2),
            "anomalie": anomalie,
        }

        if anomalie:
            try:
                from src.services.core.events import obtenir_bus

                obtenir_bus().emettre(
                    "energie.anomalie_detectee",
                    {
                        "categorie": courante.categorie,
                        "hausse_pct": round(hausse_pct, 2),
                        "seuil_pct": seuil_hausse_pct,
                    },
                    source="charges_energie",
                )
            except Exception:
                logger.debug("Emission evenement energie.anomalie_detectee impossible", exc_info=True)

        details["message"] = (
            "Anomalie detectee: analyse energie declenchee." if anomalie else "Pas d'anomalie detectee."
        )
        return details


@service_factory("charges_energie_interaction", tags={"maison", "energie", "depenses"})
def obtenir_service_charges_energie_interaction() -> ChargesEnergieInteractionService:
    """Factory pour le bridge charges -> energie."""
    return ChargesEnergieInteractionService()
