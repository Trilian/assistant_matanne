"""
Service Weekend - Logique métier pour les sorties weekend.

Opérations:
- Planning des activités weekend (samedi/dimanche)
- Budget estimé et réel
- Lieux testés avec notes
- Ajout et notation des sorties
"""

import logging
from datetime import date as date_type
from datetime import timedelta
from typing import TypedDict

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ActiviteWeekend
from src.core.monitoring import chronometre
from src.services.core.base import BaseService
from src.services.core.events import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class BudgetWeekendDict(TypedDict):
    """Structure de données pour le budget weekend."""

    estime: float
    reel: float


class ServiceWeekend(BaseService[ActiviteWeekend]):
    """Service de gestion des activités weekend.

    Hérite de BaseService[ActiviteWeekend] pour le CRUD générique.
    Encapsule les opérations spécialisées et la logique métier
    liée aux sorties du weekend.
    """

    def __init__(self):
        super().__init__(model=ActiviteWeekend, cache_ttl=300)

    # ═══════════════════════════════════════════════════════════
    # UTILITAIRES
    # ═══════════════════════════════════════════════════════════

    @staticmethod
    def get_next_weekend() -> tuple[date_type, date_type]:
        """Calcule les dates du prochain weekend.

        Returns:
            Tuple (samedi, dimanche) du prochain weekend.
            Si on est samedi, retourne le weekend actuel.
            Si on est dimanche, retourne le weekend suivant.
        """
        today = date_type.today()
        days_until_saturday = (5 - today.weekday()) % 7

        if today.weekday() == 5:  # Samedi
            saturday = today
        elif today.weekday() == 6:  # Dimanche
            saturday = today + timedelta(days=6)  # Prochain samedi
        else:
            if days_until_saturday == 0:
                days_until_saturday = 7
            saturday = today + timedelta(days=days_until_saturday)

        sunday = saturday + timedelta(days=1)
        return saturday, sunday

    # ═══════════════════════════════════════════════════════════
    # LECTURE
    # ═══════════════════════════════════════════════════════════

    @chronometre("famille.weekend.lister", seuil_alerte_ms=1500)
    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def lister_activites_weekend(
        self, saturday: date_type, sunday: date_type, db: Session | None = None
    ) -> dict[str, list[ActiviteWeekend]]:
        """Récupère les activités du weekend par jour.

        Args:
            saturday: Date du samedi.
            sunday: Date du dimanche.
            db: Session DB (injectée automatiquement).

        Returns:
            Dictionnaire avec clés 'saturday' et 'sunday' contenant
            les listes d'activités triées par heure de début.
        """
        if db is None:
            raise ValueError("Session DB requise")
        activities = (
            db.query(ActiviteWeekend)
            .filter(ActiviteWeekend.date_prevue.in_([saturday, sunday]))
            .order_by(ActiviteWeekend.heure_debut)
            .all()
        )

        return {
            "saturday": [a for a in activities if a.date_prevue == saturday],
            "sunday": [a for a in activities if a.date_prevue == sunday],
        }

    @avec_gestion_erreurs(default_return={})
    @avec_cache(ttl=300)
    @avec_session_db
    def get_budget_weekend(
        self, saturday: date_type, sunday: date_type, db: Session | None = None
    ) -> BudgetWeekendDict:
        """Calcule le budget estimé et réel du weekend.

        Args:
            saturday: Date du samedi.
            sunday: Date du dimanche.
            db: Session DB (injectée automatiquement).

        Returns:
            BudgetWeekendDict avec 'estime' (budget total prévu) et
            'reel' (dépenses des activités terminées).
        """
        if db is None:
            raise ValueError("Session DB requise")
        activities = (
            db.query(ActiviteWeekend)
            .filter(ActiviteWeekend.date_prevue.in_([saturday, sunday]))
            .all()
        )

        estime = sum(a.cout_estime or 0 for a in activities)
        reel = sum(a.cout_reel or 0 for a in activities if a.statut == "termine")

        return {"estime": estime, "reel": reel}

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_lieux_testes(self, db: Session | None = None) -> list[ActiviteWeekend]:
        """Récupère les lieux déjà testés avec notes.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des activités terminées et notées,
            triées par note décroissante.
        """
        if db is None:
            raise ValueError("Session DB requise")
        return (
            db.query(ActiviteWeekend)
            .filter(
                ActiviteWeekend.statut == "termine",
                ActiviteWeekend.note_lieu.isnot(None),
            )
            .order_by(ActiviteWeekend.note_lieu.desc())
            .all()
        )

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_activites_non_notees(self, db: Session | None = None) -> list[ActiviteWeekend]:
        """Récupère les activités terminées non notées.

        Args:
            db: Session DB (injectée automatiquement).

        Returns:
            Liste des activités terminées sans note.
        """
        if db is None:
            raise ValueError("Session DB requise")
        return (
            db.query(ActiviteWeekend)
            .filter(
                ActiviteWeekend.statut == "termine",
                ActiviteWeekend.note_lieu.is_(None),
            )
            .all()
        )

    # ═══════════════════════════════════════════════════════════
    # ÉCRITURE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_activite(
        self,
        titre: str,
        type_activite: str,
        date_prevue: date_type,
        heure: str | None = None,
        duree: float = 2.0,
        lieu: str | None = None,
        cout_estime: float | None = None,
        meteo_requise: str | None = None,
        description: str | None = None,
        adapte_jules: bool = True,
        participants: list[str] | None = None,
        db: Session | None = None,
    ) -> ActiviteWeekend:
        """Ajoute une nouvelle activité weekend.

        Args:
            titre: Titre de l'activité.
            type_activite: Type (parc, musée, piscine, etc.).
            date_prevue: Date prévue.
            heure: Heure de début au format "HH:MM".
            duree: Durée estimée en heures.
            lieu: Lieu / adresse.
            cout_estime: Coût estimé en euros.
            meteo_requise: Météo requise (ensoleillé, couvert, intérieur).
            description: Notes / description.
            adapte_jules: Si l'activité est adaptée à Jules.
            participants: Liste des participants.
            db: Session DB (injectée automatiquement).

        Returns:
            L'activité créée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        if participants is None:
            participants = ["Anne", "Mathieu", "Jules"]

        activity = ActiviteWeekend(
            titre=titre,
            type_activite=type_activite,
            date_prevue=date_prevue,
            heure_debut=heure,
            duree_estimee_h=duree,
            lieu=lieu,
            cout_estime=cout_estime,
            meteo_requise=meteo_requise,
            description=description,
            adapte_jules=adapte_jules,
            statut="planifie",
            participants=participants,
        )
        db.add(activity)
        db.commit()
        logger.info("Activité weekend créée: %s (id=%d)", titre, activity.id)

        # Emit event after successful commit
        obtenir_bus().emettre(
            "weekend.cree",
            {"id": activity.id, "titre": titre, "type": type_activite, "date": str(date_prevue)},
            source="ServiceWeekend",
        )

        return activity

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def marquer_termine(self, activity_id: int, db: Session | None = None) -> bool:
        """Marque une activité comme terminée.

        Args:
            activity_id: ID de l'activité.
            db: Session DB (injectée automatiquement).

        Returns:
            True si l'activité a été trouvée et mise à jour.
        """
        if db is None:
            raise ValueError("Session DB requise")
        activity = db.get(ActiviteWeekend, activity_id)
        if activity:
            activity.statut = "termine"
            db.commit()
            logger.info("Activité weekend terminée: id=%d", activity_id)

            # Emit event after successful commit
            obtenir_bus().emettre(
                "weekend.termine",
                {"id": activity_id, "titre": activity.titre},
                source="ServiceWeekend",
            )

            return True
        return False

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def noter_sortie(
        self,
        activity_id: int,
        note: int,
        a_refaire: bool = False,
        cout_reel: float | None = None,
        commentaire: str | None = None,
        db: Session | None = None,
    ) -> bool:
        """Note une sortie terminée.

        Args:
            activity_id: ID de l'activité.
            note: Note de 1 à 5.
            a_refaire: Si on veut y retourner.
            cout_reel: Coût réel dépensé.
            commentaire: Commentaire / avis.
            db: Session DB (injectée automatiquement).

        Returns:
            True si l'activité a été trouvée et notée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        activity = db.get(ActiviteWeekend, activity_id)
        if activity:
            activity.note_lieu = note
            activity.a_refaire = a_refaire
            activity.cout_reel = cout_reel
            activity.commentaire = commentaire
            db.commit()
            logger.info("Activité weekend notée: id=%d, note=%d", activity_id, note)

            # Emit event after successful commit
            obtenir_bus().emettre(
                "weekend.note",
                {"id": activity_id, "titre": activity.titre, "note": note, "a_refaire": a_refaire},
                source="ServiceWeekend",
            )

            return True
        return False

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def supprimer_activite(self, activity_id: int, db: Session | None = None) -> bool:
        """Supprime une activité weekend.

        Args:
            activity_id: ID de l'activité.
            db: Session DB (injectée automatiquement).

        Returns:
            True si supprimée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        deleted = db.query(ActiviteWeekend).filter(ActiviteWeekend.id == activity_id).delete()
        db.commit()
        if deleted > 0:
            logger.info("Activité weekend supprimée: id=%d", activity_id)
        return deleted > 0


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("weekend", tags={"famille", "crud"})
def obtenir_service_weekend() -> ServiceWeekend:
    """Factory pour le service weekend (singleton via ServiceRegistry)."""
    return ServiceWeekend()


# Alias anglais
get_weekend_service = obtenir_service_weekend
