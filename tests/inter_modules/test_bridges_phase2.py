"""Tests Phase 2 — bridges EventBus inter-modules.

Ces tests ciblent:
- le câblage des subscriptions phase 2,
- l'émission d'événements planning lors de la validation.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest


class _BusFaux:
    def __init__(self) -> None:
        self.subscriptions: list[tuple[str, object, int]] = []
        self.events: list[tuple[str, dict, str]] = []

    def souscrire(self, event_type: str, handler: object, priority: int = 0) -> None:
        self.subscriptions.append((event_type, handler, priority))

    def emettre(self, event_type: str, data: dict | None = None, source: str = "") -> int:
        self.events.append((event_type, data or {}, source))
        return 1


@pytest.mark.asyncio
async def test_valider_planning_emet_events_phase2(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.api.routes import planning as routes_planning

    bus = _BusFaux()

    async def _executer_async_faux(_callable):
        return SimpleNamespace(data={"semaine_debut": "2026-04-06"})

    class _DispatcherFaux:
        def envoyer(self, **_kwargs) -> None:
            return None

    monkeypatch.setattr(routes_planning, "executer_async", _executer_async_faux)
    monkeypatch.setattr("src.services.core.events.obtenir_bus", lambda: bus)
    monkeypatch.setattr(
        "src.services.core.notifications.get_dispatcher_notifications",
        lambda: _DispatcherFaux(),
    )

    await routes_planning.valider_planning(planning_id=42, user={"sub": "u-test"})

    emitted_types = [event_type for event_type, _data, _source in bus.events]
    assert "planning.valide" in emitted_types
    assert "planning.semaine_validee" in emitted_types
