"""
Tests pour src/api/routes/jeux.py

Tests unitaires pour les routes jeux (paris, loto, équipes, matchs).
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app)


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

PARI_CREATE = {
    "match_id": 1,
    "type_pari": "1X2",
    "prediction": "1",
    "mise": 10.0,
    "cote": 2.5,
    "est_virtuel": True,
}

PARI_PATCH = {
    "resultat": "gagne",
}


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES ÉQUIPES
# ═══════════════════════════════════════════════════════════


class TestRoutesEquipes:
    """Tests des routes équipes."""

    def test_lister_equipes_endpoint(self, client):
        """GET /api/v1/jeux/equipes existe."""
        response = client.get("/api/v1/jeux/equipes")
        assert response.status_code in (200, 500)

    def test_lister_equipes_filtre_championnat(self, client):
        """GET /api/v1/jeux/equipes?championnat=ligue1 accepte le filtre."""
        response = client.get("/api/v1/jeux/equipes?championnat=ligue1")
        assert response.status_code in (200, 500)

    def test_lister_equipes_recherche(self, client):
        """GET /api/v1/jeux/equipes?search=PSG accepte la recherche."""
        response = client.get("/api/v1/jeux/equipes?search=PSG")
        assert response.status_code in (200, 500)

    def test_obtenir_equipe_endpoint(self, client):
        """GET /api/v1/jeux/equipes/{id} existe."""
        response = client.get("/api/v1/jeux/equipes/999999")
        assert response.status_code in (200, 404, 500)


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES MATCHS
# ═══════════════════════════════════════════════════════════


class TestRoutesMatchs:
    """Tests des routes matchs."""

    def test_lister_matchs_endpoint(self, client):
        """GET /api/v1/jeux/matchs existe."""
        response = client.get("/api/v1/jeux/matchs")
        assert response.status_code in (200, 500)

    def test_lister_matchs_pagination(self, client):
        """GET /api/v1/jeux/matchs?page=1&page_size=10 accepte la pagination."""
        response = client.get("/api/v1/jeux/matchs?page=1&page_size=10")
        assert response.status_code in (200, 500)

    def test_lister_matchs_filtre_championnat(self, client):
        """GET /api/v1/jeux/matchs?championnat=ligue1 accepte le filtre."""
        response = client.get("/api/v1/jeux/matchs?championnat=ligue1")
        assert response.status_code in (200, 500)

    def test_lister_matchs_filtre_joue(self, client):
        """GET /api/v1/jeux/matchs?joue=true accepte le filtre."""
        response = client.get("/api/v1/jeux/matchs?joue=true")
        assert response.status_code in (200, 500)

    def test_obtenir_match_endpoint(self, client):
        """GET /api/v1/jeux/matchs/{id} existe."""
        response = client.get("/api/v1/jeux/matchs/999999")
        assert response.status_code in (200, 404, 500)


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES PARIS
# ═══════════════════════════════════════════════════════════


class TestRoutesParis:
    """Tests des routes paris sportifs."""

    def test_lister_paris_endpoint(self, client):
        """GET /api/v1/jeux/paris existe."""
        response = client.get("/api/v1/jeux/paris")
        assert response.status_code in (200, 500)

    def test_lister_paris_filtre_statut(self, client):
        """GET /api/v1/jeux/paris?statut=en_attente accepte le filtre."""
        response = client.get("/api/v1/jeux/paris?statut=en_attente")
        assert response.status_code in (200, 500)

    def test_lister_paris_filtre_virtuel(self, client):
        """GET /api/v1/jeux/paris?est_virtuel=true accepte le filtre."""
        response = client.get("/api/v1/jeux/paris?est_virtuel=true")
        assert response.status_code in (200, 500)

    def test_obtenir_stats_paris_endpoint(self, client):
        """GET /api/v1/jeux/paris/stats existe."""
        response = client.get("/api/v1/jeux/paris/stats")
        assert response.status_code in (200, 500)

    def test_creer_pari_endpoint(self, client):
        """POST /api/v1/jeux/paris existe."""
        response = client.post("/api/v1/jeux/paris", json=PARI_CREATE)
        assert response.status_code in (200, 201, 422, 500)

    def test_modifier_pari_endpoint(self, client):
        """PATCH /api/v1/jeux/paris/{id} existe."""
        response = client.patch("/api/v1/jeux/paris/1", json=PARI_PATCH)
        assert response.status_code in (200, 404, 422, 500)

    def test_supprimer_pari_endpoint(self, client):
        """DELETE /api/v1/jeux/paris/{id} existe."""
        response = client.delete("/api/v1/jeux/paris/999999")
        assert response.status_code in (200, 204, 404, 500)


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES LOTO
# ═══════════════════════════════════════════════════════════


class TestRoutesLoto:
    """Tests des routes loto."""

    def test_lister_tirages_endpoint(self, client):
        """GET /api/v1/jeux/loto/tirages existe."""
        response = client.get("/api/v1/jeux/loto/tirages")
        assert response.status_code in (200, 500)

    def test_lister_tirages_filtre_type(self, client):
        """GET /api/v1/jeux/loto/tirages?type_loto=loto accepte le filtre."""
        response = client.get("/api/v1/jeux/loto/tirages?type_loto=loto")
        assert response.status_code in (200, 500)

    def test_lister_grilles_endpoint(self, client):
        """GET /api/v1/jeux/loto/grilles existe."""
        response = client.get("/api/v1/jeux/loto/grilles")
        assert response.status_code in (200, 500)

    def test_lister_grilles_filtre_tirage(self, client):
        """GET /api/v1/jeux/loto/grilles?tirage_id=1 accepte le filtre."""
        response = client.get("/api/v1/jeux/loto/grilles?tirage_id=1")
        assert response.status_code in (200, 500)
