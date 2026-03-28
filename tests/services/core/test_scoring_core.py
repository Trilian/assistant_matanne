from src.services.core.scoring import BaseScoringService


class _ScoringDummy(BaseScoringService):
    pass


def test_construire_score_borne_haute():
    score = _ScoringDummy.construire_score(1.7, ["a"])
    assert score.score == 1.0


def test_construire_score_borne_basse():
    score = _ScoringDummy.construire_score(-0.2, [])
    assert score.score == 0.0
    assert score.raison == "Suggestion generale"


def test_construire_score_raison_depuis_sources():
    score = _ScoringDummy.construire_score(0.73, ["meteo adaptee", "budget disponible"])
    assert score.score == 0.73
    assert "meteo adaptee" in score.raison
    assert len(score.sources) == 2
