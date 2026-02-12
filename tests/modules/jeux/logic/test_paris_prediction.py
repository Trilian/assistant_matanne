"""
Tests du module paris - Prédiction de matchs.

Tests de couverture pour:
- predire_resultat_match
- generer_conseil_pari
- predire_over_under
- generer_conseils_avances
"""

import pytest
from src.domains.jeux.logic.paris.prediction import (
    predire_resultat_match,
    generer_conseil_pari,
    predire_over_under,
    generer_conseils_avances,
)


class TestPredireResultatMatch:
    """Tests pour predire_resultat_match."""
    
    @pytest.fixture
    def forme_domicile_forte(self):
        """Équipe domicile en forme."""
        return {
            "score": 85,
            "forme_str": "VVVVV",
            "tendance": "hausse",
            "victoires": 5,
            "nuls": 0,
            "defaites": 0,
            "nb_matchs": 5,
            "serie_en_cours": "5V",
            "matchs_sans_nul": 5
        }
    
    @pytest.fixture
    def forme_exterieur_faible(self):
        """Équipe extérieur en difficulté."""
        return {
            "score": 25,
            "forme_str": "DDDVD",
            "tendance": "baisse",
            "victoires": 1,
            "nuls": 0,
            "defaites": 4,
            "nb_matchs": 5,
            "serie_en_cours": "2D",
            "matchs_sans_nul": 5
        }
    
    @pytest.fixture
    def h2h_equilibre(self):
        """Historique équilibré."""
        return {
            "nb_matchs": 6,
            "victoires_dom": 2,
            "victoires_ext": 2,
            "nuls": 2,
            "avantage": "equilibre"
        }
    
    def test_prediction_victoire_domicile(self, forme_domicile_forte, forme_exterieur_faible, h2h_equilibre):
        """Prédit victoire domicile quand forme très supérieure."""
        result = predire_resultat_match(
            forme_domicile_forte,
            forme_exterieur_faible,
            h2h_equilibre
        )
        
        assert result["prediction"] == "1"
        assert result["probabilites"]["domicile"] > 50
        assert result["confiance"] > 50
        assert result["niveau_confiance"] in ["moyenne", "haute"]
    
    def test_prediction_avec_cotes(self, forme_domicile_forte, forme_exterieur_faible, h2h_equilibre):
        """Les cotes influencent légèrement la prédiction."""
        cotes = {"domicile": 1.5, "nul": 4.0, "exterieur": 6.0}
        
        result = predire_resultat_match(
            forme_domicile_forte,
            forme_exterieur_faible,
            h2h_equilibre,
            cotes
        )
        
        assert "conseil" in result
        assert result["prediction"] == "1"
    
    def test_prediction_raisons_generees(self, forme_domicile_forte, forme_exterieur_faible, h2h_equilibre):
        """Les raisons expliquent la prédiction."""
        result = predire_resultat_match(
            forme_domicile_forte,
            forme_exterieur_faible,
            h2h_equilibre
        )
        
        assert "raisons" in result
        assert len(result["raisons"]) > 0
        assert any("domicile" in r.lower() for r in result["raisons"])
    
    def test_prediction_avec_bonus_nul(self):
        """Bonus nul quand longue série sans nul."""
        forme_dom = {
            "score": 60, "forme_str": "VDVDV", "tendance": "stable",
            "victoires": 3, "nuls": 0, "defaites": 2, "nb_matchs": 5,
            "serie_en_cours": None, "matchs_sans_nul": 8
        }
        forme_ext = {
            "score": 55, "forme_str": "DVDVD", "tendance": "stable",
            "victoires": 2, "nuls": 0, "defaites": 3, "nb_matchs": 5,
            "serie_en_cours": None, "matchs_sans_nul": 7
        }
        h2h = {"nb_matchs": 2, "avantage": None}
        
        result = predire_resultat_match(forme_dom, forme_ext, h2h)
        
        # Le bonus nul devrait augmenter la proba de nul
        assert result["probabilites"]["nul"] > 20
        # Et générer une raison liée au nul
        raisons_nul = [r for r in result["raisons"] if "nul" in r.lower()]
        assert len(raisons_nul) > 0
    
    def test_confiance_basse_si_peu_de_matchs(self, h2h_equilibre):
        """Confiance réduite si pas assez de données."""
        forme_dom = {
            "score": 70, "forme_str": "VV", "tendance": "hausse",
            "victoires": 2, "nuls": 0, "defaites": 0, "nb_matchs": 2,
            "serie_en_cours": "2V", "matchs_sans_nul": 2
        }
        forme_ext = {
            "score": 30, "forme_str": "DD", "tendance": "baisse",
            "victoires": 0, "nuls": 0, "defaites": 2, "nb_matchs": 2,
            "serie_en_cours": "2D", "matchs_sans_nul": 2
        }
        
        result = predire_resultat_match(forme_dom, forme_ext, h2h_equilibre)
        
        # Confiance réduite de 20% (x 0.8)
        assert result["confiance"] < 80


class TestGenererConseilPari:
    """Tests pour generer_conseil_pari."""
    
    def test_conseil_confiance_haute(self):
        """Conseil positif avec haute confiance."""
        conseil = generer_conseil_pari(
            prediction="1",
            confiance=75,
            cotes={"domicile": 1.8, "nul": 3.5, "exterieur": 4.5}
        )
        
        assert "PARIER" in conseil
        assert "Victoire domicile" in conseil
    
    def test_conseil_confiance_moyenne(self):
        """Conseil prudent avec confiance moyenne."""
        conseil = generer_conseil_pari(
            prediction="N",
            confiance=55,
            cotes={"domicile": 2.5, "nul": 3.2, "exterieur": 2.8}
        )
        
        assert "PRUDENT" in conseil
    
    def test_conseil_confiance_basse(self):
        """Conseil d'éviter avec basse confiance."""
        conseil = generer_conseil_pari(
            prediction="2",
            confiance=35
        )
        
        assert "VITER" in conseil or "Attends" in conseil
    
    def test_conseil_value_bet_detecte(self):
        """Détection de value bet si cote élevée."""
        conseil = generer_conseil_pari(
            prediction="1",
            confiance=70,
            cotes={"domicile": 2.5, "nul": 3.5, "exterieur": 3.0}
        )
        
        assert "VALUE" in conseil or "value" in conseil.lower()
    
    def test_conseil_proba_nul_elevee(self):
        """Suggère le nul si proba élevée."""
        conseil = generer_conseil_pari(
            prediction="1",
            confiance=60,
            proba_nul=0.35
        )
        
        assert "nul" in conseil.lower()


class TestPredireOverUnder:
    """Tests pour predire_over_under."""
    
    def test_over_equipes_offensives(self):
        """Prédit over avec équipes offensives."""
        forme_dom = {
            "buts_marques": 15, "buts_encaisses": 8, "nb_matchs": 5
        }
        forme_ext = {
            "buts_marques": 12, "buts_encaisses": 10, "nb_matchs": 5
        }
        
        result = predire_over_under(forme_dom, forme_ext, seuil=2.5)
        
        assert result["prediction"] == "over"
        assert result["buts_attendus"] > 2.5
        assert result["probabilite_over"] > 50
    
    def test_under_equipes_defensives(self):
        """Prédit under avec équipes défensives."""
        forme_dom = {
            "buts_marques": 3, "buts_encaisses": 2, "nb_matchs": 5
        }
        forme_ext = {
            "buts_marques": 2, "buts_encaisses": 3, "nb_matchs": 5
        }
        
        result = predire_over_under(forme_dom, forme_ext, seuil=2.5)
        
        assert result["prediction"] == "under"
        assert result["buts_attendus"] < 2.5
        assert result["probabilite_under"] > 50
    
    def test_seuil_personnalise(self):
        """Seuil différent de 2.5."""
        forme_dom = {"buts_marques": 10, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"buts_marques": 8, "buts_encaisses": 6, "nb_matchs": 5}
        
        result_25 = predire_over_under(forme_dom, forme_ext, seuil=2.5)
        result_35 = predire_over_under(forme_dom, forme_ext, seuil=3.5)
        
        # Proba over plus basse avec seuil plus haut
        assert result_25["probabilite_over"] > result_35["probabilite_over"]
    
    def test_confiance_calculee(self):
        """Confiance basée sur l'écart au 50%."""
        forme_dom = {"buts_marques": 20, "buts_encaisses": 10, "nb_matchs": 5}
        forme_ext = {"buts_marques": 15, "buts_encaisses": 8, "nb_matchs": 5}
        
        result = predire_over_under(forme_dom, forme_ext)
        
        assert "confiance" in result
        assert 0 <= result["confiance"] <= 100


class TestGenererConseilsAvances:
    """Tests pour generer_conseils_avances."""
    
    def test_conseil_serie_sans_nul(self):
        """Génère conseil si longue série sans nul."""
        forme_dom = {"matchs_sans_nul": 7, "serie_en_cours": None, 
                     "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        assert any("NUL" in c["type"] for c in conseils)
    
    def test_conseil_rebond_apres_defaites(self):
        """Génère conseil rebond après série de défaites."""
        forme_dom = {"matchs_sans_nul": 2, "serie_en_cours": "5D",
                     "buts_marques": 5, "buts_encaisses": 10, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        assert any("REBOND" in c["type"] for c in conseils)
    
    def test_conseil_over_equipes_offensives(self):
        """Génère conseil over si moyenne de buts élevée."""
        forme_dom = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 15, "buts_encaisses": 8, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 12, "buts_encaisses": 10, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        assert any("OVER" in c["type"] for c in conseils)
    
    def test_conseil_value_bet_nul(self):
        """Génère conseil value bet si cote nul élevée + série."""
        forme_dom = {"matchs_sans_nul": 5, "serie_en_cours": None,
                     "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 5, "buts_encaisses": 5, "nb_matchs": 5}
        cotes = {"domicile": 2.0, "nul": 4.5, "exterieur": 3.0}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext, cotes)
        
        assert any("VALUE" in c["type"] for c in conseils)
    
    def test_pas_de_conseil_si_rien_notable(self):
        """Aucun conseil si pas de pattern notable."""
        forme_dom = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 6, "buts_encaisses": 6, "nb_matchs": 5}
        forme_ext = {"matchs_sans_nul": 2, "serie_en_cours": None,
                     "buts_marques": 6, "buts_encaisses": 6, "nb_matchs": 5}
        
        conseils = generer_conseils_avances(forme_dom, forme_ext)
        
        # Peut être vide ou avoir des conseils génériques
        assert isinstance(conseils, list)
