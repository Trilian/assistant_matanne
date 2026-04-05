"""
Tests des routes API de la Phase 6 (IA Avancée).

Couvre: auto-tags notes, mémo vocal, pilote auto,
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
    """Client HTTP async avec auth override."""
    from src.api.dependencies import require_auth
    from src.api.main import app

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user-p6",
        "email": "test@matanne.fr",
        "role": "membre",
    }
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as c:
        yield c
    app.dependency_overrides.clear()


# ──────────────────────────────────────────────
# Routes utilitaires — auto-tags & mémo vocal
# ──────────────────────────────────────────────


class TestAutoTagsRoute:
    """Tests POST /api/v1/utilitaires/notes/{note_id}/auto-tags"""

    @pytest.mark.asyncio
    async def test_auto_tags_success(self, client):
        """Auto-tagging d'une note → 200 avec tags."""
        mock_note = Mock()
        mock_note.id = 1
        mock_note.titre = "Courses semaine"
        mock_note.contenu = "Acheter du lait, des oeufs et du beurre"
        mock_note.user_id = "test-user-p6"

        mock_session = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_note

        @contextmanager
        def _ctx():
            yield mock_session

        with patch("src.api.routes.utilitaires.executer_avec_session") as mock_exec:
            mock_exec.return_value = _ctx()
            with patch("src.api.routes.utilitaires.get_notes_ia_service") as mock_svc_factory:
                mock_svc = Mock()
                mock_svc.auto_etiqueter.return_value = Mock(
                    tags=["courses", "cuisine"],
                    confiance=0.9,
                )
                mock_svc_factory.return_value = mock_svc
                with patch("src.api.routes.utilitaires.executer_async", side_effect=lambda fn: fn()):
                    response = await client.post("/api/v1/utilitaires/notes/1/auto-tags")

        assert response.status_code == 200
        data = response.json()
        assert "tags" in data or "note_id" in data

    @pytest.mark.asyncio
    async def test_auto_tags_sans_auth(self):
        """Sans auth → 401 ou 403."""
        from src.api.main import app

        async with httpx.AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as unauthenticated:
            response = await unauthenticated.post("/api/v1/utilitaires/notes/1/auto-tags")
        assert response.status_code in (401, 403)


class TestMemoVocalRoute:
    """Tests POST /api/v1/utilitaires/memos/vocal"""

    @pytest.mark.asyncio
    async def test_memo_vocal_success(self, client):
        """Classification mémo vocal → 200."""
        from src.services.utilitaires.memo_vocal import MemoClassifie

        with patch("src.api.routes.utilitaires.get_memo_vocal_service") as mock_factory:
            mock_svc = Mock()
            mock_svc.transcrire_et_classer.return_value = MemoClassifie(
                module="courses",
                action="ajouter",
                contenu="lait, pain",
                tags=["alimentation"],
                destination_url="/cuisine/courses",
                confiance=0.92,
            )
            mock_factory.return_value = mock_svc
            with patch("src.api.routes.utilitaires.executer_async", side_effect=lambda fn: fn()):
                response = await client.post(
                    "/api/v1/utilitaires/memos/vocal",
                    json={"texte": "Acheter du lait et du pain"},
                )

        assert response.status_code == 200
        data = response.json()
        assert data["module"] == "courses"
        assert data["destination_url"] == "/cuisine/courses"

    @pytest.mark.asyncio
    async def test_memo_vocal_texte_vide(self, client):
        """Texte vide → 422 ou 200 avec note fallback."""
        with patch("src.api.routes.utilitaires.get_memo_vocal_service") as mock_factory:
            mock_svc = Mock()
            from src.services.utilitaires.memo_vocal import MemoClassifie
            mock_svc.transcrire_et_classer.return_value = MemoClassifie(
                module="note", action="ajouter", contenu="", confiance=0.0,
            )
            mock_factory.return_value = mock_svc
            with patch("src.api.routes.utilitaires.executer_async", side_effect=lambda fn: fn()):
                response = await client.post(
                    "/api/v1/utilitaires/memos/vocal",
                    json={"texte": ""},
                )
        # Accepte 200 (le service gère le fallback) ou 422 (validation Pydantic)
        assert response.status_code in (200, 422)


# ──────────────────────────────────────────────
# Routes pilote automatique
# ──────────────────────────────────────────────


class TestPiloteAutoRoutes:
    """Tests des endpoints pilote automatique."""

    @pytest.mark.asyncio
    async def test_status(self, client):
        """GET /pilote-auto/status → 200."""
        with patch("src.api.routes.ia_avancee.executer_async", side_effect=lambda fn: fn()):
            response = await client.get("/api/v1/ia-avancee/pilote-auto/status")
        assert response.status_code == 200
        data = response.json()
        assert "actif" in data

    @pytest.mark.asyncio
    async def test_toggle_activation(self, client):
        """POST /pilote-auto/toggle → 200."""
        with patch("src.api.routes.ia_avancee.executer_async", side_effect=lambda fn: fn()):
            response = await client.post(
                "/api/v1/ia-avancee/pilote-auto/toggle",
                json={"actif": True},
            )
        assert response.status_code == 200
        data = response.json()
        assert "actif" in data or "message" in data

    @pytest.mark.asyncio
    async def test_toggle_desactivation(self, client):
        """POST /pilote-auto/toggle actif=False → 200."""
        with patch("src.api.routes.ia_avancee.executer_async", side_effect=lambda fn: fn()):
            response = await client.post(
                "/api/v1/ia-avancee/pilote-auto/toggle",
                json={"actif": False},
            )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_actions_recentes(self, client):
        """GET /pilote-auto/actions-recentes → 200."""
        with patch("src.api.routes.ia_avancee.executer_async", side_effect=lambda fn: fn()):
            response = await client.get("/api/v1/ia-avancee/pilote-auto/actions-recentes")
        assert response.status_code == 200
        data = response.json()
        assert "actions" in data or isinstance(data, list)

    @pytest.mark.asyncio
    async def test_actions_recentes_limite(self, client):
        """GET /actions-recentes?limite=5 → paramètre accepté."""
        with patch("src.api.routes.ia_avancee.executer_async", side_effect=lambda fn: fn()):
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

        with patch("src.api.routes.dashboard.get_insights_analytics_service") as mock_factory:
            mock_svc = Mock()
            mock_svc.generer_insights_famille.return_value = InsightsFamille(
                periode_jours=30,
                repas_planifies=14,
                repas_cuisines=12,
                taux_realisation_repas=85.7,
                resume_ia="Bonne semaine !",
            )
            mock_factory.return_value = mock_svc
            with patch("src.api.routes.dashboard.executer_async", side_effect=lambda fn: fn()):
                with patch("src.api.routes.dashboard.verifier_limite_debit_ia", return_value={}):
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

        with patch("src.api.routes.ia_modules.get_jardin_anomalies_ia_service") as mock_factory:
            mock_svc = Mock()
            mock_svc.detecter_anomalies.return_value = AnomaliesJardinResponse(
                score_sante_jardin=80.0,
                recommandations_generales=["Tout va bien"],
            )
            mock_factory.return_value = mock_svc
            with patch("src.api.routes.ia_modules.executer_async", side_effect=lambda fn: fn()):
                with patch("src.api.routes.ia_modules.verifier_limite_debit_ia", return_value={}):
                    with patch("src.api.routes.ia_modules.obtenir_contexte_db") as mock_db:
                        mock_session = Mock()
                        mock_session.query.return_value.filter.return_value.all.return_value = []

                        @contextmanager
                        def _ctx():
                            yield mock_session

                        mock_db.return_value = _ctx()
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
        with patch("src.api.routes.ia_modules.executer_async", side_effect=lambda fn: fn()):
            with patch("src.api.routes.ia_modules.verifier_limite_debit_ia", return_value={}):
                with patch("src.api.routes.ia_modules.get_ia_avancee_service") as mock_factory:
                    mock_svc = Mock()
                    mock_svc.calculer_score_eco_responsable.return_value = {
                        "score": "B",
                        "detail": "Bon score, majorité d'ingrédients locaux",
                    }
                    mock_factory.return_value = mock_svc
                    response = await client.post(
                        "/api/v1/ia/modules/recette/score-ecologique",
                        json={"recette_id": 1, "ingredients": ["tomate", "basilic"]},
                    )

        assert response.status_code == 200
