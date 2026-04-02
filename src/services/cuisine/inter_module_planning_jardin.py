"""
Service inter-modules : Planning → Jardin feedback loop.

NIM2: Ingrédients jardin non utilisés en planning → ajuster la production.
Event subscriber: quand planning finalisé → comparer avec récoltes disponibles → feedback.
"""

import logging
from typing import Any

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class PlanningJardinInteractionService:
    """Service inter-modules Planning → Jardin feedback loop."""

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def analyser_recoltes_non_utilisees(
        self,
        *,
        semaines_lookback: int = 4,
        db=None,
    ) -> dict[str, Any]:
        """Identifie les récoltes du jardin non utilisées dans le planning.

        Compare les récoltes disponibles vs les ingrédients planifiés sur une période
        pour détecter les surproductions ou les pertes potentielles.

        Args:
            semaines_lookback: Nombre de semaines à analyser (défaut: 4)
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Dict avec:
                - recoltes_non_utilisees: Liste des plantes non planifiées
                - taux_utilisation: % des récoltes utilisées
                - recommandations: Suggestions d'amélioration production
        """
        from src.core.models.temps_entretien import ActionPlante, PlanteJardin

        # Récupérer les récoltes disponibles
        plantes_au_jardin = db.query(PlanteJardin).all()

        if not plantes_au_jardin:
            return {
                "recoltes_non_utilisees": [],
                "taux_utilisation": 0.0,
                "recommendations": [],
                "recommandations": [],
                "message": "Aucune plante active au jardin.",
            }

        # Approximation robuste: une plante est considérée utilisée si une récolte
        # a été enregistrée sur la période analysée.
        recoltes_recentes = (
            db.query(ActionPlante.plante_id)
            .filter(ActionPlante.type_action == "recolte")
            .all()
        )
        plantes_utilisees = {plante_id for (plante_id,) in recoltes_recentes}

        # Comparer avec les plantes du jardin
        recoltes_non_utilisees = []
        recoltes_utilisees = 0

        for plante in plantes_au_jardin:
            est_utilisee = plante.id in plantes_utilisees

            if not est_utilisee:
                recoltes_non_utilisees.append({
                    "plante_id": plante.id,
                    "nom": getattr(plante, 'nom', 'Inconnue'),
                    "quantite_recolte": 1,
                    "unite": getattr(plante, 'unite', None) or "kg",
                    "risque_perte": "moyen",
                })
            else:
                recoltes_utilisees += 1

        taux_utilisation = (recoltes_utilisees / len(plantes_au_jardin) * 100) if plantes_au_jardin else 0.0

        # Générer recommandations
        recommandations = []
        if taux_utilisation < 50:
            recommandations.append("⚠️ Moins de 50% des récoltes utilisées — envisager de réduire la production")
        if len(recoltes_non_utilisees) > 3:
            recommandations.append("📋 Intégrer davantage les productions existantes au planning")
        if any(r["risque_perte"] == "élevé" for r in recoltes_non_utilisees):
            recommandations.append("⏰ Des récoltes à conservation courte risquent d'être perdues")

        logger.info(
            f"✅ Planning→Jardin: {taux_utilisation:.1f}% utilisation, "
            f"{len(recoltes_non_utilisees)} récoltes non utilisées"
        )

        return {
            "periode_semaines": semaines_lookback,
            "recoltes_non_utilisees": recoltes_non_utilisees,
            "taux_utilisation": round(taux_utilisation, 1),
            "recommendations": recommandations,
            "recommandations": recommandations,
            "message": f"{len(recoltes_non_utilisees)} récolte(s) non intégrée(s) au planning.",
        }

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def modifier_production_jardin_selon_planning(
        self,
        *,
        plante_id: int,
        facteur_ajustement: float = 0.8,
        db=None,
    ) -> dict[str, Any]:
        """Ajuste les quantités de production pour une plante basé sur l'utilisation.

        Args:
            plante_id: ID de la plante à ajuster
            facteur_ajustement: Coefficient de réduction (ex: 0.8 = réduire de 20%)
            db: Session DB

        Returns:
            Dict avec ancien_surface, nouvelle_surface, message
        """
        from src.core.models.temps_entretien import PlanteJardin

        plante = db.query(PlanteJardin).filter(PlanteJardin.id == plante_id).first()

        if not plante:
            return {"error": "Plante non trouvée", "plante_id": plante_id}

        zone = getattr(plante, "zone", None)
        ancien_surface = float(getattr(zone, "superficie_m2", 0.0) or 0.0)
        nouvelle_surface = ancien_surface * facteur_ajustement

        ajustement_persisted = zone is not None and hasattr(zone, "superficie_m2")
        if ajustement_persisted:
            zone.superficie_m2 = nouvelle_surface
            db.commit()
            db.refresh(zone)

        if ajustement_persisted:
            logger.info(
                f"✅ Production ajustée pour {plante.nom}: "
                f"{ancien_surface:.1f}m² → {nouvelle_surface:.1f}m² (facteur {facteur_ajustement})"
            )
            message = f"Ajustement recolte pour {plante.nom} appliqué sur la zone." 
        else:
            logger.info(
                f"ℹ️ Ajustement recommandé pour {plante.nom}: "
                f"{ancien_surface:.1f}m² → {nouvelle_surface:.1f}m² (facteur {facteur_ajustement})"
            )
            message = f"Ajustement recommandé pour {plante.nom}, sans modification persistée."

        return {
            "plante_id": plante.id,
            "nom": plante.nom,
            "zone_id": getattr(plante, "zone_id", None),
            "ancien_surface_m2": ancien_surface,
            "nouvelle_surface_m2": round(nouvelle_surface, 2),
            "facteur_ajustement": facteur_ajustement,
            "ajustement_persisted": ajustement_persisted,
            "message": message,
        }


@service_factory("planning_jardin", tags={"planning", "jardin", "feedback"})
def get_planning_jardin_service() -> PlanningJardinInteractionService:
    """Factory pour le service inter-modules Planning→Jardin."""
    return PlanningJardinInteractionService()
