"""
Tests pour loto_logic.py - Fonctions pures d'analyse du Loto
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, Any, List

from src.domains.jeux.logic.loto_logic import (
    calculer_frequences_numeros,
    calculer_ecart,
    identifier_numeros_chauds_froids,
    NUMERO_MIN,
    NUMERO_MAX,
    CHANCE_MIN,
    CHANCE_MAX,
    NB_NUMEROS,
    GAINS_PAR_RANG,
    COUT_GRILLE,
    NUMEROS_POPULAIRES,
    PROBA_JACKPOT,
)


# ═══════════════════════════════════════════════════════════
# Tests Constantes
# ═══════════════════════════════════════════════════════════


class TestConstantesLoto:
    """Tests des constantes du Loto."""

    def test_plage_numeros(self):
        """Vérifie la plage des numéros principaux."""
        assert NUMERO_MIN == 1
        assert NUMERO_MAX == 49
        assert NB_NUMEROS == 5

    def test_plage_chance(self):
        """Vérifie la plage du numéro chance."""
        assert CHANCE_MIN == 1
        assert CHANCE_MAX == 10

    def test_cout_grille(self):
        """Vérifie le coût d'une grille."""
        assert COUT_GRILLE == Decimal("2.20")

    def test_numeros_populaires(self):
        """Vérifie les numéros populaires (dates)."""
        assert 1 in NUMEROS_POPULAIRES
        assert 31 in NUMEROS_POPULAIRES
        assert 32 not in NUMEROS_POPULAIRES

    def test_proba_jackpot(self):
        """La probabilité du jackpot est très faible."""
        assert PROBA_JACKPOT < 0.0000001

    def test_gains_par_rang(self):
        """Vérifie la structure des gains."""
        assert 1 in GAINS_PAR_RANG  # Jackpot
        assert GAINS_PAR_RANG[1] is None  # Variable
        # Les gains au rang 2 sont supérieurs au rang 3
        gain_rang2 = GAINS_PAR_RANG.get(2)
        gain_rang3 = GAINS_PAR_RANG.get(3)
        if gain_rang2 is not None and gain_rang3 is not None:
            assert gain_rang2 > gain_rang3  # 5 bons > 4+chance


# ═══════════════════════════════════════════════════════════
# Tests Calcul Fréquences
# ═══════════════════════════════════════════════════════════


class TestCalculerFrequencesNumeros:
    """Tests pour calculer_frequences_numeros."""

    def test_liste_vide(self):
        """Gère une liste vide."""
        result = calculer_frequences_numeros([])
        assert result["nb_tirages"] == 0
        assert result["frequences"] == {}
        assert result["frequences_chance"] == {}

    def test_tirage_unique(self):
        """Compte un tirage unique."""
        tirages = [{
            "date_tirage": date.today(),
            "numero_1": 1,
            "numero_2": 10,
            "numero_3": 20,
            "numero_4": 30,
            "numero_5": 40,
            "numero_chance": 5
        }]
        
        result = calculer_frequences_numeros(tirages)
        
        assert result["nb_tirages"] == 1
        assert result["frequences"][1]["frequence"] == 1
        assert result["frequences"][10]["frequence"] == 1
        assert result["frequences"][2]["frequence"] == 0  # Non sorti
        assert result["frequences_chance"][5]["frequence"] == 1

    def test_plusieurs_tirages(self):
        """Compte plusieurs tirages."""
        tirages = [
            {"numero_1": 1, "numero_2": 2, "numero_3": 3, "numero_4": 4, "numero_5": 5, "numero_chance": 1},
            {"numero_1": 1, "numero_2": 2, "numero_3": 6, "numero_4": 7, "numero_5": 8, "numero_chance": 2},
        ]
        
        result = calculer_frequences_numeros(tirages)
        
        assert result["nb_tirages"] == 2
        assert result["frequences"][1]["frequence"] == 2  # Sorti 2x
        assert result["frequences"][2]["frequence"] == 2  # Sorti 2x
        assert result["frequences"][3]["frequence"] == 1  # Sorti 1x
        assert result["frequences"][6]["frequence"] == 1  # Sorti 1x

    def test_pourcentage_calcule(self):
        """Calcule le pourcentage correctement."""
        tirages = [
            {"numero_1": 1, "numero_2": 2, "numero_3": 3, "numero_4": 4, "numero_5": 5},
            {"numero_1": 1, "numero_2": 6, "numero_3": 7, "numero_4": 8, "numero_5": 9},
        ]
        
        result = calculer_frequences_numeros(tirages)
        
        # 1 est sorti 2x sur 2 tirages = 100%
        assert result["frequences"][1]["pourcentage"] == 100.0
        # 2 est sorti 1x sur 2 tirages = 50%
        assert result["frequences"][2]["pourcentage"] == 50.0


# ═══════════════════════════════════════════════════════════
# Tests Calcul Écart
# ═══════════════════════════════════════════════════════════


class TestCalculerEcart:
    """Tests pour calculer_ecart."""

    def test_numero_recent(self):
        """Écart 0 si sorti au dernier tirage."""
        tirages = [
            {"numero_1": 5, "numero_2": 10, "numero_3": 15, "numero_4": 20, "numero_5": 25},
        ]
        
        ecart = calculer_ecart(tirages, 5)
        assert ecart == 0

    def test_numero_ancien(self):
        """Écart correct pour numéro pas sorti récemment."""
        tirages = [
            {"numero_1": 5, "numero_2": 10, "numero_3": 15, "numero_4": 20, "numero_5": 25},
            {"numero_1": 6, "numero_2": 11, "numero_3": 16, "numero_4": 21, "numero_5": 26},
            {"numero_1": 7, "numero_2": 12, "numero_3": 17, "numero_4": 22, "numero_5": 27},
        ]
        
        # Le numéro 5 n'est sorti qu'au premier tirage (index 0, donc écart = 2)
        ecart = calculer_ecart(tirages, 5)
        assert ecart == 2

    def test_numero_jamais_sorti(self):
        """Écart = nb tirages si jamais sorti."""
        tirages = [
            {"numero_1": 1, "numero_2": 2, "numero_3": 3, "numero_4": 4, "numero_5": 5},
            {"numero_1": 6, "numero_2": 7, "numero_3": 8, "numero_4": 9, "numero_5": 10},
        ]
        
        ecart = calculer_ecart(tirages, 49)  # Jamais sorti
        assert ecart == 2


# ═══════════════════════════════════════════════════════════
# Tests Numéros Chauds/Froids
# ═══════════════════════════════════════════════════════════


class TestIdentifierNumerosChaudsFroids:
    """Tests pour identifier_numeros_chauds_froids."""

    def test_frequences_vides(self):
        """Gère des fréquences vides."""
        result = identifier_numeros_chauds_froids({})
        assert result["chauds"] == []
        assert result["froids"] == []
        assert result["retard"] == []

    def test_tri_par_frequence(self):
        """Trie correctement par fréquence."""
        frequences = {
            1: {"frequence": 10, "ecart": 0},
            2: {"frequence": 5, "ecart": 5},
            3: {"frequence": 15, "ecart": 2},
            4: {"frequence": 1, "ecart": 10},
            5: {"frequence": 8, "ecart": 1},
        }
        
        result = identifier_numeros_chauds_froids(frequences, nb_top=3)
        
        # Chauds: plus fréquents (3, 1, 5)
        assert result["chauds"][0] == 3
        assert result["chauds"][1] == 1
        
        # Froids: moins fréquents (4, 2, ...)
        assert 4 in result["froids"]

    def test_tri_par_ecart(self):
        """Trie correctement par écart (retard)."""
        frequences = {
            1: {"frequence": 10, "ecart": 5},
            2: {"frequence": 5, "ecart": 15},
            3: {"frequence": 15, "ecart": 1},
        }
        
        result = identifier_numeros_chauds_froids(frequences, nb_top=2)
        
        # Retard: plus grand écart en premier
        assert result["retard"][0] == 2  # Écart 15
        assert result["retard"][1] == 1  # Écart 5

    def test_nb_top_limite(self):
        """Limite le nombre de résultats."""
        frequences = {i: {"frequence": i, "ecart": i} for i in range(1, 20)}
        
        result = identifier_numeros_chauds_froids(frequences, nb_top=5)
        
        assert len(result["chauds"]) == 5
        assert len(result["froids"]) == 5
        assert len(result["retard"]) == 5
