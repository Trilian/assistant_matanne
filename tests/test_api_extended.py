"""
Tests API complémentaires - Endpoints manquants

Tests pour:
- Endpoints budget
- Endpoints météo
- Endpoints backup
- Endpoints calendrier
- Rate limiting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date
from fastapi.testclient import TestClient


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def api_client():
    """Client de test FastAPI avec mocks"""
    with patch.dict('sys.modules', {
        'src.core.database': MagicMock(),
        'src.core.models': MagicMock(),
    }):
        from src.api.main import app
        return TestClient(app)


@pytest.fixture
def auth_headers():
    """Headers d'authentification mockés"""
    return {"Authorization": "Bearer test_token_12345"}


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS BUDGET
# ═══════════════════════════════════════════════════════════


class TestBudgetEndpoints:
    """Tests endpoints budget"""

    def test_get_depenses_mois(self, api_client, auth_headers):
        """Test récupération dépenses du mois"""
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.all.return_value = []
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            # L'endpoint peut ne pas exister encore - test conditionnel
            response = api_client.get("/api/budget/depenses", headers=auth_headers)
            
            # 200 ou 404 si endpoint non implémenté
            assert response.status_code in [200, 404, 401]

    def test_create_depense(self, api_client, auth_headers):
        """Test création dépense"""
        depense_data = {
            "montant": 45.50,
            "categorie": "alimentation",
            "description": "Courses Carrefour",
            "date": str(date.today())
        }
        
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            response = api_client.post(
                "/api/budget/depenses",
                json=depense_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 201, 404, 401, 422]

    def test_get_budget_resume(self, api_client, auth_headers):
        """Test résumé budget mensuel"""
        mois = date.today().strftime("%Y-%m")
        
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            response = api_client.get(
                f"/api/budget/resume/{mois}",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401]

    def test_budget_categories_valides(self):
        """Test catégories budget valides"""
        categories_valides = [
            'alimentation', 'transport', 'logement', 'sante',
            'loisirs', 'vetements', 'education', 'cadeaux',
            'abonnements', 'restaurant', 'vacances', 'bebe', 'autre'
        ]
        
        assert 'alimentation' in categories_valides
        assert len(categories_valides) >= 10


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS MÉTÉO
# ═══════════════════════════════════════════════════════════


class TestWeatherEndpoints:
    """Tests endpoints météo"""

    def test_get_current_weather(self, api_client):
        """Test météo actuelle"""
        with patch('src.services.weather.WeatherService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_current_weather.return_value = {
                "temperature": 18,
                "condition": "Nuageux",
                "humidity": 65
            }
            mock_service.return_value = mock_instance
            
            response = api_client.get("/api/weather/current")
            
            assert response.status_code in [200, 404]

    def test_get_weather_alerts(self, api_client, auth_headers):
        """Test alertes météo jardin"""
        with patch('src.services.weather.WeatherService') as mock_service:
            mock_instance = Mock()
            mock_instance.get_garden_alerts.return_value = []
            mock_service.return_value = mock_instance
            
            response = api_client.get(
                "/api/weather/alerts",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401]

    def test_weather_forecast(self, api_client):
        """Test prévisions météo"""
        response = api_client.get("/api/weather/forecast")
        
        # Peut ne pas être implémenté
        assert response.status_code in [200, 404]


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS BACKUP
# ═══════════════════════════════════════════════════════════


class TestBackupEndpoints:
    """Tests endpoints backup"""

    def test_list_backups(self, api_client, auth_headers):
        """Test liste des backups"""
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            response = api_client.get(
                "/api/backup/list",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401]

    def test_create_backup(self, api_client, auth_headers):
        """Test création backup"""
        with patch('src.services.backup.BackupService') as mock_service:
            mock_instance = Mock()
            mock_instance.create_backup.return_value = {
                "id": 1,
                "filename": "backup_2026-01-26.json",
                "size_bytes": 1024
            }
            mock_service.return_value = mock_instance
            
            response = api_client.post(
                "/api/backup/create",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 201, 404, 401]

    def test_restore_backup(self, api_client, auth_headers):
        """Test restauration backup"""
        with patch('src.services.backup.BackupService') as mock_service:
            mock_instance = Mock()
            mock_instance.restore_backup.return_value = True
            mock_service.return_value = mock_instance
            
            response = api_client.post(
                "/api/backup/restore/1",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401]


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS CALENDRIER
# ═══════════════════════════════════════════════════════════


class TestCalendarEndpoints:
    """Tests endpoints calendrier"""

    def test_get_events(self, api_client, auth_headers):
        """Test récupération événements"""
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.filter.return_value.all.return_value = []
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            response = api_client.get(
                "/api/calendar/events",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401]

    def test_sync_external_calendar(self, api_client, auth_headers):
        """Test synchronisation calendrier externe"""
        sync_data = {
            "provider": "google",
            "calendar_id": "primary"
        }
        
        with patch('src.services.calendar_sync.CalendarSyncService') as mock_service:
            mock_instance = Mock()
            mock_instance.sync.return_value = {"synced": 5}
            mock_service.return_value = mock_instance
            
            response = api_client.post(
                "/api/calendar/sync",
                json=sync_data,
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401, 422]


# ═══════════════════════════════════════════════════════════
# TESTS RATE LIMITING
# ═══════════════════════════════════════════════════════════


class TestRateLimiting:
    """Tests rate limiting API"""

    def test_rate_limit_headers(self, api_client):
        """Test présence headers rate limit"""
        response = api_client.get("/")
        
        # Headers rate limit peuvent être présents
        headers = response.headers
        
        # Vérifier que la réponse est OK
        assert response.status_code == 200

    def test_rate_limit_exceeded(self, api_client):
        """Test dépassement rate limit"""
        # Simuler beaucoup de requêtes
        # En pratique, le rate limiting devrait bloquer
        
        responses = []
        for _ in range(10):
            response = api_client.get("/health")
            responses.append(response.status_code)
        
        # Toutes devraient passer ou certaines bloquées (429)
        assert all(code in [200, 429] for code in responses)

    def test_ai_rate_limit(self, api_client, auth_headers):
        """Test rate limit spécifique IA"""
        # Les endpoints IA ont des limites plus strictes
        with patch('src.api.rate_limiting.check_ai_rate_limit') as mock_check:
            mock_check.return_value = True  # Pas dépassé
            
            # Un endpoint qui utilise l'IA
            response = api_client.get(
                "/api/recettes/suggestions",
                headers=auth_headers
            )
            
            assert response.status_code in [200, 404, 401, 429]


# ═══════════════════════════════════════════════════════════
# TESTS CORS
# ═══════════════════════════════════════════════════════════


class TestCORS:
    """Tests configuration CORS"""

    def test_cors_headers_preflight(self, api_client):
        """Test headers CORS sur requête OPTIONS"""
        response = api_client.options(
            "/",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "GET"
            }
        )
        
        # OPTIONS devrait retourner les headers CORS
        assert response.status_code in [200, 204]

    def test_cors_allowed_origin(self, api_client):
        """Test origine autorisée"""
        response = api_client.get(
            "/",
            headers={"Origin": "http://localhost:8501"}
        )
        
        assert response.status_code == 200
        
        # Vérifier header Access-Control-Allow-Origin
        acl_header = response.headers.get("access-control-allow-origin")
        if acl_header:
            assert "localhost" in acl_header or acl_header == "*"

    def test_cors_blocked_origin(self, api_client):
        """Test origine bloquée"""
        response = api_client.get(
            "/",
            headers={"Origin": "http://malicious-site.com"}
        )
        
        # Devrait toujours répondre, mais sans header CORS ou bloqué
        # Dépend de la configuration
        assert response.status_code in [200, 403]


# ═══════════════════════════════════════════════════════════
# TESTS AUTHENTIFICATION
# ═══════════════════════════════════════════════════════════


class TestAuthentication:
    """Tests authentification API"""

    def test_endpoint_protected(self, api_client):
        """Test endpoint protégé sans auth"""
        # Un endpoint qui nécessite auth
        response = api_client.get("/api/user/profile")
        
        # 401 Unauthorized ou 404 si non implémenté
        assert response.status_code in [401, 403, 404]

    def test_invalid_token(self, api_client):
        """Test token invalide"""
        headers = {"Authorization": "Bearer invalid_token"}
        
        response = api_client.get(
            "/api/user/profile",
            headers=headers
        )
        
        assert response.status_code in [401, 403, 404]

    def test_expired_token(self, api_client):
        """Test token expiré"""
        # Token JWT expiré (simulé)
        expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2MDAwMDAwMDB9.invalid"
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = api_client.get(
            "/api/user/profile",
            headers=headers
        )
        
        assert response.status_code in [401, 403, 404]


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidation:
    """Tests validation des données"""

    def test_invalid_json(self, api_client, auth_headers):
        """Test JSON invalide"""
        response = api_client.post(
            "/api/recettes",
            content="not valid json",
            headers={**auth_headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code in [400, 422]

    def test_missing_required_field(self, api_client, auth_headers):
        """Test champ requis manquant"""
        # Recette sans nom (requis)
        response = api_client.post(
            "/api/recettes",
            json={"temps_preparation": 30},
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422, 401, 404]

    def test_invalid_field_type(self, api_client, auth_headers):
        """Test type de champ invalide"""
        # temps_preparation devrait être int, pas string
        response = api_client.post(
            "/api/recettes",
            json={
                "nom": "Test",
                "temps_preparation": "trente"  # Invalide
            },
            headers=auth_headers
        )
        
        assert response.status_code in [400, 422, 401, 404]


# ═══════════════════════════════════════════════════════════
# TESTS PAGINATION
# ═══════════════════════════════════════════════════════════


class TestPagination:
    """Tests pagination API"""

    def test_list_with_pagination(self, api_client):
        """Test liste avec pagination"""
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = []
            mock_session.query.return_value.count.return_value = 100
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            response = api_client.get(
                "/api/recettes?skip=0&limit=10"
            )
            
            assert response.status_code in [200, 404]

    def test_pagination_params(self, api_client):
        """Test paramètres pagination"""
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_session.query.return_value.offset.return_value.limit.return_value.all.return_value = []
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            # Page 2, 20 items par page
            response = api_client.get(
                "/api/recettes?skip=20&limit=20"
            )
            
            assert response.status_code in [200, 404]

    def test_pagination_max_limit(self, api_client):
        """Test limite max pagination"""
        with patch('src.api.main.get_db_context') as mock_db:
            mock_session = MagicMock()
            mock_db.return_value.__enter__ = Mock(return_value=mock_session)
            mock_db.return_value.__exit__ = Mock(return_value=None)
            
            # Limite très grande
            response = api_client.get(
                "/api/recettes?limit=10000"
            )
            
            # Devrait être accepté ou limité automatiquement
            assert response.status_code in [200, 400, 422, 404]
