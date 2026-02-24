"""
Service Accueil Data.

Centralise les accès base de données pour le module accueil/dashboard.
"""

import logging
from datetime import date

from sqlalchemy.orm import Session

from src.core.decorators import avec_gestion_erreurs, avec_session_db
from src.core.models import TacheEntretien
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class AccueilDataService:
    """Service de données pour le dashboard accueil."""

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_taches_en_retard(self, limit: int = 10, db: Session | None = None) -> list[dict]:
        """Récupère les tâches ménage en retard.

        Returns:
            Liste de dicts avec nom, prochaine_fois, jours_retard
        """
        taches = (
            db.query(TacheEntretien)
            .filter(
                TacheEntretien.prochaine_fois < date.today(),
                TacheEntretien.fait.is_(False),
            )
            .limit(limit)
            .all()
        )

        return [
            {
                "nom": t.nom,
                "prochaine_fois": t.prochaine_fois,
                "jours_retard": (date.today() - t.prochaine_fois).days,
            }
            for t in taches
        ]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("accueil_data", tags={"accueil", "data"})
def get_accueil_data_service() -> AccueilDataService:
    """Factory singleton pour le service accueil data."""
    return AccueilDataService()


def obtenir_service_accueil_data() -> AccueilDataService:
    """Factory française pour le service accueil data."""
    return get_accueil_data_service()
