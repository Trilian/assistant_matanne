"""
Jobs cron — Ordonnanceur APScheduler pour l'automatisation quotidienne.

Jobs déclarés :
- 07h00 quotidien : Rappels famille (anniversaires, documents, crèche, jalons)
- 08h00 quotidien : Rappels maison (garanties, contrats, entretien)
- 08h30 quotidien : Rappels généraux (inventaire, garanties intelligentes)
- lundi 06h00    : Entretien saisonnier (vérification tâches de saison)
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


# ─── Jobs ─────────────────────────────────────────────────────────────────────


def _job_rappels_famille() -> None:
    """Évalue et envoie les rappels famille du jour (anniversaires, documents, crèche, jalons)."""
    try:
        from src.services.famille.rappels import ServiceRappelsFamille

        service = ServiceRappelsFamille()
        nb = service.envoyer_rappels_du_jour()
        logger.info("Rappels famille : %d envoyé(s)", nb)
    except Exception:
        logger.exception("Erreur lors des rappels famille")


def _job_rappels_maison() -> None:
    """Évalue et envoie les rappels maison du jour (garanties, contrats, entretien)."""
    try:
        from src.services.maison.notifications_maison import NotificationsMaisonService

        service = NotificationsMaisonService()
        result = service.evaluer_et_envoyer_rappels()
        if result:
            logger.info(
                "Rappels maison : %d envoyé(s), %d ignoré(s), %d erreur(s)",
                result.rappels_envoyes,
                result.rappels_ignores,
                len(result.erreurs),
            )
    except Exception:
        logger.exception("Erreur lors des rappels maison")


def _job_rappels_generaux() -> None:
    """Évalue les rappels GenericService (inventaire faible, garanties générales)."""
    try:
        from src.services.core.rappels_intelligents import get_rappels_intelligents_service

        service = get_rappels_intelligents_service()
        rappels = service.evaluer_rappels()
        if rappels:
            logger.info("Rappels intelligents : %d rappel(s) actif(s)", len(rappels))
        else:
            logger.debug("Rappels intelligents : aucun rappel actif")
    except Exception:
        logger.exception("Erreur lors des rappels intelligents")


def _job_entretien_saisonnier() -> None:
    """Vérifie si des tâches d'entretien saisonnières doivent être créées cette semaine."""
    try:
        from src.services.maison import get_entretien_service

        service = get_entretien_service()
        if hasattr(service, "verifier_saison"):
            resultats = service.verifier_saison()
            logger.info("Entretien saisonnier : %s", resultats)
        else:
            logger.debug("Entretien saisonnier : méthode verifier_saison non disponible")
    except Exception:
        logger.exception("Erreur lors de la vérification saisonnière")


# ─── Orchestrateur ────────────────────────────────────────────────────────────


class DémarreurCron:
    """Enveloppe legère autour de BackgroundScheduler pour un démarrage/arrêt propre."""

    def __init__(self) -> None:
        self._scheduler = BackgroundScheduler(
            job_defaults={"coalesce": True, "max_instances": 1},
            timezone="Europe/Paris",
        )
        self._configurer_jobs()

    def _configurer_jobs(self) -> None:
        self._scheduler.add_job(
            _job_rappels_famille,
            CronTrigger(hour=7, minute=0),
            id="rappels_famille",
            name="Rappels famille quotidiens",
        )
        self._scheduler.add_job(
            _job_rappels_maison,
            CronTrigger(hour=8, minute=0),
            id="rappels_maison",
            name="Rappels maison quotidiens",
        )
        self._scheduler.add_job(
            _job_rappels_generaux,
            CronTrigger(hour=8, minute=30),
            id="rappels_generaux",
            name="Rappels intelligents quotidiens",
        )
        self._scheduler.add_job(
            _job_entretien_saisonnier,
            CronTrigger(day_of_week="mon", hour=6, minute=0),
            id="entretien_saisonnier",
            name="Entretien saisonnier hebdomadaire",
        )

    def demarrer(self) -> None:
        if not self._scheduler.running:
            self._scheduler.start()
            logger.info("Scheduler cron démarré (%d job(s))", len(self._scheduler.get_jobs()))

    def arreter(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)
            logger.info("Scheduler cron arrêté")


# ─── Helpers module-level ─────────────────────────────────────────────────────

_demarreur: DémarreurCron | None = None


def demarrer_scheduler() -> None:
    """Initialise et démarre l'ordonnanceur global (appelé depuis le lifespan FastAPI)."""
    global _demarreur
    try:
        _demarreur = DémarreurCron()
        _demarreur.demarrer()
    except Exception:
        logger.exception("Impossible de démarrer le scheduler cron")


def arreter_scheduler() -> None:
    """Arrête proprement l'ordonnanceur (appelé depuis le lifespan FastAPI à l'arrêt)."""
    global _demarreur
    if _demarreur is not None:
        try:
            _demarreur.arreter()
        except Exception:
            logger.exception("Erreur à l'arrêt du scheduler cron")
        finally:
            _demarreur = None
