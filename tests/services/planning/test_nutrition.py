"""Tests unitaires du scoring nutritionnel planning."""

from typing import Any, cast

from src.services.planning.nutrition import evaluer_equilibre_repas


class _RecetteFake:
    def __init__(self, categorie: str | None):
        self.categorie_nutritionnelle = categorie
        self.type_proteines = None


class _RepasFake:
    def __init__(
        self,
        *,
        categorie: str | None,
        type_repas: str = "diner",
        legumes: str | None = None,
        feculents: str | None = None,
        proteine_accompagnement: str | None = None,
    ):
        self.type_repas = type_repas
        self.recette = _RecetteFake(categorie)
        self.legumes = legumes
        self.legumes_recette_id = None
        self.feculents = feculents
        self.feculents_recette_id = None
        self.proteine_accompagnement = proteine_accompagnement
        self.proteine_accompagnement_recette_id = None


def test_placeholder_feculents_compte_comme_manquant():
    """Un texte type 'pas de féculents' ne doit pas être validé comme féculent présent."""
    repas = _RepasFake(
        categorie="proteines_viande_rouge",
        legumes="Haricots verts",
        feculents="pas de féculents",
    )

    resultat = evaluer_equilibre_repas(cast(Any, repas))

    assert resultat["score_equilibre"] == 66
    assert "Féculents manquants" in (resultat["alertes_equilibre"] or [])


def test_categorie_mixte_ne_donne_pas_points_automatiques():
    """La catégorie mixte ne doit pas attribuer légumes/féculents automatiquement."""
    repas = _RepasFake(
        categorie="mixte",
        legumes="aucun",
        feculents="none",
        proteine_accompagnement=None,
    )

    resultat = evaluer_equilibre_repas(cast(Any, repas))

    assert resultat["score_equilibre"] == 0
    assert "Pas de légumes" in (resultat["alertes_equilibre"] or [])
    assert "Féculents manquants" in (resultat["alertes_equilibre"] or [])
    assert "Protéine manquante" in (resultat["alertes_equilibre"] or [])
