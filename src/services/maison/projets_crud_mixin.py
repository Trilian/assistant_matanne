"""
Mixin CRUD Projets — Opérations base de données du service projets.

Extrait de projets_service.py pour maintenir chaque fichier sous 500 LOC.
Contient:
- CRUD projets (créer, lister, terminer)
- CRUD tâches (ajouter, terminer, charger)
- Statistiques projets
- Émission d'événements
"""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy.orm import Session

from src.core.decorators import avec_cache, avec_session_db
from src.core.models import Projet
from src.core.monitoring import chronometre
from src.services.core.events import obtenir_bus

logger = logging.getLogger(__name__)


class ProjetsCrudMixin:
    """Mixin fournissant les opérations CRUD du service projets.

    Toutes les méthodes utilisent @avec_session_db pour l'injection de session.
    Requiert ServiceMetricsMixin pour self._incrementer_compteur et self._mesurer_duree.
    Requiert EventBusMixin pour self._emettre_creation et self._emettre_modification.
    """

    # ─────────────────────────────────────────────────────────
    # ÉMISSION D'ÉVÉNEMENTS
    # ─────────────────────────────────────────────────────────

    @staticmethod
    def emettre_modification(
        projet_id: int = 0,
        nom: str = "",
        action: str = "modifie",
    ) -> None:
        """Émet un événement projets.modifie pour déclencher l'invalidation de cache.

        Args:
            projet_id: ID du projet
            nom: Nom du projet
            action: "cree", "modifie", "archive", "tache_ajoutee"
        """
        obtenir_bus().emettre(
            "projets.modifie",
            {"projet_id": projet_id, "nom": nom, "action": action},
            source="projets",
        )

    # ─────────────────────────────────────────────────────────
    # LECTURE PROJETS
    # ─────────────────────────────────────────────────────────

    @chronometre("maison.projets.lister", seuil_alerte_ms=1500)
    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_projets(self, db: Session | None = None, statut: str | None = None) -> list[Projet]:
        """Récupère les projets.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)
            statut: Filtrer par statut (en_cours, termine, etc.)

        Returns:
            Liste des projets
        """
        return self._query_projets(db, statut)

    def get_projets(self, db: Session | None = None, statut: str | None = None) -> list[Projet]:
        """Alias anglais pour obtenir_projets (rétrocompatibilité)."""
        return self.obtenir_projets(db, statut)

    def _query_projets(self, db: Session, statut: str | None = None) -> list[Projet]:
        """Query interne pour projets."""
        query = db.query(Projet)
        if statut:
            query = query.filter(Projet.statut == statut)
        return query.order_by(Projet.priorite.desc()).all()

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_projets_urgents(self, db: Session | None = None) -> list[Projet]:
        """Récupère les projets urgents/prioritaires.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Liste des projets urgents
        """
        return self._query_projets_urgents(db)

    def get_projets_urgents(self, db: Session | None = None) -> list[Projet]:
        """Alias anglais pour obtenir_projets_urgents (rétrocompatibilité)."""
        return self.obtenir_projets_urgents(db)

    def _query_projets_urgents(self, db: Session) -> list[Projet]:
        """Query interne pour projets urgents."""
        return (
            db.query(Projet)
            .filter(
                Projet.statut == "en_cours",
                Projet.priorite == "haute",
            )
            .all()
        )

    # ─────────────────────────────────────────────────────────
    # CRUD PROJETS
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def creer_projet(
        self,
        nom: str,
        description: str,
        priorite: str = "moyenne",
        date_fin_prevue: date | None = None,
        db: Session | None = None,
    ) -> int | None:
        """Crée un nouveau projet.

        Args:
            nom: Nom du projet
            description: Description
            priorite: Priorité (basse, moyenne, haute, urgente)
            date_fin_prevue: Date d'échéance optionnelle
            db: Session DB (injectée par @avec_session_db)

        Returns:
            ID du projet créé, ou None en cas d'erreur.
        """
        try:
            self._incrementer_compteur("projets_crees")

            with self._mesurer_duree("creation_projet"):
                projet = Projet(
                    nom=nom,
                    description=description,
                    priorite=priorite,
                    statut="en_cours",
                )
                if date_fin_prevue:
                    projet.date_fin_prevue = date_fin_prevue
                db.add(projet)
                db.commit()
                db.refresh(projet)

            logger.info(f"✅ Projet '{nom}' créé (ID: {projet.id})")
            self._emettre_creation("projets", projet.id, nom)
            return projet.id
        except Exception as e:
            logger.error(f"Erreur création projet: {e}")
            db.rollback()
            self._incrementer_compteur("erreurs")
            return None

    @avec_session_db
    def marquer_projet_termine(
        self,
        project_id: int,
        db: Session | None = None,
    ) -> bool:
        """Marque un projet comme terminé.

        Args:
            project_id: ID du projet
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si le projet a été marqué terminé.
        """
        try:
            projet = db.query(Projet).get(project_id)
            if projet is None:
                logger.warning(f"Projet {project_id} non trouvé")
                return False
            projet.statut = "termine"
            db.commit()
            logger.info(f"✅ Projet {project_id} terminé")
            self._emettre_modification("projets", project_id, projet.nom, "termine")
            self._incrementer_compteur("projets_termines")
            return True
        except Exception as e:
            logger.error(f"Erreur marquage projet terminé: {e}")
            db.rollback()
            self._incrementer_compteur("erreurs")
            return False

    # ─────────────────────────────────────────────────────────
    # CRUD TÂCHES
    # ─────────────────────────────────────────────────────────

    @avec_session_db
    def charger_taches_projet(
        self,
        project_id: int,
        db: Session | None = None,
    ) -> list:
        """Charge les tâches d'un projet.

        Args:
            project_id: ID du projet
            db: Session DB (injectée par @avec_session_db)

        Returns:
            Liste des tâches du projet (objets TacheProjet).
        """
        try:
            from src.core.models.maison import TacheProjet

            taches = db.query(TacheProjet).filter_by(project_id=project_id).all()
            return taches
        except Exception as e:
            logger.error(f"Erreur chargement tâches projet {project_id}: {e}")
            return []

    @avec_session_db
    def marquer_tache_terminee(
        self,
        task_id: int,
        db: Session | None = None,
    ) -> bool:
        """Marque une tâche comme terminée.

        Args:
            task_id: ID de la tâche
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si la tâche a été marquée terminée.
        """
        try:
            from src.core.models.maison import TacheProjet

            tache = db.query(TacheProjet).get(task_id)
            if tache is None:
                logger.warning(f"Tâche {task_id} non trouvée")
                return False
            tache.statut = "termine"
            db.commit()
            logger.info(f"✅ Tâche {task_id} terminée")
            return True
        except Exception as e:
            logger.error(f"Erreur marquage tâche terminée: {e}")
            db.rollback()
            return False

    @avec_session_db
    def ajouter_tache(
        self,
        project_id: int,
        nom: str,
        description: str | None = None,
        priorite: str | None = None,
        date_echeance: date | None = None,
        db: Session | None = None,
    ) -> bool:
        """Ajoute une tâche à un projet.

        Args:
            project_id: ID du projet
            nom: Nom de la tâche
            description: Description optionnelle
            priorite: Priorité optionnelle
            date_echeance: Date d'échéance optionnelle
            db: Session DB (injectée par @avec_session_db)

        Returns:
            True si la tâche a été ajoutée.
        """
        try:
            from src.core.models.maison import TacheProjet

            self._incrementer_compteur("taches_ajoutees")

            kwargs = {
                "project_id": project_id,
                "nom": nom,
                "statut": "a_faire",
            }
            if description:
                kwargs["description"] = description
            if priorite:
                kwargs["priorite"] = priorite
            if date_echeance:
                kwargs["date_echeance"] = date_echeance
            tache = TacheProjet(**kwargs)
            db.add(tache)
            db.commit()
            logger.info(f"✅ Tâche '{nom}' ajoutée au projet {project_id}")
            self._emettre_modification("projets", project_id, nom, "tache_ajoutee")
            return True
        except Exception as e:
            logger.error(f"Erreur ajout tâche: {e}")
            db.rollback()
            self._incrementer_compteur("erreurs")
            return False

    # ─────────────────────────────────────────────────────────
    # STATISTIQUES
    # ─────────────────────────────────────────────────────────

    @avec_cache(ttl=300)
    @avec_session_db
    def obtenir_stats_projets(self, db: Session | None = None) -> dict:
        """Calcule les statistiques globales des projets.

        Args:
            db: Session DB (injectée automatiquement par @avec_session_db)

        Returns:
            Dict avec total, en_cours, termines, avg_progress.
        """
        total = db.query(Projet).count()
        en_cours = db.query(Projet).filter(Projet.statut == "en_cours").count()
        termines = db.query(Projet).filter(Projet.statut == "termine").count()

        projets = db.query(Projet).all()
        if projets:
            progressions = []
            for p in projets:
                tasks = p.tasks if p.tasks else []
                t_total = len(tasks)
                t_done = len([t for t in tasks if t.statut == "termine"])
                progressions.append((t_done / t_total * 100) if t_total > 0 else 0)
            avg_progress = sum(progressions) / len(progressions) if progressions else 0
        else:
            avg_progress = 0

        return {
            "total": total,
            "en_cours": en_cours,
            "termines": termines,
            "avg_progress": avg_progress,
        }

    def get_stats_projets(self, db: Session | None = None) -> dict:
        """Alias anglais pour obtenir_stats_projets (rétrocompatibilité)."""
        return self.obtenir_stats_projets(db)
