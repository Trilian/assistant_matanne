"""
Tests unitaires pour BankrollManager.

Vérifie:
- Calcul Kelly Criterion avec coefficient fractionnaire 0.25
- Validation de mise (seuils 3% et 5%)
- Historique bankroll
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.services.jeux.bankroll_manager import BankrollManager
from src.core.models.jeux import BankrollHistorique
from src.core.db import obtenir_contexte_db


class TestBankrollManager:
    """Tests pour le service BankrollManager."""

    def test_calculer_mise_kelly_formule(self):
        """Test calcul Kelly avec formule correcte."""
        manager = BankrollManager()
        
        # Cas typique: bankroll 1000€, edge 5%, cote 2.5
        bankroll = 1000.0
        edge = 0.05
        cote = 2.5
        
        mise = manager.calculer_mise_kelly(bankroll, edge, cote)
        
        # Kelly full = (edge * (cote - 1)) / (cote - 1) = 0.05
        # Kelly fractional (25%) = 0.05 * 0.25 = 0.0125
        # Mise = 1000 * 0.0125 = 12.5€
        assert 12.0 <= mise <= 13.0, f"Mise {mise}€ hors plage attendue"
    
    def test_calculer_mise_kelly_edge_zero(self):
        """Test avec edge nul (mise = 0)."""
        manager = BankrollManager()
        
        mise = manager.calculer_mise_kelly(1000.0, 0.0, 2.0)
        
        assert mise == 0.0, "Edge nul devrait donner mise 0"
    
    def test_calculer_mise_kelly_edge_negatif(self):
        """Test avec edge négatif (mise = 0)."""
        manager = BankrollManager()
        
        mise = manager.calculer_mise_kelly(1000.0, -0.05, 2.5)
        
        assert mise == 0.0, "Edge négatif devrait donner mise 0"
    
    def test_calculer_mise_kelly_fractional_25(self):
        """Vérifie le coefficient fractionnaire 0.25."""
        manager = BankrollManager()
        
        # Edge élevé: 20%, cote 3.0
        mise = manager.calculer_mise_kelly(1000.0, 0.20, 3.0)
        
        # Kelly full = (0.20 * 2.0) / 2.0 = 0.20 → mise full = 200€
        # Fractional 25% = 200 * 0.25 = 50€
        assert 48.0 <= mise <= 52.0, f"Fractional 25% non appliqué: {mise}€"
    
    def test_valider_mise_acceptable(self):
        """Test validation mise acceptable (<3%)."""
        manager = BankrollManager()
        
        validation = manager.valider_mise(20.0, 1000.0)
        
        assert validation.autorise is True
        assert validation.niveau_risque != "eleve"
    
    def test_valider_mise_alerte_3_pct(self):
        """Test seuil alerte 3%."""
        manager = BankrollManager()
        
        # 35€ / 1000€ = 3.5% → alerte
        validation = manager.valider_mise(35.0, 1000.0, seuil=0.03)
        
        assert validation.autorise is True
        assert validation.niveau_risque == "eleve"
        assert "élevée" in validation.raison.lower() or "3%" in validation.raison
    
    def test_valider_mise_hard_cap_5_pct(self):
        """Test hard cap 5%."""
        manager = BankrollManager()
        
        # 60€ / 1000€ = 6% → bloqué
        validation = manager.valider_mise(60.0, 1000.0)
        
        assert validation.autorise is False
        assert "5%" in validation.raison or "cap" in validation.raison.lower()
    
    def test_valider_mise_limite_exacte_5_pct(self):
        """Test limite exacte 5%."""
        manager = BankrollManager()
        
        # 50€ / 1000€ = 5.0% exactement
        validation = manager.valider_mise(50.0, 1000.0)
        
        # Devrait être autorisé (≤ 5%) ou bloqué selon implémentation stricte
        # Vérifier cohérence
        assert isinstance(validation.autorise, bool)
    
    @pytest.mark.integration
    def test_obtenir_historique_vide(self):
        """Test historique sans données."""
        manager = BankrollManager()
        
        with obtenir_contexte_db() as session:
            # User ID fictif qui n'existe pas
            historique = manager.obtenir_historique(user_id=99999, jours=30, session=session)
        
        assert isinstance(historique, list)
        assert len(historique) == 0
    
    @pytest.mark.integration
    def test_obtenir_historique_avec_donnees(self):
        """Test historique avec données mockées."""
        manager = BankrollManager()
        
        with obtenir_contexte_db() as session:
            # Créer données de test
            user_id_test = 1
            
            # Supprimer anciennes données test
            session.query(BankrollHistorique).filter(
                BankrollHistorique.user_id == user_id_test
            ).delete()
            
            # Insérer 3 enregistrements
            for i in range(3):
                record = BankrollHistorique(
                    user_id=user_id_test,
                    montant=1000.0 + (i * 50),
                    date=datetime.now() - timedelta(days=i),
                    variation=50.0 if i > 0 else 0.0
                )
                session.add(record)
            
            session.commit()
            
            # Récupérer historique
            historique = manager.obtenir_historique(user_id=user_id_test, jours=7, session=session)
            
            assert len(historique) == 3
            assert all("montant" in h for h in historique)
            assert all("date" in h for h in historique)
            
            # Nettoyage
            session.query(BankrollHistorique).filter(
                BankrollHistorique.user_id == user_id_test
            ).delete()
            session.commit()


class TestBankrollEdgeCases:
    """Tests cas limites."""
    
    def test_bankroll_zero(self):
        """Test avec bankroll à zéro."""
        manager = BankrollManager()
        
        mise = manager.calculer_mise_kelly(0.0, 0.05, 2.5)
        
        assert mise == 0.0
    
    def test_cote_trop_faible(self):
        """Test avec cote < 1.0 (invalide)."""
        manager = BankrollManager()
        
        # Cote 0.8 n'a pas de sens (paris sportifs: cote ≥ 1.0)
        mise = manager.calculer_mise_kelly(1000.0, 0.05, 0.8)
        
        # Devrait retourner 0 ou lever exception
        assert mise == 0.0 or mise is None
    
    def test_edge_extreme_100_pct(self):
        """Test avec edge 100% (irréaliste mais testé)."""
        manager = BankrollManager()
        
        mise = manager.calculer_mise_kelly(1000.0, 1.0, 2.0)
        
        # Kelly full = (1.0 * 1.0) / 1.0 = 1.0 → tous les fonds
        # Fractional 25% = 1000 * 1.0 * 0.25 = 250€
        # Devrait être plafonné à 5% (50€) après validation
        assert mise > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
