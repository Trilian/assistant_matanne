"""
Tests pour src/core/state.py - Gestionnaire d'état avec MemorySessionStorage.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.core.storage import MemorySessionStorage, configurer_storage


@pytest.fixture(autouse=True)
def memory_storage():
    """Configure un storage mémoire propre pour chaque test."""
    storage = MemorySessionStorage()
    configurer_storage(storage)
    yield storage
    # Cleanup
    storage.clear()


@pytest.fixture
def mock_session_state():
    """Legacy fixture — redirige vers MemorySessionStorage."""
    # Fixture conservée pour compatibilité mais ne fait plus rien
    # car memory_storage (autouse) gère le setup
    yield None


# ═══════════════════════════════════════════════════════════
# TESTS ETAT APP DATACLASS
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# TESTS GESTIONNAIRE ETAT
# ═══════════════════════════════════════════════════════════


class TestGestionnaireEtatInit:
    """Tests pour GestionnaireEtat.initialiser()."""

    def test_initialiser_creates_etat(self, memory_storage):
        """Test initialiser crée l'état."""
        from src.core.state import GestionnaireEtat

        GestionnaireEtat.initialiser()

        assert memory_storage.contains("etat_app")

    def test_initialiser_only_once(self, memory_storage):
        """Test initialiser ne réécrit pas si existant."""
        from src.core.state import GestionnaireEtat

        # Première init
        GestionnaireEtat.initialiser()

        # Modifier l'état
        etat = memory_storage.get("etat_app")
        etat.nom_utilisateur = "Mathieu"
        memory_storage.set("etat_app", etat)

        # Deuxième init ne doit pas écraser
        GestionnaireEtat.initialiser()

        assert memory_storage.get("etat_app").nom_utilisateur == "Mathieu"


class TestGestionnaireEtatObtenir:
    """Tests pour GestionnaireEtat.obtenir()."""

    def test_obtenir_returns_etat(self):
        """Test obtenir retourne l'état."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import EtatApp, GestionnaireEtat

            etat = GestionnaireEtat.obtenir()

            assert isinstance(etat, EtatApp)

    def test_obtenir_initializes_if_needed(self):
        """Test obtenir initialise si besoin."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            # Pas d'init préalable
            etat = GestionnaireEtat.obtenir()

            assert etat.module_actuel == "accueil"


class TestGestionnaireEtatNavigation:
    """Tests pour la navigation."""

    def test_naviguer_vers_updates_module(self):
        """Test naviguer_vers met à jour le module."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")

            etat = GestionnaireEtat.obtenir()
            assert etat.module_actuel == "cuisine.recettes"

    def test_naviguer_vers_saves_previous(self):
        """Test naviguer_vers sauvegarde le précédent."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.naviguer_vers("famille.jules")

            etat = GestionnaireEtat.obtenir()
            assert etat.module_precedent == "cuisine.recettes"

    def test_naviguer_vers_adds_to_historique(self):
        """Test naviguer_vers ajoute à l'historique."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.naviguer_vers("famille.jules")

            etat = GestionnaireEtat.obtenir()
            assert "cuisine.recettes" in etat.historique_navigation
            assert "famille.jules" in etat.historique_navigation

    def test_naviguer_vers_same_module_no_duplicate(self):
        """Test naviguer vers même module ne duplique pas."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            historique_len = len(GestionnaireEtat.obtenir().historique_navigation)

            GestionnaireEtat.naviguer_vers("cuisine.recettes")

            # Même longueur car même module
            assert len(GestionnaireEtat.obtenir().historique_navigation) == historique_len

    def test_historique_limited_to_50(self):
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

    def test_revenir_to_previous(self):
        """Test revenir au module précédent."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.naviguer_vers("famille.jules")
            GestionnaireEtat.revenir()

            etat = GestionnaireEtat.obtenir()
            assert etat.module_actuel == "cuisine.recettes"

    def test_revenir_uses_historique_if_no_previous(self):
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

    def test_fil_ariane_returns_list(self):
        """Test fil d'Ariane retourne une liste."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            fil = GestionnaireEtat.obtenir_fil_ariane_navigation()

            assert isinstance(fil, list)

    def test_fil_ariane_default_accueil(self):
        """Test fil d'Ariane par défaut contient Accueil."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            fil = GestionnaireEtat.obtenir_fil_ariane_navigation()

            assert len(fil) >= 1

    def test_fil_ariane_limited_to_5(self):
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

    def test_known_module_returns_label(self):
        """Test module connu retourne label."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            label = GestionnaireEtat._module_vers_label("cuisine.recettes")
            assert label == "Recettes"

    def test_unknown_module_capitalizes(self):
        """Test module inconnu capitalise le nom."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            label = GestionnaireEtat._module_vers_label("test.unknown_module")
            assert label == "Unknown_module"


class TestGestionnaireEtatReinitialiser:
    """Tests pour GestionnaireEtat.reinitialiser()."""

    def test_reinitialiser_clears_state(self):
        """Test réinitialiser efface l'état."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")
            GestionnaireEtat.reinitialiser()

            etat = GestionnaireEtat.obtenir()
            assert etat.module_actuel == "accueil"


class TestGestionnaireEtatResume:
    """Tests pour GestionnaireEtat.obtenir_resume_etat()."""

    def test_resume_returns_dict(self):
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

    def test_nettoyer_resets_ui_flags(self):
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

    def test_definir_recette_visualisation(self):
        """Test définir recette visualisation."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_recette_visualisation(42)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_visualisation == 42

    def test_definir_recette_edition(self):
        """Test définir recette édition."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_recette_edition(42)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_edition == 42

    def test_definir_recette_null(self):
        """Test définir recette null."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_recette_visualisation(42)
            GestionnaireEtat.definir_recette_visualisation(None)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_visualisation is None


class TestGestionnaireEtatPlanning:
    """Tests pour gestion planning."""

    def test_definir_planning_visualisation(self):
        """Test définir planning visualisation."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_planning_visualisation(10)

            etat = GestionnaireEtat.obtenir()
            assert etat.id_planning_visualisation == 10


class TestGestionnaireEtatContexte:
    """Tests pour definir_contexte()."""

    def test_definir_contexte_recette(self):
        """Test définir contexte recette."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_contexte(42, "recette")

            etat = GestionnaireEtat.obtenir()
            assert etat.id_recette_visualisation == 42

    def test_definir_contexte_planning(self):
        """Test définir contexte planning."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.definir_contexte(10, "planning")

            etat = GestionnaireEtat.obtenir()
            assert etat.id_planning_visualisation == 10


class TestGestionnaireEtatNotifications:
    """Tests pour notifications."""

    def test_incrementer_notifications(self):
        """Test incrémenter notifications."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            initial = etat.notifications_non_lues

            GestionnaireEtat.incrementer_notifications()

            assert etat.notifications_non_lues == initial + 1

    def test_effacer_notifications(self):
        """Test effacer notifications."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            etat.notifications_non_lues = 5

            GestionnaireEtat.effacer_notifications()

            assert etat.notifications_non_lues == 0


class TestGestionnaireEtatDebug:
    """Tests pour mode debug."""

    def test_basculer_mode_debug(self):
        """Test basculer mode debug."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            etat = GestionnaireEtat.obtenir()
            initial = etat.mode_debug

            GestionnaireEtat.basculer_mode_debug()

            assert etat.mode_debug != initial


class TestGestionnaireEtatEstDansModule:
    """Tests pour est_dans_module()."""

    def test_est_dans_module_true(self):
        """Test est_dans_module retourne True."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("cuisine.recettes")

            assert GestionnaireEtat.est_dans_module("cuisine") is True

    def test_est_dans_module_false(self):
        """Test est_dans_module retourne False."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            GestionnaireEtat.naviguer_vers("famille.jules")

            assert GestionnaireEtat.est_dans_module("cuisine") is False


class TestGestionnaireEtatContexteModule:
    """Tests pour obtenir_contexte_module()."""

    def test_contexte_module_returns_dict(self):
        """Test contexte module retourne dict."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.state import GestionnaireEtat

            contexte = GestionnaireEtat.obtenir_contexte_module()

            assert isinstance(contexte, dict)
            assert "module" in contexte
            assert "fil_ariane" in contexte
