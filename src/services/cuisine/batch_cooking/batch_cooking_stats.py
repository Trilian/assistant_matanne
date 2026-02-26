"""
Mixin préparations et planning pour le batch cooking.

Regroupe les méthodes de gestion des préparations stockées
et d'intégration avec le planning hebdomadaire :
- CRUD des préparations (frigo/congélateur)
- Alertes de péremption
- Attribution automatique des préparations aux repas du planning
"""

import logging
from datetime import date, timedelta
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.core.caching import obtenir_cache
from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.exceptions import ErreurNonTrouve
from src.core.models import (
    Planning,
    PreparationBatch,
    SessionBatchCooking,
)

logger = logging.getLogger(__name__)


class BatchCookingStatsMixin:
    """Mixin pour les préparations stockées et l'intégration planning.

    Fournit :
    - Gestion des préparations (création, consommation, alertes péremption)
    - Attribution automatique des préparations aux repas du planning
    """

    # ═══════════════════════════════════════════════════════════
    # PRÉPARATIONS STOCKÉES
    # ═══════════════════════════════════════════════════════════

    @avec_cache(
        ttl=600,
        key_func=lambda self, consommees=False, localisation=None: (
            f"preparations_{consommees}_{localisation}"
        ),
    )
    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_preparations(
        self,
        consommees: bool = False,
        localisation: str | None = None,
        db: Session | None = None,
    ) -> list[PreparationBatch]:
        """Récupère les préparations stockées."""
        query = db.query(PreparationBatch).filter(PreparationBatch.consomme == consommees)

        if localisation:
            query = query.filter(PreparationBatch.localisation == localisation)

        return query.order_by(PreparationBatch.date_peremption).all()

    @avec_gestion_erreurs(default_return=[])
    @avec_session_db
    def get_preparations_alertes(self, db: Session | None = None) -> list[PreparationBatch]:
        """Récupère les préparations proches de la péremption."""
        limite = date.today() + timedelta(days=3)
        return (
            db.query(PreparationBatch)
            .filter(
                not PreparationBatch.consomme,
                PreparationBatch.date_peremption <= limite,
            )
            .order_by(PreparationBatch.date_peremption)
            .all()
        )

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_preparation(
        self,
        nom: str,
        portions: int,
        date_preparation: date,
        conservation_jours: int,
        localisation: str = "frigo",
        session_id: int | None = None,
        recette_id: int | None = None,
        container: str | None = None,
        notes: str | None = None,
        db: Session | None = None,
    ) -> PreparationBatch | None:
        """Crée une nouvelle préparation stockée."""
        preparation = PreparationBatch(
            session_id=session_id,
            recette_id=recette_id,
            nom=nom,
            portions_initiales=portions,
            portions_restantes=portions,
            date_preparation=date_preparation,
            date_peremption=date_preparation + timedelta(days=conservation_jours),
            localisation=localisation,
            container=container,
            notes=notes,
        )

        db.add(preparation)
        db.commit()
        db.refresh(preparation)

        # Invalider cache
        obtenir_cache().invalidate(pattern="preparations")

        logger.info(f"✅ Préparation créée: {preparation.id}")
        return preparation

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def consommer_preparation(
        self,
        preparation_id: int,
        portions: int = 1,
        db: Session | None = None,
    ) -> PreparationBatch | None:
        """Consomme des portions d'une préparation."""
        preparation = db.query(PreparationBatch).filter_by(id=preparation_id).first()
        if not preparation:
            raise ErreurNonTrouve(f"Préparation {preparation_id} non trouvée")

        preparation.consommer_portion(portions)

        db.commit()
        db.refresh(preparation)

        # Invalider cache
        obtenir_cache().invalidate(pattern="preparations")

        logger.info(f"✅ {portions} portion(s) consommée(s): {preparation_id}")
        return preparation

    # ═══════════════════════════════════════════════════════════
    # INTÉGRATION PLANNING
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def attribuer_preparations_planning(
        self,
        session_id: int,
        db: Session | None = None,
    ) -> dict[str, Any] | None:
        """Attribue automatiquement les préparations aux repas du planning."""
        session = (
            db.query(SessionBatchCooking)
            .options(joinedload(SessionBatchCooking.preparations))
            .filter_by(id=session_id)
            .first()
        )
        if not session or not session.planning_id:
            return None

        planning = (
            db.query(Planning)
            .options(joinedload(Planning.repas))
            .filter_by(id=session.planning_id)
            .first()
        )
        if not planning:
            return None

        # Attribuer les préparations aux repas
        attributions = []
        for preparation in session.preparations:
            if preparation.consomme:
                continue

            # Trouver les repas sans recette
            repas_libres = [r for r in planning.repas if not r.recette_id and not r.notes]

            # Attribuer à des repas
            nb_attribue = min(preparation.portions_restantes, len(repas_libres))
            for _i, repas in enumerate(repas_libres[:nb_attribue]):
                repas.notes = f"🍱 {preparation.nom}"

                if preparation.repas_attribues is None:
                    preparation.repas_attribues = []
                preparation.repas_attribues.append(repas.id)

                attributions.append(
                    {
                        "preparation": preparation.nom,
                        "repas_id": repas.id,
                        "date": repas.date_repas.isoformat(),
                    }
                )

        db.commit()

        logger.info(f"✅ {len(attributions)} attributions créées")
        return {
            "session_id": session_id,
            "planning_id": planning.id,
            "attributions": attributions,
        }
