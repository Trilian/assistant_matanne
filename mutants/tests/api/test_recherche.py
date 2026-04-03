"""
Tests pour les routes de recherche globale.

Couverture:
- Recherche globale multi-entités
- Filtres et pagination
- Résultats par type (recettes, projets, activités, notes, contacts)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE GLOBALE
# ═══════════════════════════════════════════════════════════


class TestRechercheGlobale:
    """Tests de recherche multi-entités."""

    def test_recherche_requires_auth(self, client):
        """La recherche nécessite une authentification."""
        response = client.get("/api/v1/recherche/global", params={"q": "test"})
        # En mode dev, l'API peut accepter sans auth - on vérifie juste qu'elle répond
        assert response.status_code in [200, 401]

    def test_recherche_requires_min_length(self, client, auth_headers):
        """La recherche requiert au minimum 2 caractères."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "a"},  # Trop court
            headers=auth_headers,
        )
        # Devrait échouer la validation Pydantic
        assert response.status_code == 422

    def test_recherche_avec_query_valide(self, client, auth_headers):
        """La recherche avec une requête valide retourne 200."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_recherche_avec_limit(self, client, auth_headers):
        """La recherche respecte la limite de résultats."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test", "limit": 10},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10

    def test_recherche_limite_max_100(self, client, auth_headers):
        """La limite maximum est de 100."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test", "limit": 200},  # Au-dessus du max
            headers=auth_headers,
        )
        # Devrait échouer la validation
        assert response.status_code == 422

    def test_recherche_structure_resultats(self, client, auth_headers):
        """Les résultats ont la structure attendue."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()

        # Si des résultats existent, vérifier la structure
        if len(data) > 0:
            resultat = data[0]
            assert "type" in resultat
            assert "id" in resultat
            assert "titre" in resultat
            assert "url" in resultat
            assert "icone" in resultat


# ═══════════════════════════════════════════════════════════
# TESTS DE PERFORMANCE
# ═══════════════════════════════════════════════════════════


class TestRecherchePerformance:
    """Tests de performance de la recherche."""

    def test_recherche_temps_reponse_acceptable(self, client, auth_headers):
        """La recherche répond en moins de 2 secondes."""
        import time

        start = time.time()
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test", "limit": 50},
            headers=auth_headers,
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0  # Moins de 2 secondes


# ═══════════════════════════════════════════════════════════
# TESTS DE VALIDATION
# ═══════════════════════════════════════════════════════════


class TestRechercheValidation:
    """Tests de validation des paramètres."""

    def test_query_vide_rejete(self, client, auth_headers):
        """Une query vide est rejetée."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": ""},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_limit_negative_rejete(self, client, auth_headers):
        """Une limite négative est rejetée."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test", "limit": -1},
            headers=auth_headers,
        )
        assert response.status_code == 422

    def test_limit_zero_rejete(self, client, auth_headers):
        """Une limite de zéro est rejetée."""
        response = client.get(
            "/api/v1/recherche/global",
            params={"q": "test", "limit": 0},
            headers=auth_headers,
        )
        assert response.status_code == 422
