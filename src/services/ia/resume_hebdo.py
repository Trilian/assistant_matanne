"""
Service IA — Résumé hebdomadaire intelligent.

Génère un résumé narratif de la semaine (repas, tâches, budget, scores)
via Mistral AI (B4.3 / IA5).
"""

import logging
from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ResumeHebdoService(BaseAIService):
    """Service de génération de résumé hebdomadaire intelligent."""

    def __init__(self):
        super().__init__(
            cache_prefix="resume_hebdo",
            default_ttl=3600,
            service_name="resume_hebdo",
        )

    @avec_gestion_erreurs(default_return={})
    @avec_session_db
    def collecter_donnees_semaine(self, db: Session | None = None) -> dict:
        """Collecte les données de la semaine pour le résumé.

        Returns:
            Dict avec repas, taches, budget, activites, etc.
        """
        from src.core.models import BudgetFamille
        from src.core.models.planning import Repas
        from src.core.models import TacheEntretien

        aujourd_hui = date.today()
        lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        dimanche = lundi + timedelta(days=6)

        # Repas de la semaine
        repas = (
            db.query(Repas)
            .filter(Repas.date_repas >= lundi, Repas.date_repas <= dimanche)
            .all()
        )
        repas_prepares = sum(1 for r in repas if r.prepare)
        repas_consommes = sum(1 for r in repas if r.consomme)

        # Tâches entretien terminées cette semaine
        taches_faites = (
            db.query(func.count(TacheEntretien.id))
            .filter(
                TacheEntretien.fait.is_(True),
                TacheEntretien.prochaine_fois >= lundi,
                TacheEntretien.prochaine_fois <= dimanche,
            )
            .scalar() or 0
        )

        # Budget semaine
        depenses_semaine = (
            db.query(func.sum(BudgetFamille.montant))
            .filter(
                BudgetFamille.date >= lundi,
                BudgetFamille.date <= dimanche,
            )
            .scalar() or 0
        )

        return {
            "periode": f"{lundi.strftime('%d/%m')} - {dimanche.strftime('%d/%m/%Y')}",
            "repas": {
                "planifies": len(repas),
                "prepares": repas_prepares,
                "consommes": repas_consommes,
            },
            "taches_entretien_faites": taches_faites,
            "budget": {
                "depenses_semaine": float(depenses_semaine),
            },
        }

    def generer_resume(self, donnees: dict | None = None) -> dict:
        """Génère le résumé narratif via IA.

        Args:
            donnees: Données préalablement collectées (ou auto-collectées)

        Returns:
            Dict avec resume_texte, points_forts, suggestions
        """
        if not donnees:
            donnees = self.collecter_donnees_semaine()

        if not donnees:
            return {
                "resume_texte": "Pas de données disponibles pour cette semaine.",
                "points_forts": [],
                "suggestions": [],
            }

        prompt = f"""Génère un résumé familial de la semaine en français.

Données de la semaine ({donnees.get('periode', 'cette semaine')}):
- Repas planifiés: {donnees['repas']['planifies']}, préparés: {donnees['repas']['prepares']}, consommés: {donnees['repas']['consommes']}
- Tâches entretien terminées: {donnees['taches_entretien_faites']}
- Dépenses semaine: {donnees['budget']['depenses_semaine']:.2f}€

Réponds en JSON:
{{
  "resume_texte": "Résumé narratif sympathique de la semaine en 3-4 phrases",
  "points_forts": ["point fort 1", "point fort 2"],
  "suggestions": ["suggestion amélioration 1", "suggestion 2"]
}}"""

        try:
            result = self.call_with_parsing_sync(
                prompt=prompt,
                system_prompt="Tu es un assistant familial bienveillant. Réponds toujours en JSON valide.",
            )
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Erreur IA résumé hebdo: {e}")

        # Fallback sans IA
        return {
            "resume_texte": (
                f"Cette semaine ({donnees.get('periode', '')}), "
                f"vous avez planifié {donnees['repas']['planifies']} repas "
                f"et terminé {donnees['taches_entretien_faites']} tâches d'entretien. "
                f"Dépenses: {donnees['budget']['depenses_semaine']:.2f}€."
            ),
            "points_forts": [],
            "suggestions": [],
            "donnees_brutes": donnees,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("resume_hebdo", tags={"ia", "dashboard"})
def obtenir_service_resume_hebdo() -> ResumeHebdoService:
    """Factory singleton pour le service de résumé hebdomadaire."""
    return ResumeHebdoService()

