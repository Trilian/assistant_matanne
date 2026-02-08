"""
Tests pour les méthodes de PDFExportService qui utilisent la base de données.

Ces tests ciblent les lignes non couvertes (121-151, 229-267, 330-354) en mockant
obtenir_contexte_db correctement.
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from io import BytesIO
from datetime import datetime, timedelta, date


# ═══════════════════════════════════════════════════════════
# FIXTURES - Mock Models
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_recette():
    """Crée un mock de Recette avec tous les attributs."""
    recette = MagicMock()
    recette.id = 1
    recette.nom = "Tarte aux pommes"
    recette.description = "Une délicieuse tarte"
    recette.temps_preparation = 30
    recette.temps_cuisson = 45
    recette.difficulte = "moyen"
    recette.portions = 6
    recette.calories = 350
    recette.instructions = "Étape 1: Préparer la pâte\\nÉtape 2: Couper les pommes\\nÉtape 3: Cuire au four"
    
    # Ingrédients
    ingredient1 = MagicMock()
    ingredient1.nom = "Pommes"
    ingredient1.quantite = 500
    ingredient1.unite = "g"
    
    ingredient2 = MagicMock()
    ingredient2.nom = "Beurre"
    ingredient2.quantite = 100
    ingredient2.unite = "g"
    
    ingredient3 = MagicMock()
    ingredient3.nom = "Sucre"
    ingredient3.quantite = 150
    ingredient3.unite = "g"
    
    recette.ingredients = [ingredient1, ingredient2, ingredient3]
    
    # Étapes
    etape1 = MagicMock()
    etape1.ordre = 1
    etape1.description = "Préparer la pâte"
    
    etape2 = MagicMock()
    etape2.ordre = 2
    etape2.description = "Couper les pommes"
    
    etape3 = MagicMock()
    etape3.ordre = 3
    etape3.description = "Enfourner 45 minutes"
    
    recette.etapes = [etape1, etape2, etape3]
    
    return recette


@pytest.fixture
def mock_recette_minimal():
    """Crée un mock de Recette avec attributs minimaux."""
    recette = MagicMock()
    recette.id = 2
    recette.nom = "Recette simple"
    recette.description = None
    recette.temps_preparation = None
    recette.temps_cuisson = None
    recette.difficulte = None
    recette.portions = None
    recette.calories = None
    recette.instructions = None
    recette.ingredients = []
    recette.etapes = []
    
    return recette


@pytest.fixture
def mock_planning():
    """Crée un mock de Planning avec repas."""
    planning = MagicMock()
    planning.id = 1
    planning.nom = "Menu Semaine"
    
    # Repas avec dates
    today = datetime.now().date() - timedelta(days=datetime.now().weekday())
    
    # Repas lundi
    repas1 = MagicMock()
    repas1.date = today
    repas1.type_repas = "déjeuner"
    repas1.notes = "Léger"
    repas1.recette = MagicMock()
    repas1.recette.nom = "Salade composée"
    
    # Repas mardi
    repas2 = MagicMock()
    repas2.date = today + timedelta(days=1)
    repas2.type_repas = "dîner"
    repas2.notes = ""
    repas2.recette = MagicMock()
    repas2.recette.nom = "Pâtes carbonara"
    
    # Repas vendredi
    repas3 = MagicMock()
    repas3.date = today + timedelta(days=4)
    repas3.type_repas = "déjeuner"
    repas3.notes = "En famille"
    repas3.recette = None  # Cas recette non définie
    
    planning.repas = [repas1, repas2, repas3]
    
    return planning


@pytest.fixture
def mock_planning_vide():
    """Crée un mock de Planning sans repas."""
    planning = MagicMock()
    planning.id = 2
    planning.nom = None  # Pas de nom
    planning.repas = []
    
    return planning


@pytest.fixture
def mock_articles_courses():
    """Crée des mocks d'ArticleCourses."""
    article1 = MagicMock()
    article1.nom = "Tomates"
    article1.quantite = 500
    article1.unite = "g"
    article1.categorie = "fruits_legumes"
    article1.urgent = True
    article1.achete = False
    
    article2 = MagicMock()
    article2.nom = "Lait"
    article2.quantite = 1
    article2.unite = "L"
    article2.categorie = "produits_laitiers"
    article2.urgent = False
    article2.achete = False
    
    article3 = MagicMock()
    article3.nom = "Pain"
    article3.quantite = 2
    article3.unite = ""
    article3.categorie = "boulangerie"
    article3.urgent = False
    article3.achete = False
    
    article4 = MagicMock()
    article4.nom = "Article divers"
    article4.quantite = None
    article4.unite = None
    article4.categorie = None  # Pas de catégorie
    article4.urgent = None
    article4.achete = False
    
    return [article1, article2, article3, article4]


# ═══════════════════════════════════════════════════════════
# TESTS - exporter_recette (lignes 121-151)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExporterRecetteDB:
    """Tests pour exporter_recette avec mocks de base de données."""

    def test_exporter_recette_succes(self, mock_recette):
        """Test export recette avec données complètes."""
        from src.services.pdf_export import PDFExportService
        
        # Configuration du mock de session
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_recette
        
        # Mock du context manager
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_recette(1)
        
        assert result is not None
        # Vérifie que la requête a été faite
        mock_session.query.assert_called()

    def test_exporter_recette_non_trouve(self):
        """Test export recette qui n'existe pas - retourne None (decorator catches)."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # Recette non trouvée
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            # Le decorator @with_error_handling() attrape l'exception et retourne None
            result = service.exporter_recette(999)
            assert result is None

    def test_exporter_recette_sans_etapes(self, mock_recette_minimal):
        """Test export recette sans étapes."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_recette_minimal
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_recette(2)
        
        assert result is not None

    def test_exporter_recette_avec_instructions_fallback(self):
        """Test recette utilisant instructions comme fallback pour étapes."""
        from src.services.pdf_export import PDFExportService
        
        recette = MagicMock()
        recette.id = 3
        recette.nom = "Recette avec instructions"
        recette.description = "Description"
        recette.temps_preparation = 15
        recette.temps_cuisson = 30
        recette.difficulte = "facile"
        recette.portions = 4
        recette.calories = 200
        recette.instructions = "Étape 1\\nÉtape 2\\nÉtape 3"
        recette.ingredients = []
        recette.etapes = []  # Pas d'étapes définies
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = recette
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_recette(3)
        
        assert result is not None

    def test_exporter_recette_metadata_complete(self, mock_recette):
        """Test recette avec toutes les métadonnées."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_recette
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_recette(1)
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        # Vérifier que c'est un PDF valide (commence par %PDF)
        content = result.read(4)
        assert content == b'%PDF'


# ═══════════════════════════════════════════════════════════
# TESTS - exporter_planning_semaine (lignes 229-267)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExporterPlanningSemaineDB:
    """Tests pour exporter_planning_semaine avec mocks de base de données."""

    def test_exporter_planning_succes(self, mock_planning):
        """Test export planning avec repas."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_planning
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_planning_semaine(1)
        
        assert result is not None
        mock_session.query.assert_called()

    def test_exporter_planning_non_trouve(self):
        """Test export planning qui n'existe pas - retourne None (decorator catches)."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            # Le decorator @with_error_handling() attrape l'exception et retourne None
            result = service.exporter_planning_semaine(999)
            assert result is None

    def test_exporter_planning_vide(self, mock_planning_vide):
        """Test export planning sans repas."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_planning_vide
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_planning_semaine(2)
        
        assert result is not None

    def test_exporter_planning_avec_date_specifique(self, mock_planning):
        """Test export planning avec date de début spécifiée."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_planning
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        # Date spécifique
        date_debut = datetime(2024, 1, 15)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_planning_semaine(1, date_debut=date_debut)
        
        assert result is not None

    def test_exporter_planning_repas_hors_periode(self):
        """Test export planning avec repas hors de la période."""
        from src.services.pdf_export import PDFExportService
        
        planning = MagicMock()
        planning.id = 3
        planning.nom = "Planning"
        
        # Repas hors période (il y a un mois)
        repas = MagicMock()
        repas.date = date.today() - timedelta(days=30)
        repas.type_repas = "déjeuner"
        repas.notes = ""
        repas.recette = MagicMock()
        repas.recette.nom = "Vieille recette"
        
        planning.repas = [repas]
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = planning
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_planning_semaine(3)
        
        # Devrait réussir même si aucun repas dans la période
        assert result is not None

    def test_exporter_planning_repas_sans_date(self):
        """Test export planning avec repas sans date."""
        from src.services.pdf_export import PDFExportService
        
        planning = MagicMock()
        planning.id = 4
        planning.nom = "Planning sans dates"
        
        repas = MagicMock()
        repas.date = None  # Pas de date
        repas.type_repas = "déjeuner"
        repas.notes = ""
        repas.recette = MagicMock()
        repas.recette.nom = "Recette"
        
        planning.repas = [repas]
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = planning
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_planning_semaine(4)
        
        assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS - exporter_liste_courses (lignes 330-354)
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExporterListeCoursesDB:
    """Tests pour exporter_liste_courses avec mocks de base de données."""

    def test_exporter_liste_courses_succes(self, mock_articles_courses):
        """Test export liste courses avec articles."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_articles_courses
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        # Mock the ArticleCourses class with proper column descriptors
        mock_article_model = MagicMock()
        mock_article_model.achete = MagicMock()
        mock_article_model.categorie = MagicMock()
        mock_article_model.nom = MagicMock()
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context), \
             patch('src.services.pdf_export.ArticleCourses', mock_article_model):
            service = PDFExportService()
            result = service.exporter_liste_courses()
        
        assert result is not None
        mock_session.query.assert_called()

    def test_exporter_liste_courses_vide(self):
        """Test export liste courses vide."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []  # Aucun article
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        mock_article_model = MagicMock()
        mock_article_model.achete = MagicMock()
        mock_article_model.categorie = MagicMock()
        mock_article_model.nom = MagicMock()
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context), \
             patch('src.services.pdf_export.ArticleCourses', mock_article_model):
            service = PDFExportService()
            result = service.exporter_liste_courses()
        
        assert result is not None

    def test_exporter_liste_courses_urgents(self):
        """Test export liste avec articles urgents."""
        from src.services.pdf_export import PDFExportService
        
        article_urgent = MagicMock()
        article_urgent.nom = "Article urgent"
        article_urgent.quantite = 1
        article_urgent.unite = ""
        article_urgent.categorie = "urgent_cat"
        article_urgent.urgent = True
        article_urgent.achete = False
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [article_urgent]
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        mock_article_model = MagicMock()
        mock_article_model.achete = MagicMock()
        mock_article_model.categorie = MagicMock()
        mock_article_model.nom = MagicMock()
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context), \
             patch('src.services.pdf_export.ArticleCourses', mock_article_model):
            service = PDFExportService()
            result = service.exporter_liste_courses()
        
        assert result is not None

    def test_exporter_liste_courses_categories_multiples(self, mock_articles_courses):
        """Test export liste avec plusieurs catégories."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_articles_courses
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        mock_article_model = MagicMock()
        mock_article_model.achete = MagicMock()
        mock_article_model.categorie = MagicMock()
        mock_article_model.nom = MagicMock()
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context), \
             patch('src.services.pdf_export.ArticleCourses', mock_article_model):
            service = PDFExportService()
            result = service.exporter_liste_courses()
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        # Vérifier que c'est un PDF valide
        content = result.read(4)
        assert content == b'%PDF'

    def test_exporter_liste_courses_attributs_none(self):
        """Test export liste avec attributs None."""
        from src.services.pdf_export import PDFExportService
        
        article = MagicMock()
        article.nom = "Article basique"
        article.quantite = None
        article.unite = None
        article.categorie = None
        article.urgent = None
        article.achete = False
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [article]
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        mock_article_model = MagicMock()
        mock_article_model.achete = MagicMock()
        mock_article_model.categorie = MagicMock()
        mock_article_model.nom = MagicMock()
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context), \
             patch('src.services.pdf_export.ArticleCourses', mock_article_model):
            service = PDFExportService()
            result = service.exporter_liste_courses()
        
        assert result is not None


# ═══════════════════════════════════════════════════════════
# TESTS - Cas d'erreur et exceptions
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExporterDBErrors:
    """Tests pour les cas d'erreur - le decorator attrape et retourne None."""

    def test_exporter_recette_db_error(self):
        """Test erreur de base de données lors de l'export recette."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("DB connection error")
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            # Le decorator attrape l'exception et retourne None
            result = service.exporter_recette(1)
            assert result is None

    def test_exporter_planning_db_error(self):
        """Test erreur de base de données lors de l'export planning."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("DB timeout")
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            # Le decorator attrape l'exception et retourne None
            result = service.exporter_planning_semaine(1)
            assert result is None

    def test_exporter_liste_courses_db_error(self):
        """Test erreur de base de données lors de l'export liste courses."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_session.query.side_effect = Exception("Database unavailable")
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            # Le decorator attrape l'exception et retourne None
            result = service.exporter_liste_courses()
            assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS - Integration complète
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestExporterIntegration:
    """Tests d'intégration vérifiant le flux complet."""

    def test_flux_complet_export_recette(self, mock_recette):
        """Test du flux complet pour exporter une recette."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_recette
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_recette(1)
        
        # Vérifications
        assert isinstance(result, BytesIO)
        result.seek(0)
        pdf_content = result.read()
        
        # PDF valide commence par %PDF
        assert pdf_content[:4] == b'%PDF'
        # PDF valide termine par %%EOF (avec possible whitespace)
        assert b'%%EOF' in pdf_content[-20:]

    def test_flux_complet_export_planning(self, mock_planning):
        """Test du flux complet pour exporter un planning."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.options.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_planning
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context):
            service = PDFExportService()
            result = service.exporter_planning_semaine(1)
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        pdf_content = result.read()
        assert pdf_content[:4] == b'%PDF'

    def test_flux_complet_export_courses(self, mock_articles_courses):
        """Test du flux complet pour exporter une liste de courses."""
        from src.services.pdf_export import PDFExportService
        
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_articles_courses
        
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=False)
        
        mock_article_model = MagicMock()
        mock_article_model.achete = MagicMock()
        mock_article_model.categorie = MagicMock()
        mock_article_model.nom = MagicMock()
        
        with patch('src.services.pdf_export.obtenir_contexte_db', return_value=mock_context), \
             patch('src.services.pdf_export.ArticleCourses', mock_article_model):
            service = PDFExportService()
            result = service.exporter_liste_courses()
        
        assert isinstance(result, BytesIO)
        result.seek(0)
        pdf_content = result.read()
        assert pdf_content[:4] == b'%PDF'
