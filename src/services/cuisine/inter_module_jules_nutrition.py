"""
Service inter-modules : Jules croissance -> Planning nutrition.

Phase 5:
- P5-02: adapter portions/nutriments selon croissance de Jules
- P5-14: adapter automatiquement les portions des recettes planifiees
"""

from __future__ import annotations

import logging
from datetime import date as date_type, timedelta
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class JulesNutritionInteractionService:
    """Bridge Jules croissance -> planning nutrition/portions."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def adapter_planning_nutrition_selon_croissance(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """P5-02: produit des recommandations nutritionnelles a partir de la derniere mesure."""
        from src.core.models import MesureCroissance, ProfilEnfant

        jules = db.query(ProfilEnfant).filter(ProfilEnfant.name == "Jules", ProfilEnfant.actif.is_(True)).first()
        if not jules:
            return {"recommandations": [], "message": "Profil Jules introuvable."}

        mesure = (
            db.query(MesureCroissance)
            .filter(MesureCroissance.enfant_id == jules.id)
            .order_by(MesureCroissance.date_mesure.desc())
            .first()
        )
        if not mesure:
            return {"recommandations": [], "message": "Aucune mesure de croissance disponible."}

        recommandations = []
        age_mois = mesure.age_mois or 0
        if age_mois < 24:
            recommandations.append("Maintenir des textures adaptees et une densite energetique elevee.")
        if mesure.poids_kg and mesure.poids_kg < 10:
            recommandations.append("Verifier un apport proteine/energie suffisant sur les 7 prochains jours.")
        if mesure.imc_calcule and mesure.imc_calcule > 18:
            recommandations.append("Favoriser legumes/fibres et limiter les desserts sucres repetitifs.")

        recommandations.append(f"Horizon de planification nutritionnelle: {jours_horizon} jours.")

        return {
            "enfant_id": jules.id,
            "age_mois": age_mois,
            "derniere_mesure": mesure.date_mesure.isoformat() if mesure.date_mesure else None,
            "recommandations": recommandations,
            "message": "Recommandations nutritionnelles generees.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def adapter_portions_recettes_planifiees(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """P5-14: ajuste automatiquement portion_ajustee sur les repas planifies."""
        from src.core.models import MesureCroissance, Planning, ProfilEnfant, Repas

        jules = db.query(ProfilEnfant).filter(ProfilEnfant.name == "Jules", ProfilEnfant.actif.is_(True)).first()
        if not jules:
            return {"repas_mis_a_jour": 0, "message": "Profil Jules introuvable."}

        mesure = (
            db.query(MesureCroissance)
            .filter(MesureCroissance.enfant_id == jules.id)
            .order_by(MesureCroissance.date_mesure.desc())
            .first()
        )
        if not mesure:
            return {"repas_mis_a_jour": 0, "message": "Aucune mesure de croissance disponible."}

        aujourd_hui = date_type.today()
        fin = aujourd_hui + timedelta(days=jours_horizon)
        planning = (
            db.query(Planning)
            .filter(Planning.semaine_debut <= aujourd_hui, Planning.semaine_fin >= aujourd_hui)
            .first()
        )
        if not planning:
            return {"repas_mis_a_jour": 0, "message": "Aucun planning actif."}

        if (mesure.age_mois or 0) < 18:
            portion_jules = 1
        elif (mesure.age_mois or 0) < 36:
            portion_jules = 2
        else:
            portion_jules = 3

        repas = (
            db.query(Repas)
            .filter(
                Repas.planning_id == planning.id,
                Repas.date_repas >= aujourd_hui,
                Repas.date_repas <= fin,
            )
            .all()
        )

        maj = 0
        for r in repas:
            if r.portion_ajustee != portion_jules:
                r.portion_ajustee = portion_jules
                r.adaptation_auto = True
                maj += 1

        if maj:
            db.commit()

        return {
            "repas_mis_a_jour": maj,
            "portion_jules": portion_jules,
            "message": f"{maj} repas ajustes pour Jules.",
        }


@service_factory("jules_nutrition_interaction", tags={"cuisine", "famille", "nutrition"})
def obtenir_service_jules_nutrition_interaction() -> JulesNutritionInteractionService:
    """Factory pour le bridge Jules -> nutrition."""
    return JulesNutritionInteractionService()
