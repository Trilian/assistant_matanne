"""
Tests unitaires pour StatsPersonnellesService.

Vérifie:
- Calcul ROI global
- Calcul win rate
- Analyse patterns gagnants
- Évolution mensuelle
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.services.jeux.stats_personnelles import StatsPersonnellesService
from src.core.models.jeux import PariSportif, GrilleLoto, GrilleEuromillions
from src.core.db import obtenir_contexte_db
from tests.services.jeux.conftest import creer_match_test


class TestStatsPersonnellesService:
    """Tests pour le service StatsPersonnellesService."""
    
    @pytest.fixture
    def service(self):
        """Fixture service."""
        return StatsPersonnellesService()
    
    @pytest.fixture
    def user_id_test(self):
        """User ID pour tests."""
        return 1
    
    def test_calculer_roi_global_sans_donnees(self, service, user_id_test):
        """Test ROI avec aucun pari/grille."""
        with obtenir_contexte_db() as session:
            # User fictif sans données
            result = service.calculer_roi_global(user_id=99999, jours=30, session=session)
        
        assert result["roi"] == 0.0
        assert result["gains_totaux"] == 0.0
        assert result["mises_totales"] == 0.0
        assert result["benefice_net"] == 0.0
        assert result["nb_paris"] == 0
        assert result["nb_grilles"] == 0
    
    @pytest.mark.integration
    def test_calculer_roi_global_avec_paris(self, service, user_id_test):
        """Test ROI avec paris mockés."""
        with obtenir_contexte_db() as session:
            # Nettoyer données test
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            
            # Créer matchs de test
            for mid in (1, 2, 3):
                creer_match_test(session, mid)
            
            # Créer 3 paris: 2 gagnants, 1 perdant
            paris = [
                PariSportif(
                    user_id=user_id_test,
                    match_id=1,
                    type_pari="1X2",
                    prediction="Domicile",
                    cote=2.0,
                    mise=10.0,
                    gain=20.0,
                    statut="gagnant",
                    date_pari=datetime.now()
                ),
                PariSportif(
                    user_id=user_id_test,
                    match_id=2,
                    type_pari="1X2",
                    prediction="Exterieur",
                    cote=3.0,
                    mise=10.0,
                    gain=30.0,
                    statut="gagnant",
                    date_pari=datetime.now()
                ),
                PariSportif(
                    user_id=user_id_test,
                    match_id=3,
                    type_pari="1X2",
                    prediction="Nul",
                    cote=2.5,
                    mise=10.0,
                    gain=0.0,
                    statut="perdant",
                    date_pari=datetime.now()
                ),
            ]
            
            for p in paris:
                session.add(p)
            session.commit()
            
            # Calculer ROI
            result = service.calculer_roi_global(user_id=user_id_test, jours=30, session=session)
            
            # Gains = 20 + 30 = 50€
            # Mises = 10 + 10 + 10 = 30€
            # ROI = (50 - 30) / 30 * 100 = 66.67%
            assert result["gains_totaux"] == 50.0
            assert result["mises_totales"] == 30.0
            assert result["benefice_net"] == 20.0
            assert 65.0 <= result["roi"] <= 67.0
            assert result["nb_paris"] == 3
            
            # Nettoyage
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            session.commit()
    
    def test_calculer_win_rate_sans_donnees(self, service, user_id_test):
        """Test win rate sans données."""
        with obtenir_contexte_db() as session:
            result = service.calculer_win_rate(user_id=99999, jours=30, session=session)
        
        assert result["win_rate_global"] == 0.0
        assert result["nb_gagnants"] == 0
        assert result["nb_total"] == 0
    
    @pytest.mark.integration
    def test_calculer_win_rate_avec_paris(self, service, user_id_test):
        """Test win rate avec paris mockés."""
        with obtenir_contexte_db() as session:
            # Nettoyer
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            
            # Créer matchs de test
            for mid in range(5):
                creer_match_test(session, mid)
            
            # 3 gagnants / 5 total = 60%
            statuts = ["gagnant", "gagnant", "gagnant", "perdant", "perdant"]
            
            for i, statut in enumerate(statuts):
                pari = PariSportif(
                    user_id=user_id_test,
                    match_id=i,
                    type_pari="1X2",
                    prediction="Test",
                    cote=2.0,
                    mise=10.0,
                    gain=20.0 if statut == "gagnant" else 0.0,
                    statut=statut,
                    date_pari=datetime.now()
                )
                session.add(pari)
            session.commit()
            
            result = service.calculer_win_rate(user_id=user_id_test, jours=30, session=session)
            
            assert result["nb_total"] == 5
            assert result["nb_gagnants"] == 3
            assert result["win_rate_global"] == 60.0
            assert result["win_rate_paris"] == 60.0
            
            # Nettoyage
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            session.commit()
    
    @pytest.mark.integration
    def test_analyser_patterns_gagnants_sans_donnees(self, service, user_id_test):
        """Test patterns sans données."""
        with obtenir_contexte_db() as session:
            result = service.analyser_patterns_gagnants(user_id=99999, jours=90, session=session)
        
        assert result["meilleur_type_pari"] is None
        assert result["meilleure_strategie_loto"] is None
        assert result["meilleure_strategie_euro"] is None
        assert len(result["roi_par_type"]) == 0
        assert len(result["recommandations"]) == 0
    
    @pytest.mark.integration
    def test_analyser_patterns_gagnants_avec_donnees(self, service, user_id_test):
        """Test patterns avec paris variés."""
        with obtenir_contexte_db() as session:
            # Nettoyer
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            
            # Créer matchs de test
            for mid in (1, 2, 3):
                creer_match_test(session, mid)
            
            # Type "1" très rentable: 2 gagnés
            paris_type_1 = [
                PariSportif(
                    user_id=user_id_test,
                    match_id=1,
                    type_pari="1",
                    prediction="Domicile",
                    cote=2.0,
                    mise=10.0,
                    gain=20.0,
                    statut="gagnant",
                    date_pari=datetime.now()
                ),
                PariSportif(
                    user_id=user_id_test,
                    match_id=2,
                    type_pari="1",
                    prediction="Domicile",
                    cote=2.5,
                    mise=10.0,
                    gain=25.0,
                    statut="gagnant",
                    date_pari=datetime.now()
                ),
            ]
            
            # Type "X" peu rentable: 1 perdu
            paris_type_x = [
                PariSportif(
                    user_id=user_id_test,
                    match_id=3,
                    type_pari="X",
                    prediction="Nul",
                    cote=3.0,
                    mise=10.0,
                    gain=0.0,
                    statut="perdant",
                    date_pari=datetime.now()
                ),
            ]
            
            for p in paris_type_1 + paris_type_x:
                session.add(p)
            session.commit()
            
            result = service.analyser_patterns_gagnants(user_id=user_id_test, jours=90, session=session)
            
            # Type "1" devrait être meilleur
            assert result["meilleur_type_pari"] == "1"
            
            # ROI type 1: (45 - 20) / 20 * 100 = 125%
            assert "1" in result["roi_par_type"]
            assert result["roi_par_type"]["1"]["roi"] > 100
            
            # ROI type X: (0 - 10) / 10 * 100 = -100%
            assert "X" in result["roi_par_type"]
            assert result["roi_par_type"]["X"]["roi"] < 0
            
            # Recommandation
            assert len(result["recommandations"]) > 0
            assert any("1" in rec for rec in result["recommandations"])
            
            # Nettoyage
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            session.commit()
    
    def test_obtenir_evolution_mensuelle_sans_donnees(self, service, user_id_test):
        """Test évolution sans données."""
        with obtenir_contexte_db() as session:
            result = service.obtenir_evolution_mensuelle(user_id=99999, mois=6, session=session)
        
        assert "evolution" in result
        assert len(result["evolution"]) == 6  # 6 mois demandés
        
        # Tous les mois devraient avoir ROI = 0
        assert all(m["roi"] == 0.0 for m in result["evolution"])
    
    @pytest.mark.integration
    def test_obtenir_evolution_mensuelle_avec_donnees(self, service, user_id_test):
        """Test évolution mensuelle avec paris répartis."""
        with obtenir_contexte_db() as session:
            # Nettoyer
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            
            # Créer matchs de test
            for mid in (1, 2):
                creer_match_test(session, mid)
            
            # Mois courant: 1 gagnant
            pari_courant = PariSportif(
                user_id=user_id_test,
                match_id=1,
                type_pari="1X2",
                prediction="Test",
                cote=2.0,
                mise=10.0,
                gain=20.0,
                statut="gagnant",
                date_pari=datetime.now()
            )
            
            # Mois -1: 1 perdant
            pari_ancien = PariSportif(
                user_id=user_id_test,
                match_id=2,
                type_pari="1X2",
                prediction="Test",
                cote=2.0,
                mise=10.0,
                gain=0.0,
                statut="perdant",
                date_pari=datetime.now() - timedelta(days=35)
            )
            
            session.add(pari_courant)
            session.add(pari_ancien)
            session.commit()
            
            result = service.obtenir_evolution_mensuelle(user_id=user_id_test, mois=3, session=session)
            
            assert len(result["evolution"]) == 3
            
            # Dernier mois (index -1) devrait avoir ROI positif
            dernier_mois = result["evolution"][-1]
            assert dernier_mois["roi"] > 0
            assert dernier_mois["gains"] == 20.0
            assert dernier_mois["mises"] == 10.0
            assert dernier_mois["benefice"] == 10.0
            
            # Nettoyage
            session.query(PariSportif).filter(PariSportif.user_id == user_id_test).delete()
            session.commit()


class TestStatsPersonnellesEdgeCases:
    """Tests cas limites."""
    
    def test_roi_avec_mises_nulles(self):
        """Test ROI quand mises = 0 (division par zéro)."""
        service = StatsPersonnellesService()
        
        with obtenir_contexte_db() as session:
            # Devrait retourner ROI = 0 sans crash
            result = service.calculer_roi_global(user_id=99999, jours=30, session=session)
            
            assert result["roi"] == 0.0
    
    def test_win_rate_avec_zero_paris(self):
        """Test win rate sans aucun pari."""
        service = StatsPersonnellesService()
        
        with obtenir_contexte_db() as session:
            result = service.calculer_win_rate(user_id=99999, jours=30, session=session)
            
            assert result["win_rate_global"] == 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
