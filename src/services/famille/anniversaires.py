"""
Service Anniversaires - Dates importantes, rappels et historique cadeaux.

Opérations:
- CRUD anniversaires avec calcul d'âge
- Prochains anniversaires avec compte à rebours
- Historique des cadeaux offerts
"""

import logging
from datetime import date as date_type
from typing import Any, TypedDict

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import AnniversaireFamille
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ProchainAnniversaireDict(TypedDict):
    """Prochain anniversaire avec informations calculées."""

    id: int
    nom: str
    relation: str | None
    date_naissance: str
    age: int
    jours_restants: int


class ServiceAnniversaires(BaseService[AnniversaireFamille]):
    """Service de gestion des anniversaires famille.

    Hérite de BaseService[AnniversaireFamille] pour le CRUD générique.
    """

    def __init__(self):
        super().__init__(model=AnniversaireFamille, cache_ttl=3600)

    # ═══════════════════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════════════════

    @chronometre("anniversaires.liste", seuil_alerte_ms=1000)
    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_anniversaires(self, *, db: Session | None = None) -> list[AnniversaireFamille]:
        """Récupère tous les anniversaires."""
        if db is None:
            return []
        return (
            db.query(AnniversaireFamille).order_by(AnniversaireFamille.date_naissance.asc()).all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_anniversaire(
        self, data: dict[str, Any], *, db: Session | None = None
    ) -> AnniversaireFamille | None:
        """Ajoute un anniversaire."""
        if db is None:
            return None
        anniversaire = AnniversaireFamille(**data)
        db.add(anniversaire)
        db.commit()
        db.refresh(anniversaire)
        logger.info("Anniversaire ajouté: %s", anniversaire.nom)
        obtenir_bus().emettre(
            "anniversaires.ajoute",
            {"anniversaire_id": anniversaire.id, "nom": anniversaire.nom},
            source="ServiceAnniversaires",
        )
        return anniversaire

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def modifier_anniversaire(
        self, anniversaire_id: int, data: dict[str, Any], *, db: Session | None = None
    ) -> bool:
        """Modifie un anniversaire existant."""
        if db is None:
            return False
        anniv = db.query(AnniversaireFamille).get(anniversaire_id)
        if not anniv:
            return False
        for key, value in data.items():
            if hasattr(anniv, key):
                setattr(anniv, key, value)
        db.commit()
        logger.info("Anniversaire modifié: id=%d", anniversaire_id)
        return True

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def supprimer_anniversaire(self, anniversaire_id: int, *, db: Session | None = None) -> bool:
        """Supprime un anniversaire."""
        if db is None:
            return False
        deleted = db.query(AnniversaireFamille).filter_by(id=anniversaire_id).delete()
        db.commit()
        return deleted > 0

    # ═══════════════════════════════════════════════════════════
    # PROCHAINS ANNIVERSAIRES
    # ═══════════════════════════════════════════════════════════

    @chronometre("anniversaires.prochains", seuil_alerte_ms=1000)
    @avec_cache(ttl=3600)
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def obtenir_prochains(
        self, *, jours: int = 90, db: Session | None = None
    ) -> list[ProchainAnniversaireDict]:
        """Récupère les anniversaires arrivant dans les prochains jours."""
        if db is None:
            return []
        tous = db.query(AnniversaireFamille).all()
        aujourd_hui = date_type.today()
        prochains: list[ProchainAnniversaireDict] = []

        for anniv in tous:
            jours_restants = anniv.jours_restants
            if jours_restants is not None and jours_restants <= jours:
                prochains.append(
                    ProchainAnniversaireDict(
                        id=anniv.id,
                        nom=anniv.nom,
                        relation=anniv.relation,
                        date_naissance=anniv.date_naissance.isoformat(),
                        age=anniv.age or 0,
                        jours_restants=jours_restants,
                    )
                )

        return sorted(prochains, key=lambda a: a["jours_restants"])

    # Compatibility aliases expected by older UI code
    def lister_prochains(self, *, limite: int = 90, db: Session | None = None):
        """Alias historique for `obtenir_prochains` (old callers expect `lister_prochains`)."""
        return self.obtenir_prochains(jours=limite, db=db)

    def lister_anniversaires(self, *, db: Session | None = None):
        """Alias for `obtenir_anniversaires` to support older callers."""
        return self.obtenir_anniversaires(db=db)

    # ═══════════════════════════════════════════════════════════
    # CADEAUX
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=False)
    @avec_session_db
    def ajouter_cadeau(
        self,
        anniversaire_id: int,
        annee: int,
        cadeau: str,
        *,
        db: Session | None = None,
    ) -> bool:
        """Ajoute un cadeau à l'historique d'un anniversaire."""
        if db is None:
            return False
        anniv = db.query(AnniversaireFamille).get(anniversaire_id)
        if not anniv:
            return False
        historique = list(anniv.historique_cadeaux or [])
        historique.append({"annee": annee, "cadeau": cadeau})
        anniv.historique_cadeaux = historique
        db.commit()
        logger.info("Cadeau ajouté pour %s: %s (%d)", anniv.nom, cadeau, annee)
        return True


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("anniversaires", tags={"famille"})
def obtenir_service_anniversaires() -> ServiceAnniversaires:
    """Factory pour le service anniversaires (singleton via ServiceRegistry)."""
    return ServiceAnniversaires()


# Alias anglais
get_anniversaires_service = obtenir_service_anniversaires
