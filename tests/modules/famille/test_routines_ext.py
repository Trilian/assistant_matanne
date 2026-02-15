"""Tests etendus pour routines.py - couverture fonction app()."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


def _create_mock_col():
    """Creer un mock column context manager."""
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=cm)
    cm.__exit__ = MagicMock(return_value=False)
    return cm


def _setup_mocks(mock_st, mock_db_context, mock_rt=None):
    """Setup mocks de base avec columns dynamique."""

    def columns_side_effect(spec):
        if isinstance(spec, list):
            n = len(spec)
        elif isinstance(spec, int):
            n = spec
        else:
            n = 2
        return [_create_mock_col() for _ in range(n)]

    mock_st.columns.side_effect = columns_side_effect

    mock_tabs = [_create_mock_col() for _ in range(4)]
    mock_st.tabs.return_value = mock_tabs

    mock_expander = _create_mock_col()
    mock_st.expander.return_value = mock_expander

    mock_form = _create_mock_col()
    mock_st.form.return_value = mock_form

    mock_spinner = _create_mock_col()
    mock_st.spinner.return_value = mock_spinner

    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []
    mock_session.query.return_value.filter.return_value.count.return_value = 0
    mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []
    mock_db_context.return_value.__enter__ = MagicMock(return_value=mock_session)
    mock_db_context.return_value.__exit__ = MagicMock(return_value=False)

    if mock_rt is not None:
        mock_rt.completed_at.__ge__ = MagicMock(return_value=MagicMock())
        mock_rt.completed_at.__le__ = MagicMock(return_value=MagicMock())
        mock_rt.completed_at.__gt__ = MagicMock(return_value=MagicMock())
        mock_rt.completed_at.__lt__ = MagicMock(return_value=MagicMock())
    return mock_session


class TestAppTab1Full:
    """Tests Tab1."""

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab1_routines_affichees(
        self, mock_retard, mock_taches, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test Tab1 avec routines."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 1,
                    "nom": "Routine matin",
                    "description": "Desc",
                    "pour": "Famille",
                    "frequence": "quotidien",
                    "active": True,
                    "ia": "",
                    "nb_taches": 1,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame(
            [
                {
                    "id": 1,
                    "nom": "Reveil",
                    "heure": "07:00",
                    "statut": "termine",
                    "completed_at": datetime(2025, 1, 1, 8, 0),
                }
            ]
        )
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db, mock_rt)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    @patch("src.modules.famille.routines.reinitialiser_taches_jour")
    def test_tab1_reinit_jour(
        self, mock_reinit, mock_retard, mock_taches, mock_charger, mock_db, mock_st
    ):
        """Test reinitialisation taches jour."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.side_effect = lambda l, **k: "Reinitialiser" in l
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        mock_reinit.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    @patch("src.modules.famille.routines.supprimer_routine")
    def test_tab1_supprimer_routine(
        self, mock_suppr, mock_retard, mock_taches, mock_charger, mock_db, mock_st
    ):
        """Test suppression routine."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 10,
                    "nom": "R",
                    "description": "",
                    "pour": "F",
                    "frequence": "q",
                    "active": True,
                    "ia": "",
                    "nb_taches": 0,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.side_effect = lambda l, **k: k.get("key", "").startswith("del_")
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        mock_suppr.assert_called_with(10)

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab1_desactiver_routine(
        self, mock_retard, mock_taches, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test desactivation routine."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 15,
                    "nom": "R",
                    "description": "",
                    "pour": "F",
                    "frequence": "q",
                    "active": True,
                    "ia": "",
                    "nb_taches": 0,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": None}

        mock_robj = MagicMock()
        mock_robj.is_active = True
        mock_sess = MagicMock()
        mock_sess.query.return_value.all.return_value = []
        mock_sess.query.return_value.filter.return_value.count.return_value = 0
        mock_sess.query.return_value.get.return_value = mock_robj

        mock_st.button.side_effect = lambda l, **k: k.get("key", "").startswith("disable_")
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db, mock_rt)
        mock_db.return_value.__enter__.return_value = mock_sess

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        assert mock_robj.is_active is False

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    @patch("src.modules.famille.routines.ajouter_tache")
    def test_tab1_ajouter_tache(
        self, mock_ajout, mock_retard, mock_taches, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test ajout tache."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 20,
                    "nom": "R",
                    "description": "",
                    "pour": "F",
                    "frequence": "q",
                    "active": True,
                    "ia": "",
                    "nb_taches": 1,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame(
            [{"id": 1, "nom": "T", "heure": "10:00", "statut": "a faire", "completed_at": None}]
        )
        mock_st.session_state = {"agent_ia": None, "adding_task_to": 20}
        mock_st.button.return_value = False
        mock_st.text_input.return_value = "New task"
        mock_t = MagicMock()
        mock_t.strftime.return_value = "11:30"
        mock_st.time_input.return_value = mock_t

        cnt = [0]

        def fsub(l, **k):
            cnt[0] += 1
            return "Ajouter" in l and cnt[0] == 1

        mock_st.form_submit_button.side_effect = fsub
        _setup_mocks(mock_st, mock_db, mock_rt)

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        mock_ajout.assert_called_with(20, "New task", "11:30")


class TestAppTab2Full:
    """Tests Tab2 - Rappels IA."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab2_sans_agent(self, mock_retard, mock_charger, mock_db, mock_st):
        """Test Tab2 sans agent IA."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        app()
        mock_st.error.assert_any_call("Agent IA non disponible")

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab2_rappels_haute_priorite(self, mock_retard, mock_charger, mock_db, mock_st):
        """Test rappel priorite haute."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {
            "agent_ia": MagicMock(),
            "rappels_ia": [{"routine": "R", "message": "M", "priorite": "haute"}],
        }
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab2_rappels_moyenne_priorite(self, mock_retard, mock_charger, mock_db, mock_st):
        """Test rappel priorite moyenne."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {
            "agent_ia": MagicMock(),
            "rappels_ia": [{"routine": "R", "message": "M", "priorite": "moyenne"}],
        }
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        app()
        mock_st.warning.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab2_rappels_basse_priorite(self, mock_retard, mock_charger, mock_db, mock_st):
        """Test rappel priorite basse."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {
            "agent_ia": MagicMock(),
            "rappels_ia": [{"routine": "R", "message": "M", "priorite": "basse"}],
        }
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        app()
        mock_st.info.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab2_rappels_vide(self, mock_retard, mock_charger, mock_db, mock_st):
        """Test aucun rappel."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": MagicMock(), "rappels_ia": []}
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        app()
        mock_st.success.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    @patch("src.modules.famille.routines.creer_routine")
    @patch("src.modules.famille.routines.ajouter_tache")
    def test_tab2_creer_routine_suggeree(
        self, mock_ajout, mock_creer, mock_retard, mock_charger, mock_db, mock_st
    ):
        """Test creation routine suggeree."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_creer.return_value = 100
        mock_st.session_state = {"agent_ia": MagicMock()}
        mock_st.button.side_effect = lambda l, **k: "create_Routine du matin" in k.get("key", "")
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        mock_creer.assert_called()
        assert mock_ajout.call_count == 4


class TestAppTab3Full:
    """Tests Tab3 - Creation routine."""

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    @patch("src.modules.famille.routines.creer_routine")
    @patch("src.modules.famille.routines.ajouter_tache")
    def test_tab3_creation_succes(
        self, mock_ajout, mock_creer, mock_retard, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test creation reussie."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_creer.return_value = 50
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.return_value = False
        mock_st.text_input.side_effect = lambda l, **k: "Ma routine" if "Nom" in l else "Tache"
        mock_st.text_area.return_value = "Desc"
        mock_st.selectbox.side_effect = lambda l, opts, **k: opts[0]
        mock_st.number_input.return_value = 1
        mock_t = MagicMock()
        mock_t.strftime.return_value = "09:00"
        mock_st.time_input.return_value = mock_t
        mock_st.form_submit_button.return_value = True

        mock_child = MagicMock()
        mock_child.name = "Jules"
        mock_sess = MagicMock()
        mock_sess.query.return_value.all.return_value = [mock_child]
        mock_sess.query.return_value.filter.return_value.count.return_value = 0
        _setup_mocks(mock_st, mock_db, mock_rt)
        mock_db.return_value.__enter__.return_value = mock_sess

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        mock_creer.assert_called()
        mock_st.balloons.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab3_erreur_sans_nom(self, mock_retard, mock_charger, mock_db, mock_st):
        """Test erreur sans nom."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.return_value = False
        mock_st.text_input.return_value = ""
        mock_st.text_area.return_value = ""
        mock_st.selectbox.return_value = "Famille"
        mock_st.number_input.return_value = 1
        mock_st.time_input.return_value = None
        mock_st.form_submit_button.return_value = True
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        app()
        mock_st.error.assert_any_call("Le nom est obligatoire")


class TestAppTab4Full:
    """Tests Tab4 - Suivi."""

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_tab4_avec_donnees(
        self, mock_retard, mock_taches, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test Tab4 avec donnees."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 1,
                    "nom": "R1",
                    "description": "",
                    "pour": "F",
                    "frequence": "q",
                    "active": True,
                    "ia": "",
                    "nb_taches": 2,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame(
            [
                {"id": 1, "nom": "T1", "heure": "08:00", "statut": "termine", "completed_at": None},
                {"id": 2, "nom": "T2", "heure": "09:00", "statut": "a faire", "completed_at": None},
            ]
        )
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.return_value = False
        mock_st.form_submit_button.return_value = False

        mock_sess = MagicMock()
        mock_sess.query.return_value.all.return_value = []
        mock_sess.query.return_value.filter.return_value.count.return_value = 5
        _setup_mocks(mock_st, mock_db, mock_rt)
        mock_db.return_value.__enter__.return_value = mock_sess

        from src.modules.famille.routines import app

        app()
        mock_st.metric.assert_called()
        mock_st.progress.assert_called()


class TestAlertesRetard:
    """Tests alertes taches retard."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    @patch("src.modules.famille.routines.marquer_complete")
    def test_click_bouton_retard(self, mock_marquer, mock_retard, mock_charger, mock_db, mock_st):
        """Test click bouton tache en retard."""
        mock_retard.return_value = [{"routine": "M", "tache": "R", "heure": "06:00", "id": 99}]
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": None}
        mock_st.button.side_effect = lambda l, **k: k.get("key", "") == "late_99"
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db)

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        mock_marquer.assert_called_with(99)


class TestBranchesSpeciales:
    """Tests branches speciales."""

    @patch("src.modules.famille.routines.obtenir_contexte_db")
    def test_creer_routine_enfant_introuvable(self, mock_db):
        """Test enfant non trouve."""
        mock_sess = MagicMock()
        mock_sess.query.return_value.filter.return_value.first.return_value = None
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_sess)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        mock_r = MagicMock()
        mock_r.id = 55
        from src.modules.famille.routines import creer_routine

        with patch("src.modules.famille.routines.Routine") as MR:
            MR.return_value = mock_r
            res = creer_routine("R", "D", "Unknown", "q")
            assert res == 55
            assert MR.call_args[1]["child_id"] is None

    @patch("src.modules.famille.routines.Routine")
    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    def test_heure_invalide_ignoree(self, mock_db, mock_tc, mock_rc):
        """Test exception pour heure invalide ignoree."""
        mock_sess = MagicMock()
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_sess)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)
        mock_t = MagicMock()
        mock_t.scheduled_time = "invalid"
        mock_r = MagicMock()
        mock_sess.query.return_value.join.return_value.filter.return_value.all.return_value = [
            (mock_t, mock_r)
        ]

        from src.modules.famille.routines import get_taches_en_retard

        res = get_taches_en_retard()
        assert len(res) == 0

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.asyncio")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_erreur_ia(self, mock_retard, mock_charger, mock_db, mock_st, mock_async, mock_rt):
        """Test erreur IA affichee."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame()
        mock_st.session_state = {"agent_ia": MagicMock()}
        mock_loop = MagicMock()
        mock_async.new_event_loop.return_value = mock_loop
        mock_loop.run_until_complete.side_effect = Exception("IA Error")
        mock_st.button.side_effect = lambda l, **k: "Demander rappels IA" in l
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db, mock_rt)

        from src.modules.famille.routines import app

        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_bouton_add_task(
        self, mock_retard, mock_taches, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test bouton ajouter tache."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 30,
                    "nom": "R",
                    "description": "",
                    "pour": "F",
                    "frequence": "q",
                    "active": True,
                    "ia": "",
                    "nb_taches": 1,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame(
            [{"id": 1, "nom": "T", "heure": "10:00", "statut": "a faire", "completed_at": None}]
        )
        sess = {"agent_ia": None}
        mock_st.session_state = sess
        mock_st.button.side_effect = lambda l, **k: k.get("key", "").startswith("add_")
        mock_st.form_submit_button.return_value = False
        _setup_mocks(mock_st, mock_db, mock_rt)

        from src.modules.famille.routines import app

        app()
        assert sess.get("adding_task_to") == 30

    @patch("src.modules.famille.routines.RoutineTask")
    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines.obtenir_contexte_db")
    @patch("src.modules.famille.routines.charger_routines")
    @patch("src.modules.famille.routines.charger_taches_routine")
    @patch("src.modules.famille.routines.get_taches_en_retard")
    def test_annuler_ajout_tache(
        self, mock_retard, mock_taches, mock_charger, mock_db, mock_st, mock_rt
    ):
        """Test annulation ajout tache."""
        mock_retard.return_value = []
        mock_charger.return_value = pd.DataFrame(
            [
                {
                    "id": 40,
                    "nom": "R",
                    "description": "",
                    "pour": "F",
                    "frequence": "q",
                    "active": True,
                    "ia": "",
                    "nb_taches": 1,
                }
            ]
        )
        mock_taches.return_value = pd.DataFrame(
            [{"id": 1, "nom": "T", "heure": "10:00", "statut": "a faire", "completed_at": None}]
        )
        sess = {"agent_ia": None, "adding_task_to": 40}
        mock_st.session_state = sess
        mock_st.button.return_value = False
        mock_st.text_input.return_value = ""
        mock_st.form_submit_button.side_effect = lambda l, **k: "Annuler" in l
        _setup_mocks(mock_st, mock_db, mock_rt)

        from src.modules.famille.routines import app

        try:
            app()
        except Exception:
            pass
        assert "adding_task_to" not in sess
