"""
Tests pour la Feature 5: Prévisions ML
Tests du service PredictionService et des modèles associés
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.services.predictions import (
    PredictionService,
    PredictionArticle,
    AnalysePrediction,
    obtenir_service_predictions
)


class TestPredictionArticle:
    """Tests du modèle Pydantic PredictionArticle"""
    
    def test_prediction_article_creation(self):
        """Test création d'une prédiction d'article"""
        pred = PredictionArticle(
            nom="Tomates",
            unite="kg",
            quantite_actuelle=10.0,
            quantite_predite=5.5,
            consommation_moyenne=0.5,
            tendance="décroissante",
            confiance=0.85,
            risque_rupture=False,
            jours_avant_rupture=20
        )
        
        assert pred.nom == "Tomates"
        assert pred.quantite_actuelle == 10.0
        assert pred.confiance == 0.85
        assert pred.risque_rupture == False
    
    def test_prediction_article_with_rupture(self):
        """Test création avec risque de rupture"""
        pred = PredictionArticle(
            nom="Lait",
            unite="L",
            quantite_actuelle=0.5,
            quantite_predite=-0.5,
            consommation_moyenne=0.2,
            tendance="décroissante",
            confiance=0.9,
            risque_rupture=True,
            jours_avant_rupture=2
        )
        
        assert pred.risque_rupture == True
        assert pred.jours_avant_rupture == 2
    
    def test_prediction_article_validation(self):
        """Test validation des champs Pydantic"""
        # Confiance doit être entre 0 et 1
        with pytest.raises(ValueError):
            PredictionArticle(
                nom="Test",
                unite="kg",
                quantite_actuelle=1,
                quantite_predite=0.5,
                consommation_moyenne=0.1,
                tendance="stable",
                confiance=1.5,  # Invalid!
                risque_rupture=False,
                jours_avant_rupture=None
            )


class TestAnalysePrediction:
    """Tests du modèle Pydantic AnalysePrediction"""
    
    def test_analyse_prediction_creation(self):
        """Test création d'une analyse globale"""
        analyse = AnalysePrediction(
            tendance_globale="stable",
            consommation_moyenne_globale=0.5,
            consommation_min=0.1,
            consommation_max=1.5,
            nb_articles_croissance=3,
            nb_articles_decroissance=2,
            nb_articles_stables=5
        )
        
        assert analyse.tendance_globale == "stable"
        assert analyse.consommation_moyenne_globale == 0.5
        assert analyse.nb_articles_croissance == 3
    
    def test_analyse_prediction_croissante(self):
        """Test analyse avec tendance croissante"""
        analyse = AnalysePrediction(
            tendance_globale="croissante",
            consommation_moyenne_globale=0.8,
            consommation_min=0.3,
            consommation_max=1.8,
            nb_articles_croissance=7,
            nb_articles_decroissance=1,
            nb_articles_stables=2
        )
        
        assert analyse.tendance_globale == "croissante"
        assert analyse.nb_articles_croissance == 7


class TestPredictionService:
    """Tests du service PredictionService"""
    
    @pytest.fixture
    def mock_service(self):
        """Fixture pour un service mocké"""
        service = PredictionService()
        
        # Mock la database
        service.db = MagicMock()
        
        return service
    
    def test_service_initialization(self, mock_service):
        """Test initialisation du service"""
        assert mock_service is not None
        assert hasattr(mock_service, 'generer_predictions')
        assert hasattr(mock_service, 'obtenir_analyse_globale')
        assert hasattr(mock_service, 'generer_recommandations')
    
    def test_analyser_historique_article_insufficient_data(self, mock_service):
        """Test analyse avec données insuffisantes"""
        # Mock article avec peu de données
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Tomates"
        mock_article.unite = "kg"
        mock_article.quantite = 10
        mock_article.seuil_min = 2
        mock_article.historique = []  # Pas d'historique
        
        result = mock_service.analyser_historique_article(1)
        
        # Doit retourner confiance 0 avec données insuffisantes
        assert result['confiance'] == 0.0
    
    def test_analyser_historique_article_with_data(self, mock_service):
        """Test analyse avec données historiques"""
        # Mock données historiques
        historiques = [
            Mock(quantite_nouveau=10, date_changement=datetime.now() - timedelta(days=10)),
            Mock(quantite_nouveau=9, date_changement=datetime.now() - timedelta(days=5)),
            Mock(quantite_nouveau=8, date_changement=datetime.now()),
        ]
        
        mock_article = Mock()
        mock_article.id = 1
        mock_article.nom = "Tomates"
        mock_article.unite = "kg"
        mock_article.quantite = 8
        mock_article.seuil_min = 2
        mock_article.historique = historiques
        
        # Mock la query
        mock_query = MagicMock()
        mock_query.filter_by.return_value.first.return_value = mock_article
        mock_service.db.session.query.return_value = mock_query
        
        result = mock_service.analyser_historique_article(1)
        
        assert 'consommation_moyenne' in result
        assert 'tendance' in result
        assert result['confiance'] > 0
    
    def test_predire_quantite(self, mock_service):
        """Test prédiction de quantité"""
        # Mock analyse historique
        analyse = {
            'consommation_moyenne': 0.5,
            'quantite_actuelle': 10,
            'stabilite': 0.1
        }
        
        prediction = mock_service.predire_quantite(analyse, jours=30)
        
        # Quantité prédite = actuelle - (consommation * jours)
        expected = 10 - (0.5 * 30)
        
        assert prediction == expected
    
    def test_detecter_rupture_risque(self, mock_service):
        """Test détection de risque de rupture"""
        analyse = {
            'quantite_actuelle': 2,
            'seuil_min': 1,
            'consommation_moyenne': 0.5,
            'stabilite': 0.1
        }
        
        # Avec consommation de 0.5/jour, 2 kg = 4 jours
        risque, jours = mock_service.detecter_rupture_risque(analyse)
        
        # 4 jours < 14 jours = risque
        assert risque == True
        assert jours == 4
    
    def test_detecter_rupture_risque_secure(self, mock_service):
        """Test quand stock est sûr"""
        analyse = {
            'quantite_actuelle': 50,
            'seuil_min': 1,
            'consommation_moyenne': 0.5,
            'stabilite': 0.1
        }
        
        # Avec consommation de 0.5/jour, 50 kg = 100 jours
        risque, jours = mock_service.detecter_rupture_risque(analyse)
        
        # 100 jours > 14 jours = pas de risque
        assert risque == False
        assert jours == 100
    
    def test_generer_predictions(self, mock_service):
        """Test génération batch de prédictions"""
        # Mock multiple articles
        mock_articles = [
            Mock(
                id=1,
                nom="Tomates",
                unite="kg",
                quantite=10,
                seuil_min=2,
                historique=[]
            ),
            Mock(
                id=2,
                nom="Lait",
                unite="L",
                quantite=2,
                seuil_min=1,
                historique=[]
            ),
        ]
        
        # Mock la query pour retourner tous les articles
        mock_query = MagicMock()
        mock_query.all.return_value = mock_articles
        mock_service.db.session.query.return_value = mock_query
        
        predictions = mock_service.generer_predictions()
        
        assert isinstance(predictions, list)
        assert len(predictions) == 2
        assert all(isinstance(p, PredictionArticle) for p in predictions)
    
    def test_obtenir_analyse_globale(self, mock_service):
        """Test analyse globale"""
        predictions = [
            PredictionArticle(
                nom="Tomates",
                unite="kg",
                quantite_actuelle=10,
                quantite_predite=5,
                consommation_moyenne=0.5,
                tendance="décroissante",
                confiance=0.8,
                risque_rupture=False,
                jours_avant_rupture=20
            ),
            PredictionArticle(
                nom="Lait",
                unite="L",
                quantite_actuelle=2,
                quantite_predite=1,
                consommation_moyenne=0.3,
                tendance="stable",
                confiance=0.85,
                risque_rupture=False,
                jours_avant_rupture=7
            ),
        ]
        
        # Mock la méthode de génération
        with patch.object(mock_service, 'generer_predictions', return_value=predictions):
            analyse = mock_service.obtenir_analyse_globale()
        
        assert isinstance(analyse, AnalysePrediction)
        assert analyse.consommation_moyenne_globale > 0
    
    def test_generer_recommandations(self, mock_service):
        """Test génération de recommandations"""
        predictions = [
            PredictionArticle(
                nom="Tomates",
                unite="kg",
                quantite_actuelle=0.5,  # Peu de stock
                quantite_predite=-1,
                consommation_moyenne=0.5,
                tendance="décroissante",
                confiance=0.8,
                risque_rupture=True,
                jours_avant_rupture=1
            ),
        ]
        
        # Mock la méthode de génération
        with patch.object(mock_service, 'generer_predictions', return_value=predictions):
            recommandations = mock_service.generer_recommandations()
        
        assert isinstance(recommandations, list)
        if recommandations:
            rec = recommandations[0]
            assert hasattr(rec, 'nom')
            assert hasattr(rec, 'priorite')


class TestObteinirServicePredictions:
    """Tests du singleton obtenir_service_predictions"""
    
    def test_singleton_pattern(self):
        """Test que le singleton retourne la même instance"""
        service1 = obtenir_service_predictions()
        service2 = obtenir_service_predictions()
        
        assert service1 is service2
    
    def test_singleton_is_prediction_service(self):
        """Test que le singleton retourne un PredictionService"""
        service = obtenir_service_predictions()
        
        assert isinstance(service, PredictionService)


class TestPredictionIntegration:
    """Tests d'intégration pour les prédictions"""
    
    def test_full_prediction_workflow(self):
        """Test du workflow complet de prédiction"""
        service = obtenir_service_predictions()
        
        # Vérifier que le service a les bonnes méthodes
        assert hasattr(service, 'analyser_historique_article')
        assert hasattr(service, 'predire_quantite')
        assert hasattr(service, 'detecter_rupture_risque')
        assert hasattr(service, 'generer_predictions')
        assert hasattr(service, 'obtenir_analyse_globale')
        assert hasattr(service, 'generer_recommandations')
    
    def test_prediction_service_without_database(self):
        """Test que le service peut être instancié sans DB active"""
        service = PredictionService()
        
        # Doit pouvoir créer des modèles sans DB
        pred = PredictionArticle(
            nom="Test",
            unite="kg",
            quantite_actuelle=1,
            quantite_predite=0.5,
            consommation_moyenne=0.1,
            tendance="stable",
            confiance=0.5,
            risque_rupture=False,
            jours_avant_rupture=None
        )
        
        assert pred.nom == "Test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
