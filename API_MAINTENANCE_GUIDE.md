"""
API MAINTENANCE & TESTING GUIDE
════════════════════════════════════════════════════════════════════

Guide complet pour maintenir et tester src/api et tests/api.
Suit le même système que src/core et tests/core.
"""

# ═════════════════════════════════════════════════════════════════════
# SECTION 1: ARCHITECTURE API
# ═════════════════════════════════════════════════════════════════════

## Structure src/api

```
src/api/
├── __init__.py
├── main.py              (787 lines) - App FastAPI, endpoints, schemas
├── rate_limiting.py     (522 lines) - Rate limiting middleware
```

**Module Sizes:**
- main.py: 787 lines (Endpoints REST, CRUD)
- rate_limiting.py: 522 lines (Rate limiting strategy)
- Total: 1,309 lines

**Features:**
- ✅ CORS configuré
- ✅ Rate limiting middleware
- ✅ Pydantic schemas
- ✅ JWT authentication ready
- ✅ Documentation Swagger
- ✅ Error handling
- ✅ Logging intégré


## Test Structure

```
tests/api/
├── __init__.py
├── helpers.py          (700+ lines) - NEW: Helpers réutilisables
├── conftest.py         (300+ lines) - NEW: Fixtures centralisées
├── test_main.py        (TBD) - Tests endpoints
├── test_rate_limiting.py (TBD) - Tests rate limiting
├── test_auth.py        (TBD) - Tests authentification
└── test_integration.py (TBD) - Tests intégration
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 2: PATTERNS RÉUTILISABLES API
# ═════════════════════════════════════════════════════════════════════

## Pattern 1: Test Endpoint GET

```python
❌ AVANT (répété dans chaque test):
def test_get_recipe(client: TestClient):
    response = client.get("/api/recipes/1")
    assert response.status_code == 200
    assert "id" in response.json()
    assert "nom" in response.json()

✅ APRÈS (avec helpers):
def test_get_recipe(client, test_recipe_data, api_response_validator):
    response = client.get("/api/recipes/1")
    api_response_validator.assert_success(response)
    api_response_validator.assert_json_response(response, ["id", "nom"])
```

**Helpers disponibles:**
- `APITestClientBuilder.create_test_client()`
- `APIResponseValidator.assert_success()`
- `APIResponseValidator.assert_json_response()`
- `APITestUtils.build_url()`


## Pattern 2: Test Endpoint POST avec Auth

```python
❌ AVANT:
def test_create_recipe(client, test_user):
    headers = {"Authorization": f"Bearer test-token"}
    response = client.post(
        "/api/recipes",
        json={"nom": "Recipe", "portions": 4},
        headers=headers
    )
    assert response.status_code == 201

✅ APRÈS:
def test_create_recipe(authenticated_client, test_recipe_data):
    response = authenticated_client.post(
        "/api/recipes",
        json=test_recipe_data
    )
    api_response_validator.assert_status_code(response, 201)
```

**Fixtures:**
- `authenticated_client` - Client avec token
- `test_recipe_data` - Données test
- `api_response_validator` - Validateur réponse


## Pattern 3: Test Rate Limiting

```python
❌ AVANT:
with patch("src.api.rate_limiting.RateLimiter") as mock:
    mock_limiter = Mock()
    mock_limiter.is_rate_limited.return_value = True
    mock.return_value = mock_limiter
    # test code

✅ APRÈS:
def test_rate_limited(client, mock_rate_limiter):
    mock_rate_limiter.is_rate_limited.return_value = True
    with mock_rate_limiter_context(rate_limited=True):
        response = client.get("/api/recipes")
        assert response.status_code == 429
```

**Helpers:**
- `mock_rate_limiter_context()` - Context manager
- `APIMockBuilder.create_rate_limiter_mock()` - Mock builder


## Pattern 4: Test Cache

```python
❌ AVANT:
cache = Mock()
cache.get.return_value = None
cache.set.return_value = True

✅ APRÈS:
def test_caching(mock_cache):
    mock_cache.get.return_value = {"id": 1, "nom": "Recipe"}
    # test code
```

**Helpers:**
- `mock_cache` fixture
- `mock_cache_context()` context manager


## Pattern 5: Test Error Handling

```python
❌ AVANT:
response = client.get("/api/recipes/999")
assert response.status_code == 404
assert "error" in response.json()

✅ APRÈS:
def test_not_found(client, api_response_validator):
    response = client.get("/api/recipes/999")
    api_response_validator.assert_status_code(response, 404)
    api_response_validator.assert_has_error(response, "not_found")
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 3: AJOUTER UN NOUVEAU TEST API
# ═════════════════════════════════════════════════════════════════════

## Template Endpoint Test

```python
"""Tests pour endpoint /api/recipes"""

import pytest
from tests.api.helpers import (
    APIResponseValidator, create_api_test_data
)


class TestRecipesEndpoint:
    """Tests pour CRUD recettes."""
    
    @pytest.mark.unit
    @pytest.mark.endpoint
    def test_list_recipes(self, client):
        """GET /api/recipes - Lister recettes."""
        # Arrange: données déjà en BD ou mockées
        
        # Act
        response = client.get("/api/recipes")
        
        # Assert
        APIResponseValidator.assert_success(response)
        data = response.json()
        assert isinstance(data, list) or "items" in data


class TestRecipeDetail:
    """Tests pour détail recette."""
    
    @pytest.mark.unit
    def test_get_recipe_success(self, client, test_recipe_data):
        """GET /api/recipes/{id} - Récupérer recette."""
        response = client.get(f"/api/recipes/{test_recipe_data['id']}")
        
        APIResponseValidator.assert_success(response)
        APIResponseValidator.assert_json_response(
            response, 
            ["id", "nom", "portions"]
        )
    
    @pytest.mark.unit
    def test_get_recipe_not_found(self, client, api_response_validator):
        """GET /api/recipes/{id} - Recette inexistante."""
        response = client.get("/api/recipes/999")
        
        api_response_validator.assert_status_code(response, 404)


class TestCreateRecipe:
    """Tests pour créer recette."""
    
    @pytest.mark.unit
    @pytest.mark.endpoint
    def test_create_recipe_success(self, authenticated_client, test_recipe_data):
        """POST /api/recipes - Créer recette."""
        response = authenticated_client.post(
            "/api/recipes",
            json=test_recipe_data
        )
        
        APIResponseValidator.assert_status_code(response, 201)
        APIResponseValidator.assert_json_response(response, ["id"])


class TestUpdateRecipe:
    """Tests pour modifier recette."""
    
    @pytest.mark.unit
    def test_update_recipe_success(
        self, 
        authenticated_client, 
        test_recipe_data,
        api_response_validator
    ):
        """PUT /api/recipes/{id} - Modifier recette."""
        recipe_id = test_recipe_data['id']
        updated_data = {**test_recipe_data, "nom": "Updated Recipe"}
        
        response = authenticated_client.put(
            f"/api/recipes/{recipe_id}",
            json=updated_data
        )
        
        api_response_validator.assert_success(response)


class TestDeleteRecipe:
    """Tests pour supprimer recette."""
    
    @pytest.mark.unit
    def test_delete_recipe_success(self, authenticated_client):
        """DELETE /api/recipes/{id} - Supprimer recette."""
        response = authenticated_client.delete("/api/recipes/1")
        
        assert response.status_code in [200, 204]


class TestRateLimiting:
    """Tests pour rate limiting."""
    
    @pytest.mark.unit
    @pytest.mark.rate_limit
    def test_rate_limited_response(self, client, mock_rate_limiter):
        """Vérifie réponse rate limited."""
        mock_rate_limiter.is_rate_limited.return_value = True
        
        # Multiple requests
        for _ in range(101):
            response = client.get("/api/recipes")
        
        assert response.status_code == 429


class TestAuthentication:
    """Tests pour authentification."""
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_unauthorized_without_token(self, client):
        """POST sans token → 401."""
        response = client.post(
            "/api/recipes",
            json={"nom": "Recipe"}
        )
        
        assert response.status_code == 401
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_authorized_with_token(self, authenticated_client, test_recipe_data):
        """POST avec token → succès."""
        response = authenticated_client.post(
            "/api/recipes",
            json=test_recipe_data
        )
        
        assert response.status_code in [200, 201]


class TestValidation:
    """Tests pour validation input."""
    
    @pytest.mark.unit
    @pytest.mark.parametrize("invalid_input", [
        "",
        None,
        {"nom": ""},
        {"nom": "x" * 1000},
    ])
    def test_invalid_recipe_data(self, authenticated_client, invalid_input):
        """POST avec données invalides → 400."""
        response = authenticated_client.post(
            "/api/recipes",
            json=invalid_input
        )
        
        assert response.status_code == 400
```

## Checklist Nouveau Test API

- [ ] Utiliser `authenticated_client` si besoin auth
- [ ] Utiliser `create_api_test_data()` pour données
- [ ] Utiliser `APIResponseValidator` pour assertions
- [ ] Ajouter @pytest.mark.unit ou .integration
- [ ] Ajouter @pytest.mark.endpoint, .auth, .rate_limit si applicable
- [ ] Couvrir normal + error cases
- [ ] Docstring avec description clear
- [ ] Pas de hardcoding endpoints (utiliser factory ou fixtures)


# ═════════════════════════════════════════════════════════════════════
# SECTION 4: COMMANDES DE TEST
# ═════════════════════════════════════════════════════════════════════

```bash
# ===== TESTS API =====
pytest tests/api/ -v                        # Tous
pytest tests/api/test_main.py -v           # Un fichier
pytest tests/api/ -m endpoint -v           # Endpoints seulement
pytest tests/api/ -m auth -v               # Auth seulement
pytest tests/api/ -m rate_limit -v         # Rate limit seulement
pytest tests/api/ --cov=src/api -v        # Avec couverture

# ===== LANCER API =====
uvicorn src.api.main:app --reload          # Dev
uvicorn src.api.main:app --port 8000       # Custom port

# ===== TESTER ENDPOINTS =====
curl http://localhost:8000/api/recipes     # GET
curl -X POST http://localhost:8000/api/recipes \\
  -H "Content-Type: application/json" \\
  -d '{"nom": "Recipe"}'
curl http://localhost:8000/docs             # Swagger docs
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 5: ORGANISER TESTS PAR ENDPOINT
# ═════════════════════════════════════════════════════════════════════

## Structure Recommandée

```python
# tests/api/test_recipes.py

class TestListRecipes:
    """GET /api/recipes"""

class TestCreateRecipe:
    """POST /api/recipes"""

class TestGetRecipe:
    """GET /api/recipes/{id}"""

class TestUpdateRecipe:
    """PUT /api/recipes/{id}"""

class TestDeleteRecipe:
    """DELETE /api/recipes/{id}"""

class TestRecipeSearch:
    """GET /api/recipes/search?q="""

class TestRecipePagination:
    """GET /api/recipes?page=1&limit=10"""

class TestRecipeFiltering:
    """GET /api/recipes?categoria=plats"""

class TestRecipeErrors:
    """Tests pour erreurs et validation"""

class TestRecipePermissions:
    """Tests pour permissions"""
```

## Par Module

```
tests/api/
├── test_recipes.py        → /api/recipes endpoints
├── test_inventory.py      → /api/inventory endpoints
├── test_planning.py       → /api/planning endpoints
├── test_auth.py          → /api/auth endpoints
├── test_health.py        → /api/health endpoints
└── test_integration.py   → Multi-endpoint workflows
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 6: FIXTURES DISPONIBLES
# ═════════════════════════════════════════════════════════════════════

## Client Fixtures

- `client` - TestClient standard
- `authenticated_client` - Client avec token
- `client_with_headers` - Client avec headers personnalisés

## Mock Fixtures

- `mock_auth` - Mock authentification
- `mock_rate_limiter` - Mock rate limiter
- `mock_cache` - Mock cache
- `mock_db` - Mock BD

## Data Fixtures

- `test_user` - User data
- `test_recipe` - Recipe data
- `test_inventory_item` - Inventory item
- `test_planning` - Planning data
- `test_token` - Auth token

## Helper Fixtures

- `api_client_builder` - APITestClientBuilder
- `api_request_builder` - APIRequestBuilder
- `api_mock_builder` - APIMockBuilder
- `api_response_validator` - APIResponseValidator
- `api_test_patterns` - APITestPatterns
- `api_test_utils` - APITestUtils

## Context Manager Fixtures

- `auth_context` - Mock auth context manager
- `rate_limit_context` - Mock rate limit context manager
- `cache_context` - Mock cache context manager
- `db_context` - Mock DB context manager


# ═════════════════════════════════════════════════════════════════════
# SECTION 7: BEST PRACTICES API TESTING
# ═════════════════════════════════════════════════════════════════════

### ✅ DO's

- ✅ Utiliser `TestClient` pour tests synchrones
- ✅ Utiliser fixtures de conftest.py
- ✅ Utiliser helpers pour builders
- ✅ Tester status codes attendus
- ✅ Valider structure réponse JSON
- ✅ Couvrir erreurs (404, 401, 400, 500)
- ✅ Tester validation input
- ✅ Tester authentication/authorization
- ✅ Tester rate limiting
- ✅ Ajouter docstrings descriptives
- ✅ Utiliser @pytest.mark pour catégoriser


### ❌ DON'Ts

- ❌ Pas de requêtes réelles HTTP (mocker)
- ❌ Pas de dépendances sur ordre test
- ❌ Pas d'endpoints hardcodés (utiliser builders)
- ❌ Pas de données hardcodées (utiliser factories)
- ❌ Pas de tests sans assertions
- ❌ Pas de side effects inattendus
- ❌ Pas de tests trop longs (> 1 min)
- ❌ Pas de duplication (utiliser patterns)


# ═════════════════════════════════════════════════════════════════════
# SECTION 8: COUVERTURE CIBLE
# ═════════════════════════════════════════════════════════════════════

## Estimation Tests Nécessaires

```
src/api/main.py (787 lines)
├─ CRUD endpoints: 5 classes × 4 methods = 20 endpoints
├─ Validation: 10+ edge cases
├─ Auth: 5 tests
├─ Errors: 8 tests
└─ Estimated: 150+ tests

src/api/rate_limiting.py (522 lines)
├─ RateLimitConfig: 5 tests
├─ RateLimiter: 15 tests
├─ Rate limit strategies: 20 tests
├─ Edge cases: 10+ tests
└─ Estimated: 50+ tests

TOTAL API TESTS: 200+ tests
Coverage target: >85%
```


# ═════════════════════════════════════════════════════════════════════
# SECTION 9: CHECKLIST MAINTENANCE MENSUELLE
# ═════════════════════════════════════════════════════════════════════

- [ ] Exécuter tous les tests: `pytest tests/api/ -v`
- [ ] Vérifier couverture: `pytest tests/api/ --cov=src/api`
- [ ] Vérifier endpoints: `uvicorn src.api.main:app --reload`
- [ ] Tester Swagger: http://localhost:8000/docs
- [ ] Vérifier rate limiting fonctionne
- [ ] Vérifier auth fonctionne
- [ ] Ajouter tests pour nouvelles features
- [ ] Refactoriser patterns dupliqués
- [ ] Update documentation


# ═════════════════════════════════════════════════════════════════════
# SECTION 10: TROUBLESHOOTING
# ═════════════════════════════════════════════════════════════════════

## "Test échoue - endpoint retourne 404"

```bash
1. Vérifier endpoint existe: grep -n "@app.get\|@app.post" src/api/main.py
2. Vérifier path correct: print(response.url)
3. Debug: pytest tests/api/test_[file].py -vv -s
4. Vérifier données setup correctement
```

## "Auth test échoue"

```bash
1. Vérifier token: print(authenticated_client.headers)
2. Vérifier auth logic dans src/api/main.py
3. Mock si nécessaire: use mock_auth fixture
4. Debug: pytest -vv -s --tb=long
```

## "Rate limiting test échoue"

```bash
1. Vérifier rate limit config
2. Mock limiter: use mock_rate_limiter fixture
3. Vérifier middleware enregistré
4. Test avec context manager
```

## "Couverture baisse"

```bash
1. Identifier lignes manquantes:
   pytest tests/api/ --cov=src/api --cov-report=term-missing
2. Ajouter tests manquants
3. Couvrir error paths
4. Couvrir tous les status codes
```


════════════════════════════════════════════════════════════════════════

**NEXT STEPS:**
1. Créer tests/api/test_main.py avec endpoints
2. Créer tests/api/test_rate_limiting.py
3. Créer tests/api/test_auth.py
4. Vérifier couverture > 85%
5. Intégrer à CI/CD
"""
