"""
Tests pour src/services/predictions.py
"""
import pytest
from datetime import datetime, timedelta


class TestPredictionArticleSchema:
    """Tests pour le schéma PredictionArticle."""

    def test_prediction_article_minimal(self):
        """Prédiction avec champs requis."""
        from src.services.suggestions import PredictionArticle
        
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=10,
            nom="Lait",
            quantite_actuelle=2.0,
            quantite_predite_semaine=1.5,
            quantite_predite_mois=0.5,
            taux_consommation_moyen=0.07
        )
        assert pred.nom == "Lait"
        assert pred.tendance == "stable"
        assert pred.confiance == 0.0

    def test_prediction_article_complet(self):
        """Prédiction avec tous les champs."""
        from src.services.suggestions import PredictionArticle
        
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=10,
            nom="Farine",
            quantite_actuelle=500,
            quantite_predite_semaine=400,
            quantite_predite_mois=100,
            taux_consommation_moyen=14.3,
            tendance="decroissante",
            confiance=0.85,
            risque_rupture_mois=True,
            jours_avant_rupture=20
        )
        assert pred.tendance == "decroissante"
        assert pred.risque_rupture_mois is True
        assert pred.jours_avant_rupture == 20


class TestAnalysePredictionSchema:
    """Tests pour le schéma AnalysePrediction."""

    def test_analyse_prediction_default(self):
        """Analyse avec valeurs par défaut."""
        from src.services.suggestions import AnalysePrediction
        
        analyse = AnalysePrediction(
            nombre_articles=10,
            articles_en_rupture_risque=["Lait", "Oeufs"],
            articles_croissance=["Pain"],
            articles_decroissance=["Beurre"],
            consommation_moyenne_globale=5.5,
            tendance_globale="stable"
        )
        assert analyse.nombre_articles == 10
        assert len(analyse.articles_en_rupture_risque) == 2
        assert analyse.nb_articles_croissance == 0  # Default

    def test_analyse_prediction_complete(self):
        """Analyse complète."""
        from src.services.suggestions import AnalysePrediction
        
        analyse = AnalysePrediction(
            nombre_articles=50,
            articles_en_rupture_risque=["Lait"],
            articles_croissance=["Pain", "Oeufs"],
            articles_decroissance=["Beurre"],
            consommation_moyenne_globale=10.5,
            consommation_min=0.5,
            consommation_max=50.0,
            nb_articles_croissance=2,
            nb_articles_decroissance=1,
            nb_articles_stables=47,
            tendance_globale="croissante"
        )
        assert analyse.nb_articles_croissance == 2
        assert analyse.consommation_max == 50.0


class TestPredictionService:
    """Tests pour PredictionService."""

    @pytest.fixture
    def service(self):
        """Crée une instance du service."""
        from src.services.suggestions import PredictionService
        return PredictionService()

    def test_init_default_min_data_points(self, service):
        """Vérifie min_data_points par défaut."""
        assert service.min_data_points == 3

    def test_analyser_historique_empty(self, service):
        """Historique vide retourne None."""
        result = service.analyser_historique_article(1, [])
        assert result is None

    def test_analyser_historique_insufficient_data(self, service):
        """Données insuffisantes retourne None."""
        historique = [
            {"article_id": 1, "type_modification": "modification_quantite"},
            {"article_id": 1, "type_modification": "modification_quantite"},
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is None

    def test_analyser_historique_wrong_article(self, service):
        """Historique pour autre article retourne None."""
        historique = [
            {"article_id": 2, "type_modification": "modification_quantite"},
            {"article_id": 2, "type_modification": "modification_quantite"},
            {"article_id": 2, "type_modification": "modification_quantite"},
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is None

    def test_analyser_historique_avec_consommation(self, service):
        """Analyse avec données de consommation valides."""
        now = datetime.now()
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
                "date_modification": (now - timedelta(days=3)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 8,
                "quantite_apres": 5,
                "date_modification": (now - timedelta(days=2)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 5,
                "quantite_apres": 3,
                "date_modification": (now - timedelta(days=1)).isoformat(),
            },
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is not None

    def test_analyser_historique_sans_consommation(self, service):
        """Historique sans consommation (ajouts seulement) retourne None."""
        now = datetime.now()
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 5,
                "quantite_apres": 10,  # Ajout (négatif)
                "date_modification": now.isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 15,  # Ajout
                "date_modification": now.isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 15,
                "quantite_apres": 20,  # Ajout
                "date_modification": now.isoformat(),
            },
        ]
        result = service.analyser_historique_article(1, historique)
        # Pas de consommation (que des ajouts), retourne None
        assert result is None
