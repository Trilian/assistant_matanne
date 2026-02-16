"""
Tests pour SchedulerService - Planification automatique des synchronisations.
"""

import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from src.services.jeux.scheduler_service import (
    APSCHEDULER_AVAILABLE,
    HEURE_LOTO,
    INTERVALLE_PARIS_HEURES,
    MINUTE_LOTO,
    SchedulerService,
    get_scheduler_service,
    reset_scheduler_service,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset le singleton après chaque test."""
    yield
    reset_scheduler_service()


class TestSchedulerServiceDisponibilite:
    """Tests de disponibilité."""

    def test_apscheduler_disponible(self):
        """Vérifie que APScheduler est installé."""
        assert APSCHEDULER_AVAILABLE is True

    def test_service_creation(self):
        """Test création du service."""
        service = SchedulerService()
        assert service is not None
        assert service.est_disponible is True


class TestSchedulerServiceFactory:
    """Tests de la factory singleton."""

    def test_get_scheduler_service(self):
        """Test création via factory."""
        service = get_scheduler_service()
        assert isinstance(service, SchedulerService)

    def test_singleton_pattern(self):
        """Test que la factory retourne toujours la même instance."""
        service1 = get_scheduler_service()
        service2 = get_scheduler_service()
        assert service1 is service2

    def test_reset_singleton(self):
        """Test reset du singleton."""
        service1 = get_scheduler_service()
        reset_scheduler_service()
        service2 = get_scheduler_service()
        assert service1 is not service2


class TestSchedulerServiceConstantes:
    """Tests des constantes."""

    def test_intervalle_paris(self):
        """Vérifie l'intervalle Paris."""
        assert INTERVALLE_PARIS_HEURES == 6

    def test_heure_loto(self):
        """Vérifie l'heure Loto."""
        assert HEURE_LOTO == 21
        assert MINUTE_LOTO == 30


class TestSchedulerServiceDemarrage:
    """Tests du démarrage/arrêt."""

    def test_demarrer_scheduler(self):
        """Test démarrage du scheduler."""
        service = SchedulerService()

        assert service.est_demarre is False
        result = service.demarrer(competitions=["FL1"], inclure_loto=True)

        assert result is True
        assert service.est_demarre is True

        # Cleanup
        service.arreter()

    def test_arreter_scheduler(self):
        """Test arrêt du scheduler."""
        service = SchedulerService()
        service.demarrer()

        result = service.arreter()

        assert result is True
        assert service.est_demarre is False

    def test_demarrage_double(self):
        """Test double démarrage (devrait être idempotent)."""
        service = SchedulerService()
        service.demarrer()

        # Second démarrage
        result = service.demarrer()
        assert result is True  # Retourne True même si déjà démarré

        service.arreter()

    def test_redemarrer_scheduler(self):
        """Test redémarrage."""
        service = SchedulerService()
        service.demarrer()

        result = service.redemarrer()

        assert result is True
        assert service.est_demarre is True

        service.arreter()


class TestSchedulerServiceJobs:
    """Tests des jobs programmés."""

    def test_jobs_crees_au_demarrage(self):
        """Vérifie que les jobs sont créés."""
        service = SchedulerService()
        service.demarrer(competitions=["FL1"], inclure_loto=True)

        jobs = service.obtenir_jobs()

        # 1 job Paris (FL1) + 1 job Loto
        assert len(jobs) == 2

        job_ids = [j["id"] for j in jobs]
        assert "sync_paris_FL1" in job_ids
        assert "sync_loto" in job_ids

        service.arreter()

    def test_jobs_multiples_competitions(self):
        """Test avec plusieurs compétitions."""
        service = SchedulerService()
        service.demarrer(competitions=["FL1", "PL", "BL1"], inclure_loto=False)

        jobs = service.obtenir_jobs()

        assert len(jobs) == 3
        job_ids = [j["id"] for j in jobs]
        assert "sync_paris_FL1" in job_ids
        assert "sync_paris_PL" in job_ids
        assert "sync_paris_BL1" in job_ids

        service.arreter()

    def test_job_sans_loto(self):
        """Test sans synchronisation Loto."""
        service = SchedulerService()
        service.demarrer(competitions=["FL1"], inclure_loto=False)

        jobs = service.obtenir_jobs()

        assert len(jobs) == 1
        assert jobs[0]["id"] == "sync_paris_FL1"

        service.arreter()

    def test_prochaines_executions(self):
        """Test récupération des prochaines exécutions."""
        service = SchedulerService()
        service.demarrer(competitions=["FL1"], inclure_loto=True)

        prochaines = service.obtenir_prochaines_executions()

        assert "paris" in prochaines
        assert "loto" in prochaines

        # Vérifier que les dates sont dans le futur
        now = datetime.now(prochaines["paris"].tzinfo)
        assert prochaines["paris"] > now

        service.arreter()


class TestSchedulerServiceExecutionManuelle:
    """Tests d'exécution manuelle."""

    @patch.object(SchedulerService, "_executer_sync_paris")
    def test_executer_maintenant_paris(self, mock_sync):
        """Test exécution manuelle Paris."""
        mock_sync.return_value = {"marches_maj": 6}

        service = SchedulerService()
        result = service.executer_maintenant("paris", "FL1")

        mock_sync.assert_called_once_with("FL1")
        assert result == {"marches_maj": 6}

    @patch.object(SchedulerService, "_executer_sync_loto")
    def test_executer_maintenant_loto(self, mock_sync):
        """Test exécution manuelle Loto."""
        mock_sync.return_value = {"numeros_maj": 59}

        service = SchedulerService()
        result = service.executer_maintenant("loto")

        mock_sync.assert_called_once()
        assert result == {"numeros_maj": 59}

    def test_executer_maintenant_type_invalide(self):
        """Test avec type invalide."""
        service = SchedulerService()

        with pytest.raises(ValueError):
            service.executer_maintenant("invalide")


class TestSchedulerServiceHistorique:
    """Tests de l'historique."""

    def test_historique_vide_initial(self):
        """Test historique vide au départ."""
        service = SchedulerService()

        historique = service.obtenir_historique()

        assert historique == []

    def test_enregistrement_historique(self):
        """Test enregistrement dans l'historique."""
        service = SchedulerService()

        # Enregistrer manuellement
        service._enregistrer_historique("paris", "FL1", {"test": True})
        service._enregistrer_historique("loto", None, {"test": True})

        historique = service.obtenir_historique()

        assert len(historique) == 2
        # Plus récent en premier
        assert historique[0]["type"] == "loto"
        assert historique[1]["type"] == "paris"

    def test_limite_historique(self):
        """Test limite de l'historique."""
        service = SchedulerService()
        service._max_historique = 5

        # Ajouter plus que la limite
        for i in range(10):
            service._enregistrer_historique("paris", f"test_{i}", {})

        historique = service.obtenir_historique(limite=10)

        # Devrait être limité à _max_historique
        assert len(service._historique) == 5


class TestSchedulerServiceIntegration:
    """Tests d'intégration avec mocks."""

    @patch("src.services.jeux.scheduler_service.get_sync_service")
    def test_integration_sync_service(self, mock_get_sync):
        """Test intégration avec SyncService."""
        mock_sync = MagicMock()
        mock_sync.synchroniser_paris.return_value = {"marches_maj": 6}
        mock_sync.synchroniser_loto.return_value = {"numeros_maj": 59}
        mock_get_sync.return_value = mock_sync

        service = SchedulerService(sync_service=mock_sync)

        # Exécuter manuellement
        result_paris = service._executer_sync_paris("FL1")
        result_loto = service._executer_sync_loto()

        mock_sync.synchroniser_paris.assert_called_once()
        mock_sync.synchroniser_loto.assert_called_once()


class TestSchedulerServiceScenarios:
    """Tests de scénarios réalistes."""

    def test_scenario_demarrage_complet(self):
        """
        Scénario: Démarrage complet avec Ligue 1 et Loto.
        """
        service = SchedulerService()

        # Démarrer
        assert service.demarrer(competitions=["FL1"], inclure_loto=True)

        # Vérifier jobs
        jobs = service.obtenir_jobs()
        assert len(jobs) == 2

        # Vérifier infos jobs
        for job in jobs:
            assert "id" in job
            assert "nom" in job
            assert "prochaine_execution" in job

        # Arrêter proprement
        assert service.arreter()

    def test_scenario_plusieurs_ligues(self):
        """
        Scénario: Suivi de plusieurs championnats européens.
        """
        service = SchedulerService()

        competitions = ["FL1", "PL", "BL1", "SA", "PD"]
        service.demarrer(competitions=competitions, inclure_loto=True)

        # 5 jobs Paris + 1 job Loto = 6 jobs
        jobs = service.obtenir_jobs()
        assert len(jobs) == 6

        service.arreter()
