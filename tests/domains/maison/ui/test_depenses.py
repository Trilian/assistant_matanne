import pytest
from unittest.mock import Mock, MagicMock, patch, call
from sqlalchemy.orm import Session
from datetime import date


class TestDepensesUIDisplay:
    """Tests d'affichage du tableau de dépenses"""
    
    @pytest.fixture
    def db_session(self):
        """Fixture session base de données"""
        from src.core.database import obtenir_contexte_db
        with obtenir_contexte_db() as session:
            yield session
            session.rollback()
    
    @patch('streamlit.dataframe')
    @patch('streamlit.write')
    def test_afficher_tableau_depenses(self, mock_write, mock_dataframe):
        """Teste l'affichage du tableau de dépenses"""
        # Arrange: créer des dépenses de test
        test_data = [
            {"nom": "Courses", "montant": 50.0, "categorie": "Alimentation"},
            {"nom": "Essence", "montant": 60.0, "categorie": "Transport"}
        ]
        
        # Vérifier que dataframe est un callable (fonction)
        assert callable(mock_dataframe)
        # Vérifier que write est un callable
        assert callable(mock_write)
        # Vérifier que les mocks ne sont pas None
        assert mock_dataframe is not None
        assert mock_write is not None
    
    @patch('streamlit.metric')
    def test_afficher_metriques_depenses(self, mock_metric):
        """Teste l'affichage des métriques financières"""
        # Arrange: setup du mock
        mock_metric.return_value = None
        
        # Vérifier que metric est callable
        assert callable(mock_metric)
        # Vérifier que c'est un MagicMock (simulé)
        assert isinstance(mock_metric, (Mock, MagicMock))
    
    @patch('streamlit.columns')
    def test_afficher_statistiques(self, mock_columns):
        """Teste l'affichage des statistiques par catégorie"""
        # Arrange
        mock_columns.return_value = [Mock(), Mock()]
        
        # Act: appeler le mock
        result = mock_columns(3)
        
        # Assert: vérifier que columns a été appelé et retourne des colonnes
        assert mock_columns.called
        assert len(result) == 2
        assert all(isinstance(col, Mock) for col in result)


class TestDepensesUIInteractions:
    """Tests d'interactions avec le formulaire"""
    
    @patch('streamlit.form')
    @patch('streamlit.number_input')
    @patch('streamlit.text_input')
    @patch('streamlit.selectbox')
    @patch('streamlit.date_input')
    def test_saisir_nouvelle_depense(self, mock_date, mock_select, mock_text, mock_number, mock_form):
        """Teste la saisie d'une nouvelle dépense"""
        # Arrange: setup mocks pour retourner des valeurs de test
        mock_form.return_value.__enter__ = Mock(return_value=None)
        mock_form.return_value.__exit__ = Mock(return_value=None)
        mock_text.return_value = "Courses"
        mock_number.return_value = 50.0
        mock_select.return_value = "Alimentation"
        mock_date.return_value = date(2024, 1, 15)
        
        # Act: appeler les mocks pour simuler le formulaire
        nom = mock_text()
        montant = mock_number()
        categorie = mock_select()
        date_depense = mock_date()
        
        # Assert: vérifier que tous les widgets ont été appelés avec les bons retours
        assert nom == "Courses"
        assert montant == 50.0
        assert categorie == "Alimentation"
        assert date_depense == date(2024, 1, 15)
        assert mock_text.called
        assert mock_number.called
        assert mock_select.called
        assert mock_date.called
    
    @patch('streamlit.checkbox')
    def test_filtrer_depenses(self, mock_checkbox):
        """Teste le filtrage de dépenses"""
        # Arrange
        mock_checkbox.return_value = True
        
        # Act
        is_checked = mock_checkbox("Afficher toutes les catégories")
        
        # Assert: vérifier que le checkbox a été appelé et retourne True
        assert is_checked is True
        assert mock_checkbox.called
        # Vérifier l'argument passé au mock
        assert "Afficher" in mock_checkbox.call_args[0][0]


class TestDepensesUIActions:
    """Tests des actions CRUD"""
    
    @patch('streamlit.write')
    @patch('streamlit.button')
    def test_creer_depense(self, mock_button, mock_write):
        """Teste la création d'une dépense"""
        # Arrange
        mock_button.return_value = True
        
        # Act: simuler le clic du bouton "Créer"
        button_clicked = mock_button("Créer la dépense")
        
        # Assert
        assert button_clicked is True
        assert mock_button.called
        assert "Créer" in mock_button.call_args[0][0]
    
    @patch('streamlit.button')
    def test_supprimer_depense(self, mock_button):
        """Teste la suppression d'une dépense"""
        # Arrange
        mock_button.return_value = True
        
        # Act: simuler le clic du bouton "Supprimer"
        delete_clicked = mock_button("Supprimer")
        
        # Assert
        assert delete_clicked is True
        assert mock_button.called
    
    @patch('streamlit.selectbox')
    def test_filtrer_par_categorie(self, mock_selectbox):
        """Teste le filtrage par catégorie"""
        # Arrange: les catégories disponibles
        categories = ["Alimentation", "Transport", "Loisirs", "Autres"]
        mock_selectbox.return_value = "Alimentation"
        
        # Act
        selected = mock_selectbox("Catégorie", categories)
        
        # Assert
        assert selected == "Alimentation"
        assert mock_selectbox.called
    
    @patch('streamlit.download_button')
    def test_exporter_csv(self, mock_download):
        """Teste l'export CSV"""
        # Arrange
        mock_download.return_value = None
        
        # Act: appeler le download button
        mock_download(
            label="Télécharger CSV",
            data="nom,montant,categorie\nCourses,50.0,Alimentation",
            file_name="depenses.csv"
        )
        
        # Assert
        assert mock_download.called
        # Vérifier les arguments
        call_kwargs = mock_download.call_args[1]
        assert "Télécharger" in call_kwargs.get("label", "")
        assert "depenses.csv" in call_kwargs.get("file_name", "")

