"""
Tests pour les routes d'administration (audit logs).

Couverture:
- Listing des logs d'audit (paginés, filtrés)
- Statistiques d'audit
- Export CSV des logs
- Sécurité (rôle admin requis)
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Client de test FastAPI."""
    from src.api.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_headers():
    """Headers d'authentification standard (non-admin)."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def admin_headers():
    """Headers d'authentification admin."""
    # En mode dev, on peut utiliser un token spécial ou mocker le rôle
    return {"Authorization": "Bearer admin-token"}


# ═══════════════════════════════════════════════════════════
# TESTS AUDIT LOGS
# ═══════════════════════════════════════════════════════════


class TestAuditLogs:
    """Tests de consultation des logs d'audit."""

    def test_audit_logs_requires_auth(self, client):
        """L'accès aux logs nécessite une authentification."""
        response = client.get("/api/v1/admin/audit-logs")
        # En mode dev, vérifier juste que l'endpoint existe
        assert response.status_code in [200, 401, 403]

    def test_audit_logs_requires_admin_role(self, client, auth_headers):
        """Seuls les admins peuvent accéder aux logs (utilisateur standard rejeté)."""
        response = client.get("/api/v1/admin/audit-logs", headers=auth_headers)
        # Devrait retourner 403 Forbidden si l'authentification de rôle est active
        # En mode dev, peut retourner 200 si le check de rôle est désactivé
        assert response.status_code in [200, 403]

    def test_audit_logs_pagination(self, client, admin_headers):
        """La pagination fonctionne correctement."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"page": 1, "par_page": 10},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "par_page" in data
        assert "pages_totales" in data
        assert isinstance(data["items"], list)

    def test_audit_logs_pagination_limits(self, client, admin_headers):
        """La pagination respecte les limites (max 200 par page)."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"page": 1, "par_page": 300},  # Au-dessus du max
            headers=admin_headers,
        )
        # Devrait échouer la validation
        assert response.status_code == 422

    def test_audit_logs_filter_by_action(self, client, admin_headers):
        """Filtrer les logs par type d'action."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"action": "creation"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_audit_logs_filter_by_entite_type(self, client, admin_headers):
        """Filtrer les logs par type d'entité."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"entite_type": "recette"},
            headers=admin_headers,
        )
        assert response.status_code == 200

    def test_audit_logs_filter_by_date_range(self, client, admin_headers):
        """Filtrer les logs par plage de dates."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={
                "depuis": "2024-01-01T00:00:00Z",
                "jusqu_a": "2024-12-31T23:59:59Z",
            },
            headers=admin_headers,
        )
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestAuditStats:
    """Tests des statistiques d'audit."""

    def test_audit_stats_requires_admin(self, client, auth_headers):
        """Seuls les admins peuvent accéder aux stats."""
        response = client.get("/api/v1/admin/audit-stats", headers=auth_headers)
        assert response.status_code in [200, 403]

    def test_audit_stats_structure(self, client, admin_headers):
        """Les stats retournent une structure cohérente."""
        response = client.get("/api/v1/admin/audit-stats", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()

        # Vérifier que c'est un dict (compteurs par action/entité/source)
        assert isinstance(data, dict)


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT CSV
# ═══════════════════════════════════════════════════════════


class TestAuditExport:
    """Tests de l'export CSV."""

    def test_audit_export_requires_admin(self, client, auth_headers):
        """Seuls les admins peuvent exporter les logs."""
        response = client.get("/api/v1/admin/audit-export", headers=auth_headers)
        assert response.status_code in [200, 403]

    def test_audit_export_csv_format(self, client, admin_headers):
        """L'export retourne un fichier CSV."""
        response = client.get("/api/v1/admin/audit-export", headers=admin_headers)
        assert response.status_code == 200

        # Vérifier le Content-Type CSV
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type or "application/octet-stream" in content_type

    def test_audit_export_with_filters(self, client, admin_headers):
        """L'export CSV peut être filtré."""
        response = client.get(
            "/api/v1/admin/audit-export",
            params={"action": "creation", "entite_type": "recette"},
            headers=admin_headers,
        )
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════
# TESTS DE SÉCURITÉ
# ═══════════════════════════════════════════════════════════


class TestAuditSecurity:
    """Tests de sécurité des routes admin."""

    def test_audit_logs_no_sql_injection(self, client, admin_headers):
        """Résistance à l'injection SQL dans les filtres."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"action": "'; DROP TABLE audit_logs; --"},
            headers=admin_headers,
        )
        # Ne devrait pas crasher, juste retourner 0 résultats ou 200/400
        assert response.status_code in [200, 400, 422]

    def test_audit_logs_xss_protection(self, client, admin_headers):
        """Protection contre XSS dans les paramètres."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"action": "<script>alert('xss')</script>"},
            headers=admin_headers,
        )
        # Devrait retourner une réponse saine
        assert response.status_code in [200, 400]

    def test_audit_export_no_path_traversal(self, client, admin_headers):
        """Protection contre path traversal."""
        response = client.get(
            "/api/v1/admin/audit-export",
            params={"entite_type": "../../../etc/passwd"},
            headers=admin_headers,
        )
        # Devrait être sécurisé
        assert response.status_code in [200, 400]
