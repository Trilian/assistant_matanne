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
    """Client de test FastAPI avec dépendances d'auth mocké pour accès admin."""
    from src.api.main import app
    from src.api.dependencies import require_auth

    # Override require_auth pour retourner un utilisateur admin
    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-admin-user",
        "email": "admin@test.local",
        "role": "admin",
    }

    client = TestClient(app, raise_server_exceptions=False)

    yield client

    # Nettoyer les overrides après le test
    app.dependency_overrides.clear()


@pytest.fixture
def non_admin_client():
    """Client de test FastAPI avec un utilisateur non-admin."""
    from src.api.main import app
    from src.api.dependencies import require_auth

    # Override require_auth pour retourner un utilisateur NON admin
    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user",
        "email": "user@test.local",
        "role": "membre",
    }

    client = TestClient(app, raise_server_exceptions=False)

    yield client

    # Nettoyer les overrides après le test
    app.dependency_overrides.clear()



# ═══════════════════════════════════════════════════════════
# TESTS AUDIT LOGS
# ═══════════════════════════════════════════════════════════


class TestAuditLogs:
    """Tests de consultation des logs d'audit."""

    def test_audit_logs_requires_auth(self):
        """L'acceso aux logs necesita autenticación o será rechazado por rol."""
        from src.api.main import app

        # Client SANS override para tester sin override — retorna 403 (rol insuficiente)
        client = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/v1/admin/audit-logs")
        # En mode dev, retorna 403 porque auto-auth donne role "membre" (pas admin)
        # En production, retournerait 401 (pas de token)
        assert response.status_code in [401, 403]

    def test_audit_logs_requires_admin_role(self, non_admin_client):
        """Seuls les admins peuvent accéder aux logs (utilisateur standard rejeté)."""
        response = non_admin_client.get("/api/v1/admin/audit-logs")
        # Devrait retourner 403 Forbidden (utilisateur standard)
        assert response.status_code == 403

    def test_audit_logs_pagination(self, client):
        """La pagination fonctionne correctement."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"page": 1, "par_page": 10},
        )
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "par_page" in data
        assert "pages_totales" in data
        assert isinstance(data["items"], list)

    def test_audit_logs_pagination_limits(self, client):
        """La pagination respecte les limites (max 200 par page)."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"page": 1, "par_page": 300},  # Au-dessus du max
        )
        # Devrait échouer la validation
        assert response.status_code == 422

    def test_audit_logs_filter_by_action(self, client):
        """Filtrer les logs par type d'action."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"action": "creation"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data

    def test_audit_logs_filter_by_entite_type(self, client):
        """Filtrer les logs par type d'entité."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"entite_type": "recette"},
        )
        assert response.status_code == 200

    def test_audit_logs_filter_by_date_range(self, client):
        """Filtrer les logs par plage de dates."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={
                "depuis": "2024-01-01T00:00:00Z",
                "jusqu_a": "2024-12-31T23:59:59Z",
            },
        )
        assert response.status_code == 200



# ═══════════════════════════════════════════════════════════
# TESTS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestAuditStats:
    """Tests des statistiques d'audit."""

    def test_audit_stats_requires_admin(self, non_admin_client):
        """Seuls les admins peuvent accéder aux stats."""
        response = non_admin_client.get("/api/v1/admin/audit-stats")
        assert response.status_code == 403

    def test_audit_stats_structure(self, client):
        """Les stats retournent une structure cohérente."""
        response = client.get("/api/v1/admin/audit-stats")
        assert response.status_code == 200
        data = response.json()

        # Vérifier que c'est un dict (compteurs par action/entité/source)
        assert isinstance(data, dict)


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT CSV
# ═══════════════════════════════════════════════════════════


class TestAuditExport:
    """Tests de l'export CSV."""

    def test_audit_export_requires_admin(self, non_admin_client):
        """Seuls les admins peuvent exporter les logs."""
        response = non_admin_client.get("/api/v1/admin/audit-export")
        assert response.status_code == 403

    def test_audit_export_csv_format(self, client):
        """L'export retourne un fichier CSV."""
        response = client.get("/api/v1/admin/audit-export")
        assert response.status_code == 200

        # Vérifier le Content-Type CSV
        content_type = response.headers.get("content-type", "")
        assert "text/csv" in content_type or "application/octet-stream" in content_type

    def test_audit_export_with_filters(self, client):
        """L'export CSV peut être filtré."""
        response = client.get(
            "/api/v1/admin/audit-export",
            params={"action": "creation", "entite_type": "recette"},
        )
        assert response.status_code == 200


# ═══════════════════════════════════════════════════════════
# TESTS DE SÉCURITÉ
# ═══════════════════════════════════════════════════════════


class TestAuditSecurity:
    """Tests de sécurité des routes admin."""

    def test_audit_logs_no_sql_injection(self, client):
        """Résistance à l'injection SQL dans les filtres."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"action": "'; DROP TABLE audit_logs; --"},
        )
        # Ne devrait pas crasher, juste retourner 0 résultats ou 200/400
        assert response.status_code in [200, 400, 422]

    def test_audit_logs_xss_protection(self, client):
        """Protection contre XSS dans les paramètres."""
        response = client.get(
            "/api/v1/admin/audit-logs",
            params={"action": "<script>alert('xss')</script>"},
        )
        # Devrait retourner une réponse saine
        assert response.status_code in [200, 400]

    def test_audit_export_no_path_traversal(self, client):
        """Protection contre path traversal."""
        response = client.get(
            "/api/v1/admin/audit-export",
            params={"entite_type": "../../../etc/passwd"},
        )
        # Devrait être sécurisé
        assert response.status_code in [200, 400]
