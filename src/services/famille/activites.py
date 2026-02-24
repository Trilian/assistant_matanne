"""
Service Activités Famille - Logique métier pour les activités familiales.

Hérite de BaseService[ActiviteFamille] pour CRUD générique + méthodes spécialisées.

Opérations:
- CRUD activités (planification, marquage terminé)
- Statistiques et budget
"""

import logging
from datetime import date as date_type

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ActiviteFamille
from src.services.core.base import BaseService
from src.services.core.events.bus import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class ServiceActivites(BaseService[ActiviteFamille]):
    """Service de gestion des activités familiales.

    Hérite de BaseService[ActiviteFamille] pour le CRUD générique.
    Les méthodes spécialisées gèrent la logique métier spécifique.
    """

    def __init__(self):
        super().__init__(model=ActiviteFamille, cache_ttl=300)

    # ═══════════════════════════════════════════════════════════
    # CRUD
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_activite(
        self,
        titre: str,
        type_activite: str,
        date_prevue: date_type,
        duree: float,
        lieu: str,
        participants: list,
        cout_estime: float,
        notes: str = "",
        db: Session | None = None,
    ) -> ActiviteFamille:
        """Ajoute une nouvelle activité familiale.

        Args:
            titre: Titre de l'activité.
            type_activite: Type (parc, musée, etc.).
            date_prevue: Date planifiée.
            duree: Durée en heures.
            lieu: Lieu de l'activité.
            participants: Liste des participants.
            cout_estime: Coût estimé en euros.
            notes: Notes optionnelles.
            db: Session DB (injectée automatiquement).

        Returns:
            L'activité créée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        activity = ActiviteFamille(
            titre=titre,
            type_activite=type_activite,
            date_prevue=date_prevue,
            duree_heures=duree,
            lieu=lieu,
            qui_participe=participants,
            cout_estime=cout_estime,
            statut="planifie",
            notes=notes,
        )
        db.add(activity)
        db.commit()
        logger.info("Activité créée: %s (id=%d)", titre, activity.id)
        obtenir_bus().emettre(
            "activites.cree",
            {"id": activity.id, "titre": titre, "date": date_prevue.isoformat()},
            source="ServiceActivites",
        )
        return activity

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def marquer_terminee(
        self,
        activity_id: int,
        cout_reel: float | None = None,
        notes: str = "",
        db: Session | None = None,
    ) -> bool:
        """Marque une activité comme terminée.

        Args:
            activity_id: ID de l'activité.
            cout_reel: Coût réel (optionnel).
            notes: Notes de retour (optionnel).
            db: Session DB (injectée automatiquement).

        Returns:
            True si l'activité a été trouvée et mise à jour.
        """
        if db is None:
            raise ValueError("Session DB requise")
        activity = db.get(ActiviteFamille, activity_id)
        if activity:
            activity.statut = "termine"
            if cout_reel is not None:
                activity.cout_reel = cout_reel
            db.commit()
            logger.info("Activité terminée: id=%d", activity_id)
            obtenir_bus().emettre(
                "activites.terminee", {"id": activity_id}, source="ServiceActivites"
            )
            return True
        return False

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def lister_activites(
        self,
        statut: str | None = None,
        type_activite: str | None = None,
        db: Session | None = None,
    ) -> list[ActiviteFamille]:
        """Liste les activités avec filtres optionnels.

        Args:
            statut: Filtrer par statut ('planifie', 'termine').
            type_activite: Filtrer par type d'activité.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des activités correspondantes.
        """
        if db is None:
            raise ValueError("Session DB requise")
        query = db.query(ActiviteFamille)
        if statut:
            query = query.filter(ActiviteFamille.statut == statut)
        if type_activite:
            query = query.filter(ActiviteFamille.type_activite == type_activite)
        return query.order_by(ActiviteFamille.date_prevue.desc()).all()

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def supprimer_activite(self, activity_id: int, db: Session | None = None) -> bool:
        """Supprime une activité.

        Args:
            activity_id: ID de l'activité.
            db: Session DB (injectée automatiquement).

        Returns:
            True si supprimée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        deleted = db.query(ActiviteFamille).filter(ActiviteFamille.id == activity_id).delete()
        db.commit()
        if deleted > 0:
            obtenir_bus().emettre(
                "activites.supprimee", {"id": activity_id}, source="ServiceActivites"
            )
        return deleted > 0


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("activites", tags={"famille", "crud"})
def obtenir_service_activites() -> ServiceActivites:
    """Factory pour le service activités (singleton via ServiceRegistry)."""
    return ServiceActivites()


# Alias anglais
get_activites_service = obtenir_service_activites
