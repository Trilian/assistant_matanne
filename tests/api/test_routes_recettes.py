"""
Tests pour src/api/routes/recettes.py

Tests unitaires avec vraies données pour les routes recettes.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST RÉELLES
# ═══════════════════════════════════════════════════════════


RECETTES_TEST = [
    {
        "id": 1,
        "nom": "Tarte aux pommes",
        "description": "Tarte classique française aux pommes",
        "temps_preparation": 30,
        "temps_cuisson": 45,
        "portions": 8,
        "difficulte": "moyen",
        "categorie": "Dessert",
        "created_at": datetime(2026, 1, 1, 10, 0),
        "updated_at": None,
    },
    {
        "id": 2,
        "nom": "Poulet rôti",
        "description": "Poulet rôti au four avec herbes",
        "temps_preparation": 15,
        "temps_cuisson": 90,
        "portions": 4,
        "difficulte": "facile",
        "categorie": "Plat",
        "created_at": datetime(2026, 1, 2, 12, 0),
        "updated_at": None,
    },
    {
        "id": 3,
        "nom": "Soupe de légumes",
        "description": "Soupe aux légumes de saison",
        "temps_preparation": 20,
        "temps_cuisson": 30,
        "portions": 6,
        "difficulte": "facile",
        "categorie": "Entrée",
        "created_at": datetime(2026, 1, 3, 18, 0),
        "updated_at": None,
    },
]

RECETTE_NOUVELLE = {
    "nom": "Quiche lorraine",
    "description": "Quiche traditionnelle aux lardons",
    "temps_preparation": 25,
    "temps_cuisson": 35,
    "portions": 6,
    "difficulte": "moyen",
    "categorie": "Plat",
}


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app)


def creer_mock_recette(data: dict) -> MagicMock:
    """Crée un mock de recette avec les données."""
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS SCHÉMAS
# ═══════════════════════════════════════════════════════════


class TestSchemasRecettes:
    """Tests des schémas Pydantic."""

    def test_recette_base_creation(self):
        """RecetteBase valide."""
        from src.api.routes.recettes import RecetteBase

        recette = RecetteBase(nom="Test recette")

        assert recette.nom == "Test recette"
        assert recette.temps_preparation == 15  # défaut
        assert recette.temps_cuisson == 0  # défaut
        assert recette.portions == 4  # défaut

    def test_recette_base_nom_vide_rejete(self):
        """Nom vide est rejeté."""
        from pydantic import ValidationError

        from src.api.routes.recettes import RecetteBase

        with pytest.raises(ValidationError):
            RecetteBase(nom="")

    def test_recette_base_nom_strip(self):
        """Le nom est nettoyé des espaces."""
        from src.api.routes.recettes import RecetteBase

        recette = RecetteBase(nom="  Ma recette  ")

        assert recette.nom == "Ma recette"

    def test_recette_create_avec_ingredients(self):
        """RecetteCreate accepte les ingrédients."""
        from src.api.routes.recettes import RecetteCreate

        recette = RecetteCreate(
            nom="Test",
            ingredients=[{"nom": "Farine", "quantite": 200, "unite": "g"}],
            instructions=["Mélanger", "Cuire"],
        )

        assert len(recette.ingredients) == 1
        assert len(recette.instructions) == 2

    def test_recette_response_validation(self):
        """RecetteResponse valide les données."""
        from src.api.routes.recettes import RecetteResponse

        data = RECETTES_TEST[0].copy()
        recette = RecetteResponse(**data)

        assert recette.id == 1
        assert recette.nom == "Tarte aux pommes"
        assert recette.categorie == "Dessert"


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES CRUD
# ═══════════════════════════════════════════════════════════


class TestRoutesRecettesCRUD:
    """Tests CRUD des routes recettes."""

    def test_lister_recettes_endpoint_existe(self, client):
        """GET /api/v1/recettes existe."""
        response = client.get("/api/v1/recettes")
        # 200 ou 500 (si pas de BD) mais pas 404
        assert response.status_code in (200, 500)

    def test_obtenir_recette_endpoint_existe(self, client):
        """GET /api/v1/recettes/{id} existe."""
        response = client.get("/api/v1/recettes/999999")
        # 404, 200 ou 500 - endpoint existe
        assert response.status_code in (200, 404, 500)

    def test_creer_recette_endpoint_existe(self, client):
        """POST /api/v1/recettes existe."""
        response = client.post("/api/v1/recettes", json=RECETTE_NOUVELLE)
        # 200 ou 500, pas 404
        assert response.status_code in (200, 500)

    def test_supprimer_recette_endpoint_existe(self, client):
        """DELETE /api/v1/recettes/{id} existe."""
        response = client.delete("/api/v1/recettes/999999")
        # 404, 200 ou 500
        assert response.status_code in (200, 404, 500)


# ═══════════════════════════════════════════════════════════
# TESTS AVEC MOCK BD
# ═══════════════════════════════════════════════════════════


class TestRoutesRecettesAvecMock:
    """Tests avec mock de la base de données."""

    def test_lister_recettes_retourne_liste(self):
        """Liste des recettes retourne format correct."""
        # Setup mocks
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=None)

        mock_recettes = [creer_mock_recette(r) for r in RECETTES_TEST]

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = len(mock_recettes)
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_recettes
        mock_session.query.return_value = mock_query

        with patch("src.core.db.obtenir_contexte_db", return_value=mock_context):
            from src.api.main import app

            client = TestClient(app)

            response = client.get("/api/v1/recettes")

        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["items"]) == 3

    def test_obtenir_recette_par_id_existe(self):
        """GET /api/v1/recettes/{id} retourne la recette."""
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=None)

        mock_recette = creer_mock_recette(RECETTES_TEST[0])

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_recette
        mock_session.query.return_value = mock_query

        with patch("src.core.db.obtenir_contexte_db", return_value=mock_context):
            from src.api.main import app

            client = TestClient(app)

            response = client.get("/api/v1/recettes/1")

        assert response.status_code == 200
        data = response.json()

        assert data["nom"] == "Tarte aux pommes"
        assert data["categorie"] == "Dessert"

    def test_obtenir_recette_non_trouvee(self):
        """GET /api/v1/recettes/{id} retourne 404 si inexistante."""
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=None)

        mock_query = MagicMock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_session.query.return_value = mock_query

        with patch("src.core.db.obtenir_contexte_db", return_value=mock_context):
            from src.api.main import app

            client = TestClient(app)

            response = client.get("/api/v1/recettes/999999")

        assert response.status_code == 404

    def test_creer_recette_succes(self):
        """POST /api/v1/recettes crée une recette."""
        mock_session = MagicMock()
        mock_context = MagicMock()
        mock_context.__enter__ = MagicMock(return_value=mock_session)
        mock_context.__exit__ = MagicMock(return_value=None)

        mock_recette = creer_mock_recette(
            {
                **RECETTE_NOUVELLE,
                "id": 4,
                "created_at": datetime.now(),
                "updated_at": None,
            }
        )

        def fake_refresh(obj):
            obj.id = 4
            obj.created_at = datetime.now()
            obj.updated_at = None

        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh.side_effect = fake_refresh

        with patch("src.core.db.obtenir_contexte_db", return_value=mock_context):
            from src.api.main import app

            client = TestClient(app)

            response = client.post("/api/v1/recettes", json=RECETTE_NOUVELLE)

        # Vérifie que add et commit ont été appelés
        assert mock_session.add.called
        assert mock_session.commit.called


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidationRecettes:
    """Tests de validation des données."""

    def test_creer_recette_nom_vide_echoue(self, client):
        """POST avec nom vide échoue avec 422."""
        response = client.post(
            "/api/v1/recettes",
            json={
                "nom": "",
                "description": "Test",
            },
        )

        assert response.status_code == 422

    def test_creer_recette_temps_negatif_echoue(self, client):
        """POST avec temps négatif échoue."""
        response = client.post(
            "/api/v1/recettes",
            json={
                "nom": "Test",
                "temps_preparation": -10,
            },
        )

        assert response.status_code == 422

    def test_creer_recette_portions_zero_echoue(self, client):
        """POST avec 0 portions échoue."""
        response = client.post(
            "/api/v1/recettes",
            json={
                "nom": "Test",
                "portions": 0,
            },
        )

        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════
# TESTS PAGINATION
# ═══════════════════════════════════════════════════════════


class TestPaginationRecettes:
    """Tests de la pagination."""

    def test_pagination_parametres_invalides(self, client):
        """Page < 1 échoue avec 422."""
        response = client.get("/api/v1/recettes?page=0")
        assert response.status_code == 422

    def test_page_size_trop_grand(self, client):
        """page_size > 100 échoue."""
        response = client.get("/api/v1/recettes?page_size=200")
        assert response.status_code == 422
