"""
Tests pour src/ui/components/data.py
Pagination, métriques, export, tableaux
"""

from unittest.mock import MagicMock, patch, call

import pandas as pd
import pytest


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit avec session_state"""
    with patch("src.ui.components.data.st") as mock_st:
        mock_st.session_state = {}

        # Mocks columns
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]

        # Autres mocks
        mock_st.button.return_value = False
        mock_st.selectbox.return_value = 1
        mock_st.caption = MagicMock()
        mock_st.metric = MagicMock()
        mock_st.download_button = MagicMock()
        mock_st.dataframe = MagicMock()
        mock_st.progress = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.info = MagicMock()
        mock_st.rerun = MagicMock()

        yield mock_st


# ═══════════════════════════════════════════════════════════
# TESTS PAGINATION
# ═══════════════════════════════════════════════════════════


class TestPagination:
    """Tests pour pagination()"""

    def test_pagination_few_items_no_pagination(self, mock_streamlit):
        """Test pas de pagination si peu d'items"""
        from src.ui.components.data import pagination

        page, per_page = pagination(total_items=10, items_per_page=20)

        assert page == 1
        assert per_page == 20
        # Pas de colonnes créées car pas de pagination
        mock_streamlit.columns.assert_not_called()

    def test_pagination_many_items(self, mock_streamlit):
        """Test pagination avec beaucoup d'items"""
        from src.ui.components.data import pagination

        page, per_page = pagination(total_items=100, items_per_page=20)

        # Doit créer colonnes pour navigation
        mock_streamlit.columns.assert_called()
        assert per_page == 20

    def test_pagination_initializes_session_state(self, mock_streamlit):
        """Test initialisation session state"""
        from src.ui.components.data import pagination

        pagination(total_items=100, items_per_page=20, key="test")

        assert "test_page" in mock_streamlit.session_state
        assert mock_streamlit.session_state["test_page"] == 1

    def test_pagination_preserves_existing_page(self, mock_streamlit):
        """Test préservation page existante"""
        from src.ui.components.data import pagination

        mock_streamlit.session_state["test_page"] = 3

        pagination(total_items=100, items_per_page=20, key="test")

        # La page existante doit être préservée
        assert mock_streamlit.session_state["test_page"] == 3

    def test_pagination_shows_caption(self, mock_streamlit):
        """Test affichage caption avec infos"""
        from src.ui.components.data import pagination

        pagination(total_items=100, items_per_page=20)

        mock_streamlit.caption.assert_called_once()
        caption_text = mock_streamlit.caption.call_args[0][0]
        assert "100" in caption_text
        assert "Page" in caption_text

    def test_pagination_calculates_total_pages(self, mock_streamlit):
        """Test calcul nombre de pages"""
        from src.ui.components.data import pagination

        # 100 items / 20 par page = 5 pages
        pagination(total_items=100, items_per_page=20)

        caption_text = mock_streamlit.caption.call_args[0][0]
        assert "/5" in caption_text or "5" in caption_text

    def test_pagination_exact_division(self, mock_streamlit):
        """Test division exacte"""
        from src.ui.components.data import pagination

        # 60 items / 20 = exactement 3 pages
        pagination(total_items=60, items_per_page=20)

        caption_text = mock_streamlit.caption.call_args[0][0]
        assert "3" in caption_text


# ═══════════════════════════════════════════════════════════
# TESTS METRICS_ROW
# ═══════════════════════════════════════════════════════════


class TestMetricsRow:
    """Tests pour metrics_row()"""

    def test_metrics_row_empty(self, mock_streamlit):
        """Test ligne vide"""
        from src.ui.components.data import metrics_row

        metrics_row([])

        mock_streamlit.metric.assert_not_called()

    def test_metrics_row_single_stat(self, mock_streamlit):
        """Test une seule métrique"""
        from src.ui.components.data import metrics_row

        stats = [{"label": "Total", "value": 42}]

        metrics_row(stats)

        mock_streamlit.metric.assert_called_once_with(
            label="Total",
            value=42,
            delta=None
        )

    def test_metrics_row_multiple_stats(self, mock_streamlit):
        """Test plusieurs métriques"""
        from src.ui.components.data import metrics_row

        stats = [
            {"label": "Total", "value": 42},
            {"label": "Actifs", "value": 38},
            {"label": "Inactifs", "value": 4},
        ]

        metrics_row(stats)

        assert mock_streamlit.metric.call_count == 3

    def test_metrics_row_with_delta(self, mock_streamlit):
        """Test métrique avec delta"""
        from src.ui.components.data import metrics_row

        stats = [{"label": "Total", "value": 42, "delta": "+5"}]

        metrics_row(stats)

        mock_streamlit.metric.assert_called_with(
            label="Total",
            value=42,
            delta="+5"
        )

    def test_metrics_row_custom_cols(self, mock_streamlit):
        """Test nombre de colonnes personnalisé"""
        from src.ui.components.data import metrics_row

        stats = [{"label": "A", "value": 1}, {"label": "B", "value": 2}]

        metrics_row(stats, cols=4)

        mock_streamlit.columns.assert_called_with(4)

    def test_metrics_row_auto_cols(self, mock_streamlit):
        """Test colonnes automatiques"""
        from src.ui.components.data import metrics_row

        stats = [{"label": "A", "value": 1}, {"label": "B", "value": 2}]

        metrics_row(stats)

        # Doit utiliser len(stats) = 2 colonnes
        mock_streamlit.columns.assert_called_with(2)


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT_BUTTONS
# ═══════════════════════════════════════════════════════════


class TestExportButtons:
    """Tests pour export_buttons()"""

    def test_export_buttons_list_data(self, mock_streamlit):
        """Test export avec liste"""
        from src.ui.components.data import export_buttons

        data = [{"nom": "Test1"}, {"nom": "Test2"}]

        export_buttons(data, "export_test")

        # Doit appeler download_button
        mock_streamlit.download_button.assert_called()

    def test_export_buttons_dataframe_data(self, mock_streamlit):
        """Test export avec DataFrame"""
        from src.ui.components.data import export_buttons

        df = pd.DataFrame([{"nom": "Test1"}, {"nom": "Test2"}])

        export_buttons(df, "export_test")

        mock_streamlit.download_button.assert_called()

    def test_export_buttons_csv_format(self, mock_streamlit):
        """Test format CSV"""
        from src.ui.components.data import export_buttons

        data = [{"nom": "Test"}]

        export_buttons(data, "test", formats=["csv"])

        call_args = mock_streamlit.download_button.call_args_list
        # Vérifier qu'un bouton CSV existe
        csv_calls = [c for c in call_args if ".csv" in str(c)]
        assert len(csv_calls) >= 1

    def test_export_buttons_json_format(self, mock_streamlit):
        """Test format JSON"""
        from src.ui.components.data import export_buttons

        data = [{"nom": "Test"}]

        export_buttons(data, "test", formats=["json"])

        call_args = mock_streamlit.download_button.call_args_list
        json_calls = [c for c in call_args if ".json" in str(c)]
        assert len(json_calls) >= 1

    def test_export_buttons_both_formats(self, mock_streamlit):
        """Test les deux formats"""
        from src.ui.components.data import export_buttons

        data = [{"nom": "Test"}]

        export_buttons(data, "test", formats=["csv", "json"])

        assert mock_streamlit.download_button.call_count == 2

    def test_export_buttons_custom_filename(self, mock_streamlit):
        """Test nom de fichier personnalisé"""
        from src.ui.components.data import export_buttons

        data = [{"nom": "Test"}]

        export_buttons(data, "mes_recettes", formats=["csv"])

        call_args = mock_streamlit.download_button.call_args
        assert "mes_recettes.csv" in call_args[0] or "mes_recettes.csv" in str(call_args)


# ═══════════════════════════════════════════════════════════
# TESTS DATA_TABLE
# ═══════════════════════════════════════════════════════════


class TestDataTable:
    """Tests pour data_table()"""

    def test_data_table_list_data(self, mock_streamlit):
        """Test tableau avec liste"""
        from src.ui.components.data import data_table

        data = [{"nom": "Test1"}, {"nom": "Test2"}]

        data_table(data)

        mock_streamlit.dataframe.assert_called_once()

    def test_data_table_dataframe_data(self, mock_streamlit):
        """Test tableau avec DataFrame"""
        from src.ui.components.data import data_table

        df = pd.DataFrame([{"nom": "Test1"}, {"nom": "Test2"}])

        data_table(df)

        mock_streamlit.dataframe.assert_called_once()

    def test_data_table_custom_key(self, mock_streamlit):
        """Test clé personnalisée"""
        from src.ui.components.data import data_table

        data_table([{"a": 1}], key="my_table")

        call_kwargs = mock_streamlit.dataframe.call_args[1]
        assert call_kwargs["key"] == "my_table"

    def test_data_table_use_container_width(self, mock_streamlit):
        """Test largeur container"""
        from src.ui.components.data import data_table

        data_table([{"a": 1}])

        call_kwargs = mock_streamlit.dataframe.call_args[1]
        assert call_kwargs["use_container_width"] is True


# ═══════════════════════════════════════════════════════════
# TESTS PROGRESS_BAR
# ═══════════════════════════════════════════════════════════


class TestProgressBar:
    """Tests pour progress_bar()"""

    def test_progress_bar_basic(self, mock_streamlit):
        """Test barre de progression basique"""
        from src.ui.components.data import progress_bar

        progress_bar(0.5)

        mock_streamlit.progress.assert_called_once()

    def test_progress_bar_with_label(self, mock_streamlit):
        """Test avec label"""
        from src.ui.components.data import progress_bar

        progress_bar(0.75, label="Progression")

        mock_streamlit.markdown.assert_called_once()
        assert "Progression" in mock_streamlit.markdown.call_args[0][0]

    def test_progress_bar_without_label(self, mock_streamlit):
        """Test sans label"""
        from src.ui.components.data import progress_bar

        progress_bar(0.5, label="")

        mock_streamlit.markdown.assert_not_called()

    def test_progress_bar_zero(self, mock_streamlit):
        """Test valeur zéro"""
        from src.ui.components.data import progress_bar

        progress_bar(0.0)

        mock_streamlit.progress.assert_called()

    def test_progress_bar_full(self, mock_streamlit):
        """Test valeur maximale"""
        from src.ui.components.data import progress_bar

        progress_bar(1.0)

        mock_streamlit.progress.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS STATUS_INDICATOR
# ═══════════════════════════════════════════════════════════


class TestStatusIndicator:
    """Tests pour status_indicator()"""

    def test_status_indicator_success(self, mock_streamlit):
        """Test indicateur succès"""
        from src.ui.components.data import status_indicator

        status_indicator("success", "Connecté")

        mock_streamlit.markdown.assert_called_once()
        html = mock_streamlit.markdown.call_args[0][0]
        assert "#4CAF50" in html  # Couleur verte
        assert "Connecté" in html

    def test_status_indicator_warning(self, mock_streamlit):
        """Test indicateur warning"""
        from src.ui.components.data import status_indicator

        status_indicator("warning", "En attente")

        html = mock_streamlit.markdown.call_args[0][0]
        assert "#FFC107" in html  # Couleur jaune

    def test_status_indicator_error(self, mock_streamlit):
        """Test indicateur erreur"""
        from src.ui.components.data import status_indicator

        status_indicator("error", "Déconnecté")

        html = mock_streamlit.markdown.call_args[0][0]
        assert "#f44336" in html  # Couleur rouge

    def test_status_indicator_info(self, mock_streamlit):
        """Test indicateur info"""
        from src.ui.components.data import status_indicator

        status_indicator("info", "Information")

        html = mock_streamlit.markdown.call_args[0][0]
        assert "#2196F3" in html  # Couleur bleue

    def test_status_indicator_unknown_status(self, mock_streamlit):
        """Test statut inconnu"""
        from src.ui.components.data import status_indicator

        status_indicator("unknown", "Test")

        # Doit quand même afficher
        mock_streamlit.markdown.assert_called_once()

    def test_status_indicator_unsafe_html(self, mock_streamlit):
        """Test HTML non sécurisé activé"""
        from src.ui.components.data import status_indicator

        status_indicator("success")

        call_kwargs = mock_streamlit.markdown.call_args[1]
        assert call_kwargs["unsafe_allow_html"] is True

    def test_status_indicator_no_label(self, mock_streamlit):
        """Test sans label"""
        from src.ui.components.data import status_indicator

        status_indicator("success", "")

        mock_streamlit.markdown.assert_called_once()
