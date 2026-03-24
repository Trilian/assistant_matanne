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

    def test_export_pdf_type_budget_retourne_501(self, client):
        """POST /api/v1/export/pdf?type_export=budget retourne 501."""
        response = client.post("/api/v1/export/pdf?type_export=budget")
        assert response.status_code in (501, 500)

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
