"""Tests Phase 2 — bridges EventBus inter-modules.

Ces tests ciblent:
- l'émission d'événements planning lors de la validation,
- le flux bout-en-bout planning -> courses -> notification.
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


@pytest.mark.integration
def test_e2e_planning_vers_courses_vers_notif(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.services.core.events import subscribers
    from src.services.core.events.bus import BusEvenements

    class _Champ:
        def __init__(self, nom: str):
            self.nom = nom

        def __eq__(self, other):
            return (self.nom, "==", other)

        def is_(self, other):
            return (self.nom, "is", other)

    class _RepasModel:
        planning_id = _Champ("planning_id")

    class _RecetteModel:
        id = _Champ("id")

    class _ArticleCoursesModel:
        ingredient_id = _Champ("ingredient_id")
        achete = _Champ("achete")

        def __init__(self, **kwargs):
            self.ingredient_id = kwargs.get("ingredient_id")
            self.quantite_necessaire = kwargs.get("quantite_necessaire")
            self.priorite = kwargs.get("priorite")
            self.suggere_par_ia = kwargs.get("suggere_par_ia")
            self.notes = kwargs.get("notes")
            self.achete = False

    class _QueryFaux:
        def __init__(self, session, model):
            self.session = session
            self.model = model
            self.conditions = []

        def filter(self, *conditions):
            self.conditions.extend(conditions)
            return self

        def all(self):
            if self.model is _RepasModel:
                return self.session.repas
            return []

        def first(self):
            if self.model is _RecetteModel:
                recette_id = None
                for cond in self.conditions:
                    if isinstance(cond, tuple) and cond[0] == "id" and cond[1] == "==":
                        recette_id = cond[2]
                return self.session.recettes.get(recette_id)

            if self.model is _ArticleCoursesModel:
                ingredient_id = None
                achete = None
                for cond in self.conditions:
                    if isinstance(cond, tuple) and cond[0] == "ingredient_id":
                        ingredient_id = cond[2]
                    if isinstance(cond, tuple) and cond[0] == "achete":
                        achete = cond[2]
                for article in self.session.articles:
                    if article.ingredient_id == ingredient_id and article.achete is achete:
                        return article
                return None

            return None

    class _SessionFaux:
        def __init__(self):
            self.repas = [SimpleNamespace(recette_id=1)]
            self.recettes = {
                1: SimpleNamespace(
                    ingredients=[SimpleNamespace(ingredient_id=11, quantite=2)],
                )
            }
            self.articles = []

        def query(self, model):
            return _QueryFaux(self, model)

        def add(self, article):
            self.articles.append(article)

        def commit(self):
            return None

    class _ContexteDBFaux:
        def __init__(self, session):
            self._session = session

        def __enter__(self):
            return self._session

        def __exit__(self, exc_type, exc, tb):
            return False

    notifications = []

    class _ServiceNtfyFaux:
        def envoyer_sync(self, notification):
            notifications.append(notification)
            return {"success": True}

    bus = BusEvenements()
    session = _SessionFaux()

    monkeypatch.setattr("src.services.core.events.bus.obtenir_bus", lambda: bus)
    monkeypatch.setattr("src.core.db.obtenir_contexte_db", lambda: _ContexteDBFaux(session))

    import src.core.models as models

    monkeypatch.setattr(models, "Repas", _RepasModel)
    monkeypatch.setattr(models, "Recette", _RecetteModel)
    monkeypatch.setattr(models, "ArticleCourses", _ArticleCoursesModel)
    monkeypatch.setattr(models, "Ingredientx", object, raising=False)
    monkeypatch.setattr("src.services.core.notifications.notif_ntfy.ServiceNtfy", _ServiceNtfyFaux)
    monkeypatch.setattr("src.services.core.notifications.types.NotificationNtfy", lambda **kwargs: kwargs)

    bus.souscrire("planning.valide", subscribers._generer_courses_depuis_planning, priority=80)
    bus.souscrire("courses.generees", subscribers._notifier_courses_generees, priority=79)

    notified = bus.emettre(
        "planning.valide",
        {"planning_id": 7, "semaine_debut": "2026-04-06"},
        source="test",
    )

    assert notified >= 1
    assert len(session.articles) == 1
    assert session.articles[0].ingredient_id == 11
    assert len(notifications) == 1
    assert notifications[0]["click_url"] == "/cuisine/courses"
