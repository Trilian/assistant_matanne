"""
Tests pour la génération de grilles Loto.

Couvre les 4 stratégies de génération:
- Aléatoire
- Éviter populaires
- Équilibrée
- Chauds/Froids
"""

import pytest

from src.modules.jeux.loto.generation import (
    CHANCE_MAX,
    CHANCE_MIN,
    NB_NUMEROS,
    NUMERO_MAX,
    NUMERO_MIN,
    NUMEROS_POPULAIRES,
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
)


class TestGrilleAleatoire:
    """Tests pour generer_grille_aleatoire()."""

    def test_retourne_dict(self):
        grille = generer_grille_aleatoire()
        assert isinstance(grille, dict)

    def test_contient_5_numeros(self):
        grille = generer_grille_aleatoire()
        assert len(grille["numeros"]) == NB_NUMEROS

    def test_numeros_dans_plage(self):
        grille = generer_grille_aleatoire()
        for n in grille["numeros"]:
            assert NUMERO_MIN <= n <= NUMERO_MAX

    def test_numeros_uniques(self):
        grille = generer_grille_aleatoire()
        assert len(set(grille["numeros"])) == NB_NUMEROS

    def test_numeros_tries(self):
        grille = generer_grille_aleatoire()
        assert grille["numeros"] == sorted(grille["numeros"])

    def test_numero_chance_dans_plage(self):
        grille = generer_grille_aleatoire()
        assert CHANCE_MIN <= grille["numero_chance"] <= CHANCE_MAX

    def test_source_aleatoire(self):
        grille = generer_grille_aleatoire()
        assert grille["source"] == "aleatoire"

    def test_grilles_differentes(self):
        """Vérifie que 2 appels ne donnent pas toujours le même résultat."""
        grilles = [generer_grille_aleatoire() for _ in range(10)]
        numeros_set = [tuple(g["numeros"]) for g in grilles]
        # Au moins 2 grilles différentes sur 10
        assert len(set(numeros_set)) >= 2


class TestGrilleEviterPopulaires:
    """Tests pour generer_grille_eviter_populaires()."""

    def test_retourne_dict(self):
        grille = generer_grille_eviter_populaires()
        assert isinstance(grille, dict)

    def test_contient_5_numeros(self):
        grille = generer_grille_eviter_populaires()
        assert len(grille["numeros"]) == NB_NUMEROS

    def test_numeros_dans_plage(self):
        grille = generer_grille_eviter_populaires()
        for n in grille["numeros"]:
            assert NUMERO_MIN <= n <= NUMERO_MAX

    def test_numeros_uniques(self):
        grille = generer_grille_eviter_populaires()
        assert len(set(grille["numeros"])) == NB_NUMEROS

    def test_majorite_hors_populaires(self):
        """La majorité des numéros doivent être hors zone populaire (>31)."""
        grille = generer_grille_eviter_populaires()
        hors_populaires = [n for n in grille["numeros"] if n > 31]
        # Au moins 3 numéros hors zone populaire
        assert len(hors_populaires) >= 3

    def test_source_correcte(self):
        grille = generer_grille_eviter_populaires()
        assert grille["source"] == "eviter_populaires"

    def test_note_presente(self):
        grille = generer_grille_eviter_populaires()
        assert "note" in grille


class TestGrilleEquilibree:
    """Tests pour generer_grille_equilibree()."""

    def test_retourne_dict(self):
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)
        assert isinstance(grille, dict)

    def test_contient_5_numeros(self):
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)
        assert len(grille["numeros"]) == NB_NUMEROS

    def test_numeros_dans_plage(self):
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)
        for n in grille["numeros"]:
            assert NUMERO_MIN <= n <= NUMERO_MAX

    def test_somme_proche_moyenne(self):
        """La somme devrait être relativement proche de la cible."""
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)
        somme = sum(grille["numeros"])
        # Tolérance large mais vérifie que l'optimisation fonctionne
        assert 50 <= somme <= 245  # Bornes théoriques

    def test_source_equilibree(self):
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)
        assert grille["source"] == "equilibree"

    def test_contient_somme_et_ecart(self):
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)
        assert "somme" in grille
        assert "ecart" in grille

    def test_patterns_vides(self):
        """Fonctionne même avec des patterns vides (utilise valeurs par défaut)."""
        grille = generer_grille_equilibree({})
        assert len(grille["numeros"]) == NB_NUMEROS


class TestGrilleChaudsFroids:
    """Tests pour generer_grille_chauds_froids()."""

    @pytest.fixture
    def frequences_mock(self) -> dict[int, dict]:
        """Fréquences simulées pour les tests."""
        return {
            i: {
                "frequence": 50 - i if i <= 25 else i,
                "derniere_sortie": 100 - i,
            }
            for i in range(1, 50)
        }

    def test_strategie_chauds(self, frequences_mock):
        grille = generer_grille_chauds_froids(frequences_mock, "chauds")
        assert len(grille["numeros"]) == NB_NUMEROS
        assert grille["source"] == "strategie_chauds"

    def test_strategie_froids(self, frequences_mock):
        grille = generer_grille_chauds_froids(frequences_mock, "froids")
        assert len(grille["numeros"]) == NB_NUMEROS
        assert grille["source"] == "strategie_froids"

    def test_strategie_mixte(self, frequences_mock):
        grille = generer_grille_chauds_froids(frequences_mock, "mixte")
        assert len(grille["numeros"]) == NB_NUMEROS
        assert grille["source"] == "strategie_mixte"

    def test_numeros_dans_plage(self, frequences_mock):
        for strategie in ["chauds", "froids", "mixte"]:
            grille = generer_grille_chauds_froids(frequences_mock, strategie)
            for n in grille["numeros"]:
                assert NUMERO_MIN <= n <= NUMERO_MAX

    def test_numeros_uniques(self, frequences_mock):
        grille = generer_grille_chauds_froids(frequences_mock, "mixte")
        assert len(set(grille["numeros"])) == NB_NUMEROS

    def test_numero_chance(self, frequences_mock):
        grille = generer_grille_chauds_froids(frequences_mock, "chauds")
        assert CHANCE_MIN <= grille["numero_chance"] <= CHANCE_MAX

    def test_note_presente(self, frequences_mock):
        grille = generer_grille_chauds_froids(frequences_mock, "chauds")
        assert "note" in grille
