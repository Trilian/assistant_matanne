"""
Service Planning - IMPORTS CORRIGÉS
"""
from datetime import date, timedelta
from typing import Optional, Dict
from src.services.base_service import BaseService
from src.core.models import PlanningHebdomadaire, RepasPlanning
from src.core.errors import handle_errors  # ✅ AJOUTÉ
from src.core.database import get_db_context  # ✅ AJOUTÉ

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


class PlanningService(BaseService[PlanningHebdomadaire]):
    def __init__(self):
        super().__init__(PlanningHebdomadaire, cache_ttl=60)

    @staticmethod
    def get_semaine_debut(date_ref: date = None) -> date:
        """Lundi de la semaine"""
        if date_ref is None:
            date_ref = date.today()
        return date_ref - timedelta(days=date_ref.weekday())

    @handle_errors(show_in_ui=False, fallback_value=None)
    def get_planning_semaine(self, semaine_debut: date):
        """Planning d'une semaine"""
        with get_db_context() as db:
            return db.query(PlanningHebdomadaire).filter(
                PlanningHebdomadaire.semaine_debut == semaine_debut
            ).first()

    @handle_errors(show_in_ui=False, fallback_value={})
    def get_planning_structure(self, planning_id: int) -> Dict:
        """Structure complète du planning"""
        with get_db_context() as db:
            planning = db.query(PlanningHebdomadaire).filter(
                PlanningHebdomadaire.id == planning_id
            ).first()

            if not planning:
                return {}

            structure = {
                "planning_id": planning.id,
                "nom": planning.nom,
                "semaine_debut": planning.semaine_debut,
                "jours": []
            }

            for jour_idx in range(7):
                date_jour = planning.semaine_debut + timedelta(days=jour_idx)
                repas_jour = [r for r in planning.repas if r.jour_semaine == jour_idx]

                structure["jours"].append({
                    "jour_idx": jour_idx,
                    "nom_jour": JOURS_SEMAINE[jour_idx],
                    "date": date_jour,
                    "repas": [
                        {
                            "id": r.id,
                            "type": r.type_repas,
                            "recette": {
                                "id": r.recette.id,
                                "nom": r.recette.nom,
                                "temps_total": r.recette.temps_preparation + r.recette.temps_cuisson,
                                "url_image": r.recette.url_image,
                            } if r.recette else None,
                            "portions": r.portions,
                            "est_adapte_bebe": r.est_adapte_bebe,
                            "statut": r.statut,
                        }
                        for r in sorted(repas_jour, key=lambda x: x.ordre)
                    ]
                })

            return structure


class RepasService(BaseService[RepasPlanning]):
    def __init__(self):
        super().__init__(RepasPlanning, cache_ttl=30)


planning_service = PlanningService()
repas_service = RepasService()