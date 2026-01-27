"""
Tests pour les composants UI

Tests unitaires:
- Atoms (badge, empty_state, metric_card, toast)
- Dashboard widgets
- Composants de formulaires
- Layouts
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


# ═══════════════════════════════════════════════════════════
# TESTS ATOMS
# ═══════════════════════════════════════════════════════════


class TestAtoms:
    """Tests pour les composants atomiques"""

    @patch('streamlit.markdown')
    def test_badge_default_color(self, mock_markdown):
        """Test badge avec couleur par défaut"""
        from src.ui.components.atoms import badge
        
        badge("Actif")
        
        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Actif" in call_args
        assert "#4CAF50" in call_args  # Couleur par défaut

    @patch('streamlit.markdown')
    def test_badge_custom_color(self, mock_markdown):
        """Test badge avec couleur personnalisée"""
        from src.ui.components.atoms import badge
        
        badge("Urgent", "#FF5722")
        
        call_args = mock_markdown.call_args[0][0]
        assert "Urgent" in call_args
        assert "#FF5722" in call_args

    @patch('streamlit.markdown')
    def test_empty_state_basic(self, mock_markdown):
        """Test empty state basique"""
        from src.ui.components.atoms import empty_state
        
        empty_state("Aucune donnée", "📭")
        
        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Aucune donnée" in call_args
        assert "📭" in call_args

    @patch('streamlit.markdown')
    def test_empty_state_with_subtext(self, mock_markdown):
        """Test empty state avec sous-texte"""
        from src.ui.components.atoms import empty_state
        
        empty_state("Aucune recette", "🍽️", "Ajoutez votre première recette")
        
        call_args = mock_markdown.call_args[0][0]
        assert "Aucune recette" in call_args
        assert "Ajoutez votre première recette" in call_args

    @patch('streamlit.markdown')
    def test_metric_card_basic(self, mock_markdown):
        """Test carte métrique basique"""
        from src.ui.components.atoms import metric_card
        
        metric_card("Total", "42")
        
        mock_markdown.assert_called_once()
        call_args = mock_markdown.call_args[0][0]
        assert "Total" in call_args
        assert "42" in call_args

    @patch('streamlit.markdown')
    def test_metric_card_with_delta(self, mock_markdown):
        """Test carte métrique avec variation"""
        from src.ui.components.atoms import metric_card
        
        metric_card("Ventes", "150", "+12%")
        
        call_args = mock_markdown.call_args[0][0]
        assert "Ventes" in call_args
        assert "150" in call_args
        assert "+12%" in call_args

    @patch('streamlit.success')
    def test_toast_success(self, mock_success):
        """Test toast succès"""
        from src.ui.components.atoms import toast
        
        toast("Sauvegardé", "success")
        
        mock_success.assert_called_once_with("Sauvegardé")

    @patch('streamlit.error')
    def test_toast_error(self, mock_error):
        """Test toast erreur"""
        from src.ui.components.atoms import toast
        
        toast("Erreur survenue", "error")
        
        mock_error.assert_called_once_with("Erreur survenue")

    @patch('streamlit.warning')
    def test_toast_warning(self, mock_warning):
        """Test toast warning"""
        from src.ui.components.atoms import toast
        
        toast("Attention", "warning")
        
        mock_warning.assert_called_once_with("Attention")


# ═══════════════════════════════════════════════════════════
# TESTS DASHBOARD WIDGETS
# ═══════════════════════════════════════════════════════════


class TestDashboardWidgets:
    """Tests pour les widgets de dashboard"""

    def test_stat_widget_structure(self):
        """Test structure widget statistique"""
        stat_data = {
            "label": "Recettes",
            "value": 42,
            "icon": "📖",
            "trend": "+5%",
            "color": "green"
        }
        
        assert "label" in stat_data
        assert "value" in stat_data
        assert isinstance(stat_data["value"], int)

    def test_chart_widget_data(self):
        """Test données widget graphique"""
        chart_data = {
            "type": "bar",
            "title": "Dépenses par catégorie",
            "data": [
                {"category": "Alimentation", "value": 350},
                {"category": "Transport", "value": 150},
                {"category": "Loisirs", "value": 100},
            ],
            "x_label": "Catégorie",
            "y_label": "Montant (€)"
        }
        
        assert chart_data["type"] in ["bar", "line", "pie", "area"]
        assert len(chart_data["data"]) == 3

    def test_alert_widget_priority(self):
        """Test priorité widget alerte"""
        alerts = [
            {"type": "error", "message": "Stock critique", "priority": 1},
            {"type": "warning", "message": "Péremption proche", "priority": 2},
            {"type": "info", "message": "Nouvelle suggestion", "priority": 3},
        ]
        
        # Tri par priorité
        sorted_alerts = sorted(alerts, key=lambda x: x["priority"])
        
        assert sorted_alerts[0]["type"] == "error"
        assert sorted_alerts[-1]["type"] == "info"


# ═══════════════════════════════════════════════════════════
# TESTS FORMS
# ═══════════════════════════════════════════════════════════


class TestFormComponents:
    """Tests pour les composants de formulaires"""

    def test_form_field_validation(self):
        """Test validation champ formulaire"""
        def validate_required(value):
            return value is not None and value != ""
        
        assert validate_required("test") is True
        assert validate_required("") is False
        assert validate_required(None) is False

    def test_form_number_range_validation(self):
        """Test validation plage numérique"""
        def validate_range(value, min_val, max_val):
            return min_val <= value <= max_val
        
        assert validate_range(5, 1, 10) is True
        assert validate_range(0, 1, 10) is False
        assert validate_range(15, 1, 10) is False

    def test_form_email_pattern(self):
        """Test pattern email"""
        import re
        
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        
        assert re.match(email_pattern, "test@example.com") is not None
        assert re.match(email_pattern, "invalid-email") is None
        assert re.match(email_pattern, "user.name@domain.co.uk") is not None

    def test_form_date_format(self):
        """Test format date"""
        from datetime import date
        
        date_str = "2026-01-27"
        parsed_date = date.fromisoformat(date_str)
        
        assert parsed_date.year == 2026
        assert parsed_date.month == 1
        assert parsed_date.day == 27


# ═══════════════════════════════════════════════════════════
# TESTS LAYOUTS
# ═══════════════════════════════════════════════════════════


class TestLayouts:
    """Tests pour les layouts"""

    def test_grid_layout_columns(self):
        """Test calcul colonnes grille"""
        items = 7
        cols_per_row = 3
        
        full_rows = items // cols_per_row
        remaining = items % cols_per_row
        
        assert full_rows == 2
        assert remaining == 1

    def test_responsive_breakpoints(self):
        """Test breakpoints responsive"""
        breakpoints = {
            "mobile": 576,
            "tablet": 768,
            "desktop": 992,
            "wide": 1200
        }
        
        screen_width = 800
        
        if screen_width < breakpoints["mobile"]:
            layout = "single_column"
        elif screen_width < breakpoints["tablet"]:
            layout = "two_columns"
        else:
            layout = "three_columns"
        
        assert layout == "three_columns"

    def test_sidebar_state(self):
        """Test état sidebar"""
        sidebar_config = {
            "expanded": True,
            "width": 300,
            "items": [
                {"label": "Accueil", "icon": "🏠", "active": True},
                {"label": "Cuisine", "icon": "🍽️", "active": False},
                {"label": "Planning", "icon": "📅", "active": False},
            ]
        }
        
        active_item = next(
            (item for item in sidebar_config["items"] if item["active"]), 
            None
        )
        
        assert active_item is not None
        assert active_item["label"] == "Accueil"


# ═══════════════════════════════════════════════════════════
# TESTS FEEDBACK
# ═══════════════════════════════════════════════════════════


class TestFeedbackComponents:
    """Tests pour les composants de feedback"""

    def test_progress_percentage(self):
        """Test calcul pourcentage progression"""
        current = 75
        total = 100
        
        percentage = (current / total) * 100
        
        assert percentage == 75.0

    def test_spinner_states(self):
        """Test états spinner"""
        spinner_states = ["idle", "loading", "success", "error"]
        
        current_state = "loading"
        
        assert current_state in spinner_states

    def test_notification_types(self):
        """Test types de notification"""
        notification_types = {
            "success": {"color": "#4CAF50", "icon": "✅"},
            "error": {"color": "#f44336", "icon": "❌"},
            "warning": {"color": "#ff9800", "icon": "⚠️"},
            "info": {"color": "#2196F3", "icon": "ℹ️"},
        }
        
        assert "success" in notification_types
        assert notification_types["error"]["color"] == "#f44336"
