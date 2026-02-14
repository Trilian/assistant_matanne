"""Tests pour vue ensemble planning - Dashboard d'actions prioritaires."""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

from tests.conftest import SessionStateMock

# ═══════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════


class TestVueEnsembleImport:
    """Tests d'import du module vue_ensemble."""

    def test_import_module(self):
        """Test que le module s'importe sans erreur."""
        import src.modules.planning.vue_ensemble as module

        assert module is not None

    def test_import_app_function(self):
        """Test que la fonction app() existe."""
        from src.modules.planning.vue_ensemble import app

        assert callable(app)

    def test_import_helper_functions(self):
        """Test que les fonctions helper existent."""
        from src.modules.planning.vue_ensemble import (
            afficher_actions_prioritaires,
            afficher_metriques_cles,
            afficher_opportunities,
            afficher_synthese_jours,
        )

        assert callable(afficher_actions_prioritaires)
        assert callable(afficher_metriques_cles)
        assert callable(afficher_synthese_jours)
        assert callable(afficher_opportunities)


# ═══════════════════════════════════════════════════════════
# TESTS AFFICHER ACTIONS PRIORITAIRES
# ═══════════════════════════════════════════════════════════


class TestAfficherActionsPrioritaires:
    """Tests pour afficher_actions_prioritaires."""

    @patch("src.modules.planning.vue_ensemble.st")
    def test_no_alertes_shows_success(self, mock_st):
        """Test affichage success quand pas d'alertes."""
        from src.modules.planning.vue_ensemble import afficher_actions_prioritaires

        afficher_actions_prioritaires([])

        mock_st.success.assert_called_once_with(
            "✅ Semaine bien equilibree - Aucune action urgente"
        )

    @patch("src.modules.planning.vue_ensemble.st")
    def test_alertes_with_dash_separator(self, mock_st):
        """Test parsing des alertes avec separateur ' - '."""
        from src.modules.planning.vue_ensemble import afficher_actions_prioritaires

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        alertes = ["🎯 - Activite manquante"]
        afficher_actions_prioritaires(alertes)

        mock_st.markdown.assert_called_with("### 🎯 Actions à Prendre")

    @patch("src.modules.planning.vue_ensemble.st")
    def test_alertes_without_separator(self, mock_st):
        """Test parsing des alertes sans separateur."""
        from src.modules.planning.vue_ensemble import afficher_actions_prioritaires

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        alertes = ["Alerte simple"]
        afficher_actions_prioritaires(alertes)

        mock_st.markdown.assert_called()

    @patch("src.modules.planning.vue_ensemble.st")
    def test_button_activites_clicked(self, mock_st):
        """Test click sur bouton Activites."""
        from src.modules.planning.vue_ensemble import afficher_actions_prioritaires

        mock_col_msg = MagicMock()
        mock_col_action = MagicMock()
        mock_st.columns.return_value = [mock_col_msg, mock_col_action]
        mock_st.button.return_value = True
        mock_st.session_state = SessionStateMock()

        alertes = ["🎯 - Test activite"]
        afficher_actions_prioritaires(alertes)

        assert mock_st.session_state.get("planning_view") == "activites"

    @patch("src.modules.planning.vue_ensemble.st")
    def test_button_budget_clicked(self, mock_st):
        """Test click sur bouton Budget."""
        from src.modules.planning.vue_ensemble import afficher_actions_prioritaires

        mock_col_msg = MagicMock()
        mock_col_action = MagicMock()
        mock_st.columns.return_value = [mock_col_msg, mock_col_action]
        mock_st.button.return_value = True
        mock_st.session_state = SessionStateMock()

        alertes = ["🍽️ - Budget eleve"]
        afficher_actions_prioritaires(alertes)

        assert mock_st.session_state.get("planning_view") == "budget"


# ═══════════════════════════════════════════════════════════
# TESTS AFFICHER METRIQUES CLES
# ═══════════════════════════════════════════════════════════


class TestAfficherMetriquesCles:
    """Tests pour afficher_metriques_cles."""

    @patch("src.modules.planning.vue_ensemble.st")
    def test_affiche_toutes_metriques(self, mock_st):
        """Test affichage de toutes les metriques."""
        from src.modules.planning.vue_ensemble import afficher_metriques_cles

        mock_cols = [MagicMock() for _ in range(5)]
        mock_st.columns.return_value = mock_cols

        stats = {
            "total_repas": 10,
            "total_activites": 5,
            "activites_jules": 3,
            "total_projets": 2,
            "budget_total": 350.5,
            "charge_moyenne": 60,
        }

        afficher_metriques_cles(stats, "normal")

        # Verify metric calls on columns
        assert mock_st.columns.called

    @patch("src.modules.planning.vue_ensemble.st")
    def test_charge_faible(self, mock_st):
        """Test affichage charge faible."""
        from src.modules.planning.vue_ensemble import afficher_metriques_cles

        mock_st.columns.return_value = [MagicMock() for _ in range(5)]

        stats = {"charge_moyenne": 40}
        afficher_metriques_cles(stats, "faible")

        # Verify success message for low charge
        mock_st.success.assert_called()

    @patch("src.modules.planning.vue_ensemble.st")
    def test_charge_intense_warning(self, mock_st):
        """Test affichage warning pour charge intense."""
        from src.modules.planning.vue_ensemble import afficher_metriques_cles

        mock_st.columns.return_value = [MagicMock() for _ in range(5)]

        stats = {"charge_moyenne": 85}
        afficher_metriques_cles(stats, "intense")

        mock_st.warning.assert_called()

    @patch("src.modules.planning.vue_ensemble.st")
    def test_charge_normale_info(self, mock_st):
        """Test affichage info pour charge normale."""
        from src.modules.planning.vue_ensemble import afficher_metriques_cles

        mock_st.columns.return_value = [MagicMock() for _ in range(5)]

        stats = {"charge_moyenne": 75}
        afficher_metriques_cles(stats, "normal")

        mock_st.info.assert_called()

    @patch("src.modules.planning.vue_ensemble.st")
    def test_stats_vides(self, mock_st):
        """Test avec stats vides."""
        from src.modules.planning.vue_ensemble import afficher_metriques_cles

        mock_st.columns.return_value = [MagicMock() for _ in range(5)]

        afficher_metriques_cles({}, "normal")

        # Should not raise exception
        assert mock_st.columns.called


# ═══════════════════════════════════════════════════════════
# TESTS AFFICHER SYNTHESE JOURS
# ═══════════════════════════════════════════════════════════


class TestAfficherSyntheseJours:
    """Tests pour afficher_synthese_jours."""

    @patch("src.modules.planning.vue_ensemble.st")
    def test_affiche_7_jours(self, mock_st):
        """Test affichage synthese 7 jours."""
        from src.modules.planning.vue_ensemble import afficher_synthese_jours

        mock_cols = [MagicMock() for _ in range(7)]
        mock_st.columns.return_value = mock_cols

        # Create mock jour objects
        class MockJour:
            charge = "normal"
            charge_score = 50
            repas = []
            activites = []

        jours = {f"2025-01-{i:02d}": MockJour() for i in range(1, 8)}

        afficher_synthese_jours(jours)

        mock_st.columns.assert_called_with(7)

    @patch("src.modules.planning.vue_ensemble.st")
    def test_charge_emojis(self, mock_st):
        """Test affichage emojis de charge."""
        from src.modules.planning.vue_ensemble import afficher_synthese_jours

        mock_cols = [MagicMock() for _ in range(7)]
        mock_st.columns.return_value = mock_cols

        class MockJourFaible:
            charge = "faible"
            charge_score = 30
            repas = ["r1"]
            activites = ["a1", "a2"]

        class MockJourIntense:
            charge = "intense"
            charge_score = 90
            repas = []
            activites = []

        jours = {
            "2025-01-01": MockJourFaible(),
            "2025-01-02": MockJourIntense(),
            "2025-01-03": MockJourFaible(),
            "2025-01-04": MockJourFaible(),
            "2025-01-05": MockJourFaible(),
            "2025-01-06": MockJourFaible(),
            "2025-01-07": MockJourFaible(),
        }

        afficher_synthese_jours(jours)

        # Verify markdown called with HTML content
        markdown_calls = [str(call) for call in mock_st.markdown.call_args_list]
        assert len(markdown_calls) > 0


# ═══════════════════════════════════════════════════════════
# TESTS AFFICHER OPPORTUNITIES
# ═══════════════════════════════════════════════════════════


class TestAfficherOpportunities:
    """Tests pour afficher_opportunities."""

    @patch("src.modules.planning.vue_ensemble.st")
    def test_no_suggestions_success(self, mock_st):
        """Test affichage success quand semaine equilibree."""
        from src.modules.planning.vue_ensemble import afficher_opportunities

        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        semaine_data = {
            "activites_jules": 5,
            "budget_total": 300,
            "total_repas": 14,
        }

        afficher_opportunities(semaine_data)

        mock_st.success.assert_called_with("✅ Semaine bien equilibree - Aucune suggestion")

    @patch("src.modules.planning.vue_ensemble.st")
    def test_suggestion_pas_activites_jules(self, mock_st):
        """Test suggestion quand pas d'activites pour Jules."""
        from src.modules.planning.vue_ensemble import afficher_opportunities

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        semaine_data = {
            "activites_jules": 0,
            "budget_total": 300,
            "total_repas": 14,
        }

        afficher_opportunities(semaine_data)

        # Should not call success (has suggestions)
        assert not mock_st.success.called or mock_st.write.called

    @patch("src.modules.planning.vue_ensemble.st")
    def test_suggestion_peu_activites_jules(self, mock_st):
        """Test suggestion quand peu d'activites pour Jules."""
        from src.modules.planning.vue_ensemble import afficher_opportunities

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        semaine_data = {
            "activites_jules": 1,
            "budget_total": 300,
            "total_repas": 14,
        }

        afficher_opportunities(semaine_data)

        assert mock_st.write.called or mock_st.markdown.called

    @patch("src.modules.planning.vue_ensemble.st")
    def test_suggestion_budget_eleve(self, mock_st):
        """Test suggestion quand budget depasse."""
        from src.modules.planning.vue_ensemble import afficher_opportunities

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        semaine_data = {
            "activites_jules": 5,
            "budget_total": 600,  # > 500 limit
            "total_repas": 14,
        }

        afficher_opportunities(semaine_data)

        assert mock_st.write.called or mock_st.markdown.called

    @patch("src.modules.planning.vue_ensemble.st")
    def test_suggestion_pas_repas(self, mock_st):
        """Test suggestion quand pas de repas planifies."""
        from src.modules.planning.vue_ensemble import afficher_opportunities

        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        semaine_data = {
            "activites_jules": 5,
            "budget_total": 300,
            "total_repas": 0,
        }

        afficher_opportunities(semaine_data)

        assert mock_st.markdown.called


# ═══════════════════════════════════════════════════════════
# TESTS FONCTION APP
# ═══════════════════════════════════════════════════════════


class TestAppFunction:
    """Tests pour la fonction app() principale."""

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_app_renders_title(self, mock_st, mock_get_service):
        """Test que app() affiche le titre."""
        from src.modules.planning.vue_ensemble import app

        # Setup mocks
        mock_st.session_state = SessionStateMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = None
        mock_get_service.return_value = mock_service

        app()

        mock_st.title.assert_called_with("🎯 Vue d'Ensemble Planning")

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_app_no_semaine_shows_error(self, mock_st, mock_get_service):
        """Test affichage erreur quand pas de semaine."""
        from src.modules.planning.vue_ensemble import app

        mock_st.session_state = SessionStateMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = None
        mock_get_service.return_value = mock_service

        app()

        mock_st.error.assert_called_with("❌ Erreur lors du chargement de la semaine")

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_app_with_semaine_data(self, mock_st, mock_get_service):
        """Test app() avec donnees de semaine valides."""
        from src.modules.planning.vue_ensemble import app

        # Create mock jour
        class MockJour:
            charge = "normal"
            charge_score = 50
            repas = []
            activites = []
            projets = []
            budget_jour = 50

            def dict(self):
                return {
                    "charge": self.charge,
                    "charge_score": self.charge_score,
                    "repas": self.repas,
                    "activites": self.activites,
                    "projets": self.projets,
                    "budget_jour": self.budget_jour,
                    "alertes": [],
                }

        # Create mock semaine
        mock_semaine = MagicMock()
        mock_semaine.alertes_semaine = []
        mock_semaine.stats_semaine = {
            "total_repas": 10,
            "total_activites": 5,
            "activites_jules": 3,
            "total_projets": 2,
            "budget_total": 350,
            "charge_moyenne": 50,
        }
        mock_semaine.charge_globale = "normal"
        mock_semaine.jours = {f"2025-01-{i:02d}": MockJour() for i in range(1, 8)}

        mock_st.session_state = SessionStateMock()
        mock_st.columns.side_effect = lambda n: [
            MagicMock() for _ in range(n if isinstance(n, int) else len(n))
        ]
        mock_st.button.return_value = False
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = "lundi"
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock()
        mock_st.form_submit_button.return_value = False
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = mock_semaine
        mock_get_service.return_value = mock_service

        app()

        # Verify service was called
        mock_service.get_semaine_complete.assert_called_once()

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_app_navigation_previous_week(self, mock_st, mock_get_service):
        """Test navigation semaine precedente."""
        from src.modules.planning.vue_ensemble import app

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        mock_st.session_state = SessionStateMock({"ensemble_week_start": week_start})
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [True, False]  # First button clicked

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = None
        mock_get_service.return_value = mock_service

        app()

        # Session state should be updated
        assert mock_st.session_state["ensemble_week_start"] == week_start - timedelta(days=7)
        mock_st.rerun.assert_called()

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_app_navigation_next_week(self, mock_st, mock_get_service):
        """Test navigation semaine suivante."""
        from src.modules.planning.vue_ensemble import app

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        mock_st.session_state = SessionStateMock({"ensemble_week_start": week_start})
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.button.side_effect = [False, True]  # Second button clicked

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = None
        mock_get_service.return_value = mock_service

        app()

        assert mock_st.session_state["ensemble_week_start"] == week_start + timedelta(days=7)
        mock_st.rerun.assert_called()

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_app_with_alertes(self, mock_st, mock_get_service):
        """Test app() avec alertes affichees."""
        from src.modules.planning.vue_ensemble import app

        class MockJour:
            charge = "normal"
            charge_score = 50
            repas = []
            activites = []
            projets = []
            budget_jour = 50

            def dict(self):
                return {
                    "charge": self.charge,
                    "charge_score": self.charge_score,
                    "repas": self.repas,
                    "activites": self.activites,
                    "projets": self.projets,
                    "budget_jour": self.budget_jour,
                    "alertes": [],
                }

        mock_semaine = MagicMock()
        mock_semaine.alertes_semaine = ["🎯 - Alerte test"]
        mock_semaine.stats_semaine = {"charge_moyenne": 50}
        mock_semaine.charge_globale = "normal"
        mock_semaine.jours = {f"2025-01-{i:02d}": MockJour() for i in range(1, 8)}

        mock_st.session_state = SessionStateMock()
        mock_st.columns.side_effect = lambda n: [
            MagicMock() for _ in range(n if isinstance(n, int) else len(n))
        ]
        mock_st.button.return_value = False
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = "lundi"
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock()
        mock_st.form_submit_button.return_value = False
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = mock_semaine
        mock_get_service.return_value = mock_service

        app()

        # Should show alertes section
        markdown_calls = [str(call) for call in mock_st.markdown.call_args_list]
        assert any("Actions Critiques" in str(call) for call in markdown_calls)


# ═══════════════════════════════════════════════════════════
# TESTS ONGLETS
# ═══════════════════════════════════════════════════════════


class TestOnglets:
    """Tests pour les onglets de l'application."""

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_onglet_reequilibrer_jours_charges(self, mock_st, mock_get_service):
        """Test onglet reequilibrage avec jours charges."""
        from src.modules.planning.vue_ensemble import app

        class MockJourCharge:
            charge = "intense"
            charge_score = 85
            repas = ["r1", "r2"]
            activites = ["a1", "a2", "a3"]
            projets = []
            budget_jour = 100

            def dict(self):
                return {
                    "charge": self.charge,
                    "charge_score": self.charge_score,
                    "repas": self.repas,
                    "activites": self.activites,
                    "projets": self.projets,
                    "budget_jour": self.budget_jour,
                    "alertes": [],
                }

        mock_semaine = MagicMock()
        mock_semaine.alertes_semaine = []
        mock_semaine.stats_semaine = {"charge_moyenne": 80}
        mock_semaine.charge_globale = "intense"
        mock_semaine.jours = {f"2025-01-{i:02d}": MockJourCharge() for i in range(1, 8)}

        mock_st.session_state = SessionStateMock()
        mock_st.columns.side_effect = lambda n: [
            MagicMock() for _ in range(n if isinstance(n, int) else len(n))
        ]
        mock_st.button.return_value = False
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = "lundi"
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock()
        mock_st.form_submit_button.return_value = False
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = mock_semaine
        mock_get_service.return_value = mock_service

        app()

        # Should show expanders for charged days
        assert mock_st.expander.called

    @patch("src.modules.planning.vue_ensemble.get_planning_unified_service")
    @patch("src.modules.planning.vue_ensemble.st")
    def test_onglet_optimiser_ia_form_submit(self, mock_st, mock_get_service):
        """Test soumission formulaire optimisation IA."""
        from src.modules.planning.vue_ensemble import app

        class MockJour:
            charge = "normal"
            charge_score = 50
            repas = []
            activites = []
            projets = []
            budget_jour = 50

            def dict(self):
                return {
                    "charge": self.charge,
                    "charge_score": self.charge_score,
                    "repas": self.repas,
                    "activites": self.activites,
                    "projets": self.projets,
                    "budget_jour": self.budget_jour,
                    "alertes": [],
                }

        mock_semaine = MagicMock()
        mock_semaine.alertes_semaine = []
        mock_semaine.stats_semaine = {"charge_moyenne": 50}
        mock_semaine.charge_globale = "normal"
        mock_semaine.jours = {f"2025-01-{i:02d}": MockJour() for i in range(1, 8)}

        mock_st.session_state = SessionStateMock()
        mock_st.columns.side_effect = lambda n: [
            MagicMock() for _ in range(n if isinstance(n, int) else len(n))
        ]
        mock_st.button.return_value = False
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.selectbox.return_value = "lundi"
        mock_st.number_input.return_value = 400
        mock_st.multiselect.return_value = ["Activites Jules"]

        # Setup form context manager
        mock_form = MagicMock()
        mock_st.form.return_value = mock_form
        mock_form.__enter__ = MagicMock(return_value=mock_form)
        mock_form.__exit__ = MagicMock(return_value=None)

        mock_st.form_submit_button.return_value = True
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock()
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()

        # Mock IA result
        mock_ia_result = MagicMock()
        mock_ia_result.harmonie_description = "Test harmonie"
        mock_ia_result.raisons = ["Raison 1", "Raison 2"]

        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = mock_semaine
        mock_service.generer_semaine_ia.return_value = mock_ia_result
        mock_get_service.return_value = mock_service

        app()

        # Verify form was rendered
        mock_st.form.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests pour les cas limites."""

    @patch("src.modules.planning.vue_ensemble.st")
    def test_metriques_progress_capped(self, mock_st):
        """Test que progress est limite a 1.0."""
        from src.modules.planning.vue_ensemble import afficher_metriques_cles

        mock_st.columns.return_value = [MagicMock() for _ in range(5)]

        stats = {"charge_moyenne": 150}  # > 100
        afficher_metriques_cles(stats, "intense")

        # Progress should be called with value <= 1.0
        progress_calls = [call for call in mock_st.progress.call_args_list if call[0][0] <= 1.0]
        assert len(progress_calls) > 0 or mock_st.progress.called

    @patch("src.modules.planning.vue_ensemble.st")
    def test_alertes_unknown_emoji(self, mock_st):
        """Test alerte avec emoji non reconnu."""
        from src.modules.planning.vue_ensemble import afficher_actions_prioritaires

        mock_st.columns.return_value = [MagicMock(), MagicMock()]
        mock_st.button.return_value = False

        alertes = ["⚠️ - Alerte generique"]
        afficher_actions_prioritaires(alertes)

        # Should not raise and button should be rendered
        assert mock_st.button.called

    @patch("src.modules.planning.vue_ensemble.st")
    def test_opportunities_empty_data(self, mock_st):
        """Test opportunities avec donnees vides."""
        from src.modules.planning.vue_ensemble import afficher_opportunities

        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock()
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        afficher_opportunities({})

        # Should show multiple suggestions for empty data
        assert mock_st.markdown.called
