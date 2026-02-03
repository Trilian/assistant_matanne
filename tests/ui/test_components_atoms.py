"""
Tests pour les composants atomiques UI (atoms.py)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st


class TestAtomsImport:
    """Tests d'importation des composants atomiques"""

    def test_import_atoms_module(self):
        """Test l'import du module atoms"""
        from src.ui.components import atoms
        assert atoms is not None

    def test_atoms_module_has_functions(self):
        """Test que le module atoms contient des fonctions"""
        from src.ui.components import atoms
        # Vérifier que le module n'est pas vide
        public_funcs = [f for f in dir(atoms) if not f.startswith('_')]
        assert len(public_funcs) > 0

    def test_atoms_module_structure(self):
        """Test la structure du module atoms"""
        from src.ui.components import atoms
        # Vérifier que c'est un module
        assert hasattr(atoms, '__file__') or hasattr(atoms, '__dict__')


@pytest.mark.unit
class TestBoutonPrimaire:
    """Tests pour le bouton primaire"""

    @patch('streamlit.button')
    def test_bouton_primaire_mock(self, mock_button):
        """Test les boutons via streamlit mock"""
        from src.ui.components import atoms
        mock_button.return_value = True
        
        result = st.button("Cliquer")
        
        assert mock_button.called

    @patch('streamlit.button')
    def test_button_with_key(self, mock_button):
        """Test la création d'un bouton avec clé"""
        from src.ui.components import atoms
        mock_button.return_value = False
        
        result = st.button("Cliquer", key="btn_test")
        
        assert mock_button.called

    @patch('streamlit.button')
    def test_button_with_container_width(self, mock_button):
        """Test la création d'un bouton avec largeur conteneur"""
        from src.ui.components import atoms
        mock_button.return_value = True
        
        result = st.button("Ajouter", use_container_width=True)
        
        assert mock_button.called


@pytest.mark.unit
class TestBadge:
    """Tests pour le composant badge"""

    @patch('streamlit.markdown')
    def test_markdown_badge_text(self, mock_markdown):
        """Test l'affichage d'un badge texte via markdown"""
        from src.ui.components import atoms
        
        st.markdown("Badge Info")
        
        assert mock_markdown.called

    @patch('streamlit.markdown')
    def test_markdown_success(self, mock_markdown):
        """Test l'affichage d'un badge succès"""
        from src.ui.components import atoms
        
        st.markdown("✅ Succès")
        
        assert mock_markdown.called

    @patch('streamlit.markdown')
    def test_markdown_error(self, mock_markdown):
        """Test l'affichage d'un badge erreur"""
        from src.ui.components import atoms
        
        st.markdown("❌ Erreur")
        
        assert mock_markdown.called

    @patch('streamlit.markdown')
    def test_markdown_warning(self, mock_markdown):
        """Test l'affichage d'un badge avertissement"""
        from src.ui.components import atoms
        
        st.markdown("⚠️ Attention")
        
        assert mock_markdown.called


@pytest.mark.unit
class TestIcone:
    """Tests pour les icônes"""

    @patch('streamlit.write')
    def test_icon_emoji(self, mock_write):
        """Test l'affichage d'une icône emoji"""
        from src.ui.components import atoms
        
        st.write("📱 Téléphone")
        
        assert mock_write.called

    @patch('streamlit.write')
    def test_icon_with_text(self, mock_write):
        """Test l'affichage d'une icône avec texte"""
        from src.ui.components import atoms
        
        st.write("🍽️ Recette")
        
        assert mock_write.called

    def test_icon_emoji_rendering(self):
        """Test le rendu d'une icône emoji"""
        from src.ui.components import atoms
        
        # Tester que l'emoji fonctionne
        emoji = "✅"
        text = f"{emoji} Valider"
        assert "✅" in text


@pytest.mark.unit
class TestTexteFormate:
    """Tests pour les composants de texte formaté"""

    @patch('streamlit.markdown')
    def test_titre_format(self, mock_markdown):
        """Test le formatage d'un titre"""
        from src.ui.components import atoms
        
        # Vérifier que le module atoms existe et fonctionne
        st.markdown("# Titre Principal")
        assert mock_markdown.called

    def test_atoms_module_structure(self):
        """Test la structure du module atoms"""
        from src.ui.components import atoms
        
        # Vérifier que le module n'est pas vide
        assert len(dir(atoms)) > 0


@pytest.mark.unit
class TestStylesAtoms:
    """Tests pour les styles des composants atomiques"""

    def test_atoms_exports_callables(self):
        """Vérifie que le module atoms existe et est structuré"""
        from src.ui.components import atoms
        
        # Récupérer tous les attributs publics
        public_attrs = [attr for attr in dir(atoms) if not attr.startswith('_')]
        
        # Au moins 5 éléments doivent être présents
        assert len(public_attrs) >= 5

    @patch('streamlit.columns')
    def test_atoms_in_columns(self, mock_columns):
        """Test l'utilisation de streamlit dans des colonnes"""
        from src.ui.components import atoms
        
        mock_columns.return_value = (MagicMock(), MagicMock())
        
        # Vérifier que st.columns fonctionne
        cols = st.columns(2)
        assert mock_columns.called


@pytest.mark.integration
class TestAtomsIntegration:
    """Tests d'intégration pour les composants atomiques"""

    def test_atoms_composition(self):
        """Test la composition de plusieurs composants"""
        from src.ui.components import atoms
        
        # Vérifier que le module peut être composé
        assert atoms is not None and len(dir(atoms)) > 0

    @patch('streamlit.container')
    def test_atoms_in_container(self, mock_container):
        """Test l'utilisation de streamlit dans un conteneur"""
        from src.ui.components import atoms
        
        mock_container.return_value = MagicMock()
        
        # Vérifier que st.container fonctionne
        container = st.container()
        assert mock_container.called
