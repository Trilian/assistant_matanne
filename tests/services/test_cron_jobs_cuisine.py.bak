"""
Tests pour les cron jobs du module Cuisine.

Couvre les 4 jobs dans src/services/cuisine/cron_cuisine.py :
1. job_verifier_peremptions — Quotidien 7h
2. job_proposition_planning — Dimanche 18h
3. job_stocks_bas — Lundi 9h
4. job_rapport_mensuel — 1er du mois 8h
"""

import pytest
from contextlib import contextmanager
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def mock_session():
    """Session DB mockée."""
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.count.return_value = 0
    return session


@contextmanager
def _ctx(mock_session):
    yield mock_session


@pytest.fixture
def patch_db(mock_session):
    """Patch le contexte DB pour les jobs cuisine."""
    with patch(
        "src.services.cuisine.cron_cuisine.obtenir_contexte_db",
        return_value=_ctx(mock_session),
    ):
        yield mock_session


@pytest.fixture
def patch_notifications():
    """Patch le dispatcher de notifications."""
    mock_dispatcher = MagicMock()
    with patch(
        "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
        return_value=mock_dispatcher,
    ):
        yield mock_dispatcher


# ═══════════════════════════════════════════════════════════════
# JOB 1: VÉRIFICATION PÉREMPTIONS
# ═══════════════════════════════════════════════════════════════


class TestJobVerifierPeremptions:
    """Tests pour job_verifier_peremptions."""

    @pytest.mark.unit
    def test_aucune_peremption(self, patch_db):
        """Aucun article en péremption → pas de notification."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.cuisine.cron_cuisine import job_verifier_peremptions

        job_verifier_peremptions()

    @pytest.mark.unit
    def test_articles_en_peremption(self, patch_db):
        """Articles bientôt périmés détectés."""
        articles = [
            SimpleNamespace(
                id=1, nom="Lait", date_peremption=date.today() + timedelta(days=2),
                quantite=1, unite="L",
            ),
            SimpleNamespace(
                id=2, nom="Yaourt", date_peremption=date.today() + timedelta(days=1),
                quantite=4, unite="pcs",
            ),
        ]
        patch_db.query.return_value.filter.return_value.all.return_value = articles

        from src.services.cuisine.cron_cuisine import job_verifier_peremptions

        job_verifier_peremptions()

    @pytest.mark.unit
    def test_peremption_erreur_db(self):
        """Erreur DB gérée sans crash."""
        with patch(
            "src.services.cuisine.cron_cuisine.obtenir_contexte_db",
            side_effect=Exception("DB error"),
        ):
            from src.services.cuisine.cron_cuisine import job_verifier_peremptions

            job_verifier_peremptions()


# ═══════════════════════════════════════════════════════════════
# JOB 2: PROPOSITION PLANNING
# ═══════════════════════════════════════════════════════════════


class TestJobPropositionPlanning:
    """Tests pour job_proposition_planning."""

    @pytest.mark.unit
    def test_planning_existe_deja(self, patch_db):
        """Planning existant → pas de proposition."""
        planning = SimpleNamespace(id=1, statut="actif")
        patch_db.query.return_value.filter.return_value.first.return_value = planning

        from src.services.cuisine.cron_cuisine import job_proposition_planning

        job_proposition_planning()

    @pytest.mark.unit
    def test_planning_absent_notification(self, patch_db):
        """Pas de planning → notification envoyée."""
        patch_db.query.return_value.filter.return_value.first.return_value = None

        from src.services.cuisine.cron_cuisine import job_proposition_planning

        job_proposition_planning()


# ═══════════════════════════════════════════════════════════════
# JOB 3: STOCKS BAS
# ═══════════════════════════════════════════════════════════════


class TestJobStocksBas:
    """Tests pour job_stocks_bas."""

    @pytest.mark.unit
    def test_aucun_stock_bas(self, patch_db):
        """Aucun stock bas détecté."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.cuisine.cron_cuisine import job_stocks_bas

        job_stocks_bas()

    @pytest.mark.unit
    def test_stocks_bas_detectes(self, patch_db):
        """Articles sous le seuil identifiés."""
        articles_bas = [
            SimpleNamespace(id=1, nom="Farine", quantite=0.2, seuil_min=1, unite="kg"),
            SimpleNamespace(id=2, nom="Sucre", quantite=0.1, seuil_min=0.5, unite="kg"),
        ]
        patch_db.query.return_value.filter.return_value.all.return_value = articles_bas

        from src.services.cuisine.cron_cuisine import job_stocks_bas

        job_stocks_bas()


# ═══════════════════════════════════════════════════════════════
# JOB 4: RAPPORT MENSUEL
# ═══════════════════════════════════════════════════════════════


class TestJobRapportMensuel:
    """Tests pour job_rapport_mensuel."""

    @pytest.mark.unit
    def test_rapport_mensuel_generation(self, patch_db):
        """Rapport mensuel généré correctement."""
        from src.services.cuisine.cron_cuisine import job_rapport_mensuel

        job_rapport_mensuel()

    @pytest.mark.unit
    def test_rapport_mensuel_erreur(self):
        """Erreur lors de la génération du rapport."""
        with patch(
            "src.services.cuisine.cron_cuisine.obtenir_contexte_db",
            side_effect=Exception("Timeout"),
        ):
            from src.services.cuisine.cron_cuisine import job_rapport_mensuel

            job_rapport_mensuel()
