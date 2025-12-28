"""
Service Planning REFACTORISÉ
Utilise les nouveaux decorators + cache + AIJsonParser
"""
import logging
from datetime import date, timedelta
from typing import List, Dict, Optional

from src.services.base_enhanced_service import EnhancedCRUDService
from src.core.database import get_db_context
from src.core.cache import Cache, RateLimit
from src.core.errors import handle_errors, NotFoundError
from src.core.ai import AIParser
from src.core.models import (
    PlanningHebdomadaire,
    RepasPlanning,
    ConfigPlanningUtilisateur,
    Recette,
    TypeVersionRecetteEnum,
)

logger = logging.getLogger(__name__)


class PlanningService(EnhancedCRUDService[PlanningHebdomadaire]):
    """Service métier pour le planning hebdomadaire - REFACTORISÉ"""

    JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    def __init__(self):
        super().__init__(PlanningHebdomadaire)

    # ═══════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=None)
    @Cache.cached(ttl=300)
    def get_or_create_config(self, utilisateur_id: int = None) -> ConfigPlanningUtilisateur:
        """Récupère ou crée la config utilisateur (avec cache)"""
        with get_db_context() as db:
            config = (
                db.query(ConfigPlanningUtilisateur)
                .filter(ConfigPlanningUtilisateur.utilisateur_id == utilisateur_id)
                .first()
            )

            if not config:
                config = ConfigPlanningUtilisateur(utilisateur_id=utilisateur_id)
                db.add(config)
                db.commit()
                db.refresh(config)

            return config

    @handle_errors(show_in_ui=True)
    def update_config(self, config_data: Dict, utilisateur_id: int = None):
        """Met à jour la config utilisateur"""
        with get_db_context() as db:
            config = self.get_or_create_config(utilisateur_id)

            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)

            db.commit()

            # Invalider cache
            Cache.invalidate("planning_config")
            logger.info("Config planning mise à jour")

    # ═══════════════════════════════════════════════════════════
    # CRUD PLANNING
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def get_semaine_debut(date_ref: date = None) -> date:
        """Retourne le lundi de la semaine"""
        if date_ref is None:
            date_ref = date.today()
        return date_ref - timedelta(days=date_ref.weekday())

    @handle_errors(show_in_ui=True, fallback_value=None)
    def create_planning(self, semaine_debut: date, nom: str = None) -> int:
        """Crée un nouveau planning vide"""
        data = {
            "semaine_debut": semaine_debut,
            "nom": nom or f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}",
            "statut": "brouillon"
        }

        planning = self.create(data)
        return planning.id if planning else None

    @handle_errors(show_in_ui=False, fallback_value=None)
    @Cache.cached(ttl=60)
    def get_planning_semaine(self, semaine_debut: date) -> Optional[PlanningHebdomadaire]:
        """Récupère le planning d'une semaine (avec cache)"""
        with get_db_context() as db:
            return (
                db.query(PlanningHebdomadaire)
                .filter(PlanningHebdomadaire.semaine_debut == semaine_debut)
                .first()
            )

    # ═══════════════════════════════════════════════════════════
    # EXPORT / UTILS
    # ═══════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=False, fallback_value=None)
    @Cache.cached(ttl=60)
    def get_planning_structure(self, planning_id: int) -> Dict:
        """Retourne le planning sous forme structurée (avec cache)"""
        with get_db_context() as db:
            planning = (
                db.query(PlanningHebdomadaire)
                .filter(PlanningHebdomadaire.id == planning_id)
                .first()
            )

            if not planning:
                raise NotFoundError(
                    f"Planning {planning_id} non trouvé",
                    user_message="Planning introuvable"
                )

            # Structure par jour
            structure = {
                "planning_id": planning.id,
                "nom": planning.nom,
                "semaine_debut": planning.semaine_debut,
                "jours": [],
            }

            for jour_idx in range(7):
                date_jour = planning.semaine_debut + timedelta(days=jour_idx)

                repas_jour = [r for r in planning.repas if r.jour_semaine == jour_idx]

                structure["jours"].append(
                    {
                        "jour_idx": jour_idx,
                        "nom_jour": self.JOURS_SEMAINE[jour_idx],
                        "date": date_jour,
                        "repas": [
                            {
                                "id": r.id,
                                "type": r.type_repas,
                                "recette": {
                                    "id": r.recette.id,
                                    "nom": r.recette.nom,
                                    "temps_total": r.recette.temps_preparation
                                                   + r.recette.temps_cuisson,
                                    "url_image": r.recette.url_image,
                                }
                                if r.recette
                                else None,
                                "portions": r.portions,
                                "est_adapte_bebe": r.est_adapte_bebe,
                                "est_batch": r.est_batch_cooking,
                                "notes": r.notes,
                                "statut": r.statut,
                            }
                            for r in sorted(repas_jour, key=lambda x: x.ordre)
                        ],
                    }
                )

            return structure


# Instance globale
planning_service = PlanningService()