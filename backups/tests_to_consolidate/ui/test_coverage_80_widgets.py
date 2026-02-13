"""
Tests pour augmenter la couverture du module UI.
Cible: dashboard_widgets.py, data.py, forms.py, layouts.py
"""

from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DASHBOARD_WIDGETS.PY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGraphiqueRepartitionRepas:
    """Tests pour graphique_repartition_repas."""

    def test_graphique_repartition_repas_empty(self):
        """Retourne None si donnÃ©es vides."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        result = graphique_repartition_repas([])
        assert result is None

    def test_graphique_repartition_repas_with_data(self):
        """CrÃ©e un graphique avec des donnÃ©es."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        planning_data = [
            {"type_repas": "dÃ©jeuner"},
            {"type_repas": "dÃ©jeuner"},
            {"type_repas": "dÃ®ner"},
            {"type_repas": "petit_dÃ©jeuner"},
            {"type_repas": "goÃ»ter"},
        ]

        result = graphique_repartition_repas(planning_data)
        assert result is not None

    def test_graphique_repartition_repas_unknown_type(self):
        """GÃ¨re les types de repas inconnus."""
        from src.ui.components.dashboard_widgets import graphique_repartition_repas

        planning_data = [
            {"type_repas": "brunch"},
            {"type_repas": "autre"},
        ]

        result = graphique_repartition_repas(planning_data)
        assert result is not None


class TestGraphiqueInventaireCategories:
    """Tests pour graphique_inventaire_categories."""

    def test_graphique_inventaire_empty(self):
        """Retourne None si vide."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        result = graphique_inventaire_categories([])
        assert result is None

    def test_graphique_inventaire_with_data(self):
        """CrÃ©e le graphique avec des donnÃ©es."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        inventaire = [
            {"categorie": "Fruits", "statut": "ok"},
            {"categorie": "Fruits", "statut": "critique"},
            {"categorie": "LÃ©gumes", "statut": "sous_seuil"},
            {"categorie": "Viandes", "statut": "ok"},
        ]

        result = graphique_inventaire_categories(inventaire)
        assert result is not None

    def test_graphique_inventaire_missing_categorie(self):
        """GÃ¨re les articles sans catÃ©gorie."""
        from src.ui.components.dashboard_widgets import graphique_inventaire_categories

        inventaire = [
            {"statut": "ok"},
            {"categorie": "Fruits"},
        ]

        result = graphique_inventaire_categories(inventaire)
        assert result is not None


class TestGraphiqueActiviteSemaine:
    """Tests pour graphique_activite_semaine."""

    def test_graphique_activite_empty(self):
        """Retourne un Figure avec des zÃ©ros si vide."""
        import plotly.graph_objects as go

        from src.ui.components.dashboard_widgets import graphique_activite_semaine

        result = graphique_activite_semaine([])
        # La fonction retourne une Figure mÃªme si vide (avec valeurs 0)
        assert isinstance(result, go.Figure)

    def test_graphique_activite_with_data(self):
        """CrÃ©e le graphique avec des donnÃ©es."""
        from src.ui.components.dashboard_widgets import graphique_activite_semaine

        today = date.today()
        activites = [
            {"date": today, "count": 5, "type": "recette"},
            {"date": today - timedelta(days=1), "count": 3, "type": "course"},
        ]

        result = graphique_activite_semaine(activites)
        assert result is not None


class TestCarteMetriqueAvancee:
    """Tests pour carte_metrique_avancee."""

    @patch("src.ui.components.dashboard_widgets.st")
    def test_carte_metrique_basic(self, mock_st):
        """Test carte mÃ©trique basique."""
        mock_st.session_state = {}
        mock_st.markdown = MagicMock()

        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(titre="Total", valeur=42, icone="ðŸ“Š")

        mock_st.markdown.assert_called()

    @patch("src.ui.components.dashboard_widgets.st")
    def test_carte_metrique_with_delta(self, mock_st):
        """Test carte avec delta."""
        mock_st.session_state = {}
        mock_st.markdown = MagicMock()

        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(
            titre="Score", valeur=85, icone="ðŸ“ˆ", delta="+5", delta_positif=True
        )

        mock_st.markdown.assert_called()

    @patch("src.ui.components.dashboard_widgets.st")
    def test_carte_metrique_with_sous_titre(self, mock_st):
        """Test carte avec sous-titre."""
        mock_st.session_state = {}
        mock_st.markdown = MagicMock()

        from src.ui.components.dashboard_widgets import carte_metrique_avancee

        carte_metrique_avancee(
            titre="Progress", valeur="80%", icone="ðŸŽ¯", sous_titre="Cette semaine"
        )

        mock_st.markdown.assert_called()


class TestAfficherTimelineActivites:
    """Tests pour afficher_timeline_activites."""

    @patch("src.ui.components.dashboard_widgets.st")
    def test_timeline_empty(self, mock_st):
        """Test timeline vide."""
        mock_st.session_state = {}
        mock_st.info = MagicMock()

        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        afficher_timeline_activites([])
        mock_st.info.assert_called()

    @patch("src.ui.components.dashboard_widgets.st")
    def test_timeline_with_activities(self, mock_st):
        """Test timeline avec activitÃ©s."""
        mock_st.session_state = {}
        mock_st.markdown = MagicMock()
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container = MagicMock(return_value=mock_container)

        from src.ui.components.dashboard_widgets import afficher_timeline_activites

        activities = [
            {
                "timestamp": datetime.now(),
                "type": "recette",
                "description": "Nouvelle recette ajoutÃ©e",
                "icon": "ðŸ½ï¸",
            }
        ]

        afficher_timeline_activites(activities)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DATA.PY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPagination:
    """Tests pour pagination."""

    @patch("src.ui.components.data.st")
    def test_pagination_small_dataset(self, mock_st):
        """Pas de pagination si peu d'items."""
        mock_st.session_state = {}

        from src.ui.components.data import pagination

        page, per_page = pagination(10, 20, "test")
        assert page == 1
        assert per_page == 20

    @patch("src.ui.components.data.st")
    def test_pagination_large_dataset(self, mock_st):
        """Pagination pour grand dataset."""
        mock_st.session_state = {"test_page": 2}
        mock_st.columns = MagicMock(return_value=[MagicMock(), MagicMock(), MagicMock()])
        mock_st.button = MagicMock(return_value=False)
        mock_st.selectbox = MagicMock(return_value=2)
        mock_st.caption = MagicMock()

        from src.ui.components.data import pagination

        page, per_page = pagination(100, 20, "test")
        assert page == 2
        assert per_page == 20


class TestMetricsRow:
    """Tests pour metrics_row."""

    @patch("src.ui.components.data.st")
    def test_metrics_row_empty(self, mock_st):
        """Ne fait rien si liste vide."""
        from src.ui.components.data import metrics_row

        metrics_row([])
        # Pas d'appel Ã  st.columns

    @patch("src.ui.components.data.st")
    def test_metrics_row_with_stats(self, mock_st):
        """Affiche les mÃ©triques."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_st.metric = MagicMock()

        from src.ui.components.data import metrics_row

        stats = [{"label": "Total", "value": 42, "delta": "+5"}, {"label": "Actifs", "value": 38}]

        metrics_row(stats)
        mock_st.columns.assert_called()


class TestExportButtons:
    """Tests pour export_buttons."""

    @patch("src.ui.components.data.st")
    def test_export_buttons_list(self, mock_st):
        """Export depuis liste."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_st.download_button = MagicMock(return_value=False)

        from src.ui.components.data import export_buttons

        data = [{"A": 1, "B": 2}, {"A": 3, "B": 4}]
        export_buttons(data, "test")
        mock_st.download_button.assert_called()

    @patch("src.ui.components.data.st")
    def test_export_buttons_with_dataframe(self, mock_st):
        """Export depuis DataFrame."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_st.download_button = MagicMock(return_value=False)

        from src.ui.components.data import export_buttons

        df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        export_buttons(df, "data")
        mock_st.download_button.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMS.PY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestFormField:
    """Tests pour form_field."""

    @patch("src.ui.components.forms.st")
    def test_form_field_text(self, mock_st):
        """Test champ texte."""
        mock_st.text_input = MagicMock(return_value="test value")

        from src.ui.components.forms import form_field

        config = {"type": "text", "name": "nom", "label": "Nom"}
        result = form_field(config, "recipe")

        assert result == "test value"
        mock_st.text_input.assert_called()

    @patch("src.ui.components.forms.st")
    def test_form_field_number(self, mock_st):
        """Test champ numÃ©rique."""
        mock_st.number_input = MagicMock(return_value=42.0)

        from src.ui.components.forms import form_field

        config = {"type": "number", "name": "qty", "label": "QuantitÃ©", "default": 0}
        result = form_field(config, "item")

        assert result == 42.0

    @patch("src.ui.components.forms.st")
    def test_form_field_select(self, mock_st):
        """Test champ select."""
        mock_st.selectbox = MagicMock(return_value="option1")

        from src.ui.components.forms import form_field

        config = {
            "type": "select",
            "name": "cat",
            "label": "CatÃ©gorie",
            "options": ["option1", "option2"],
        }
        result = form_field(config, "item")

        assert result == "option1"

    @patch("src.ui.components.forms.st")
    def test_form_field_multiselect(self, mock_st):
        """Test champ multiselect."""
        mock_st.multiselect = MagicMock(return_value=["a", "b"])

        from src.ui.components.forms import form_field

        config = {"type": "multiselect", "name": "tags", "options": ["a", "b", "c"]}
        result = form_field(config, "item")

        assert result == ["a", "b"]

    @patch("src.ui.components.forms.st")
    def test_form_field_checkbox(self, mock_st):
        """Test champ checkbox."""
        mock_st.checkbox = MagicMock(return_value=True)

        from src.ui.components.forms import form_field

        config = {"type": "checkbox", "name": "active", "label": "Actif"}
        result = form_field(config, "item")

        assert result is True

    @patch("src.ui.components.forms.st")
    def test_form_field_date(self, mock_st):
        """Test champ date."""
        today = date.today()
        mock_st.date_input = MagicMock(return_value=today)

        from src.ui.components.forms import form_field

        config = {"type": "date", "name": "date", "label": "Date"}
        result = form_field(config, "event")

        assert result == today

    @patch("src.ui.components.forms.st")
    def test_form_field_textarea(self, mock_st):
        """Test champ textarea."""
        mock_st.text_area = MagicMock(return_value="Long text")

        from src.ui.components.forms import form_field

        config = {"type": "textarea", "name": "desc", "label": "Description"}
        result = form_field(config, "item")

        assert result == "Long text"

    @patch("src.ui.components.forms.st")
    def test_form_field_required(self, mock_st):
        """Test champ requis ajoute astÃ©risque."""
        mock_st.text_input = MagicMock(return_value="")

        from src.ui.components.forms import form_field

        config = {"type": "text", "name": "nom", "label": "Nom", "required": True}
        form_field(config, "recipe")

        # VÃ©rifier que le label contient *
        call_args = mock_st.text_input.call_args
        assert "*" in call_args[0][0]


class TestSearchBar:
    """Tests pour search_bar."""

    @patch("src.ui.components.forms.st")
    def test_search_bar_basic(self, mock_st):
        """Test barre de recherche."""
        mock_st.text_input = MagicMock(return_value="query")

        from src.ui.components.forms import search_bar

        result = search_bar(key="search")
        assert result == "query"

    @patch("src.ui.components.forms.st")
    def test_search_bar_with_placeholder(self, mock_st):
        """Test avec placeholder."""
        mock_st.text_input = MagicMock(return_value="")

        from src.ui.components.forms import search_bar

        search_bar(placeholder="Rechercher...", key="search")

        call_args = mock_st.text_input.call_args
        assert "Rechercher..." in str(call_args)


class TestFilterPanel:
    """Tests pour filter_panel."""

    @patch("src.ui.components.forms.st")
    def test_filter_panel_basic(self, mock_st):
        """Test panneau de filtres."""
        mock_st.selectbox = MagicMock(return_value="all")
        mock_st.text_input = MagicMock(return_value="")

        from src.ui.components.forms import filter_panel

        filters_config = {
            "status": {"type": "select", "label": "Statut", "options": ["all", "active"]},
            "search": {"type": "text", "label": "Recherche"},
        }

        result = filter_panel(filters_config, "test")
        assert isinstance(result, dict)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LAYOUTS.PY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGridLayout:
    """Tests pour grid_layout."""

    @patch("src.ui.components.layouts.st")
    def test_grid_layout_empty(self, mock_st):
        """Test grille vide."""
        mock_st.info = MagicMock()

        from src.ui.components.layouts import grid_layout

        grid_layout([], cols_per_row=3)
        mock_st.info.assert_called_with("Aucun Ã©lÃ©ment")

    @patch("src.ui.components.layouts.st")
    def test_grid_layout_with_items(self, mock_st):
        """Test grille avec items."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col, mock_col])
        mock_st.write = MagicMock()

        from src.ui.components.layouts import grid_layout

        items = [{"name": "Item 1"}, {"name": "Item 2"}, {"name": "Item 3"}]
        grid_layout(items, cols_per_row=3)

        mock_st.columns.assert_called()

    @patch("src.ui.components.layouts.st")
    def test_grid_layout_with_custom_renderer(self, mock_st):
        """Test grille avec renderer personnalisÃ©."""
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])

        from src.ui.components.layouts import grid_layout

        render_calls = []

        def custom_renderer(item, key):
            render_calls.append((item, key))

        items = [{"id": 1}, {"id": 2}]
        grid_layout(items, cols_per_row=2, card_renderer=custom_renderer)

        assert len(render_calls) == 2


class TestItemCard:
    """Tests pour item_card."""

    @patch("src.ui.components.layouts.st")
    def test_item_card_basic(self, mock_st):
        """Test carte basique."""
        mock_st.markdown = MagicMock()

        from src.ui.components.layouts import item_card

        item_card(title="Test Item", metadata=["Meta 1", "Meta 2"])

        mock_st.markdown.assert_called()

    @patch("src.ui.components.layouts.st")
    def test_item_card_with_status(self, mock_st):
        """Test carte avec statut."""
        mock_st.markdown = MagicMock()
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container = MagicMock(return_value=mock_container)

        from src.ui.components.layouts import item_card

        item_card(title="Test", metadata=["Info"], status="Active", status_color="#4CAF50")

        mock_st.markdown.assert_called()

    @patch("src.ui.components.layouts.st")
    def test_item_card_with_tags(self, mock_st):
        """Test carte avec tags."""
        mock_st.markdown = MagicMock()

        from src.ui.components.layouts import item_card

        item_card(title="Test", metadata=[], tags=["tag1", "tag2"])

        mock_st.markdown.assert_called()

    @patch("src.ui.components.layouts.st")
    def test_item_card_with_actions(self, mock_st):
        """Test carte avec actions."""
        mock_st.markdown = MagicMock()
        mock_st.caption = MagicMock()
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=mock_col)
        mock_col.__exit__ = MagicMock(return_value=False)
        mock_st.columns = MagicMock(return_value=[mock_col, mock_col])
        mock_st.button = MagicMock(return_value=False)
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        mock_st.container = MagicMock(return_value=mock_container)

        from src.ui.components.layouts import item_card

        # actions format: list[tuple] = (label, callback)
        actions = [("Edit", lambda: None), ("Delete", lambda: None)]

        item_card(title="Test", metadata=["Info"], actions=actions)


class TestCollapsibleSection:
    """Tests pour collapsible_section."""

    @patch("src.ui.components.layouts.st")
    def test_collapsible_section(self, mock_st):
        """Test section dÃ©pliable."""
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=mock_expander)
        mock_expander.__exit__ = MagicMock(return_value=False)
        mock_st.expander = MagicMock(return_value=mock_expander)

        from src.ui.components.layouts import collapsible_section

        content_called = []

        def content_fn():
            content_called.append(True)

        collapsible_section("Section Test", content_fn)
        mock_st.expander.assert_called()


class TestTabsLayout:
    """Tests pour tabs_layout."""

    @patch("src.ui.components.layouts.st")
    def test_tabs_layout_basic(self, mock_st):
        """Test onglets."""
        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=mock_tab)
        mock_tab.__exit__ = MagicMock(return_value=False)
        mock_st.tabs = MagicMock(return_value=[mock_tab, mock_tab])

        from src.ui.components.layouts import tabs_layout

        content_called = []
        tab_data = {
            "Tab 1": lambda: content_called.append(1),
            "Tab 2": lambda: content_called.append(2),
        }

        tabs_layout(tab_data)
        mock_st.tabs.assert_called()
