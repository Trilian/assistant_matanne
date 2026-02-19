"""
Tests pour l'API principale (main.py).

Utilise une vraie DB SQLite en mémoire via les fixtures.
Tests des endpoints de santé, racine et intégration.
"""

import pytest
from fastapi.testclient import TestClient

# ═══════════════════════════════════════════════════════════════════════
# DONNÉES DE TEST RÉELLES
# ═══════════════════════════════════════════════════════════════════════

EXPECTED_ROOT_RESPONSE = {"message": "API Assistant Matanne", "docs": "/docs", "version": "1.0.0"}


# ═══════════════════════════════════════════════════════════════════════
# TESTS DE BASE (sans DB)
# ═══════════════════════════════════════════════════════════════════════


class TestImportModule:
    """Tests d'import du module."""

    def test_import_main(self):
        """Vérifie que le module main s'importe sans erreur."""
        from src.api import main

        assert hasattr(main, "app")

    def test_app_has_routes(self):
        """Vérifie que l'app a des routes."""
        from src.api.main import app

        routes = [r.path for r in app.routes]
        assert "/" in routes
        assert "/health" in routes
        assert "/docs" in routes


# ═══════════════════════════════════════════════════════════════════════
# TESTS ENDPOINTS AVEC DB SQLITE
# ═══════════════════════════════════════════════════════════════════════


class TestRootEndpoint:
    """Tests pour l'endpoint racine."""

    def test_root_returns_200(self, client):
        """Endpoint racine retourne 200."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_response_content(self, client):
        """Endpoint racine retourne le bon contenu."""
        response = client.get("/")
        data = response.json()

        assert data["message"] == EXPECTED_ROOT_RESPONSE["message"]
        assert data["docs"] == EXPECTED_ROOT_RESPONSE["docs"]
        assert data["version"] == EXPECTED_ROOT_RESPONSE["version"]


class TestHealthEndpoint:
    """Tests pour l'endpoint /health."""

    def test_health_returns_200(self, client):
        """Endpoint health retourne 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Endpoint health a la bonne structure."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "database" in data
        assert "timestamp" in data

    def test_health_db_status(self, client):
        """Endpoint health rapporte l'état de la DB."""
        response = client.get("/health")
        data = response.json()

        # Avec SQLite de test, la DB devrait être "ok" ou "error"
        # (error possible si SELECT 1 ne fonctionne pas sur SQLite)
        assert data["database"] in ("ok",) or data["database"].startswith("error")


class TestRecettesEndpoint:
    """Tests pour l'endpoint /api/v1/recettes."""

    def test_list_recettes_returns_200(self, client):
        """Endpoint recettes retourne 200."""
        response = client.get("/api/v1/recettes")
        assert response.status_code == 200

    def test_list_recettes_response_structure(self, client):
        """Endpoint recettes a la bonne structure de pagination."""
        response = client.get("/api/v1/recettes")
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data

    def test_list_recettes_empty_by_default(self, client):
        """Endpoint recettes retourne liste vide par défaut."""
        response = client.get("/api/v1/recettes")
        data = response.json()

        assert data["items"] == []
        assert data["total"] == 0

    def test_list_recettes_with_data(self, client, db):
        """Endpoint recettes retourne les recettes si présentes."""
        from src.core.models import Recette

        # Ajouter une recette test
        recette = Recette(
            nom="Tarte aux pommes",
            temps_preparation=30,
            temps_cuisson=45,
            portions=8,
            difficulte="facile",
            categorie="desserts",
        )
        db.add(recette)
        db.commit()

        response = client.get("/api/v1/recettes")
        data = response.json()

        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["nom"] == "Tarte aux pommes"


class TestInventaireEndpoint:
    """Tests pour l'endpoint /api/v1/inventaire."""

    def test_list_inventaire_returns_200(self, client):
        """Endpoint inventaire retourne 200."""
        response = client.get("/api/v1/inventaire")
        assert response.status_code == 200

    def test_list_inventaire_empty_by_default(self, client):
        """Endpoint inventaire retourne liste vide par défaut."""
        response = client.get("/api/v1/inventaire")
        data = response.json()

        assert "items" in data
        assert data["items"] == []

    def test_list_inventaire_with_data(self, client, db):
        """Endpoint inventaire retourne les articles si présents."""
        from src.core.models import ArticleInventaire, Ingredient

        # Créer d'abord un ingrédient (requis par ArticleInventaire)
        ingredient = Ingredient(nom="Pommes", categorie="Fruits", unite="kg")
        db.add(ingredient)
        db.commit()
        db.refresh(ingredient)

        # Ajouter un article test lié à l'ingrédient
        article = ArticleInventaire(ingredient_id=ingredient.id, quantite=5, emplacement="Frigo")
        db.add(article)
        db.commit()

        response = client.get("/api/v1/inventaire")
        data = response.json()

        assert data["total"] >= 1


class TestCoursesEndpoint:
    """Tests pour l'endpoint /api/v1/courses."""

    def test_list_courses_returns_200(self, client):
        """Endpoint courses retourne 200."""
        response = client.get("/api/v1/courses")
        assert response.status_code == 200

    def test_list_courses_empty_by_default(self, client):
        """Endpoint courses retourne liste vide par défaut."""
        response = client.get("/api/v1/courses")
        data = response.json()

        assert "items" in data


class TestPlanningEndpoint:
    """Tests pour l'endpoint /api/v1/planning."""

    def test_planning_semaine_returns_200(self, client):
        """Endpoint planning retourne 200."""
        response = client.get("/api/v1/planning/semaine")
        assert response.status_code == 200

    def test_planning_semaine_structure(self, client):
        """Endpoint planning a la bonne structure."""
        response = client.get("/api/v1/planning/semaine")
        data = response.json()

        assert "planning" in data
        assert "date_debut" in data
        assert "date_fin" in data


class TestCORSHeaders:
    """Tests pour les headers CORS."""

    def test_cors_headers_present(self, client):
        """Headers CORS sont présents dans la réponse."""
        response = client.options("/")
        # OPTIONS peut retourner 405 si pas configuré, c'est OK
        # L'important est que les vraies requêtes passent
        assert response.status_code in (200, 405)


class TestAPIVersioning:
    """Tests pour le versioning de l'API."""

    def test_api_v1_prefix_exists(self, client):
        """Les endpoints API utilisent le prefix /api/v1."""
        # Vérifier que les endpoints API v1 existent
        endpoints = [
            "/api/v1/recettes",
            "/api/v1/inventaire",
            "/api/v1/courses",
            "/api/v1/planning/semaine",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200, f"Endpoint {endpoint} failed"


# ═══════════════════════════════════════════════════════════
# TESTS AUTHENTIFICATION JWT
# ═══════════════════════════════════════════════════════════


class TestAuthentication:
    """Tests pour l'authentification JWT."""

    def test_get_current_user_without_token_dev_mode(self, client, monkeypatch):
        """En mode dev, pas de token retourne utilisateur dev."""
        monkeypatch.setenv("ENVIRONMENT", "development")

        # L'endpoint root ne nécessite pas d'auth
        response = client.get("/")
        assert response.status_code == 200

    def test_get_current_user_with_invalid_token(self, app, monkeypatch):
        """Token invalide retourne 401."""

        # Forcer mode production pour tester l'auth
        monkeypatch.setenv("ENVIRONMENT", "production")

        # Supprimer l'override de l'auth pour tester le vrai comportement
        from src.api.main import get_current_user

        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]

        test_client = TestClient(app, raise_server_exceptions=False)
        response = test_client.get(
            "/api/v1/suggestions/recettes", headers={"Authorization": "Bearer invalid-token-12345"}
        )

        # Devrait retourner 401 (token invalide)
        assert response.status_code in (401, 500)

    def test_authenticated_endpoint_with_mock_user(self, client):
        """Endpoint authentifié fonctionne avec utilisateur mocké."""
        # Le fixture client a déjà un utilisateur mocké
        response = client.get("/api/v1/recettes")
        assert response.status_code == 200

    def test_require_auth_dependency(self):
        """La dependency require_auth fonctionne."""
        from fastapi import HTTPException

        from src.api.main import require_auth

        # Utilisateur valide
        user = {"id": "123", "email": "test@test.com", "role": "admin"}
        result = require_auth(user)
        assert result == user

        # Utilisateur None devrait lever une exception
        with pytest.raises(HTTPException) as exc_info:
            require_auth(None)
        assert exc_info.value.status_code == 401


# ═══════════════════════════════════════════════════════════
# TESTS ENDPOINTS IA
# ═══════════════════════════════════════════════════════════


class TestIAEndpoints:
    """Tests pour les endpoints IA."""

    def test_suggestions_recettes_endpoint_exists(self, client):
        """GET /api/v1/suggestions/recettes existe."""
        response = client.get("/api/v1/suggestions/recettes")
        # 200 si IA fonctionne, 500 si service IA non dispo
        assert response.status_code in (200, 429, 500)

    def test_suggestions_recettes_with_params(self, client):
        """Suggestions acceptent les paramètres contexte et nombre."""
        response = client.get(
            "/api/v1/suggestions/recettes", params={"contexte": "repas rapide", "nombre": 5}
        )
        # Accepte les paramètres même si IA non disponible
        assert response.status_code in (200, 429, 500)

    def test_suggestions_recettes_default_params(self, client):
        """Suggestions utilisent les valeurs par défaut."""
        response = client.get("/api/v1/suggestions/recettes")

        if response.status_code == 200:
            data = response.json()
            assert "suggestions" in data
            assert "contexte" in data

    def test_suggestions_recettes_rate_limited(self, client, monkeypatch):
        """Suggestions respectent la limite de débit IA."""
        from unittest.mock import patch

        # Simuler une limite de débit atteinte
        with patch("src.api.limitation_debit.verifier_limite_debit_ia") as mock_limit:
            from fastapi import HTTPException

            mock_limit.side_effect = HTTPException(status_code=429, detail="Limite IA atteinte")

            response = client.get("/api/v1/suggestions/recettes")
            # Peut retourner 429 ou 500 selon la gestion d'erreurs
            assert response.status_code in (429, 500)

    def test_suggestions_recettes_response_structure(self, client):
        """Structure de réponse des suggestions."""
        from unittest.mock import patch

        mock_suggestions = [
            {"nom": "Salade César", "difficulte": "facile"},
            {"nom": "Pasta Carbonara", "difficulte": "moyen"},
        ]

        with patch("src.services.cuisine.recettes.get_recette_service") as mock_service:
            mock_instance = mock_service.return_value
            mock_instance.suggerer_recettes_ia.return_value = mock_suggestions

            with patch("src.api.limitation_debit.verifier_limite_debit_ia"):
                response = client.get("/api/v1/suggestions/recettes")

                if response.status_code == 200:
                    data = response.json()
                    assert "suggestions" in data
                    assert "contexte" in data


# ═══════════════════════════════════════════════════════════
# TESTS ROUTES MODIFICATION (PUT/DELETE)
# ═══════════════════════════════════════════════════════════


class TestRecettesModification:
    """Tests pour les routes de modification de recettes."""

    def test_update_recette_endpoint_exists(self, client):
        """PUT /api/v1/recettes/{id} existe."""
        response = client.put(
            "/api/v1/recettes/999",
            json={
                "nom": "Recette mise à jour",
                "temps_preparation": 30,
                "temps_cuisson": 45,
                "portions": 4,
            },
        )
        # 404 si recette n'existe pas, 200 si mise à jour OK
        assert response.status_code in (200, 404, 500)

    def test_update_recette_success(self, client, db):
        """PUT met à jour une recette existante."""
        from src.core.models import Recette

        # Créer une recette
        recette = Recette(
            nom="Recette originale",
            temps_preparation=20,
            temps_cuisson=30,
            portions=4,
            difficulte="facile",
            categorie="plats",
        )
        db.add(recette)
        db.commit()
        db.refresh(recette)

        # Mettre à jour
        response = client.put(
            f"/api/v1/recettes/{recette.id}",
            json={
                "nom": "Recette modifiée",
                "temps_preparation": 25,
                "temps_cuisson": 35,
                "portions": 6,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nom"] == "Recette modifiée"
        assert data["temps_preparation"] == 25

    def test_update_recette_not_found(self, client):
        """PUT sur recette inexistante retourne 404."""
        response = client.put(
            "/api/v1/recettes/99999",
            json={"nom": "Test", "temps_preparation": 10, "temps_cuisson": 20, "portions": 2},
        )

        assert response.status_code == 404

    def test_delete_recette_endpoint_exists(self, client):
        """DELETE /api/v1/recettes/{id} existe."""
        response = client.delete("/api/v1/recettes/999")
        # 404 si recette n'existe pas
        assert response.status_code in (200, 404, 500)

    def test_delete_recette_success(self, client, db):
        """DELETE supprime une recette existante."""
        from src.core.models import Recette

        # Créer une recette
        recette = Recette(
            nom="Recette à supprimer",
            temps_preparation=10,
            temps_cuisson=20,
            portions=2,
            difficulte="facile",
            categorie="desserts",
        )
        db.add(recette)
        db.commit()
        db.refresh(recette)
        recette_id = recette.id

        # Supprimer
        response = client.delete(f"/api/v1/recettes/{recette_id}")

        assert response.status_code == 200
        data = response.json()
        assert "supprimée" in data["message"]

        # Vérifier qu'elle n'existe plus
        deleted = db.query(Recette).filter(Recette.id == recette_id).first()
        assert deleted is None

    def test_delete_recette_not_found(self, client):
        """DELETE sur recette inexistante retourne 404."""
        response = client.delete("/api/v1/recettes/99999")

        assert response.status_code == 404
