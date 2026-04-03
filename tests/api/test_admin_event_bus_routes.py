"""Tests Event Bus Event Bus (API + flux E2E publication->action)."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport


@pytest_asyncio.fixture
async def async_client():
    from src.api.main import app
    from src.api.dependencies import require_auth

    app.dependency_overrides[require_auth] = lambda: {"id": "admin-test", "role": "admin"}
    async with httpx.AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        yield client
    app.dependency_overrides.clear()


class TestAdminEventBusRoutes:
    @pytest.mark.asyncio
    async def test_lire_evenements_retourne_historique_et_metriques(self, async_client: httpx.AsyncClient):
        fake_event = SimpleNamespace(
            event_id="evt-1",
            type="stock.modifie",
            source="tests",
            timestamp=datetime(2026, 4, 2, 12, 0, 0),
            data={"article_id": 1},
        )
        fake_bus = SimpleNamespace(
            obtenir_historique=lambda **_: [fake_event],
            obtenir_metriques=lambda: {"total": 1},
        )

        with patch("src.services.core.events.obtenir_bus", return_value=fake_bus):
            response = await async_client.get("/api/v1/admin/events?limite=10")

        assert response.status_code == 200
        payload = response.json()
        assert payload["total"] == 1
        assert payload["items"][0]["type"] == "stock.modifie"
        assert payload["metriques"]["total"] == 1


class TestEventBusEndToEnd:
    def test_publication_declenche_subscriber_et_action(self):
        from src.services.core.events.bus import BusEvenements

        bus = BusEvenements(historique_taille=20)
        actions: list[str] = []

        def subscriber(event):
            if event.type == "planning.genere":
                actions.append(f"courses:{event.data.get('planning_id')}")

        bus.souscrire("planning.genere", subscriber)
        notified = bus.emettre("planning.genere", data={"planning_id": 42}, source="tests")

        assert notified == 1
        assert actions == ["courses:42"]

    def test_pipeline_event_bus_avec_wildcard(self):
        from src.services.core.events.bus import BusEvenements

        bus = BusEvenements(historique_taille=20)
        journal: list[str] = []

        def subscriber_all(event):
            journal.append(event.type)

        bus.souscrire("*", subscriber_all)
        bus.emettre("stock.modifie", data={"article_id": 1})
        bus.emettre("courses.generees", data={"liste_id": 12})

        assert journal == ["stock.modifie", "courses.generees"]
        historique = bus.obtenir_historique(limite=10)
        assert len(historique) == 2
