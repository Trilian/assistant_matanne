"""
SchedulerService - Service de planification des synchronisations automatiques.

Utilise APScheduler pour exécuter les jobs de synchronisation:
- Paris Sportifs: toutes les 6 heures
- Loto: Lundi, Mercredi, Samedi à 21:30 (après les tirages)

Usage:
    scheduler = get_scheduler_service()
    scheduler.demarrer()  # Démarre le scheduler en arrière-plan
    scheduler.arreter()   # Arrête proprement

Note: Le scheduler utilise BackgroundScheduler qui s'exécute dans un thread séparé.
Compatible avec Streamlit (pas de blocage de l'UI).
"""

import logging
import threading
from datetime import datetime
from typing import Literal

try:
    from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger

    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None
    CronTrigger = None
    IntervalTrigger = None

from src.core.decorators import avec_resilience
from src.services.core.registry import service_factory

from .sync_service import SyncService, get_sync_service

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Intervalles par défaut
INTERVALLE_PARIS_HEURES = 6
HEURE_LOTO = 21
MINUTE_LOTO = 30

# Jours des tirages Loto (0=lundi, 2=mercredi, 5=samedi)
JOURS_LOTO = [0, 2, 5]  # lundi, mercredi, samedi


# ═══════════════════════════════════════════════════════════
# SERVICE PRINCIPAL
# ═══════════════════════════════════════════════════════════


class SchedulerService:
    """
    Service de planification des synchronisations automatiques.

    Gère les jobs de synchronisation pour Paris Sportifs et Loto
    via APScheduler BackgroundScheduler.
    """

    def __init__(
        self,
        sync_service: SyncService | None = None,
        api_key_football: str | None = None,
    ):
        """
        Initialise le scheduler.

        Args:
            sync_service: Service de synchronisation
            api_key_football: Clé API Football-Data.org
        """
        self.sync_service = sync_service or get_sync_service()
        self.api_key_football = api_key_football
        self._scheduler: BackgroundScheduler | None = None
        self._est_demarre = False
        self._lock = threading.Lock()

        # Historique des exécutions
        self._historique: list[dict] = []
        self._max_historique = 100

    @property
    def est_disponible(self) -> bool:
        """Vérifie si APScheduler est installé."""
        return APSCHEDULER_AVAILABLE

    @property
    def est_demarre(self) -> bool:
        """Vérifie si le scheduler est démarré."""
        return self._est_demarre and self._scheduler is not None

    # ─────────────────────────────────────────────────────────────────
    # GESTION DU SCHEDULER
    # ─────────────────────────────────────────────────────────────────

    def demarrer(
        self,
        competitions: list[str] | None = None,
        inclure_loto: bool = True,
    ) -> bool:
        """
        Démarre le scheduler avec les jobs configurés.

        Args:
            competitions: Compétitions Paris à synchroniser (défaut: FL1)
            inclure_loto: Inclure la sync Loto

        Returns:
            True si démarré avec succès
        """
        if not APSCHEDULER_AVAILABLE:
            logger.error("APScheduler non installé. Installer avec: pip install apscheduler")
            return False

        with self._lock:
            if self._est_demarre:
                logger.warning("Scheduler déjà démarré")
                return True

            try:
                self._scheduler = BackgroundScheduler(
                    daemon=True,
                    job_defaults={
                        "coalesce": True,  # Fusionne les jobs manqués
                        "max_instances": 1,  # Une seule instance par job
                        "misfire_grace_time": 3600,  # 1h de grâce
                    },
                )

                # Listener pour logging
                self._scheduler.add_listener(
                    self._on_job_event,
                    EVENT_JOB_EXECUTED | EVENT_JOB_ERROR,
                )

                # Ajouter jobs Paris
                competitions = competitions or ["FL1"]
                for comp in competitions:
                    self._ajouter_job_paris(comp)

                # Ajouter job Loto
                if inclure_loto:
                    self._ajouter_job_loto()

                self._scheduler.start()
                self._est_demarre = True
                logger.info(f"Scheduler démarré: {len(self._scheduler.get_jobs())} jobs programmés")
                return True

            except Exception as e:
                logger.error(f"Erreur démarrage scheduler: {e}")
                self._scheduler = None
                return False

    def arreter(self, wait: bool = True) -> bool:
        """
        Arrête le scheduler proprement.

        Args:
            wait: Attendre la fin des jobs en cours

        Returns:
            True si arrêté avec succès
        """
        with self._lock:
            if not self._est_demarre or self._scheduler is None:
                return True

            try:
                self._scheduler.shutdown(wait=wait)
                self._scheduler = None
                self._est_demarre = False
                logger.info("Scheduler arrêté")
                return True

            except Exception as e:
                logger.error(f"Erreur arrêt scheduler: {e}")
                return False

    def redemarrer(self) -> bool:
        """Redémarre le scheduler."""
        self.arreter()
        return self.demarrer()

    # ─────────────────────────────────────────────────────────────────
    # CONFIGURATION DES JOBS
    # ─────────────────────────────────────────────────────────────────

    def _ajouter_job_paris(self, competition: str) -> None:
        """Ajoute un job de synchronisation Paris."""
        if self._scheduler is None:
            return

        job_id = f"sync_paris_{competition}"

        self._scheduler.add_job(
            func=self._executer_sync_paris,
            trigger=IntervalTrigger(hours=INTERVALLE_PARIS_HEURES),
            id=job_id,
            name=f"Sync Paris {competition}",
            kwargs={"competition": competition},
            replace_existing=True,
        )

        logger.info(f"Job ajouté: {job_id} (toutes les {INTERVALLE_PARIS_HEURES}h)")

    def _ajouter_job_loto(self) -> None:
        """Ajoute un job de synchronisation Loto."""
        if self._scheduler is None:
            return

        job_id = "sync_loto"

        # Cron: lundi(0), mercredi(2), samedi(5) à 21:30
        self._scheduler.add_job(
            func=self._executer_sync_loto,
            trigger=CronTrigger(
                day_of_week="mon,wed,sat",
                hour=HEURE_LOTO,
                minute=MINUTE_LOTO,
            ),
            id=job_id,
            name="Sync Loto",
            replace_existing=True,
        )

        logger.info(f"Job ajouté: {job_id} (L/M/S à {HEURE_LOTO}:{MINUTE_LOTO:02d})")

    # ─────────────────────────────────────────────────────────────────
    # EXÉCUTION DES JOBS
    # ─────────────────────────────────────────────────────────────────

    @avec_resilience(retry=1, timeout_s=120, fallback=None)
    def _executer_sync_paris(self, competition: str) -> dict:
        """Exécute la synchronisation Paris."""
        logger.info(f"Exécution sync Paris {competition}")

        try:
            resultat = self.sync_service.synchroniser_paris(
                competition=competition,
                api_key=self.api_key_football,
            )
            self._enregistrer_historique("paris", competition, resultat)
            return resultat

        except Exception as e:
            logger.error(f"Erreur sync Paris {competition}: {e}")
            self._enregistrer_historique("paris", competition, {"erreur": str(e)})
            raise

    @avec_resilience(retry=1, timeout_s=120, fallback=None)
    def _executer_sync_loto(self) -> dict:
        """Exécute la synchronisation Loto."""
        logger.info("Exécution sync Loto")

        try:
            resultat = self.sync_service.synchroniser_loto(type_numeros="tous")
            self._enregistrer_historique("loto", None, resultat)
            return resultat

        except Exception as e:
            logger.error(f"Erreur sync Loto: {e}")
            self._enregistrer_historique("loto", None, {"erreur": str(e)})
            raise

    def _on_job_event(self, event) -> None:
        """Callback appelé après exécution d'un job."""
        if event.exception:
            logger.error(f"Job {event.job_id} échoué: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} terminé avec succès")

    def _enregistrer_historique(
        self,
        type_sync: str,
        competition: str | None,
        resultat: dict,
    ) -> None:
        """Enregistre une exécution dans l'historique."""
        entry = {
            "type": type_sync,
            "competition": competition,
            "timestamp": datetime.utcnow().isoformat(),
            "resultat": resultat,
        }

        self._historique.append(entry)

        # Limiter la taille de l'historique
        if len(self._historique) > self._max_historique:
            self._historique = self._historique[-self._max_historique :]

    # ─────────────────────────────────────────────────────────────────
    # EXÉCUTION MANUELLE
    # ─────────────────────────────────────────────────────────────────

    def executer_maintenant(
        self,
        type_sync: Literal["paris", "loto", "tout"],
        competition: str | None = None,
    ) -> dict:
        """
        Exécute une synchronisation immédiatement.

        Args:
            type_sync: "paris", "loto" ou "tout"
            competition: Compétition (pour paris)

        Returns:
            Résultat de la synchronisation
        """
        if type_sync == "paris":
            return self._executer_sync_paris(competition or "FL1")
        elif type_sync == "loto":
            return self._executer_sync_loto()
        elif type_sync == "tout":
            return self.sync_service.synchroniser_tout(
                competitions=[competition] if competition else ["FL1"],
                api_key=self.api_key_football,
            )
        else:
            raise ValueError(f"Type sync inconnu: {type_sync}")

    # ─────────────────────────────────────────────────────────────────
    # INFORMATIONS
    # ─────────────────────────────────────────────────────────────────

    def obtenir_jobs(self) -> list[dict]:
        """
        Retourne la liste des jobs programmés.

        Returns:
            Liste de dicts avec infos sur chaque job
        """
        if not self._scheduler:
            return []

        jobs = []
        for job in self._scheduler.get_jobs():
            next_run = job.next_run_time
            jobs.append(
                {
                    "id": job.id,
                    "nom": job.name,
                    "prochaine_execution": next_run.isoformat() if next_run else None,
                    "trigger": str(job.trigger),
                }
            )

        return jobs

    def obtenir_historique(self, limite: int = 20) -> list[dict]:
        """
        Retourne l'historique des exécutions.

        Args:
            limite: Nombre max d'entrées

        Returns:
            Liste des dernières exécutions
        """
        return self._historique[-limite:][::-1]  # Plus récent en premier

    def obtenir_prochaines_executions(self) -> dict:
        """
        Retourne les prochaines exécutions programmées.

        Returns:
            Dict type -> datetime prochaine exécution
        """
        if not self._scheduler:
            return {}

        prochaines = {}
        for job in self._scheduler.get_jobs():
            if job.next_run_time:
                type_sync = "paris" if "paris" in job.id else "loto"
                if type_sync not in prochaines:
                    prochaines[type_sync] = job.next_run_time

        return prochaines


# ═══════════════════════════════════════════════════════════
# FACTORY — Singleton via @service_factory (thread-safe)
# ═══════════════════════════════════════════════════════════


@service_factory("scheduler", tags={"jeux", "scheduler"})
def get_scheduler_service(
    sync_service: SyncService | None = None,
    api_key_football: str | None = None,
) -> SchedulerService:
    """
    Factory singleton pour le scheduler.

    Sans arguments: singleton via registre (thread-safe).
    Avec arguments: bypass singleton (instance dédiée).

    Args:
        sync_service: Service de synchronisation
        api_key_football: Clé API Football-Data

    Returns:
        Instance unique du SchedulerService
    """
    return SchedulerService(
        sync_service=sync_service,
        api_key_football=api_key_football,
    )


def obtenir_service_planificateur_jeux(
    sync_service: SyncService | None = None,
    api_key_football: str | None = None,
) -> SchedulerService:
    """Alias français pour get_scheduler_service (singleton via registre)."""
    if sync_service is not None or api_key_football is not None:
        return get_scheduler_service(
            sync_service=sync_service,
            api_key_football=api_key_football,
        )
    return get_scheduler_service()


def reset_scheduler_service() -> None:
    """Remet le singleton à zéro (utile pour tests)."""
    from src.services.core.registry import obtenir_registre

    reg = obtenir_registre()
    if reg.est_instancie("scheduler"):
        try:
            service = reg.obtenir("scheduler")
            service.arreter()
        except Exception:
            pass
    reg.reinitialiser("scheduler")
