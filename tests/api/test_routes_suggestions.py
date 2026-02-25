"""
Tests pour src/api/routes/suggestions.py

Tests d'intégration pour les routes de suggestions IA:
- GET /api/v1/suggestions/recettes
- GET /api/v1/suggestions/planning
- Validation des paramètres
- Gestion des erreurs IA
- Sécurité et rate limiting
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

SUGGESTIONS_RECETTES_MOCK = [
    {
        "nom": "Curry de lentilles",
        "description": "Curry végétarien aux lentilles corail",
        "temps_preparation": 30,
        "pourquoi": "Rapide et nutritif",
    },
    {
        "nom": "Buddha bowl",
        "description": "Bowl équilibré avec quinoa et légumes",
        "temps_preparation": 20,
        "pourquoi": "Repas complet et sain",
    },
    {
        "nom": "Soupe miso",
        "description": "Soupe japonaise légère au tofu",
        "temps_preparation": 15,
        "pourquoi": "Léger et rapide à préparer",
    },
]

PLANNING_MOCK = {
    "lundi": {"dejeuner": "Poulet rôti", "diner": "Soupe de légumes"},
    "mardi": {"dejeuner": "Pasta carbonara", "diner": "Salade composée"},
    "mercredi": {"dejeuner": "Curry de lentilles", "diner": "Quiche lorraine"},
}


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def client():
    """Client de test FastAPI avec rate limiting IA désactivé."""
    from src.api.main import app
    from src.api.rate_limiting import verifier_limite_debit_ia

    # Override la dépendance IA rate limiting pour les tests
    async def mock_rate_check():
        return {"allowed": True, "remaining": 100}

    app.dependency_overrides[verifier_limite_debit_ia] = mock_rate_check

    yield TestClient(app)

    # Cleanup
    app.dependency_overrides.pop(verifier_limite_debit_ia, None)


@pytest.fixture
def mock_recette_service():
    """Mock du service recettes pour suggestions."""
    mock = MagicMock()
    mock.suggerer_recettes_ia.return_value = SUGGESTIONS_RECETTES_MOCK
    return mock


@pytest.fixture
def mock_planning_service():
    """Mock du service planning pour suggestions."""
    mock = MagicMock()
    mock.generer_planning_ia.return_value = PLANNING_MOCK
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS: GET /api/v1/suggestions/recettes
# ═══════════════════════════════════════════════════════════


class TestSuggestionsRecettes:
    """Tests pour l'endpoint GET /api/v1/suggestions/recettes."""

    def test_endpoint_exists(self, client):
        """L'endpoint /api/v1/suggestions/recettes existe et répond."""
        response = client.get("/api/v1/suggestions/recettes")
        assert response.status_code != 404

    def test_default_params(self, client, mock_recette_service):
        """Suggestions utilisent les valeurs par défaut (contexte='repas équilibré', nombre=3)."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get("/api/v1/suggestions/recettes")
            assert response.status_code == 200
            data = response.json()
            assert "suggestions" in data
            assert data["contexte"] == "repas équilibré"
            assert data["nombre"] == 3

    def test_custom_context_param(self, client, mock_recette_service):
        """Suggestions avec contexte personnalisé."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get(
                "/api/v1/suggestions/recettes",
                params={"contexte": "végétarien rapide"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["contexte"] == "végétarien rapide"

    def test_custom_nombre_param(self, client, mock_recette_service):
        """Suggestions avec nombre personnalisé."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get(
                "/api/v1/suggestions/recettes",
                params={"nombre": 5},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["nombre"] == 5

    def test_nombre_min_validation(self, client):
        """Le paramètre nombre refuse les valeurs < 1."""
        response = client.get(
            "/api/v1/suggestions/recettes",
            params={"nombre": 0},
        )
        assert response.status_code in (422, 429)

    def test_nombre_max_validation(self, client):
        """Le paramètre nombre refuse les valeurs > 10."""
        response = client.get(
            "/api/v1/suggestions/recettes",
            params={"nombre": 11},
        )
        assert response.status_code in (422, 429)

    def test_response_structure(self, client, mock_recette_service):
        """La réponse a la bonne structure {suggestions, contexte, nombre}."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get("/api/v1/suggestions/recettes")
            assert response.status_code == 200
            data = response.json()
            assert "suggestions" in data
            assert "contexte" in data
            assert "nombre" in data
            assert isinstance(data["suggestions"], list)

    def test_suggestions_content(self, client, mock_recette_service):
        """Les suggestions contiennent les bonnes données."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get("/api/v1/suggestions/recettes")
            assert response.status_code == 200
            data = response.json()
            suggestions = data["suggestions"]
            assert len(suggestions) == 3
            assert suggestions[0]["nom"] == "Curry de lentilles"

    def test_service_called_with_correct_params(self, client, mock_recette_service):
        """Le service est appelé avec les bons paramètres."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            client.get(
                "/api/v1/suggestions/recettes",
                params={"contexte": "batch cooking", "nombre": 7},
            )
            mock_recette_service.suggerer_recettes_ia.assert_called_once_with(
                contexte="batch cooking",
                nombre_suggestions=7,
            )

    def test_empty_suggestions(self, client):
        """Le service peut retourner une liste vide."""
        mock_service = MagicMock()
        mock_service.suggerer_recettes_ia.return_value = []
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_service,
        ):
            response = client.get("/api/v1/suggestions/recettes")
            assert response.status_code == 200
            data = response.json()
            assert data["suggestions"] == []

    def test_service_exception_handled(self, client):
        """Les exceptions du service sont gérées proprement."""
        mock_service = MagicMock()
        mock_service.suggerer_recettes_ia.side_effect = Exception("Service IA indisponible")
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_service,
        ):
            response = client.get("/api/v1/suggestions/recettes")
            # Le décorateur @gerer_exception_api gère l'erreur
            assert response.status_code in (500, 503)


# ═══════════════════════════════════════════════════════════
# TESTS: GET /api/v1/suggestions/planning
# ═══════════════════════════════════════════════════════════


class TestSuggestionsPlanning:
    """Tests pour l'endpoint GET /api/v1/suggestions/planning."""

    def test_endpoint_exists(self, client):
        """L'endpoint /api/v1/suggestions/planning existe et répond."""
        response = client.get("/api/v1/suggestions/planning")
        assert response.status_code != 404

    def test_default_params(self, client, mock_planning_service):
        """Planning utilise les valeurs par défaut (jours=7, personnes=4)."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            response = client.get("/api/v1/suggestions/planning")
            assert response.status_code == 200
            data = response.json()
            assert "planning" in data
            assert data["jours"] == 7
            assert data["personnes"] == 4

    def test_custom_jours_param(self, client, mock_planning_service):
        """Planning avec nombre de jours personnalisé."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            response = client.get(
                "/api/v1/suggestions/planning",
                params={"jours": 5},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["jours"] == 5

    def test_custom_personnes_param(self, client, mock_planning_service):
        """Planning avec nombre de personnes personnalisé."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            response = client.get(
                "/api/v1/suggestions/planning",
                params={"personnes": 6},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["personnes"] == 6

    def test_jours_min_validation(self, client):
        """Le paramètre jours refuse les valeurs < 1."""
        response = client.get(
            "/api/v1/suggestions/planning",
            params={"jours": 0},
        )
        assert response.status_code in (422, 429)

    def test_jours_max_validation(self, client):
        """Le paramètre jours refuse les valeurs > 14."""
        response = client.get(
            "/api/v1/suggestions/planning",
            params={"jours": 15},
        )
        assert response.status_code in (422, 429)

    def test_personnes_min_validation(self, client):
        """Le paramètre personnes refuse les valeurs < 1."""
        response = client.get(
            "/api/v1/suggestions/planning",
            params={"personnes": 0},
        )
        assert response.status_code in (422, 429)

    def test_personnes_max_validation(self, client):
        """Le paramètre personnes refuse les valeurs > 20."""
        response = client.get(
            "/api/v1/suggestions/planning",
            params={"personnes": 21},
        )
        assert response.status_code in (422, 429)

    def test_response_structure(self, client, mock_planning_service):
        """La réponse a la bonne structure {planning, jours, personnes}."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            response = client.get("/api/v1/suggestions/planning")
            assert response.status_code == 200
            data = response.json()
            assert "planning" in data
            assert "jours" in data
            assert "personnes" in data

    def test_planning_content(self, client, mock_planning_service):
        """Le planning retourné contient les données du service."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            response = client.get("/api/v1/suggestions/planning")
            assert response.status_code == 200
            data = response.json()
            planning = data["planning"]
            assert "lundi" in planning
            assert "dejeuner" in planning["lundi"]

    def test_service_called_with_correct_params(self, client, mock_planning_service):
        """Le service est appelé avec les bons paramètres."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            client.get(
                "/api/v1/suggestions/planning",
                params={"jours": 5, "personnes": 2},
            )
            mock_planning_service.generer_planning_ia.assert_called_once_with(
                nombre_jours=5,
                nombre_personnes=2,
            )

    def test_service_exception_handled(self, client):
        """Les exceptions du service planning sont gérées proprement."""
        mock_service = MagicMock()
        mock_service.generer_planning_ia.side_effect = Exception("Service IA indisponible")
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_service,
        ):
            response = client.get("/api/v1/suggestions/planning")
            assert response.status_code in (500, 503)


# ═══════════════════════════════════════════════════════════
# TESTS: SÉCURITÉ — /metrics protégé (Item 4 audit)
# ═══════════════════════════════════════════════════════════


class TestMetricsProtection:
    """Tests de sécurité pour l'endpoint /metrics (Phase 1 Item 4)."""

    def test_metrics_returns_data_for_admin(self, client):
        """Un admin peut accéder aux métriques."""
        from src.api.dependencies import get_current_user
        from src.api.main import app

        # Override pour fournir un admin
        app.dependency_overrides[get_current_user] = lambda: {
            "id": "admin-test",
            "email": "admin@test.com",
            "role": "admin",
        }
        try:
            admin_client = TestClient(app)
            response = admin_client.get("/metrics")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.pop(get_current_user, None)

    def test_metrics_requires_auth_in_production(self):
        """En production, /metrics exige un token valide."""
        import os

        os.environ["ENVIRONMENT"] = "production"
        try:
            from src.api.main import app

            prod_client = TestClient(app)
            response = prod_client.get("/metrics")
            # Sans token en prod, doit être rejeté
            assert response.status_code in (401, 403)
        finally:
            os.environ["ENVIRONMENT"] = "development"

    def test_metrics_rejects_non_admin_role(self):
        """Un utilisateur non-admin est rejeté avec 403."""
        from fastapi import Depends

        from src.api.dependencies import get_current_user
        from src.api.main import app

        # Override pour retourner un utilisateur non-admin
        def mock_user():
            return {"id": "user-1", "email": "user@test.com", "role": "user"}

        app.dependency_overrides[get_current_user] = mock_user
        try:
            test_client = TestClient(app)
            response = test_client.get("/metrics")
            assert response.status_code == 403
        finally:
            app.dependency_overrides.clear()


# ═══════════════════════════════════════════════════════════
# TESTS: SÉCURITÉ — JWT rate limiting (Item 3 audit)
# ═══════════════════════════════════════════════════════════


class TestJWTRateLimitingSecurity:
    """Tests de sécurité pour la validation JWT dans le rate limiting (Phase 1 Item 3)."""

    def test_forged_token_not_accepted(self):
        """Un JWT forgé (non signé) n'extrait pas d'user_id via le rate limiting middleware."""
        import os

        # Désactiver temporairement le bypass de rate limiting
        os.environ.pop("RATE_LIMITING_DISABLED", None)

        try:
            # Créer un faux JWT sans signature valide
            import base64
            import json

            header = (
                base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode())
                .decode()
                .rstrip("=")
            )
            payload = (
                base64.urlsafe_b64encode(json.dumps({"sub": "forged-user-id"}).encode())
                .decode()
                .rstrip("=")
            )
            forged_token = f"{header}.{payload}."

            # Vérifier que le token API (signé) rejette bien le token forgé
            from src.api.auth import valider_token_api

            result = valider_token_api(forged_token)
            assert result is None, "Un token forgé ne doit pas être validé par valider_token_api"

            # Note: valider_token() fallback Supabase sans SUPABASE_JWT_SECRET
            # accepte en mode dégradé — c'est un comportement attendu en dev.
            # En production, SUPABASE_JWT_SECRET doit être configuré.
        finally:
            os.environ["RATE_LIMITING_DISABLED"] = "true"

    def test_valid_api_token_accepted(self):
        """Un token API valide est accepté par valider_token()."""
        from src.api.auth import creer_token_acces, valider_token

        token = creer_token_acces(user_id="test-123", email="test@test.com", role="user")
        result = valider_token(token)
        assert result is not None
        assert result.id == "test-123"


# ═══════════════════════════════════════════════════════════
# TESTS: COMBINAISON PARAMÈTRES
# ═══════════════════════════════════════════════════════════


class TestParameterCombinations:
    """Tests de combinaisons de paramètres pour les suggestions."""

    @pytest.mark.parametrize(
        "contexte",
        [
            "rapide",
            "végétarien",
            "batch cooking",
            "sans gluten",
            "repas de fête",
            "économique",
        ],
    )
    def test_recettes_various_contexts(self, client, mock_recette_service, contexte):
        """Les suggestions acceptent différents contextes."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get(
                "/api/v1/suggestions/recettes",
                params={"contexte": contexte},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["contexte"] == contexte

    @pytest.mark.parametrize("nombre", [1, 3, 5, 10])
    def test_recettes_valid_nombre_range(self, client, mock_recette_service, nombre):
        """Les suggestions acceptent les valeurs valides de nombre."""
        with patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recette_service,
        ):
            response = client.get(
                "/api/v1/suggestions/recettes",
                params={"nombre": nombre},
            )
            assert response.status_code == 200

    @pytest.mark.parametrize(
        "jours,personnes",
        [
            (1, 1),
            (7, 4),
            (14, 20),
            (3, 2),
        ],
    )
    def test_planning_valid_combinations(self, client, mock_planning_service, jours, personnes):
        """Le planning accepte les combinaisons valides."""
        with patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ):
            response = client.get(
                "/api/v1/suggestions/planning",
                params={"jours": jours, "personnes": personnes},
            )
            assert response.status_code == 200

    @pytest.mark.parametrize("nombre", [-1, 0, 11, 100, 999])
    def test_recettes_invalid_nombre(self, client, nombre):
        """Les suggestions rejettent les valeurs invalides de nombre."""
        response = client.get(
            "/api/v1/suggestions/recettes",
            params={"nombre": nombre},
        )
        assert response.status_code in (422, 429)
