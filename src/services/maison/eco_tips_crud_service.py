"""
Service CRUD Actions Écologiques.

Centralise tous les accès base de données pour les actions écologiques.
Pattern: BaseService[ActionEcologique] pour CRUD générique.
"""

import logging

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ActionEcologique
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.event_bus_mixin import EventBusMixin
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class EcoTipsCrudService(EventBusMixin, BaseService[ActionEcologique]):
    """Service CRUD pour les actions écologiques.

    Hérite de BaseService[ActionEcologique] pour le CRUD générique.
    Utilise EventBusMixin pour émettre des événements domaine.
    """

    _event_source = "eco_tips"

    def __init__(self):
        super().__init__(model=ActionEcologique, cache_ttl=300)

    @chronometre("maison.eco_tips.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=[])
    def get_all_actions(
        self,
        actif_only: bool = False,
        db: Session | None = None,
    ) -> list[ActionEcologique]:
        """Récupère toutes les actions écologiques.

        Args:
            actif_only: Ne retourner que les actions actives.
            db: Session DB optionnelle.

        Returns:
            Liste d'objets ActionEcologique.
        """
        query = db.query(ActionEcologique)
        if actif_only:
            query = query.filter(ActionEcologique.actif == True)  # noqa: E712
        return query.order_by(ActionEcologique.id).all()

    @avec_cache(ttl=300)
    @avec_session_db
    @avec_gestion_erreurs(default_return=None)
    def get_action_by_id(
        self, action_id: int, db: Session | None = None
    ) -> ActionEcologique | None:
        """Récupère une action par son ID.

        Args:
            action_id: ID de l'action.
            db: Session DB optionnelle.

        Returns:
            Objet ActionEcologique ou None.
        """
        return db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()

    @avec_session_db
    def create_action(self, data: dict, db: Session | None = None) -> ActionEcologique:
        """Crée une nouvelle action écologique.

        Args:
            data: Dict avec les champs de l'action.
            db: Session DB optionnelle.

        Returns:
            Objet ActionEcologique créé.
        """
        action = ActionEcologique(**data)
        db.add(action)
        db.commit()
        db.refresh(action)
        logger.info(f"Action écologique créée: {action.id} - {action.nom}")
        self._emettre_evenement(
            "eco_tips.modifie",
            {"action_id": action.id, "nom": action.nom, "action": "cree"},
        )
        return action

    @avec_session_db
    def update_action(
        self, action_id: int, data: dict, db: Session | None = None
    ) -> ActionEcologique | None:
        """Met à jour une action existante.

        Args:
            action_id: ID de l'action.
            data: Dict des champs à mettre à jour.
            db: Session DB optionnelle.

        Returns:
            Objet ActionEcologique mis à jour ou None si non trouvé.
        """
        action = db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()
        if action is None:
            return None
        for key, value in data.items():
            setattr(action, key, value)
        db.commit()
        db.refresh(action)
        logger.info(f"Action écologique {action_id} mise à jour")
        self._emettre_evenement(
            "eco_tips.modifie",
            {"action_id": action_id, "nom": action.nom, "action": "modifie"},
        )
        return action

    @avec_session_db
    def delete_action(self, action_id: int, db: Session | None = None) -> bool:
        """Supprime une action écologique.

        Args:
            action_id: ID de l'action.
            db: Session DB optionnelle.

        Returns:
            True si supprimée, False si non trouvée.
        """
        action = db.query(ActionEcologique).filter(ActionEcologique.id == action_id).first()
        if action is None:
            return False
        nom = action.nom
        db.delete(action)
        db.commit()
        logger.info(f"Action écologique {action_id} supprimée")
        self._emettre_evenement(
            "eco_tips.modifie",
            {"action_id": action_id, "nom": nom, "action": "supprime"},
        )
        return True


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("eco_tips_crud", tags={"maison", "crud", "eco_tips"})
def get_eco_tips_crud_service() -> EcoTipsCrudService:
    """Factory singleton pour le service CRUD actions écologiques."""
    return EcoTipsCrudService()


def obtenir_service_eco_tips_crud() -> EcoTipsCrudService:
    """Factory française pour le service CRUD actions écologiques."""
    return get_eco_tips_crud_service()
