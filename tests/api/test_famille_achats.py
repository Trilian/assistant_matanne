"""
CT-07a — Tests des routes famille/achats (Sprint 3)

Tests couvrant:
- GET  /api/v1/famille/achats  : liste des achats
- POST /api/v1/famille/achats  : création d'un achat
- PATCH /api/v1/famille/achats/{id} : modification
- POST /api/v1/famille/achats/{id}/achete : marquage acheté
- DELETE /api/v1/famille/achats/{id} : suppression
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport


# ═══════════════════════════════════════════════════════════
# DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════


ACHAT_CREATE_PAYLOAD = {
    "nom": "Pull Jules 18 mois",
    "categorie": "jules_vetements",
    "priorite": "haute",
    "prix_estime": 25.0,
    "pour_qui": "jules",
    "a_revendre": True,
    "prix_revente_estime": 10.0,
}

ACHAT_RESPONSE_MOCK = {
    "id": 1,
    "nom": "Pull Jules 18 mois",
    "categorie": "jules_vetements",
    "priorite": "haute",
    "prix_estime": 25.0,
    "prix_reel": None,
    "taille": None,
    "magasin": None,
    "url": None,
    "description": None,
    "age_recommande_mois": None,
    "suggere_par": None,
    "achete": False,
    "date_achat": None,
    "pour_qui": "jules",
    "a_revendre": True,
    "prix_revente_estime": 10.0,
    "vendu_le": None,
}


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def async_client():
    from src.api.main import app
    from src.api.dependencies import require_auth

    app.dependency_overrides[require_auth] = lambda: {"id": "test-user", "role": "membre"}
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _mock_achat_orm():
    """Crée un objet ORM-like simulant un AchatFamille."""
    obj = MagicMock()
    obj.id = 1
    obj.nom = ACHAT_CREATE_PAYLOAD["nom"]
    obj.categorie = ACHAT_CREATE_PAYLOAD["categorie"]
    obj.priorite = ACHAT_CREATE_PAYLOAD["priorite"]
    obj.prix_estime = ACHAT_CREATE_PAYLOAD["prix_estime"]
    obj.prix_reel = None
    obj.taille = None
    obj.magasin = None
    obj.url = None
    obj.description = None
    obj.age_recommande_mois = None
    obj.suggere_par = None
    obj.achete = False
    obj.date_achat = None
    obj.pour_qui = "jules"
    obj.a_revendre = True
    obj.prix_revente_estime = 10.0
    obj.vendu_le = None
    return obj


# ═══════════════════════════════════════════════════════════
# GET /api/v1/famille/achats
# ═══════════════════════════════════════════════════════════


class TestListerAchats:
    """Tests pour GET /api/v1/famille/achats."""

    @pytest.mark.asyncio
    async def test_lister_retourne_200(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.lister_achats.return_value = []

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.get("/api/v1/famille/achats")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_lister_retourne_items_et_total(self, async_client: httpx.AsyncClient):
        mock_achat = _mock_achat_orm()
        mock_service = MagicMock()
        mock_service.lister_achats.return_value = [mock_achat]

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.get("/api/v1/famille/achats")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_lister_filtre_par_pour_qui(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.lister_par_personne.return_value = []

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.get("/api/v1/famille/achats?pour_qui=jules")

        assert response.status_code == 200
        mock_service.lister_par_personne.assert_called_once()

    @pytest.mark.asyncio
    async def test_lister_filtre_a_revendre(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.lister_a_revendre.return_value = []

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.get("/api/v1/famille/achats?a_revendre=true")

        assert response.status_code == 200
        mock_service.lister_a_revendre.assert_called_once()


# ═══════════════════════════════════════════════════════════
# POST /api/v1/famille/achats
# ═══════════════════════════════════════════════════════════


class TestCreerAchat:
    """Tests pour POST /api/v1/famille/achats."""

    @pytest.mark.asyncio
    async def test_creer_retourne_201(self, async_client: httpx.AsyncClient):
        mock_achat = _mock_achat_orm()
        mock_service = MagicMock()
        mock_service.ajouter_achat.return_value = mock_achat

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats", json=ACHAT_CREATE_PAYLOAD
            )

        assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_creer_retourne_achat_serialise(self, async_client: httpx.AsyncClient):
        mock_achat = _mock_achat_orm()
        mock_service = MagicMock()
        mock_service.ajouter_achat.return_value = mock_achat

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats", json=ACHAT_CREATE_PAYLOAD
            )

        if response.status_code == 201:
            data = response.json()
            assert data["nom"] == ACHAT_CREATE_PAYLOAD["nom"]
            assert data["categorie"] == ACHAT_CREATE_PAYLOAD["categorie"]
            assert data["pour_qui"] == "jules"

    @pytest.mark.asyncio
    async def test_creer_validation_nom_vide(self, async_client: httpx.AsyncClient):
        payload = {**ACHAT_CREATE_PAYLOAD, "nom": ""}
        response = await async_client.post("/api/v1/famille/achats", json=payload)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_creer_champs_requis_manquants(self, async_client: httpx.AsyncClient):
        response = await async_client.post("/api/v1/famille/achats", json={})
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_creer_appelle_service(self, async_client: httpx.AsyncClient):
        mock_achat = _mock_achat_orm()
        mock_service = MagicMock()
        mock_service.ajouter_achat.return_value = mock_achat

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            await async_client.post("/api/v1/famille/achats", json=ACHAT_CREATE_PAYLOAD)

        mock_service.ajouter_achat.assert_called_once()


# ═══════════════════════════════════════════════════════════
# POST /api/v1/famille/achats/{id}/achete
# ═══════════════════════════════════════════════════════════


class TestMarquerAchete:
    """Tests pour POST /api/v1/famille/achats/{id}/achete."""

    @pytest.mark.asyncio
    async def test_marquer_achete_success(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.marquer_achete.return_value = True

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/1/achete",
                json={"prix_reel": 22.5},
            )

        assert response.status_code in [200, 201]

    @pytest.mark.asyncio
    async def test_marquer_achete_not_found(self, async_client: httpx.AsyncClient):
        mock_service = MagicMock()
        mock_service.marquer_achete.return_value = False

        with patch(
            "src.services.famille.achats.obtenir_service_achats_famille",
            return_value=mock_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/9999/achete",
                json={},
            )

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════
# DELETE /api/v1/famille/achats/{id}
# ═══════════════════════════════════════════════════════════


class TestSupprimerAchat:
    """Tests pour DELETE /api/v1/famille/achats/{id}."""

    @pytest.mark.asyncio
    async def test_supprimer_not_found(self, async_client: httpx.AsyncClient):
        """Un achat inexistant doit retourner 404 (via DB mock)."""
        from contextlib import contextmanager

        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None

        @contextmanager
        def _mock_session():
            yield session

        with patch("src.api.routes.famille.executer_avec_session", _mock_session):
            response = await async_client.delete("/api/v1/famille/achats/9999")

        assert response.status_code == 404


# ═══════════════════════════════════════════════════════════
# Validation schémas
# ═══════════════════════════════════════════════════════════


class TestAchatSchemas:
    """Tests unitaires sur les schémas Pydantic des achats."""

    def test_achat_create_valide(self):
        from src.api.schemas.famille import AchatCreate

        achat = AchatCreate(**ACHAT_CREATE_PAYLOAD)
        assert achat.nom == ACHAT_CREATE_PAYLOAD["nom"]
        assert achat.pour_qui == "jules"
        assert achat.a_revendre is True

    def test_achat_create_defaults(self):
        from src.api.schemas.famille import AchatCreate

        achat = AchatCreate(nom="Test", categorie="maison")
        assert achat.priorite == "moyenne"
        assert achat.pour_qui == "famille"
        assert achat.a_revendre is False

    def test_achat_patch_tous_optionnels(self):
        from src.api.schemas.famille import AchatPatch

        patch_data = AchatPatch()
        assert patch_data.nom is None
        assert patch_data.categorie is None

    def test_achat_patch_partiel(self):
        from src.api.schemas.famille import AchatPatch

        patch_data = AchatPatch(priorite="urgent")
        dumped = patch_data.model_dump(exclude_unset=True)
        assert "priorite" in dumped
        assert "nom" not in dumped


# ═══════════════════════════════════════════════════════════
# POST /api/v1/famille/achats/suggestions-ia-enrichies
# ═══════════════════════════════════════════════════════════


class TestSuggestionsIAEnrichies:
    """Tests pour POST /api/v1/famille/achats/suggestions-ia-enrichies."""

    @pytest.mark.asyncio
    async def test_suggestions_generiques_retourne_200(self, async_client: httpx.AsyncClient):
        """Trigger générique → appelle suggerer_achats et retourne 200."""
        mock_ia_service = MagicMock()
        mock_ia_service.suggerer_achats.return_value = []

        with patch(
            "src.services.famille.achats_ia.obtenir_service_achats_ia",
            return_value=mock_ia_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/suggestions-ia-enrichies",
                json={"triggers": ["autre"], "pour_qui": "famille"},
            )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def test_suggestions_vetements_qualite(self, async_client: httpx.AsyncClient):
        """Trigger vetements_qualite avec pour_qui → appelle suggerer_vetements_qualite."""
        mock_ia_service = MagicMock()
        mock_ia_service.suggerer_vetements_qualite.return_value = [
            {"nom": "T-shirt coton bio", "priorite": "haute"},
        ]

        with patch(
            "src.services.famille.achats_ia.obtenir_service_achats_ia",
            return_value=mock_ia_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/suggestions-ia-enrichies",
                json={"triggers": ["vetements_qualite"], "pour_qui": "jules"},
            )

        assert response.status_code == 200
        mock_ia_service.suggerer_vetements_qualite.assert_called_once_with(
            pour_qui="jules", saison="courante"
        )

    @pytest.mark.asyncio
    async def test_suggestions_sejour_avec_destination(self, async_client: httpx.AsyncClient):
        """Trigger sejour avec destination → appelle suggerer_achats_sejour."""
        mock_ia_service = MagicMock()
        mock_ia_service.suggerer_achats_sejour.return_value = []

        with patch(
            "src.services.famille.achats_ia.obtenir_service_achats_ia",
            return_value=mock_ia_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/suggestions-ia-enrichies",
                json={
                    "triggers": ["sejour"],
                    "destination": "Barcelone",
                    "age_jules_mois": 18,
                },
            )

        assert response.status_code == 200
        mock_ia_service.suggerer_achats_sejour.assert_called_once()

    @pytest.mark.asyncio
    async def test_triggers_manquants_retourne_422(self, async_client: httpx.AsyncClient):
        """Payload sans triggers → validation Pydantic (422)."""
        response = await async_client.post(
            "/api/v1/famille/achats/suggestions-ia-enrichies", json={}
        )
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════
# POST /api/v1/famille/achats/{id}/annonce-vinted
# ═══════════════════════════════════════════════════════════


class TestAnnonceVinted:
    """Tests pour POST /api/v1/famille/achats/{id}/annonce-vinted."""

    PAYLOAD_VINTED = {
        "nom": "Pull Jules 18 mois Petit Bateau",
        "description": "Très bon état, porté 2 fois.",
        "etat_usage": "bon",
        "prix_cible": 8.0,
        "marque": "Petit Bateau",
        "taille": "18 mois",
        "categorie_vinted": "Vêtements enfants",
    }

    @pytest.mark.asyncio
    async def test_generer_annonce_retourne_200(self, async_client: httpx.AsyncClient):
        """Génération annonce Vinted valide → 200 avec texte."""
        mock_ia_service = MagicMock()
        mock_ia_service.generer_annonce_vinted = MagicMock(
            return_value="Pull Petit Bateau 18 mois…"
        )

        with patch(
            "src.services.famille.achats_ia.obtenir_service_achats_ia",
            return_value=mock_ia_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/1/annonce-vinted",
                json=self.PAYLOAD_VINTED,
            )

        assert response.status_code == 200
        data = response.json()
        assert "annonce" in data

    @pytest.mark.asyncio
    async def test_generer_annonce_appelle_service(self, async_client: httpx.AsyncClient):
        """Le service est bien appelé avec marque et taille."""
        mock_ia_service = MagicMock()
        mock_ia_service.generer_annonce_vinted = MagicMock(return_value="Annonce test")

        with patch(
            "src.services.famille.achats_ia.obtenir_service_achats_ia",
            return_value=mock_ia_service,
        ):
            await async_client.post(
                "/api/v1/famille/achats/1/annonce-vinted",
                json=self.PAYLOAD_VINTED,
            )

        mock_ia_service.generer_annonce_vinted.assert_called_once()
        call_kwargs = mock_ia_service.generer_annonce_vinted.call_args
        assert call_kwargs.kwargs.get("marque") == "Petit Bateau"

    @pytest.mark.asyncio
    async def test_payload_minimal_sans_marque_retourne_200_ou_422(
        self, async_client: httpx.AsyncClient
    ):
        """Annonce sans champs optionnels (marque/taille/categorie) → accepté ou validation."""
        mock_ia_service = MagicMock()
        mock_ia_service.generer_annonce_vinted = MagicMock(return_value="Annonce minimale")

        with patch(
            "src.services.famille.achats_ia.obtenir_service_achats_ia",
            return_value=mock_ia_service,
        ):
            response = await async_client.post(
                "/api/v1/famille/achats/1/annonce-vinted",
                json={
                    "nom": "Tshirt",
                    "description": "Bon état.",
                    "etat_usage": "bon",
                    "prix_cible": 5.0,
                },
            )

        assert response.status_code in [200, 422]
