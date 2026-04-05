"""Tests ciblés — présence des jobs IA et automations dans le scheduler."""

import pytest


@pytest.fixture
def demarreur_cron():
    from src.services.core.cron.jobs import DémarreurCron

    return DémarreurCron()


class TestJobsCatalog:
    JOBS_IA_AUTOMATIONS = {
        "briefing_matinal_ia",
        "comparateur_abonnements",
        "rapport_nutritionnel_jules",
        "nettoyage_notifications_30j",
        "prediction_depenses",
        "alerte_plantes_arrosage",
        "sync_tirages_euromillions",
        "recap_journee",
        "suggestion_soiree",
    }

    def test_jobs_ia_automations_presents_dans_scheduler(self, demarreur_cron):
        job_ids = {job.id for job in demarreur_cron._scheduler.get_jobs()}
        assert self.JOBS_IA_AUTOMATIONS.issubset(job_ids)

    def test_jobs_phase4_habitat_ont_un_timing_coherent(self, demarreur_cron):
        jobs = {job.id: job for job in demarreur_cron._scheduler.get_jobs()}

        trigger_comparateur = str(jobs["comparateur_abonnements"].trigger)
        trigger_rapport = str(jobs["rapport_maison_mensuel"].trigger)

        assert "day_of_week='mon'" in trigger_comparateur
        assert "hour='8'" in trigger_comparateur
        assert "day='1'" in trigger_rapport
