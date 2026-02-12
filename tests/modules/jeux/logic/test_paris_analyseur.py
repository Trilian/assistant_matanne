"""
Tests du module paris - Analyseur intelligent.

Tests de couverture pour:
- AnalyseurParis
- calculer_value_bet
- analyser_tendance_buts
- generer_analyse_complete
- generer_resume_parieur
"""

import pytest
from src.domains.jeux.logic.paris.analyseur import (
    AnalyseurParis,
    generer_analyse_complete,
    generer_resume_parieur,
)


class TestAnalyseurParis:
    """Tests pour la classe AnalyseurParis."""
    
    @pytest.fixture
    def analyseur(self):
        """Crée un analyseur de paris."""
        return AnalyseurParis(cache_enabled=False)
    
    @pytest.fixture
    def matchs_domicile(self):
        """Matchs récents équipe domicile."""
        return [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 1},
            {"equipe_domicile_id": 1, "score_domicile": 3, "score_exterieur": 1},
            {"equipe_domicile_id": 2, "score_domicile": 0, "score_exterieur": 2},  # Ext
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 0},
        ]
    
    @pytest.fixture
    def matchs_exterieur(self):
        """Matchs récents équipe extérieur."""
        return [
            {"equipe_domicile_id": 2, "score_domicile": 1, "score_exterieur": 1},
            {"equipe_domicile_id": 3, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 2, "score_domicile": 0, "score_exterieur": 1},
        ]
    
    @pytest.fixture
    def matchs_h2h(self):
        """Historique face-à-face."""
        return [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 1},
            {"equipe_domicile_id": 2, "score_domicile": 1, "score_exterieur": 1},
        ]
    
    def test_analyser_match_structure(self, analyseur, matchs_domicile, matchs_exterieur, matchs_h2h):
        """L'analyse retourne une structure complète."""
        result = analyseur.analyser_match(
            equipe_dom_id=1,
            equipe_ext_id=2,
            matchs_dom=matchs_domicile,
            matchs_ext=matchs_exterieur,
            matchs_h2h=matchs_h2h
        )
        
        assert "timestamp" in result
        assert "equipes" in result
        assert "formes" in result
        assert "h2h" in result
        assert "prediction" in result
        assert "over_under" in result
    
    def test_analyser_match_avec_cotes(self, analyseur, matchs_domicile, matchs_exterieur, matchs_h2h):
        """L'analyse avec cotes inclut les value bets."""
        cotes = {"domicile": 2.0, "nul": 3.5, "exterieur": 4.0}
        
        result = analyseur.analyser_match(
            equipe_dom_id=1,
            equipe_ext_id=2,
            matchs_dom=matchs_domicile,
            matchs_ext=matchs_exterieur,
            matchs_h2h=matchs_h2h,
            cotes=cotes
        )
        
        assert "value_bets" in result
        assert isinstance(result["value_bets"], list)
    
    def test_historique_analyses_stocke(self, analyseur, matchs_domicile, matchs_exterieur, matchs_h2h):
        """L'analyseur stocke l'historique des analyses."""
        analyseur.analyser_match(1, 2, matchs_domicile, matchs_exterieur, matchs_h2h)
        analyseur.analyser_match(3, 4, matchs_domicile, matchs_exterieur, matchs_h2h)
        
        assert len(analyseur._historique_analyses) == 2


class TestCalculerValueBet:
    """Tests pour calculer_value_bet."""
    
    @pytest.fixture
    def analyseur(self):
        return AnalyseurParis()
    
    def test_value_bet_detecte(self, analyseur):
        """Détecte un value bet quand cote > cote juste."""
        prediction = {
            "probabilites": {
                "domicile": 55.0,  # Proba 55%
                "nul": 25.0,
                "exterieur": 20.0
            }
        }
        cotes = {
            "domicile": 2.2,  # Cote juste = 1/0.55 = 1.82 → Value!
            "nul": 3.5,
            "exterieur": 5.0
        }
        
        value_bets = analyseur.calculer_value_bet(prediction, cotes)
        
        assert len(value_bets) >= 1
        dom_vb = next((vb for vb in value_bets if vb["type"] == "1"), None)
        assert dom_vb is not None
        assert dom_vb["ev"] > 0
    
    def test_pas_de_value_bet(self, analyseur):
        """Pas de value bet si cotes normales."""
        prediction = {
            "probabilites": {
                "domicile": 55.0,
                "nul": 25.0,
                "exterieur": 20.0
            }
        }
        cotes = {
            "domicile": 1.6,  # Cote juste = 1.82, ici trop basse
            "nul": 3.0,
            "exterieur": 4.0
        }
        
        value_bets = analyseur.calculer_value_bet(prediction, cotes)
        
        # Peut retourner vide ou des petits value bets
        for vb in value_bets:
            # Les EV ne devraient pas être énormes
            assert vb["ev"] < 50
    
    def test_niveau_value_bet(self, analyseur):
        """Classement du niveau de value bet."""
        prediction = {
            "probabilites": {
                "domicile": 60.0,
                "nul": 20.0,
                "exterieur": 20.0
            }
        }
        cotes = {
            "domicile": 3.0,  # Très bon value (cote juste 1.67)
            "nul": 3.5,
            "exterieur": 4.0
        }
        
        value_bets = analyseur.calculer_value_bet(prediction, cotes)
        
        if value_bets:
            assert value_bets[0]["niveau"] in ["excellent", "bon", "acceptable"]


class TestAnalyserTendanceButs:
    """Tests pour analyser_tendance_buts."""
    
    @pytest.fixture
    def analyseur(self):
        return AnalyseurParis()
    
    def test_tendance_offensive(self, analyseur):
        """Détecte une tendance offensive."""
        matchs = [
            {"score_domicile": 3, "score_exterieur": 2},
            {"score_domicile": 2, "score_exterieur": 2},
            {"score_domicile": 4, "score_exterieur": 1},
            {"score_domicile": 2, "score_exterieur": 3},
        ]
        
        result = analyseur.analyser_tendance_buts(matchs)
        
        assert result["tendance"] in ["offensif", "très offensif"]
        assert result["stats"]["over_2_5"] > 50
    
    def test_tendance_defensive(self, analyseur):
        """Détecte une tendance défensive."""
        matchs = [
            {"score_domicile": 1, "score_exterieur": 0},
            {"score_domicile": 0, "score_exterieur": 0},
            {"score_domicile": 1, "score_exterieur": 1},
            {"score_domicile": 0, "score_exterieur": 1},
        ]
        
        result = analyseur.analyser_tendance_buts(matchs)
        
        assert result["tendance"] in ["défensif", "très défensif"]
        assert result["stats"]["over_2_5"] < 40
    
    def test_stats_btts(self, analyseur):
        """Statistiques BTTS."""
        matchs = [
            {"score_domicile": 2, "score_exterieur": 1},  # BTTS
            {"score_domicile": 1, "score_exterieur": 2},  # BTTS
            {"score_domicile": 3, "score_exterieur": 0},  # No BTTS
            {"score_domicile": 1, "score_exterieur": 1},  # BTTS
        ]
        
        result = analyseur.analyser_tendance_buts(matchs)
        
        assert result["stats"]["btts"] == 75.0
    
    def test_clean_sheets_equipe(self, analyseur):
        """Stats clean sheets pour une équipe spécifique."""
        matchs = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0},
            {"equipe_domicile_id": 1, "score_domicile": 1, "score_exterieur": 1},
            {"equipe_domicile_id": 2, "score_domicile": 0, "score_exterieur": 1},  # Ext
        ]
        
        result = analyseur.analyser_tendance_buts(matchs, equipe_id=1)
        
        # 2 clean sheets sur 3 matchs
        assert result["stats"]["clean_sheets"] is not None
    
    def test_matchs_vides(self, analyseur):
        """Retourne tendance inconnue sans matchs."""
        result = analyseur.analyser_tendance_buts([])
        
        assert result["tendance"] == "inconnu"


class TestGenererAnalyseComplete:
    """Tests pour generer_analyse_complete."""
    
    def test_analyse_complete_structure(self):
        """L'analyse complète a toutes les sections."""
        match = {
            "equipe_domicile_id": 1,
            "equipe_exterieur_id": 2,
            "equipe_domicile": "PSG",
            "equipe_exterieur": "Lyon",
            "date": "2024-01-15",
            "championnat": "Ligue 1"
        }
        matchs_dom = [
            {"equipe_domicile_id": 1, "score_domicile": 2, "score_exterieur": 0}
        ]
        matchs_ext = [
            {"equipe_domicile_id": 2, "score_domicile": 1, "score_exterieur": 1}
        ]
        
        result = generer_analyse_complete(
            match, matchs_dom, matchs_ext, [], None, "Ligue 1"
        )
        
        assert "prediction" in result
        assert "formes" in result
        assert "tendance_buts" in result
        assert "resume" in result
        assert "match" in result
    
    def test_analyse_avec_cotes(self):
        """Analyse avec cotes inclut les value bets."""
        match = {
            "equipe_domicile_id": 1,
            "equipe_exterieur_id": 2,
            "equipe_domicile": "PSG",
            "equipe_exterieur": "Lyon"
        }
        cotes = {"domicile": 1.5, "nul": 4.0, "exterieur": 6.0}
        
        result = generer_analyse_complete(
            match, [], [], [], cotes
        )
        
        assert "value_bets" in result


class TestGenererResumeParieur:
    """Tests pour generer_resume_parieur."""
    
    def test_resume_contient_prediction(self):
        """Le résumé contient la prédiction."""
        analyse = {
            "match": {"equipe_domicile": "PSG", "equipe_exterieur": "Lyon"},
            "prediction": {
                "prediction": "1",
                "confiance": 70,
                "probabilites": {"domicile": 55, "nul": 25, "exterieur": 20},
                "conseil": "Parier 3%"
            },
            "formes": {
                "domicile": {"forme_str": "VVVND", "score": 75, "matchs_sans_nul": 2},
                "exterieur": {"forme_str": "DDVND", "score": 45, "matchs_sans_nul": 2}
            },
            "value_bets": [],
            "over_under": {"prediction": "over", "buts_attendus": 2.8}
        }
        
        resume = generer_resume_parieur(analyse)
        
        assert "PSG" in resume
        assert "Lyon" in resume
        assert "Prédiction" in resume or "Pr" in resume
    
    def test_resume_avec_alertes_nul(self):
        """Le résumé signale les séries sans nul."""
        analyse = {
            "match": {"equipe_domicile": "PSG", "equipe_exterieur": "Lyon"},
            "prediction": {
                "prediction": "N",
                "confiance": 60,
                "probabilites": {"domicile": 35, "nul": 35, "exterieur": 30},
                "conseil": "Prudent"
            },
            "formes": {
                "domicile": {"forme_str": "VVVVV", "score": 80, "matchs_sans_nul": 8, "serie_en_cours": None},
                "exterieur": {"forme_str": "DDDDD", "score": 20, "matchs_sans_nul": 6, "serie_en_cours": None}
            },
            "value_bets": [],
            "over_under": {"prediction": "under", "buts_attendus": 2.0}
        }
        
        resume = generer_resume_parieur(analyse)
        
        assert "nul" in resume.lower() or "⚠" in resume
    
    def test_resume_avec_value_bets(self):
        """Le résumé affiche les value bets."""
        analyse = {
            "match": {"equipe_domicile": "PSG", "equipe_exterieur": "Lyon"},
            "prediction": {
                "prediction": "1",
                "confiance": 65,
                "probabilites": {"domicile": 50, "nul": 25, "exterieur": 25},
                "conseil": "OK"
            },
            "formes": {
                "domicile": {"forme_str": "VVNDD", "score": 55, "matchs_sans_nul": 2},
                "exterieur": {"forme_str": "DDNVV", "score": 55, "matchs_sans_nul": 2}
            },
            "value_bets": [
                {"type": "1", "cote_actuelle": 2.5, "ev": 12}
            ],
            "over_under": {"prediction": "over", "buts_attendus": 2.6}
        }
        
        resume = generer_resume_parieur(analyse)
        
        assert "Value" in resume or "💎" in resume
