"""
Tests pour src/modules/jeux/loto/utils.py

Tests complets pour atteindre 80%+ de couverture.
Module de fonctions pures pour l'analyse statistique Loto.
"""

from datetime import date
from decimal import Decimal

import pytest

from src.modules.jeux.loto.utils import (
    CHANCE_MAX,
    CHANCE_MIN,
    COUT_GRILLE,
    NB_NUMEROS,
    NUMERO_MAX,
    NUMERO_MIN,
    analyser_patterns_tirages,
    calculer_ecart,
    calculer_esperance_mathematique,
    calculer_frequences_numeros,
    generer_grille_aleatoire,
    generer_grille_chauds_froids,
    generer_grille_equilibree,
    generer_grille_eviter_populaires,
    identifier_numeros_chauds_froids,
    verifier_grille,
)

# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def tirages_exemple():
    """Crée une liste de tirages exemple pour les tests"""
    return [
        {
            "id": 1,
            "date_tirage": date(2024, 1, 1),
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
            "jackpot_euros": 2000000,
        },
        {
            "id": 2,
            "date_tirage": date(2024, 1, 4),
            "numero_1": 7,
            "numero_2": 12,
            "numero_3": 25,
            "numero_4": 38,
            "numero_5": 49,
            "numero_chance": 5,
            "jackpot_euros": 3000000,
        },
        {
            "id": 3,
            "date_tirage": date(2024, 1, 8),
            "numero_1": 3,
            "numero_2": 15,
            "numero_3": 23,
            "numero_4": 31,
            "numero_5": 42,
            "numero_chance": 3,
            "jackpot_euros": 4000000,
        },
    ]


@pytest.fixture
def frequences_exemple():
    """Crée des fréquences exemple pour les tests"""
    frequences = {}
    for i in range(1, 50):
        frequences[i] = {
            "frequence": i % 10,
            "pourcentage": (i % 10) * 10,
            "ecart": 50 - i,
        }
    return frequences


# ═══════════════════════════════════════════════════════════════════
# TESTS CALCUL FRÉQUENCES
# ═══════════════════════════════════════════════════════════════════


class TestCalculerFrequencesNumeros:
    """Tests pour le calcul des fréquences"""

    def test_frequences_basique(self, tirages_exemple):
        """Teste le calcul de fréquences basique"""
        result = calculer_frequences_numeros(tirages_exemple)

        assert result["nb_tirages"] == 3
        assert "frequences" in result
        assert "frequences_chance" in result

    def test_frequences_numero_present(self, tirages_exemple):
        """Teste qu'un numéro présent a une fréquence > 0"""
        result = calculer_frequences_numeros(tirages_exemple)

        # Le numéro 12 apparaît dans 2 tirages
        assert result["frequences"][12]["frequence"] == 2

    def test_frequences_numero_absent(self, tirages_exemple):
        """Teste qu'un numéro absent a une fréquence de 0"""
        result = calculer_frequences_numeros(tirages_exemple)

        # Le numéro 1 n'apparaît dans aucun tirage
        assert result["frequences"][1]["frequence"] == 0

    def test_frequences_chance(self, tirages_exemple):
        """Teste le calcul des fréquences du numéro chance"""
        result = calculer_frequences_numeros(tirages_exemple)

        # Le numéro chance 3 apparaît 2 fois
        assert result["frequences_chance"][3]["frequence"] == 2

    def test_frequences_liste_vide(self):
        """Teste avec une liste vide"""
        result = calculer_frequences_numeros([])

        assert result["nb_tirages"] == 0
        assert result["frequences"] == {}


class TestCalculerEcart:
    """Tests pour le calcul d'écart"""

    def test_ecart_numero_recent(self, tirages_exemple):
        """Teste l'écart pour un numéro récent"""
        # Le numéro 42 est dans le dernier tirage
        ecart = calculer_ecart(tirages_exemple, 42)
        assert ecart == 0

    def test_ecart_numero_ancien(self, tirages_exemple):
        """Teste l'écart pour un numéro plus ancien"""
        # Le numéro 45 est seulement dans le premier tirage
        ecart = calculer_ecart(tirages_exemple, 45)
        assert ecart == 2  # 2 tirages depuis

    def test_ecart_numero_absent(self, tirages_exemple):
        """Teste l'écart pour un numéro jamais sorti"""
        ecart = calculer_ecart(tirages_exemple, 1)
        assert ecart == len(tirages_exemple)


class TestIdentifierNumerosChaudsFroids:
    """Tests pour l'identification des numéros chauds/froids"""

    def test_identification_basique(self, frequences_exemple):
        """Teste l'identification basique"""
        result = identifier_numeros_chauds_froids(frequences_exemple)

        assert "chauds" in result
        assert "froids" in result
        assert "retard" in result

    def test_nombre_resultats(self, frequences_exemple):
        """Teste le nombre de résultats retournés"""
        result = identifier_numeros_chauds_froids(frequences_exemple, nb_top=5)

        assert len(result["chauds"]) == 5
        assert len(result["froids"]) == 5
        assert len(result["retard"]) == 5

    def test_frequences_vides(self):
        """Teste avec fréquences vides"""
        result = identifier_numeros_chauds_froids({})

        assert result["chauds"] == []
        assert result["froids"] == []


# ═══════════════════════════════════════════════════════════════════
# TESTS ANALYSE PATTERNS
# ═══════════════════════════════════════════════════════════════════


class TestAnalyserPatternsTirages:
    """Tests pour l'analyse des patterns"""

    def test_patterns_basique(self, tirages_exemple):
        """Teste l'analyse de patterns basique"""
        result = analyser_patterns_tirages(tirages_exemple)

        assert "somme_moyenne" in result
        assert "somme_min" in result
        assert "somme_max" in result
        assert "pairs_moyen" in result
        assert "ecart_moyen" in result

    def test_patterns_distribution_parite(self, tirages_exemple):
        """Teste la distribution de parité"""
        result = analyser_patterns_tirages(tirages_exemple)

        assert "distribution_parite" in result
        distribution = result["distribution_parite"]
        assert "0_pair_5_impair" in distribution
        assert "5_pair_0_impair" in distribution

    def test_patterns_paires_frequentes(self, tirages_exemple):
        """Teste les paires fréquentes"""
        result = analyser_patterns_tirages(tirages_exemple)

        assert "paires_frequentes" in result
        # Les paires doivent être des listes de 2 numéros
        if result["paires_frequentes"]:
            assert len(result["paires_frequentes"][0]["paire"]) == 2

    def test_patterns_liste_vide(self):
        """Teste avec une liste vide"""
        result = analyser_patterns_tirages([])

        assert result == {}


# ═══════════════════════════════════════════════════════════════════
# TESTS GÉNÉRATION GRILLES
# ═══════════════════════════════════════════════════════════════════


class TestGenererGrilleAleatoire:
    """Tests pour la génération de grille aléatoire"""

    def test_grille_complete(self):
        """Teste qu'une grille complète est générée"""
        grille = generer_grille_aleatoire()

        assert "numeros" in grille
        assert "numero_chance" in grille
        assert len(grille["numeros"]) == NB_NUMEROS

    def test_numeros_dans_plage(self):
        """Teste que les numéros sont dans la plage valide"""
        grille = generer_grille_aleatoire()

        for num in grille["numeros"]:
            assert NUMERO_MIN <= num <= NUMERO_MAX

    def test_chance_dans_plage(self):
        """Teste que le numéro chance est dans la plage valide"""
        grille = generer_grille_aleatoire()

        assert CHANCE_MIN <= grille["numero_chance"] <= CHANCE_MAX

    def test_numeros_uniques(self):
        """Teste que les numéros sont uniques"""
        grille = generer_grille_aleatoire()

        assert len(set(grille["numeros"])) == NB_NUMEROS

    def test_numeros_tries(self):
        """Teste que les numéros sont triés"""
        grille = generer_grille_aleatoire()

        assert grille["numeros"] == sorted(grille["numeros"])


class TestGenererGrilleEviterPopulaires:
    """Tests pour la génération évitant les numéros populaires"""

    def test_grille_complete(self):
        """Teste qu'une grille complète est générée"""
        grille = generer_grille_eviter_populaires()

        assert len(grille["numeros"]) == NB_NUMEROS
        assert grille["source"] == "eviter_populaires"

    def test_preference_numeros_hauts(self):
        """Teste la préférence pour les numéros > 31"""
        # Exécuter plusieurs fois pour vérifier la tendance
        total_hauts = 0
        nb_tests = 100

        for _ in range(nb_tests):
            grille = generer_grille_eviter_populaires()
            hauts = sum(1 for n in grille["numeros"] if n > 31)
            total_hauts += hauts

        # En moyenne, on devrait avoir 3-4 numéros > 31
        moyenne = total_hauts / nb_tests
        assert moyenne >= 2.5  # Tolérance pour l'aléatoire


class TestGenererGrilleEquilibree:
    """Tests pour la génération de grille équilibrée"""

    def test_grille_complete(self):
        """Teste qu'une grille complète est générée"""
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)

        assert len(grille["numeros"]) == NB_NUMEROS
        assert grille["source"] == "equilibree"

    def test_somme_proche_moyenne(self):
        """Teste que la somme est proche de la moyenne cible"""
        patterns = {"somme_moyenne": 125, "ecart_moyen": 35}
        grille = generer_grille_equilibree(patterns)

        somme = sum(grille["numeros"])
        # Tolérance de 30
        assert abs(somme - 125) < 30


class TestGenererGrilleChaudsFroids:
    """Tests pour la génération basée sur chauds/froids"""

    def test_grille_chauds(self, frequences_exemple):
        """Teste la stratégie numéros chauds"""
        grille = generer_grille_chauds_froids(frequences_exemple, "chauds")

        assert len(grille["numeros"]) == NB_NUMEROS
        assert "chauds" in grille["source"]

    def test_grille_froids(self, frequences_exemple):
        """Teste la stratégie numéros froids"""
        grille = generer_grille_chauds_froids(frequences_exemple, "froids")

        assert len(grille["numeros"]) == NB_NUMEROS
        assert "froids" in grille["source"]

    def test_grille_mixte(self, frequences_exemple):
        """Teste la stratégie mixte"""
        grille = generer_grille_chauds_froids(frequences_exemple, "mixte")

        assert len(grille["numeros"]) == NB_NUMEROS


# ═══════════════════════════════════════════════════════════════════
# TESTS VÉRIFICATION GRILLES
# ═══════════════════════════════════════════════════════════════════


class TestVerifierGrille:
    """Tests pour la vérification des grilles contre un tirage"""

    def test_grille_perdante(self):
        """Teste une grille perdante (0 numéro bon)"""
        grille = {"numeros": [1, 2, 3, 4, 6], "numero_chance": 1}
        tirage = {
            "numero_1": 10,
            "numero_2": 20,
            "numero_3": 30,
            "numero_4": 40,
            "numero_5": 49,
            "numero_chance": 5,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 0
        assert result["gagnant"] is False
        assert result["rang"] is None

    def test_grille_jackpot(self):
        """Teste une grille gagnante au jackpot"""
        grille = {"numeros": [5, 12, 23, 34, 45], "numero_chance": 3}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
            "jackpot_euros": 5000000,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 5
        assert result["chance_ok"] is True
        assert result["rang"] == 1
        assert result["gagnant"] is True

    def test_grille_5_numeros_sans_chance(self):
        """Teste avec 5 numéros bons mais pas la chance"""
        grille = {"numeros": [5, 12, 23, 34, 45], "numero_chance": 1}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 5
        assert result["chance_ok"] is False
        assert result["rang"] == 2

    def test_grille_4_numeros_avec_chance(self):
        """Teste avec 4 numéros bons + chance"""
        grille = {"numeros": [5, 12, 23, 34, 1], "numero_chance": 3}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 4
        assert result["chance_ok"] is True
        assert result["rang"] == 3

    def test_grille_4_numeros_sans_chance(self):
        """Teste avec 4 numéros bons sans chance"""
        grille = {"numeros": [5, 12, 23, 34, 1], "numero_chance": 1}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 4
        assert result["rang"] == 4

    def test_grille_3_numeros_avec_chance(self):
        """Teste avec 3 numéros bons + chance"""
        grille = {"numeros": [5, 12, 23, 1, 2], "numero_chance": 3}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 3
        assert result["rang"] == 5

    def test_grille_3_numeros_sans_chance(self):
        """Teste avec 3 numéros bons sans chance"""
        grille = {"numeros": [5, 12, 23, 1, 2], "numero_chance": 1}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 3
        assert result["rang"] == 6

    def test_grille_2_numeros_avec_chance(self):
        """Teste avec 2 numéros bons + chance"""
        grille = {"numeros": [5, 12, 1, 2, 3], "numero_chance": 3}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 2
        assert result["rang"] == 7

    def test_grille_2_numeros_sans_chance(self):
        """Teste avec 2 numéros bons sans chance"""
        grille = {"numeros": [5, 12, 1, 2, 3], "numero_chance": 1}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 2
        assert result["rang"] == 8

    def test_grille_1_numero_avec_chance(self):
        """Teste avec 1 numéro bon + chance (remboursement)"""
        grille = {"numeros": [5, 1, 2, 3, 4], "numero_chance": 3}
        tirage = {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 3,
        }

        result = verifier_grille(grille, tirage)

        assert result["bons_numeros"] == 1
        assert result["rang"] == 9
        assert result["gain"] == Decimal("2.20")


# ═══════════════════════════════════════════════════════════════════
# TESTS ESPÉRANCE MATHÉMATIQUE
# ═══════════════════════════════════════════════════════════════════


class TestCalculerEsperanceMathematique:
    """Tests pour le calcul de l'espérance mathématique"""

    def test_esperance_negative(self):
        """Teste que l'espérance est négative (c'est un jeu d'argent)"""
        result = calculer_esperance_mathematique()

        assert result["esperance"] < 0

    def test_cout_grille(self):
        """Teste le coût d'une grille"""
        result = calculer_esperance_mathematique()

        assert result["cout_grille"] == float(COUT_GRILLE)

    def test_probabilites_presentes(self):
        """Teste que les probabilités sont présentes"""
        result = calculer_esperance_mathematique()

        assert "probabilites" in result
        assert len(result["probabilites"]) == 9  # 9 rangs

    def test_conclusion_presente(self):
        """Teste que la conclusion est présente"""
        result = calculer_esperance_mathematique()

        assert "conclusion" in result
        assert "perdez" in result["conclusion"].lower()


# ═══════════════════════════════════════════════════════════════════
# TESTS SIMULATION STRATÉGIES
# ═══════════════════════════════════════════════════════════════════


class TestSimulerStrategie:
    """Tests pour la simulation de stratégies"""

    def test_simulation_aleatoire(self, tirages_exemple):
        """Teste la simulation avec stratégie aléatoire"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie(tirages_exemple, strategie="aleatoire")

        assert result["strategie"] == "aleatoire"
        assert result["nb_tirages"] == 3
        assert "mises_totales" in result
        assert "gains_totaux" in result

    def test_simulation_eviter_populaires(self, tirages_exemple):
        """Teste la simulation avec stratégie éviter populaires"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie(tirages_exemple, strategie="eviter_populaires")

        assert result["strategie"] == "eviter_populaires"
        assert result["nb_grilles"] == 3

    def test_simulation_equilibree(self, tirages_exemple):
        """Teste la simulation avec stratégie équilibrée"""
        from src.modules.jeux.loto.utils import analyser_patterns_tirages, simuler_strategie

        patterns = analyser_patterns_tirages(tirages_exemple)
        result = simuler_strategie(tirages_exemple, strategie="equilibree", patterns=patterns)

        assert result["strategie"] == "equilibree"

    def test_simulation_chauds(self, tirages_exemple, frequences_exemple):
        """Teste la simulation avec stratégie numéros chauds"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie(
            tirages_exemple, strategie="chauds", frequences=frequences_exemple
        )

        assert result["strategie"] == "chauds"

    def test_simulation_froids(self, tirages_exemple, frequences_exemple):
        """Teste la simulation avec stratégie numéros froids"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie(
            tirages_exemple, strategie="froids", frequences=frequences_exemple
        )

        assert result["strategie"] == "froids"

    def test_simulation_sans_tirages(self):
        """Teste la simulation sans tirages"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie([])

        assert "erreur" in result

    def test_simulation_plusieurs_grilles(self, tirages_exemple):
        """Teste la simulation avec plusieurs grilles par tirage"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie(tirages_exemple, nb_grilles_par_tirage=3)

        assert result["nb_grilles"] == 9  # 3 tirages * 3 grilles

    def test_simulation_roi(self, tirages_exemple):
        """Teste le calcul du ROI dans la simulation"""
        from src.modules.jeux.loto.utils import simuler_strategie

        result = simuler_strategie(tirages_exemple)

        assert "roi" in result
        assert "profit" in result
        assert isinstance(result["roi"], int | float)


class TestComparerStrategies:
    """Tests pour la comparaison de stratégies"""

    def test_comparaison_basique(self, tirages_exemple):
        """Teste la comparaison basique de stratégies"""
        from src.modules.jeux.loto.utils import comparer_strategies

        result = comparer_strategies(tirages_exemple)

        assert "resultats" in result
        assert "classement" in result
        assert "meilleure_strategie" in result
        assert len(result["resultats"]) == 5

    def test_comparaison_sans_tirages(self):
        """Teste la comparaison sans tirages"""
        from src.modules.jeux.loto.utils import comparer_strategies

        result = comparer_strategies([])

        assert "erreur" in result

    def test_comparaison_classement(self, tirages_exemple):
        """Teste que le classement est retourné"""
        from src.modules.jeux.loto.utils import comparer_strategies

        result = comparer_strategies(tirages_exemple)

        assert len(result["classement"]) == 5
        assert result["meilleure_strategie"] in result["classement"]


# ═══════════════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour vérifier les constantes du Loto français"""

    def test_plage_numeros(self):
        """Teste la plage des numéros principaux"""
        assert NUMERO_MIN == 1
        assert NUMERO_MAX == 49

    def test_plage_chance(self):
        """Teste la plage du numéro chance"""
        assert CHANCE_MIN == 1
        assert CHANCE_MAX == 10

    def test_nb_numeros(self):
        """Teste le nombre de numéros à choisir"""
        assert NB_NUMEROS == 5

    def test_cout_grille(self):
        """Teste le coût d'une grille"""
        assert COUT_GRILLE == Decimal("2.20")
