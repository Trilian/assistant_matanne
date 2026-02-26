"""
Service CRUD Artisans.

Carnet d'adresses artisans avec historique d'interventions.
"""

import logging

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models.contrats_artisans import Artisan, InterventionArtisan
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ArtisansCrudService(EventBusMixin, BaseService[Artisan]):
    """Service CRUD pour les artisans et interventions."""

    _event_source = "artisans"

    def __init__(self):
        super().__init__(model=Artisan, cache_ttl=300)

    @chronometre("maison.artisans.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_artisans(
        self,
        filtre_metier: str | None = None,
        db: Session | None = None,
    ) -> list[Artisan]:
        """Récupère tous les artisans avec filtre optionnel par métier."""
        query = db.query(Artisan)
        if filtre_metier:
            query = query.filter(Artisan.metier == filtre_metier)
        return query.order_by(Artisan.nom).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_artisan_by_id(self, artisan_id: int, db: Session | None = None) -> Artisan | None:
        """Récupère un artisan par son ID."""
        return db.query(Artisan).filter(Artisan.id == artisan_id).first()

    @avec_session_db
    def create_artisan(self, data: dict, db: Session | None = None) -> Artisan:
        """Crée un nouvel artisan."""
        artisan = Artisan(**data)
        db.add(artisan)
        db.commit()
        db.refresh(artisan)
        logger.info(f"Artisan créé: {artisan.id} - {artisan.nom}")
        self._emettre_evenement(
            "artisans.modifie",
            {"artisan_id": artisan.id, "nom": artisan.nom, "action": "cree"},
        )
        return artisan

    @avec_session_db
    def update_artisan(
        self, artisan_id: int, data: dict, db: Session | None = None
    ) -> Artisan | None:
        """Met à jour un artisan existant."""
        artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
        if artisan is None:
            return None
        for key, value in data.items():
            setattr(artisan, key, value)
        db.commit()
        db.refresh(artisan)
        logger.info(f"Artisan {artisan_id} mis à jour")
        self._emettre_evenement(
            "artisans.modifie",
            {"artisan_id": artisan_id, "nom": artisan.nom, "action": "modifie"},
        )
        return artisan

    @avec_session_db
    def delete_artisan(self, artisan_id: int, db: Session | None = None) -> bool:
        """Supprime un artisan et ses interventions."""
        artisan = db.query(Artisan).filter(Artisan.id == artisan_id).first()
        if artisan is None:
            return False
        nom = artisan.nom
        db.delete(artisan)
        db.commit()
        logger.info(f"Artisan {artisan_id} supprimé")
        self._emettre_evenement(
            "artisans.modifie",
            {"artisan_id": artisan_id, "nom": nom, "action": "supprime"},
        )
        return True

    # ── Interventions ──

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_interventions(
        self, artisan_id: int, db: Session | None = None
    ) -> list[InterventionArtisan]:
        """Récupère les interventions d'un artisan."""
        return (
            db.query(InterventionArtisan)
            .filter(InterventionArtisan.artisan_id == artisan_id)
            .order_by(InterventionArtisan.date_intervention.desc())
            .all()
        )

    @avec_session_db
    def create_intervention(self, data: dict, db: Session | None = None) -> InterventionArtisan:
        """Crée une nouvelle intervention."""
        intervention = InterventionArtisan(**data)
        db.add(intervention)
        db.commit()
        db.refresh(intervention)
        logger.info(f"Intervention créée: {intervention.id}")
        self._emettre_evenement(
            "artisans.intervention",
            {
                "intervention_id": intervention.id,
                "artisan_id": data["artisan_id"],
                "action": "cree",
            },
        )
        return intervention

    @avec_session_db
    def delete_intervention(self, intervention_id: int, db: Session | None = None) -> bool:
        """Supprime une intervention."""
        intervention = (
            db.query(InterventionArtisan).filter(InterventionArtisan.id == intervention_id).first()
        )
        if intervention is None:
            return False
        db.delete(intervention)
        db.commit()
        return True

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def get_stats_artisans(self, db: Session | None = None) -> dict:
        """Statistiques globales artisans."""
        artisans = db.query(Artisan).all()
        interventions = db.query(InterventionArtisan).all()
        total_depense = sum(float(i.montant_facture or 0) for i in interventions)
        par_metier: dict = {}
        for a in artisans:
            par_metier[a.metier] = par_metier.get(a.metier, 0) + 1
        return {
            "nb_artisans": len(artisans),
            "nb_interventions": len(interventions),
            "total_depense": total_depense,
            "par_metier": par_metier,
        }


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("artisans_crud", tags={"maison", "crud", "artisans"})
def get_artisans_crud_service() -> ArtisansCrudService:
    """Factory singleton pour le service CRUD artisans."""
    return ArtisansCrudService()


def obtenir_service_artisans_crud() -> ArtisansCrudService:
    """Factory française pour le service CRUD artisans."""
    return get_artisans_crud_service()
