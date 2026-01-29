"""
Tests pour src/ui/components/layouts.py
Grilles, cartes, containers
"""

from unittest.mock import MagicMock, patch, call

import pytest


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit"""
    with patch("src.ui.components.layouts.st") as mock_st:
        # Mock columns
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_st.columns.return_value = [mock_col, mock_col, mock_col]

        # Mock expander
        mock_expander = MagicMock()
        mock_expander.__enter__ = MagicMock(return_value=None)
        mock_expander.__exit__ = MagicMock(return_value=None)
        mock_st.expander.return_value = mock_expander

        # Mock container
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=None)
        mock_container.__exit__ = MagicMock(return_value=None)
        mock_st.container.return_value = mock_container

        # Mock tabs
        mock_tab = MagicMock()
        mock_tab.__enter__ = MagicMock(return_value=None)
        mock_tab.__exit__ = MagicMock(return_value=None)
        mock_st.tabs.return_value = [mock_tab, mock_tab, mock_tab]

        # Autres mocks
        mock_st.info = MagicMock()
        mock_st.write = MagicMock()
        mock_st.markdown = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.image = MagicMock()
        mock_st.button.return_value = False

        yield mock_st


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GRID_LAYOUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestGridLayout:
    """Tests pour grid_layout()"""

    def test_grid_layout_empty(self, mock_streamlit):
        """Test grille vide"""
        from src.ui.components.layouts import grid_layout

        grid_layout([])

        mock_streamlit.info.assert_called_once_with("Aucun élément")

    def test_grid_layout_single_item(self, mock_streamlit):
        """Test un seul item"""
        from src.ui.components.layouts import grid_layout

        items = [{"nom": "Item 1"}]

        grid_layout(items)

        mock_streamlit.columns.assert_called()

    def test_grid_layout_multiple_items(self, mock_streamlit):
        """Test plusieurs items"""
        from src.ui.components.layouts import grid_layout

        items = [{"nom": f"Item {i}"} for i in range(5)]

        grid_layout(items, cols_per_row=3)

        # Avec 5 items et 3 colonnes, besoin de 2 lignes
        assert mock_streamlit.columns.call_count >= 2

    def test_grid_layout_custom_cols(self, mock_streamlit):
        """Test colonnes personnalisées"""
        from src.ui.components.layouts import grid_layout

        items = [{"nom": "Item"}]

        grid_layout(items, cols_per_row=4)

        mock_streamlit.columns.assert_called_with(4)

    def test_grid_layout_with_renderer(self, mock_streamlit):
        """Test avec fonction de rendu personnalisée"""
        from src.ui.components.layouts import grid_layout

        items = [{"nom": "Test"}]
        mock_renderer = MagicMock()

        grid_layout(items, card_renderer=mock_renderer)

        mock_renderer.assert_called_once()

    def test_grid_layout_without_renderer(self, mock_streamlit):
        """Test sans fonction de rendu"""
        from src.ui.components.layouts import grid_layout

        items = [{"nom": "Test"}]

        grid_layout(items)

        # Doit utiliser st.write par défaut
        mock_streamlit.write.assert_called()

    def test_grid_layout_exact_rows(self, mock_streamlit):
        """Test nombre exact de lignes"""
        from src.ui.components.layouts import grid_layout

        # 9 items / 3 colonnes = 3 lignes exactes
        items = [{"id": i} for i in range(9)]

        grid_layout(items, cols_per_row=3)

        assert mock_streamlit.columns.call_count == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ITEM_CARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestItemCard:
    """Tests pour item_card()"""

    def test_item_card_basic(self, mock_streamlit):
        """Test carte basique"""
        from src.ui.components.layouts import item_card

        item_card(title="Test", metadata=["Info 1"])

        mock_streamlit.markdown.assert_called()

    def test_item_card_with_status(self, mock_streamlit):
        """Test carte avec statut"""
        from src.ui.components.layouts import item_card

        # Mock colonnes pour le layout avec statut
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_streamlit.columns.return_value = [mock_col, mock_col]

        item_card(
            title="Test",
            metadata=["Info"],
            status="Actif",
            status_color="#4CAF50"
        )

        # Vérifier colonnes pour titre + statut
        mock_streamlit.columns.assert_called()

    def test_item_card_without_status(self, mock_streamlit):
        """Test carte sans statut"""
        from src.ui.components.layouts import item_card

        item_card(title="Test", metadata=["Info"], status=None)

        # Le markdown pour le titre doit être appelé
        assert any("### Test" in str(c) for c in mock_streamlit.markdown.call_args_list)

    def test_item_card_with_tags(self, mock_streamlit):
        """Test carte avec tags"""
        from src.ui.components.layouts import item_card

        item_card(
            title="Test",
            metadata=["Info"],
            tags=["Tag1", "Tag2"]
        )

        # Vérifier que les tags sont dans le HTML
        calls = mock_streamlit.markdown.call_args_list
        tag_calls = [c for c in calls if "Tag1" in str(c) or "Tag2" in str(c)]
        assert len(tag_calls) >= 1

    def test_item_card_with_image(self, mock_streamlit):
        """Test carte avec image"""
        from src.ui.components.layouts import item_card

        # Mock colonnes pour layout image + contenu
        mock_col = MagicMock()
        mock_col.__enter__ = MagicMock(return_value=None)
        mock_col.__exit__ = MagicMock(return_value=None)
        mock_streamlit.columns.return_value = [mock_col, mock_col]

        item_card(
            title="Test",
            metadata=["Info"],
            image_url="https://example.com/image.jpg"
        )

        mock_streamlit.image.assert_called_once()

    def test_item_card_without_image(self, mock_streamlit):
        """Test carte sans image"""
        from src.ui.components.layouts import item_card

        item_card(title="Test", metadata=["Info"])

        mock_streamlit.image.assert_not_called()

    def test_item_card_with_actions(self, mock_streamlit):
        """Test carte avec actions"""
        from src.ui.components.layouts import item_card

        action1 = MagicMock()
        action2 = MagicMock()

        item_card(
            title="Test",
            metadata=[],
            actions=[("Voir", action1), ("Ã‰diter", action2)]
        )

        # Buttons doivent être créés
        assert mock_streamlit.button.call_count >= 2

    def test_item_card_action_callback(self, mock_streamlit):
        """Test callback d'action"""
        from src.ui.components.layouts import item_card

        mock_callback = MagicMock()
        mock_streamlit.button.return_value = True

        item_card(
            title="Test",
            metadata=[],
            actions=[("Action", mock_callback)]
        )

        mock_callback.assert_called_once()

    def test_item_card_metadata_display(self, mock_streamlit):
        """Test affichage métadonnées"""
        from src.ui.components.layouts import item_card

        item_card(
            title="Test",
            metadata=["45min", "6 portions", "Facile"]
        )

        # Caption doit être appelé avec les métadonnées jointes
        mock_streamlit.caption.assert_called()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COLLAPSIBLE_SECTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCollapsibleSection:
    """Tests pour collapsible_section()"""

    def test_collapsible_section_basic(self, mock_streamlit):
        """Test section pliable basique"""
        from src.ui.components.layouts import collapsible_section

        content_fn = MagicMock()

        collapsible_section("Détails", content_fn)

        mock_streamlit.expander.assert_called_once()
        content_fn.assert_called_once()

    def test_collapsible_section_expanded(self, mock_streamlit):
        """Test section ouverte par défaut"""
        from src.ui.components.layouts import collapsible_section

        collapsible_section("Détails", lambda: None, expanded=True)

        call_args = mock_streamlit.expander.call_args
        assert call_args[1]["expanded"] is True

    def test_collapsible_section_collapsed(self, mock_streamlit):
        """Test section fermée par défaut"""
        from src.ui.components.layouts import collapsible_section

        collapsible_section("Détails", lambda: None, expanded=False)

        call_args = mock_streamlit.expander.call_args
        assert call_args[1]["expanded"] is False

    def test_collapsible_section_title(self, mock_streamlit):
        """Test titre de section"""
        from src.ui.components.layouts import collapsible_section

        collapsible_section("Mon titre", lambda: None)

        mock_streamlit.expander.assert_called_with("Mon titre", expanded=False)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS TABS_LAYOUT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestTabsLayout:
    """Tests pour tabs_layout()"""

    def test_tabs_layout_basic(self, mock_streamlit):
        """Test tabs basique"""
        from src.ui.components.layouts import tabs_layout

        tab1 = MagicMock()
        tab2 = MagicMock()

        tabs_layout({"Vue 1": tab1, "Vue 2": tab2})

        mock_streamlit.tabs.assert_called_once()
        tab1.assert_called_once()
        tab2.assert_called_once()

    def test_tabs_layout_tab_labels(self, mock_streamlit):
        """Test labels des tabs"""
        from src.ui.components.layouts import tabs_layout

        tabs_layout({
            "Recettes": lambda: None,
            "Planning": lambda: None,
            "Stats": lambda: None
        })

        call_args = mock_streamlit.tabs.call_args[0][0]
        assert "Recettes" in call_args
        assert "Planning" in call_args
        assert "Stats" in call_args

    def test_tabs_layout_single_tab(self, mock_streamlit):
        """Test un seul tab"""
        from src.ui.components.layouts import tabs_layout

        content_fn = MagicMock()

        tabs_layout({"Seul": content_fn})

        content_fn.assert_called_once()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CARD_CONTAINER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCardContainer:
    """Tests pour card_container()"""

    def test_card_container_basic(self, mock_streamlit):
        """Test container basique"""
        from src.ui.components.layouts import card_container

        content_fn = MagicMock()

        card_container(content_fn)

        content_fn.assert_called_once()
        # Deux appels markdown: ouverture et fermeture div
        assert mock_streamlit.markdown.call_count == 2

    def test_card_container_custom_color(self, mock_streamlit):
        """Test couleur personnalisée"""
        from src.ui.components.layouts import card_container

        card_container(lambda: None, color="#f0f0f0")

        html = mock_streamlit.markdown.call_args_list[0][0][0]
        assert "#f0f0f0" in html

    def test_card_container_default_color(self, mock_streamlit):
        """Test couleur par défaut"""
        from src.ui.components.layouts import card_container

        card_container(lambda: None)

        html = mock_streamlit.markdown.call_args_list[0][0][0]
        assert "#ffffff" in html

    def test_card_container_unsafe_html(self, mock_streamlit):
        """Test HTML non sécurisé"""
        from src.ui.components.layouts import card_container

        card_container(lambda: None)

        # Les deux appels doivent avoir unsafe_allow_html=True
        for call in mock_streamlit.markdown.call_args_list:
            assert call[1]["unsafe_allow_html"] is True

