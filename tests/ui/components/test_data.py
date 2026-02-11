"""
Tests complets pour src/ui/components/data.py
Couverture cible: >80%
"""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd


# ═══════════════════════════════════════════════════════════
# PAGINATION
# ═══════════════════════════════════════════════════════════


class TestPagination:
    """Tests pour pagination()."""

    def test_pagination_import(self):
        """Test import réussi."""
        from src.ui.components.data import pagination
        assert callable(pagination)

    def test_pagination_small_dataset(self):
        """Test pagination avec petit dataset (pas de pagination nécessaire)."""
        from src.ui.components.data import pagination
        
        # Moins d'items que par page -> retourne page 1
        result = pagination(10, items_per_page=20)
        assert result == (1, 20)

    def test_pagination_exact_page(self):
        """Test pagination avec nombre exact d'items par page."""
        from src.ui.components.data import pagination
        
        result = pagination(20, items_per_page=20)
        assert result == (1, 20)

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    @patch("streamlit.button", return_value=False)
    @patch("streamlit.selectbox", return_value=1)
    @patch("streamlit.caption")
    def test_pagination_multiple_pages(self, mock_caption, mock_select, mock_btn, mock_cols):
        """Test pagination avec plusieurs pages."""
        from src.ui.components.data import pagination
        
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        page, per_page = pagination(100, items_per_page=20, key="test_pag")
        
        assert per_page == 20
        assert mock_cols.called
        assert mock_caption.called

    @patch("streamlit.session_state", {"test_page": 2})
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.selectbox", return_value=2)
    @patch("streamlit.caption")
    def test_pagination_with_existing_state(self, mock_caption, mock_select, mock_btn, mock_cols):
        """Test pagination avec état existant."""
        from src.ui.components.data import pagination
        
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_btn.return_value = False
        
        page, per_page = pagination(100, items_per_page=20, key="test")
        assert per_page == 20

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.selectbox", return_value=1)
    @patch("streamlit.caption")
    @patch("streamlit.rerun")
    def test_pagination_prev_button(self, mock_rerun, mock_caption, mock_select, mock_btn, mock_cols):
        """Test clic sur bouton précédent."""
        from src.ui.components.data import pagination
        
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        # Premier appel (prev) = True, deuxième (next) = False
        mock_btn.side_effect = [True, False]
        
        try:
            pagination(100, items_per_page=20, key="test_prev")
        except Exception:
            pass  # rerun arrête l'exécution

    @patch("streamlit.session_state", {})
    @patch("streamlit.columns")
    @patch("streamlit.button")
    @patch("streamlit.selectbox", return_value=1)
    @patch("streamlit.caption")
    @patch("streamlit.rerun")
    def test_pagination_next_button(self, mock_rerun, mock_caption, mock_select, mock_btn, mock_cols):
        """Test clic sur bouton suivant."""
        from src.ui.components.data import pagination
        
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock()]
        # Premier appel (prev) = False, deuxième (next) = True
        mock_btn.side_effect = [False, True]
        
        try:
            pagination(100, items_per_page=20, key="test_next")
        except Exception:
            pass  # rerun arrête l'exécution


# ═══════════════════════════════════════════════════════════
# LIGNE_METRIQUES (metrics_row)
# ═══════════════════════════════════════════════════════════


class TestLigneMetriques:
    """Tests pour ligne_metriques()."""

    def test_ligne_metriques_import(self):
        """Test import réussi."""
        from src.ui.components.data import ligne_metriques
        assert callable(ligne_metriques)

    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_ligne_metriques_basic(self, mock_metric, mock_cols):
        """Test avec stats de base."""
        from src.ui.components.data import ligne_metriques
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        stats = [
            {"label": "Total", "value": 42},
            {"label": "Actifs", "value": 38}
        ]
        
        ligne_metriques(stats)
        
        assert mock_cols.called
        assert mock_metric.called

    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_ligne_metriques_with_delta(self, mock_metric, mock_cols):
        """Test avec delta."""
        from src.ui.components.data import ligne_metriques
        
        mock_cols.return_value = [MagicMock()]
        
        stats = [{"label": "Total", "value": 100, "delta": "+10"}]
        
        ligne_metriques(stats)
        
        assert mock_metric.called

    def test_ligne_metriques_empty(self):
        """Test avec liste vide."""
        from src.ui.components.data import ligne_metriques
        
        # Ne doit pas lever d'erreur
        result = ligne_metriques([])
        assert result is None

    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_ligne_metriques_custom_cols(self, mock_metric, mock_cols):
        """Test avec nombre de colonnes personnalisé."""
        from src.ui.components.data import ligne_metriques
        
        mock_cols.return_value = [MagicMock(), MagicMock(), MagicMock(), MagicMock()]
        
        stats = [{"label": "A", "value": 1}, {"label": "B", "value": 2}]
        
        ligne_metriques(stats, cols=4)
        
        mock_cols.assert_called_with(4)

    @patch("streamlit.columns")
    @patch("streamlit.metric")
    def test_ligne_metriques_more_stats_than_cols(self, mock_metric, mock_cols):
        """Test avec plus de stats que de colonnes."""
        from src.ui.components.data import ligne_metriques
        
        # Seulement 2 colonnes retournées
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        stats = [
            {"label": "A", "value": 1},
            {"label": "B", "value": 2},
            {"label": "C", "value": 3}  # Sera ignoré
        ]
        
        ligne_metriques(stats, cols=2)
        
        # Seulement 2 appels à metric (pas 3)
        assert mock_metric.call_count == 2


# ═══════════════════════════════════════════════════════════
# BOUTONS_EXPORT (export_buttons)
# ═══════════════════════════════════════════════════════════


class TestBoutonsExport:
    """Tests pour boutons_export()."""

    def test_boutons_export_import(self):
        """Test import réussi."""
        from src.ui.components.data import boutons_export
        assert callable(boutons_export)

    @patch("streamlit.columns")
    @patch("streamlit.download_button")
    def test_boutons_export_list_data(self, mock_download, mock_cols):
        """Test export avec liste."""
        from src.ui.components.data import boutons_export
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        data = [{"id": 1, "nom": "Test"}, {"id": 2, "nom": "Test2"}]
        
        boutons_export(data, "export_test", ["csv", "json"], "test_key")
        
        assert mock_cols.called
        assert mock_download.call_count == 2  # CSV + JSON

    @patch("streamlit.columns")
    @patch("streamlit.download_button")
    def test_boutons_export_dataframe(self, mock_download, mock_cols):
        """Test export avec DataFrame."""
        from src.ui.components.data import boutons_export
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        df = pd.DataFrame([{"id": 1, "nom": "Test"}])
        
        boutons_export(df, "export_df", ["csv", "json"], "df_key")
        
        assert mock_download.call_count == 2

    @patch("streamlit.columns")
    @patch("streamlit.download_button")
    def test_boutons_export_csv_only(self, mock_download, mock_cols):
        """Test export CSV seulement."""
        from src.ui.components.data import boutons_export
        
        mock_cols.return_value = [MagicMock()]
        
        data = [{"id": 1}]
        
        boutons_export(data, "csv_export", ["csv"], "csv_key")
        
        assert mock_download.call_count == 1

    @patch("streamlit.columns")
    @patch("streamlit.download_button")
    def test_boutons_export_json_only(self, mock_download, mock_cols):
        """Test export JSON seulement."""
        from src.ui.components.data import boutons_export
        
        mock_cols.return_value = [MagicMock()]
        
        data = [{"id": 1}]
        
        boutons_export(data, "json_export", ["json"], "json_key")
        
        assert mock_download.call_count == 1

    @patch("streamlit.columns")
    @patch("streamlit.download_button")
    def test_boutons_export_default_formats(self, mock_download, mock_cols):
        """Test formats par défaut (csv + json)."""
        from src.ui.components.data import boutons_export
        
        mock_cols.return_value = [MagicMock(), MagicMock()]
        
        data = [{"id": 1}]
        
        # Pas de formats spécifiés -> csv + json par défaut
        boutons_export(data, "default_export", cle="default_key")
        
        assert mock_download.call_count == 2


# ═══════════════════════════════════════════════════════════
# TABLEAU_DONNEES (data_table)
# ═══════════════════════════════════════════════════════════


class TestTableauDonnees:
    """Tests pour tableau_donnees()."""

    def test_tableau_donnees_import(self):
        """Test import réussi."""
        from src.ui.components.data import tableau_donnees
        assert callable(tableau_donnees)

    @patch("streamlit.dataframe")
    def test_tableau_donnees_list(self, mock_dataframe):
        """Test avec liste."""
        from src.ui.components.data import tableau_donnees
        
        data = [{"id": 1, "nom": "Test"}, {"id": 2, "nom": "Test2"}]
        
        tableau_donnees(data, "list_table")
        
        assert mock_dataframe.called

    @patch("streamlit.dataframe")
    def test_tableau_donnees_dataframe(self, mock_dataframe):
        """Test avec DataFrame."""
        from src.ui.components.data import tableau_donnees
        
        df = pd.DataFrame([{"id": 1, "nom": "Test"}])
        
        tableau_donnees(df, "df_table")
        
        mock_dataframe.assert_called_once()

    @patch("streamlit.dataframe")
    def test_tableau_donnees_uses_container_width(self, mock_dataframe):
        """Test que use_container_width=True est passé."""
        from src.ui.components.data import tableau_donnees
        
        data = [{"id": 1}]
        
        tableau_donnees(data, "width_test")
        
        # Vérifie que use_container_width=True est passé
        call_kwargs = mock_dataframe.call_args[1]
        assert call_kwargs.get("use_container_width") is True


# ═══════════════════════════════════════════════════════════
# BARRE_PROGRESSION (progress_bar)
# ═══════════════════════════════════════════════════════════


class TestBarreProgression:
    """Tests pour barre_progression()."""

    def test_barre_progression_import(self):
        """Test import réussi."""
        from src.ui.components.data import barre_progression
        assert callable(barre_progression)

    @patch("streamlit.progress")
    @patch("streamlit.markdown")
    def test_barre_progression_with_label(self, mock_markdown, mock_progress):
        """Test avec label."""
        from src.ui.components.data import barre_progression
        
        barre_progression(0.75, "Progression", "prog_key")
        
        mock_markdown.assert_called_with("**Progression**")
        mock_progress.assert_called_with(0.75, key="prog_key")

    @patch("streamlit.progress")
    @patch("streamlit.markdown")
    def test_barre_progression_without_label(self, mock_markdown, mock_progress):
        """Test sans label."""
        from src.ui.components.data import barre_progression
        
        barre_progression(0.5, cle="no_label")
        
        # markdown ne doit pas être appelé pour un label vide
        mock_markdown.assert_not_called()
        mock_progress.assert_called_once()

    @patch("streamlit.progress")
    def test_barre_progression_zero(self, mock_progress):
        """Test valeur 0."""
        from src.ui.components.data import barre_progression
        
        barre_progression(0.0, cle="zero")
        
        mock_progress.assert_called_with(0.0, key="zero")

    @patch("streamlit.progress")
    def test_barre_progression_full(self, mock_progress):
        """Test valeur 1.0 (100%)."""
        from src.ui.components.data import barre_progression
        
        barre_progression(1.0, cle="full")
        
        mock_progress.assert_called_with(1.0, key="full")


# ═══════════════════════════════════════════════════════════
# INDICATEUR_STATUT (status_indicator)
# ═══════════════════════════════════════════════════════════


class TestIndicateurStatut:
    """Tests pour indicateur_statut()."""

    def test_indicateur_statut_import(self):
        """Test import réussi."""
        from src.ui.components.data import indicateur_statut
        assert callable(indicateur_statut)

    @patch("streamlit.markdown")
    def test_indicateur_statut_success(self, mock_markdown):
        """Test statut success."""
        from src.ui.components.data import indicateur_statut
        
        indicateur_statut("success", "Connecté")
        
        # Vérifie que markdown est appelé avec couleur verte
        call_args = mock_markdown.call_args[0][0]
        assert "#4CAF50" in call_args
        assert "Connecté" in call_args

    @patch("streamlit.markdown")
    def test_indicateur_statut_warning(self, mock_markdown):
        """Test statut warning."""
        from src.ui.components.data import indicateur_statut
        
        indicateur_statut("warning", "Attention")
        
        call_args = mock_markdown.call_args[0][0]
        assert "#FFC107" in call_args

    @patch("streamlit.markdown")
    def test_indicateur_statut_error(self, mock_markdown):
        """Test statut error."""
        from src.ui.components.data import indicateur_statut
        
        indicateur_statut("error", "Erreur")
        
        call_args = mock_markdown.call_args[0][0]
        assert "#f44336" in call_args

    @patch("streamlit.markdown")
    def test_indicateur_statut_info(self, mock_markdown):
        """Test statut info."""
        from src.ui.components.data import indicateur_statut
        
        indicateur_statut("info", "Information")
        
        call_args = mock_markdown.call_args[0][0]
        assert "#2196F3" in call_args

    @patch("streamlit.markdown")
    def test_indicateur_statut_unknown(self, mock_markdown):
        """Test statut inconnu (fallback gris)."""
        from src.ui.components.data import indicateur_statut
        
        indicateur_statut("unknown", "Inconnu")
        
        call_args = mock_markdown.call_args[0][0]
        # Fallback couleur grise
        assert "#gray" in call_args or "gray" in call_args

    @patch("streamlit.markdown")
    def test_indicateur_statut_empty_label(self, mock_markdown):
        """Test sans label."""
        from src.ui.components.data import indicateur_statut
        
        indicateur_statut("success")
        
        assert mock_markdown.called


# ═══════════════════════════════════════════════════════════
# TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestDataIntegration:
    """Tests d'intégration pour le module data."""

    def test_all_functions_exported(self):
        """Test que toutes les fonctions sont exportées."""
        from src.ui.components import data
        
        assert hasattr(data, "pagination")
        assert hasattr(data, "ligne_metriques")
        assert hasattr(data, "boutons_export")
        assert hasattr(data, "tableau_donnees")
        assert hasattr(data, "barre_progression")
        assert hasattr(data, "indicateur_statut")

    def test_imports_from_components(self):
        """Test imports depuis components."""
        from src.ui.components import (
            pagination,
            ligne_metriques,
            boutons_export,
            tableau_donnees,
            barre_progression,
            indicateur_statut,
        )
        
        assert callable(pagination)
        assert callable(ligne_metriques)
        assert callable(boutons_export)
        assert callable(tableau_donnees)
        assert callable(barre_progression)
        assert callable(indicateur_statut)

    def test_imports_from_ui(self):
        """Test imports depuis ui."""
        from src.ui import (
            pagination,
            ligne_metriques,
            boutons_export,
            tableau_donnees,
            barre_progression,
            indicateur_statut,
        )
        
        assert callable(pagination)
        assert callable(ligne_metriques)
        assert callable(boutons_export)
        assert callable(tableau_donnees)
        assert callable(barre_progression)
        assert callable(indicateur_statut)
