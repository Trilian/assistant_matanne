"""
Service Hub Data Maison.

Centralise les accès base de données pour le hub maison
(statistiques globales, alertes objets urgents).
"""

import logging
from datetime import date, datetime

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ObjetMaison, PieceMaison
from src.core.models.temps_entretien import SessionTravail, ZoneJardin
from src.core.monitoring import chronometre
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class HubDataService:
    """Service de données pour le hub maison.

    Note (S12): Service read-heavy standalone sans BaseService[T] — acceptable
    car il ne fait que de la lecture agrégée, pas de CRUD standard.
    """

    @chronometre("maison.hub.stats_db", seuil_alerte_ms=2000)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return={})
    def obtenir_stats_db(self, db: Session | None = None) -> dict:
        """Récupère les statistiques depuis la base de données.

        Returns:
            dict avec zones_jardin, pieces, objets_a_changer, temps_mois_heures
        """
        stats = {
            "zones_jardin": db.query(ZoneJardin).count(),
            "pieces": db.query(PieceMaison).count(),
            "objets_a_changer": (
                db.query(ObjetMaison)
                .filter(ObjetMaison.statut.in_(["a_changer", "a_reparer"]))
                .count()
            ),
        }

        debut_mois = date.today().replace(day=1)
        sessions = (
            db.query(SessionTravail)
            .filter(SessionTravail.debut >= datetime.combine(debut_mois, datetime.min.time()))
            .all()
        )
        stats["temps_mois_heures"] = sum(s.duree_minutes or 0 for s in sessions) / 60

        return stats

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=0)
    def compter_objets_urgents(self, db: Session | None = None) -> int:
        """Compte les objets à remplacer en priorité urgente."""
        return (
            db.query(ObjetMaison)
            .filter(
                ObjetMaison.statut == "a_changer",
                ObjetMaison.priorite_remplacement == "urgente",
            )
            .count()
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("hub_data", tags={"maison", "data"})
def get_hub_data_service() -> HubDataService:
    """Factory singleton pour le service hub data."""
    return HubDataService()


def obtenir_service_hub_data() -> HubDataService:
    """Alias français pour get_hub_data_service."""
    return get_hub_data_service()
