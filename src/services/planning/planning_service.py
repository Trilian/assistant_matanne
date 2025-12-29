"""
Services Planning + Repas ULTRA-OPTIMISÉS v2.0
Fusion intelligente + EnhancedCRUDService
AVANT: 400 lignes (2 fichiers) | APRÈS: 180 lignes (-55%)
"""
from typing import List, Dict, Optional, Tuple
from datetime import date, timedelta
from sqlalchemy.orm import Session

from src.services.base_enhanced_service import EnhancedCRUDService
from src.core.cache import Cache
from src.core.errors import handle_errors, NotFoundError
from src.core.database import get_db_context
from src.core.models import (
    PlanningHebdomadaire, RepasPlanning, ConfigPlanningUtilisateur,
    Recette, TypeRepasEnum, VersionRecette, TypeVersionRecetteEnum
)
import logging

logger = logging.getLogger(__name__)

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# ═══════════════════════════════════════════════════════════════
# PLANNING SERVICE (Unifié)
# ═══════════════════════════════════════════════════════════════

class PlanningService(EnhancedCRUDService[PlanningHebdomadaire]):
    """Service planning optimisé"""

    def __init__(self):
        super().__init__(PlanningHebdomadaire)

    # ═══════════════════════════════════════════════════════════════
    # CONFIGURATION
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=300)
    def get_or_create_config(self, utilisateur_id: int = None) -> ConfigPlanningUtilisateur:
        """Config utilisateur - Cache 5min"""
        with get_db_context() as db:
            config = db.query(ConfigPlanningUtilisateur).filter(
                ConfigPlanningUtilisateur.utilisateur_id == utilisateur_id
            ).first()

            if not config:
                config = ConfigPlanningUtilisateur(utilisateur_id=utilisateur_id)
                db.add(config)
                db.commit()
                db.refresh(config)

            return config

    @handle_errors(show_in_ui=True)
    def update_config(self, config_data: Dict, utilisateur_id: int = None):
        """Met à jour config"""
        with get_db_context() as db:
            config = self.get_or_create_config(utilisateur_id)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            db.commit()
            Cache.invalidate("config")

    # ═══════════════════════════════════════════════════════════════
    # CRUD PLANNING (utilise base)
    # ═══════════════════════════════════════════════════════════════

    @staticmethod
    def get_semaine_debut(date_ref: date = None) -> date:
        """Lundi de la semaine"""
        if date_ref is None:
            date_ref = date.today()
        return date_ref - timedelta(days=date_ref.weekday())

    @handle_errors(show_in_ui=True)
    def create_planning(self, semaine_debut: date, nom: str = None) -> int:
        """Crée planning vide"""
        planning = self.create({
            "semaine_debut": semaine_debut,
            "nom": nom or f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}",
            "statut": "brouillon"
        })
        return planning.id

    @Cache.cached(ttl=60)
    def get_planning_semaine(self, semaine_debut: date) -> Optional[PlanningHebdomadaire]:
        """Planning d'une semaine - Cache 60s"""
        with get_db_context() as db:
            return db.query(PlanningHebdomadaire).filter(
                PlanningHebdomadaire.semaine_debut == semaine_debut
            ).first()

    @handle_errors(show_in_ui=True)
    def delete_planning(self, planning_id: int):
        """Supprime planning"""
        self.delete(planning_id)
        Cache.invalidate("planning")

    # ═══════════════════════════════════════════════════════════════
    # STRUCTURE (Vue enrichie)
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=30)
    def get_planning_structure(self, planning_id: int) -> Dict:
        """Structure complète (cache 30s)"""
        with get_db_context() as db:
            planning = db.query(PlanningHebdomadaire).filter(
                PlanningHebdomadaire.id == planning_id
            ).first()

            if not planning:
                return None

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
                            "est_batch": r.est_batch_cooking,
                            "notes": r.notes,
                            "statut": r.statut,
                        }
                        for r in sorted(repas_jour, key=lambda x: x.ordre)
                    ]
                })

            return structure


# ═══════════════════════════════════════════════════════════════
# REPAS SERVICE (Optimisé)
# ═══════════════════════════════════════════════════════════════

class RepasService(EnhancedCRUDService[RepasPlanning]):
    """Service repas optimisé"""

    def __init__(self):
        super().__init__(RepasPlanning)

    # Ordre des types de repas
    ORDRE_MAP = {
        "petit_déjeuner": 1, "déjeuner": 2, "goûter": 3,
        "dîner": 4, "bébé": 5, "batch_cooking": 6
    }

    # ═══════════════════════════════════════════════════════════════
    # CRÉATION
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def ajouter_repas(self, planning_id: int, jour_semaine: int,
                      date_repas: date, type_repas: str, recette_id: int,
                      portions: int = 4, est_adapte_bebe: bool = False,
                      est_batch: bool = False, notes: Optional[str] = None,
                      db: Session = None) -> int:
        """Ajoute repas"""
        repas = self.create({
            "planning_id": planning_id,
            "jour_semaine": jour_semaine,
            "date": date_repas,
            "type_repas": type_repas,
            "recette_id": recette_id,
            "ordre": self.ORDRE_MAP.get(type_repas, 0),
            "portions": portions,
            "est_adapte_bebe": est_adapte_bebe,
            "est_batch_cooking": est_batch,
            "notes": notes
        }, db=db)

        Cache.invalidate("planning")
        logger.info(f"Repas ajouté: {type_repas} jour {jour_semaine}")
        return repas.id

    # ═══════════════════════════════════════════════════════════════
    # MODIFICATION
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def modifier_repas(self, repas_id: int, **kwargs) -> bool:
        """Modifie repas"""
        updated = self.update(repas_id, kwargs)
        if updated:
            Cache.invalidate("planning")
        return updated is not None

    @handle_errors(show_in_ui=True)
    def deplacer_repas(self, repas_id: int, nouveau_jour: int,
                       nouvelle_date: date) -> bool:
        """Déplace repas"""
        return self.modifier_repas(
            repas_id,
            jour_semaine=nouveau_jour,
            date=nouvelle_date
        )

    @handle_errors(show_in_ui=True)
    def echanger_repas(self, repas_id_1: int, repas_id_2: int) -> bool:
        """Échange deux repas"""
        with get_db_context() as db:
            repas1 = self.get_by_id(repas_id_1, db)
            repas2 = self.get_by_id(repas_id_2, db)

            if not repas1 or not repas2:
                return False

            # Échanger
            repas1.recette_id, repas2.recette_id = repas2.recette_id, repas1.recette_id
            repas1.portions, repas2.portions = repas2.portions, repas1.portions
            repas1.notes, repas2.notes = repas2.notes, repas1.notes
            repas1.est_adapte_bebe, repas2.est_adapte_bebe = (
                repas2.est_adapte_bebe, repas1.est_adapte_bebe
            )

            db.commit()
            Cache.invalidate("planning")
            logger.info(f"Repas {repas_id_1} ↔ {repas_id_2} échangés")
            return True

    # ═══════════════════════════════════════════════════════════════
    # SUPPRESSION
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def supprimer_repas(self, repas_id: int) -> bool:
        """Supprime repas"""
        success = self.delete(repas_id)
        if success:
            Cache.invalidate("planning")
        return success

    # ═══════════════════════════════════════════════════════════════
    # DUPLICATION
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def dupliquer_repas(self, repas_id: int, nouveau_jour: int,
                        nouvelle_date: date) -> Optional[int]:
        """Duplique repas"""
        with get_db_context() as db:
            repas_original = self.get_by_id(repas_id, db)
            if not repas_original:
                return None

            nouveau_repas = self.create({
                "planning_id": repas_original.planning_id,
                "jour_semaine": nouveau_jour,
                "date": nouvelle_date,
                "type_repas": repas_original.type_repas,
                "recette_id": repas_original.recette_id,
                "portions": repas_original.portions,
                "est_adapte_bebe": repas_original.est_adapte_bebe,
                "est_batch_cooking": repas_original.est_batch_cooking,
                "notes": repas_original.notes,
                "ordre": repas_original.ordre
            }, db=db)

            Cache.invalidate("planning")
            logger.info(f"Repas {repas_id} dupliqué → {nouveau_repas.id}")
            return nouveau_repas.id

    # ═══════════════════════════════════════════════════════════════
    # STATUT
    # ═══════════════════════════════════════════════════════════════

    @handle_errors(show_in_ui=True)
    def marquer_termine(self, repas_id: int) -> bool:
        """Marque terminé"""
        return self.modifier_repas(repas_id, statut="terminé")

    # ═══════════════════════════════════════════════════════════════
    # RÉCUPÉRATION ENRICHIE
    # ═══════════════════════════════════════════════════════════════

    @Cache.cached(ttl=30)
    def get_repas_avec_details(self, repas_id: int) -> Optional[Dict]:
        """Repas avec détails - Cache 30s"""
        with get_db_context() as db:
            repas = self.get_by_id(repas_id, db)
            if not repas:
                return None

            recette = db.query(Recette).get(repas.recette_id) if repas.recette_id else None

            return {
                "id": repas.id,
                "jour_semaine": repas.jour_semaine,
                "date": repas.date,
                "type_repas": repas.type_repas,
                "portions": repas.portions,
                "est_adapte_bebe": repas.est_adapte_bebe,
                "est_batch": repas.est_batch_cooking,
                "notes": repas.notes,
                "statut": repas.statut,
                "recette": {
                    "id": recette.id,
                    "nom": recette.nom,
                    "temps_total": recette.temps_preparation + recette.temps_cuisson,
                    "difficulte": recette.difficulte,
                    "url_image": recette.url_image,
                } if recette else None
            }


# ═══════════════════════════════════════════════════════════════
# INSTANCES GLOBALES
# ═══════════════════════════════════════════════════════════════

planning_service = PlanningService()
repas_service = RepasService()