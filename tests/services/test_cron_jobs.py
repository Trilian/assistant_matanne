"""
T3 — Tests jobs cron APScheduler.

Couvre src/services/core/cron/jobs.py :
- Présence des jobs dans le scheduler
- Vérification SQL correct (articles_courses, pas liste_courses)
- Alertes péremption 48h
- Structure résumé hebdo
- Push contextuel soir
- Rapport mensuel budget
- Pas d'accès privé à ._subscriptions
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch, call
import logging

import pytest


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def demarreur_cron():
    """Crée un DémarreurCron sans démarrer le scheduler."""
    from src.services.core.cron.jobs import DémarreurCron
    d = DémarreurCron()
    yield d
    # Pas de start → pas besoin de stop


# ═══════════════════════════════════════════════════════════
# T3a — Jobs présents dans le scheduler
# ═══════════════════════════════════════════════════════════


class TestJobsSchedules:
    """Vérifie que les jobs critiques sont enregistrés."""

    def test_job_rappels_famille_present(self, demarreur_cron):
        """rappels_famille doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "rappels_famille" in job_ids

    def test_job_alertes_peremption_present(self, demarreur_cron):
        """alertes_peremption_48h doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "alertes_peremption_48h" in job_ids

    def test_job_resume_hebdo_present(self, demarreur_cron):
        """resume_hebdo doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "resume_hebdo" in job_ids

    def test_job_push_contextuel_soir_present(self, demarreur_cron):
        """push_contextuel_soir doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "push_contextuel_soir" in job_ids

    def test_job_rappel_courses_present(self, demarreur_cron):
        """rappel_courses doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "rappel_courses" in job_ids

    def test_job_digest_queue_present(self, demarreur_cron):
        """digest_notifications_queue doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "digest_notifications_queue" in job_ids

    def test_job_sync_calendrier_scolaire_present(self, demarreur_cron):
        """sync_calendrier_scolaire doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "sync_calendrier_scolaire" in job_ids

    def test_job_rapport_mensuel_present(self, demarreur_cron):
        """rapport_mensuel_budget doit être dans le scheduler."""
        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]
        assert "rapport_mensuel_budget" in job_ids

    def test_nombre_minimal_jobs(self, demarreur_cron):
        """Le scheduler doit contenir au moins 15 jobs enregistrés."""
        assert len(demarreur_cron._scheduler.get_jobs()) >= 15


# ═══════════════════════════════════════════════════════════
# T3b — SQL correct dans _job_rappel_courses_ntfy
# ═══════════════════════════════════════════════════════════


class TestRappelCoursesSQL:
    """Vérifie que le job utilise articles_courses (et non liste_courses)."""

    def test_sql_utilise_articles_courses(self):
        """Le code source du job contient 'articles_courses', pas 'liste_courses'."""
        import inspect
        from src.services.core.cron import jobs as cron_module

        source = inspect.getsource(cron_module._job_rappel_courses_ntfy)
        assert "articles_courses" in source
        assert "liste_courses" not in source

    def test_job_rappel_courses_avec_mock_db(self):
        """_job_rappel_courses_ntfy exécuté avec une DB mockée retourne sans lever d'exception."""
        from src.services.core.cron.jobs import _job_rappel_courses_ntfy

        mock_scalar = MagicMock(return_value=0)
        mock_execute = MagicMock(return_value=MagicMock(scalar=mock_scalar, fetchall=MagicMock(return_value=[])))
        mock_session = MagicMock()
        mock_session.execute = mock_execute

        @contextmanager
        def _ctx():
            yield mock_session

        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):
            # 0 articles → log debug, pas d'envoi
            _job_rappel_courses_ntfy()  # Ne doit pas lever d'exception


# ═══════════════════════════════════════════════════════════
# T3c — Alertes péremption 48h
# ═══════════════════════════════════════════════════════════


class TestAlertesPeremption:
    """Tests _job_alertes_peremption_48h."""

    def test_articles_a_perimer_detectes(self):
        """Articles avec date_peremption à J+1 doivent être détectés et notifiés."""
        from src.services.core.cron.jobs import _job_alertes_peremption_48h

        demain = date.today() + timedelta(days=1)
        article_a = SimpleNamespace(nom="Yaourt", date_peremption=demain, quantite=2)
        article_b = SimpleNamespace(nom="Lait", date_peremption=demain, quantite=1)

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = [
            article_a, article_b
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
            _job_alertes_peremption_48h()

        # Dispatcher doit avoir été appelé
        mock_dispatcher.envoyer.assert_called_once()
        args = mock_dispatcher.envoyer.call_args
        message = args[1].get("message") or args[0][1] if args[0] else args[1]["message"]
        assert "Yaourt" in message or "Lait" in message

    def test_aucun_article_aucune_notification(self):
        """Sans article à périmé, le dispatcher ne doit pas être appelé."""
        from src.services.core.cron.jobs import _job_alertes_peremption_48h

        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []

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
            _job_alertes_peremption_48h()

        mock_dispatcher.envoyer.assert_not_called()


# ═══════════════════════════════════════════════════════════
# T3d — Structure résumé hebdo
# ═══════════════════════════════════════════════════════════


class TestResumeHebdo:
    """Tests _job_resume_hebdo."""

    def test_resume_hebdo_appelle_dispatcher(self):
        """_job_resume_hebdo doit appeler le dispatcher avec les sections attendues."""
        from src.services.core.cron.jobs import _job_resume_hebdo

        mock_resume = SimpleNamespace(
            semaine="2025-W01",
            resume_narratif="Super semaine",
            score_semaine=85,
            repas=SimpleNamespace(nb_repas_realises=5),
            budget=SimpleNamespace(total_depenses=120.0),
            activites=SimpleNamespace(nb_activites=3),
            taches=SimpleNamespace(nb_taches_realisees=8),
        )
        mock_service = MagicMock()
        mock_service.generer_resume_semaine_sync.return_value = mock_resume

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {}

        with (
            patch(
                "src.services.famille.resume_hebdo.obtenir_service_resume_hebdo",
                return_value=mock_service,
            ),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
        ):
            _job_resume_hebdo()

        mock_dispatcher.envoyer.assert_called_once()
        call_kwargs = mock_dispatcher.envoyer.call_args[1]
        assert "titre" in call_kwargs
        assert "2025-W01" in call_kwargs["titre"]


# ═══════════════════════════════════════════════════════════
# T3e — Push contextuel soir
# ═══════════════════════════════════════════════════════════


class TestPushContextuelSoir:
    """Tests _job_push_contextuel_soir."""

    def test_push_soir_appelle_dispatcher(self):
        """_job_push_contextuel_soir doit appeler le dispatcher avec ntfy + push."""
        from src.services.core.cron.jobs import _job_push_contextuel_soir

        mock_session = MagicMock()
        # Aucun repas demain
        mock_session.query.return_value.filter.return_value.all.return_value = []
        mock_session.query.return_value.filter.return_value.limit.return_value.all.return_value = []

        mock_dispatcher = MagicMock()
        mock_dispatcher.envoyer.return_value = {}
        mock_meteo = MagicMock()
        mock_meteo.get_previsions.side_effect = Exception("Météo indisponible")

        @contextmanager
        def _ctx():
            yield mock_session

        with (
            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),
            patch(
                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
                return_value=mock_dispatcher,
            ),
            patch("src.services.integrations.weather.obtenir_service_meteo", return_value=mock_meteo),
        ):
            _job_push_contextuel_soir()

        mock_dispatcher.envoyer.assert_called_once()
        call_kwargs = mock_dispatcher.envoyer.call_args[1]
        # Nouveau comportement: push en canal primaire + fallback géré par stratégie
        assert "push" in call_kwargs.get("canaux", [])
        assert call_kwargs.get("strategie") == "failover"


# ═══════════════════════════════════════════════════════════
# T3f — Rapport mensuel budget
# ═══════════════════════════════════════════════════════════


class TestRapportMensuelBudget:
    """Tests _job_rapport_mensuel_budget."""

    def test_rapport_mensuel_appelle_dispatcher(self):
        """_job_rapport_mensuel_budget doit appeler le dispatcher avec les totaux."""
        from src.services.core.cron.jobs import _job_rapport_mensuel_budget

        mock_session = MagicMock()
        # Retourne des valeurs scalaires pour les SUM
        mock_session.query.return_value.filter.return_value.scalar.return_value = 100.0

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
            _job_rapport_mensuel_budget()

        mock_dispatcher.envoyer.assert_called_once()


# ═══════════════════════════════════════════════════════════
# T3g — Pas d'accès ._subscriptions dans les jobs
# ═══════════════════════════════════════════════════════════


class TestPushServiceAccesPublic:
    """Vérifie que les jobs cron n'utilisent pas l'attribut privé ._subscriptions."""

    def test_jobs_no_private_subscriptions_access(self):
        """Le code source des jobs ne doit pas contenir '._subscriptions'."""
        import inspect
        from src.services.core.cron import jobs as cron_module

        # Vérifier toutes les fonctions de job
        job_fns = [
            cron_module._job_push_quotidien,
            cron_module._job_push_contextuel_soir,
            cron_module._job_rappels_famille,
        ]
        for fn in job_fns:
            source = inspect.getsource(fn)
            assert "._subscriptions" not in source, (
                f"{fn.__name__} contient un accès privé ._subscriptions."
                " Utiliser obtenir_abonnes() à la place."
            )

    def test_push_quotidien_utilise_charger_abonnements_db(self):
        """_job_push_quotidien doit utiliser charger_tous_abonnements_actifs_db() ou obtenir_abonnes()."""
        import inspect
        from src.services.core.cron import jobs as cron_module

        source = inspect.getsource(cron_module._job_push_quotidien)
        assert (
            "charger_tous_abonnements_actifs_db" in source
            or "obtenir_abonnes" in source
        ), "_job_push_quotidien doit utiliser la méthode publique d'abonnements."


# ═══════════════════════════════════════════════════════════
# T2 — Error handling jobs cron
# ═══════════════════════════════════════════════════════════


class TestCronErrorHandling:
    """Valide que les jobs absorbent les erreurs et journalisent l'échec."""

    def test_job_rappels_famille_capture_exception(self, caplog):
        """Une exception service ne doit pas remonter hors du job."""
        from src.services.core.cron.jobs import _job_rappels_famille

        with patch("src.services.famille.rappels.ServiceRappelsFamille") as mock_service_cls:
            mock_service_cls.return_value.envoyer_rappels_du_jour.side_effect = RuntimeError("boom")
            with caplog.at_level(logging.ERROR):
                _job_rappels_famille()

        assert "Erreur lors des rappels famille" in caplog.text

    def test_job_rappel_courses_capture_exception_db(self, caplog):
        """Une erreur DB dans le rappel courses est gérée sans lever d'exception."""
        from src.services.core.cron.jobs import _job_rappel_courses_ntfy

        with patch("src.core.db.obtenir_contexte_db", side_effect=RuntimeError("db down")):
            with caplog.at_level(logging.DEBUG):
                _job_rappel_courses_ntfy()

        assert "Impossible de compter les articles en attente" in caplog.text


class TestDigestQueueCron:
    """Tests du flush automatique de la queue digest notifications (Phase 8.4)."""

    def test_digest_queue_flush_appelle_dispatcher(self):
        """Le job doit vider le digest pour chaque utilisateur en attente."""
        from src.services.core.cron.jobs import _job_digest_notifications_queue

        mock_dispatcher = MagicMock()
        mock_dispatcher.lister_users_digest_pending.return_value = ["u1", "u2"]
        mock_dispatcher.vider_digest.side_effect = [{"email": True}, {"ntfy": True}]

        with patch(
            "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
            return_value=mock_dispatcher,
        ):
            _job_digest_notifications_queue()

        assert mock_dispatcher.vider_digest.call_count == 2
        mock_dispatcher.vider_digest.assert_any_call("u1")
        mock_dispatcher.vider_digest.assert_any_call("u2")


class TestJobExecutionsPersistence:
    """Tests ciblés Phase 7: persistance explicite dans job_executions."""

    def test_executer_job_trace_persiste_insert_et_update_success(self):
        """Une exécution normale doit faire INSERT puis UPDATE sur job_executions."""
        from src.services.core.cron.jobs import _executer_job_trace

        session_insert = MagicMock()
        result_insert = MagicMock()
        result_insert.scalar.return_value = 123
        session_insert.execute.return_value = result_insert

        session_update = MagicMock()

        @contextmanager
        def _ctx_insert():
            yield session_insert

        @contextmanager
        def _ctx_update():
            yield session_update

        with patch(
            "src.core.db.obtenir_contexte_db",
            side_effect=[_ctx_insert(), _ctx_update()],
        ):
            result = _executer_job_trace(
                job_id="job_test_persist",
                job_name="Job Test Persist",
                fonction=lambda: None,
                dry_run=False,
                source="manual",
                triggered_by_user_id="42",
            )

        assert result["status"] == "ok"
        assert session_insert.execute.called
        assert session_update.execute.called
        assert "INSERT INTO job_executions" in str(session_insert.execute.call_args[0][0])
        assert "UPDATE job_executions" in str(session_update.execute.call_args[0][0])

    def test_executer_job_trace_persiste_statut_dry_run(self):
        """Un dry-run doit aussi persister un statut dry_run avec UPDATE."""
        from src.services.core.cron.jobs import _executer_job_trace

        session_insert = MagicMock()
        result_insert = MagicMock()
        result_insert.scalar.return_value = 456
        session_insert.execute.return_value = result_insert

        session_update = MagicMock()

        @contextmanager
        def _ctx_insert():
            yield session_insert

        @contextmanager
        def _ctx_update():
            yield session_update

        with patch(
            "src.core.db.obtenir_contexte_db",
            side_effect=[_ctx_insert(), _ctx_update()],
        ):
            result = _executer_job_trace(
                job_id="job_test_dry",
                job_name="Job Test Dry",
                fonction=lambda: None,
                dry_run=True,
                source="manual",
                triggered_by_user_id="42",
            )

        assert result["status"] == "dry_run"
        assert result["dry_run"] is True
        assert session_insert.execute.called
        assert session_update.execute.called

        params_update = session_update.execute.call_args[0][1]
        assert params_update["status"] == "dry_run"
