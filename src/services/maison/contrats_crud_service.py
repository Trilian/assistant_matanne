"""
Service CRUD Contrats Maison.

Gestion des contrats (assurance, énergie, box internet, etc.)
avec alertes de renouvellement.
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.contrats_artisans import Contrat
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ContratsCrudService(EventBusMixin, BaseService[Contrat]):
    """Service CRUD pour les contrats maison."""

    _event_source = "contrats"

    def __init__(self):
        super().__init__(model=Contrat, cache_ttl=300)

    @chronometre("maison.contrats.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_contrats(
        self,
        filtre_type: str | None = None,
        filtre_statut: str | None = None,
        db: Session | None = None,
    ) -> list[Contrat]:
        """Récupère tous les contrats avec filtres optionnels."""
        query = db.query(Contrat)
        if filtre_type:
            query = query.filter(Contrat.type_contrat == filtre_type)
        if filtre_statut:
            query = query.filter(Contrat.statut == filtre_statut)
        return query.order_by(Contrat.date_renouvellement).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_contrat_by_id(self, contrat_id: int, db: Session | None = None) -> Contrat | None:
        """Récupère un contrat par son ID."""
        return db.query(Contrat).filter(Contrat.id == contrat_id).first()

    @avec_session_db
    def create_contrat(self, data: dict, db: Session | None = None) -> Contrat:
        """Crée un nouveau contrat."""
        contrat = Contrat(**data)
        db.add(contrat)
        db.commit()
        db.refresh(contrat)
        logger.info(f"Contrat créé: {contrat.id} - {contrat.nom}")
        self._emettre_evenement(
            "contrats.modifie",
            {"contrat_id": contrat.id, "nom": contrat.nom, "action": "cree"},
        )
        return contrat

    @avec_session_db
    def update_contrat(
        self, contrat_id: int, data: dict, db: Session | None = None
    ) -> Contrat | None:
        """Met à jour un contrat existant."""
        contrat = db.query(Contrat).filter(Contrat.id == contrat_id).first()
        if contrat is None:
            return None
        for key, value in data.items():
            setattr(contrat, key, value)
        db.commit()
        db.refresh(contrat)
        logger.info(f"Contrat {contrat_id} mis à jour")
        self._emettre_evenement(
            "contrats.modifie",
            {"contrat_id": contrat_id, "nom": contrat.nom, "action": "modifie"},
        )
        return contrat

    @avec_session_db
    def delete_contrat(self, contrat_id: int, db: Session | None = None) -> bool:
        """Supprime un contrat."""
        contrat = db.query(Contrat).filter(Contrat.id == contrat_id).first()
        if contrat is None:
            return False
        nom = contrat.nom
        db.delete(contrat)
        db.commit()
        logger.info(f"Contrat {contrat_id} supprimé")
        self._emettre_evenement(
            "contrats.modifie",
            {"contrat_id": contrat_id, "nom": nom, "action": "supprime"},
        )
        return True

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_alertes_contrats(
        self, jours_horizon: int = 60, db: Session | None = None
    ) -> list[dict]:
        """Récupère les contrats nécessitant attention (renouvellement proche)."""
        date_limite = date.today() + timedelta(days=jours_horizon)
        contrats = (
            db.query(Contrat)
            .filter(
                Contrat.statut == "actif",
                Contrat.alerte_active.is_(True),
                Contrat.date_renouvellement.isnot(None),
                Contrat.date_renouvellement <= date_limite,
            )
            .order_by(Contrat.date_renouvellement)
            .all()
        )
        alertes = []
        for c in contrats:
            jours_restants = (c.date_renouvellement - date.today()).days
            alertes.append(
                {
                    "contrat_id": c.id,
                    "nom": c.nom,
                    "type_contrat": c.type_contrat,
                    "date_echeance": c.date_renouvellement,
                    "jours_restants": jours_restants,
                    "action": "résilier" if c.tacite_reconduction else "renouveler",
                }
            )
        return alertes

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def get_resume_financier(self, db: Session | None = None) -> dict:
        """Calcule le résumé financier des contrats actifs."""
        contrats = db.query(Contrat).filter(Contrat.statut == "actif").all()
        total_mensuel = sum(float(c.montant_mensuel or 0) for c in contrats)
        total_annuel = sum(
            float(c.montant_annuel or c.montant_mensuel * 12 if c.montant_mensuel else 0)
            for c in contrats
        )
        par_type: dict = {}
        for c in contrats:
            t = c.type_contrat
            if t not in par_type:
                par_type[t] = {"count": 0, "total_mensuel": 0.0}
            par_type[t]["count"] += 1
            par_type[t]["total_mensuel"] += float(c.montant_mensuel or 0)
        return {
            "nb_contrats": len(contrats),
            "total_mensuel": total_mensuel,
            "total_annuel": total_annuel,
            "par_type": par_type,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("contrats_crud", tags={"maison", "crud", "contrats"})
def get_contrats_crud_service() -> ContratsCrudService:
    """Factory singleton pour le service CRUD contrats."""
    return ContratsCrudService()


def obtenir_service_contrats_crud() -> ContratsCrudService:
    """Factory française pour le service CRUD contrats."""
    return get_contrats_crud_service()
