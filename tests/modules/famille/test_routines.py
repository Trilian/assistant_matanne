"""
Tests pour src/modules/famille/routines.py

Tests du module Routines avec mocks complets pour éviter les appels réseau/DB.
Adapté au refactoring: logique métier dans ServiceRoutines, UI dans routines.py.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_routine():
    """Fixture pour une routine mockée (modèle ORM)."""
    routine = MagicMock()
    routine.id = 1
    routine.name = "Routine du matin"
    routine.description = "Routine matinale pour Jules"
    routine.child_id = 1
    routine.frequency = "quotidien"
    routine.is_active = True
    routine.ai_suggested = False
    routine.created_at = datetime(2025, 1, 1, 8, 0, 0)
    routine.tasks = []
    return routine


@pytest.fixture
def mock_routine_task():
    """Fixture pour une tâche de routine mockée (modèle ORM)."""
    task = MagicMock()
    task.id = 1
    task.routine_id = 1
    task.task_name = "Réveil"
    task.scheduled_time = "07:00"
    task.status = "à faire"
    task.completed_at = None
    return task


@pytest.fixture
def mock_child_profile():
    """Fixture pour un profil enfant mocké."""
    child = MagicMock()
    child.id = 1
    child.name = "Jules"
    return child


@pytest.fixture
def mock_db_session(mock_routine, mock_routine_task, mock_child_profile):
    """Fixture pour une session DB mockée."""
    session = MagicMock()

    mock_query = MagicMock()
    mock_query.filter.return_value = mock_query
    mock_query.filter_by.return_value = mock_query
    mock_query.order_by.return_value = mock_query
    mock_query.all.return_value = [mock_routine]
    mock_query.first.return_value = mock_routine_task
    mock_query.get.return_value = mock_child_profile
    mock_query.delete.return_value = 1
    mock_query.count.return_value = 5
    mock_query.join.return_value = mock_query
    mock_query.options.return_value = mock_query

    session.query.return_value = mock_query
    session.add = MagicMock()
    session.commit = MagicMock()

    return session


@pytest.fixture
def service():
    """Fixture pour un ServiceRoutines prêt à tester.

    Patche les modèles ORM au niveau du service pour éviter les erreurs
    d'attributs (mismatch entre noms FR du modèle et EN du service).
    """
    with (
        patch("src.services.famille.routines.Routine") as mock_routine_cls,
        patch("src.services.famille.routines.RoutineTask") as mock_task_cls,
        patch("src.services.famille.routines.ChildProfile") as mock_child_cls,
        patch("src.services.famille.routines.selectinload", return_value=MagicMock()),
        patch("src.services.famille.routines.obtenir_bus"),
    ):
        from src.services.famille.routines import ServiceRoutines

        svc = ServiceRoutines()
        svc._mock_routine = mock_routine_cls
        svc._mock_task = mock_task_cls
        svc._mock_child = mock_child_cls
        yield svc


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════════════════════════


class TestImports:
    """Tests d'import du module et du service."""

    def test_import_app(self):
        """Test import de app()."""
        from src.modules.famille.routines import app

        assert callable(app)

    def test_import_service_routines(self):
        """Test import de ServiceRoutines."""
        from src.services.famille.routines import ServiceRoutines

        assert callable(ServiceRoutines)

    def test_import_factory(self):
        """Test import de la factory obtenir_service_routines."""
        from src.services.famille.routines import obtenir_service_routines

        assert callable(obtenir_service_routines)

    def test_service_has_expected_methods(self):
        """Test que ServiceRoutines expose les méthodes attendues."""
        from src.services.famille.routines import ServiceRoutines

        svc = ServiceRoutines()
        for method in [
            "lister_routines",
            "lister_taches",
            "creer_routine",
            "ajouter_tache",
            "marquer_complete",
            "reinitialiser_taches_jour",
            "supprimer_routine",
            "get_taches_en_retard",
        ]:
            assert hasattr(svc, method), f"ServiceRoutines n'a pas la méthode {method}"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS LISTER ROUTINES
# ═══════════════════════════════════════════════════════════════════════════════


class TestChargerRoutines:
    """Tests pour ServiceRoutines.lister_routines()."""

    def test_charger_routines_retourne_liste(self, service, mock_db_session, mock_routine):
        """lister_routines retourne une liste de RoutineDict."""
        result = service.lister_routines(actives_uniquement=True, db=mock_db_session)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["nom"] == "Routine du matin"
        assert result[0]["frequence"] == "quotidien"
        assert result[0]["active"] is True

    def test_charger_routines_vide(self, service, mock_db_session):
        """lister_routines retourne une liste vide si aucune routine."""
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        mock_db_session.query.return_value.order_by.return_value.all.return_value = []

        result = service.lister_routines(actives_uniquement=False, db=mock_db_session)

        assert result == []


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS LISTER TACHES
# ═══════════════════════════════════════════════════════════════════════════════


class TestChargerTachesRoutine:
    """Tests pour ServiceRoutines.lister_taches()."""

    def test_charger_taches_routine_retourne_liste(
        self, service, mock_db_session, mock_routine_task
    ):
        """lister_taches retourne des TacheDict."""
        mock_db_session.query.return_value.filter.return_value.order_by.return_value.all.return_value = [
            mock_routine_task
        ]

        result = service.lister_taches(routine_id=1, db=mock_db_session)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["nom"] == "Réveil"
        assert result[0]["heure"] == "07:00"
        assert result[0]["statut"] == "à faire"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CREER ROUTINE
# ═══════════════════════════════════════════════════════════════════════════════


class TestCreerRoutine:
    """Tests pour ServiceRoutines.creer_routine()."""

    def test_creer_routine_famille(self, service, mock_db_session):
        """Créer une routine pour la famille."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = service.creer_routine(
            nom="Test routine",
            description="Desc",
            pour_qui="Famille",
            frequence="quotidien",
            db=mock_db_session,
        )

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_creer_routine_pour_enfant(self, service, mock_db_session, mock_child_profile):
        """Créer une routine pour un enfant."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_child_profile
        )

        result = service.creer_routine(
            nom="Routine Jules",
            description="Pour Jules",
            pour_qui="Jules",
            frequence="quotidien",
            db=mock_db_session,
        )

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS AJOUTER TACHE
# ═══════════════════════════════════════════════════════════════════════════════


class TestAjouterTache:
    """Tests pour ServiceRoutines.ajouter_tache()."""

    def test_ajouter_tache_avec_heure(self, service, mock_db_session):
        """Ajouter une tâche avec heure planifiée."""
        service.ajouter_tache(routine_id=1, nom="Petit-déjeuner", heure="08:00", db=mock_db_session)

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    def test_ajouter_tache_sans_heure(self, service, mock_db_session):
        """Ajouter une tâche sans heure planifiée."""
        service.ajouter_tache(routine_id=1, nom="Activité libre", heure=None, db=mock_db_session)

        mock_db_session.add.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MARQUER COMPLETE
# ═══════════════════════════════════════════════════════════════════════════════


class TestMarquerComplete:
    """Tests pour ServiceRoutines.marquer_complete()."""

    def test_marquer_complete_existante(self, service, mock_db_session, mock_routine_task):
        """Marquer une tâche existante comme terminée."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = (
            mock_routine_task
        )

        result = service.marquer_complete(task_id=1, db=mock_db_session)

        assert result is True
        assert mock_routine_task.status == "termine"
        assert mock_routine_task.completed_at is not None

    def test_marquer_complete_inexistante(self, service, mock_db_session):
        """Marquer une tâche inexistante retourne False."""
        mock_db_session.query.return_value.filter.return_value.first.return_value = None

        result = service.marquer_complete(task_id=999, db=mock_db_session)

        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS REINITIALISER TACHES JOUR
# ═══════════════════════════════════════════════════════════════════════════════


class TestReinitialiserTachesJour:
    """Tests pour ServiceRoutines.reinitialiser_taches_jour()."""

    def test_reinitialiser_taches(self, service, mock_db_session, mock_routine_task):
        """Réinitialiser les tâches terminées ramène à 'à faire'."""
        mock_routine_task.status = "termine"
        mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_routine_task
        ]

        result = service.reinitialiser_taches_jour(db=mock_db_session)

        assert result == 1
        assert mock_routine_task.status == "à faire"
        assert mock_routine_task.completed_at is None


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS SUPPRIMER ROUTINE
# ═══════════════════════════════════════════════════════════════════════════════


class TestSupprimerRoutine:
    """Tests pour ServiceRoutines.supprimer_routine()."""

    def test_supprimer_routine(self, service, mock_db_session):
        """Supprimer une routine existante retourne True."""
        mock_db_session.query.return_value.filter.return_value.delete.return_value = 1

        result = service.supprimer_routine(routine_id=1, db=mock_db_session)

        assert result is True
        mock_db_session.commit.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS GET TACHES EN RETARD
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetTachesEnRetard:
    """Tests pour ServiceRoutines.get_taches_en_retard()."""

    def test_get_taches_en_retard_aucune(self, service, mock_db_session):
        """Aucune tâche en retard retourne une liste vide."""
        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = []

        result = service.get_taches_en_retard(db=mock_db_session)

        assert result == []

    def test_get_taches_en_retard_avec_retard(
        self, service, mock_db_session, mock_routine_task, mock_routine
    ):
        """Tâches dont l'heure est passée apparaissent en retard."""
        mock_routine_task.scheduled_time = "00:01"
        mock_routine_task.status = "à faire"

        mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_routine_task, mock_routine)
        ]

        result = service.get_taches_en_retard(db=mock_db_session)

        assert len(result) == 1
        assert result[0]["routine"] == "Routine du matin"
        assert result[0]["tache"] == "Réveil"
        assert result[0]["heure"] == "00:01"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS APP (UI)
# ═══════════════════════════════════════════════════════════════════════════════


def _create_mock_col():
    """Crée un mock context manager réutilisable."""
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=cm)
    cm.__exit__ = MagicMock(return_value=False)
    return cm


def _setup_st_mocks(mock_st):
    """Configure les mocks Streamlit de base."""

    def columns_side_effect(spec):
        n = (
            len(spec)
            if isinstance(spec, list | tuple)
            else int(spec)
            if isinstance(spec, int)
            else 2
        )
        return [_create_mock_col() for _ in range(n)]

    mock_st.columns.side_effect = columns_side_effect
    mock_st.tabs.return_value = [_create_mock_col() for _ in range(4)]
    mock_st.expander.return_value = _create_mock_col()
    mock_st.form.return_value = _create_mock_col()
    mock_st.spinner.return_value = _create_mock_col()
    mock_st.button.return_value = False
    mock_st.form_submit_button.return_value = False
    mock_st.session_state = {"agent_ia": None}


class TestApp:
    """Tests pour la fonction app() du module UI routines."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_app_import(self, mock_get_svc, mock_st):
        """L'import de app réussit."""
        from src.modules.famille.routines import app

        assert callable(app)

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_app_runs_without_error(self, mock_get_svc, mock_st):
        """app() s'exécute sans erreur avec un service mocké."""
        mock_svc = MagicMock()
        mock_get_svc.return_value = mock_svc
        mock_svc.get_taches_en_retard.return_value = []
        mock_svc.lister_routines.return_value = []
        mock_svc.lister_taches.return_value = []
        mock_svc.lister_personnes.return_value = ["Famille"]
        mock_svc.compter_completees_aujourdhui.return_value = 0

        _setup_st_mocks(mock_st)

        from src.modules.famille.routines import app

        app()

        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_app_affiche_alertes_retard(self, mock_get_svc, mock_st):
        """app() affiche les alertes de tâches en retard."""
        mock_svc = MagicMock()
        mock_get_svc.return_value = mock_svc
        mock_svc.get_taches_en_retard.return_value = [
            {"routine": "Matin", "tache": "Réveil", "heure": "07:00", "id": 1}
        ]
        mock_svc.lister_routines.return_value = []
        mock_svc.lister_taches.return_value = []
        mock_svc.lister_personnes.return_value = ["Famille"]
        mock_svc.compter_completees_aujourdhui.return_value = 0

        _setup_st_mocks(mock_st)

        from src.modules.famille.routines import app

        app()

        mock_st.warning.assert_called()
