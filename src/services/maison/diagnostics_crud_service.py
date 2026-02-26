"""
Service CRUD Diagnostics Maison & Estimations Immobilières.

Carnet de santé de la maison (DPE, diagnostics) et estimation via DVF.
"""

import logging
from datetime import date, timedelta

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.maison_extensions import DiagnosticMaison, EstimationImmobiliere
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

# Durées de validité par type de diagnostic (en années)
VALIDITE_DIAGNOSTICS: dict[str, int] = {
    "dpe": 10,
    "amiante": 0,  # Illimité si négatif
    "plomb": 0,  # Illimité si négatif, 1 an si positif (vente), 6 ans (location)
    "termites": 0,  # 6 mois (vente uniquement)
    "electricite": 6,
    "gaz": 6,
    "erp": 0,  # 6 mois
    "assainissement": 3,
    "surface_carrez": 0,  # Illimité sauf travaux
    "audit_energetique": 5,
}


class DiagnosticsCrudService(EventBusMixin, BaseService[DiagnosticMaison]):
    """Service CRUD pour les diagnostics immobiliers."""

    _event_source = "diagnostics"

    def __init__(self):
        super().__init__(model=DiagnosticMaison, cache_ttl=300)

    @chronometre("maison.diagnostics.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_diagnostics(
        self,
        filtre_type: str | None = None,
        db: Session | None = None,
    ) -> list[DiagnosticMaison]:
        """Récupère tous les diagnostics."""
        query = db.query(DiagnosticMaison)
        if filtre_type:
            query = query.filter(DiagnosticMaison.type_diagnostic == filtre_type)
        return query.order_by(DiagnosticMaison.date_validite).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_diagnostic_by_id(
        self, diagnostic_id: int, db: Session | None = None
    ) -> DiagnosticMaison | None:
        """Récupère un diagnostic par son ID."""
        return db.query(DiagnosticMaison).filter(DiagnosticMaison.id == diagnostic_id).first()

    @avec_session_db
    def create_diagnostic(self, data: dict, db: Session | None = None) -> DiagnosticMaison:
        """Crée un nouveau diagnostic."""
        diagnostic = DiagnosticMaison(**data)
        db.add(diagnostic)
        db.commit()
        db.refresh(diagnostic)
        logger.info(f"Diagnostic créé: {diagnostic.id} - {diagnostic.type_diagnostic}")
        self._emettre_evenement(
            "diagnostics.modifie",
            {"diagnostic_id": diagnostic.id, "type": diagnostic.type_diagnostic, "action": "cree"},
        )
        return diagnostic

    @avec_session_db
    def update_diagnostic(
        self, diagnostic_id: int, data: dict, db: Session | None = None
    ) -> DiagnosticMaison | None:
        """Met à jour un diagnostic."""
        diagnostic = db.query(DiagnosticMaison).filter(DiagnosticMaison.id == diagnostic_id).first()
        if diagnostic is None:
            return None
        for key, value in data.items():
            setattr(diagnostic, key, value)
        db.commit()
        db.refresh(diagnostic)
        return diagnostic

    @avec_session_db
    def delete_diagnostic(self, diagnostic_id: int, db: Session | None = None) -> bool:
        """Supprime un diagnostic."""
        diagnostic = db.query(DiagnosticMaison).filter(DiagnosticMaison.id == diagnostic_id).first()
        if diagnostic is None:
            return False
        db.delete(diagnostic)
        db.commit()
        return True

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_alertes_validite(
        self, jours_horizon: int = 90, db: Session | None = None
    ) -> list[dict]:
        """Récupère les diagnostics expirant bientôt."""
        date_limite = date.today() + timedelta(days=jours_horizon)
        diags = (
            db.query(DiagnosticMaison)
            .filter(
                DiagnosticMaison.alerte_active.is_(True),
                DiagnosticMaison.date_validite.isnot(None),
                DiagnosticMaison.date_validite <= date_limite,
            )
            .order_by(DiagnosticMaison.date_validite)
            .all()
        )
        return [
            {
                "diagnostic_id": d.id,
                "type": d.type_diagnostic,
                "date_validite": d.date_validite,
                "jours_restants": (d.date_validite - date.today()).days,
                "expire": d.date_validite < date.today(),
            }
            for d in diags
        ]

    def get_validite_par_type(self) -> dict[str, int]:
        """Retourne les durées de validité connues par type."""
        return VALIDITE_DIAGNOSTICS.copy()


# ═══════════════════════════════════════════════════════════
# ESTIMATIONS IMMOBILIÈRES
# ═══════════════════════════════════════════════════════════


class EstimationsCrudService(EventBusMixin, BaseService[EstimationImmobiliere]):
    """Service CRUD pour les estimations immobilières."""

    _event_source = "estimations"

    def __init__(self):
        super().__init__(model=EstimationImmobiliere, cache_ttl=600)

    @avec_cache(ttl=600)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_estimations(self, db: Session | None = None) -> list[EstimationImmobiliere]:
        """Récupère toutes les estimations."""
        return (
            db.query(EstimationImmobiliere)
            .order_by(EstimationImmobiliere.date_estimation.desc())
            .all()
        )

    @avec_session_db
    def create_estimation(self, data: dict, db: Session | None = None) -> EstimationImmobiliere:
        """Crée une nouvelle estimation."""
        estimation = EstimationImmobiliere(**data)
        db.add(estimation)
        db.commit()
        db.refresh(estimation)
        logger.info(f"Estimation créée: {estimation.id} - {estimation.valeur_moyenne}")
        return estimation

    @avec_session_db
    def delete_estimation(self, estimation_id: int, db: Session | None = None) -> bool:
        """Supprime une estimation."""
        estimation = (
            db.query(EstimationImmobiliere)
            .filter(EstimationImmobiliere.id == estimation_id)
            .first()
        )
        if estimation is None:
            return False
        db.delete(estimation)
        db.commit()
        return True

    @avec_cache(ttl=600)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_derniere_estimation(self, db: Session | None = None) -> EstimationImmobiliere | None:
        """Retourne la dernière estimation en date."""
        return (
            db.query(EstimationImmobiliere)
            .order_by(EstimationImmobiliere.date_estimation.desc())
            .first()
        )


# ═══════════════════════════════════════════════════════════
# FACTORIES
# ═══════════════════════════════════════════════════════════


@service_factory("diagnostics_crud", tags={"maison", "crud", "diagnostics"})
def get_diagnostics_crud_service() -> DiagnosticsCrudService:
    """Factory singleton pour le service CRUD diagnostics."""
    return DiagnosticsCrudService()


@service_factory("estimations_crud", tags={"maison", "crud", "estimations"})
def get_estimations_crud_service() -> EstimationsCrudService:
    """Factory singleton pour le service CRUD estimations."""
    return EstimationsCrudService()


def obtenir_service_diagnostics_crud() -> DiagnosticsCrudService:
    """Factory française pour le service CRUD diagnostics."""
    return get_diagnostics_crud_service()


def obtenir_service_estimations_crud() -> EstimationsCrudService:
    """Factory française pour le service CRUD estimations."""
    return get_estimations_crud_service()
