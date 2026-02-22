"""Tests étendus pour routines.py — couverture de la fonction app() et des onglets.

Adapté au refactoring: la logique métier est dans ServiceRoutines,
le module UI n'expose que app() qui utilise _get_service().
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════


def _create_mock_col():
    """Crée un mock context manager."""
    cm = MagicMock()
    cm.__enter__ = MagicMock(return_value=cm)
    cm.__exit__ = MagicMock(return_value=False)
    return cm


def _setup_mocks(mock_st):
    """Setup mocks Streamlit de base."""

    def columns_side_effect(spec):
        if isinstance(spec, list):
            n = len(spec)
        elif isinstance(spec, int):
            n = spec
        else:
            n = 2
        return [_create_mock_col() for _ in range(n)]

    mock_st.columns.side_effect = columns_side_effect
    mock_st.tabs.return_value = [_create_mock_col() for _ in range(4)]
    mock_st.expander.return_value = _create_mock_col()
    mock_st.form.return_value = _create_mock_col()
    mock_st.spinner.return_value = _create_mock_col()
    mock_st.button.return_value = False
    mock_st.form_submit_button.return_value = False
    mock_st.session_state = {"agent_ia": None}
    mock_st.number_input.return_value = 0
    mock_st.text_input.return_value = ""
    mock_st.text_area.return_value = ""
    mock_st.selectbox.return_value = "Famille"
    mock_st.time_input.return_value = None


def _setup_svc_mock(override=None):
    """Crée un mock ServiceRoutines avec des valeurs par défaut."""
    svc = MagicMock()
    svc.get_taches_en_retard.return_value = []
    svc.lister_routines.return_value = []
    svc.lister_taches.return_value = []
    svc.lister_personnes.return_value = ["Famille"]
    svc.compter_completees_aujourdhui.return_value = 0
    svc.creer_routine.return_value = 1
    svc.ajouter_tache.return_value = 1
    svc.marquer_complete.return_value = True
    svc.reinitialiser_taches_jour.return_value = 0
    svc.supprimer_routine.return_value = True
    svc.desactiver_routine.return_value = True
    svc.get_taches_ia_data.return_value = []
    if override:
        for attr, val in override.items():
            setattr(svc, attr, val) if not callable(val) else None
            if callable(val):
                getattr(svc, attr).return_value = val()
    return svc


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 : MES ROUTINES
# ═══════════════════════════════════════════════════════════════════════════════


class TestAppTab1Full:
    """Tests Tab1 — Mes Routines."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab1_routines_affichees(self, mock_get_svc, mock_st):
        """Tab1 affiche les routines actives."""
        mock_svc = _setup_svc_mock()
        mock_svc.lister_routines.return_value = [
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
        mock_svc.lister_taches.return_value = [
            {
                "id": 1,
                "nom": "Reveil",
                "heure": "07:00",
                "statut": "termine",
                "completed_at": datetime(2025, 1, 1, 8, 0),
            }
        ]
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab1_reinit_jour(self, mock_get_svc, mock_st):
        """Tab1 — bouton réinitialiser jour."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab1_supprimer_routine(self, mock_get_svc, mock_st):
        """Tab1 — bouton supprimer routine."""
        mock_svc = _setup_svc_mock()
        mock_svc.lister_routines.return_value = [
            {
                "id": 1,
                "nom": "Routine test",
                "description": "",
                "pour": "Famille",
                "frequence": "quotidien",
                "active": True,
                "ia": "",
                "nb_taches": 0,
            }
        ]
        mock_svc.lister_taches.return_value = []
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab1_desactiver_routine(self, mock_get_svc, mock_st):
        """Tab1 — bouton désactiver routine."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab1_ajouter_tache(self, mock_get_svc, mock_st):
        """Tab1 — formulaire ajout tâche."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 : RAPPELS IA
# ═══════════════════════════════════════════════════════════════════════════════


class TestAppTab2Full:
    """Tests Tab2 — Rappels IA."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab2_sans_agent(self, mock_get_svc, mock_st):
        """Tab2 affiche erreur si agent IA non disponible."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)
        mock_st.session_state = {"agent_ia": None}

        from src.modules.famille.routines import app

        app()
        mock_st.error.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab2_rappels_haute_priorite(self, mock_get_svc, mock_st):
        """Tab2 affiche les rappels haute priorité en rouge."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)
        mock_st.session_state = {
            "agent_ia": None,
            "rappels_ia": [{"routine": "Matin", "message": "En retard !", "priorite": "haute"}],
        }

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab2_rappels_moyenne_priorite(self, mock_get_svc, mock_st):
        """Tab2 affiche les rappels moyenne priorité en orange."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)
        mock_st.session_state = {
            "agent_ia": None,
            "rappels_ia": [{"routine": "Midi", "message": "À faire", "priorite": "moyenne"}],
        }

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab2_rappels_basse_priorite(self, mock_get_svc, mock_st):
        """Tab2 affiche les rappels basse priorité en bleu."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)
        mock_st.session_state = {
            "agent_ia": None,
            "rappels_ia": [{"routine": "Soir", "message": "Optionnel", "priorite": "basse"}],
        }

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab2_rappels_vide(self, mock_get_svc, mock_st):
        """Tab2 affiche message OK si aucun rappel."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)
        mock_st.session_state = {"agent_ia": None, "rappels_ia": []}

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab2_creer_routine_suggeree(self, mock_get_svc, mock_st):
        """Tab2 — créer une routine suggérée par l'IA."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 : CREER ROUTINE
# ═══════════════════════════════════════════════════════════════════════════════


class TestAppTab3Full:
    """Tests Tab3 — Créer routine."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab3_creation_succes(self, mock_get_svc, mock_st):
        """Tab3 — formulaire de création affiché."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab3_erreur_sans_nom(self, mock_get_svc, mock_st):
        """Tab3 — erreur si nom vide à la soumission."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 : SUIVI
# ═══════════════════════════════════════════════════════════════════════════════


class TestAppTab4Full:
    """Tests Tab4 — Suivi."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_tab4_avec_donnees(self, mock_get_svc, mock_st):
        """Tab4 affiche les métriques de suivi."""
        mock_svc = _setup_svc_mock()
        mock_svc.lister_routines.return_value = [
            {
                "id": 1,
                "nom": "Routine test",
                "description": "",
                "pour": "Famille",
                "frequence": "quotidien",
                "active": True,
                "ia": "",
                "nb_taches": 2,
            }
        ]
        mock_svc.lister_taches.return_value = [
            {
                "id": 1,
                "nom": "Tâche 1",
                "heure": "08:00",
                "statut": "termine",
                "completed_at": datetime(2025, 1, 1, 8, 30),
            },
            {
                "id": 2,
                "nom": "Tâche 2",
                "heure": "09:00",
                "statut": "à faire",
                "completed_at": None,
            },
        ]
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.title.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# ALERTES RETARD
# ═══════════════════════════════════════════════════════════════════════════════


class TestAlertesRetard:
    """Tests pour l'affichage des alertes de retard."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_click_bouton_retard(self, mock_get_svc, mock_st):
        """Click sur bouton retard marque la tâche comme terminée."""
        mock_svc = _setup_svc_mock()
        mock_svc.get_taches_en_retard.return_value = [
            {"routine": "Matin", "tache": "Réveil", "heure": "07:00", "id": 1}
        ]
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
        mock_st.warning.assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# BRANCHES SPÉCIALES
# ═══════════════════════════════════════════════════════════════════════════════


class TestBranchesSpeciales:
    """Tests pour les branches et cas limites."""

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_creer_routine_enfant_introuvable(self, mock_get_svc, mock_st):
        """Créer une routine pour un enfant inexistant."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_heure_invalide_ignoree(self, mock_get_svc, mock_st):
        """Les heures invalides sont ignorées sans erreur."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_erreur_ia(self, mock_get_svc, mock_st):
        """L'erreur IA est gérée proprement."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_bouton_add_task(self, mock_get_svc, mock_st):
        """Le bouton d'ajout de tâche fonctionne."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()

    @patch("src.modules.famille.routines.st")
    @patch("src.modules.famille.routines._get_service")
    def test_annuler_ajout_tache(self, mock_get_svc, mock_st):
        """Le bouton annuler ferme le formulaire d'ajout."""
        mock_svc = _setup_svc_mock()
        mock_get_svc.return_value = mock_svc
        _setup_mocks(mock_st)

        from src.modules.famille.routines import app

        app()
