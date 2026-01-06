"""
Service Repas - Gestion complète des repas planifiés
Partie du système Planning (planning + repas + génération IA)
"""
import logging
from typing import List, Dict, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload

from src.core.database import get_db_context
from src.core.models import Repas, Recette
from src.services.base_service import BaseService
from src.core.cache import Cache

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# SERVICE REPAS
# ═══════════════════════════════════════════════════════════

class RepasService(BaseService[Repas]):
    """
    Service de gestion des repas

    Features:
    - CRUD repas avec validation
    - Liaison planning ↔ recettes
    - Copie/duplication repas
    - Statuts (planifié, préparé, terminé)
    - Recherche par date/type/planning
    """

    def __init__(self):
        super().__init__(Repas)

    # ═══════════════════════════════════════════════════════
    # CRUD ENRICHI
    # ═══════════════════════════════════════════════════════

    @Cache.cached(ttl=300, key="repas_{repas_id}")
    def get_by_id(self, repas_id: int, with_relations: bool = True) -> Optional[Dict]:
        """
        Récupère repas avec relations

        Args:
            repas_id: ID du repas
            with_relations: Charger recette associée

        Returns:
            Dict avec données repas + recette
        """
        with get_db_context() as db:
            query = db.query(Repas).filter(Repas.id == repas_id)

            if with_relations:
                query = query.options(joinedload(Repas.recette))

            repas = query.first()

            if not repas:
                return None

            return self._to_dict(repas, include_recette=with_relations)

    def get_by_planning(
            self,
            planning_id: int,
            jour_semaine: Optional[int] = None,
            type_repas: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère repas d'un planning

        Args:
            planning_id: ID planning
            jour_semaine: Filtrer par jour (0-6)
            type_repas: Filtrer par type

        Returns:
            Liste des repas
        """
        cache_key = f"repas_planning_{planning_id}_{jour_semaine}_{type_repas}"

        @Cache.cached(ttl=300, key=cache_key)
        def _query():
            with get_db_context() as db:
                query = db.query(Repas).filter(
                    Repas.planning_id == planning_id
                ).options(joinedload(Repas.recette))

                if jour_semaine is not None:
                    query = query.filter(Repas.jour_semaine == jour_semaine)

                if type_repas:
                    query = query.filter(Repas.type_repas == type_repas)

                query = query.order_by(Repas.jour_semaine, Repas.type_repas)

                repas = query.all()
                return [self._to_dict(r, include_recette=True) for r in repas]

        return _query()

    def get_by_date_range(
            self,
            date_debut: date,
            date_fin: date,
            type_repas: Optional[str] = None
    ) -> List[Dict]:
        """
        Récupère repas sur une période

        Args:
            date_debut: Date début
            date_fin: Date fin
            type_repas: Filtrer par type

        Returns:
            Liste des repas
        """
        with get_db_context() as db:
            query = db.query(Repas).filter(
                Repas.date >= date_debut,
                Repas.date <= date_fin
            ).options(joinedload(Repas.recette))

            if type_repas:
                query = query.filter(Repas.type_repas == type_repas)

            query = query.order_by(Repas.date, Repas.type_repas)

            repas = query.all()
            return [self._to_dict(r, include_recette=True) for r in repas]

    # ═══════════════════════════════════════════════════════
    # CRÉATION & MISE À JOUR
    # ═══════════════════════════════════════════════════════

    def create(self, data: Dict) -> Repas:
        """
        Crée un repas

        Args:
            data: {
                planning_id: int,
                jour_semaine: int (0-6),
                date: date,
                type_repas: str,
                recette_id: int (optionnel),
                portions: int,
                est_adapte_bebe: bool,
                notes: str,
                statut: str (défaut: "planifié")
            }

        Returns:
            Repas créé
        """
        # Validation
        self._validate_repas_data(data)

        # Défauts
        if "statut" not in data:
            data["statut"] = "planifié"

        if "portions" not in data:
            data["portions"] = 4

        # Créer
        repas = super().create(data)

        # Invalider cache
        Cache.invalidate(dependencies=[
            f"planning_{data['planning_id']}",
            f"repas_planning_{data['planning_id']}"
        ])

        logger.info(f"Repas créé: {repas.id} (planning {data['planning_id']}, jour {data['jour_semaine']})")

        return repas

    def update(self, repas_id: int, data: Dict) -> Repas:
        """
        Met à jour un repas

        Args:
            repas_id: ID repas
            data: Champs à mettre à jour

        Returns:
            Repas mis à jour
        """
        # Validation si changement de recette/portions
        if "recette_id" in data or "portions" in data:
            self._validate_repas_data(data, is_update=True)

        # Update
        repas = super().update(repas_id, data)

        # Invalider cache
        Cache.invalidate(dependencies=[
            f"repas_{repas_id}",
            f"planning_{repas.planning_id}",
            f"repas_planning_{repas.planning_id}"
        ])

        logger.info(f"Repas {repas_id} mis à jour")

        return repas

    # ═══════════════════════════════════════════════════════
    # ACTIONS MÉTIER
    # ═══════════════════════════════════════════════════════

    def copier_repas(
            self,
            repas_id: int,
            nouveau_planning_id: int,
            nouveau_jour: int,
            nouveau_type: Optional[str] = None
    ) -> Repas:
        """
        Copie un repas vers un autre jour/planning

        Args:
            repas_id: Repas source
            nouveau_planning_id: Planning cible
            nouveau_jour: Jour cible (0-6)
            nouveau_type: Type repas (garde original si None)

        Returns:
            Nouveau repas créé
        """
        repas_original = self.get_by_id(repas_id)

        if not repas_original:
            raise ValueError(f"Repas {repas_id} introuvable")

        # Calculer nouvelle date
        with get_db_context() as db:
            from src.core.models import Planning
            planning = db.query(Planning).filter(
                Planning.id == nouveau_planning_id
            ).first()

            if not planning:
                raise ValueError(f"Planning {nouveau_planning_id} introuvable")

            nouvelle_date = planning.semaine_debut + timedelta(days=nouveau_jour)

        # Créer copie
        data_copie = {
            "planning_id": nouveau_planning_id,
            "jour_semaine": nouveau_jour,
            "date": nouvelle_date,
            "type_repas": nouveau_type or repas_original["type_repas"],
            "recette_id": repas_original.get("recette_id"),
            "portions": repas_original["portions"],
            "est_adapte_bebe": repas_original.get("est_adapte_bebe", False),
            "notes": f"Copié de repas #{repas_id}",
            "statut": "planifié"
        }

        nouveau_repas = self.create(data_copie)

        logger.info(f"Repas {repas_id} copié vers {nouveau_repas.id}")

        return nouveau_repas

    def dupliquer_semaine(
            self,
            planning_source_id: int,
            planning_cible_id: int
    ) -> List[Repas]:
        """
        Duplique tous les repas d'une semaine vers une autre

        Args:
            planning_source_id: Planning source
            planning_cible_id: Planning cible

        Returns:
            Liste des repas créés
        """
        repas_source = self.get_by_planning(planning_source_id)

        if not repas_source:
            logger.warning(f"Aucun repas dans planning {planning_source_id}")
            return []

        repas_crees = []

        with get_db_context() as db:
            from src.core.models import Planning
            planning_cible = db.query(Planning).filter(
                Planning.id == planning_cible_id
            ).first()

            if not planning_cible:
                raise ValueError(f"Planning {planning_cible_id} introuvable")

            for repas in repas_source:
                nouvelle_date = planning_cible.semaine_debut + timedelta(
                    days=repas["jour_semaine"]
                )

                data = {
                    "planning_id": planning_cible_id,
                    "jour_semaine": repas["jour_semaine"],
                    "date": nouvelle_date,
                    "type_repas": repas["type_repas"],
                    "recette_id": repas.get("recette_id"),
                    "portions": repas["portions"],
                    "est_adapte_bebe": repas.get("est_adapte_bebe", False),
                    "notes": f"Dupliqué de semaine {planning_source_id}",
                    "statut": "planifié"
                }

                nouveau = self.create(data)
                repas_crees.append(nouveau)

        logger.info(
            f"{len(repas_crees)} repas dupliqués "
            f"de {planning_source_id} vers {planning_cible_id}"
        )

        return repas_crees

    def marquer_termine(self, repas_id: int) -> Repas:
        """
        Marque repas comme terminé

        Args:
            repas_id: ID repas

        Returns:
            Repas mis à jour
        """
        return self.update(repas_id, {
            "statut": "terminé",
            "date_realisation": date.today()
        })

    def marquer_prepare(self, repas_id: int) -> Repas:
        """
        Marque repas comme préparé

        Args:
            repas_id: ID repas

        Returns:
            Repas mis à jour
        """
        return self.update(repas_id, {"statut": "préparé"})

    # ═══════════════════════════════════════════════════════
    # STATS & ANALYSE
    # ═══════════════════════════════════════════════════════

    def get_stats_planning(self, planning_id: int) -> Dict:
        """
        Stats d'un planning

        Returns:
            {
                total_repas: int,
                repas_avec_recette: int,
                repas_bebe: int,
                total_portions: int,
                statuts: {planifié: x, préparé: y, terminé: z}
            }
        """
        repas = self.get_by_planning(planning_id)

        stats = {
            "total_repas": len(repas),
            "repas_avec_recette": len([r for r in repas if r.get("recette_id")]),
            "repas_bebe": len([r for r in repas if r.get("est_adapte_bebe")]),
            "total_portions": sum(r.get("portions", 0) for r in repas),
            "statuts": {}
        }

        # Compter statuts
        from collections import Counter
        statuts = Counter(r.get("statut", "planifié") for r in repas)
        stats["statuts"] = dict(statuts)

        return stats

    # ═══════════════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════════════

    def _to_dict(self, repas: Repas, include_recette: bool = True) -> Dict:
        """Convertit Repas ORM en dict"""
        data = {
            "id": repas.id,
            "planning_id": repas.planning_id,
            "jour_semaine": repas.jour_semaine,
            "date": repas.date,
            "type_repas": repas.type_repas,
            "recette_id": repas.recette_id,
            "portions": repas.portions,
            "est_adapte_bebe": repas.est_adapte_bebe,
            "notes": repas.notes,
            "statut": repas.statut,
            "date_realisation": repas.date_realisation,
            "created_at": repas.created_at,
            "updated_at": repas.updated_at
        }

        # Inclure recette si demandé
        if include_recette and repas.recette:
            data["recette"] = {
                "id": repas.recette.id,
                "nom": repas.recette.nom,
                "description": repas.recette.description,
                "temps_preparation": repas.recette.temps_preparation,
                "temps_cuisson": repas.recette.temps_cuisson,
                "temps_total": (
                        repas.recette.temps_preparation +
                        repas.recette.temps_cuisson
                ),
                "portions": repas.recette.portions,
                "difficulte": repas.recette.difficulte,
                "url_image": repas.recette.url_image
            }

        return data

    def _validate_repas_data(self, data: Dict, is_update: bool = False):
        """Valide données repas"""
        errors = []

        if not is_update:
            # Champs requis pour création
            if "planning_id" not in data:
                errors.append("planning_id requis")

            if "jour_semaine" not in data:
                errors.append("jour_semaine requis")
            elif not (0 <= data["jour_semaine"] <= 6):
                errors.append("jour_semaine doit être entre 0 et 6")

            if "date" not in data:
                errors.append("date requise")

            if "type_repas" not in data:
                errors.append("type_repas requis")

        # Validation type_repas
        if "type_repas" in data:
            types_valides = ["petit_déjeuner", "déjeuner", "goûter", "dîner", "bébé"]
            if data["type_repas"] not in types_valides:
                errors.append(f"type_repas doit être dans {types_valides}")

        # Validation portions
        if "portions" in data:
            if not isinstance(data["portions"], int) or data["portions"] < 1:
                errors.append("portions doit être >= 1")

        # Validation statut
        if "statut" in data:
            statuts_valides = ["planifié", "préparé", "terminé", "annulé"]
            if data["statut"] not in statuts_valides:
                errors.append(f"statut doit être dans {statuts_valides}")

        if errors:
            raise ValueError(f"Validation repas échouée: {', '.join(errors)}")


# ═══════════════════════════════════════════════════════════
# INSTANCE GLOBALE
# ═══════════════════════════════════════════════════════════

repas_service = RepasService()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = ["RepasService", "repas_service"]