"""
Service Événements Familiaux - Calendrier partagé avec récurrences.

Opérations:
- CRUD événements familiaux
- Événements par période (semaine, mois)
- Gestion des récurrences
- Filtrage par type
"""

import logging
from datetime import date as date_type
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import EvenementFamilial
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)

TYPES_EVENEMENTS = [
    "famille",
    "medical",
    "scolaire",
    "loisir",
    "administratif",
    "couple",
]


class ServiceEvenements(BaseService[EvenementFamilial]):
    """Service de gestion du calendrier familial.

    Hérite de BaseService[EvenementFamilial] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=EvenementFamilial, cache_ttl=300)

    # ═══════════════════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════════════════

    @chronometre("evenements.semaine", seuil_alerte_ms=1000)
    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_evenements_semaine(
        self,
        *,
        date_ref: date_type | None = None,
        db: Session | None = None,
    ) -> list[EvenementFamilial]:
        """Récupère les événements de la semaine."""
        if db is None:
            return []
        ref = date_ref or date_type.today()
        debut_semaine = ref - timedelta(days=ref.weekday())
        fin_semaine = debut_semaine + timedelta(days=6, hours=23, minutes=59)
        return (
            db.query(EvenementFamilial)
            .filter(
                and_(
                    EvenementFamilial.date_debut
                    >= datetime.combine(debut_semaine, datetime.min.time()),
                    EvenementFamilial.date_debut
                    <= datetime.combine(fin_semaine, datetime.max.time()),
                )
            )
            .order_by(EvenementFamilial.date_debut.asc())
            .all()
        )

    @chronometre("evenements.mois", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_evenements_mois(
        self,
        *,
        annee: int | None = None,
        mois: int | None = None,
        db: Session | None = None,
    ) -> list[EvenementFamilial]:
        """Récupère les événements d'un mois donné."""
        if db is None:
            return []
        aujourd_hui = date_type.today()
        a = annee or aujourd_hui.year
        m = mois or aujourd_hui.month

        from calendar import monthrange

        _, dernier_jour = monthrange(a, m)
        debut = datetime(a, m, 1)
        fin = datetime(a, m, dernier_jour, 23, 59, 59)

        return (
            db.query(EvenementFamilial)
            .filter(
                and_(
                    EvenementFamilial.date_debut >= debut,
                    EvenementFamilial.date_debut <= fin,
                )
            )
            .order_by(EvenementFamilial.date_debut.asc())
            .all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_evenement(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> EvenementFamilial | None:
        """Ajoute un événement familial."""
        if db is None:
            return None
        evt = EvenementFamilial(**data)
        db.add(evt)
        db.commit()
        db.refresh(evt)
        logger.info("Événement ajouté: %s le %s", evt.titre, evt.date_debut)
        obtenir_bus().emettre(
            "evenements.ajoute",
            {"evenement_id": evt.id, "titre": evt.titre},
            source="ServiceEvenements",
        )
        return evt

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def modifier_evenement(
        self, evenement_id: int, data: dict[str, Any], *, db: Session | None = None
    ) -> bool:
        """Modifie un événement existant."""
        if db is None:
            return False
        evt = db.query(EvenementFamilial).get(evenement_id)
        if not evt:
            return False
        for key, value in data.items():
            if hasattr(evt, key):
                setattr(evt, key, value)
        db.commit()
        logger.info("Événement modifié: id=%d", evenement_id)
        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_evenement(self, evenement_id: int, *, db: Session | None = None) -> bool:
        """Supprime un événement."""
        if db is None:
            return False
        deleted = db.query(EvenementFamilial).filter_by(id=evenement_id).delete()
        db.commit()
        if deleted > 0:
            logger.info("Événement supprimé: id=%d", evenement_id)
        return deleted > 0

    # ═══════════════════════════════════════════════════════════
    # FILTRES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(ttl=300)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_par_type(
        self, type_evenement: str, *, db: Session | None = None
    ) -> list[EvenementFamilial]:
        """Filtre les événements par type."""
        if db is None:
            return []
        return (
            db.query(EvenementFamilial)
            .filter_by(type_evenement=type_evenement)
            .order_by(EvenementFamilial.date_debut.desc())
            .all()
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("evenements_familiaux", tags={"famille", "calendrier"})
def obtenir_service_evenements() -> ServiceEvenements:
    """Factory pour le service événements familiaux (singleton via ServiceRegistry)."""
    return ServiceEvenements()


# Alias anglais
get_evenements_service = obtenir_service_evenements
