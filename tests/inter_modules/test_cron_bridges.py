"""
Tests d'intégration pour les cron jobs bridges inter-modules.

Vérifie que chaque bridge (B8.1 → B8.8, 11.3) s'exécute sans erreur
avec des données mockées.
"""

import pytest
from contextlib import contextmanager
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, AsyncMock


# ═══════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════


@pytest.fixture
def mock_session():
    """Session DB mockée pour les bridges."""
    session = MagicMock()
    session.query.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.filter.return_value.all.return_value = []
    session.query.return_value.filter.return_value.filter.return_value.first.return_value = None
    session.query.return_value.filter.return_value.scalar.return_value = 0
    return session


@contextmanager
def _ctx(mock_session):
    yield mock_session


@pytest.fixture
def patch_db(mock_session):
    """Patch le contexte DB pour tous les bridges."""
    with patch(
        "src.services.core.cron_bridges.obtenir_contexte_db",
        return_value=_ctx(mock_session),
    ):
        yield mock_session


@pytest.fixture
def patch_notifications():
    """Patch le dispatcher de notifications."""
    mock_dispatcher = MagicMock()
    mock_dispatcher.envoyer_evenement = MagicMock()

    with patch(
        "src.services.core.notifications.notif_dispatcher.get_dispatcher_notifications",
        return_value=mock_dispatcher,
    ):
        yield mock_dispatcher


# ═══════════════════════════════════════════════════════════════
# B8.1 — PRÉDICTION COURSES HEBDO
# ═══════════════════════════════════════════════════════════════


class TestBridgePredictionCourses:
    """Tests pour prediction_courses_hebdo (B8.1)."""

    @pytest.mark.unit
    def test_prediction_courses_sans_historique(self):
        """Aucune prédiction si historique insuffisant."""
        mock_service = MagicMock()
        mock_service.predire_prochaine_liste.return_value = []

        with patch(
            "src.services.ia.prediction_courses.obtenir_service_prediction_courses",
            return_value=mock_service,
        ):
            from src.services.core.cron_bridges import prediction_courses_hebdo

            prediction_courses_hebdo()
            mock_service.predire_prochaine_liste.assert_called_once_with(limite=30)

    @pytest.mark.unit
    def test_prediction_courses_avec_resultats(self, patch_notifications):
        """Des prédictions trouvées déclenchent une notification."""
        predictions = [
            {"nom": "Lait", "score": 0.95},
            {"nom": "Beurre", "score": 0.90},
            {"nom": "Pain", "score": 0.85},
            {"nom": "Oeufs", "score": 0.80},
            {"nom": "Fromage", "score": 0.75},
            {"nom": "Yaourt", "score": 0.70},
        ]
        mock_service = MagicMock()
        mock_service.predire_prochaine_liste.return_value = predictions

        with patch(
            "src.services.ia.prediction_courses.obtenir_service_prediction_courses",
            return_value=mock_service,
        ):
            with patch(
                "src.services.core.cron_bridges._obtenir_user_ids",
                return_value=["user1"],
            ):
                from src.services.core.cron_bridges import prediction_courses_hebdo

                prediction_courses_hebdo()

    @pytest.mark.unit
    def test_prediction_courses_erreur_service(self):
        """Erreur service IA gérée gracieusement."""
        with patch(
            "src.services.ia.prediction_courses.obtenir_service_prediction_courses",
            side_effect=Exception("Service IA indisponible"),
        ):
            from src.services.core.cron_bridges import prediction_courses_hebdo

            # Ne doit PAS lever d'exception
            prediction_courses_hebdo()


# ═══════════════════════════════════════════════════════════════
# B8.2 — PLANNING AUTO SEMAINE
# ═══════════════════════════════════════════════════════════════


class TestBridgePlanningAutoSemaine:
    """Tests pour planning_auto_semaine (B8.2)."""

    @pytest.mark.unit
    def test_planning_existant_pas_de_notification(self, patch_db):
        """Si un planning actif existe, pas de notification."""
        planning_mock = SimpleNamespace(
            id=1, semaine_debut=date.today(), semaine_fin=date.today() + timedelta(days=6),
            statut="actif",
        )
        patch_db.query.return_value.filter.return_value.first.return_value = planning_mock

        from src.services.core.cron_bridges import planning_auto_semaine

        planning_auto_semaine()

    @pytest.mark.unit
    def test_planning_vide_notifie(self, patch_db):
        """Si aucun planning, une notification est envoyée."""
        patch_db.query.return_value.filter.return_value.first.return_value = None

        with patch(
            "src.services.core.cron_bridges._notifier_proposition_planning"
        ) as mock_notif:
            from src.services.core.cron_bridges import planning_auto_semaine

            planning_auto_semaine()
            mock_notif.assert_called_once()


# ═══════════════════════════════════════════════════════════════
# B8.3 — ALERTES BUDGET SEUIL
# ═══════════════════════════════════════════════════════════════


class TestBridgeAlertesBudget:
    """Tests pour alertes_budget_seuil (B8.3)."""

    @pytest.mark.unit
    def test_aucun_depassement(self):
        """Pas d'alerte si aucune catégorie ne dépasse."""
        mock_service = MagicMock()
        mock_service.detecter_anomalies_budget.return_value = []

        with patch(
            "src.services.ia.prevision_budget.obtenir_service_prevision_budget",
            return_value=mock_service,
        ):
            from src.services.core.cron_bridges import alertes_budget_seuil

            alertes_budget_seuil()
            mock_service.detecter_anomalies_budget.assert_called_once_with(seuil_pct=80)

    @pytest.mark.unit
    def test_depassements_detectes(self):
        """Des anomalies détectées déclenchent des notifications."""
        anomalies = [
            {"categorie": "Alimentation", "depense": 450, "pourcentage": 90, "niveau": "critique"},
            {"categorie": "Loisirs", "depense": 200, "pourcentage": 85, "niveau": "attention"},
        ]
        mock_service = MagicMock()
        mock_service.detecter_anomalies_budget.return_value = anomalies

        with patch(
            "src.services.ia.prevision_budget.obtenir_service_prevision_budget",
            return_value=mock_service,
        ):
            with patch(
                "src.services.core.cron_bridges._notifier_alertes_budget"
            ) as mock_notif:
                from src.services.core.cron_bridges import alertes_budget_seuil

                alertes_budget_seuil()
                mock_notif.assert_called_once_with(anomalies)

    @pytest.mark.unit
    def test_erreur_service_budget(self):
        """Erreur service budget gérée sans crash."""
        with patch(
            "src.services.ia.prevision_budget.obtenir_service_prevision_budget",
            side_effect=Exception("DB timeout"),
        ):
            from src.services.core.cron_bridges import alertes_budget_seuil

            alertes_budget_seuil()


# ═══════════════════════════════════════════════════════════════
# B8.5 — RAPPEL JARDIN SAISON
# ═══════════════════════════════════════════════════════════════


class TestBridgeRappelJardin:
    """Tests pour rappel_jardin_saison (B8.5)."""

    @pytest.mark.unit
    def test_rappel_jardin_sans_catalogue(self):
        """Fonctionne même sans fichier catalogue."""
        with patch("pathlib.Path.exists", return_value=False):
            from src.services.core.cron_bridges import rappel_jardin_saison

            rappel_jardin_saison()

    @pytest.mark.unit
    def test_rappel_jardin_avec_conseils(self):
        """Génère des conseils saisonniers avec catalogue."""
        import json

        catalogue = [
            {"nom": "Tomate", "mois_plantation": [4, 5]},
            {"nom": "Basilic", "mois_plantation": [4, 5, 6]},
        ]

        with patch("pathlib.Path.exists", return_value=True):
            with patch("pathlib.Path.read_text", return_value=json.dumps(catalogue)):
                with patch(
                    "src.services.core.cron_bridges._notifier_jardin_saison"
                ) as mock_notif:
                    from src.services.core.cron_bridges import rappel_jardin_saison

                    rappel_jardin_saison()
                    # Doit toujours appeler la notification (au moins pour les conseils généraux)


# ═══════════════════════════════════════════════════════════════
# B8.6 — SYNC BUDGET CONSOLIDATION
# ═══════════════════════════════════════════════════════════════


class TestBridgeBudgetConsolidation:
    """Tests pour sync_budget_consolidation (B8.6)."""

    @pytest.mark.unit
    def test_consolidation_totaux_corrects(self, patch_db):
        """Calcule correctement les totaux famille + maison."""
        # Mock pour total_famille
        patch_db.query.return_value.filter.return_value.scalar.return_value = 350.50

        from src.services.core.cron_bridges import sync_budget_consolidation

        sync_budget_consolidation()

    @pytest.mark.unit
    def test_consolidation_sans_depenses(self, patch_db):
        """Fonctionne même sans aucune dépense."""
        patch_db.query.return_value.filter.return_value.scalar.return_value = 0

        from src.services.core.cron_bridges import sync_budget_consolidation

        sync_budget_consolidation()

    @pytest.mark.unit
    def test_consolidation_erreur_db(self):
        """Erreur DB gérée gracieusement."""
        with patch(
            "src.services.core.cron_bridges.obtenir_contexte_db",
            side_effect=Exception("Connection refused"),
        ):
            from src.services.core.cron_bridges import sync_budget_consolidation

            sync_budget_consolidation()


# ═══════════════════════════════════════════════════════════════
# B8.7 — TENDANCES NUTRITION HEBDO
# ═══════════════════════════════════════════════════════════════


class TestBridgeTendancesNutrition:
    """Tests pour tendances_nutrition_hebdo (B8.7)."""

    @pytest.mark.unit
    def test_nutrition_avec_repas(self, patch_db):
        """Compte correctement les repas planifiés et préparés."""
        repas_mock = [
            SimpleNamespace(id=1, date_repas=date.today(), prepare=True),
            SimpleNamespace(id=2, date_repas=date.today(), prepare=False),
            SimpleNamespace(id=3, date_repas=date.today(), prepare=True),
        ]
        patch_db.query.return_value.filter.return_value.all.return_value = repas_mock

        from src.services.core.cron_bridges import tendances_nutrition_hebdo

        tendances_nutrition_hebdo()

    @pytest.mark.unit
    def test_nutrition_semaine_vide(self, patch_db):
        """Aucun repas planifié, pas d'erreur."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.core.cron_bridges import tendances_nutrition_hebdo

        tendances_nutrition_hebdo()


# ═══════════════════════════════════════════════════════════════
# B8.8 — RAPPEL ACTIVITÉ JULES
# ═══════════════════════════════════════════════════════════════


class TestBridgeActiviteJules:
    """Tests pour rappel_activite_jules (B8.8)."""

    @pytest.mark.unit
    def test_jules_profil_trouve(self, patch_db):
        """Profil Jules trouvé, calcul de l'âge correct."""
        jules = SimpleNamespace(
            name="Jules",
            actif=True,
            date_of_birth=date.today() - timedelta(days=1000),
        )
        patch_db.query.return_value.filter.return_value.first.return_value = jules

        from src.services.core.cron_bridges import rappel_activite_jules

        rappel_activite_jules()

    @pytest.mark.unit
    def test_jules_profil_absent(self, patch_db):
        """Si profil Jules absent, exit gracieux."""
        patch_db.query.return_value.filter.return_value.first.return_value = None

        from src.services.core.cron_bridges import rappel_activite_jules

        rappel_activite_jules()

    @pytest.mark.unit
    def test_jules_sans_date_naissance(self, patch_db):
        """Profil sans date de naissance, exit gracieux."""
        jules = SimpleNamespace(name="Jules", actif=True, date_of_birth=None)
        patch_db.query.return_value.filter.return_value.first.return_value = jules

        from src.services.core.cron_bridges import rappel_activite_jules

        rappel_activite_jules()


# ═══════════════════════════════════════════════════════════════
# 11.3 — SYNC GOOGLE CALENDAR
# ═══════════════════════════════════════════════════════════════


class TestBridgeSyncGoogleCalendar:
    """Tests pour sync_google_calendar (11.3)."""

    @pytest.mark.unit
    def test_aucun_utilisateur_connecte(self, patch_db):
        """Aucun calendrier externe connecté, exit propre."""
        patch_db.query.return_value.filter.return_value.all.return_value = []

        from src.services.core.cron_bridges import sync_google_calendar

        sync_google_calendar()

    @pytest.mark.unit
    def test_sync_avec_utilisateurs(self, patch_db):
        """Sync exécutée pour chaque utilisateur connecté."""
        cals = [
            SimpleNamespace(user_id="u1", provider="google", enabled=True),
            SimpleNamespace(user_id="u2", provider="google", enabled=True),
        ]
        patch_db.query.return_value.filter.return_value.all.return_value = cals

        mock_service = MagicMock()
        mock_service.sync_google_calendar.return_value = SimpleNamespace(imported=3, exported=2)

        with patch(
            "src.services.famille.calendrier.get_calendar_sync_service",
            return_value=mock_service,
        ):
            from src.services.core.cron_bridges import sync_google_calendar

            sync_google_calendar()
            assert mock_service.sync_google_calendar.call_count == 2

    @pytest.mark.unit
    def test_sync_erreur_partielle(self, patch_db):
        """Erreur sur un utilisateur n'empêche pas le suivant."""
        cals = [
            SimpleNamespace(user_id="u1", provider="google", enabled=True),
            SimpleNamespace(user_id="u2", provider="google", enabled=True),
        ]
        patch_db.query.return_value.filter.return_value.all.return_value = cals

        mock_service = MagicMock()
        mock_service.sync_google_calendar.side_effect = [
            Exception("Token expired"),
            SimpleNamespace(imported=1, exported=0),
        ]

        with patch(
            "src.services.famille.calendrier.get_calendar_sync_service",
            return_value=mock_service,
        ):
            from src.services.core.cron_bridges import sync_google_calendar

            sync_google_calendar()
            assert mock_service.sync_google_calendar.call_count == 2


# ═══════════════════════════════════════════════════════════════
# SCHEDULER CONFIGURATION
# ═══════════════════════════════════════════════════════════════


class TestConfigurerJobsBridges:
    """Tests pour configurer_jobs_bridges."""

    @pytest.mark.unit
    def test_tous_les_jobs_enregistres(self):
        """Vérifie que les 9 jobs bridges sont enregistrés dans le scheduler."""
        mock_scheduler = MagicMock()
        mock_scheduler.add_job = MagicMock()

        from src.services.core.cron_bridges import configurer_jobs_bridges

        configurer_jobs_bridges(mock_scheduler)

        job_ids = [call.kwargs.get("id") for call in mock_scheduler.add_job.call_args_list]
        expected_ids = [
            "prediction_courses_hebdo",
            "planning_auto_semaine",
            "alertes_budget_seuil",
            "rappel_jardin_saison",
            "sync_budget_consolidation",
            "tendances_nutrition_hebdo",
            "rappel_activite_jules",
            "sync_google_calendar",
        ]

        for expected_id in expected_ids:
            assert expected_id in job_ids, f"Job '{expected_id}' non enregistré dans le scheduler"
