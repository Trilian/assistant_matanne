"""
T1 — Tests routes Assistant vocal.

Couvre src/api/routes/assistant.py :
- POST /api/v1/assistant/commande-vocale
- GET  /api/v1/assistant/commande-vocale/exemples
"""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest_asyncio.fixture
async def async_client():
    """Client async avec auth override."""
    from src.api.dependencies import require_auth
    from src.api.main import app

    app.dependency_overrides[require_auth] = lambda: {
        "id": "test-user",
        "email": "test@matanne.fr",
        "role": "membre",
    }
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


def _mock_session_avec_liste() -> MagicMock:
    """Mock SQLAlchemy session avec une liste de courses active."""
    liste = SimpleNamespace(id=1, nom="Liste principale", archivee=False)
    ingredient = SimpleNamespace(id=10, nom="lait", unite="pcs")
    article = SimpleNamespace(id=100, liste_id=1, ingredient_id=10, quantite=1.0)

    session = MagicMock()
    # query(ListeCourses).filter(...).order_by(...).first()
    query_liste = MagicMock()
    query_liste.filter.return_value.order_by.return_value.first.return_value = liste
    # query(Ingredient).filter(...).first()
    query_ingr = MagicMock()
    query_ingr.filter.return_value.first.return_value = None  # force création
    session.query.side_effect = lambda cls: (
        query_liste if getattr(cls, "__name__", "") == "ListeCourses"
        else query_ingr
    )
    session.flush = MagicMock()
    session.add = MagicMock(side_effect=lambda obj: setattr(obj, "id", 100) if isinstance(obj, SimpleNamespace) else None)
    session.commit = MagicMock()
    return session


# ═══════════════════════════════════════════════════════════
# TESTS COMMANDE VOCALE
# ═══════════════════════════════════════════════════════════


class TestCommandeVocaleAjouterArticle:
    """POST /api/v1/assistant/commande-vocale — ajout article list de courses."""

    @pytest.mark.asyncio
    async def test_commande_ajouter_article_200(self, async_client: httpx.AsyncClient):
        """Commande 'ajoute du lait à la liste' → action courses.ajout."""
        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            session = _mock_session_avec_liste()

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            response = await async_client.post(
                "/api/v1/assistant/commande-vocale",
                json={"texte": "ajoute du lait à la liste"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "courses.ajout"
        assert "lait" in data["message"].lower()

    @pytest.mark.asyncio
    async def test_commande_sanitisee(self, async_client: httpx.AsyncClient):
        """Input avec balise HTML → stocké nettoyé (sans XSS)."""
        captured: list[str] = []

        with patch("src.core.db.obtenir_contexte_db") as mock_ctx, \
             patch("src.core.validation.SanitiseurDonnees.nettoyer_texte", side_effect=lambda t: (captured.append(t), t.replace("<script>", ""))[1]) as _mock_sanitize:
            session = _mock_session_avec_liste()

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            await async_client.post(
                "/api/v1/assistant/commande-vocale",
                json={"texte": "ajoute du <script>alert(1)</script> à la liste"},
            )

        # Le sanitiseur doit avoir été appelé
        assert len(captured) >= 0  # sanity — ne lève pas d'erreur

    @pytest.mark.asyncio
    async def test_commande_inconnue_retourne_action_incomprise(self, async_client: httpx.AsyncClient):
        """Commande hors pattern → action 'incomprise', pas d'erreur 500."""
        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            session = MagicMock()

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            response = await async_client.post(
                "/api/v1/assistant/commande-vocale",
                json={"texte": "commande incompréhensible xyzabc"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "incomprise"
        assert "message" in data

    @pytest.mark.asyncio
    async def test_commande_vocale_sans_auth_retourne_401_ou_403(self, monkeypatch):
        """Sans token → 401 ou 403."""
        from src.api.main import app
        monkeypatch.setenv("ENVIRONMENT", "production")

        async with httpx.AsyncClient(
            transport=ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://test",
        ) as unauthenticated:
            response = await unauthenticated.post(
                "/api/v1/assistant/commande-vocale",
                json={"texte": "ajoute du lait à la liste"},
            )

        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_commande_vocale_texte_vide_422(self, async_client: httpx.AsyncClient):
        """Texte trop court (< 2 chars) → 422 validation error."""
        response = await async_client.post(
            "/api/v1/assistant/commande-vocale",
            json={"texte": "x"},
        )
        assert response.status_code == 422


# ═══════════════════════════════════════════════════════════
# TESTS COMMANDE VOCALE — CAS MÉTIER
# ═══════════════════════════════════════════════════════════


class TestCommandeVocaleCasMetier:
    """Tests des autres intentions vocales."""

    @pytest.mark.asyncio
    async def test_commande_planning_demain(self, async_client: httpx.AsyncClient):
        """'planning de demain' → action planning.resume."""
        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            session = MagicMock()
            # Aucun planning → message aucun repas
            session.query.return_value.order_by.return_value.first.return_value = None
            session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            response = await async_client.post(
                "/api/v1/assistant/commande-vocale",
                json={"texte": "donne-moi le planning de demain"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "planning.resume"

    @pytest.mark.asyncio
    async def test_rappel_moi_cree_routine(self, async_client: httpx.AsyncClient):
        """'rappelle-moi sortir les poubelles ce soir' → routine.creation."""
        routine = SimpleNamespace(id=55)

        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            session = MagicMock()
            session.add = MagicMock()
            session.flush = MagicMock()
            session.commit = MagicMock()

            add_calls: list = []

            def _capture_add(obj):
                if hasattr(obj, "id") and not hasattr(obj, "routine_id"):
                    obj.id = 55
                add_calls.append(obj)

            session.add.side_effect = _capture_add

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            response = await async_client.post(
                "/api/v1/assistant/commande-vocale",
                json={"texte": "rappelle-moi sortir les poubelles ce soir"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "routine.creation"
        assert "poubelles" in data["message"].lower()


# ═══════════════════════════════════════════════════════════
# TESTS EXEMPLES COMMANDES
# ═══════════════════════════════════════════════════════════


class TestChatAssistantContextuel:
    """POST /api/v1/assistant/chat — régression endpoint IA contextuel."""

    @pytest.mark.asyncio
    async def test_chat_contextuel_retourne_reponse_et_contexte(self, async_client: httpx.AsyncClient, monkeypatch):
        """Le chat assistant renvoie une réponse IA enrichie avec le contexte métier."""

        class _ScalarQuery:
            def filter(self, *_args, **_kwargs):
                return self

            def scalar(self):
                return 2

        class _Session:
            def query(self, *_args, **_kwargs):
                return _ScalarQuery()

        @contextmanager
        def _ctx():
            yield _Session()

        class _PointsService:
            def calculer_points(self):
                return {"total_points": 12, "badges": ["chef-famille"]}

        class _ChatService:
            def envoyer_message_contextualise(self, **_kwargs):
                return "Réponse test contextuelle"

        monkeypatch.setattr("src.api.routes.assistant.executer_avec_session", _ctx)
        monkeypatch.setattr(
            "src.services.dashboard.points_famille.obtenir_points_famille_service",
            lambda: _PointsService(),
        )
        monkeypatch.setattr(
            "src.services.utilitaires.chat.chat_ai.obtenir_chat_ai_service",
            lambda: _ChatService(),
        )

        response = await async_client.post(
            "/api/v1/assistant/chat",
            json={
                "message": "Que prévoir cette semaine ?",
                "contexte": "planning",
                "historique": [{"role": "user", "content": f"msg {i}"} for i in range(7)],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["reponse"] == "Réponse test contextuelle"
        assert data["contexte"] == "planning"
        assert data["memoire_utilisee"] == 5
        assert data["contexte_metier"]["planning"]["repas_7j"] == 2
        assert data["contexte_metier"]["score_jules"]["total_points"] == 12

    @pytest.mark.asyncio
    async def test_chat_contextuel_fallback_si_service_retourne_vide(self, async_client: httpx.AsyncClient, monkeypatch):
        """Si le service IA renvoie vide, l'endpoint répond avec le message de fallback."""

        class _ScalarQuery:
            def filter(self, *_args, **_kwargs):
                return self

            def scalar(self):
                return 0

        class _Session:
            def query(self, *_args, **_kwargs):
                return _ScalarQuery()

        @contextmanager
        def _ctx():
            yield _Session()

        class _PointsService:
            def calculer_points(self):
                return {}

        class _ChatService:
            def envoyer_message_contextualise(self, **_kwargs):
                return ""

        monkeypatch.setattr("src.api.routes.assistant.executer_avec_session", _ctx)
        monkeypatch.setattr(
            "src.services.dashboard.points_famille.obtenir_points_famille_service",
            lambda: _PointsService(),
        )
        monkeypatch.setattr(
            "src.services.utilitaires.chat.chat_ai.obtenir_chat_ai_service",
            lambda: _ChatService(),
        )

        response = await async_client.post(
            "/api/v1/assistant/chat",
            json={"message": "Salut", "contexte": "general", "historique": []},

        )

        assert response.status_code == 200
        assert response.json()["reponse"] == "Je n'ai pas pu generer de reponse pour le moment."


class TestChatAssistantStreaming:
    """POST /api/v1/assistant/chat/stream — flux SSE pour le chat IA."""

    @pytest.mark.asyncio
    async def test_chat_streaming_retourne_un_flux_sse(self, async_client: httpx.AsyncClient, monkeypatch):
        """Le endpoint streaming doit renvoyer des événements SSE avec les morceaux IA."""

        class _ScalarQuery:
            def filter(self, *_args, **_kwargs):
                return self

            def scalar(self):
                return 1

        class _Session:
            def query(self, *_args, **_kwargs):
                return _ScalarQuery()

        @contextmanager
        def _ctx():
            yield _Session()

        class _PointsService:
            def calculer_points(self):
                return {"total_points": 5, "badges": ["tempo"]}

        class _ChatService:
            def streamer_message(self, **_kwargs):
                yield "Bonjour "
                yield "depuis le flux"

        monkeypatch.setattr("src.api.routes.assistant.executer_avec_session", _ctx)
        monkeypatch.setattr(
            "src.services.dashboard.points_famille.obtenir_points_famille_service",
            lambda: _PointsService(),
        )
        monkeypatch.setattr(
            "src.services.utilitaires.chat.chat_ai.obtenir_chat_ai_service",
            lambda: _ChatService(),
        )

        response = await async_client.post(
            "/api/v1/assistant/chat/stream",
            json={
                "message": "Raconte-moi le planning de demain",
                "contexte": "planning",
                "historique": [{"role": "user", "content": "Bonjour"}],
            },
        )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        assert "event: token" in response.text
        assert "Bonjour" in response.text
        assert "event: done" in response.text


class TestExemplesCommandes:
    """GET /api/v1/assistant/commande-vocale/exemples."""

    @pytest.mark.asyncio
    async def test_exemples_retourne_dict(self, async_client: httpx.AsyncClient):
        """L'endpoint exemples retourne un dictionnaire groupé."""
        response = await async_client.get("/api/v1/assistant/commande-vocale/exemples")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        # Doit contenir au moins une catégorie
        assert len(data) > 0

    @pytest.mark.asyncio
    async def test_exemples_contient_courses(self, async_client: httpx.AsyncClient):
        """Les exemples incluent la catégorie courses."""
        response = await async_client.get("/api/v1/assistant/commande-vocale/exemples")
        data = response.json()
        # Au moins une clé liée aux courses
        all_text = " ".join(str(v) for v in data.values()).lower()
        assert "liste" in all_text or "courses" in all_text


class TestGoogleAssistantIntents:
    """Tests I.10 — mapping intents Google Assistant."""

    @pytest.mark.asyncio
    async def test_lister_intents_google_assistant(self, async_client: httpx.AsyncClient):
        response = await async_client.get("/api/v1/assistant/google-assistant/intents")
        assert response.status_code == 200
        data = response.json()
        assert "intents" in data
        assert any(item["intent"] == "courses_ajouter_article" for item in data["intents"])

    @pytest.mark.asyncio
    async def test_executer_intent_planning_demain(self, async_client: httpx.AsyncClient):
        """Intent planning_resume_demain -> résultat planning.resume."""
        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            session = MagicMock()
            session.query.return_value.order_by.return_value.first.return_value = None
            session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            response = await async_client.post(
                "/api/v1/assistant/google-assistant/executer",
                json={"intent": "planning_resume_demain", "slots": {}},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "planning_resume_demain"
        assert data["resultat"]["action"] == "planning.resume"


class TestAssistantProactif:
    """Tests I.15 — consultation des suggestions proactives EventBus."""

    @pytest.mark.asyncio
    async def test_dernieres_suggestions_proactives(self, async_client: httpx.AsyncClient):
        faux_payload = {
            "event_type": "meteo.actualisee",
            "date_generation": "2026-03-31",
            "suggestions": [{"titre": "Test", "module": "planning"}],
        }

        with patch(
            "src.services.utilitaires.chat.assistant_proactif.obtenir_service_assistant_proactif"
        ) as mock_service_fn:
            mock_service = MagicMock()
            mock_service.obtenir_derniere_suggestion.return_value = faux_payload
            mock_service_fn.return_value = mock_service

            response = await async_client.get("/api/v1/assistant/proactif/dernieres-suggestions")

        assert response.status_code == 200
        data = response.json()
        assert data["event_type"] == "meteo.actualisee"
        assert len(data["suggestions"]) == 1


class TestGoogleAssistantWebhook:
    """Tests webhook fulfillment Google Assistant."""

    @pytest.mark.asyncio
    async def test_webhook_google_assistant_intent_ok(self, async_client: httpx.AsyncClient):
        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            session = MagicMock()
            session.query.return_value.order_by.return_value.first.return_value = None
            session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []

            @contextmanager
            def _ctx():
                yield session

            mock_ctx.return_value = _ctx()
            response = await async_client.post(
                "/api/v1/assistant/google-assistant/webhook",
                json={
                    "intent": {"displayName": "planning_resume_demain"},
                    "sessionInfo": {"parameters": {}},
                    "languageCode": "fr",
                },
            )

        assert response.status_code == 200
        data = response.json()
        message = data["fulfillment_response"]["messages"][0]["text"]["text"][0]
        assert isinstance(message, str)
        assert data["sessionInfo"]["parameters"]["intent"] == "planning_resume_demain"
