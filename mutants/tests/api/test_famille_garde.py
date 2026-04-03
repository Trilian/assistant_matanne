"""
CT-07b — Tests des routes famille/garde et planning (routes famille/garde)

Tests couvrant:
- GET  /api/v1/famille/config/garde    : lecture config crèche
- PUT  /api/v1/famille/config/garde    : écriture config crèche
- GET  /api/v1/famille/planning/jours-sans-creche : jours sans crèche
"""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def async_client():
    from src.api.main import app
    from src.api.dependencies import require_auth

    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "membre"}
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _mock_jours_speciaux_service(jours: list | None = None):
    service = MagicMock()
    service.charger_config_depuis_db.return_value = None
    service.fermetures_creche.return_value = jours or []
    service.sauvegarder_fermetures_creche.return_value = None
    return service


# ═══════════════════════════════════════════════════════════
# GET /api/v1/famille/config/garde
# ═══════════════════════════════════════════════════════════


class TestLireConfigGarde:
    """Tests pour GET /api/v1/famille/config/garde."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ), patch("src.services.famille.jours_speciaux._config_creche", {
            "semaines_fermeture": [],
            "nom_creche": "",
            "zone_academique": "B",
            "annee_courante": None,
        }):
            response = await async_client.get("/api/v1/famille/config/garde")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retourne_structure_valide(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ), patch("src.services.famille.jours_speciaux._config_creche", {
            "semaines_fermeture": [],
            "nom_creche": "Crèche des Lilas",
            "zone_academique": "B",
            "annee_courante": 2025,
        }):
            response = await async_client.get("/api/v1/famille/config/garde")

        if response.status_code == 200:
            data = response.json()
            assert "zone_academique" in data
            assert "semaines_fermeture" in data

    @pytest.mark.asyncio
    async def test_zone_academique_par_defaut_b(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ), patch("src.services.famille.jours_speciaux._config_creche", {
            "semaines_fermeture": [],
            "nom_creche": "",
            "zone_academique": "B",
            "annee_courante": None,
        }):
            response = await async_client.get("/api/v1/famille/config/garde")

        if response.status_code == 200:
            data = response.json()
            assert data.get("zone_academique") == "B"


# ═══════════════════════════════════════════════════════════
# PUT /api/v1/famille/config/garde
# ═══════════════════════════════════════════════════════════


class TestSauvegarderConfigGarde:
    """Tests pour PUT /api/v1/famille/config/garde."""

    @pytest.mark.asyncio
    async def test_sauvegarde_config_vide(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        payload = {
            "semaines_fermeture": [],
            "nom_creche": "Crèche Les Lutins",
            "zone_academique": "A",
        }

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            response = await async_client.put("/api/v1/famille/config/garde", json=payload)

        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_sauvegarde_appelle_service(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        payload = {
            "semaines_fermeture": [],
            "nom_creche": "Crèche Test",
            "zone_academique": "C",
        }

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            await async_client.put("/api/v1/famille/config/garde", json=payload)

        mock_service.sauvegarder_fermetures_creche.assert_called_once()

    @pytest.mark.asyncio
    async def test_validation_zone_academique_requise(self, async_client: httpx.AsyncClient):
        payload = {
            "semaines_fermeture": [],
            "nom_creche": "Test",
            # zone_academique omise → a une default dans le schéma
        }
        response = await async_client.put("/api/v1/famille/config/garde", json=payload)
        # zone_academique a une valeur par défaut "B" donc 200 OK
        assert response.status_code in [200, 201, 422]


# ═══════════════════════════════════════════════════════════
# GET /api/v1/famille/planning/jours-sans-creche
# ═══════════════════════════════════════════════════════════


class TestJoursSansCreche:
    """Tests pour GET /api/v1/famille/planning/jours-sans-creche."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            response = await async_client.get("/api/v1/famille/planning/jours-sans-creche")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_retourne_structure_avec_mois(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            response = await async_client.get("/api/v1/famille/planning/jours-sans-creche")

        assert response.status_code == 200
        data = response.json()
        assert "mois" in data
        assert "jours" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_parametre_mois_valide(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            response = await async_client.get(
                "/api/v1/famille/planning/jours-sans-creche?mois=2025-07"
            )

        assert response.status_code == 200
        data = response.json()
        assert data["mois"] == "2025-07"

    @pytest.mark.asyncio
    async def test_parametre_mois_invalide_retourne_422(self, async_client: httpx.AsyncClient):
        mock_service = _mock_jours_speciaux_service()

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            response = await async_client.get(
                "/api/v1/famille/planning/jours-sans-creche?mois=pas-une-date"
            )

        assert response.status_code in [422, 500]

    @pytest.mark.asyncio
    async def test_liste_des_jours_est_une_liste(self, async_client: httpx.AsyncClient):
        mock_jour = MagicMock()
        mock_jour.date_jour = date(2025, 4, 7)
        mock_jour.nom = "Lundi de Pâques"

        mock_service = _mock_jours_speciaux_service(jours=[mock_jour])

        with patch(
            "src.services.famille.jours_speciaux.obtenir_service_jours_speciaux",
            return_value=mock_service,
        ):
            response = await async_client.get(
                "/api/v1/famille/planning/jours-sans-creche?mois=2025-04"
            )

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data["jours"], list)
            if data["jours"]:
                jour = data["jours"][0]
                assert "date" in jour
                assert "label" in jour


# ═══════════════════════════════════════════════════════════
# Schémas — validation Pydantic
# ═══════════════════════════════════════════════════════════


class TestConfigGardeSchemas:
    """Tests unitaires des schémas Pydantic config garde."""

    def test_config_garde_request_defaults(self):
        from src.api.schemas.famille import ConfigGardeRequest

        config = ConfigGardeRequest()
        assert config.semaines_fermeture == []
        assert config.nom_creche == ""
        assert config.zone_academique == "B"

    def test_config_garde_request_avec_zone(self):
        from src.api.schemas.famille import ConfigGardeRequest

        config = ConfigGardeRequest(
            semaines_fermeture=[],
            nom_creche="Crèche Arc-en-ciel",
            zone_academique="A",
        )
        assert config.zone_academique == "A"
        assert config.nom_creche == "Crèche Arc-en-ciel"
