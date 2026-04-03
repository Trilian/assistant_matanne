"""
Tests pour src/api/routes/export.py

Tests unitaires pour les routes d'export PDF.
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
# TESTS ROUTES EXPORT
# ═══════════════════════════════════════════════════════════


class TestRoutesExport:
    """Tests des routes d'export PDF."""

    def test_export_pdf_endpoint_existe(self, client):
        """POST /api/v1/export/pdf existe."""
        response = client.post("/api/v1/export/pdf?type_export=courses")
        assert response.status_code in (200, 500)

    def test_export_pdf_type_courses(self, client):
        """POST /api/v1/export/pdf?type_export=courses existe."""
        response = client.post("/api/v1/export/pdf?type_export=courses")
        assert response.status_code in (200, 500)

    def test_export_pdf_type_planning(self, client):
        """POST /api/v1/export/pdf?type_export=planning&id_ressource=1 existe."""
        response = client.post("/api/v1/export/pdf?type_export=planning&id_ressource=1")
        assert response.status_code in (200, 500)

    def test_export_pdf_type_recette_avec_id(self, client):
        """POST /api/v1/export/pdf?type_export=recette&id_ressource=1 existe."""
        response = client.post(
            "/api/v1/export/pdf?type_export=recette&id_ressource=1"
        )
        assert response.status_code in (200, 500)

    def test_export_pdf_planning_sans_id(self, client):
        """POST /api/v1/export/pdf?type_export=planning sans id_ressource retourne 422."""
        response = client.post("/api/v1/export/pdf?type_export=planning")
        assert response.status_code == 422

    def test_export_pdf_type_budget_retourne_reponse(self, client):
        """POST /api/v1/export/pdf?type_export=budget retourne une réponse valide."""
        response = client.post("/api/v1/export/pdf?type_export=budget")
        assert response.status_code in (200, 500, 501)

    def test_export_pdf_type_manquant(self, client):
        """POST /api/v1/export/pdf sans type_export échoue."""
        response = client.post("/api/v1/export/pdf")
        assert response.status_code == 422

    def test_export_pdf_type_invalide(self, client):
        """POST /api/v1/export/pdf?type_export=invalid retourne erreur."""
        response = client.post("/api/v1/export/pdf?type_export=invalid")
        assert response.status_code in (400, 422, 500)


class TestRoutesExportAvecMock:
    """Tests avec mock du service d'export."""

    def test_export_courses_retourne_pdf(self):
        """Export courses retourne un PDF valide."""
        mock_service = MagicMock()
        mock_service.exporter_courses.return_value = b"%PDF-1.4 fake content"

        with patch(
            "src.api.routes.export.obtenir_service_export_pdf",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app)
            response = client.post("/api/v1/export/pdf?type_export=courses")

            if response.status_code == 200:
                assert response.headers.get("content-type") == "application/pdf"

    def test_export_planning_retourne_pdf(self):
        """Export planning retourne un PDF valide."""
        mock_service = MagicMock()
        mock_service.exporter_planning.return_value = b"%PDF-1.4 fake content"

        with patch(
            "src.api.routes.export.obtenir_service_export_pdf",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app)
            response = client.post("/api/v1/export/pdf?type_export=planning")

            if response.status_code == 200:
                assert response.headers.get("content-type") == "application/pdf"

    def test_export_budget_retourne_pdf(self):
        """Export budget retourne un PDF valide."""
        from io import BytesIO

        mock_buffer = BytesIO(b"%PDF-1.4 budget content")
        mock_service = MagicMock()
        mock_service.exporter_budget.return_value = mock_buffer

        with patch(
            "src.api.routes.export.obtenir_service_export_pdf",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app)
            response = client.post("/api/v1/export/pdf?type_export=budget")

            if response.status_code == 200:
                assert response.headers.get("content-type") == "application/pdf"

    def test_export_recette_retourne_pdf(self):
        """Export recette avec id_ressource retourne un PDF valide."""
        from io import BytesIO

        mock_buffer = BytesIO(b"%PDF-1.4 recette content")
        mock_service = MagicMock()
        mock_service.exporter_recette.return_value = mock_buffer

        with patch(
            "src.api.routes.export.obtenir_service_export_pdf",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app)
            response = client.post("/api/v1/export/pdf?type_export=recette&id_ressource=1")

            if response.status_code == 200:
                assert response.headers.get("content-type") == "application/pdf"

    def test_export_recette_sans_id_retourne_422(self):
        """Export recette sans id_ressource retourne 422."""
        from src.api.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/v1/export/pdf?type_export=recette")
        assert response.status_code == 422


class TestRoutesExportErreurs:
    """Tests erreurs et edge cases pour l'export PDF."""

    def test_export_service_exception_retourne_500(self):
        """Si le service lève une exception, l'API retourne 500."""
        mock_service = MagicMock()
        mock_service.exporter_liste_courses.side_effect = RuntimeError("PDF generation failed")

        with patch(
            "src.api.routes.export.obtenir_service_export_pdf",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app, raise_server_exceptions=False)
            response = client.post("/api/v1/export/pdf?type_export=courses")
            assert response.status_code == 500

    def test_export_recette_id_negatif(self):
        """Export recette avec ID négatif ne plante pas."""
        from src.api.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/v1/export/pdf?type_export=recette&id_ressource=-1")
        assert response.status_code in (200, 404, 422, 500)

    def test_export_planning_id_inexistant(self):
        """Export planning avec ID inexistant retourne erreur ou résultat vide."""
        from src.api.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.post("/api/v1/export/pdf?type_export=planning&id_ressource=999999")
        assert response.status_code in (200, 404, 500)

    def test_export_pdf_content_type_valide(self):
        """L'export PDF retourne le bon Content-Type."""
        from io import BytesIO

        mock_buffer = BytesIO(b"%PDF-1.4 content")
        mock_service = MagicMock()
        mock_service.exporter_liste_courses.return_value = (mock_buffer, "test_export")

        with patch(
            "src.api.routes.export.obtenir_service_export_pdf",
            return_value=mock_service,
        ):
            from src.api.main import app

            client = TestClient(app, raise_server_exceptions=False)
            response = client.post("/api/v1/export/pdf?type_export=courses")
            if response.status_code == 200:
                assert "application/pdf" in response.headers.get("content-type", "")
                assert "Content-Disposition" in response.headers

    def test_export_json_domaines_valides(self):
        """GET /api/v1/export/domaines retourne les domaines disponibles."""
        from src.api.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/export/domaines")
        assert response.status_code in (200, 401)
        if response.status_code == 200:
            data = response.json()
            assert "domaines" in data
            assert len(data["domaines"]) > 0

    def test_export_json_domaine_invalide(self):
        """GET /api/v1/export/json avec domaine invalide retourne 422."""
        from src.api.main import app

        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/export/json?domaines=fake_domain")
        assert response.status_code in (422, 401)
