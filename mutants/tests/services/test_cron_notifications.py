"""
Tests — Jobs CRON additionnels (notifications).

Couvre src/services/core/cron/jobs.py :
- rappel_documents: rappel_documents_expirants (quotidien)
- rapport_mensuel: rapport_mensuel_auto (mensuel)
- bilan_energetique: bilan_energetique (mensuel)
- rappel_vaccins: rappel_vaccins (hebdo)
- sync_entretien_budget: sync_entretien_budget
- sync_voyages_calendrier: sync_voyages_calendrier
- sync_charges_dashboard: sync_charges_dashboard

Tests inter-modules dans src/services/core/events/subscribers.py :
- Entretien → Budget
- Voyages → Calendrier
- Charges → Dashboard
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════
# P8-SCHED — Jobs présents dans le scheduler
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def demarreur_cron():
    """Crée un DémarreurCron sans démarrer le scheduler."""
    from src.services.core.cron.jobs import DémarreurCron

    d = DémarreurCron()
    yield d


class TestNotificationJobsSchedules:
    """Vérifie que les jobs de notifications sont enregistrés dans le scheduler."""

    NOTIFICATION_JOBS = [
        "rappel_documents_expirants",
        "rapport_mensuel_auto",
        "bilan_energetique",
        "rappel_vaccins",
        "sync_entretien_budget",
        "sync_voyages_calendrier",
        "sync_charges_dashboard",
    ]

    def test_tous_les_jobs_notifications_presents(self, demarreur_cron):
        """Tous les jobs de notifications doivent être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        for job_id in self.NOTIFICATION_JOBS:
            assert job_id in job_ids, f"Job '{job_id}' manquant dans le scheduler"

    def test_jobs_notifications_dans_registre(self):
        """Tous les jobs de notifications doivent être dans le registre."""
        from src.services.core.cron.jobs import lister_jobs_disponibles

        jobs = lister_jobs_disponibles()
        for job_id in self.NOTIFICATION_JOBS:
            assert job_id in jobs, f"Job '{job_id}' manquant dans le registre"


# ═══════════════════════════════════════════════════════════
# Rappel documents expirants
# ═══════════════════════════════════════════════════════════


class TestRappelDocumentsExpirants:

    def test_documents_urgents_notifies(self):
        """Documents expirant sous 7 jours → notification push + ntfy + email."""
        from src.services.core.cron.jobs import _job_rappel_documents_expirants

        dans_3j = date.today() + timedelta(days=3)
        doc = SimpleNamespace(
            titre="Carte identité",
            membre_famille="Mathieu",
            date_expiration=dans_3j,
            jours_avant_expiration=3,
            actif=True,
        )

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [doc]

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {}

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_rappel_documents_expirants()

        mock_dispatcher.envoyer.assert_called()
        call_kwargs = mock_dispatcher.envoyer.call_args[1]
        assert "Carte identité" in call_kwargs.get("message", "")
        assert "email" in call_kwargs.get("canaux", [])

    def test_aucun_document_aucune_notification(self):
        """Sans document expirant, le dispatcher ne doit pas être appelé."""
        from src.services.core.cron.jobs import _job_rappel_documents_expirants

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

        mock_dispatcher = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_rappel_documents_expirants()

        mock_dispatcher.envoyer.assert_not_called()


# ═══════════════════════════════════════════════════════════
# rapport_mensuel — Rapport mensuel auto
# ═══════════════════════════════════════════════════════════


class TestRapportMensuelAuto:

    def test_rapport_mensuel_envoye(self):
        """Le rapport mensuel doit être envoyé avec dépenses et projets."""
        from src.services.core.cron.jobs import _job_rapport_mensuel_auto

        mock_session = MagicMock()
        # func.sum → total dépenses
        mock_session.query.return_value.filter.return_value.scalar.return_value = Decimal("450.00")
        # count projets
        mock_session.query.return_value.filter.return_value.count.return_value = 2
        # budget
        mock_session.query.return_value.filter.return_value.first.return_value = SimpleNamespace(
            budget_total=Decimal("3000.00")
        )
        # relevés énergie
        mock_session.query.return_value.filter.return_value.all.return_value = [
            SimpleNamespace(type_energie="electricite", consommation=Decimal("120.5"), unite="kWh", montant=Decimal("25.00")),
        ]

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {}

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_rapport_mensuel_auto()

        mock_dispatcher.envoyer.assert_called()


# ═══════════════════════════════════════════════════════════
# bilan_energetique — Bilan énergétique
# ═══════════════════════════════════════════════════════════


class TestBilanEnergetique:

    def test_bilan_avec_comparaison_annee_precedente(self):
        """Bilan énergie avec comparaison N-1 → notification envoyée."""
        from src.services.core.cron.jobs import _job_bilan_energetique

        mock_session = MagicMock()
        # Types d'énergie distincts
        mock_session.query.return_value.distinct.return_value.all.return_value = [("electricite",)]
        # Relevé actuel
        releve_actuel = SimpleNamespace(consommation=Decimal("150.0"), montant=Decimal("30.00"), unite="kWh")
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            releve_actuel,  # releve actuel
            SimpleNamespace(consommation=Decimal("130.0")),  # releve N-1
        ]
        # Moyenne 12m
        mock_session.query.return_value.filter.return_value.scalar.return_value = Decimal("140.0")

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {}

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_bilan_energetique()

        mock_dispatcher.envoyer.assert_called()


# ═══════════════════════════════════════════════════════════
# rappel_vaccins — Rappels vaccins
# ═══════════════════════════════════════════════════════════


class TestRappelVaccins:

    def test_vaccins_en_retard_notifies(self):
        """Vaccins obligatoires en retard → notification urgente."""
        from src.services.core.cron.jobs import _job_rappel_vaccins

        hier = date.today() - timedelta(days=1)
        vaccin_retard = SimpleNamespace(
            nom_vaccin="DTP",
            type_vaccin="obligatoire",
            fait=False,
            rappel_prevu=hier,
        )

        dans_5j = date.today() + timedelta(days=5)
        vaccin_proche = SimpleNamespace(
            nom_vaccin="ROR",
            type_vaccin="recommandé",
            fait=False,
            rappel_prevu=dans_5j,
        )

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [vaccin_proche]
        mock_session.query.return_value.filter.return_value.all.return_value = [vaccin_retard]

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {}

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_rappel_vaccins()

        assert mock_dispatcher.envoyer.call_count >= 1

    def test_aucun_vaccin_aucune_notification(self):
        """Sans vaccin à signaler, pas de notification."""
        from src.services.core.cron.jobs import _job_rappel_vaccins

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.all.return_value = []

        mock_dispatcher = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_rappel_vaccins()

        mock_dispatcher.envoyer.assert_not_called()


# ═══════════════════════════════════════════════════════════
# sync_entretien_budget — Sync entretien → budget
# ═══════════════════════════════════════════════════════════


class TestSyncEntretienBudget:

    def test_interventions_synchronisees(self):
        """Interventions facturées → dépenses maison créées."""
        from src.services.core.cron.jobs import _job_sync_entretien_budget

        intervention = SimpleNamespace(
            id=42,
            montant_facture=Decimal("250.00"),
            description="Réparation fuite",
            date_intervention=date.today() - timedelta(days=10),
        )

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [intervention]
        mock_session.query.return_value.filter.return_value.first.return_value = None  # pas de doublon
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()

        mock_bus = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch("src.services.core.events.bus.obtenir_bus", return_value=mock_bus),
        ):
            _job_sync_entretien_budget()

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_bus.emettre.assert_called_once()
        assert mock_bus.emettre.call_args[0][0] == "depenses.sync_entretien"


# ═══════════════════════════════════════════════════════════
# sync_voyages_calendrier — Sync voyages → calendrier
# ═══════════════════════════════════════════════════════════


class TestSyncVoyagesCalendrier:

    def test_voyage_planifie_cree_evenement(self):
        """Voyage planifié dans le futur → événement planning créé."""
        from src.services.core.cron.jobs import _job_sync_voyages_calendrier

        voyage = SimpleNamespace(
            id=7,
            titre="Weekend Bretagne",
            destination="Saint-Malo",
            date_depart=date.today() + timedelta(days=14),
            date_retour=date.today() + timedelta(days=16),
            type_voyage="weekend",
            statut="planifié",
            participants=["Mathieu", "Anne", "Jules"],
        )

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.all.return_value = [voyage]
        mock_session.query.return_value.filter.return_value.first.return_value = None  # pas de doublon
        mock_session.add = MagicMock()
        mock_session.commit = MagicMock()

        mock_bus = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch("src.services.core.events.bus.obtenir_bus", return_value=mock_bus),
        ):
            _job_sync_voyages_calendrier()

        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_bus.emettre.assert_called_once()
        assert mock_bus.emettre.call_args[0][0] == "planning.sync_voyages"


# ═══════════════════════════════════════════════════════════
# sync_charges_dashboard — Sync charges → dashboard
# ═══════════════════════════════════════════════════════════


class TestSyncChargesDashboard:

    def test_charges_emises_sur_bus(self):
        """Les charges fixes et dépenses doivent être émises sur le bus."""
        from src.services.core.cron.jobs import _job_sync_charges_dashboard

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.scalar.return_value = Decimal("850.00")

        mock_bus = MagicMock()

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch("src.services.core.events.bus.obtenir_bus", return_value=mock_bus),
        ):
            _job_sync_charges_dashboard()

        mock_bus.emettre.assert_called_once()
        event_data = mock_bus.emettre.call_args[0][1]
        assert event_data["depenses_mois"] == 850.0


# ═══════════════════════════════════════════════════════════
# INTER-MODULE SUBSCRIBERS
# ═══════════════════════════════════════════════════════════


class TestInterModuleSubscribers:

    def test_subscribers_notifications_enregistres(self):
        """Les subscribers de notifications doivent être enregistrés dans le bus."""
        from src.services.core.events.subscribers import enregistrer_subscribers

        # Reset le flag pour permettre le re-enregistrement
        import src.services.core.events.subscribers as mod
        mod._subscribers_enregistres = False

        with patch("src.services.core.events.bus.obtenir_bus") as mock_bus_fn:
            mock_bus = MagicMock()
            mock_bus_fn.return_value = mock_bus
            nb = enregistrer_subscribers()

        # Vérifier que les 3 nouveaux subscribers de notifications sont enregistrés
        souscriptions = [call[0][0] for call in mock_bus.souscrire.call_args_list]
        assert "depenses.sync_entretien" in souscriptions
        assert "planning.sync_voyages" in souscriptions
        assert "dashboard.charges_update" in souscriptions

        # Reset le flag pour éviter d'interférer avec d'autres tests
        mod._subscribers_enregistres = False

    def test_sync_entretien_vers_budget_invalide_cache(self):
        """Le subscriber entretien→budget doit invalider le cache budget/dashboard."""
        from src.services.core.events.bus import EvenementDomaine
        from src.services.core.events.subscribers import _sync_entretien_vers_budget

        event = EvenementDomaine(
            type="depenses.sync_entretien",
            data={"nb_depenses": 3},
            source="cron.sync_entretien_budget",
        )

        with patch("src.core.caching.obtenir_cache") as mock_cache_fn:
            mock_cache = MagicMock()
            mock_cache.invalidate.return_value = 5
            mock_cache_fn.return_value = mock_cache
            _sync_entretien_vers_budget(event)

        # Doit invalider budget, depenses et dashboard
        patterns = [call[1].get("pattern") or call[0][0] for call in mock_cache.invalidate.call_args_list]
        assert "budget" in patterns
        assert "depenses" in patterns
        assert "dashboard" in patterns
