"""
Tests pour src/api/routes/dashboard.py et src/api/routes/jeux.py

Tests unitaires des routes dashboard (agrégation) et jeux
(équipes, matchs, paris, loto, grilles).
"""

from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio(loop_scope="function")


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

EQUIPE_TEST = {
    "id": 1,
    "nom": "Paris Saint-Germain",
    "nom_court": "PSG",
    "championnat": "Ligue 1",
    "pays": "France",
    "logo_url": None,
    "matchs_joues": 30,
    "victoires": 22,
    "nuls": 5,
    "defaites": 3,
    "buts_marques": 65,
    "buts_encaisses": 25,
    "points": 71,
    "forme_recente": "VVDNV",
}

MATCH_TEST = {
    "id": 1,
    "championnat": "Ligue 1",
    "journee": 30,
    "date_match": "2026-04-10",
    "heure": "21:00",
    "score_domicile": 2,
    "score_exterieur": 1,
    "resultat": "1",
    "joue": True,
    "cote_domicile": 1.45,
    "cote_nul": 4.50,
    "cote_exterieur": 6.00,
}

PARI_TEST = {
    "id": 1,
    "match_id": 1,
    "type_pari": "1N2",
    "prediction": "1",
    "cote": 1.45,
    "mise": 10.0,
    "statut": "gagne",
    "gain": 14.5,
    "est_virtuel": True,
    "confiance_prediction": 0.85,
}


# ═══════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def client():
    """Client HTTP léger pour tester les routes."""
    import httpx

    from src.api.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


def creer_mock(data: dict) -> MagicMock:
    """Crée un mock avec attributs depuis un dict."""
    mock = MagicMock()
    for key, value in data.items():
        setattr(mock, key, value)
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS — EXISTENCE DES ENDPOINTS
# ═══════════════════════════════════════════════════════════


class TestEndpointsDashboard:
    """Vérifie que l'endpoint dashboard existe."""

    async def test_dashboard_existe(self, client):
        """GET /api/v1/dashboard n'est pas 404."""
        response = await client.get("/api/v1/dashboard")
        assert response.status_code not in (404, 405)


class TestEndpointsJeux:
    """Vérifie que les endpoints jeux existent (pas 404/405)."""

    @pytest.mark.parametrize(
        "method,path",
        [
            # Équipes
            ("GET", "/api/v1/jeux/equipes"),
            ("GET", "/api/v1/jeux/equipes/1"),
            # Matchs
            ("GET", "/api/v1/jeux/matchs"),
            ("GET", "/api/v1/jeux/matchs/1"),
            # Paris
            ("GET", "/api/v1/jeux/paris"),
            ("GET", "/api/v1/jeux/paris/stats"),
            ("POST", "/api/v1/jeux/paris"),
            ("PATCH", "/api/v1/jeux/paris/1"),
            ("DELETE", "/api/v1/jeux/paris/1"),
            # Loto
            ("GET", "/api/v1/jeux/loto/tirages"),
        ],
    )
    async def test_endpoint_existe(self, client, method, path):
        """L'endpoint existe (pas 404 ni 405)."""
        func = getattr(client, method.lower())
        if method == "POST" and "paris" in path:
            response = await func(
                path,
                json={
                    "match_id": 1,
                    "prediction": "1",
                    "cote": 1.5,
                    "mise": 10,
                },
            )
        elif method == "PATCH":
            response = await func(path, json={"statut": "gagne"})
        else:
            response = await func(path)
        assert response.status_code not in (404, 405), (
            f"{method} {path} retourne {response.status_code}"
        )


# ═══════════════════════════════════════════════════════════
# TESTS — FORMAT DASHBOARD
# ═══════════════════════════════════════════════════════════


class TestFormatDashboard:
    """Vérifie le format de la réponse dashboard."""

    @pytest.mark.skip(reason="RepasPlanning model not yet defined in src.core.models")
    @patch("src.api.routes.dashboard.executer_avec_session")
    @patch("src.api.routes.dashboard.executer_async")
    async def test_dashboard_format_complet(self, mock_exec, mock_session, client):
        """Le dashboard retourne statistiques, budget, activités, alertes."""
        mock_exec.side_effect = lambda fn: fn()

        from sqlalchemy import func as sa_func

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()

        # Mock query chain — toutes les queries retournent des scalaires/listes vides
        query = session.query.return_value
        query.filter.return_value = query
        query.with_entities.return_value = query
        query.group_by.return_value = query
        query.order_by.return_value = query
        query.limit.return_value = query
        query.scalar.return_value = 0
        query.count.return_value = 0
        query.all.return_value = []
        mock_session.return_value = ctx

        response = await client.get("/api/v1/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "statistiques" in data
        assert "budget_mois" in data
        assert "prochaines_activites" in data
        assert "alertes" in data
        assert "recettes_total" in data["statistiques"]
        assert "total_mois" in data["budget_mois"]


# ═══════════════════════════════════════════════════════════
# TESTS — FORMAT JEUX
# ═══════════════════════════════════════════════════════════


class TestFormatJeux:
    """Vérifie le format des réponses routes jeux."""

    @patch("src.api.routes.jeux.executer_avec_session")
    @patch("src.api.routes.jeux.executer_async")
    async def test_lister_equipes_format(self, mock_exec, mock_session, client):
        """La liste d'équipes retourne items correctement."""
        mock_exec.side_effect = lambda fn: fn()
        mock_equipe = creer_mock(EQUIPE_TEST)

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.order_by.return_value.all.return_value = [mock_equipe]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/jeux/equipes")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["items"][0]["nom"] == "Paris Saint-Germain"

    @patch("src.api.routes.jeux.executer_avec_session")
    @patch("src.api.routes.jeux.executer_async")
    async def test_lister_paris_format(self, mock_exec, mock_session, client):
        """La liste de paris retourne format paginé."""
        mock_exec.side_effect = lambda fn: fn()
        mock_pari = creer_mock(PARI_TEST)
        mock_pari.cree_le = MagicMock()

        ctx = MagicMock()
        ctx.__enter__ = MagicMock(return_value=MagicMock())
        ctx.__exit__ = MagicMock(return_value=False)
        session = ctx.__enter__()
        query = session.query.return_value
        query.filter.return_value = query
        query.count.return_value = 1
        query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            mock_pari
        ]
        mock_session.return_value = ctx

        response = await client.get("/api/v1/jeux/paris")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["items"][0]["statut"] == "gagne"
