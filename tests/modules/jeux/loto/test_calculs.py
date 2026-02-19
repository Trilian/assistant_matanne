"""Tests pour le module de calculs Loto."""

from decimal import Decimal

import pytest

from src.modules.jeux.loto.calculs import (
    COUT_GRILLE,
    GAINS_PAR_RANG,
    PROBA_JACKPOT,
    calculer_esperance_mathematique,
    verifier_grille,
)


class TestConstantes:
    """Tests des constantes du module."""

    def test_cout_grille_valide(self):
        """Le coût de la grille doit être 2.20€."""
        assert COUT_GRILLE == Decimal("2.20")

    def test_gains_par_rang_tous_definis(self):
        """Tous les rangs de 1 à 9 doivent être définis."""
        for rang in range(1, 10):
            assert rang in GAINS_PAR_RANG

    def test_gains_decroissants(self):
        """Les gains doivent décroître du rang 2 au rang 9."""
        # Rang 1 est variable (jackpot)
        gains_fixes = [GAINS_PAR_RANG[r] for r in range(2, 10)]
        assert gains_fixes == sorted(gains_fixes, reverse=True)

    def test_proba_jackpot(self):
        """Probabilité jackpot environ 1/19M."""
        assert PROBA_JACKPOT < 1e-7
        assert PROBA_JACKPOT > 1e-8


class TestVerifierGrille:
    """Tests de vérification des grilles."""

    @pytest.fixture
    def tirage_exemple(self):
        """Tirage exemple pour les tests."""
        return {
            "numero_1": 5,
            "numero_2": 12,
            "numero_3": 23,
            "numero_4": 34,
            "numero_5": 45,
            "numero_chance": 7,
            "jackpot_euros": 10_000_000,
        }

    def test_jackpot_5_numeros_plus_chance(self, tirage_exemple):
        """Grille gagnante = 5 bons numéros + numéro chance."""
        grille = {"numeros": [5, 12, 23, 34, 45], "numero_chance": 7}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 1
        assert resultat["bons_numeros"] == 5
        assert resultat["chance_ok"] is True
        assert resultat["gagnant"] is True
        assert resultat["gain"] == Decimal("10000000")

    def test_rang_2_cinq_numeros_sans_chance(self, tirage_exemple):
        """5 bons numéros sans le numéro chance = Rang 2."""
        grille = {"numeros": [5, 12, 23, 34, 45], "numero_chance": 1}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 2
        assert resultat["bons_numeros"] == 5
        assert resultat["chance_ok"] is False
        assert resultat["gain"] == Decimal("100000")

    def test_rang_3_quatre_numeros_plus_chance(self, tirage_exemple):
        """4 bons numéros + numéro chance = Rang 3."""
        grille = {"numeros": [5, 12, 23, 34, 99], "numero_chance": 7}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 3
        assert resultat["bons_numeros"] == 4
        assert resultat["chance_ok"] is True
        assert resultat["gain"] == Decimal("1000")

    def test_rang_4_quatre_numeros_sans_chance(self, tirage_exemple):
        """4 bons numéros sans numéro chance = Rang 4."""
        grille = {"numeros": [5, 12, 23, 34, 99], "numero_chance": 1}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 4
        assert resultat["bons_numeros"] == 4
        assert resultat["gain"] == Decimal("500")

    def test_rang_5_trois_numeros_plus_chance(self, tirage_exemple):
        """3 bons numéros + numéro chance = Rang 5."""
        grille = {"numeros": [5, 12, 23, 98, 99], "numero_chance": 7}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 5
        assert resultat["bons_numeros"] == 3
        assert resultat["chance_ok"] is True
        assert resultat["gain"] == Decimal("50")

    def test_rang_6_trois_numeros_sans_chance(self, tirage_exemple):
        """3 bons numéros sans numéro chance = Rang 6."""
        grille = {"numeros": [5, 12, 23, 98, 99], "numero_chance": 1}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 6
        assert resultat["bons_numeros"] == 3
        assert resultat["gain"] == Decimal("20")

    def test_rang_7_deux_numeros_plus_chance(self, tirage_exemple):
        """2 bons numéros + numéro chance = Rang 7."""
        grille = {"numeros": [5, 12, 97, 98, 99], "numero_chance": 7}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 7
        assert resultat["bons_numeros"] == 2
        assert resultat["gain"] == Decimal("10")

    def test_rang_8_deux_numeros_sans_chance(self, tirage_exemple):
        """2 bons numéros sans numéro chance = Rang 8."""
        grille = {"numeros": [5, 12, 97, 98, 99], "numero_chance": 1}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 8
        assert resultat["bons_numeros"] == 2
        assert resultat["gain"] == Decimal("5")

    def test_rang_9_un_numero_plus_chance(self, tirage_exemple):
        """1 bon numéro + numéro chance = Rang 9 (remboursement)."""
        grille = {"numeros": [5, 96, 97, 98, 99], "numero_chance": 7}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] == 9
        assert resultat["bons_numeros"] == 1
        assert resultat["gain"] == Decimal("2.20")

    def test_perdant_aucun_numero(self, tirage_exemple):
        """Aucun bon numéro = perdant."""
        grille = {"numeros": [1, 2, 3, 4, 6], "numero_chance": 1}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] is None
        assert resultat["gagnant"] is False
        assert resultat["gain"] == Decimal("0.00")

    def test_perdant_un_numero_sans_chance(self, tirage_exemple):
        """1 bon numéro sans chance = perdant."""
        grille = {"numeros": [5, 96, 97, 98, 99], "numero_chance": 1}
        resultat = verifier_grille(grille, tirage_exemple)

        assert resultat["rang"] is None
        assert resultat["gagnant"] is False

    def test_description_incluse(self, tirage_exemple):
        """Le résultat doit inclure une description."""
        grille = {"numeros": [5, 12, 23, 34, 45], "numero_chance": 7}
        resultat = verifier_grille(grille, tirage_exemple)

        assert "description" in resultat
        assert "5 numéros" in resultat["description"]
        assert "chance" in resultat["description"]


class TestCalculerEsperanceMathematique:
    """Tests du calcul d'espérance mathématique."""

    def test_esperance_negative(self):
        """L'espérance doit être négative (jeu défavorable)."""
        resultat = calculer_esperance_mathematique()

        assert resultat["esperance"] < 0

    def test_cout_grille_correct(self):
        """Le coût de grille doit être correct."""
        resultat = calculer_esperance_mathematique()

        assert resultat["cout_grille"] == float(COUT_GRILLE)

    def test_perte_moyenne_positive(self):
        """Le pourcentage de perte doit être positif."""
        resultat = calculer_esperance_mathematique()

        assert resultat["perte_moyenne_pct"] > 0
        assert resultat["perte_moyenne_pct"] < 100

    def test_probabilites_tous_rangs(self):
        """Toutes les probabilités des 9 rangs doivent être présentes."""
        resultat = calculer_esperance_mathematique()

        for rang in range(1, 10):
            assert rang in resultat["probabilites"]

    def test_conclusion_presente(self):
        """Une conclusion doit être incluse."""
        resultat = calculer_esperance_mathematique()

        assert "conclusion" in resultat
        assert len(resultat["conclusion"]) > 10

    def test_gains_esperes_positifs(self):
        """Les gains espérés doivent être positifs."""
        resultat = calculer_esperance_mathematique()

        assert resultat["gains_esperes"] > 0

    def test_reversement_environ_50_pourcent(self):
        """Le Loto reverse environ 50% des mises."""
        resultat = calculer_esperance_mathematique()

        # Le taux de retour typique est entre 45% et 55%
        taux_retour = 100 - resultat["perte_moyenne_pct"]
        assert 40 < taux_retour < 60
