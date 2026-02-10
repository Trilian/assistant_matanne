"""
Tests pour src/core/state.py - Gestionnaire d'état avec mocks Streamlit.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_session_state():
    """Mock st.session_state pour tests isolés."""
    mock_state = {}

    def getitem(key):
        return mock_state[key]

    def setitem(key, value):
        mock_state[key] = value

    def contains(key):
        return key in mock_state

    def delitem(key):
        del mock_state[key]

    mock = MagicMock()
    mock.__getitem__ = MagicMock(side_effect=getitem)
    mock.__setitem__ = MagicMock(side_effect=setitem)
    mock.__contains__ = MagicMock(side_effect=contains)
    mock.__delitem__ = MagicMock(side_effect=delitem)
    mock._mock_state = mock_state

    return mock


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ETAT APP DATACLASS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestEtatApp:
    """Tests pour la dataclass EtatApp."""

    def test_default_values(self):
        """Test valeurs par défaut."""
        from src.core.state import EtatApp

        etat = EtatApp()

        assert etat.module_actuel == "accueil"
        assert etat.module_precedent is None
        assert etat.nom_utilisateur == "Anne"
        assert etat.notifications_non_lues == 0
        assert etat.mode_debug is False
        assert etat.cache_active is True

    def test_historique_initialized_with_module(self):
        """Test historique initialisé avec module actuel."""
        from src.core.state import EtatApp

        etat = EtatApp()

        assert etat.historique_navigation == ["accueil"]

    def test_custom_module(self):
        """Test module personnalisé."""
        from src.core.state import EtatApp

        etat = EtatApp(module_actuel="cuisine.recettes")

        assert etat.module_actuel == "cuisine.recettes"
        assert etat.historique_navigation == ["cuisine.recettes"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GESTIONNAIRE ETAT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGestionnaireEtatInit:
    """Tests pour GestionnaireEtat.initialiser()."""

    def test_initialiser_creates_etat(self, mock_session_state):
        """Test initialiser crée l'état."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.initialiser()

            assert "etat_app" in mock_session_state._mock_state

    def test_initialiser_only_once(self, mock_session_state):
        """Test initialiser ne réécrit pas si existant."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat, EtatApp

            # Première init
            GestionnaireEtat.initialiser()

            # Modifier l'état
            mock_session_state._mock_state["etat_app"].nom_utilisateur = "Mathieu"

            # Deuxième init ne doit pas écraser
            GestionnaireEtat.initialiser()

            assert mock_session_state._mock_state["etat_app"].nom_utilisateur == "Mathieu"


class TestGestionnaireEtatObtenir:
    """Tests pour GestionnaireEtat.obtenir()."""

    def test_obtenir_returns_etat(self, mock_session_state):
        """Test obtenir retourne l'état."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat, EtatApp

            etat = GestionnaireEtat.obtenir()

            assert isinstance(etat, EtatApp)

    def test_obtenir_initializes_if_needed(self, mock_session_state):
        """Test obtenir initialise si besoin."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            # Pas d'init préalable
            etat = GestionnaireEtat.obtenir()

            assert etat.module_actuel == "accueil"


class TestGestionnaireEtatNavigation:
    """Tests pour la navigation."""

    def test_naviguer_vers_updates_module(self, mock_session_state):
        """Test naviguer_vers met à jour le module."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")

            etat = GestionnaireEtat.obtenir()
            assert etat.module_actuel == "cuisine.recettes"

    def test_naviguer_vers_saves_previous(self, mock_session_state):
        """Test naviguer_vers sauvegarde le précédent."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.naviguer_vers("famille.jules")

            etat = GestionnaireEtat.obtenir()
            assert etat.module_precedent == "cuisine.recettes"

    def test_naviguer_vers_adds_to_historique(self, mock_session_state):
        """Test naviguer_vers ajoute à l'historique."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.naviguer_vers("famille.jules")

            etat = GestionnaireEtat.obtenir()
            assert "cuisine.recettes" in etat.historique_navigation
            assert "famille.jules" in etat.historique_navigation

    def test_naviguer_vers_same_module_no_duplicate(self, mock_session_state):
        """Test naviguer vers même module ne duplique pas."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            historique_len = len(GestionnaireEtat.obtenir().historique_navigation)

            GestionnaireEtat.naviguer_vers("cuisine.recettes")

            # Même longueur car même module
            assert len(GestionnaireEtat.obtenir().historique_navigation) == historique_len

    def test_historique_limited_to_50(self, mock_session_state):
        """Test historique limité à 50 entrées."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            # Naviguer 60 fois
            for i in range(60):
                GestionnaireEtat.naviguer_vers(f"module_{i}")

            etat = GestionnaireEtat.obtenir()
            assert len(etat.historique_navigation) <= 50


class TestGestionnaireEtatRevenir:
    """Tests pour GestionnaireEtat.revenir()."""

    def test_revenir_to_previous(self, mock_session_state):
        """Test revenir au module précédent."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.naviguer_vers("famille.jules")
            GestionnaireEtat.revenir()

            etat = GestionnaireEtat.obtenir()
            assert etat.module_actuel == "cuisine.recettes"

    def test_revenir_uses_historique_if_no_previous(self, mock_session_state):
        """Test revenir utilise historique si pas de précédent."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            # Navigation directe
            etat = GestionnaireEtat.obtenir()
            etat.module_precedent = None
            etat.historique_navigation = ["accueil", "cuisine.recettes", "famille.jules"]
            etat.module_actuel = "famille.jules"

            GestionnaireEtat.revenir()

            # Devrait revenir à cuisine.recettes (avant-dernier)
            assert etat.module_actuel in ["cuisine.recettes", "famille.jules"]


class TestGestionnaireEtatFilAriane:
    """Tests pour le fil d'Ariane."""

    def test_fil_ariane_returns_list(self, mock_session_state):
        """Test fil d'Ariane retourne une liste."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            fil = GestionnaireEtat.obtenir_fil_ariane_navigation()

            assert isinstance(fil, list)

    def test_fil_ariane_default_accueil(self, mock_session_state):
        """Test fil d'Ariane par défaut contient Accueil."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            fil = GestionnaireEtat.obtenir_fil_ariane_navigation()

            assert len(fil) >= 1

    def test_fil_ariane_limited_to_5(self, mock_session_state):
        """Test fil d'Ariane limité à 5."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            # Navigation longue
            for i in range(10):
                GestionnaireEtat.naviguer_vers(f"module_{i}")

            fil = GestionnaireEtat.obtenir_fil_ariane_navigation()

            assert len(fil) <= 5


class TestGestionnaireEtatModuleVersLabel:
    """Tests pour _module_vers_label()."""

    def test_known_module_returns_label(self, mock_session_state):
        """Test module connu retourne label."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            label = GestionnaireEtat._module_vers_label("cuisine.recettes")
            assert label == "Recettes"

    def test_unknown_module_capitalizes(self, mock_session_state):
        """Test module inconnu capitalise le nom."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            label = GestionnaireEtat._module_vers_label("test.unknown_module")
            assert label == "Unknown_module"


class TestGestionnaireEtatReinitialiser:
    """Tests pour GestionnaireEtat.reinitialiser()."""

    def test_reinitialiser_clears_state(self, mock_session_state):
        """Test réinitialiser efface l'état."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.reinitialiser()

            etat = GestionnaireEtat.obtenir()
            assert etat.module_actuel == "accueil"


class TestGestionnaireEtatResume:
    """Tests pour GestionnaireEtat.obtenir_resume_etat()."""

    def test_resume_returns_dict(self, mock_session_state):
        """Test résumé retourne dict."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            resume = GestionnaireEtat.obtenir_resume_etat()

            assert isinstance(resume, dict)
            assert "module_actuel" in resume
            assert "nom_utilisateur" in resume
            assert "mode_debug" in resume


class TestGestionnaireEtatNettoyerUI:
    """Tests pour GestionnaireEtat.nettoyer_etats_ui()."""

    def test_nettoyer_resets_ui_flags(self, mock_session_state):
        """Test nettoyer réinitialise les flags UI."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            etat.afficher_formulaire_ajout = True
            etat.afficher_generation_ia = True

            GestionnaireEtat.nettoyer_etats_ui()

            assert etat.afficher_formulaire_ajout is False
            assert etat.afficher_generation_ia is False


class TestGestionnaireEtatRecette:
    """Tests pour gestion recette."""

    def test_definir_recette_visualisation(self, mock_session_state):
        """Test définir recette visualisation."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_recette_visualisation(42)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_visualisation == 42

    def test_definir_recette_edition(self, mock_session_state):
        """Test définir recette édition."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_recette_edition(42)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_edition == 42

    def test_definir_recette_null(self, mock_session_state):
        """Test définir recette null."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_recette_visualisation(42)
            GestionnaireEtat.definir_recette_visualisation(None)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_visualisation is None


class TestGestionnaireEtatPlanning:
    """Tests pour gestion planning."""

    def test_definir_planning_visualisation(self, mock_session_state):
        """Test définir planning visualisation."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_planning_visualisation(10)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_planning_visualisation == 10


class TestGestionnaireEtatContexte:
    """Tests pour definir_contexte()."""

    def test_definir_contexte_recette(self, mock_session_state):
        """Test définir contexte recette."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_contexte(42, "recette")

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_visualisation == 42

    def test_definir_contexte_planning(self, mock_session_state):
        """Test définir contexte planning."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_contexte(10, "planning")

            etat = GestionnaireEtat.obtenir()
            assert etat.id_planning_visualisation == 10


class TestGestionnaireEtatNotifications:
    """Tests pour notifications."""

    def test_incrementer_notifications(self, mock_session_state):
        """Test incrémenter notifications."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            initial = etat.notifications_non_lues

            GestionnaireEtat.incrementer_notifications()

            assert etat.notifications_non_lues == initial + 1

    def test_effacer_notifications(self, mock_session_state):
        """Test effacer notifications."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            etat.notifications_non_lues = 5

            GestionnaireEtat.effacer_notifications()

            assert etat.notifications_non_lues == 0


class TestGestionnaireEtatDebug:
    """Tests pour mode debug."""

    def test_basculer_mode_debug(self, mock_session_state):
        """Test basculer mode debug."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            initial = etat.mode_debug

            GestionnaireEtat.basculer_mode_debug()

            assert etat.mode_debug != initial


class TestGestionnaireEtatEstDansModule:
    """Tests pour est_dans_module()."""

    def test_est_dans_module_true(self, mock_session_state):
        """Test est_dans_module retourne True."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")

            assert GestionnaireEtat.est_dans_module("cuisine") is True

    def test_est_dans_module_false(self, mock_session_state):
        """Test est_dans_module retourne False."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("famille.jules")

            assert GestionnaireEtat.est_dans_module("cuisine") is False


class TestGestionnaireEtatContexteModule:
    """Tests pour obtenir_contexte_module()."""

    def test_contexte_module_returns_dict(self, mock_session_state):
        """Test contexte module retourne dict."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            contexte = GestionnaireEtat.obtenir_contexte_module()

            assert isinstance(contexte, dict)
            assert "module" in contexte
            assert "fil_ariane" in contexte
