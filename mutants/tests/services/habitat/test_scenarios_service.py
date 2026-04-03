from decimal import Decimal

from src.services.habitat.scenarios_service import ScenariosHabitatService


class FauxCritere:
    def __init__(self, poids: str, note: str):
        self.poids = Decimal(poids)
        self.note = Decimal(note)


class FauxQuery:
    def __init__(self, items):
        self.items = items

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self.items


class FauxSession:
    def __init__(self, items):
        self.items = items

    def query(self, model):
        return FauxQuery(self.items)


def test_calculer_score_global_pondere():
    session = FauxSession([
        FauxCritere("1.0", "8.0"),
        FauxCritere("2.0", "6.0"),
    ])
    score = ScenariosHabitatService.calculer_score_global(session, 1)
    assert score == Decimal("66.67")


def test_calculer_score_global_sans_criteres():
    session = FauxSession([])
    score = ScenariosHabitatService.calculer_score_global(session, 1)
    assert score == Decimal("0")
