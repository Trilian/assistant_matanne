from src.services.core.budget_seuils import (
    calculer_pourcentage_utilisation,
    evaluer_seuils_budget,
)


def test_calculer_pourcentage_utilisation_basique():
    assert calculer_pourcentage_utilisation(50, 100) == 50.0


def test_calculer_pourcentage_limite_zero():
    assert calculer_pourcentage_utilisation(10, 0) == 0.0


def test_evaluer_seuils_budget_niveau_normal():
    etat = evaluer_seuils_budget(20, 100)
    assert etat.niveau == "normal"
    assert etat.seuils_franchis == []


def test_evaluer_seuils_budget_niveau_attention():
    etat = evaluer_seuils_budget(80, 100)
    assert etat.niveau == "attention"
    assert 75 in etat.seuils_franchis


def test_evaluer_seuils_budget_niveau_bloque():
    etat = evaluer_seuils_budget(120, 100)
    assert etat.niveau == "bloque"
    assert etat.pourcentage == 120.0
    assert 100 in etat.seuils_franchis
