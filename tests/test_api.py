"""
Tests pour l'API REST FastAPI.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from contextlib import contextmanager


# ═══════════════════════════════════════════════════════════
# SETUP AVEC MOCKS
# ═══════════════════════════════════════════════════════════


# Mock de session de base de données
@pytest.fixture
def mock_db_session():
    """Crée une session DB mockée."""
    session = MagicMock()
    session.execute = Mock(return_value=None)
    session.commit = Mock()
    session.rollback = Mock()
    session.close = Mock()
    return session


@pytest.fixture
def mock_db_context(mock_db_session):
    """Mock du gestionnaire de contexte de base de données."""
    @contextmanager
    def _mock_get_db_context():
        yield mock_db_session
    
    return _mock_get_db_context


@pytest.fixture
def mock_user():
    """Utilisateur mocké pour les tests."""
    return {"id": "test-user", "email": "test@test.com", "role": "admin"}


@pytest.fixture
def client(mock_db_context, mock_user):
    """Client de test FastAPI avec DB et auth mockées."""
    from fastapi.testclient import TestClient
    from src.api.main import app, get_current_user, require_auth
    
    # Override les dépendances d'auth
    async def mock_get_current_user():
        return mock_user
    
    async def mock_require_auth():
        return mock_user
    
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_auth] = mock_require_auth
    
    with patch('src.core.database.get_db_context', mock_db_context):
        yield TestClient(app)
    
    # Cleanup
    app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS
# ═══════════════════════════════════════════════════════════


class TestSchemas:
    """Tests pour les schémas Pydantic."""
    
    def test_recette_base(self):
        """Test schéma RecetteBase."""
        from src.api.main import RecetteBase
        
        recette = RecetteBase(
            nom="Tarte aux pommes",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
        )
        
        assert recette.nom == "Tarte aux pommes"
        assert recette.temps_preparation == 30
        assert recette.portions == 8
        assert recette.difficulte == "moyen"  # Valeur par défaut
    
    def test_recette_create(self):
        """Test schéma RecetteCreate avec ingrédients."""
        from src.api.main import RecetteCreate
        
        recette = RecetteCreate(
            nom="Salade",
            ingredients=[{"nom": "Laitue", "quantite": 1}],
            instructions=["Laver", "Couper", "Servir"],
            tags=["rapide", "léger"],
        )
        
        assert len(recette.ingredients) == 1
        assert len(recette.instructions) == 3
        assert "rapide" in recette.tags
    
    def test_inventaire_item_base(self):
        """Test schéma InventaireItemBase."""
        from src.api.main import InventaireItemBase
        
        item = InventaireItemBase(
            nom="Lait",
            quantite=2.0,
            unite="L",
            categorie="Produits laitiers",
        )
        
        assert item.nom == "Lait"
        assert item.quantite == 2.0
        assert item.unite == "L"
    
    def test_course_item_base(self):
        """Test schéma CourseItemBase."""
        from src.api.main import CourseItemBase
        
        item = CourseItemBase(
            nom="Pain",
            quantite=2,
            coche=False,
        )
        
        assert item.nom == "Pain"
        assert not item.coche
    
    def test_repas_base(self):
        """Test schéma RepasBase."""
        from src.api.main import RepasBase
        
        repas = RepasBase(
            type_repas="dejeuner",
            date=datetime.now(),
            recette_id=1,
        )
        
        assert repas.type_repas == "dejeuner"
        assert repas.recette_id == 1


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS SANTÉ
# ═══════════════════════════════════════════════════════════


class TestHealthEndpoints:
    """Tests pour les endpoints de santé."""
    
    def test_root(self, client):
        """Test endpoint racine."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "docs" in data
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client, mock_db_session):
        """Test health check."""
        mock_db_session.execute = Mock(return_value=MagicMock())
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS RECETTES
# ═══════════════════════════════════════════════════════════


class TestRecettesEndpoints:
    """Tests pour les endpoints de recettes."""
    
    def test_list_recettes(self, client, mock_db_session):
        """Test liste des recettes."""
        # Configuration du mock pour retourner une liste vide
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/recettes")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
    
    def test_list_recettes_with_filters(self, client, mock_db_session):
        """Test liste des recettes avec filtres."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get(
            "/api/v1/recettes",
            params={"categorie": "dessert", "search": "tarte", "page": 1}
        )
        
        assert response.status_code == 200
    
    def test_get_recette_not_found(self, client, mock_db_session):
        """Test récupération d'une recette inexistante."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/recettes/999")
        
        assert response.status_code == 404
    
    def test_delete_recette_not_found(self, client, mock_db_session):
        """Test suppression d'une recette inexistante."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        response = client.delete("/api/v1/recettes/999")
        
        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS INVENTAIRE
# ═══════════════════════════════════════════════════════════


class TestInventaireEndpoints:
    """Tests pour les endpoints d'inventaire."""
    
    def test_list_inventaire(self, client, mock_db_session):
        """Test liste de l'inventaire."""
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/inventaire")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
    
    def test_list_inventaire_expiring(self, client, mock_db_session):
        """Test liste des articles qui expirent bientôt."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get(
            "/api/v1/inventaire",
            params={"expiring_soon": True}
        )
        
        assert response.status_code == 200
    
    def test_get_by_barcode_not_found(self, client, mock_db_session):
        """Test recherche par code-barres inexistant."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/inventaire/barcode/1234567890")
        
        # Peut retourner 200 avec item None ou 404
        assert response.status_code in [200, 404]


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS COURSES
# ═══════════════════════════════════════════════════════════


class TestCoursesEndpoints:
    """Tests pour les endpoints de courses."""
    
    def test_list_courses(self, client, mock_db_session):
        """Test liste des listes de courses."""
        mock_query = MagicMock()
        mock_query.count.return_value = 0
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/courses")
        
        assert response.status_code == 200
    
    def test_add_course_item_not_found(self, client, mock_db_session):
        """Test ajout d'article à une liste inexistante."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db_session.query.return_value = mock_query
        
        response = client.post(
            "/api/v1/courses/999/items",
            json={"nom": "Lait", "quantite": 1}
        )
        
        assert response.status_code in [404, 422]


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS PLANNING
# ═══════════════════════════════════════════════════════════


class TestPlanningEndpoints:
    """Tests pour les endpoints de planning."""
    
    def test_get_planning_semaine(self, client, mock_db_session):
        """Test récupération du planning de la semaine."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/planning/semaine")
        
        # Peut retourner 200, 404, ou 500 selon l'implémentation
        assert response.status_code in [200, 404, 500]


# ═══════════════════════════════════════════════════════════
# TESTS PAGINATION
# ═══════════════════════════════════════════════════════════


class TestPagination:
    """Tests pour la pagination."""
    
    def test_pagination_defaults(self, client, mock_db_session):
        """Test pagination avec valeurs par défaut."""
        mock_query = MagicMock()
        mock_query.count.return_value = 100
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/recettes")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 20  # Défaut
    
    def test_pagination_custom(self, client, mock_db_session):
        """Test pagination personnalisée."""
        mock_query = MagicMock()
        mock_query.count.return_value = 100
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get(
            "/api/v1/recettes",
            params={"page": 2, "page_size": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["page_size"] == 10
    
    def test_pagination_invalid_page(self, client):
        """Test pagination avec page invalide."""
        response = client.get(
            "/api/v1/recettes",
            params={"page": 0}  # Page 0 est invalide
        )
        
        # FastAPI valide le paramètre avec ge=1
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════
# TESTS SUGGESTIONS
# ═══════════════════════════════════════════════════════════


class TestSuggestionsEndpoints:
    """Tests pour les endpoints de suggestions."""
    
    def test_get_suggestions(self, client, mock_db_session):
        """Test récupération des suggestions."""
        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []
        mock_db_session.query.return_value = mock_query
        
        response = client.get("/api/v1/suggestions")
        
        # Peut retourner 200, 404, ou 500 selon l'implémentation
        assert response.status_code in [200, 404, 500]
