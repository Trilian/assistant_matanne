"""
Tests du module paris - Calcul de forme et prédictions.

Tests de couverture pour:
- calculer_forme_equipe
- calculer_serie_sans_nul
- calculer_bonus_nul_regression
- calculer_historique_face_a_face
"""

import pytest
from src.domains.jeux.logic.paris.forme import (
    calculer_forme_equipe,
    calculer_serie_sans_nul,
    calculer_bonus_nul_regression,
    calculer_historique_face_a_face,
)


class TestCalculerFormeEquipe:
    """Tests pour calculer_forme_equipe."""
    
    def test_forme_vide_retourne_par_defaut(self):
        """Sans matchs, retourne des valeurs par défaut."""
        result = calculer_forme_equipe([], equipe_id=1)
        
        assert result["score"] == 50.0
        assert result["forme_str"] == "?????"
        assert result["tendance"] == "inconnue"
        assert result["victoires"] == 0
        assert result["nuls"] == 0
        assert result["defaites"] == 0
    
    def test_forme_victoire_domicile(self):
        """Teste la détection de victoire à domicile."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0}
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["victoires"] == 1
        assert result["defaites"] == 0
        assert result["score"] == 100.0
        assert "V" in result["forme_str"]
    
    def test_forme_defaite_exterieur(self):
        """Teste la détection de défaite à l'extérieur."""
        matchs = [
            {"equipe_domicile_id": 2, "score_domicile": 3, "score_exterieur": 1}
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)  # Equipe 1 est à l'extérieur
        
        assert result["victoires"] == 0
        assert result["defaites"] == 1
        assert "D" in result["forme_str"]
    
    def test_forme_nul(self):
        """Teste la détection de match nul."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 1}
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["nuls"] == 1
        assert result["score"] == 40.0
        assert "N" in result["forme_str"]
    
    def test_forme_5_matchs_poids_differents(self):
        """Les matchs récents ont plus de poids."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 0, "score_exterieur": 1},  # D ancien
            {"equipe_domicile_id": 1, "score_domicile": 0, "score_exterieur": 1},  # D
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},  # V
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},  # V
            {"equipe_domicile_id": 1, "score_domicile": 3, "score_exterieur": 0},  # V récent
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["victoires"] == 3
        assert result["defaites"] == 2
        # Score > 50 car les victoires récentes ont plus de poids
        assert result["score"] > 50
        assert result["tendance"] == "hausse"  # 2 victoires récentes
    
    def test_tendance_baisse(self):
        """Détection de tendance à la baisse."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 3, "score_exterieur": 0},  # V ancien
            {"equipe_domicile_id": 1, "score_domicile": 0, "score_exterieur": 1},  # D
            {"equipe_domicile_id": 1, "score_domicile": 0, "score_exterieur": 2},  # D récent
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["tendance"] == "baisse"
    
    def test_serie_en_cours_victoires(self):
        """Détection de série de victoires."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "score_domicile": 3, "score_exterieur": 1},
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["serie_en_cours"] == "3V"
    
    def test_buts_marques_encaisses(self):
        """Comptage des buts marqués et encaissés."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 1},
            {"equipe_domicile_id": 2, "score_domicile": 1, "score_exterieur": 3},  # Ext
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["buts_marques"] == 2 + 3
        assert result["buts_encaisses"] == 1 + 1
    
    def test_matchs_sans_nul(self):
        """Compte les matchs consécutifs sans nul."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},  # V
            {"equipe_domicile_id": 1, "score_domicile": 0, "score_exterieur": 1},  # D
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 0},  # V
        ]
        result = calculer_forme_equipe(matchs, equipe_id=1)
        
        assert result["matchs_sans_nul"] == 3


class TestCalculerSerieSansNul:
    """Tests pour calculer_serie_sans_nul."""
    
    def test_aucun_nul(self):
        """Tous les matchs V ou D."""
        forme = ["V", "D", "V", "V", "D"]
        assert calculer_serie_sans_nul(forme) == 5
    
    def test_nul_au_debut(self):
        """Nul immédiat."""
        forme = ["N", "V", "D"]
        assert calculer_serie_sans_nul(forme) == 0
    
    def test_nul_au_milieu(self):
        """Nul après quelques matchs."""
        forme = ["V", "V", "N", "D"]
        assert calculer_serie_sans_nul(forme) == 2
    
    def test_forme_vide(self):
        """Liste vide."""
        assert calculer_serie_sans_nul([]) == 0


class TestCalculerBonusNulRegression:
    """Tests pour calculer_bonus_nul_regression."""
    
    def test_pas_de_bonus_sous_seuil(self):
        """Pas de bonus si moins de 5 matchs sans nul."""
        bonus = calculer_bonus_nul_regression(3, 4)
        assert bonus == 0.0
    
    def test_bonus_equipe_domicile(self):
        """Bonus si équipe domicile dépasse le seuil."""
        bonus = calculer_bonus_nul_regression(6, 2)
        assert bonus > 0
        assert bonus <= 0.25
    
    def test_bonus_equipe_exterieur(self):
        """Bonus si équipe extérieur dépasse le seuil."""
        bonus = calculer_bonus_nul_regression(2, 7)
        assert bonus > 0
    
    def test_bonus_cumule(self):
        """Bonus cumulé si les deux équipes dépassent."""
        bonus = calculer_bonus_nul_regression(7, 8)
        # Devrait être plus élevé car les deux + bonus combo
        assert bonus >= 0.15
    
    def test_bonus_plafonne(self):
        """Bonus ne dépasse jamais 25%."""
        bonus = calculer_bonus_nul_regression(20, 20)
        assert bonus == 0.25


class TestCalculerHistoriqueFaceAFace:
    """Tests pour calculer_historique_face_a_face."""
    
    def test_h2h_vide(self):
        """Sans historique, valeurs par défaut."""
        result = calculer_historique_face_a_face([], equipe_dom_id=1, equipe_ext_id=2)
        
        assert result["nb_matchs"] == 0
        assert result["avantage"] is None
    
    def test_h2h_avantage_domicile(self):
        """L'équipe domicile domine historiquement."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "score_domicile": 3, "score_exterieur": 1},
        ]
        result = calculer_historique_face_a_face(matchs, equipe_dom_id=1, equipe_ext_id=2)
        
        assert result["victoires_dom"] == 3
        assert result["victoires_ext"] == 0
        assert result["avantage"] == "domicile"
    
    def test_h2h_equilibre(self):
        """Match équilibré historiquement."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 2, "score_domicile": 2, "score_exterieur": 0},  # Ext gagne
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 1},  # Nul
        ]
        result = calculer_historique_face_a_face(matchs, equipe_dom_id=1, equipe_ext_id=2)
        
        assert result["avantage"] == "equilibre"
    
    def test_h2h_buts_cumules(self):
        """Cumul correct des buts."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 3, "score_exterieur": 1},
            {"equipe_domicile_id": 2, "score_domicile": 2, "score_exterieur": 2},
        ]
        result = calculer_historique_face_a_face(matchs, equipe_dom_id=1, equipe_ext_id=2)
        
        # Match 1: dom=3, ext=1
        # Match 2: inversé car dom=2 est l'équipe ext → dom(1)=2, ext(2)=2
        assert result["buts_dom"] == 3 + 2
        assert result["buts_ext"] == 1 + 2
