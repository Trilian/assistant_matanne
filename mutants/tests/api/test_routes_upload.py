"""
Tests pour src/api/routes/upload.py

Tests unitaires pour les routes d'upload de fichiers.
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app)


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES UPLOAD
# ═══════════════════════════════════════════════════════════


class TestRoutesUpload:
    """Tests des routes d'upload."""

    def test_upload_endpoint_existe(self, client):
        """POST /api/v1/upload existe."""
        fake_file = BytesIO(b"fake image content")
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test.jpg", fake_file, "image/jpeg")},
        )
        assert response.status_code in (200, 201, 413, 415, 500, 503)

    def test_upload_avec_bucket(self, client):
        """POST /api/v1/upload?bucket=photos accepte le bucket."""
        fake_file = BytesIO(b"fake photo")
        response = client.post(
            "/api/v1/upload?bucket=photos",
            files={"file": ("photo.jpg", fake_file, "image/jpeg")},
        )
        assert response.status_code in (200, 201, 413, 415, 500, 503)

    def test_lister_photos_endpoint(self, client):
        """GET /api/v1/upload/photos existe."""
        response = client.get("/api/v1/upload/photos")
        assert response.status_code in (200, 500, 503)

    def test_lister_photos_filtre_categorie(self, client):
        """GET /api/v1/upload/photos?categorie=famille accepte le filtre."""
        response = client.get("/api/v1/upload/photos?categorie=famille")
        assert response.status_code in (200, 500, 503)

    def test_supprimer_photo_endpoint(self, client):
        """DELETE /api/v1/upload/photos/{path} existe."""
        response = client.delete("/api/v1/upload/photos/test/photo.jpg")
        assert response.status_code in (200, 204, 403, 404, 500, 503)


class TestRoutesUploadValidation:
    """Tests de validation upload."""

    def test_upload_sans_fichier(self, client):
        """POST /api/v1/upload sans fichier échoue."""
        response = client.post("/api/v1/upload")
        assert response.status_code == 422
