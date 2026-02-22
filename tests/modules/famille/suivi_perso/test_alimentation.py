"""
Tests pour src/modules/famille/suivi_perso/alimentation.py

Tests complets pour afficher_food_log et afficher_food_form.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestRenderFoodLog:
    """Tests pour afficher_food_log()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit complet"""
        with patch("src.modules.famille.suivi_perso.alimentation.st") as mock:
            # Mock tabs
            mock_tab1 = MagicMock()
            mock_tab2 = MagicMock()
            mock.tabs.return_value = [mock_tab1, mock_tab2]
            mock_tab1.__enter__ = MagicMock(return_value=mock_tab1)
            mock_tab1.__exit__ = MagicMock(return_value=False)
            mock_tab2.__enter__ = MagicMock(return_value=mock_tab2)
            mock_tab2.__exit__ = MagicMock(return_value=False)
            yield mock

    @pytest.fixture
    def mock_get_food_logs(self):
        """Mock get_food_logs_today"""
        with patch("src.modules.famille.suivi_perso.alimentation.get_food_logs_today") as mock:
            yield mock

    @pytest.fixture
    def mock_render_form(self):
        """Mock afficher_food_form"""
        with patch("src.modules.famille.suivi_perso.alimentation.afficher_food_form") as mock:
            yield mock

    def test_affiche_subheader(self, mock_st, mock_get_food_logs, mock_render_form):
        """Vérifie l'affichage du titre"""
        mock_get_food_logs.return_value = []

        from src.modules.famille.suivi_perso.alimentation import afficher_food_log

        afficher_food_log("anne")

        mock_st.subheader.assert_called_once()
        assert "Alimentation" in mock_st.subheader.call_args[0][0]

    def test_cree_deux_onglets(self, mock_st, mock_get_food_logs, mock_render_form):
        """Vérifie la création des onglets"""
        mock_get_food_logs.return_value = []

        from src.modules.famille.suivi_perso.alimentation import afficher_food_log

        afficher_food_log("anne")

        mock_st.tabs.assert_called_once()
        tabs_arg = mock_st.tabs.call_args[0][0]
        assert len(tabs_arg) == 2
        assert "Aujourd'hui" in tabs_arg[0]
        assert "Ajouter" in tabs_arg[1]

    def test_affiche_message_si_pas_de_logs(self, mock_st, mock_get_food_logs, mock_render_form):
        """Vérifie le message sans logs"""
        mock_get_food_logs.return_value = []

        from src.modules.famille.suivi_perso.alimentation import afficher_food_log

        afficher_food_log("anne")

        mock_st.caption.assert_called()

    def test_calcule_total_calories(self, mock_st, mock_get_food_logs, mock_render_form):
        """Vérifie le calcul du total calories"""
        mock_log1 = MagicMock()
        mock_log1.calories_estimees = 500
        mock_log1.repas = "dejeuner"
        mock_log1.description = "Salade"
        mock_log1.qualite = 4

        mock_log2 = MagicMock()
        mock_log2.calories_estimees = 300
        mock_log2.repas = "snack"
        mock_log2.description = "Pomme"
        mock_log2.qualite = 5

        mock_get_food_logs.return_value = [mock_log1, mock_log2]

        # Mock container pour les logs
        mock_container = MagicMock()
        mock_st.container.return_value.__enter__ = MagicMock(return_value=mock_container)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        from src.modules.famille.suivi_perso.alimentation import afficher_food_log

        afficher_food_log("anne")

        # Vérifie que metric est appelé avec le total
        mock_st.metric.assert_called()
        call_args = mock_st.metric.call_args_list[0]
        assert "800" in str(call_args)  # 500 + 300

    def test_gere_calories_none(self, mock_st, mock_get_food_logs, mock_render_form):
        """Vérifie la gestion des calories None"""
        mock_log = MagicMock()
        mock_log.calories_estimees = None
        mock_log.repas = "dejeuner"
        mock_log.description = "Test"
        mock_log.qualite = None

        mock_get_food_logs.return_value = [mock_log]

        mock_st.container.return_value.__enter__ = MagicMock()
        mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        from src.modules.famille.suivi_perso.alimentation import afficher_food_log

        # Ne doit pas lever d'exception
        afficher_food_log("anne")

    def test_formate_emojis_par_type_repas(self, mock_st, mock_get_food_logs, mock_render_form):
        """Vérifie les emojis par type de repas"""
        types_repas = ["petit_dejeuner", "dejeuner", "diner", "snack"]

        for repas in types_repas:
            mock_log = MagicMock()
            mock_log.calories_estimees = 100
            mock_log.repas = repas
            mock_log.description = "Test"
            mock_log.qualite = 3

            mock_get_food_logs.return_value = [mock_log]

            mock_st.container.return_value.__enter__ = MagicMock()
            mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
            mock_st.columns.return_value = [MagicMock(), MagicMock()]

            from src.modules.famille.suivi_perso.alimentation import afficher_food_log

            afficher_food_log("anne")

            # Vérifie que markdown a été appelé
            assert mock_st.markdown.called


class TestRenderFoodForm:
    """Tests pour afficher_food_form()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit pour formulaire"""
        with patch("src.modules.famille.suivi_perso.alimentation.st") as mock:
            # Mock form context
            mock_form = MagicMock()
            mock.form.return_value.__enter__ = MagicMock(return_value=mock_form)
            mock.form.return_value.__exit__ = MagicMock(return_value=False)
            mock.columns.return_value = [MagicMock(), MagicMock()]
            yield mock

    @pytest.fixture
    def mock_db(self):
        """Mock service suivi_perso"""
        with patch("src.services.famille.suivi_perso.obtenir_service_suivi_perso") as mock_factory:
            mock_service = MagicMock()
            mock_factory.return_value = mock_service
            yield mock_service, mock_factory

    @pytest.fixture
    def mock_get_user(self):
        """Mock get_or_create_user - no longer used by alimentation.py"""
        yield MagicMock()

    def test_cree_formulaire(self, mock_st, mock_db):
        """Vérifie la création du formulaire"""
        mock_st.form_submit_button.return_value = False

        from src.modules.famille.suivi_perso.alimentation import afficher_food_form

        afficher_food_form("anne")

        mock_st.form.assert_called_once_with("add_food")

    def test_affiche_champs_formulaire(self, mock_st, mock_db):
        """Vérifie les champs du formulaire"""
        mock_st.form_submit_button.return_value = False

        from src.modules.famille.suivi_perso.alimentation import afficher_food_form

        afficher_food_form("anne")

        mock_st.selectbox.assert_called()
        mock_st.text_area.assert_called()
        mock_st.number_input.assert_called()
        mock_st.slider.assert_called()
        mock_st.text_input.assert_called()

    def test_erreur_si_description_vide(self, mock_st, mock_db):
        """Vérifie l'erreur si description manquante"""
        mock_st.form_submit_button.return_value = True
        mock_st.text_area.return_value = ""

        from src.modules.famille.suivi_perso.alimentation import afficher_food_form

        afficher_food_form("anne")

        mock_st.error.assert_called()

    def test_enregistre_log_valide(self, mock_st, mock_db, mock_get_user):
        """Vérifie l'enregistrement d'un log valide"""
        mock_service, _ = mock_db
        mock_st.form_submit_button.return_value = True
        mock_st.selectbox.return_value = ("dejeuner", "🌞 Dejeuner")
        mock_st.text_area.return_value = "Poulet grillé"
        mock_st.number_input.return_value = 450
        mock_st.slider.return_value = 4
        mock_st.text_input.return_value = "Note test"

        from src.modules.famille.suivi_perso.alimentation import afficher_food_form

        afficher_food_form("anne")

        mock_service.ajouter_food_log.assert_called_once()
        mock_st.success.assert_called()

    def test_gere_exception_db(self, mock_st, mock_db):
        """Vérifie la gestion d'erreur DB"""
        mock_service, mock_factory = mock_db
        mock_st.form_submit_button.return_value = True
        mock_st.selectbox.return_value = ("dejeuner", "🌞 Dejeuner")
        mock_st.text_area.return_value = "Test"
        mock_st.number_input.return_value = 100
        mock_st.slider.return_value = 3
        mock_st.text_input.return_value = ""
        mock_service.ajouter_food_log.side_effect = Exception("DB Error")

        from src.modules.famille.suivi_perso.alimentation import afficher_food_form

        afficher_food_form("anne")

        mock_st.error.assert_called()


class TestAlimentationIntegration:
    """Tests d'intégration pour le module alimentation"""

    def test_import_render_food_log(self):
        """Vérifie que afficher_food_log est importable"""
        from src.modules.famille.suivi_perso.alimentation import afficher_food_log

        assert callable(afficher_food_log)

    def test_import_render_food_form(self):
        """Vérifie que afficher_food_form est importable"""
        from src.modules.famille.suivi_perso.alimentation import afficher_food_form

        assert callable(afficher_food_form)
