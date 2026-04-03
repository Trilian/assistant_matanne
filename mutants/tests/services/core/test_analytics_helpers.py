from src.services.core.analytics import ServiceAnalytics


def test_calculer_roi_standard():
    assert ServiceAnalytics.calculer_roi(100, 120) == 20.0


def test_calculer_roi_sans_mise():
    assert ServiceAnalytics.calculer_roi(0, 50) == 0.0


def test_moyenne_ponderee_avec_poids():
    valeurs = [100, 200, 300]
    poids = [1, 1, 2]
    result = ServiceAnalytics.moyenne_ponderee(valeurs, poids)
    assert round(result, 2) == 225.0


def test_moyenne_ponderee_sans_poids():
    valeurs = [10, 20, 30]
    result = ServiceAnalytics.moyenne_ponderee(valeurs)
    assert result == 20.0
