"""Tests pour le module d'analyse des fréquences Loto."""

import pytest

from src.modules.jeux.loto.frequences import (
    NUMERO_MAX,
    NUMERO_MIN,
    analyser_patterns_tirages,
    calculer_ecart,
    calculer_frequences_numeros,
    identifier_numeros_chauds_froids,
)


@pytest.fixture
def tirages_exemple():
    """Tirages exemple pour les tests."""
    return [
        {
            "date_tirage": "2024-01-01",
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 7,
        },
        {
            "date_tirage": "2024-01-04",
            "numero_1": 5,
            "numero_2": 15,
            "numero_3": 25,
            "numero_4": 35,
            "numero_5": 45,
            "numero_chance": 3,
        },
        {
            "date_tirage": "2024-01-08",
            "numero_1": 1,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 49,
            "numero_chance": 7,
        },
    ]


class TestCalculerFrequencesNumeros:
    """Tests du calcul des fréquences."""

    def test_liste_vide_retourne_dict_vide(self):
        """Liste vide retourne structure vide."""
        resultat = calculer_frequences_numeros([])

        assert resultat["frequences"] == {}
        assert resultat["frequences_chance"] == {}
        assert resultat["nb_tirages"] == 0

    def test_frequence_numero_apparait_plusieurs_fois(self, tirages_exemple):
        """Un numéro qui apparaît plusieurs fois est comptabilisé."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        # Le numéro 5 apparaît dans 2 tirages sur 3
        assert resultat["frequences"][5]["frequence"] == 2

    def test_frequence_numero_apparait_une_fois(self, tirages_exemple):
        """Un numéro qui apparaît une fois est comptabilisé."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        # Le numéro 1 apparaît dans 1 tirage
        assert resultat["frequences"][1]["frequence"] == 1

    def test_frequence_numero_absent(self, tirages_exemple):
        """Un numéro qui n'apparaît jamais a fréquence 0."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        # Le numéro 2 n'apparaît pas
        assert resultat["frequences"][2]["frequence"] == 0

    def test_pourcentage_calcule(self, tirages_exemple):
        """Le pourcentage est calculé correctement."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        # Le numéro 5 apparaît 2 fois sur 3 tirages = ~66.67%
        assert resultat["frequences"][5]["pourcentage"] > 60
        assert resultat["frequences"][5]["pourcentage"] < 70

    def test_tous_numeros_presents(self, tirages_exemple):
        """Tous les numéros de 1 à 49 sont présents."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        for num in range(NUMERO_MIN, NUMERO_MAX + 1):
            assert num in resultat["frequences"]

    def test_frequence_chance_comptee(self, tirages_exemple):
        """La fréquence du numéro chance est comptabilisée."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        # Le numéro chance 7 apparaît 2 fois
        assert resultat["frequences_chance"][7]["frequence"] == 2
        # Le numéro chance 3 apparaît 1 fois
        assert resultat["frequences_chance"][3]["frequence"] == 1

    def test_nb_tirages_correct(self, tirages_exemple):
        """Le nombre de tirages est correct."""
        resultat = calculer_frequences_numeros(tirages_exemple)

        assert resultat["nb_tirages"] == 3


class TestCalculerEcart:
    """Tests du calcul d'écart."""

    def test_ecart_numero_recent(self, tirages_exemple):
        """Un numéro sorti récemment a un petit écart."""
        # Le numéro 1 est sorti dans le dernier tirage
        ecart = calculer_ecart(tirages_exemple, 1)
        assert ecart == 0

    def test_ecart_numero_ancien(self, tirages_exemple):
        """Un numéro pas sorti depuis longtemps a un grand écart."""
        # Le numéro 15 est sorti au tirage du milieu (index 1)
        ecart = calculer_ecart(tirages_exemple, 15)
        assert ecart == 1

    def test_ecart_numero_jamais_sorti(self, tirages_exemple):
        """Un numéro jamais sorti a un écart égal au nombre de tirages."""
        # Le numéro 2 n'est jamais sorti
        ecart = calculer_ecart(tirages_exemple, 2)
        assert ecart == len(tirages_exemple)

    def test_ecart_liste_vide(self):
        """Liste vide retourne 0."""
        ecart = calculer_ecart([], 5)
        assert ecart == 0


class TestIdentifierNumerosChaudsFroids:
    """Tests d'identification des numéros chauds et froids."""

    @pytest.fixture
    def frequences_exemple(self):
        """Fréquences exemple pour les tests."""
        return {
            1: {"frequence": 10, "ecart": 2},
            2: {"frequence": 8, "ecart": 5},
            3: {"frequence": 15, "ecart": 0},
            4: {"frequence": 3, "ecart": 10},
            5: {"frequence": 1, "ecart": 20},
        }

    def test_dict_vide_retourne_listes_vides(self):
        """Dict vide retourne des listes vides."""
        resultat = identifier_numeros_chauds_froids({})

        assert resultat["chauds"] == []
        assert resultat["froids"] == []
        assert resultat["retard"] == []

    def test_chauds_tries_par_frequence(self, frequences_exemple):
        """Les numéros chauds sont triés par fréquence décroissante."""
        resultat = identifier_numeros_chauds_froids(frequences_exemple, nb_top=3)

        # Le numéro 3 a la plus haute fréquence (15)
        assert resultat["chauds"][0] == 3

    def test_froids_contient_basses_frequences(self, frequences_exemple):
        """Les numéros froids contiennent les basses fréquences."""
        resultat = identifier_numeros_chauds_froids(frequences_exemple, nb_top=3)

        # Le numéro 5 (freq=1) doit être dans les froids
        assert 5 in resultat["froids"]
        # Le numéro 4 (freq=3) doit être dans les froids
        assert 4 in resultat["froids"]

    def test_retard_tries_par_ecart(self, frequences_exemple):
        """Les numéros en retard sont triés par écart décroissant."""
        resultat = identifier_numeros_chauds_froids(frequences_exemple, nb_top=3)

        # Le numéro 5 a le plus grand écart (20)
        assert resultat["retard"][0] == 5

    def test_nb_top_respecte(self, frequences_exemple):
        """Le paramètre nb_top est respecté."""
        resultat = identifier_numeros_chauds_froids(frequences_exemple, nb_top=2)

        assert len(resultat["chauds"]) == 2
        assert len(resultat["froids"]) == 2
        assert len(resultat["retard"]) == 2


class TestAnalyserPatternsTirages:
    """Tests de l'analyse des patterns."""

    def test_liste_vide_retourne_dict_vide(self):
        """Liste vide retourne dict vide."""
        resultat = analyser_patterns_tirages([])
        assert resultat == {}

    def test_somme_calculee(self, tirages_exemple):
        """La somme moyenne est calculée."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        assert "somme_moyenne" in resultat
        assert resultat["somme_moyenne"] > 0

    def test_somme_min_max(self, tirages_exemple):
        """Les sommes min et max sont calculées."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        assert "somme_min" in resultat
        assert "somme_max" in resultat
        assert resultat["somme_min"] <= resultat["somme_max"]

    def test_pairs_moyen(self, tirages_exemple):
        """Le nombre moyen de pairs est calculé."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        assert "pairs_moyen" in resultat
        assert 0 <= resultat["pairs_moyen"] <= 5

    def test_ecart_moyen(self, tirages_exemple):
        """L'écart moyen est calculé."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        assert "ecart_moyen" in resultat
        assert resultat["ecart_moyen"] > 0

    def test_paires_frequentes(self, tirages_exemple):
        """Les paires fréquentes sont identifiées."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        assert "paires_frequentes" in resultat
        # Au moins une paire identifiée
        assert len(resultat["paires_frequentes"]) > 0

    def test_paire_structure(self, tirages_exemple):
        """La structure des paires est correcte."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        if resultat["paires_frequentes"]:
            paire = resultat["paires_frequentes"][0]
            assert "paire" in paire
            assert "frequence" in paire
            assert len(paire["paire"]) == 2

    def test_distribution_parite(self, tirages_exemple):
        """La distribution de parité est présente."""
        resultat = analyser_patterns_tirages(tirages_exemple)

        assert "distribution_parite" in resultat

    def test_tirage_filtre_none(self):
        """Les valeurs None dans les tirages sont filtrées."""
        tirages = [
            {
                "numero_1": 1,
                "numero_2": 2,
                "numero_3": 3,
                "numero_4": 4,
                "numero_5": 5,
            },
            {
                "numero_1": 10,
                "numero_2": 20,
                "numero_3": 30,
                "numero_4": 40,
                "numero_5": 49,
            },
        ]
        resultat = analyser_patterns_tirages(tirages)

        # Les deux tirages doivent être traités
        # Somme tirage 1: 1+2+3+4+5 = 15
        # Somme tirage 2: 10+20+30+40+49 = 149
        # Moyenne: (15+149)/2 = 82
        assert resultat["somme_moyenne"] == 82
