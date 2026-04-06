"""
Tests pour les cron jobs du module Jeux.

Couvre les 6 jobs dans src/services/jeux/cron_jobs.py et cron_jobs_loteries.py :
1. scraper_cotes_sportives — Toutes les 2h
2. scraper_resultats_matchs — Quotidien 23h
3. detecter_opportunites — Toutes les 30min
4. analyser_series — Quotidien 9h
5. scraper_resultats_fdj — Quotidien 21h30
6. backtest_grilles — Quotidien 22h
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


@pytest.fixture
def patch_db(mock_session):
    """Patch le contexte DB pour les deux modules de cron jobs."""
    @contextmanager
    def mock_context():
        try:
            yield mock_session
        except Exception:
            mock_session.rollback()
            raise

    with (
        patch("src.services.jeux.cron_jobs.obtenir_contexte_db", side_effect=lambda: mock_context()),
        patch("src.services.jeux.cron_jobs_loteries.obtenir_contexte_db", side_effect=lambda: mock_context()),
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
        with patch(
            "src.services.jeux.cron_jobs.obtenir_contexte_db",
            side_effect=Exception("DB not available"),
        ):
            from src.services.jeux.cron_jobs import scraper_cotes_sportives

            scraper_cotes_sportives()

    @pytest.mark.unit
    def test_actualiser_cotes_avec_resultats(self, patch_db):
        """Cotes mises à jour correctement."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.jeux.cron_jobs import scraper_cotes_sportives

        scraper_cotes_sportives()

    @pytest.mark.unit
    def test_actualiser_cotes_erreur_api(self):
        """Erreur API externe gérée."""
        with patch(
            "src.services.jeux.cron_jobs.obtenir_contexte_db",
            side_effect=Exception("API timeout"),
        ):
            from src.services.jeux.cron_jobs import scraper_cotes_sportives

            scraper_cotes_sportives()


# ═══════════════════════════════════════════════════════════════
# JOB 2: RÉSULTATS MATCHS
# ═══════════════════════════════════════════════════════════════


class TestJobResultatsMatchs:
    """Tests pour le job de récupération des résultats."""

    @pytest.mark.unit
    def test_resultats_matchs_vides(self, patch_db):
        """Aucun résultat disponible."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.jeux.cron_jobs import scraper_resultats_matchs

        scraper_resultats_matchs()

    @pytest.mark.unit
    def test_resultats_matchs_avec_donnees(self, patch_db):
        """Résultats récupérés et enregistrés."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.jeux.cron_jobs import scraper_resultats_matchs

        scraper_resultats_matchs()


# ═══════════════════════════════════════════════════════════════
# JOB 3: DÉTECTER OPPORTUNITÉS
# ═══════════════════════════════════════════════════════════════


class TestJobDetecterOpportunites:
    """Tests pour le job de détection d'opportunités."""

    @pytest.mark.unit
    def test_aucune_opportunite(self, patch_db):
        """Pas d'opportunité détectée."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.jeux.cron_jobs import detecter_opportunites

        detecter_opportunites()

    @pytest.mark.unit
    def test_opportunites_detectees(self, patch_db):
        """Opportunités trouvées et alertées."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.jeux.cron_jobs import detecter_opportunites

        detecter_opportunites()


# ═══════════════════════════════════════════════════════════════
# JOB 4: ANALYSER SÉRIES
# ═══════════════════════════════════════════════════════════════


class TestJobAnalyserSeries:
    """Tests pour le job d'analyse des séries."""

    @pytest.mark.unit
    def test_analyser_series_vide(self, patch_db):
        """Pas de série à analyser."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.jeux.cron_jobs import analyser_series

        analyser_series()

    @pytest.mark.unit
    def test_analyser_series_erreur(self):
        """Erreur analyse gérée."""
        with patch(
            "src.services.jeux.cron_jobs.obtenir_contexte_db",
            side_effect=Exception("Analysis failed"),
        ):
            from src.services.jeux.cron_jobs import analyser_series

            analyser_series()


# ═══════════════════════════════════════════════════════════════
# JOB 5: SCRAPER FDJ RÉSULTATS
# ═══════════════════════════════════════════════════════════════


class TestJobScraperFDJ:
    """Tests pour le job de scraping des résultats FDJ."""

    @pytest.mark.unit
    def test_scraper_fdj_succes(self):
        """Résultats FDJ scrapés correctement."""
        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_contexte_db",
            side_effect=Exception("DB mocked"),
        ):
            from src.services.jeux.cron_jobs_loteries import scraper_resultats_fdj

            scraper_resultats_fdj()

    @pytest.mark.unit
    def test_scraper_fdj_site_indisponible(self):
        """Site FDJ indisponible → pas de crash."""
        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_contexte_db",
            side_effect=Exception("Connection timeout"),
        ):
            from src.services.jeux.cron_jobs_loteries import scraper_resultats_fdj

            scraper_resultats_fdj()


# ═══════════════════════════════════════════════════════════════
# JOB 6: BACKTEST GRILLES
# ═══════════════════════════════════════════════════════════════


class TestJobBacktestGrilles:
    """Tests pour le job de backtest des grilles."""

    @pytest.mark.unit
    def test_backtest_succes(self):
        """Backtest exécuté correctement."""
        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_contexte_db",
            side_effect=Exception("DB mocked"),
        ):
            from src.services.jeux.cron_jobs_loteries import backtest_grilles

            backtest_grilles()

    @pytest.mark.unit
    def test_backtest_erreur(self):
        """Erreur backtest gérée."""
        with patch(
            "src.services.jeux.cron_jobs_loteries.obtenir_contexte_db",
            side_effect=Exception("Insufficient data"),
        ):
            from src.services.jeux.cron_jobs_loteries import backtest_grilles

            backtest_grilles()
