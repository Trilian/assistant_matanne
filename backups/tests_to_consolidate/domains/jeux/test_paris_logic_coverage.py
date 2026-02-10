"""
Tests complets pour paris_logic.py - Couverture ≥80%

Ce module teste toutes les fonctions de logique de paris sportifs:
- Calcul de forme des équipes
- Prédiction de résultats
- Analyse des confrontations directes (H2H)
- Conseils de paris
- Over/Under predictions
- Classe AnalyseurParis
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.domains.jeux.logic.paris_logic import (
    # Constantes
    CHAMPIONNATS,
    AVANTAGE_DOMICILE,
    SEUIL_CONFIANCE_HAUTE,
    SEUIL_CONFIANCE_MOYENNE,
    SEUIL_SERIE_SANS_NUL,
    BONUS_NUL_PAR_MATCH,
    POIDS_FORME,
    # Fonctions
    calculer_forme_equipe,
    calculer_serie_sans_nul,
    calculer_bonus_nul_regression,
    calculer_historique_face_a_face,
    predire_resultat_match,
    generer_conseil_pari,
    generer_conseils_avances,
    predire_over_under,
    calculer_performance_paris,
    analyser_tendances_championnat,
    generer_analyse_complete,
    generer_resume_parieur,
    AnalyseurParis,
)


# ═══════════════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def match_victoire_domicile():
    """Match gagné par l'équipe domicile."""
    return {
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "score_domicile": 2,
        "score_exterieur": 1,
    }


@pytest.fixture
def match_victoire_exterieur():
    """Match gagné par l'équipe extérieur."""
    return {
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "score_domicile": 0,
        "score_exterieur": 2,
    }


@pytest.fixture
def match_nul():
    """Match nul."""
    return {
        "equipe_domicile_id": 1,
        "equipe_exterieur_id": 2,
        "score_domicile": 1,
        "score_exterieur": 1,
    }


@pytest.fixture
def matchs_5_victoires():
    """5 victoires consécutives pour l'équipe 1."""
    return [
        {"equipe_domicile_id": 1, "equipe_exterieur_id": 3, "score_domicile": 2, "score_exterieur": 0},
        {"equipe_domicile_id": 4, "equipe_exterieur_id": 1, "score_domicile": 1, "score_exterieur": 3},
        {"equipe_domicile_id": 1, "equipe_exterieur_id": 5, "score_domicile": 1, "score_exterieur": 0},
        {"equipe_domicile_id": 6, "equipe_exterieur_id": 1, "score_domicile": 0, "score_exterieur": 2},
        {"equipe_domicile_id": 1, "equipe_exterieur_id": 7, "score_domicile": 3, "score_exterieur": 1},
    ]


@pytest.fixture
def matchs_mixtes():
    """Matchs avec résultats variés VNDVN."""
    return [
        {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 2, "score_exterieur": 0},  # V
        {"equipe_domicile_id": 3, "equipe_exterieur_id": 1, "score_domicile": 1, "score_exterieur": 1},  # N
        {"equipe_domicile_id": 1, "equipe_exterieur_id": 4, "score_domicile": 0, "score_exterieur": 2},  # D
        {"equipe_domicile_id": 5, "equipe_exterieur_id": 1, "score_domicile": 1, "score_exterieur": 3},  # V
        {"equipe_domicile_id": 1, "equipe_exterieur_id": 6, "score_domicile": 0, "score_exterieur": 0},  # N
    ]


@pytest.fixture
def forme_bonne():
    """Forme d'une équipe en bonne forme."""
    return {
        "score": 80.0,
        "forme_str": "VVVNV",
        "tendance": "hausse",
        "victoires": 4,
        "nuls": 1,
        "defaites": 0,
        "buts_marques": 10,
        "buts_encaisses": 3,
        "serie_en_cours": "3V",
        "nb_matchs": 5,
        "matchs_sans_nul": 3
    }


@pytest.fixture
def forme_mauvaise():
    """Forme d'une équipe en mauvaise forme."""
    return {
        "score": 20.0,
        "forme_str": "DDDND",
        "tendance": "baisse",
        "victoires": 0,
        "nuls": 1,
        "defaites": 4,
        "buts_marques": 2,
        "buts_encaisses": 12,
        "serie_en_cours": "3D",
        "nb_matchs": 5,
        "matchs_sans_nul": 3
    }


@pytest.fixture
def h2h_avantage_domicile():
    """Historique H2H avec avantage pour le domicile."""
    return {
        "nb_matchs": 5,
        "victoires_dom": 3,
        "victoires_ext": 1,
        "nuls": 1,
        "avantage": "domicile",
        "buts_dom_total": 10,
        "buts_ext_total": 5,
    }


@pytest.fixture
def cotes_standard():
    """Cotes de bookmaker standard."""
    return {
        "domicile": 1.85,
        "nul": 3.50,
        "exterieur": 4.20,
    }


# ═══════════════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes du module."""
    
    def test_championnats_non_vide(self):
        """Vérifie que la liste des championnats n'est pas vide."""
        assert len(CHAMPIONNATS) >= 5
        assert "Ligue 1" in CHAMPIONNATS
        assert "Premier League" in CHAMPIONNATS
    
    def test_avantage_domicile_range(self):
        """L'avantage domicile doit être entre 0 et 0.20."""
        assert 0 < AVANTAGE_DOMICILE < 0.20
    
    def test_seuils_confiance_ordonnees(self):
        """Les seuils de confiance doivent être ordonnés."""
        assert SEUIL_CONFIANCE_HAUTE > SEUIL_CONFIANCE_MOYENNE
        assert SEUIL_CONFIANCE_MOYENNE > 0
    
    def test_poids_forme_decroissants(self):
        """Les poids de forme doivent être décroissants."""
        assert len(POIDS_FORME) == 5
        for i in range(len(POIDS_FORME) - 1):
            assert POIDS_FORME[i] > POIDS_FORME[i + 1]


# ═══════════════════════════════════════════════════════════════════
# TESTS calculer_forme_equipe
# ═══════════════════════════════════════════════════════════════════


class TestCalculerFormeEquipe:
    """Tests pour calculer_forme_equipe."""
    
    def test_matchs_vides(self):
        """Sans matchs, retourne forme neutre."""
        result = calculer_forme_equipe([], equipe_id=1)
        
        assert result["score"] == 50.0
        assert result["forme_str"] == "?????"
        assert result["tendance"] == "inconnue"
        assert result["victoires"] == 0
        assert result["nuls"] == 0
        assert result["defaites"] == 0
    
    def test_victoire_domicile(self, match_victoire_domicile):
        """Test d'une victoire à domicile."""
        result = calculer_forme_equipe([match_victoire_domicile], equipe_id=1)
        
        assert result["victoires"] == 1
        assert result["defaites"] == 0
        assert "V" in result["forme_str"]
        assert result["buts_marques"] == 2
        assert result["buts_encaisses"] == 1
    
    def test_victoire_exterieur(self, match_victoire_exterieur):
        """Test d'une victoire à l'extérieur."""
        result = calculer_forme_equipe([match_victoire_exterieur], equipe_id=2)
        
        assert result["victoires"] == 1
        assert result["defaites"] == 0
        assert "V" in result["forme_str"]
    
    def test_defaite(self, match_victoire_domicile):
        """Test d'une défaite (équipe 2 perd)."""
        result = calculer_forme_equipe([match_victoire_domicile], equipe_id=2)
        
        assert result["defaites"] == 1
        assert result["victoires"] == 0
        assert "D" in result["forme_str"]
    
    def test_match_nul(self, match_nul):
        """Test d'un match nul."""
        result = calculer_forme_equipe([match_nul], equipe_id=1)
        
        assert result["nuls"] == 1
        assert "N" in result["forme_str"]
    
    def test_5_victoires_score_eleve(self, matchs_5_victoires):
        """5 victoires = score très élevé."""
        result = calculer_forme_equipe(matchs_5_victoires, equipe_id=1)
        
        assert result["score"] > 90.0
        assert result["victoires"] == 5
        assert result["tendance"] == "hausse"
        assert result["serie_en_cours"] is not None
        assert "V" in result["serie_en_cours"]
    
    def test_matchs_mixtes(self, matchs_mixtes):
        """Matchs variés = score moyen."""
        result = calculer_forme_equipe(matchs_mixtes, equipe_id=1)
        
        assert 30.0 < result["score"] < 70.0
        assert result["victoires"] + result["nuls"] + result["defaites"] == 5
    
    def test_tendance_hausse(self):
        """Tendance hausse avec 3 victoires récentes."""
        matchs = [
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 0, "score_exterieur": 1},  # D (ancien)
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 3, "score_domicile": 2, "score_exterieur": 0},  # V
            {"equipe_domicile_id": 4, "equipe_exterieur_id": 1, "score_domicile": 0, "score_exterieur": 1},  # V
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 5, "score_domicile": 3, "score_exterieur": 1},  # V
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["tendance"] == "hausse"
    
    def test_tendance_baisse(self):
        """Tendance baisse avec 3 défaites récentes."""
        matchs = [
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 2, "score_exterieur": 0},  # V (ancien)
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 3, "score_domicile": 0, "score_exterieur": 2},  # D
            {"equipe_domicile_id": 4, "equipe_exterieur_id": 1, "score_domicile": 3, "score_exterieur": 0},  # D
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 5, "score_domicile": 1, "score_exterieur": 3},  # D
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["tendance"] == "baisse"
    
    def test_serie_en_cours_detection(self):
        """Détection d'une série en cours."""
        matchs = [
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 3, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 4, "score_domicile": 2, "score_exterieur": 0},
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["serie_en_cours"] == "3V"
    
    def test_plus_de_5_matchs_prend_5_derniers(self):
        """Ne doit prendre que les 5 derniers matchs."""
        matchs = [
            {"equipe_domicile_id": 1, "equipe_exterieur_id": i, "score_domicile": 2, "score_exterieur": 0}
            for i in range(2, 10)  # 8 matchs
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["nb_matchs"] == 5


# ═══════════════════════════════════════════════════════════════════
# TESTS calculer_serie_sans_nul
# ═══════════════════════════════════════════════════════════════════


class TestCalculerSerieSansNul:
    """Tests pour calculer_serie_sans_nul."""
    
    def test_liste_vide(self):
        """Liste vide = 0 matchs sans nul."""
        assert calculer_serie_sans_nul([]) == 0
    
    def test_commence_par_nul(self):
        """Si le premier résultat est un nul, série = 0."""
        assert calculer_serie_sans_nul(["N", "V", "D"]) == 0
    
    def test_tous_sans_nul(self):
        """Tous les résultats sans nul."""
        assert calculer_serie_sans_nul(["V", "D", "V", "V", "D"]) == 5
    
    def test_nul_au_milieu(self):
        """Compte jusqu'au premier nul."""
        assert calculer_serie_sans_nul(["V", "V", "D", "N", "V"]) == 3
    
    def test_un_seul_match_victoire(self):
        """Un seul match victoire."""
        assert calculer_serie_sans_nul(["V"]) == 1


# ═══════════════════════════════════════════════════════════════════
# TESTS calculer_bonus_nul_regression
# ═══════════════════════════════════════════════════════════════════


class TestCalculerBonusNulRegression:
    """Tests pour calculer_bonus_nul_regression."""
    
    def test_pas_de_bonus_sous_seuil(self):
        """Aucun bonus si sous le seuil."""
        assert calculer_bonus_nul_regression(3, 3) == 0.0
    
    def test_bonus_une_equipe_au_seuil(self):
        """Bonus si une équipe au seuil."""
        bonus = calculer_bonus_nul_regression(5, 0)
        assert bonus > 0.0
    
    def test_bonus_deux_equipes_au_seuil(self):
        """Bonus combo si les deux équipes au seuil."""
        bonus = calculer_bonus_nul_regression(5, 5)
        assert bonus > calculer_bonus_nul_regression(5, 0) * 2  # Bonus combo
    
    def test_cap_maximum(self):
        """Le bonus est plafonné à 25%."""
        bonus = calculer_bonus_nul_regression(20, 20)
        assert bonus <= 0.25
    
    def test_bonus_progressif(self):
        """Le bonus augmente avec la série."""
        bonus_5 = calculer_bonus_nul_regression(5, 0)
        bonus_6 = calculer_bonus_nul_regression(6, 0)
        bonus_7 = calculer_bonus_nul_regression(7, 0)
        
        assert bonus_5 < bonus_6 < bonus_7


# ═══════════════════════════════════════════════════════════════════
# TESTS calculer_historique_face_a_face
# ═══════════════════════════════════════════════════════════════════


class TestCalculerHistoriqueFaceAFace:
    """Tests pour calculer_historique_face_a_face."""
    
    def test_historique_vide(self):
        """Sans historique, retourne stats neutres."""
        result = calculer_historique_face_a_face([], 1, 2)
        
        assert result["nb_matchs"] == 0
        assert result["avantage"] is None
    
    def test_avantage_domicile(self):
        """Détecte avantage pour le domicile."""
        matchs = [
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 2, "equipe_exterieur_id": 1, "score_domicile": 0, "score_exterieur": 1},
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 3, "score_exterieur": 1},
        ]
        result = calculer_historique_face_a_face(matchs, 1, 2)
        
        assert result["nb_matchs"] == 3
        assert result["victoires_dom"] >= 2
    
    def test_avantage_exterieur(self):
        """Détecte avantage pour l'extérieur."""
        matchs = [
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 0, "score_exterieur": 2},
            {"equipe_domicile_id": 2, "equipe_exterieur_id": 1, "score_domicile": 3, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "equipe_exterieur_id": 2, "score_domicile": 1, "score_exterieur": 3},
        ]
        result = calculer_historique_face_a_face(matchs, 1, 2)
        
        assert result["victoires_ext"] >= 2


# ═══════════════════════════════════════════════════════════════════
# TESTS predire_resultat_match
# ═══════════════════════════════════════════════════════════════════


class TestPredireResultatMatch:
    """Tests pour predire_resultat_match."""
    
    def test_prediction_forme_bonne_vs_mauvaise(self, forme_bonne, forme_mauvaise, h2h_avantage_domicile):
        """Équipe en forme vs équipe en difficulté."""
        result = predire_resultat_match(forme_bonne, forme_mauvaise, h2h_avantage_domicile)
        
        assert result["prediction"] == "1"  # Victoire domicile
        assert result["confiance"] > 60
    
    def test_prediction_forme_mauvaise_vs_bonne(self, forme_bonne, forme_mauvaise, h2h_avantage_domicile):
        """Équipe en difficulté à domicile vs équipe en forme."""
        result = predire_resultat_match(forme_mauvaise, forme_bonne, h2h_avantage_domicile)
        
        # L'extérieur devrait être favori malgré le désavantage domicile
        assert result["prediction"] in ["2", "N"]
    
    def test_prediction_avec_cotes(self, forme_bonne, forme_mauvaise, h2h_avantage_domicile, cotes_standard):
        """Les cotes influencent la prédiction."""
        result = predire_resultat_match(
            forme_bonne, forme_mauvaise, h2h_avantage_domicile, 
            cotes=cotes_standard
        )
        
        # Returns probabilites dict with domicile, nul, exterieur keys
        assert "probabilites" in result
        assert "domicile" in result["probabilites"]
        assert "nul" in result["probabilites"]
        assert "exterieur" in result["probabilites"]
    
    def test_probas_somme_environ_100(self, forme_bonne, forme_mauvaise, h2h_avantage_domicile):
        """La somme des probabilités doit être proche de 100%."""
        result = predire_resultat_match(forme_bonne, forme_mauvaise, h2h_avantage_domicile)
        
        # Probabilites are returned as percentages (0-100)
        probas = result["probabilites"]
        total = probas["domicile"] + probas["nul"] + probas["exterieur"]
        assert 95 <= total <= 105  # Tolérance (percentages, ~100%)
    
    def test_bonus_nul_avec_series_sans_nul(self):
        """Test du bonus nul quand les équipes n'ont pas fait de nul."""
        forme_dom = {"score": 50, "matchs_sans_nul": 6, "serie_en_cours": None}
        forme_ext = {"score": 50, "matchs_sans_nul": 6, "serie_en_cours": None}
        h2h = {"nb_matchs": 0}
        
        result = predire_resultat_match(forme_dom, forme_ext, h2h)
        
        # La proba nul devrait être plus élevée (returned as percentage)
        assert result["probabilites"]["nul"] > 25  # > 25%
    
    def test_regression_serie_defaites(self):
        """Bonus pour équipe avec série de défaites."""
        forme_dom = {"score": 30, "matchs_sans_nul": 0, "serie_en_cours": "4D"}
        forme_ext = {"score": 50, "matchs_sans_nul": 0, "serie_en_cours": None}
        h2h = {"nb_matchs": 0}
        
        result = predire_resultat_match(forme_dom, forme_ext, h2h)
        
        # Le domicile devrait avoir un petit bonus (returned as percentage)
        assert result["probabilites"]["domicile"] > 20  # > 20%


# ═══════════════════════════════════════════════════════════════════
# TESTS generer_conseil_pari
# ═══════════════════════════════════════════════════════════════════


class TestGenererConseilPari:
    """Tests pour generer_conseil_pari."""
    
    def test_confiance_haute_conseille_parier(self):
        """Confiance haute = conseil de parier."""
        conseil = generer_conseil_pari("1", confiance=70)
        
        assert "PARIER" in conseil
        assert "bankroll" in conseil.lower()
    
    def test_confiance_moyenne_prudent(self):
        """Confiance moyenne = conseil prudent."""
        conseil = generer_conseil_pari("1", confiance=55)
        
        assert "PRUDENT" in conseil
    
    def test_confiance_faible_eviter(self):
        """Confiance faible = éviter."""
        conseil = generer_conseil_pari("1", confiance=40)
        
        assert "ÉVITER" in conseil
    
    def test_value_bet_detection(self, cotes_standard):
        """Détection des value bets."""
        # Cote élevée + confiance = value bet
        cotes_value = {"domicile": 3.5, "nul": 3.5, "exterieur": 2.0}
        conseil = generer_conseil_pari("1", confiance=70, cotes=cotes_value)
        
        assert "VALUE" in conseil
    
    def test_mention_proba_nul_elevee(self):
        """Mention si proba nul élevée."""
        conseil = generer_conseil_pari("1", confiance=60, proba_nul=0.35)
        
        assert "nul" in conseil.lower()


# ═══════════════════════════════════════════════════════════════════
# TESTS generer_conseils_avances
# ═══════════════════════════════════════════════════════════════════


class TestGenererConseilsAvances:
    """Tests pour generer_conseils_avances."""
    
    def test_conseil_serie_sans_nul(self):
        """Conseil quand série sans nul."""
        forme_dom = {"matchs_sans_nul": 7, "serie_en_cours": None, "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 3, "serie_en_cours": None, "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        types = [c["type"] for c in conseils]
        assert any("NUL" in t for t in types)
    
    def test_conseil_rebond_serie_defaites(self):
        """Conseil rebond après défaites."""
        forme_dom = {"matchs_sans_nul": 0, "serie_en_cours": "5D", "buts_marques": 2, "buts_encaisses": 10, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 0, "serie_en_cours": None, "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        types = [c["type"] for c in conseils]
        assert any("REBOND" in t for t in types)
    
    def test_conseil_over_teams_offensives(self):
        """Conseil Over avec équipes offensives."""
        forme_dom = {"matchs_sans_nul": 0, "serie_en_cours": None, "buts_marques": 12, "buts_encaisses": 8, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 0, "serie_en_cours": None, "buts_marques": 10, "buts_encaisses": 10, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        types = [c["type"] for c in conseils]
        assert any("OVER" in t for t in types)
    
    def test_conseil_under_teams_defensives(self):
        """Conseil Under avec équipes défensives."""
        forme_dom = {"matchs_sans_nul": 0, "serie_en_cours": None, "buts_marques": 3, "buts_encaisses": 2, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 0, "serie_en_cours": None, "buts_marques": 2, "buts_encaisses": 3, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        types = [c["type"] for c in conseils]
        assert any("UNDER" in t for t in types)
    
    def test_conseil_value_bet_nul(self, cotes_standard):
        """Conseil value bet nul avec cote élevée."""
        cotes_value = {"domicile": 2.0, "nul": 4.2, "exterieur": 3.0}
        forme_dom = {"matchs_sans_nul": 5, "serie_en_cours": None, "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 0, "serie_en_cours": None, "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext, cotes=cotes_value)
        
        types = [c["type"] for c in conseils]
        assert any("VALUE" in t for t in types)


# ═══════════════════════════════════════════════════════════════════
# TESTS predire_over_under
# ═══════════════════════════════════════════════════════════════════


class TestPredireOverUnder:
    """Tests pour predire_over_under."""
    
    def test_equipes_offensives_over(self):
        """Équipes offensives = over probable."""
        forme_dom = {"buts_marques": 12, "buts_encaisses": 8, "nb_matchs": 5}
        forme_ext = {"buts_marques": 10, "buts_encaisses": 10, "nb_matchs": 5}
        
        result = predire_over_under(forme_dom, forme_ext, seuil=2.5)
        
        assert result["prediction"] == "over"
        assert result["probabilite_over"] > 50  # Returned as percentage
    
    def test_equipes_defensives_under(self):
        """Équipes défensives = under probable."""
        forme_dom = {"buts_marques": 3, "buts_encaisses": 2, "nb_matchs": 5}
        forme_ext = {"buts_marques": 2, "buts_encaisses": 2, "nb_matchs": 5}
        
        result = predire_over_under(forme_dom, forme_ext, seuil=2.5)
        
        assert result["prediction"] == "under"
        assert result["probabilite_over"] < 50  # Returned as percentage
    
    def test_seuil_different(self):
        """Test avec seuil différent (1.5)."""
        forme_dom = {"buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        
        result = predire_over_under(forme_dom, forme_ext, seuil=1.5)
        
        assert result["seuil"] == 1.5
        assert result["probabilite_over"] > 50  # 2 buts/match en moyenne, returned as percentage
    
    def test_buts_attendus_calcules(self):
        """Vérifie le calcul des buts attendus."""
        forme_dom = {"buts_marques": 10, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"buts_marques": 5, "buts_encaisses": 10, "nb_matchs": 5}
        
        result = predire_over_under(forme_dom, forme_ext, seuil=2.5)
        
        assert "buts_attendus" in result
        assert result["buts_attendus"] > 0


# ═══════════════════════════════════════════════════════════════════
# TESTS calculer_performance_paris
# ═══════════════════════════════════════════════════════════════════


class TestCalculerPerformanceParis:
    """Tests pour calculer_performance_paris."""
    
    def test_paris_vides(self):
        """Sans paris, retourne stats à zéro."""
        result = calculer_performance_paris([])
        
        assert result["nb_paris"] == 0
        assert result["roi"] == 0.0
    
    def test_tous_paris_gagnes(self):
        """Tous les paris gagnés = ROI positif."""
        paris = [
            {"mise": 10, "cote": 2.0, "statut": "gagne", "gain": 20},
            {"mise": 10, "cote": 1.8, "statut": "gagne", "gain": 18},
        ]
        result = calculer_performance_paris(paris)
        
        assert result["nb_paris"] == 2
        assert result["gagnes"] == 2
        assert result["roi"] > 0
    
    def test_tous_paris_perdus(self):
        """Tous les paris perdus = ROI négatif."""
        paris = [
            {"mise": 10, "cote": 2.0, "statut": "perdu"},
            {"mise": 10, "cote": 1.8, "statut": "perdu"},
        ]
        result = calculer_performance_paris(paris)
        
        assert result["nb_paris"] == 2
        assert result["gagnes"] == 0
        assert result["roi"] < 0
    
    def test_calcul_profit_net(self):
        """Vérifie le calcul du profit net."""
        paris = [
            {"mise": 10, "cote": 2.0, "statut": "gagne", "gain": 20},  # +10 profit
            {"mise": 10, "cote": 2.0, "statut": "perdu"},  # -10 loss
        ]
        result = calculer_performance_paris(paris)
        
        # profit = gains_totaux - mises_totales = 20 - 20 = 0
        assert result["profit"] == 0


# ═══════════════════════════════════════════════════════════════════
# TESTS analyser_tendances_championnat
# ═══════════════════════════════════════════════════════════════════


class TestAnalyserTendancesChampionnat:
    """Tests pour analyser_tendances_championnat."""
    
    def test_matchs_vides(self):
        """Sans matchs, retourne stats vides."""
        result = analyser_tendances_championnat([], "Ligue 1")
        
        assert result["championnat"] == "Ligue 1"
        assert result["nb_matchs"] == 0
    
    def test_tendances_calcul(self):
        """Vérifie le calcul des tendances."""
        # Matches need 'joue': True to be counted
        matchs = [
            {"score_domicile": 2, "score_exterieur": 1, "joue": True},  # V dom
            {"score_domicile": 1, "score_exterieur": 1, "joue": True},  # Nul
            {"score_domicile": 0, "score_exterieur": 2, "joue": True},  # V ext
            {"score_domicile": 3, "score_exterieur": 0, "joue": True},  # V dom
        ]
        result = analyser_tendances_championnat(matchs, "Ligue 1")
        
        assert result["nb_matchs"] == 4
        # Returns percentages, not raw counts
        assert result["victoires_domicile_pct"] == 50.0  # 2/4 = 50%
        assert result["victoires_exterieur_pct"] == 25.0  # 1/4 = 25%
        assert result["nuls_pct"] == 25.0  # 1/4 = 25%
    
    def test_moyenne_buts(self):
        """Vérifie le calcul de la moyenne de buts."""
        # Matches need 'joue': True to be counted
        matchs = [
            {"score_domicile": 2, "score_exterieur": 1, "joue": True},  # 3 buts
            {"score_domicile": 0, "score_exterieur": 0, "joue": True},  # 0 but
            {"score_domicile": 1, "score_exterieur": 2, "joue": True},  # 3 buts
        ]
        result = analyser_tendances_championnat(matchs, "Premier League")
        
        assert result["moyenne_buts"] == 2.0


# ═══════════════════════════════════════════════════════════════════
# TESTS AnalyseurParis (classe)
# ═══════════════════════════════════════════════════════════════════


class TestAnalyseurParis:
    """Tests pour la classe AnalyseurParis."""
    
    def test_initialisation(self):
        """Test de l'initialisation."""
        analyseur = AnalyseurParis()
        
        assert analyseur is not None
    
    def test_analyser_serie_complete(self):
        """Test analyse de série."""
        analyseur = AnalyseurParis()
        
        result = analyseur.analyser_serie_complete("VVVND")
        
        assert "serie" in result
        assert "tendance" in result
        assert "proba_rupture" in result
        assert result["type_serie"] == "V"
    
    def test_calculer_value_bet(self):
        """Test calcul value bet."""
        analyseur = AnalyseurParis()
        
        # Value bet: proba 50% avec cote 2.5 = EV = (0.5 * 2.5) - 1 = 0.25 (+25%)
        result = analyseur.calculer_value_bet(0.5, 2.5)
        
        assert result["is_value"] == True
        assert result["ev"] > 0
        assert result["qualite"] in ["excellente", "bonne", "correcte"]
    
    def test_analyser_tendance_buts(self, forme_bonne):
        """Test analyse tendance buts."""
        analyseur = AnalyseurParis()
        
        result = analyseur.analyser_tendance_buts(forme_bonne)
        
        assert "moy_marques" in result
        assert "moy_encaisses" in result
        assert "profil" in result


# ═══════════════════════════════════════════════════════════════════
# TESTS generer_analyse_complete
# ═══════════════════════════════════════════════════════════════════


class TestGenererAnalyseComplete:
    """Tests pour generer_analyse_complete."""
    
    def test_analyse_complete_structure(self, forme_bonne, forme_mauvaise, h2h_avantage_domicile):
        """Vérifie la structure de l'analyse complète."""
        result = generer_analyse_complete(
            forme_dom=forme_bonne,
            forme_ext=forme_mauvaise,
            h2h=h2h_avantage_domicile
        )
        
        assert "score_global" in result
        assert "recommandation" in result
        assert "conseils" in result
        assert "stats" in result
    
    def test_analyse_complete_avec_cotes(self, forme_bonne, forme_mauvaise, h2h_avantage_domicile, cotes_standard):
        """Analyse complète avec cotes."""
        result = generer_analyse_complete(
            forme_dom=forme_bonne,
            forme_ext=forme_mauvaise,
            h2h=h2h_avantage_domicile,
            cotes=cotes_standard
        )
        
        assert "value_bets" in result
        assert "recommandation" in result


# ═══════════════════════════════════════════════════════════════════
# TESTS generer_resume_parieur
# ═══════════════════════════════════════════════════════════════════


class TestGenererResumeParieur:
    """Tests pour generer_resume_parieur."""
    
    def test_resume_basique(self):
        """Génère un résumé basique."""
        # generer_resume_parieur expects the output format from generer_analyse_complete
        analyse = {
            "recommandation": {
                "pari": "1",
                "confiance": 65,
                "mise": "2-3%",
                "raison": "Domicile grand favori"
            },
            "conseils": [],
            "alertes": []
        }
        
        resume = generer_resume_parieur(analyse)
        
        assert isinstance(resume, str)
        assert "65%" in resume or "65" in resume
    
    def test_resume_affiche_prediction(self):
        """Le résumé affiche la prédiction."""
        analyse = {
            "recommandation": {
                "pari": "N",
                "confiance": 50,
                "mise": "1-2%",
                "raison": "Match équilibré"
            },
            "conseils": [],
            "alertes": []
        }
        
        resume = generer_resume_parieur(analyse)
        
        assert "N" in resume or "POSSIBLE" in resume
