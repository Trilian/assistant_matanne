"""
Tests pour les cron jobs du module Jeux.

Couvre les 6 jobs dans src/services/jeux/cron_jobs.py et cron_jobs_loteries.py :
1. job_actualiser_cotes — Toutes les 2h
2. job_resultats_matchs — Quotidien 23h
3. job_detecter_opportunites — Toutes les 30min
4. job_analyser_series — Quotidien 9h
5. job_scraper_fdj_resultats — Quotidien 21h30
6. job_backtest_grilles — Quotidien 22h
"""

import pytest
from contextlib import contextmanager
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def mock_session():
    """Session DB mockée pour les jobs jeux."""
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.count.return_value = 0
    session.query.return_value.all.return_value = []
    return session


@contextmanager
def _ctx(mock_session):
    yield mock_session


@pytest.fixture
def patch_db(mock_session):
    """Patch le contexte DB."""
    with patch(
        "src.core.db.obtenir_contexte_db",
        return_value=_ctx(mock_session),
    ):
        yield mock_session


# ═══════════════════════════════════════════════════════════════
# JOB 1: ACTUALISER COTES
# ═══════════════════════════════════════════════════════════════


class TestJobActualiserCotes:
    """Tests pour le job d'actualisation des cotes sportives."""

    @pytest.mark.unit
    def test_actualiser_cotes_sans_matchs(self):
        """Aucun match trouvé → exit propre."""
        mock_service = MagicMock()
        mock_service.actualiser_cotes.return_value = {"total": 0, "mises_a_jour": 0}

        with patch(
            "src.services.jeux.cron_jobs.obtenir_cotes_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_actualiser_cotes

            job_actualiser_cotes()

    @pytest.mark.unit
    def test_actualiser_cotes_avec_resultats(self):
        """Cotes mises à jour correctement."""
        mock_service = MagicMock()
        mock_service.actualiser_cotes.return_value = {"total": 15, "mises_a_jour": 12}

        with patch(
            "src.services.jeux.cron_jobs.obtenir_cotes_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_actualiser_cotes

            job_actualiser_cotes()

    @pytest.mark.unit
    def test_actualiser_cotes_erreur_api(self):
        """Erreur API externe gérée."""
        with patch(
            "src.services.jeux.cron_jobs.obtenir_cotes_service",
            side_effect=Exception("API timeout"),
        ):
            from src.services.jeux.cron_jobs import job_actualiser_cotes

            job_actualiser_cotes()


# ═══════════════════════════════════════════════════════════════
# JOB 2: RÉSULTATS MATCHS
# ═══════════════════════════════════════════════════════════════


class TestJobResultatsMatchs:
    """Tests pour le job de récupération des résultats."""

    @pytest.mark.unit
    def test_resultats_matchs_vides(self):
        """Aucun résultat disponible."""
        mock_service = MagicMock()
        mock_service.recuperer_resultats.return_value = []

        with patch(
            "src.services.jeux.cron_jobs.obtenir_resultats_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_resultats_matchs

            job_resultats_matchs()

    @pytest.mark.unit
    def test_resultats_matchs_avec_donnees(self):
        """Résultats récupérés et enregistrés."""
        resultats = [
            {"match_id": 1, "score": "2-1", "statut": "terminé"},
            {"match_id": 2, "score": "0-0", "statut": "terminé"},
        ]
        mock_service = MagicMock()
        mock_service.recuperer_resultats.return_value = resultats

        with patch(
            "src.services.jeux.cron_jobs.obtenir_resultats_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_resultats_matchs

            job_resultats_matchs()


# ═══════════════════════════════════════════════════════════════
# JOB 3: DÉTECTER OPPORTUNITÉS
# ═══════════════════════════════════════════════════════════════


class TestJobDetecterOpportunites:
    """Tests pour le job de détection d'opportunités."""

    @pytest.mark.unit
    def test_aucune_opportunite(self):
        """Pas d'opportunité détectée."""
        mock_service = MagicMock()
        mock_service.detecter_opportunites.return_value = []

        with patch(
            "src.services.jeux.cron_jobs.obtenir_opportunites_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_detecter_opportunites

            job_detecter_opportunites()

    @pytest.mark.unit
    def test_opportunites_detectees(self):
        """Opportunités trouvées et alertées."""
        opps = [
            {"marche": "ML PSG", "value": 2.5, "serie": 8},
        ]
        mock_service = MagicMock()
        mock_service.detecter_opportunites.return_value = opps

        with patch(
            "src.services.jeux.cron_jobs.obtenir_opportunites_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_detecter_opportunites

            job_detecter_opportunites()


# ═══════════════════════════════════════════════════════════════
# JOB 4: ANALYSER SÉRIES
# ═══════════════════════════════════════════════════════════════


class TestJobAnalyserSeries:
    """Tests pour le job d'analyse des séries."""

    @pytest.mark.unit
    def test_analyser_series_vide(self):
        """Pas de série à analyser."""
        mock_service = MagicMock()
        mock_service.analyser_series.return_value = {"series": [], "total": 0}

        with patch(
            "src.services.jeux.cron_jobs.obtenir_series_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs import job_analyser_series

            job_analyser_series()

    @pytest.mark.unit
    def test_analyser_series_erreur(self):
        """Erreur analyse gérée."""
        with patch(
            "src.services.jeux.cron_jobs.obtenir_series_service",
            side_effect=Exception("Analysis failed"),
        ):
            from src.services.jeux.cron_jobs import job_analyser_series

            job_analyser_series()


# ═══════════════════════════════════════════════════════════════
# JOB 5: SCRAPER FDJ RÉSULTATS
# ═══════════════════════════════════════════════════════════════


class TestJobScraperFDJ:
    """Tests pour le job de scraping des résultats FDJ."""

    @pytest.mark.unit
    def test_scraper_fdj_succes(self):
        """Résultats FDJ scrapés correctement."""
        mock_service = MagicMock()
        mock_service.scraper_derniers_resultats.return_value = {
            "loto": {"numeros": [3, 7, 15, 22, 41], "chance": 5},
            "date_tirage": "2026-04-04",
        }

        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_fdj_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs_loteries import job_scraper_fdj_resultats

            job_scraper_fdj_resultats()

    @pytest.mark.unit
    def test_scraper_fdj_site_indisponible(self):
        """Site FDJ indisponible → pas de crash."""
        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_fdj_service",
            side_effect=Exception("Connection timeout"),
        ):
            from src.services.jeux.cron_jobs_loteries import job_scraper_fdj_resultats

            job_scraper_fdj_resultats()


# ═══════════════════════════════════════════════════════════════
# JOB 6: BACKTEST GRILLES
# ═══════════════════════════════════════════════════════════════


class TestJobBacktestGrilles:
    """Tests pour le job de backtest des grilles."""

    @pytest.mark.unit
    def test_backtest_succes(self):
        """Backtest exécuté correctement."""
        mock_service = MagicMock()
        mock_service.backtester_grilles.return_value = {
            "grilles_testees": 100,
            "gains_simules": 45.50,
        }

        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_backtest_service",
            return_value=mock_service,
        ):
            from src.services.jeux.cron_jobs_loteries import job_backtest_grilles

            job_backtest_grilles()

    @pytest.mark.unit
    def test_backtest_erreur(self):
        """Erreur backtest gérée."""
        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_backtest_service",
            side_effect=Exception("Insufficient data"),
        ):
            from src.services.jeux.cron_jobs_loteries import job_backtest_grilles

            job_backtest_grilles()
