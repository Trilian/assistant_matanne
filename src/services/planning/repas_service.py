"""
Service Repas - Manipulation Repas dans Planning
Ajout, déplacement, échange, suppression
"""
import logging
from typing import Optional, Dict, List
from datetime import date, timedelta
from sqlalchemy.orm import Session

from src.core.database import get_db_context
from src.core.models import RepasPlanning, PlanningHebdomadaire, Recette, TypeRepasEnum

logger = logging.getLogger(__name__)


# ===================================
# SERVICE
# ===================================


class RepasService:
    """Service de manipulation des repas dans un planning"""

    # ===================================
    # CRÉATION
    # ===================================

    @staticmethod
    def ajouter_repas(
        planning_id: int,
        jour_semaine: int,
        date_repas: date,
        type_repas: str,
        recette_id: int,
        portions: int = 4,
        est_adapte_bebe: bool = False,
        est_batch: bool = False,
        notes: Optional[str] = None,
        db: Session = None,
    ) -> int:
        """
        Ajoute un repas au planning

        Returns:
            ID du repas créé
        """
        if db:
            return RepasService._do_ajouter(
                db,
                planning_id,
                jour_semaine,
                date_repas,
                type_repas,
                recette_id,
                portions,
                est_adapte_bebe,
                est_batch,
                notes,
            )

        with get_db_context() as db:
            return RepasService._do_ajouter(
                db,
                planning_id,
                jour_semaine,
                date_repas,
                type_repas,
                recette_id,
                portions,
                est_adapte_bebe,
                est_batch,
                notes,
            )

    @staticmethod
    def _do_ajouter(
        db: Session,
        planning_id: int,
        jour_semaine: int,
        date_repas: date,
        type_repas: str,
        recette_id: int,
        portions: int,
        est_adapte_bebe: bool,
        est_batch: bool,
        notes: Optional[str],
    ) -> int:
        """Implémentation"""
        # Calculer ordre
        ordre_map = {
            "petit_déjeuner": 1,
            "déjeuner": 2,
            "goûter": 3,
            "dîner": 4,
            "bébé": 5,
            "batch_cooking": 6,
        }
        ordre = ordre_map.get(type_repas, 0)

        repas = RepasPlanning(
            planning_id=planning_id,
            jour_semaine=jour_semaine,
            date=date_repas,
            type_repas=type_repas,
            recette_id=recette_id,
            portions=portions,
            est_adapte_bebe=est_adapte_bebe,
            est_batch_cooking=est_batch,
            notes=notes,
            ordre=ordre,
        )

        db.add(repas)
        db.commit()
        db.refresh(repas)

        logger.info(f"Repas ajouté: {type_repas} jour {jour_semaine}")
        return repas.id

    # ===================================
    # MODIFICATION
    # ===================================

    @staticmethod
    def modifier_repas(
        repas_id: int,
        recette_id: Optional[int] = None,
        portions: Optional[int] = None,
        est_adapte_bebe: Optional[bool] = None,
        notes: Optional[str] = None,
        db: Session = None,
    ) -> bool:
        """
        Modifie un repas existant

        Returns:
            True si modifié, False si non trouvé
        """
        if db:
            repas = db.query(RepasPlanning).get(repas_id)
            if not repas:
                return False

            if recette_id is not None:
                repas.recette_id = recette_id
            if portions is not None:
                repas.portions = portions
            if est_adapte_bebe is not None:
                repas.est_adapte_bebe = est_adapte_bebe
            if notes is not None:
                repas.notes = notes

            db.commit()
            logger.info(f"Repas {repas_id} modifié")
            return True

        with get_db_context() as db:
            repas = db.query(RepasPlanning).get(repas_id)
            if not repas:
                return False

            if recette_id is not None:
                repas.recette_id = recette_id
            if portions is not None:
                repas.portions = portions
            if est_adapte_bebe is not None:
                repas.est_adapte_bebe = est_adapte_bebe
            if notes is not None:
                repas.notes = notes

            db.commit()
            logger.info(f"Repas {repas_id} modifié")
            return True

    # ===================================
    # DÉPLACEMENT
    # ===================================

    @staticmethod
    def deplacer_repas(
        repas_id: int, nouveau_jour: int, nouvelle_date: date, db: Session = None
    ) -> bool:
        """
        Déplace un repas vers un autre jour

        Returns:
            True si déplacé
        """
        if db:
            repas = db.query(RepasPlanning).get(repas_id)
            if not repas:
                return False

            repas.jour_semaine = nouveau_jour
            repas.date = nouvelle_date
            db.commit()

            logger.info(f"Repas {repas_id} déplacé vers jour {nouveau_jour}")
            return True

        with get_db_context() as db:
            repas = db.query(RepasPlanning).get(repas_id)
            if not repas:
                return False

            repas.jour_semaine = nouveau_jour
            repas.date = nouvelle_date
            db.commit()

            logger.info(f"Repas {repas_id} déplacé vers jour {nouveau_jour}")
            return True

    @staticmethod
    def echanger_repas(repas_id_1: int, repas_id_2: int, db: Session = None) -> bool:
        """
        Échange deux repas (déjeuner ↔ dîner par exemple)

        Returns:
            True si échangé
        """
        if db:
            repas1 = db.query(RepasPlanning).get(repas_id_1)
            repas2 = db.query(RepasPlanning).get(repas_id_2)

            if not repas1 or not repas2:
                return False

            # Échanger recettes et attributs
            repas1.recette_id, repas2.recette_id = repas2.recette_id, repas1.recette_id
            repas1.portions, repas2.portions = repas2.portions, repas1.portions
            repas1.notes, repas2.notes = repas2.notes, repas1.notes
            repas1.est_adapte_bebe, repas2.est_adapte_bebe = (
                repas2.est_adapte_bebe,
                repas1.est_adapte_bebe,
            )

            db.commit()
            logger.info(f"Repas {repas_id_1} ↔ {repas_id_2} échangés")
            return True

        with get_db_context() as db:
            repas1 = db.query(RepasPlanning).get(repas_id_1)
            repas2 = db.query(RepasPlanning).get(repas_id_2)

            if not repas1 or not repas2:
                return False

            repas1.recette_id, repas2.recette_id = repas2.recette_id, repas1.recette_id
            repas1.portions, repas2.portions = repas2.portions, repas1.portions
            repas1.notes, repas2.notes = repas2.notes, repas1.notes
            repas1.est_adapte_bebe, repas2.est_adapte_bebe = (
                repas2.est_adapte_bebe,
                repas1.est_adapte_bebe,
            )

            db.commit()
            logger.info(f"Repas {repas_id_1} ↔ {repas_id_2} échangés")
            return True

    # ===================================
    # SUPPRESSION
    # ===================================

    @staticmethod
    def supprimer_repas(repas_id: int, db: Session = None) -> bool:
        """
        Supprime un repas

        Returns:
            True si supprimé
        """
        if db:
            count = db.query(RepasPlanning).filter(RepasPlanning.id == repas_id).delete()
            db.commit()

            logger.info(f"Repas {repas_id} supprimé")
            return count > 0

        with get_db_context() as db:
            count = db.query(RepasPlanning).filter(RepasPlanning.id == repas_id).delete()
            db.commit()

            logger.info(f"Repas {repas_id} supprimé")
            return count > 0

    # ===================================
    # DUPLICATION
    # ===================================

    @staticmethod
    def dupliquer_repas(
        repas_id: int, nouveau_jour: int, nouvelle_date: date, db: Session = None
    ) -> Optional[int]:
        """
        Duplique un repas vers un autre jour

        Returns:
            ID du nouveau repas créé
        """
        if db:
            return RepasService._do_dupliquer(db, repas_id, nouveau_jour, nouvelle_date)

        with get_db_context() as db:
            return RepasService._do_dupliquer(db, repas_id, nouveau_jour, nouvelle_date)

    @staticmethod
    def _do_dupliquer(
        db: Session, repas_id: int, nouveau_jour: int, nouvelle_date: date
    ) -> Optional[int]:
        """Implémentation"""
        repas_original = db.query(RepasPlanning).get(repas_id)

        if not repas_original:
            return None

        nouveau_repas = RepasPlanning(
            planning_id=repas_original.planning_id,
            jour_semaine=nouveau_jour,
            date=nouvelle_date,
            type_repas=repas_original.type_repas,
            recette_id=repas_original.recette_id,
            portions=repas_original.portions,
            est_adapte_bebe=repas_original.est_adapte_bebe,
            est_batch_cooking=repas_original.est_batch_cooking,
            notes=repas_original.notes,
            ordre=repas_original.ordre,
        )

        db.add(nouveau_repas)
        db.commit()
        db.refresh(nouveau_repas)

        logger.info(f"Repas {repas_id} dupliqué → {nouveau_repas.id}")
        return nouveau_repas.id

    # ===================================
    # MARQUAGE STATUT
    # ===================================

    @staticmethod
    def marquer_termine(repas_id: int, db: Session = None) -> bool:
        """
        Marque un repas comme terminé

        Returns:
            True si marqué
        """
        if db:
            repas = db.query(RepasPlanning).get(repas_id)
            if repas:
                repas.statut = "terminé"
                db.commit()
                logger.info(f"Repas {repas_id} marqué terminé")
                return True
            return False

        with get_db_context() as db:
            repas = db.query(RepasPlanning).get(repas_id)
            if repas:
                repas.statut = "terminé"
                db.commit()
                logger.info(f"Repas {repas_id} marqué terminé")
                return True
            return False

    # ===================================
    # RÉCUPÉRATION ENRICHIE
    # ===================================

    @staticmethod
    def get_repas_avec_details(repas_id: int, db: Session = None) -> Optional[Dict]:
        """
        Récupère un repas avec toutes ses infos enrichies

        Returns:
            Dict avec repas + recette + détails
        """
        if db:
            return RepasService._do_get_details(db, repas_id)

        with get_db_context() as db:
            return RepasService._do_get_details(db, repas_id)

    @staticmethod
    def _do_get_details(db: Session, repas_id: int) -> Optional[Dict]:
        """Implémentation"""
        repas = db.query(RepasPlanning).get(repas_id)

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
            }
            if recette
            else None,
        }


# ===================================
# INSTANCE GLOBALE
# ===================================

repas_service = RepasService()
