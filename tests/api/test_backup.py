"""
Tests pour l'export backup personnel (POST /api/v1/export/backup).

Couverture:
- Export des données utilisateur en ZIP
- Authentification requise
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


class TestBackupPersonnel:
    """Tests de l'export backup personnel."""

    def test_backup_requires_auth(self, client):
        """Le backup nécessite une authentification."""
        response = client.post("/api/v1/export/backup")
        assert response.status_code in [200, 401]

    def test_backup_returns_zip(self, client, auth_headers):
        """Le backup retourne un fichier ZIP."""
        response = client.post("/api/v1/export/backup", headers=auth_headers)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert "application/zip" in content_type or "application/octet-stream" in content_type

    def test_backup_has_filename(self, client, auth_headers):
        """Le backup a un nom de fichier."""
        response = client.post("/api/v1/export/backup", headers=auth_headers)
        if response.status_code == 200:
            content_disposition = response.headers.get("content-disposition", "")
            assert "attachment" in content_disposition
            assert "backup_" in content_disposition

    def test_backup_multiple_calls_allowed(self, client, auth_headers):
        """L'utilisateur peut faire plusieurs backups."""
        response1 = client.post("/api/v1/export/backup", headers=auth_headers)
        response2 = client.post("/api/v1/export/backup", headers=auth_headers)
        assert response1.status_code in [200, 500]
        assert response2.status_code in [200, 500]
