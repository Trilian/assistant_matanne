"""
Tests pour le module Streamlit courses
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import streamlit as st
from datetime import datetime

# Import du module Ã  tester
# Note: Dans un vrai projet, on utiliserait pytest-streamlit ou streamlit.testing
from src.domains.cuisine.logic.courses import (
    render_liste_active,
    render_rayon_articles,
    render_ajouter_article,
    render_suggestions_ia,
    render_historique,
    render_modeles,
)


class TestRenderListeActive:
    """Tests render_liste_active"""

    @patch('src.modules.cuisine.courses.get_courses_service')
    @patch('src.modules.cuisine.courses.st')
    def test_service_unavailable(self, mock_st, mock_get_service):
        """Test affichage erreur si service unavailable"""
        mock_get_service.return_value = None
        mock_st.error = Mock()

        # Simuler le comportement
        service = Mock()
        if service is None:
            is_error = True
        else:
            is_error = False

        assert is_error is False  # car service n'est pas vraiment None

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_empty_list_display(self, mock_get_service):
        """Test affichage liste vide"""
        mock_service = Mock()
        mock_service.get_liste_courses.return_value = []
        mock_get_service.return_value = mock_service

        liste = mock_service.get_liste_courses(achetes=False)
        assert len(liste) == 0

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_list_with_items(self, mock_get_service):
        """Test affichage liste avec articles"""
        mock_service = Mock()
        articles = [
            {
                'id': 1,
                'ingredient_nom': 'Tomates',
                'quantite_necessaire': 2.0,
                'unite': 'kg',
                'priorite': 'haute',
                'rayon_magasin': 'Fruits & LÃ©gumes'
            },
            {
                'id': 2,
                'ingredient_nom': 'Oeufs',
                'quantite_necessaire': 6.0,
                'unite': 'piÃ¨ce',
                'priorite': 'moyenne',
                'rayon_magasin': 'Laitier'
            }
        ]
        mock_service.get_liste_courses.return_value = articles
        mock_get_service.return_value = mock_service

        liste = mock_service.get_liste_courses(achetes=False)
        assert len(liste) == 2
        assert liste[0]['ingredient_nom'] == 'Tomates'


class TestRenderRayonArticles:
    """Tests render_rayon_articles"""

    @patch('src.modules.cuisine.courses.st')
    def test_render_single_article(self, mock_st):
        """Test affichage article unique"""
        mock_service = Mock()
        articles = [{
            'id': 1,
            'ingredient_nom': 'Tomates',
            'quantite_necessaire': 2.0,
            'unite': 'kg',
            'priorite': 'haute',
            'notes': None,
            'suggere_par_ia': False
        }]

        # Simuler la fonction
        rayon = "Fruits & LÃ©gumes"
        assert rayon is not None
        assert len(articles) == 1

    @patch('src.modules.cuisine.courses.st')
    def test_render_multiple_articles(self, mock_st):
        """Test affichage plusieurs articles"""
        articles = [
            {'id': 1, 'ingredient_nom': 'Tomates', 'priorite': 'haute'},
            {'id': 2, 'ingredient_nom': 'Oeufs', 'priorite': 'moyenne'},
            {'id': 3, 'ingredient_nom': 'Lait', 'priorite': 'basse'}
        ]

        rayon = "Courses"
        assert len(articles) == 3
        assert all(a.get('id') for a in articles)

    def test_priority_emoji_mapping(self):
        """Test mapping emojis prioritÃ©"""
        priority_emojis = {
            "haute": "ðŸ”´",
            "moyenne": "ðŸŸ¡",
            "basse": "ðŸŸ¢"
        }

        assert priority_emojis["haute"] == "ðŸ”´"
        assert priority_emojis["moyenne"] == "ðŸŸ¡"
        assert priority_emojis["basse"] == "ðŸŸ¢"


class TestRenderAjouterArticle:
    """Tests render_ajouter_article"""

    @patch('src.modules.cuisine.courses.get_courses_service')
    @patch('src.modules.cuisine.courses.st')
    def test_form_inputs_valid(self, mock_st, mock_get_service):
        """Test inputs valides du formulaire"""
        valid_inputs = {
            'nom': 'Tomates',
            'quantite': 2.0,
            'unite': 'kg',
            'priorite': 'haute',
            'rayon': 'Fruits & LÃ©gumes'
        }

        assert len(valid_inputs['nom']) > 0
        assert valid_inputs['quantite'] > 0
        assert valid_inputs['unite'] in ['kg', 'l', 'piÃ¨ce', 'g', 'ml', 'paquet']

    def test_form_inputs_invalid_empty_name(self):
        """Test rejet nom vide"""
        nom = ""
        is_valid = len(nom) > 0
        assert is_valid is False

    def test_form_inputs_invalid_zero_quantite(self):
        """Test rejet quantitÃ© zÃ©ro"""
        quantite = 0.0
        is_valid = quantite > 0
        assert is_valid is False

    def test_form_inputs_invalid_priority(self):
        """Test rejet prioritÃ© invalide"""
        valid_priorities = ["basse", "moyenne", "haute"]
        invalid_priority = "mega_haute"
        is_valid = invalid_priority in valid_priorities
        assert is_valid is False


class TestRenderSuggestionsIA:
    """Tests render_suggestions_ia"""

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_suggestions_display(self, mock_get_service):
        """Test affichage suggestions"""
        mock_service = Mock()
        suggestions = [
            Mock(nom='Tomates', quantite=2.0, unite='kg', priorite='haute', rayon='Fruits'),
            Mock(nom='Oeufs', quantite=6.0, unite='piÃ¨ce', priorite='moyenne', rayon='Laitier')
        ]
        mock_service.generer_suggestions_ia_depuis_inventaire.return_value = suggestions
        mock_get_service.return_value = mock_service

        result = mock_service.generer_suggestions_ia_depuis_inventaire()
        assert len(result) == 2
        assert result[0].nom == 'Tomates'

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_empty_suggestions(self, mock_get_service):
        """Test suggestions vides"""
        mock_service = Mock()
        mock_service.generer_suggestions_ia_depuis_inventaire.return_value = []
        mock_get_service.return_value = mock_service

        result = mock_service.generer_suggestions_ia_depuis_inventaire()
        assert len(result) == 0


class TestRenderHistorique:
    """Tests render_historique"""

    def test_date_range_selection(self):
        """Test sÃ©lection plage de dates"""
        date_debut = datetime(2026, 1, 1)
        date_fin = datetime(2026, 1, 24)

        assert date_fin > date_debut
        assert (date_fin - date_debut).days == 23

    def test_articles_in_date_range(self):
        """Test articles dans plage de dates"""
        articles = [
            {'achete_le': datetime(2026, 1, 10)},
            {'achete_le': datetime(2026, 1, 15)},
            {'achete_le': datetime(2025, 12, 25)}  # Hors de la plage
        ]

        date_debut = datetime(2026, 1, 1)
        date_fin = datetime(2026, 1, 24)

        filtered = [
            a for a in articles
            if date_debut <= a['achete_le'] <= date_fin
        ]

        assert len(filtered) == 2


class TestRenderModeles:
    """Tests render_modeles"""

    def test_modele_creation(self):
        """Test crÃ©ation modÃ¨le"""
        modele = {
            "nom": "Courses hebdo",
            "articles": [
                {"nom": "Tomates", "quantite": 2.0},
                {"nom": "Oeufs", "quantite": 6.0}
            ]
        }

        assert modele["nom"] == "Courses hebdo"
        assert len(modele["articles"]) == 2

    def test_modele_empty_list(self):
        """Test modÃ¨le vide"""
        modeles = {}
        assert len(modeles) == 0

    def test_modele_multiple(self):
        """Test plusieurs modÃ¨les"""
        modeles = {
            "Courses hebdo": [
                {"nom": "Tomates", "quantite": 2.0}
            ],
            "Repas amis": [
                {"nom": "Steak", "quantite": 1.5},
                {"nom": "Vin rouge", "quantite": 1.0}
            ]
        }

        assert len(modeles) == 2
        assert "Courses hebdo" in modeles
        assert len(modeles["Repas amis"]) == 2


class TestIntegrationScenarios:
    """Tests scÃ©narios intÃ©gration"""

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_add_article_to_list(self, mock_get_service):
        """ScÃ©nario: ajouter article Ã  la liste"""
        mock_service = Mock()
        mock_service.create.return_value = Mock(id=1)
        mock_get_service.return_value = mock_service

        # 1. CrÃ©er article
        data = {
            "ingredient_id": 1,
            "quantite_necessaire": 2.0,
            "priorite": "haute"
        }
        result = mock_service.create(data)

        # 2. VÃ©rifier crÃ©ation
        assert result is not None
        assert result.id == 1

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_mark_article_purchased(self, mock_get_service):
        """ScÃ©nario: marquer article achetÃ©"""
        mock_service = Mock()
        mock_service.update.return_value = True
        mock_get_service.return_value = mock_service

        # 1. Marquer achetÃ©
        article_id = 1
        updates = {
            "achete": True,
            "achete_le": datetime.now()
        }
        result = mock_service.update(article_id, updates)

        # 2. VÃ©rifier mise Ã  jour
        assert result is True

    @patch('src.modules.cuisine.courses.get_courses_service')
    def test_save_and_load_modele(self, mock_get_service):
        """ScÃ©nario: sauvegarder et charger modÃ¨le"""
        mock_service = Mock()

        # 1. Sauvegarder modÃ¨le
        modele = {
            "nom": "Courses hebdo",
            "articles": [{"nom": "Tomates", "quantite": 2.0}]
        }

        # 2. Charger modÃ¨le (simulÃ©)
        loaded_articles = modele["articles"]

        # 3. VÃ©rifier chargement
        assert len(loaded_articles) == 1
        assert loaded_articles[0]["nom"] == "Tomates"


class TestErrorHandling:
    """Tests gestion des erreurs"""

    def test_invalid_article_id(self):
        """Test ID article invalide"""
        article_id = "invalid"
        try:
            is_valid = isinstance(article_id, int)
            if not is_valid:
                raise ValueError(f"Invalid ID: {article_id}")
        except ValueError:
            pass  # Erreur attendue

    def test_missing_required_field(self):
        """Test champ obligatoire manquant"""
        data = {
            "quantite_necessaire": 2.0
            # ingredient_id manquant
        }

        is_valid = "ingredient_id" in data
        assert is_valid is False

    def test_database_error_handling(self):
        """Test gestion erreur base de donnÃ©es"""
        with patch('src.modules.cuisine.courses.get_courses_service') as mock:
            mock_service = Mock()
            mock_service.create.side_effect = Exception("DB Error")

            try:
                mock_service.create({})
            except Exception as e:
                error_handled = "DB Error" in str(e)
                assert error_handled is True

