"""
Tests couverture pour src/services/courses_intelligentes.py
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date, timedelta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODÃˆLES PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestArticleCourseModel:
    """Tests pour ArticleCourse."""

    def test_article_course_minimal(self):
        """Test crÃ©ation minimale."""
        from src.services.courses_intelligentes import ArticleCourse
        
        article = ArticleCourse(nom="Tomate", quantite=2.0)
        
        assert article.nom == "Tomate"
        assert article.quantite == 2.0
        assert article.unite == ""
        assert article.rayon == "Autre"

    def test_article_course_complete(self):
        """Test crÃ©ation complÃ¨te."""
        from src.services.courses_intelligentes import ArticleCourse
        
        article = ArticleCourse(
            nom="Poulet",
            quantite=1.5,
            unite="kg",
            rayon="Boucherie",
            recettes_source=["Poulet rÃ´ti"],
            priorite=1,
            en_stock=0.5,
            a_acheter=1.0,
            notes="Bio de prÃ©fÃ©rence"
        )
        
        assert article.rayon == "Boucherie"
        assert len(article.recettes_source) == 1
        assert article.a_acheter == 1.0

    def test_article_course_defaults(self):
        """Test valeurs par dÃ©faut."""
        from src.services.courses_intelligentes import ArticleCourse
        
        article = ArticleCourse(nom="Test", quantite=1)
        
        assert article.recettes_source == []
        assert article.priorite == 2
        assert article.en_stock == 0
        assert article.a_acheter == 0
        assert article.notes == ""


@pytest.mark.unit
class TestListeCoursesIntelligenteModel:
    """Tests pour ListeCoursesIntelligente."""

    def test_liste_courses_empty(self):
        """Test liste vide."""
        from src.services.courses_intelligentes import ListeCoursesIntelligente
        
        liste = ListeCoursesIntelligente()
        
        assert liste.articles == []
        assert liste.total_articles == 0
        assert liste.recettes_couvertes == []
        assert liste.estimation_budget is None
        assert liste.alertes == []

    def test_liste_courses_with_articles(self):
        """Test liste avec articles."""
        from src.services.courses_intelligentes import (
            ListeCoursesIntelligente, ArticleCourse
        )
        
        articles = [
            ArticleCourse(nom="Tomate", quantite=2),
            ArticleCourse(nom="Oignon", quantite=3)
        ]
        
        liste = ListeCoursesIntelligente(
            articles=articles,
            total_articles=2,
            recettes_couvertes=["Ratatouille"],
            estimation_budget=15.50,
            alertes=["Tomates en promotion"]
        )
        
        assert len(liste.articles) == 2
        assert liste.estimation_budget == 15.50


@pytest.mark.unit
class TestSuggestionSubstitutionModel:
    """Tests pour SuggestionSubstitution."""

    def test_suggestion_minimal(self):
        """Test suggestion minimale."""
        from src.services.courses_intelligentes import SuggestionSubstitution
        
        suggestion = SuggestionSubstitution(
            ingredient_original="Beurre",
            suggestion="Margarine",
            raison="Alternative vÃ©gÃ©tale"
        )
        
        assert suggestion.ingredient_original == "Beurre"
        assert suggestion.suggestion == "Margarine"
        assert suggestion.economie_estimee is None

    def test_suggestion_with_economie(self):
        """Test suggestion avec Ã©conomie."""
        from src.services.courses_intelligentes import SuggestionSubstitution
        
        suggestion = SuggestionSubstitution(
            ingredient_original="Saumon frais",
            suggestion="Saumon surgelÃ©",
            raison="Moins cher",
            economie_estimee=3.50
        )
        
        assert suggestion.economie_estimee == 3.50


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestMappingRayons:
    """Tests pour MAPPING_RAYONS."""

    def test_mapping_rayons_exists(self):
        """Test que le mapping existe."""
        from src.services.courses_intelligentes import MAPPING_RAYONS
        
        assert MAPPING_RAYONS is not None
        assert isinstance(MAPPING_RAYONS, dict)
        assert len(MAPPING_RAYONS) > 0

    def test_mapping_rayons_fruits_legumes(self):
        """Test rayons fruits & lÃ©gumes."""
        from src.services.courses_intelligentes import MAPPING_RAYONS
        
        assert MAPPING_RAYONS.get("tomate") == "Fruits & LÃ©gumes"
        assert MAPPING_RAYONS.get("carotte") == "Fruits & LÃ©gumes"

    def test_mapping_rayons_boucherie(self):
        """Test rayon boucherie."""
        from src.services.courses_intelligentes import MAPPING_RAYONS
        
        assert MAPPING_RAYONS.get("poulet") == "Boucherie"
        assert MAPPING_RAYONS.get("boeuf") == "Boucherie"

    def test_mapping_rayons_cremerie(self):
        """Test rayon crÃ¨merie."""
        from src.services.courses_intelligentes import MAPPING_RAYONS
        
        assert MAPPING_RAYONS.get("lait") == "CrÃ¨merie"
        assert MAPPING_RAYONS.get("beurre") == "CrÃ¨merie"


@pytest.mark.unit
class TestPriorites:
    """Tests pour PRIORITES."""

    def test_priorites_exists(self):
        """Test que les prioritÃ©s existent."""
        from src.services.courses_intelligentes import PRIORITES
        
        assert PRIORITES is not None
        assert isinstance(PRIORITES, dict)

    def test_priorites_values(self):
        """Test valeurs des prioritÃ©s."""
        from src.services.courses_intelligentes import PRIORITES
        
        # Les prioritÃ©s sont des entiers 1-3
        for rayon, prio in PRIORITES.items():
            assert isinstance(prio, int)
            assert 1 <= prio <= 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE HELPER METHODS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestDeterminerRayon:
    """Tests pour _determiner_rayon()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_determiner_rayon_tomate(self, mock_client):
        """Test dÃ©tection rayon fruits & lÃ©gumes."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        assert service._determiner_rayon("Tomate") == "Fruits & LÃ©gumes"
        assert service._determiner_rayon("Carotte fraÃ®che") == "Fruits & LÃ©gumes"

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_determiner_rayon_viande(self, mock_client):
        """Test dÃ©tection rayon boucherie."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        assert service._determiner_rayon("Poulet fermier") == "Boucherie"
        assert service._determiner_rayon("Steak hachÃ©") == "Boucherie"

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_determiner_rayon_inconnu(self, mock_client):
        """Test rayon par dÃ©faut pour ingrÃ©dient inconnu."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        assert service._determiner_rayon("Truffe blanche") == "Autre"
        assert service._determiner_rayon("Ã‰pice rare") == "Autre"


@pytest.mark.unit
class TestDeterminerPriorite:
    """Tests pour _determiner_priorite()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_determiner_priorite_cremerie(self, mock_client):
        """Test prioritÃ© crÃ¨merie (produits frais = haute prioritÃ©)."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        prio = service._determiner_priorite("CrÃ¨merie")
        assert isinstance(prio, int)

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_determiner_priorite_rayon_inconnu(self, mock_client):
        """Test prioritÃ© pour rayon inconnu = 3."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        prio = service._determiner_priorite("RayonInexistant")
        assert prio == 3  # PrioritÃ© par dÃ©faut


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS COMPARER AVEC STOCK
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestComparerAvecStock:
    """Tests pour comparer_avec_stock()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_comparer_rien_en_stock(self, mock_client):
        """Test quand rien n'est en stock."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        articles = [
            ArticleCourse(nom="Tomate", quantite=5),
            ArticleCourse(nom="Oignon", quantite=3)
        ]
        stock = {}
        
        result = service.comparer_avec_stock(articles, stock)
        
        assert len(result) == 2
        assert result[0].a_acheter == 5
        assert result[1].a_acheter == 3

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_comparer_stock_partiel(self, mock_client):
        """Test avec stock partiel."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        articles = [
            ArticleCourse(nom="Tomate", quantite=5),
            ArticleCourse(nom="Oignon", quantite=3)
        ]
        stock = {"tomate": 2.0}
        
        result = service.comparer_avec_stock(articles, stock)
        
        # Tomate: 5 - 2 = 3 Ã  acheter
        # Oignon: 3 - 0 = 3 Ã  acheter
        tomate = next(a for a in result if a.nom.lower() == "tomate")
        assert tomate.en_stock == 2.0
        assert tomate.a_acheter == 3.0

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_comparer_stock_suffisant(self, mock_client):
        """Test quand stock suffisant (article retirÃ©)."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        articles = [
            ArticleCourse(nom="Tomate", quantite=5),
            ArticleCourse(nom="Sel", quantite=1)  # En stock
        ]
        stock = {"sel": 10.0}  # Suffisant
        
        result = service.comparer_avec_stock(articles, stock)
        
        # Sel non inclus car stock suffisant
        noms = [a.nom.lower() for a in result]
        assert "sel" not in noms
        assert "tomate" in noms


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EXTRAIRE INGREDIENTS PLANNING
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestExtraireIngredientsPlanning:
    """Tests pour extraire_ingredients_planning()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_extraire_planning_vide(self, mock_client):
        """Test extraction planning sans repas."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        # Mock planning vide
        mock_planning = Mock()
        mock_planning.repas = []
        
        result = service.extraire_ingredients_planning(mock_planning)
        
        assert result == []

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_extraire_planning_repas_sans_recette(self, mock_client):
        """Test extraction avec repas sans recette."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        # Mock repas sans recette
        mock_repas = Mock()
        mock_repas.recette = None
        
        mock_planning = Mock()
        mock_planning.repas = [mock_repas]
        
        result = service.extraire_ingredients_planning(mock_planning)
        
        assert result == []

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_extraire_planning_avec_ingredients(self, mock_client):
        """Test extraction avec ingrÃ©dients."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        # Mock ingrÃ©dient
        mock_ingredient = Mock()
        mock_ingredient.nom = "Tomate"
        
        # Mock RecetteIngredient
        mock_ri = Mock()
        mock_ri.ingredient = mock_ingredient
        mock_ri.quantite = 3
        mock_ri.unite = "piÃ¨ces"
        
        # Mock recette
        mock_recette = Mock()
        mock_recette.nom = "Salade"
        mock_recette.ingredients = [mock_ri]
        
        # Mock repas
        mock_repas = Mock()
        mock_repas.recette = mock_recette
        
        # Mock planning
        mock_planning = Mock()
        mock_planning.repas = [mock_repas]
        
        result = service.extraire_ingredients_planning(mock_planning)
        
        assert len(result) == 1
        assert result[0].nom == "Tomate"
        assert result[0].quantite == 3
        assert "Salade" in result[0].recettes_source

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_extraire_planning_agregation_meme_ingredient(self, mock_client):
        """Test agrÃ©gation du mÃªme ingrÃ©dient dans plusieurs recettes."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        # Mock mÃªme ingrÃ©dient dans 2 recettes
        mock_ingredient = Mock()
        mock_ingredient.nom = "Oignon"
        
        mock_ri1 = Mock()
        mock_ri1.ingredient = mock_ingredient
        mock_ri1.quantite = 2
        mock_ri1.unite = "piÃ¨ces"
        
        mock_ri2 = Mock()
        mock_ri2.ingredient = mock_ingredient
        mock_ri2.quantite = 1
        mock_ri2.unite = "piÃ¨ces"
        
        mock_recette1 = Mock()
        mock_recette1.nom = "Soupe"
        mock_recette1.ingredients = [mock_ri1]
        
        mock_recette2 = Mock()
        mock_recette2.nom = "Omelette"
        mock_recette2.ingredients = [mock_ri2]
        
        mock_repas1 = Mock()
        mock_repas1.recette = mock_recette1
        
        mock_repas2 = Mock()
        mock_repas2.recette = mock_recette2
        
        mock_planning = Mock()
        mock_planning.repas = [mock_repas1, mock_repas2]
        
        result = service.extraire_ingredients_planning(mock_planning)
        
        # Les quantitÃ©s sont agrÃ©gÃ©es
        assert len(result) == 1
        assert result[0].nom == "Oignon"
        assert result[0].quantite == 3  # 2 + 1
        assert len(result[0].recettes_source) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE INIT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestCoursesIntelligentesServiceInit:
    """Tests pour l'initialisation du service."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_init_success(self, mock_client):
        """Test initialisation rÃ©ussie."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        assert service is not None
        assert service.cache_prefix == "courses_intel"

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_init_no_client_raises(self, mock_client):
        """Test erreur si client IA non disponible."""
        mock_client.return_value = None
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        with pytest.raises(RuntimeError, match="Client IA non disponible"):
            CoursesIntelligentesService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FACTORY FUNCTION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestFactoryFunction:
    """Tests pour get_courses_intelligentes_service()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_get_service(self, mock_client):
        """Test factory retourne service."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import get_courses_intelligentes_service
        
        service = get_courses_intelligentes_service()
        
        assert service is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULE EXPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestModuleExports:
    """Tests pour les exports du module."""

    def test_article_course_exported(self):
        """Test ArticleCourse exportÃ©."""
        from src.services.courses_intelligentes import ArticleCourse
        assert ArticleCourse is not None

    def test_liste_courses_intelligente_exported(self):
        """Test ListeCoursesIntelligente exportÃ©."""
        from src.services.courses_intelligentes import ListeCoursesIntelligente
        assert ListeCoursesIntelligente is not None

    def test_suggestion_substitution_exported(self):
        """Test SuggestionSubstitution exportÃ©."""
        from src.services.courses_intelligentes import SuggestionSubstitution
        assert SuggestionSubstitution is not None

    def test_service_class_exported(self):
        """Test CoursesIntelligentesService exportÃ©."""
        from src.services.courses_intelligentes import CoursesIntelligentesService
        assert CoursesIntelligentesService is not None

    def test_mapping_rayons_exported(self):
        """Test MAPPING_RAYONS exportÃ©."""
        from src.services.courses_intelligentes import MAPPING_RAYONS
        assert MAPPING_RAYONS is not None

    def test_priorites_exported(self):
        """Test PRIORITES exportÃ©."""
        from src.services.courses_intelligentes import PRIORITES
        assert PRIORITES is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GENERER LISTE COURSES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestGenererListeCourses:
    """Tests pour generer_liste_courses()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_generer_sans_planning(self, mock_client):
        """Test gÃ©nÃ©ration sans planning actif."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        service.obtenir_planning_actif = Mock(return_value=None)
        
        result = service.generer_liste_courses()
        
        assert len(result.alertes) == 1
        assert "Aucun planning actif" in result.alertes[0]

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_generer_planning_sans_recettes(self, mock_client):
        """Test gÃ©nÃ©ration avec planning mais sans recettes."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        mock_planning = Mock()
        mock_planning.repas = []
        
        service.obtenir_planning_actif = Mock(return_value=mock_planning)
        service.extraire_ingredients_planning = Mock(return_value=[])
        
        result = service.generer_liste_courses()
        
        assert len(result.alertes) == 1
        assert "Aucune recette" in result.alertes[0]

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_generer_avec_stock_complet(self, mock_client):
        """Test gÃ©nÃ©ration quand tout est en stock."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        mock_planning = Mock()
        articles = [ArticleCourse(nom="Sel", quantite=1)]
        
        service.obtenir_planning_actif = Mock(return_value=mock_planning)
        service.extraire_ingredients_planning = Mock(return_value=articles)
        service.obtenir_stock_actuel = Mock(return_value={"sel": 100})
        service.comparer_avec_stock = Mock(return_value=[])
        
        result = service.generer_liste_courses()
        
        assert any("en stock" in a for a in result.alertes)

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_generer_inventaire_vide(self, mock_client):
        """Test gÃ©nÃ©ration avec inventaire vide."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        mock_planning = Mock()
        articles = [
            ArticleCourse(nom="Tomate", quantite=5, a_acheter=5),
            ArticleCourse(nom="Oignon", quantite=3, a_acheter=3)
        ]
        
        service.obtenir_planning_actif = Mock(return_value=mock_planning)
        service.extraire_ingredients_planning = Mock(return_value=articles)
        service.obtenir_stock_actuel = Mock(return_value={})
        service.comparer_avec_stock = Mock(return_value=articles)
        
        result = service.generer_liste_courses()
        
        assert any("Inventaire vide" in a for a in result.alertes)
        assert result.total_articles == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS AJOUTER A LISTE COURSES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit  
class TestAjouterAListeCourses:
    """Tests pour ajouter_a_liste_courses()."""

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_ajouter_nouvel_article(self, mock_client):
        """Test ajout nouvel article."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        # Mock session
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Articles Ã  ajouter
        articles = [
            ArticleCourse(nom="Banane", quantite=6, a_acheter=6, rayon="Fruits & LÃ©gumes")
        ]
        
        # Mock l'ingrÃ©dient crÃ©Ã©
        mock_ingredient = Mock()
        mock_ingredient.id = 1
        
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            None,  # Pas d'ingrÃ©dient existant
            None   # Pas d'article courses existant
        ]
        
        result = service.ajouter_a_liste_courses(articles, db=mock_session)
        
        # VÃ©rifie qu'on a essayÃ© d'ajouter
        assert mock_session.add.called

    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    def test_ajouter_vide(self, mock_client):
        """Test ajout liste vide."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        mock_session = MagicMock()
        
        result = service.ajouter_a_liste_courses([], db=mock_session)
        
        assert result == []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SUGGERER SUBSTITUTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestSuggererSubstitutions:
    """Tests pour suggerer_substitutions()."""

    @pytest.mark.asyncio
    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    async def test_suggerer_liste_vide(self, mock_client):
        """Test suggestion sur liste vide."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import CoursesIntelligentesService
        
        service = CoursesIntelligentesService()
        
        result = await service.suggerer_substitutions([])
        
        assert result == []

    @pytest.mark.asyncio
    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    async def test_suggerer_priorite_basse_only(self, mock_client):
        """Test avec uniquement articles prioritÃ© basse (ignorÃ©s)."""
        mock_client.return_value = Mock()
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        articles = [
            ArticleCourse(nom="Sel", quantite=1, priorite=3),
            ArticleCourse(nom="Poivre", quantite=1, priorite=3)
        ]
        
        result = await service.suggerer_substitutions(articles)
        
        # PrioritÃ© 3 => non Ã©valuÃ©
        assert result == []

    @pytest.mark.asyncio 
    @patch('src.services.courses_intelligentes.obtenir_client_ia')
    async def test_suggerer_avec_reponse_valide(self, mock_client):
        """Test avec rÃ©ponse IA valide."""
        mock_ia = Mock()
        mock_ia.appeler = Mock(return_value='[{"ingredient_original": "Beurre", "suggestion": "Margarine", "raison": "Moins cher"}]')
        mock_client.return_value = mock_ia
        
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        service.client = mock_ia
        
        # Mock async appeler
        import asyncio
        async def mock_appeler(*args):
            return '[{"ingredient_original": "Beurre", "suggestion": "Margarine", "raison": "Moins cher"}]'
        
        service.client.appeler = mock_appeler
          
        articles = [
            ArticleCourse(nom="Beurre", quantite=1, priorite=1)
        ]
        
        result = await service.suggerer_substitutions(articles)
        
        assert len(result) == 1
        assert result[0].ingredient_original == "Beurre"
        assert result[0].suggestion == "Margarine"

    @pytest.mark.asyncio
    @patch('src.services.courses_intelligentes.obtenir_client_ia') 
    async def test_suggerer_erreur_json(self, mock_client):
        """Test avec rÃ©ponse IA invalide."""
        mock_ia = Mock()
        mock_client.return_value = mock_ia
        
        from src.services.courses_intelligentes import (
            CoursesIntelligentesService, ArticleCourse
        )
        
        service = CoursesIntelligentesService()
        
        async def mock_appeler(*args):
            return "pas du json valide"
        
        service.client.appeler = mock_appeler
        
        articles = [
            ArticleCourse(nom="Truffe", quantite=1, priorite=1)
        ]
        
        result = await service.suggerer_substitutions(articles)
        
        # Erreur attrapÃ©e, retourne vide
        assert result == []
