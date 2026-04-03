"""

T3 â€” Tests jobs cron APScheduler.



Couvre src/services/core/cron/jobs.py :

- PrÃ©sence des jobs dans le scheduler

- VÃ©rification SQL correct (articles_courses, pas liste_courses)

- Alertes pÃ©remption 48h

- Structure rÃ©sumÃ© hebdo

- Push contextuel soir

- Rapport mensuel budget

- Pas d'accÃ¨s privÃ© Ã  ._subscriptions

"""



from __future__ import annotations



from contextlib import contextmanager

from datetime import date, timedelta

from types import SimpleNamespace

from unittest.mock import AsyncMock, MagicMock, patch, call

import logging



import pytest





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# FIXTURES

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





@pytest.fixture

def demarreur_cron():

    """Crée un DémarreurCron sans démarrer le scheduler."""

    from src.services.core.cron.jobs import DémarreurCron

    d = DémarreurCron()

    yield d

    # Pas de start â†’ pas besoin de stop





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3a â€” Jobs prÃ©sents dans le scheduler

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





class TestJobsSchedules:

    """VÃ©rifie que les jobs critiques sont enregistrÃ©s."""



    JOBS_SPRINT_15 = {

        "job_expiration_recettes_suggestion",

        "job_stock_prediction_reapprovisionnement",

        "job_variete_repas_alerte",

        "job_tendances_activites_famille",

        "job_energie_peak_detection",

        "job_nutrition_adultes_weekly",

        "job_briefing_matinal_push",

        "job_jardin_feedback_planning",

    }



    def test_job_rappels_famille_present(self, demarreur_cron):

        """rappels_famille doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "rappels_famille" in job_ids



    def test_job_alertes_peremption_present(self, demarreur_cron):

        """alertes_peremption_48h doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "alertes_peremption_48h" in job_ids



    def test_job_resume_hebdo_present(self, demarreur_cron):

        """resume_hebdo doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "resume_hebdo" in job_ids



    def test_job_push_contextuel_soir_present(self, demarreur_cron):

        """push_contextuel_soir doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "push_contextuel_soir" in job_ids



    def test_job_rappel_courses_present(self, demarreur_cron):

        """rappel_courses doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "rappel_courses" in job_ids



    def test_job_digest_queue_present(self, demarreur_cron):

        """digest_notifications_queue doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "digest_notifications_queue" in job_ids



    def test_job_digest_whatsapp_matinal_present(self, demarreur_cron):

        """digest_whatsapp_matinal doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "digest_whatsapp_matinal" in job_ids



    def test_job_sync_calendrier_scolaire_present(self, demarreur_cron):

        """sync_calendrier_scolaire doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "sync_calendrier_scolaire" in job_ids



    def test_job_rapport_mensuel_present(self, demarreur_cron):

        """rapport_mensuel_budget doit Ãªtre dans le scheduler."""

        job_ids = [j.id for j in demarreur_cron._scheduler.get_jobs()]

        assert "rapport_mensuel_budget" in job_ids



    def test_nombre_minimal_jobs(self, demarreur_cron):

        """Le scheduler doit contenir au moins 15 jobs enregistrÃ©s."""

        assert len(demarreur_cron._scheduler.get_jobs()) >= 15



    def test_jobs_sprint_15_presents(self, demarreur_cron):

        """Les 8 jobs du Sprint 15 doivent Ãªtre enregistrÃ©s dans le scheduler."""

        job_ids = {j.id for j in demarreur_cron._scheduler.get_jobs()}

        assert self.JOBS_SPRINT_15.issubset(job_ids)





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3b â€” SQL correct dans _job_rappel_courses_ntfy

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





class TestRappelCoursesSQL:

    """VÃ©rifie que le job utilise articles_courses (et non liste_courses)."""



    def test_sql_utilise_articles_courses(self):

        """Le code source du job contient 'articles_courses', pas 'liste_courses'."""

        import inspect

        from src.services.core.cron import jobs as cron_module



        source = inspect.getsource(cron_module._job_rappel_courses_ntfy)

        assert "articles_courses" in source

        assert "liste_courses" not in source



    def test_job_rappel_courses_avec_mock_db(self):

        """_job_rappel_courses_ntfy exÃ©cutÃ© avec une DB mockÃ©e retourne sans lever d'exception."""

        from src.services.core.cron.jobs import _job_rappel_courses_ntfy



        mock_scalar = MagicMock(return_value=0)

        mock_execute = MagicMock(return_value=MagicMock(scalar=mock_scalar, fetchall=MagicMock(return_value=[])))

        mock_session = MagicMock()

        mock_session.execute = mock_execute



        @contextmanager

        def _ctx():

            yield mock_session



        with patch("src.core.db.obtenir_contexte_db", return_value=_ctx()):

            # 0 articles â†’ log debug, pas d'envoi

            _job_rappel_courses_ntfy()  # Ne doit pas lever d'exception





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3c â€” Alertes pÃ©remption 48h

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





class TestAlertesPeremption:

    """Tests _job_alertes_peremption_48h."""



    def test_articles_a_perimer_detectes(self):

        """Articles avec date_peremption Ã  J+1 doivent Ãªtre dÃ©tectÃ©s et notifiÃ©s."""

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



        # Dispatcher doit avoir Ã©tÃ© appelÃ©

        mock_dispatcher.envoyer.assert_called_once()

        args = mock_dispatcher.envoyer.call_args

        message = args[1].get("message") or args[0][1] if args[0] else args[1]["message"]

        assert "Yaourt" in message or "Lait" in message



    def test_aucun_article_aucune_notification(self):

        """Sans article Ã  pÃ©rimÃ©, le dispatcher ne doit pas Ãªtre appelÃ©."""

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





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3d â€” Structure rÃ©sumÃ© hebdo

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





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





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3e â€” Push contextuel soir

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





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

        mock_meteo.get_previsions.side_effect = Exception("MÃ©tÃ©o indisponible")



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

        # Nouveau comportement: push en canal primaire + fallback gÃ©rÃ© par stratÃ©gie

        assert "push" in call_kwargs.get("canaux", [])

        assert call_kwargs.get("strategie") == "failover"





class TestExpirationJobsDryRun:

    """Les jobs Sprint 15 doivent Ãªtre exÃ©cutables en dry-run via le registre admin."""



    @pytest.mark.parametrize(

        "job_id",

        [

            "job_expiration_recettes_suggestion",

            "job_stock_prediction_reapprovisionnement",

            "job_variete_repas_alerte",

            "job_tendances_activites_famille",

            "job_energie_peak_detection",

            "job_nutrition_adultes_weekly",

            "job_briefing_matinal_push",

            "job_jardin_feedback_planning",

        ],

    )

    def test_job_sprint_15_supporte_dry_run(self, job_id):

        """Chaque job Sprint 15 doit renvoyer un statut dry_run sans exÃ©cution rÃ©elle."""

        from src.services.core.cron.jobs import executer_job_par_id



        resultat = executer_job_par_id(job_id, dry_run=True)



        assert resultat["status"] == "dry_run"

        assert resultat["job_id"] == job_id





class TestWeekendWeeklyReportJobsDryRun:

    """Les jobs Sprint 16 doivent Ãªtre exÃ©cutables en dry-run via le registre admin."""



    @pytest.mark.parametrize(

        "job_id",

        [

            "s16_resume_weekend_whatsapp",

            "s16_rappel_entretien_whatsapp",

            "s16_bilan_nutrition_whatsapp",

            "s16_rapport_famille_mensuel",

            "s16_rapport_maison_trimestriel",

        ],

    )

    def test_job_sprint_16_supporte_dry_run(self, job_id):

        """Chaque job Sprint 16 doit renvoyer un statut dry_run sans exÃ©cution rÃ©elle."""

        from src.services.core.cron.jobs import executer_job_par_id



        resultat = executer_job_par_id(job_id, dry_run=True)



        assert resultat["status"] == "dry_run"

        assert resultat["job_id"] == job_id

        assert resultat["dry_run"] is True

        assert resultat["dry_run"] is True





class TestExpirationJobsDetailed:

    """Tests unitaires fins des jobs Sprint 15."""



    def test_job_expiration_recettes_suggestion_notifie_les_articles_urgents(self):

        """Le job 15.1 doit notifier les produits bientÃ´t expirants."""

        from src.services.core.cron.jobs import _job_expiration_recettes_suggestion



        mock_service = MagicMock()

        mock_service.predire_peremptions_personnalisees.return_value = {

            "items": [

                {"nom": "Courgette"},

                {"nom": "Yaourt"},

            ]

        }

        mock_dispatcher = MagicMock()



        with (

            patch("src.services.cuisine.obtenir_service_prediction_peremption", return_value=mock_service),

            patch(

                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",

                return_value=mock_dispatcher,

            ),

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"push": True}) as mock_notif,

        ):

            _job_expiration_recettes_suggestion()



        mock_service.predire_peremptions_personnalisees.assert_called_once_with(horizon_jours=2)

        mock_notif.assert_called_once()

        message = mock_notif.call_args.kwargs["message"]

        assert "Courgette" in message

        assert "Yaourt" in message



    def test_job_stock_prediction_reapprovisionnement_notifie_les_articles_en_risque(self):

        """Le job 15.2 doit signaler les articles Ã  rÃ©approvisionner."""

        from src.services.core.cron.jobs import _job_stock_prediction_reapprovisionnement



        articles = [

            SimpleNamespace(nom="Lait", quantite=0.5, quantite_min=1.0, ingredient_id=1),

            SimpleNamespace(nom="PÃ¢tes", quantite=3.0, quantite_min=1.0, ingredient_id=2),

        ]

        mock_session = MagicMock()

        mock_session.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = articles



        mock_service_ia = MagicMock()

        mock_service_ia.predire_consommation.side_effect = [

            SimpleNamespace(seuil_reapprovisionnement_kg=1.0, jours_autonomie=3),

            SimpleNamespace(seuil_reapprovisionnement_kg=0.5, jours_autonomie=20),

        ]

        mock_dispatcher = MagicMock()



        @contextmanager

        def _ctx():

            yield mock_session



        with (

            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),

            patch("src.services.inventaire.ia_service.get_inventaire_ai_service", return_value=mock_service_ia),

            patch(

                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",

                return_value=mock_dispatcher,

            ),

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"ntfy": True}) as mock_notif,

        ):

            _job_stock_prediction_reapprovisionnement()



        assert mock_service_ia.predire_consommation.call_count == 2

        mock_notif.assert_called_once()

        assert "Lait" in mock_notif.call_args.kwargs["message"]



    def test_job_variete_repas_alerte_notifie_si_score_faible(self):

        """Le job 15.3 doit alerter quand la variÃ©tÃ© du planning est insuffisante."""

        from src.services.core.cron.jobs import _job_variete_repas_alerte



        repas = [

            SimpleNamespace(date_repas=date(2026, 4, 2), type_repas="midi", recette=SimpleNamespace(nom="Poulet riz"), notes=None),

            SimpleNamespace(date_repas=date(2026, 4, 3), type_repas="soir", recette=SimpleNamespace(nom="Poulet riz"), notes=None),

            SimpleNamespace(date_repas=date(2026, 4, 4), type_repas="midi", recette=SimpleNamespace(nom="Poulet riz"), notes=None),

        ]

        mock_session = MagicMock()

        mock_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = repas



        mock_planning_service = MagicMock()

        mock_planning_service.analyser_variete_semaine.return_value = SimpleNamespace(

            score_variete=35,

            repetitions_problematiques=["Poulet riz"],

            recommandations=["Ajouter une recette poisson ou vÃ©gÃ©tarienne"],

        )

        mock_dispatcher = MagicMock()



        @contextmanager

        def _ctx():

            yield mock_session



        with (

            patch("src.core.db.obtenir_contexte_db", return_value=_ctx()),

            patch("src.services.planning.ia_service.PlanningAIService", return_value=mock_planning_service),

            patch(

                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",

                return_value=mock_dispatcher,

            ),

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"push": True}) as mock_notif,

        ):

            _job_variete_repas_alerte()



        mock_planning_service.analyser_variete_semaine.assert_called_once()

        mock_notif.assert_called_once()

        assert "score 35/100" in mock_notif.call_args.kwargs["message"]



    def test_job_tendances_activites_famille_compare_deux_semaines(self):

        """Le job 15.4 doit comparer la semaine courante Ã  la prÃ©cÃ©dente."""

        from src.services.core.cron.jobs import _job_tendances_activites_famille



        query_courant = MagicMock()

        query_courant.filter.return_value.all.return_value = [

            SimpleNamespace(statut="termine"),

            SimpleNamespace(statut="planifie"),

            SimpleNamespace(statut="terminee"),

        ]

        query_precedent = MagicMock()

        query_precedent.filter.return_value.all.return_value = [SimpleNamespace(statut="termine")]



        mock_session = MagicMock()

        mock_session.query.side_effect = [query_courant, query_precedent]

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

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"ntfy": True}) as mock_notif,

        ):

            _job_tendances_activites_famille()



        mock_notif.assert_called_once()

        message = mock_notif.call_args.kwargs["message"]

        assert "3 prÃ©vues, 1 terminÃ©es" in message

        assert "hausse" in message



    def test_job_energie_peak_detection_notifie_les_anomalies(self):

        """Le job 15.5 doit agrÃ©ger les anomalies Ã©nergie dÃ©tectÃ©es."""

        from src.services.core.cron.jobs import _job_energie_peak_detection



        mock_service = MagicMock()

        mock_service.analyser_anomalies.side_effect = [

            {"anomalies": [{"explication": "pic anormal soirÃ©e"}]},

            {"anomalies": []},

            {"anomalies": [{"explication": "surconsommation eau"}]},

        ]

        mock_dispatcher = MagicMock()



        with (

            patch("src.services.maison.energie_anomalies_ia.obtenir_service_energie_anomalies_ia", return_value=mock_service),

            patch(

                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",

                return_value=mock_dispatcher,

            ),

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"push": True}) as mock_notif,

        ):

            _job_energie_peak_detection()



        assert mock_service.analyser_anomalies.call_count == 3

        mock_notif.assert_called_once()

        assert "pic anormal soirÃ©e" in mock_notif.call_args.kwargs["message"]

        assert "surconsommation eau" in mock_notif.call_args.kwargs["message"]



    def test_job_nutrition_adultes_weekly_notifie_un_bilan(self):

        """Le job 15.6 doit produire un bilan nutrition adulte Ã  partir des besoins Garmin."""

        from src.services.core.cron.jobs import _job_nutrition_adultes_weekly



        mock_garmin = MagicMock()

        mock_garmin.calculer_besoins_nutritionnels_selon_activite.return_value = {

            "nom_profil": "Matanne",

            "niveau_activite": "actif",

            "pas_detectes": 12000,

            "calories_actives_detectees": 450,

            "calories_recommended": 2450,

        }

        mock_ai = MagicMock()

        mock_ai.analyser_nutrition_personne = AsyncMock(return_value=SimpleNamespace(equilibre_score=88))

        mock_dispatcher = MagicMock()



        with (

            patch("src.services.cuisine.inter_module_garmin_nutrition_adultes.get_garmin_nutrition_adultes_service", return_value=mock_garmin),

            patch("src.services.cuisine.nutrition_famille_ia.get_nutrition_famille_ai_service", return_value=mock_ai),

            patch(

                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",

                return_value=mock_dispatcher,

            ),

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"push": True}) as mock_notif,

        ):

            _job_nutrition_adultes_weekly()



        mock_garmin.calculer_besoins_nutritionnels_selon_activite.assert_called_once()

        mock_ai.analyser_nutrition_personne.assert_awaited_once()

        mock_notif.assert_called_once()

        message = mock_notif.call_args.kwargs["message"]

        assert "score 88/100" in message

        assert "2450 kcal/jour" in message



    def test_job_briefing_matinal_push_itere_sur_tous_les_utilisateurs(self):

        """Le job 15.7 doit envoyer un briefing Ã  chaque utilisateur actif."""

        from src.services.core.cron.jobs import _job_briefing_matinal_push



        mock_service = MagicMock()

        mock_service.envoyer_briefing_notification.side_effect = [

            {"notification": {"push": True}},

            {"notification": None},

        ]



        with (

            patch("src.services.utilitaires.obtenir_service_briefing_matinal", return_value=mock_service),

            patch("src.services.core.cron.jobs._obtenir_user_ids_actifs", return_value=["u1", "u2"]),

        ):

            _job_briefing_matinal_push()



        assert mock_service.envoyer_briefing_notification.call_count == 2

        mock_service.envoyer_briefing_notification.assert_has_calls([

            call(user_id="u1"),

            call(user_id="u2"),

        ])



    def test_job_jardin_feedback_planning_notifie_les_recoltes_non_utilisees(self):

        """Le job 15.8 doit notifier les rÃ©coltes Ã  mieux intÃ©grer au planning."""

        from src.services.core.cron.jobs import _job_jardin_feedback_planning



        mock_service = MagicMock()

        mock_service.analyser_recoltes_non_utilisees.return_value = {

            "recoltes_non_utilisees": [

                {"nom": "Tomates"},

                {"nom": "Courgettes"},

            ],

            "recommandations": ["Planifier une ratatouille la semaine prochaine"],

        }

        mock_dispatcher = MagicMock()



        with (

            patch("src.services.cuisine.inter_module_planning_jardin.get_planning_jardin_service", return_value=mock_service),

            patch(

                "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",

                return_value=mock_dispatcher,

            ),

            patch("src.services.core.cron.jobs._envoyer_notif_tous_users", return_value={"push": True}) as mock_notif,

        ):

            _job_jardin_feedback_planning()



        mock_service.analyser_recoltes_non_utilisees.assert_called_once_with(semaines_lookback=4)

        mock_notif.assert_called_once()

        message = mock_notif.call_args.kwargs["message"]

        assert "Tomates" in message

        assert "Courgettes" in message





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3f â€” Rapport mensuel budget

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





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





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T3g â€” Pas d'accÃ¨s ._subscriptions dans les jobs

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





class TestPushServiceAccesPublic:

    """VÃ©rifie que les jobs cron n'utilisent pas l'attribut privÃ© ._subscriptions."""



    def test_jobs_no_private_subscriptions_access(self):

        """Le code source des jobs ne doit pas contenir '._subscriptions'."""

        import inspect

        from src.services.core.cron import jobs as cron_module



        # VÃ©rifier toutes les fonctions de job

        job_fns = [

            cron_module._job_push_quotidien,

            cron_module._job_push_contextuel_soir,

            cron_module._job_rappels_famille,

        ]

        for fn in job_fns:

            source = inspect.getsource(fn)

            assert "._subscriptions" not in source, (

                f"{fn.__name__} contient un accÃ¨s privÃ© ._subscriptions."

                " Utiliser obtenir_abonnes() Ã  la place."

            )



    def test_push_quotidien_utilise_charger_abonnements_db(self):

        """_job_push_quotidien doit utiliser charger_tous_abonnements_actifs_db() ou obtenir_abonnes()."""

        import inspect

        from src.services.core.cron import jobs as cron_module



        source = inspect.getsource(cron_module._job_push_quotidien)

        assert (

            "charger_tous_abonnements_actifs_db" in source

            or "obtenir_abonnes" in source

        ), "_job_push_quotidien doit utiliser la mÃ©thode publique d'abonnements."





# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

# T2 â€” Error handling jobs cron

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•





class TestCronErrorHandling:

    """Valide que les jobs absorbent les erreurs et journalisent l'Ã©chec."""



    def test_job_rappels_famille_capture_exception(self, caplog):

        """Une exception service ne doit pas remonter hors du job."""

        from src.services.core.cron.jobs import _job_rappels_famille



        with patch("src.services.famille.rappels.ServiceRappelsFamille") as mock_service_cls:

            mock_service_cls.return_value.envoyer_rappels_du_jour.side_effect = RuntimeError("boom")

            with caplog.at_level(logging.ERROR):

                _job_rappels_famille()



        assert "Erreur lors des rappels famille" in caplog.text



    def test_job_rappel_courses_capture_exception_db(self, caplog):

        """Une erreur DB dans le rappel courses est gÃ©rÃ©e sans lever d'exception."""

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





class TestDigestWhatsappMatinalCron:

    """Tests du job digest WhatsApp matinal."""



    def test_job_digest_whatsapp_matinal_appelle_integration(self):

        """Le job doit appeler envoyer_digest_matinal()."""

        from src.services.core.cron.jobs import _job_digest_whatsapp_matinal



        with patch(

            "src.services.integrations.whatsapp.envoyer_digest_matinal",

            new=AsyncMock(return_value=True),

        ) as mock_digest:

            _job_digest_whatsapp_matinal()



        mock_digest.assert_called_once()





class TestJobExecutionsPersistence:

    """Tests ciblÃ©s Phase 7: persistance explicite dans job_executions."""



    def test_executer_job_trace_persiste_insert_et_update_success(self):

        """Une exÃ©cution normale doit faire INSERT puis UPDATE sur job_executions."""

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

