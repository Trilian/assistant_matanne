"""
Tests des routes API IA contextuelles et avancées.

Couvre : auto-tags notes, mémo vocal, pilote auto,
insights analytics, anomalies jardin, score écologique.
"""

import pytest
import pytest_asyncio
import httpx
from httpx import ASGITransport
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager


@pytest_asyncio.fixture
async def client():
    """Client HTTP async avec auth override et rate limiting désactivé."""
    from src.api.dependencies import require_auth
    from src.api.main import app

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user-ia",
        "sub": "test-user-ia",
        "email": "test@matanne.fr",
        "role": "membre",
    }
    # Désactiver le rate limiting IA pour les tests
    try:
        from src.api.routes.ia_modules import verifier_limite_debit_ia
        app.dependency_overrides[verifier_limite_debit_ia] = lambda: {}
    except ImportError:
        pass
    try:
        from src.api.routes.dashboard import verifier_limite_debit_ia as vld_dash
        app.dependency_overrides[vld_dash] = lambda: {}
    except ImportError:
        pass

    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()


# ──────────────────────────────────────────────
# Routes utilitaires — mémo vocal
# ──────────────────────────────────────────────


class TestMemoVocalRoute:
    """Tests POST /api/v1/utilitaires/memos/vocal"""

    @pytest.mark.asyncio
    async def test_memo_vocal_success(self, client):
        """Classification mémo vocal → 200."""
        from src.services.utilitaires.memo_vocal import MemoClassifie

        mock_svc = Mock()
        mock_svc.transcrire_et_classer.return_value = MemoClassifie(
            module="courses",
            action="ajouter",
            contenu="lait, pain",
            tags=["alimentation"],
            destination_url="/cuisine/courses",
            confiance=0.92,
        )

        with patch(
            "src.services.utilitaires.memo_vocal.get_memo_vocal_service",
            return_value=mock_svc,
        ):
            response = await client.post(
                "/api/v1/utilitaires/memos/vocal",
                json={"texte": "Acheter du lait et du pain"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "courses"
        assert data["destination_url"] == "/cuisine/courses"

    @pytest.mark.asyncio
    async def test_memo_vocal_sans_auth(self):
        """Sans header auth : 200 en environnement de test, sinon 401/403."""
        from src.api.dependencies import _est_environnement_dev
        from src.api.main import app

        app.dependency_overrides.clear()
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as unauthenticated:
            response = await unauthenticated.post(
                "/api/v1/utilitaires/memos/vocal",
                json={"texte": "Test"},
            )

        if _est_environnement_dev():
            assert response.status_code == 200
        else:
            assert response.status_code in (401, 403)


# ──────────────────────────────────────────────
# Routes pilote automatique
# ──────────────────────────────────────────────


class TestPiloteAutoRoutes:
    """Tests des endpoints pilote automatique."""

    @pytest.mark.asyncio
    async def test_status(self, client):
        """GET /pilote-auto/status → 200."""
        mock_svc = Mock()
        mock_svc.obtenir_mode_pilote_automatique.return_value = None

        with patch(
            "src.api.routes.ia_avancee._get_service",
            return_value=mock_svc,
        ):
            response = await client.get("/api/v1/ia-avancee/pilote-auto/status")
        assert response.status_code == 200
        data = response.json()
        assert "actif" in data

    @pytest.mark.asyncio
    async def test_toggle_activation(self, client):
        """POST /pilote-auto/toggle → 200."""
        with patch(
            "src.services.ia_avancee.pilote_auto.configurer_mode_pilote_automatique",
            return_value=None,
        ):
            with patch("src.api.routes.ia_avancee._get_service", return_value=Mock()):
                response = await client.post(
                    "/api/v1/ia-avancee/pilote-auto/toggle",
                    json={"actif": True},
                )
        assert response.status_code == 200
        data = response.json()
        assert "actif" in data

    @pytest.mark.asyncio
    async def test_actions_recentes(self, client):
        """GET /pilote-auto/actions-recentes → 200."""
        mock_svc = Mock()
        mock_svc.obtenir_mode_pilote_automatique.return_value = None

        with patch(
            "src.api.routes.ia_avancee._get_service",
            return_value=mock_svc,
        ):
            response = await client.get("/api/v1/ia-avancee/pilote-auto/actions-recentes")
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data

    @pytest.mark.asyncio
    async def test_actions_recentes_limite(self, client):
        """GET /actions-recentes?limite=5 → paramètre accepté."""
        mock_svc = Mock()
        mock_svc.obtenir_mode_pilote_automatique.return_value = None

        with patch(
            "src.api.routes.ia_avancee._get_service",
            return_value=mock_svc,
        ):
            response = await client.get("/api/v1/ia-avancee/pilote-auto/actions-recentes?limite=5")
        assert response.status_code == 200


# ──────────────────────────────────────────────
# Route insights analytics
# ──────────────────────────────────────────────


class TestInsightsAnalyticsRoute:
    """Tests GET /api/v1/dashboard/insights-analytics"""

    @pytest.mark.asyncio
    async def test_insights_success(self, client):
        """Insights analytics → 200."""
        from src.services.dashboard.insights_analytics import InsightsFamille

        mock_svc = Mock()
        mock_svc.generer_insights_famille.return_value = InsightsFamille(
            periode_jours=30,
            repas_planifies=14,
            repas_cuisines=12,
            taux_realisation_repas=85.7,
            resume_ia="Bonne semaine !",
        )

        with patch(
            "src.services.dashboard.insights_analytics.get_insights_analytics_service",
            return_value=mock_svc,
        ):
            response = await client.get("/api/v1/dashboard/insights-analytics?periode_mois=1")

        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_insights_periode_invalide(self, client):
        """Période > 12 → 422."""
        response = await client.get("/api/v1/dashboard/insights-analytics?periode_mois=24")
        assert response.status_code == 422


# ──────────────────────────────────────────────
# Route anomalies jardin
# ──────────────────────────────────────────────


class TestAnomaliesJardinRoute:
    """Tests GET /api/v1/ia/modules/jardin/anomalies"""

    @pytest.mark.asyncio
    async def test_anomalies_success(self, client):
        """Anomalies jardin → 200."""
        from src.services.maison.ia.jardin_anomalies_ia import AnomaliesJardinResponse

        mock_svc = Mock()
        mock_svc.detecter_anomalies.return_value = AnomaliesJardinResponse(
            score_sante_jardin=80.0,
            recommandations_generales=["Tout va bien"],
        )

        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.all.return_value = []

        @contextmanager
        def _ctx():
            yield mock_session

        with patch(
            "src.services.maison.ia.jardin_anomalies_ia.get_jardin_anomalies_ia_service",
            return_value=mock_svc,
        ):
            with patch("src.api.routes.ia_modules.executer_avec_session", return_value=_ctx()):
                response = await client.get("/api/v1/ia/modules/jardin/anomalies")

        assert response.status_code == 200


# ──────────────────────────────────────────────
# Route score écologique
# ──────────────────────────────────────────────


class TestScoreEcologiqueRoute:
    """Tests POST /api/v1/ia/modules/recette/score-ecologique"""

    @pytest.mark.asyncio
    async def test_score_eco_success(self, client):
        """Score écologique → 200."""
        mock_svc = Mock()
        mock_svc.calculer_score_eco_responsable.return_value = None

        with patch(
            "src.services.ia_avancee.service.get_ia_avancee_service",
            return_value=mock_svc,
        ):
            response = await client.post(
                "/api/v1/ia/modules/recette/score-ecologique",
                json={"recette_id": 1, "ingredients": ["tomate", "basilic"]},
            )

        assert response.status_code == 200
        data = response.json()
        assert "score_global" in data
