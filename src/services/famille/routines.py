"""
Service Routines - Logique métier pour les routines familiales.

Hérite de BaseService[Routine] pour CRUD générique + méthodes spécialisées.

Opérations:
- CRUD routines et tâches
- Complétion et réinitialisation
- Détection des tâches en retard
"""

import logging
from datetime import datetime
from typing import Any, TypedDict

from sqlalchemy.orm import Session, selectinload

from src.core.decorators import avec_cache, avec_gestion_erreurs, avec_session_db
from src.core.models import ProfilEnfant, Routine, TacheRoutine
from src.services.core.base import BaseService
from src.services.core.events.bus import obtenir_bus
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class RoutineDict(TypedDict):
    """Structure de données pour une routine."""

    id: int
    nom: str
    description: str
    pour: str
    frequence: str
    active: bool
    ia: str
    nb_taches: int


class TacheDict(TypedDict):
    """Structure de données pour une tâche de routine."""

    id: int
    nom: str
    heure: str
    statut: str
    completed_at: datetime | None


class ServiceRoutines(BaseService[Routine]):
    """Service de gestion des routines quotidiennes.

    Hérite de BaseService[Routine] pour le CRUD générique.
    Les méthodes spécialisées gèrent la logique métier (tâches, complétion).
    """

    def __init__(self):
        super().__init__(model=Routine, cache_ttl=300)

    # ═══════════════════════════════════════════════════════════
    # LECTURE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def lister_routines(
        self, actives_uniquement: bool = True, db: Session | None = None
    ) -> list[RoutineDict]:
        """Liste les routines avec métadonnées.

        Args:
            actives_uniquement: Ne retourner que les routines actives.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste de RoutineDict contenant les données de chaque routine.
        """
        if db is None:
            raise ValueError("Session DB requise")
        query = db.query(Routine).options(selectinload(Routine.tasks))
        if actives_uniquement:
            query = query.filter(Routine.is_active)

        routines = query.order_by(Routine.created_at.desc()).all()
        result = []
        for r in routines:
            child_name = "Famille"
            if r.child_id:
                child = db.query(ProfilEnfant).get(r.child_id)
                if child:
                    child_name = child.name
            result.append(
                {
                    "id": r.id,
                    "nom": r.name,
                    "description": r.description or "",
                    "pour": child_name,
                    "frequence": r.frequency,
                    "active": r.is_active,
                    "ia": "–" if r.ai_suggested else "",
                    "nb_taches": len(r.tasks),
                }
            )
        return result

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def lister_taches(self, routine_id: int, db: Session | None = None) -> list[TacheDict]:
        """Liste les tâches d'une routine.

        Args:
            routine_id: ID de la routine.
            db: Session DB (injectée automatiquement).

        Returns:
            Liste de TacheDict contenant les tâches.
        """
        if db is None:
            raise ValueError("Session DB requise")
        tasks = (
            db.query(TacheRoutine)
            .filter(TacheRoutine.routine_id == routine_id)
            .order_by(TacheRoutine.scheduled_time)
            .all()
        )
        return [
            {
                "id": t.id,
                "nom": t.task_name,
                "heure": t.scheduled_time or "—",
                "statut": t.status,
                "completed_at": t.completed_at,
            }
            for t in tasks
        ]

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def lister_personnes(self, db: Session | None = None) -> list[str]:
        """Liste les personnes disponibles (Famille + enfants).

        Returns:
            Liste de noms (toujours commençant par 'Famille').
        """
        if db is None:
            raise ValueError("Session DB requise")
        children = db.query(ProfilEnfant).all()
        return ["Famille"] + [c.name for c in children]

    # ═══════════════════════════════════════════════════════════
    # ÉCRITURE
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def creer_routine(
        self,
        nom: str,
        description: str,
        pour_qui: str,
        frequence: str,
        db: Session | None = None,
    ) -> int:
        """Crée une nouvelle routine.

        Args:
            nom: Nom de la routine.
            description: Description optionnelle.
            pour_qui: 'Famille' ou nom d'un enfant.
            frequence: 'quotidien', 'semaine', 'weekend', 'occasionnel'.
            db: Session DB (injectée automatiquement).

        Returns:
            L'ID de la routine créée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        child_id = None
        if pour_qui != "Famille":
            child = db.query(ProfilEnfant).filter(ProfilEnfant.name == pour_qui).first()
            if child:
                child_id = child.id

        routine = Routine(
            name=nom,
            description=description,
            child_id=child_id,
            frequency=frequence,
            is_active=True,
            ai_suggested=False,
        )
        db.add(routine)
        db.commit()
        logger.info("Routine créée: %s (id=%d)", nom, routine.id)
        obtenir_bus().emettre(
            "routines.cree", {"id": routine.id, "nom": nom}, source="ServiceRoutines"
        )
        return routine.id

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def ajouter_tache(
        self,
        routine_id: int,
        nom: str,
        heure: str | None = None,
        db: Session | None = None,
    ) -> int:
        """Ajoute une tâche à une routine.

        Args:
            routine_id: ID de la routine parente.
            nom: Nom de la tâche.
            heure: Heure planifiée au format 'HH:MM' (optionnel).
            db: Session DB (injectée automatiquement).

        Returns:
            L'ID de la tâche créée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        task = TacheRoutine(
            routine_id=routine_id,
            task_name=nom,
            scheduled_time=heure,
            status="à faire",
        )
        db.add(task)
        db.commit()
        obtenir_bus().emettre(
            "routines.tache_ajoutee",
            {"routine_id": routine_id, "tache_id": task.id, "nom": nom},
            source="ServiceRoutines",
        )
        return task.id

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def marquer_complete(self, task_id: int, db: Session | None = None) -> bool:
        """Marque une tâche comme terminée.

        Args:
            task_id: ID de la tâche.
            db: Session DB (injectée automatiquement).

        Returns:
            True si la tâche a été trouvée et marquée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        task = db.query(TacheRoutine).filter(TacheRoutine.id == task_id).first()
        if task:
            task.status = "termine"
            task.completed_at = datetime.now()
            db.commit()
            obtenir_bus().emettre(
                "routines.tache_complete", {"id": task_id}, source="ServiceRoutines"
            )
            return True
        return False

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def reinitialiser_taches_jour(self, db: Session | None = None) -> int:
        """Réinitialise toutes les tâches terminées à 'à faire'.

        Returns:
            Nombre de tâches réinitialisées.
        """
        if db is None:
            raise ValueError("Session DB requise")
        tasks = db.query(TacheRoutine).filter(TacheRoutine.status == "termine").all()
        for task in tasks:
            task.status = "à faire"
            task.completed_at = None
        db.commit()
        logger.info("Réinitialisation: %d tâches", len(tasks))
        return len(tasks)

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def supprimer_routine(self, routine_id: int, db: Session | None = None) -> bool:
        """Supprime une routine et ses tâches.

        Args:
            routine_id: ID de la routine.
            db: Session DB (injectée automatiquement).

        Returns:
            True si la routine existait et a été supprimée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        deleted = db.query(Routine).filter(Routine.id == routine_id).delete()
        db.commit()
        if deleted > 0:
            obtenir_bus().emettre(
                "routines.supprimee", {"id": routine_id}, source="ServiceRoutines"
            )
        return deleted > 0

    @avec_gestion_erreurs(default_return=None)
    @avec_session_db
    def desactiver_routine(self, routine_id: int, db: Session | None = None) -> bool:
        """Désactive une routine sans la supprimer.

        Args:
            routine_id: ID de la routine.
            db: Session DB (injectée automatiquement).

        Returns:
            True si la routine a été trouvée et désactivée.
        """
        if db is None:
            raise ValueError("Session DB requise")
        routine = db.query(Routine).get(routine_id)
        if routine:
            routine.is_active = False
            db.commit()
            obtenir_bus().emettre(
                "routines.desactivee", {"id": routine_id}, source="ServiceRoutines"
            )
            return True
        return False

    # ═══════════════════════════════════════════════════════════
    # LOGIQUE MÉTIER
    # ═══════════════════════════════════════════════════════════

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_taches_en_retard(self, db: Session | None = None) -> list[dict[str, Any]]:
        """Détecte les tâches planifiées non terminées dont l'heure est passée.

        Returns:
            Liste de dictionnaires décrivant chaque tâche en retard.
        """
        if db is None:
            raise ValueError("Session DB requise")
        taches_retard = []
        now = datetime.now().time()

        tasks = (
            db.query(TacheRoutine, Routine)
            .join(Routine, TacheRoutine.routine_id == Routine.id)
            .filter(
                TacheRoutine.status == "à faire",
                TacheRoutine.scheduled_time.isnot(None),
                Routine.is_active,
            )
            .all()
        )

        for task, routine in tasks:
            try:
                heure = datetime.strptime(task.scheduled_time, "%H:%M").time()
                if heure < now:
                    taches_retard.append(
                        {
                            "routine": routine.name,
                            "tache": task.task_name,
                            "heure": task.scheduled_time,
                            "id": task.id,
                        }
                    )
            except (ValueError, TypeError):
                continue

        return taches_retard

    @avec_gestion_erreurs(default_return=[])
    @avec_cache(ttl=300)
    @avec_session_db
    def get_taches_ia_data(self, db: Session | None = None) -> list[dict[str, Any]]:
        """Récupère les tâches actives pour l'analyse IA.

        Returns:
            Liste de dicts avec nom routine, heure et nom tâche.
        """
        if db is None:
            raise ValueError("Session DB requise")
        tasks = (
            db.query(TacheRoutine, Routine)
            .join(Routine, TacheRoutine.routine_id == Routine.id)
            .filter(TacheRoutine.status == "à faire", Routine.is_active == True)  # noqa: E712
            .all()
        )
        return [
            {
                "nom": routine.name,
                "heure": task.scheduled_time or "—",
                "tache": task.task_name,
            }
            for task, routine in tasks
        ]

    @avec_gestion_erreurs(default_return=0)
    @avec_cache(ttl=300)
    @avec_session_db
    def compter_completees_aujourdhui(self, db: Session | None = None) -> int:
        """Compte les tâches complétées aujourd'hui.

        Returns:
            Nombre de tâches terminées depuis minuit.
        """
        if db is None:
            raise ValueError("Session DB requise")
        return (
            db.query(TacheRoutine)
            .filter(TacheRoutine.completed_at >= datetime.now().replace(hour=0, minute=0))
            .count()
        )


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


@service_factory("routines", tags={"famille", "crud"})
def obtenir_service_routines() -> ServiceRoutines:
    """Factory pour le service routines (singleton via ServiceRegistry)."""
    return ServiceRoutines()


# Alias anglais
get_routines_service = obtenir_service_routines
