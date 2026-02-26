"""
Service CRUD Garanties & SAV.

Suivi des garanties appareils avec alertes et historique incidents.
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.contrats_artisans import Garantie, IncidentSAV
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class GarantiesCrudService(EventBusMixin, BaseService[Garantie]):
    """Service CRUD pour les garanties et incidents SAV."""

    _event_source = "garanties"

    def __init__(self):
        super().__init__(model=Garantie, cache_ttl=300)

    @chronometre("maison.garanties.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_garanties(
        self,
        filtre_statut: str | None = None,
        filtre_piece: str | None = None,
        db: Session | None = None,
    ) -> list[Garantie]:
        """Récupère toutes les garanties."""
        query = db.query(Garantie)
        if filtre_statut:
            query = query.filter(Garantie.statut == filtre_statut)
        if filtre_piece:
            query = query.filter(Garantie.piece == filtre_piece)
        return query.order_by(Garantie.date_fin_garantie).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_garantie_by_id(self, garantie_id: int, db: Session | None = None) -> Garantie | None:
        """Récupère une garantie par son ID."""
        return db.query(Garantie).filter(Garantie.id == garantie_id).first()

    @avec_session_db
    def create_garantie(self, data: dict, db: Session | None = None) -> Garantie:
        """Crée une nouvelle garantie."""
        garantie = Garantie(**data)
        db.add(garantie)
        db.commit()
        db.refresh(garantie)
        logger.info(f"Garantie créée: {garantie.id} - {garantie.nom_appareil}")
        self._emettre_evenement(
            "garanties.modifie",
            {"garantie_id": garantie.id, "nom": garantie.nom_appareil, "action": "cree"},
        )
        return garantie

    @avec_session_db
    def update_garantie(
        self, garantie_id: int, data: dict, db: Session | None = None
    ) -> Garantie | None:
        """Met à jour une garantie."""
        garantie = db.query(Garantie).filter(Garantie.id == garantie_id).first()
        if garantie is None:
            return None
        for key, value in data.items():
            setattr(garantie, key, value)
        db.commit()
        db.refresh(garantie)
        logger.info(f"Garantie {garantie_id} mise à jour")
        self._emettre_evenement(
            "garanties.modifie",
            {"garantie_id": garantie_id, "nom": garantie.nom_appareil, "action": "modifie"},
        )
        return garantie

    @avec_session_db
    def delete_garantie(self, garantie_id: int, db: Session | None = None) -> bool:
        """Supprime une garantie et ses incidents."""
        garantie = db.query(Garantie).filter(Garantie.id == garantie_id).first()
        if garantie is None:
            return False
        nom = garantie.nom_appareil
        db.delete(garantie)
        db.commit()
        logger.info(f"Garantie {garantie_id} supprimée")
        self._emettre_evenement(
            "garanties.modifie",
            {"garantie_id": garantie_id, "nom": nom, "action": "supprime"},
        )
        return True

    # ── Incidents SAV ──

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_incidents(self, garantie_id: int, db: Session | None = None) -> list[IncidentSAV]:
        """Récupère les incidents d'une garantie."""
        return (
            db.query(IncidentSAV)
            .filter(IncidentSAV.garantie_id == garantie_id)
            .order_by(IncidentSAV.date_incident.desc())
            .all()
        )

    @avec_session_db
    def create_incident(self, data: dict, db: Session | None = None) -> IncidentSAV:
        """Crée un incident SAV."""
        incident = IncidentSAV(**data)
        db.add(incident)
        db.commit()
        db.refresh(incident)
        logger.info(f"Incident SAV créé: {incident.id}")
        return incident

    @avec_session_db
    def update_incident(
        self, incident_id: int, data: dict, db: Session | None = None
    ) -> IncidentSAV | None:
        """Met à jour un incident."""
        incident = db.query(IncidentSAV).filter(IncidentSAV.id == incident_id).first()
        if incident is None:
            return None
        for key, value in data.items():
            setattr(incident, key, value)
        db.commit()
        db.refresh(incident)
        return incident

    # ── Alertes ──

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_alertes_garanties(
        self, jours_horizon: int = 60, db: Session | None = None
    ) -> list[dict]:
        """Récupère les garanties expirant bientôt."""
        date_limite = date.today() + timedelta(days=jours_horizon)
        garanties = (
            db.query(Garantie)
            .filter(
                Garantie.statut == "active",
                Garantie.alerte_active.is_(True),
                Garantie.date_fin_garantie <= date_limite,
                Garantie.date_fin_garantie >= date.today(),
            )
            .order_by(Garantie.date_fin_garantie)
            .all()
        )
        return [
            {
                "garantie_id": g.id,
                "nom_appareil": g.nom_appareil,
                "date_fin_garantie": g.date_fin_garantie,
                "jours_restants": (g.date_fin_garantie - date.today()).days,
                "garantie_etendue": g.garantie_etendue,
            }
            for g in garanties
        ]

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def get_stats_garanties(self, db: Session | None = None) -> dict:
        """Statistiques globales des garanties."""
        garanties = db.query(Garantie).all()
        actives = [g for g in garanties if g.statut == "active"]
        expirees = [g for g in garanties if g.date_fin_garantie < date.today()]
        total_valeur = sum(float(g.prix_achat or 0) for g in garanties)
        return {
            "nb_total": len(garanties),
            "nb_actives": len(actives),
            "nb_expirees": len(expirees),
            "total_valeur_achats": total_valeur,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("garanties_crud", tags={"maison", "crud", "garanties"})
def get_garanties_crud_service() -> GarantiesCrudService:
    """Factory singleton pour le service CRUD garanties."""
    return GarantiesCrudService()


def obtenir_service_garanties_crud() -> GarantiesCrudService:
    """Factory française pour le service CRUD garanties."""
    return get_garanties_crud_service()
