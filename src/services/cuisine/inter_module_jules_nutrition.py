"""
Service inter-modules : Jules croissance -> Planning nutrition.

Bridge inter-modules :
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
    """Bridge Jules -> planning nutrition/portions."""

    @staticmethod
    def _calculer_age_mois(jules: Any) -> int:
        """Calcule un âge en mois à partir du profil Jules."""
        if not getattr(jules, "date_of_birth", None):
            return 0

        aujourd_hui = date_type.today()
        naissance = jules.date_of_birth
        correction = 1 if aujourd_hui.day < naissance.day else 0
        return max(
            0,
            (aujourd_hui.year - naissance.year) * 12
            + aujourd_hui.month
            - naissance.month
            - correction,
        )

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def adapter_planning_nutrition_jules(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """Produit des recommandations nutritionnelles à partir du profil actuel de Jules."""
        from src.core.models import ProfilEnfant

        jules = db.query(ProfilEnfant).filter(ProfilEnfant.name == "Jules", ProfilEnfant.actif.is_(True)).first()
        if not jules:
            return {"recommandations": [], "message": "Profil Jules introuvable."}

        age_mois = self._calculer_age_mois(jules)
        recommandations = []

        if age_mois < 12:
            recommandations.append("Conserver des textures très souples et introduire les nouveautés progressivement.")
        elif age_mois < 24:
            recommandations.append("Maintenir des textures adaptées et proposer des repas variés sur la semaine.")
        else:
            recommandations.append("Prévoir des portions enfant simples, variées et faciles à partager avec la famille.")

        recommandations.append("Respecter les aliments exclus et éviter le sel ajouté dans la version Jules.")
        recommandations.append(f"Horizon de planification nutritionnelle: {jours_horizon} jours.")

        return {
            "enfant_id": jules.id,
            "age_mois": age_mois,
            "recommandations": recommandations,
            "message": "Recommandations nutritionnelles générées.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def adapter_planning_nutrition_selon_croissance(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """Alias historique conservé pour compatibilité."""
        return self.adapter_planning_nutrition_jules(jours_horizon=jours_horizon, db=db)

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def adapter_portions_recettes_planifiees(
        self,
        *,
        jours_horizon: int = 7,
        db=None,
    ) -> dict[str, Any]:
        """Ajuste automatiquement portion_ajustee sur les repas planifiés selon l'âge de Jules."""
        from src.core.models import Planning, ProfilEnfant, Repas

        jules = db.query(ProfilEnfant).filter(ProfilEnfant.name == "Jules", ProfilEnfant.actif.is_(True)).first()
        if not jules:
            return {"repas_mis_a_jour": 0, "message": "Profil Jules introuvable."}

        age_mois = self._calculer_age_mois(jules)

        aujourd_hui = date_type.today()
        fin = aujourd_hui + timedelta(days=jours_horizon)
        planning = (
            db.query(Planning)
            .filter(Planning.semaine_debut <= aujourd_hui, Planning.semaine_fin >= aujourd_hui)
            .first()
        )
        if not planning:
            return {"repas_mis_a_jour": 0, "message": "Aucun planning actif."}

        if age_mois < 18:
            portion_jules = 1
        elif age_mois < 36:
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
            "age_mois": age_mois,
            "message": f"{maj} repas ajustés pour Jules.",
        }


@service_factory("jules_nutrition_interaction", tags={"cuisine", "famille", "nutrition"})
def obtenir_service_jules_nutrition_interaction() -> JulesNutritionInteractionService:
    """Factory pour le bridge Jules -> nutrition."""
    return JulesNutritionInteractionService()
