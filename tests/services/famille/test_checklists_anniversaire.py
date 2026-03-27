"""Tests unitaires pour la checklist anniversaire intelligente."""

import pytest

from src.services.famille.checklists_anniversaire import (
    _profil_anniversaire,
    _relation_est_enfant,
    _template_categorie_par_profil,
)


@pytest.mark.unit
def test_relation_est_enfant_true() -> None:
    assert _relation_est_enfant("enfant") is True
    assert _relation_est_enfant("fils") is True
    assert _relation_est_enfant("nièce") is True


@pytest.mark.unit
def test_relation_est_enfant_false() -> None:
    assert _relation_est_enfant("parent") is False
    assert _relation_est_enfant(None) is False


@pytest.mark.unit
@pytest.mark.parametrize(
    ("age", "relation", "expected"),
    [
        (2, "enfant", "tout_petit"),
        (5, "enfant", "enfant"),
        (10, "cousin", "pre_ado"),
        (16, "ami", "ado"),
        (35, "enfant", "enfant"),
        (35, "parent", "adulte"),
    ],
)
def test_profil_anniversaire(age: int, relation: str, expected: str) -> None:
    assert _profil_anniversaire(age, relation) == expected


@pytest.mark.unit
def test_template_categorie_enfant() -> None:
    template = _template_categorie_par_profil("enfant")
    assert "cadeau" in template
    assert "activite" in template
    assert "repas" in template
    assert any(item["libelle"] == "Cadeau principal" for item in template["cadeau"])


@pytest.mark.unit
def test_template_categorie_adulte() -> None:
    template = _template_categorie_par_profil("adulte")
    assert "cadeau" in template
    assert "repas" in template
    assert "organisation" in template
    assert any(item["libelle"] == "Repas / dîner" for item in template["repas"])
