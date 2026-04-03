"""
CT-14 - Tests des routes IA avancée (IA avancée)

Couvre src/api/routes/ia_avancee.py — 14 endpoints :
- GET  /api/v1/ia-avancee/suggestions-achats
- POST /api/v1/ia-avancee/planning-adaptatif
- POST /api/v1/ia-avancee/diagnostic-plante
- GET  /api/v1/ia-avancee/prevision-depenses
- POST /api/v1/ia-avancee/idees-cadeaux
- POST /api/v1/ia-avancee/analyse-photo
- GET  /api/v1/ia-avancee/optimisation-routines
- POST /api/v1/ia-avancee/analyse-document
- POST /api/v1/ia-avancee/estimation-travaux
- POST /api/v1/ia-avancee/planning-voyage
- GET  /api/v1/ia-avancee/recommandations-energie
- GET  /api/v1/ia-avancee/prediction-pannes
- GET  /api/v1/ia-avancee/suggestions-proactives
- POST /api/v1/ia-avancee/adaptations-meteo
"""

from __future__ import annotations

from io import BytesIO
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# -----------------------------------------------------------------------------
# FIXTURES
# -----------------------------------------------------------------------------

SERVICE_PATH = "src.api.routes.ia_avancee._get_service"


@pytest_asyncio.fixture
async def async_client():
    """Client async avec auth + rate-limit overrides."""
    from src.api.dependencies import require_auth
    from src.api.main import app
    from src.api.rate_limiting import verifier_limite_debit_ia

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user",
        "email": "test@matanne.fr",
        "role": "membre",
    }
    app.dependency_overrides[verifier_limite_debit_ia] = lambda: None
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _fake_image() -> bytes:
    """Renvoie des octets minimaux simulant une image PNG valide."""
    # Signature PNG (8 octets) suffisante pour le content_type check
    return b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


# -----------------------------------------------------------------------------
# 6.1 — GET /suggestions-achats
# -----------------------------------------------------------------------------


class TestSuggestionsAchats:
    """Tests pour GET /api/v1/ia-avancee/suggestions-achats."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.suggerer_achats.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/suggestions-achats")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_appelle_service(self, async_client: httpx.AsyncClient):
        """Le service suggerer_achats doit etre appele."""
        mock_svc = MagicMock()
        mock_svc.suggerer_achats.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.get("/api/v1/ia-avancee/suggestions-achats")
        mock_svc.suggerer_achats.assert_called_once()

    @pytest.mark.asyncio
    async def test_parametre_jours_passe_au_service(self, async_client: httpx.AsyncClient):
        """Le parametre jours doit etre transmis au service."""
        mock_svc = MagicMock()
        mock_svc.suggerer_achats.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.get("/api/v1/ia-avancee/suggestions-achats?jours=30")
        mock_svc.suggerer_achats.assert_called_once_with(jours=30)

    @pytest.mark.asyncio
    async def test_reponse_contient_suggestions(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ suggestions."""
        mock_svc = MagicMock()
        mock_svc.suggerer_achats.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/suggestions-achats")
        assert "suggestions" in response.json()


# -----------------------------------------------------------------------------
# 6.2 — POST /planning-adaptatif
# -----------------------------------------------------------------------------


class TestPlanningAdaptatif:
    """Tests pour POST /api/v1/ia-avancee/planning-adaptatif."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.generer_planning_adaptatif.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/planning-adaptatif", json={}
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_appelle_service_avec_contexte(self, async_client: httpx.AsyncClient):
        """Le service doit recevoir meteo et budget."""
        mock_svc = MagicMock()
        mock_svc.generer_planning_adaptatif.return_value = None
        payload = {"meteo": {"temp": 12, "pluie": True}, "budget_restant": 200.0}
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.post("/api/v1/ia-avancee/planning-adaptatif", json=payload)
        mock_svc.generer_planning_adaptatif.assert_called_once_with(
            meteo=payload["meteo"], budget_restant=200.0
        )

    @pytest.mark.asyncio
    async def test_reponse_contient_recommandations(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ recommandations."""
        mock_svc = MagicMock()
        mock_svc.generer_planning_adaptatif.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/planning-adaptatif", json={}
            )
        assert "recommandations" in response.json()


# -----------------------------------------------------------------------------
# 6.3 — POST /diagnostic-plante (upload fichier)
# -----------------------------------------------------------------------------


class TestDiagnosticPlante:
    """Tests pour POST /api/v1/ia-avancee/diagnostic-plante."""

    @pytest.mark.asyncio
    async def test_retourne_200_avec_image(self, async_client: httpx.AsyncClient):
        """L'upload d'image valide doit repondre 200."""
        from src.services.ia_avancee.types import DiagnosticPlante

        mock_svc = MagicMock()
        mock_svc.diagnostiquer_plante_photo.return_value = DiagnosticPlante(
            nom_plante="Tomate", etat_general="bon"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/diagnostic-plante",
                files={"file": ("plante.png", _fake_image(), "image/png")},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_rejette_fichier_non_image(self, async_client: httpx.AsyncClient):
        """Un fichier non-image doit etre rejete avec 400."""
        mock_svc = MagicMock()
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/diagnostic-plante",
                files={"file": ("doc.pdf", b"PDF content", "application/pdf")},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_503_si_service_indisponible(self, async_client: httpx.AsyncClient):
        """Si le service retourne None, l'endpoint doit repondre 503."""
        mock_svc = MagicMock()
        mock_svc.diagnostiquer_plante_photo.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/diagnostic-plante",
                files={"file": ("plante.png", _fake_image(), "image/png")},
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_reponse_contient_nom_plante(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ nom_plante."""
        from src.services.ia_avancee.types import DiagnosticPlante

        mock_svc = MagicMock()
        mock_svc.diagnostiquer_plante_photo.return_value = DiagnosticPlante(
            nom_plante="Basilic", etat_general="moyen"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/diagnostic-plante",
                files={"file": ("plante.png", _fake_image(), "image/png")},
            )
        assert response.json()["nom_plante"] == "Basilic"


# -----------------------------------------------------------------------------
# 6.4 — GET /prevision-depenses
# -----------------------------------------------------------------------------


class TestPrevisionDepenses:
    """Tests pour GET /api/v1/ia-avancee/prevision-depenses."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.prevoir_depenses_fin_mois.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/prevision-depenses")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_appelle_service(self, async_client: httpx.AsyncClient):
        """Le service prevoir_depenses_fin_mois doit etre appele."""
        mock_svc = MagicMock()
        mock_svc.prevoir_depenses_fin_mois.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.get("/api/v1/ia-avancee/prevision-depenses")
        mock_svc.prevoir_depenses_fin_mois.assert_called_once()


# -----------------------------------------------------------------------------
# 6.5 — POST /idees-cadeaux
# -----------------------------------------------------------------------------


class TestIdeesCadeaux:
    """Tests pour POST /api/v1/ia-avancee/idees-cadeaux."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.suggerer_cadeaux.return_value = None
        payload = {"nom": "Jules", "age": 4, "relation": "fils", "budget_max": 30.0}
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/idees-cadeaux", json=payload
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_passe_parametres_au_service(self, async_client: httpx.AsyncClient):
        """Le service doit recevoir tous les parametres du corps."""
        mock_svc = MagicMock()
        mock_svc.suggerer_cadeaux.return_value = None
        payload = {
            "nom": "Jules",
            "age": 4,
            "relation": "fils",
            "budget_max": 30.0,
            "occasion": "anniversaire",
        }
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.post("/api/v1/ia-avancee/idees-cadeaux", json=payload)
        mock_svc.suggerer_cadeaux.assert_called_once_with(
            nom="Jules",
            age=4,
            relation="fils",
            budget_max=30.0,
            occasion="anniversaire",
        )

    @pytest.mark.asyncio
    async def test_reponse_contient_idees(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ idees."""
        mock_svc = MagicMock()
        mock_svc.suggerer_cadeaux.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/idees-cadeaux",
                json={"nom": "Jules", "age": 4},
            )
        assert "idees" in response.json()


# -----------------------------------------------------------------------------
# 6.6 — POST /analyse-photo
# -----------------------------------------------------------------------------


class TestAnalysePhotoMultiUsage:
    """Tests pour POST /api/v1/ia-avancee/analyse-photo."""

    @pytest.mark.asyncio
    async def test_retourne_200_avec_image(self, async_client: httpx.AsyncClient):
        """L'upload d'image valide doit repondre 200."""
        from src.services.ia_avancee.types import AnalysePhotoMultiUsage

        mock_svc = MagicMock()
        mock_svc.analyser_photo_multi_usage.return_value = AnalysePhotoMultiUsage(
            contexte_detecte="recette", resume="analyse ok"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/analyse-photo",
                files={"file": ("photo.jpg", _fake_image(), "image/jpeg")},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_503_si_service_indisponible(self, async_client: httpx.AsyncClient):
        """Si le service retourne None, l'endpoint doit repondre 503."""
        mock_svc = MagicMock()
        mock_svc.analyser_photo_multi_usage.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/analyse-photo",
                files={"file": ("photo.jpg", _fake_image(), "image/jpeg")},
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_reponse_contient_contexte_detecte(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ contexte_detecte."""
        from src.services.ia_avancee.types import AnalysePhotoMultiUsage

        mock_svc = MagicMock()
        mock_svc.analyser_photo_multi_usage.return_value = AnalysePhotoMultiUsage(
            contexte_detecte="plante", resume="analyse ok"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/analyse-photo",
                files={"file": ("photo.jpg", _fake_image(), "image/jpeg")},
            )
        assert response.json()["contexte_detecte"] == "plante"


# -----------------------------------------------------------------------------
# 6.7 — GET /optimisation-routines
# -----------------------------------------------------------------------------


class TestOptimisationRoutines:
    """Tests pour GET /api/v1/ia-avancee/optimisation-routines."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.optimiser_routines.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/optimisation-routines")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reponse_contient_optimisations(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ optimisations."""
        mock_svc = MagicMock()
        mock_svc.optimiser_routines.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/optimisation-routines")
        assert "optimisations" in response.json()


# -----------------------------------------------------------------------------
# 6.8 — POST /analyse-document
# -----------------------------------------------------------------------------


class TestAnalyseDocument:
    """Tests pour POST /api/v1/ia-avancee/analyse-document."""

    @pytest.mark.asyncio
    async def test_retourne_200_avec_image(self, async_client: httpx.AsyncClient):
        """L'upload d'image valide doit repondre 200."""
        from src.services.ia_avancee.types import DocumentAnalyse

        mock_svc = MagicMock()
        mock_svc.analyser_document_photo.return_value = DocumentAnalyse(
            type_document="facture"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/analyse-document",
                files={"file": ("doc.png", _fake_image(), "image/png")},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_503_si_service_indisponible(self, async_client: httpx.AsyncClient):
        """Si le service retourne None, l'endpoint doit repondre 503."""
        mock_svc = MagicMock()
        mock_svc.analyser_document_photo.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/analyse-document",
                files={"file": ("doc.png", _fake_image(), "image/png")},
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_reponse_contient_type_document(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ type_document."""
        from src.services.ia_avancee.types import DocumentAnalyse

        mock_svc = MagicMock()
        mock_svc.analyser_document_photo.return_value = DocumentAnalyse(
            type_document="contrat"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/analyse-document",
                files={"file": ("doc.png", _fake_image(), "image/png")},
            )
        assert response.json()["type_document"] == "contrat"


# -----------------------------------------------------------------------------
# 6.9 — POST /estimation-travaux
# -----------------------------------------------------------------------------


class TestEstimationTravaux:
    """Tests pour POST /api/v1/ia-avancee/estimation-travaux."""

    @pytest.mark.asyncio
    async def test_retourne_200_avec_image(self, async_client: httpx.AsyncClient):
        """L'upload d'image valide doit repondre 200."""
        from src.services.ia_avancee.types import EstimationTravauxPhoto

        mock_svc = MagicMock()
        mock_svc.estimer_travaux_photo.return_value = EstimationTravauxPhoto(
            type_travaux="peinture", description="mur fissuré"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/estimation-travaux",
                files={"file": ("chantier.jpg", _fake_image(), "image/jpeg")},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_503_si_service_indisponible(self, async_client: httpx.AsyncClient):
        """Si le service retourne None, l'endpoint doit repondre 503."""
        mock_svc = MagicMock()
        mock_svc.estimer_travaux_photo.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/estimation-travaux",
                files={"file": ("chantier.jpg", _fake_image(), "image/jpeg")},
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_passe_description_au_service(self, async_client: httpx.AsyncClient):
        """La description query param doit etre transmise au service."""
        from src.services.ia_avancee.types import EstimationTravauxPhoto

        mock_svc = MagicMock()
        mock_svc.estimer_travaux_photo.return_value = EstimationTravauxPhoto(
            type_travaux="peinture", description="fissure mur"
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.post(
                "/api/v1/ia-avancee/estimation-travaux?description=fissure+mur",
                files={"file": ("chantier.jpg", _fake_image(), "image/jpeg")},
            )
        call_kwargs = mock_svc.estimer_travaux_photo.call_args
        assert call_kwargs is not None
        desc = call_kwargs[1].get("description") or (
            call_kwargs[0][1] if len(call_kwargs[0]) > 1 else None
        )
        assert desc is not None


# -----------------------------------------------------------------------------
# 6.10 — POST /planning-voyage
# -----------------------------------------------------------------------------


class TestPlanningVoyage:
    """Tests pour POST /api/v1/ia-avancee/planning-voyage."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        from src.services.ia_avancee.types import PlanningVoyage

        mock_svc = MagicMock()
        mock_svc.generer_planning_voyage.return_value = PlanningVoyage(
            destination="Barcelone", duree_jours=5
        )
        payload = {"destination": "Barcelone", "duree_jours": 5}
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/planning-voyage", json=payload
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_503_si_service_indisponible(self, async_client: httpx.AsyncClient):
        """Si le service retourne None, l'endpoint doit repondre 503."""
        mock_svc = MagicMock()
        mock_svc.generer_planning_voyage.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/planning-voyage",
                json={"destination": "Lyon", "duree_jours": 2},
            )
        assert response.status_code == 503

    @pytest.mark.asyncio
    async def test_passe_parametres_au_service(self, async_client: httpx.AsyncClient):
        """Tous les parametres doivent etre transmis au service."""
        from src.services.ia_avancee.types import PlanningVoyage

        mock_svc = MagicMock()
        mock_svc.generer_planning_voyage.return_value = PlanningVoyage(
            destination="Rome", duree_jours=7
        )
        payload = {
            "destination": "Rome",
            "duree_jours": 7,
            "budget_total": 1500.0,
            "avec_enfant": True,
        }
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.post("/api/v1/ia-avancee/planning-voyage", json=payload)
        mock_svc.generer_planning_voyage.assert_called_once_with(
            destination="Rome",
            duree_jours=7,
            budget_total=1500.0,
            avec_enfant=True,
        )

    @pytest.mark.asyncio
    async def test_reponse_contient_destination(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ destination."""
        from src.services.ia_avancee.types import PlanningVoyage

        mock_svc = MagicMock()
        mock_svc.generer_planning_voyage.return_value = PlanningVoyage(
            destination="Lisbonne", duree_jours=3
        )
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/planning-voyage",
                json={"destination": "Lisbonne", "duree_jours": 3},
            )
        assert response.json()["destination"] == "Lisbonne"


# -----------------------------------------------------------------------------
# 6.11 — GET /recommandations-energie
# -----------------------------------------------------------------------------


class TestRecommandationsEnergie:
    """Tests pour GET /api/v1/ia-avancee/recommandations-energie."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.recommander_economies_energie.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/recommandations-energie")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reponse_contient_recommandations(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ recommandations."""
        mock_svc = MagicMock()
        mock_svc.recommander_economies_energie.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/recommandations-energie")
        assert "recommandations" in response.json()


# -----------------------------------------------------------------------------
# 6.12 — GET /prediction-pannes
# -----------------------------------------------------------------------------


class TestPredictionPannes:
    """Tests pour GET /api/v1/ia-avancee/prediction-pannes."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.predire_pannes.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/prediction-pannes")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reponse_contient_predictions(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ predictions."""
        mock_svc = MagicMock()
        mock_svc.predire_pannes.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/prediction-pannes")
        assert "predictions" in response.json()


# -----------------------------------------------------------------------------
# 6.13 — GET /suggestions-proactives
# -----------------------------------------------------------------------------


class TestSuggestionsProactives:
    """Tests pour GET /api/v1/ia-avancee/suggestions-proactives."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200."""
        mock_svc = MagicMock()
        mock_svc.generer_suggestions_proactives.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/suggestions-proactives")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_reponse_contient_suggestions(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ suggestions."""
        mock_svc = MagicMock()
        mock_svc.generer_suggestions_proactives.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.get("/api/v1/ia-avancee/suggestions-proactives")
        assert "suggestions" in response.json()


# -----------------------------------------------------------------------------
# 6.14 — POST /adaptations-meteo
# -----------------------------------------------------------------------------


class TestAdaptationsMeteo:
    """Tests pour POST /api/v1/ia-avancee/adaptations-meteo."""

    @pytest.mark.asyncio
    async def test_retourne_200(self, async_client: httpx.AsyncClient):
        """L'endpoint doit repondre 200 avec des previsions valides."""
        mock_svc = MagicMock()
        mock_svc.adapter_planning_meteo.return_value = None
        payload = {"previsions_meteo": {"lundi": "pluie", "mardi": "soleil"}}
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/adaptations-meteo", json=payload
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_passe_previsions_au_service(self, async_client: httpx.AsyncClient):
        """Les previsions meteo doivent etre transmises au service."""
        mock_svc = MagicMock()
        mock_svc.adapter_planning_meteo.return_value = None
        previsions = {"lundi": "pluie", "mardi": "soleil"}
        with patch(SERVICE_PATH, return_value=mock_svc):
            await async_client.post(
                "/api/v1/ia-avancee/adaptations-meteo",
                json={"previsions_meteo": previsions},
            )
        mock_svc.adapter_planning_meteo.assert_called_once_with(previsions)

    @pytest.mark.asyncio
    async def test_reponse_contient_adaptations(self, async_client: httpx.AsyncClient):
        """La reponse doit contenir le champ adaptations_repas."""
        mock_svc = MagicMock()
        mock_svc.adapter_planning_meteo.return_value = None
        with patch(SERVICE_PATH, return_value=mock_svc):
            response = await async_client.post(
                "/api/v1/ia-avancee/adaptations-meteo",
                json={"previsions_meteo": {"j1": "nuageux"}},
            )
        assert "adaptations" in response.json()


# -----------------------------------------------------------------------------
# SECURITE - Auth requise sur tous les endpoints
# -----------------------------------------------------------------------------


class TestAuthRequise:
    """Verifie que l'authentification est requise sur chaque endpoint.

    En mode DEVELOPMENT l'app auto-authentifie les requetes ; on simule
    le comportement production en patchant le parametre ENVIRONMENT.
    """

    @pytest.mark.asyncio
    async def test_suggestions_achats_sans_auth(self):
        """Sans auth (mode production), l'endpoint doit repondre 401."""
        from src.api.main import app
        from src.api.rate_limiting import verifier_limite_debit_ia

        app.dependency_overrides[verifier_limite_debit_ia] = lambda: None
        with patch.dict("os.environ", {"ENVIRONMENT": "production"}):
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app, raise_app_exceptions=False),
                base_url="http://test",
            ) as client:
                response = await client.get("/api/v1/ia-avancee/suggestions-achats")
        app.dependency_overrides.clear()
        assert response.status_code in [401, 403]

    @pytest.mark.asyncio
    async def test_suggestions_proactives_sans_auth(self):
        """Sans auth (mode production), l'endpoint proactif doit repondre 401."""
        from src.api.main import app
        from src.api.rate_limiting import verifier_limite_debit_ia

        app.dependency_overrides[verifier_limite_debit_ia] = lambda: None
        with patch.dict("os.environ", {"ENVIRONMENT": "production"}):
            async with httpx.AsyncClient(
                transport=ASGITransport(app=app, raise_app_exceptions=False),
                base_url="http://test",
            ) as client:
                response = await client.get("/api/v1/ia-avancee/suggestions-proactives")
        app.dependency_overrides.clear()
        assert response.status_code in [401, 403]
