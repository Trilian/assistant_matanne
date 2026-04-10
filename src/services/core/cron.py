"""
Module de gestion du scheduler de cron jobs.

Centralise le démarrage/arrêt du scheduler APScheduler et l'enregistrement
de tous les cron jobs de l'application.
"""

import logging
from pathlib import Path
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def obtenir_scheduler() -> BackgroundScheduler:
    """
    Retourne l'instance singleton du scheduler.

    Returns:
        Scheduler APScheduler global
    """
    global _scheduler

    if _scheduler is None:
        _scheduler = BackgroundScheduler(
            timezone="Europe/Paris",
            job_defaults={
                "coalesce": True,  # Combine plusieurs exécutions manquées en une seule
                "max_instances": 1,  # Une seule instance par job
                "misfire_grace_time": 300,  # 5 minutes de tolérance pour retard
            },
        )

    return _scheduler


def demarrer_scheduler() -> None:
    """
    Démarre le scheduler et enregistre tous les cron jobs de l'application.
    """
    scheduler = obtenir_scheduler()

    if scheduler.running:
        logger.warning("⚠️ Scheduler déjà démarré, skip")
        return

    logger.info("🚀 Démarrage du scheduler APScheduler...")

    # Enregistrer les jobs Paris Sportifs
    try:
        from src.services.jeux.cron_jobs import configurer_jobs_paris

        configurer_jobs_paris(scheduler)
        logger.info("✅ Cron jobs Paris Sportifs configurés")
    except Exception as e:
        logger.error(f"❌ Échec configuration cron jobs Paris: {e}", exc_info=True)

    # Enregistrer les jobs Loteries
    try:
        from src.services.jeux.cron_jobs_loteries import configurer_jobs_loteries

        configurer_jobs_loteries(scheduler)
        logger.info("✅ Cron jobs Loteries configurés")
    except Exception as e:
        logger.error(f"❌ Échec configuration cron jobs Loteries: {e}", exc_info=True)

    # Enregistrer les jobs Cuisine
    try:
        from src.services.cuisine.cron_cuisine import configurer_jobs_cuisine

        configurer_jobs_cuisine(scheduler)
        logger.info("✅ Cron jobs Cuisine configurés")
    except Exception as e:
        logger.error(f"❌ Échec configuration cron jobs Cuisine: {e}", exc_info=True)

    # Enregistrer les jobs bridges (prédictions, budget, jardin, Jules, nutrition)
    try:
        from src.services.core.cron_bridges import configurer_jobs_bridges

        configurer_jobs_bridges(scheduler)
        logger.info("✅ Cron jobs bridges configurés")
    except Exception as e:
        logger.error(f"❌ Échec configuration cron jobs bridges: {e}", exc_info=True)

    # Démarrer le scheduler
    scheduler.start()

    # Enregistrer le job de nettoyage des exports (quotidien 03:00)
    scheduler.add_job(
        nettoyer_exports_anciens,
        trigger="cron",
        hour=3,
        minute=0,
        id="nettoyage_exports",
        name="Nettoyage exports > 7 jours",
        replace_existing=True,
    )

    logger.info("✅ Scheduler APScheduler démarré avec succès")

    # Afficher les jobs enregistrés
    jobs = scheduler.get_jobs()
    logger.info(f"📋 {len(jobs)} cron jobs actifs:")
    for job in jobs:
        logger.info(f"  - {job.name} (ID: {job.id})")


def arreter_scheduler() -> None:
    """
    Arrête proprement le scheduler.
    """
    global _scheduler

    if _scheduler is None or not _scheduler.running:
        logger.debug("Scheduler déjà arrêté ou non initialisé")
        return

    logger.info("🛑 Arrêt du scheduler APScheduler...")
    _scheduler.shutdown(wait=True)
    logger.info("✅ Scheduler arrêté")


# ── Politique de rétention data/exports/ ──────────────────

EXPORTS_DIR = Path(__file__).resolve().parents[3] / "data" / "exports"
RETENTION_JOURS = 7


def nettoyer_exports_anciens() -> int:
    """
    Supprime les fichiers d'export de plus de RETENTION_JOURS jours.

    Returns:
        Nombre de fichiers supprimés
    """
    import time

    if not EXPORTS_DIR.exists():
        return 0

    seuil = time.time() - (RETENTION_JOURS * 86400)
    supprimes = 0

    for fichier in EXPORTS_DIR.iterdir():
        if fichier.is_file() and fichier.stat().st_mtime < seuil:
            try:
                fichier.unlink()
                supprimes += 1
                logger.info(f"🗑️ Export supprimé (>{RETENTION_JOURS}j) : {fichier.name}")
            except OSError as e:
                logger.warning(f"⚠️ Impossible de supprimer {fichier.name}: {e}")

    if supprimes:
        logger.info(f"🧹 {supprimes} export(s) ancien(s) supprimé(s)")

    return supprimes
