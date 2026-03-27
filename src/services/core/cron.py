"""
Module de gestion du scheduler de cron jobs.

Centralise le démarrage/arrêt du scheduler APScheduler et l'enregistrement
de tous les cron jobs de l'application.
"""

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)

_scheduler: Optional[BackgroundScheduler] = None


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
                'coalesce': True,  # Combine plusieurs exécutions manquées en une seule
                'max_instances': 1,  # Une seule instance par job
                'misfire_grace_time': 300  # 5 minutes de tolérance pour retard
            }
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
    
    # Démarrer le scheduler
    scheduler.start()
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
