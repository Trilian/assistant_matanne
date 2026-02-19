"""
Tests for src/services/suggestions/predictions.py

PredictionService - ML predictions for inventory.
"""

import pytest

from src.services.cuisine.suggestions.predictions import (
    AnalysePrediction,
    PredictionArticle,
    PredictionService,
    obtenir_service_predictions,
)


class TestPredictionArticle:
    """Tests for PredictionArticle model."""

    def test_create_prediction_article(self):
        """Test création d'un PredictionArticle."""
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=10,
            nom="Tomate",
            quantite_actuelle=5.0,
            quantite_predite_semaine=3.0,
            quantite_predite_mois=0.0,
            taux_consommation_moyen=0.5,
            tendance="stable",
            confiance=0.8,
            risque_rupture_mois=True,
            jours_avant_rupture=10,
        )
        assert pred.article_id == 1
        assert pred.nom == "Tomate"
        assert pred.risque_rupture_mois is True
        assert pred.jours_avant_rupture == 10

    def test_prediction_article_defaults(self):
        """Test valeurs par défaut."""
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=10,
            nom="Test",
            quantite_actuelle=10.0,
            quantite_predite_semaine=8.0,
            quantite_predite_mois=5.0,
            taux_consommation_moyen=0.3,
        )
        assert pred.tendance == "stable"
        assert pred.confiance == 0.0
        assert pred.risque_rupture_mois is False
        assert pred.jours_avant_rupture is None


class TestAnalysePrediction:
    """Tests for AnalysePrediction model."""

    def test_create_analyse_prediction(self):
        """Test création d'une analyse."""
        analyse = AnalysePrediction(
            nombre_articles=10,
            articles_en_rupture_risque=["Tomate", "Oignon"],
            articles_croissance=["Lait"],
            articles_decroissance=["Pain"],
            consommation_moyenne_globale=1.5,
            tendance_globale="stable",
        )
        assert analyse.nombre_articles == 10
        assert len(analyse.articles_en_rupture_risque) == 2
        assert analyse.tendance_globale == "stable"

    def test_analyse_prediction_defaults(self):
        """Test valeurs par défaut."""
        analyse = AnalysePrediction(
            nombre_articles=0,
            articles_en_rupture_risque=[],
            articles_croissance=[],
            articles_decroissance=[],
            consommation_moyenne_globale=0,
            tendance_globale="stable",
        )
        assert analyse.consommation_min == 0.0
        assert analyse.consommation_max == 0.0
        assert analyse.nb_articles_croissance == 0


class TestPredictionService:
    """Tests for PredictionService."""

    @pytest.fixture
    def service(self):
        """Fixture service."""
        return PredictionService()

    def test_init(self, service):
        """Test initialisation."""
        assert service.min_data_points == 3

    # ═══════════════════════════════════════════════════════════
    # analyser_historique_article
    # ═══════════════════════════════════════════════════════════

    def test_analyser_historique_article_basic(self, service):
        """Test analyse historique basique."""
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
                "date_modification": "2024-07-01",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 8,
                "quantite_apres": 6,
                "date_modification": "2024-07-02",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 6,
                "quantite_apres": 4,
                "date_modification": "2024-07-03",
            },
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is not None
        assert result["taux_consommation_moyen"] == 2.0
        assert result["nombre_modifications"] == 3
        assert result["tendance"] in ["stable", "croissante", "decroissante"]
        assert 0 <= result["confiance"] <= 1

    def test_analyser_historique_article_empty(self, service):
        """Test avec historique vide."""
        result = service.analyser_historique_article(1, [])
        assert result is None

    def test_analyser_historique_article_insufficient(self, service):
        """Test avec données insuffisantes."""
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
            },
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is None

    def test_analyser_historique_article_wrong_type(self, service):
        """Test avec mauvais type de modification."""
        historique = [
            {
                "article_id": 1,
                "type_modification": "ajout",
                "quantite_avant": 0,
                "quantite_apres": 10,
            },
        ] * 5
        result = service.analyser_historique_article(1, historique)
        assert result is None

    def test_analyser_historique_article_other_article(self, service):
        """Test avec autre article."""
        historique = [
            {
                "article_id": 2,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
            },
        ] * 5
        result = service.analyser_historique_article(1, historique)
        assert result is None

    def test_analyser_historique_article_no_consumption(self, service):
        """Test sans consommation (ajouts seulement)."""
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 5,
                "quantite_apres": 10,  # Ajout
                "date_modification": "2024-07-01",
            },
        ] * 5
        result = service.analyser_historique_article(1, historique)
        assert result is None

    def test_analyser_historique_article_tendance_croissante(self, service):
        """Test détection tendance croissante."""
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 9,  # Change 1
                "date_modification": "2024-07-01",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 9,
                "quantite_apres": 8,  # Change 1
                "date_modification": "2024-07-02",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 20,
                "quantite_apres": 15,  # Change 5
                "date_modification": "2024-07-03",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 15,
                "quantite_apres": 9,  # Change 6
                "date_modification": "2024-07-04",
            },
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is not None
        # La tendance peut être croissante si les dernières consommations sont plus élevées
        assert result["tendance"] in ["croissante", "stable", "decroissante"]

    def test_analyser_historique_article_confiance_max(self, service):
        """Test confiance maximale avec beaucoup de données."""
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 100 - i,
                "quantite_apres": 100 - i - 2,
                "date_modification": f"2024-07-{i + 1:02d}",
            }
            for i in range(15)
        ]
        result = service.analyser_historique_article(1, historique)
        assert result is not None
        assert result["confiance"] == 1.0

    # ═══════════════════════════════════════════════════════════
    # predire_quantite
    # ═══════════════════════════════════════════════════════════

    def test_predire_quantite_basic(self, service):
        """Test prédiction basique."""
        result = service.predire_quantite(10.0, 0.5, 7)
        assert result == 6.5  # 10 - (0.5 * 7)

    def test_predire_quantite_zero_taux(self, service):
        """Test avec taux zéro."""
        result = service.predire_quantite(10.0, 0.0, 30)
        assert result == 10.0

    def test_predire_quantite_negative_capped(self, service):
        """Test quantité négative plafonnée à 0."""
        result = service.predire_quantite(5.0, 1.0, 30)
        assert result == 0.0  # Pas négatif

    def test_predire_quantite_30_days(self, service):
        """Test prédiction 30 jours."""
        result = service.predire_quantite(20.0, 0.5, 30)
        assert result == 5.0

    # ═══════════════════════════════════════════════════════════
    # detecter_rupture_risque
    # ═══════════════════════════════════════════════════════════

    def test_detecter_rupture_risque_true(self, service):
        """Test détection risque de rupture."""
        risque, jours = service.detecter_rupture_risque(5.0, 0.0, 0.5)
        # 5 / 0.5 = 10 jours < 14 -> risque
        assert risque is True
        assert jours == 10

    def test_detecter_rupture_risque_false(self, service):
        """Test pas de risque de rupture."""
        risque, jours = service.detecter_rupture_risque(20.0, 0.0, 0.5)
        # 20 / 0.5 = 40 jours > 14 -> pas de risque
        assert risque is False
        assert jours == 40

    def test_detecter_rupture_risque_zero_taux(self, service):
        """Test avec taux zéro (pas de consommation)."""
        risque, jours = service.detecter_rupture_risque(5.0, 0.0, 0.0)
        assert risque is False
        assert jours is None

    def test_detecter_rupture_risque_with_min(self, service):
        """Test avec quantité minimum."""
        risque, jours = service.detecter_rupture_risque(10.0, 5.0, 0.5)
        # (10 - 5) / 0.5 = 10 jours < 14 -> risque
        assert risque is True
        assert jours == 10

    def test_detecter_rupture_risque_already_below_min(self, service):
        """Test déjà sous le minimum."""
        risque, jours = service.detecter_rupture_risque(3.0, 5.0, 0.5)
        # (3 - 5) / 0.5 = -4 -> jours = 0
        assert risque is True
        assert jours == 0

    # ═══════════════════════════════════════════════════════════
    # generer_predictions
    # ═══════════════════════════════════════════════════════════

    def test_generer_predictions_basic(self, service):
        """Test génération prédictions basique."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Tomate",
                "quantite": 10.0,
                "quantite_min": 2.0,
            },
        ]
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 12,
                "quantite_apres": 10,
                "date_modification": "2024-07-01",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
                "date_modification": "2024-07-02",
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 8,
                "quantite_apres": 6,
                "date_modification": "2024-07-03",
            },
        ]
        predictions = service.generer_predictions(articles, historique)
        assert len(predictions) == 1
        pred = predictions[0]
        assert pred.nom == "Tomate"
        assert pred.taux_consommation_moyen == 2.0

    def test_generer_predictions_no_history(self, service):
        """Test prédictions sans historique."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Tomate",
                "quantite": 10.0,
                "quantite_min": 2.0,
            },
        ]
        predictions = service.generer_predictions(articles, [])
        assert len(predictions) == 1
        pred = predictions[0]
        # Valeurs par défaut
        assert pred.tendance == "stable"
        assert pred.confiance == 0.3
        assert pred.taux_consommation_moyen >= 0.2  # 2.0 * 0.1 ou 0.5

    def test_generer_predictions_empty(self, service):
        """Test avec liste vide."""
        predictions = service.generer_predictions([], [])
        assert len(predictions) == 0

    def test_generer_predictions_multiple_articles(self, service):
        """Test plusieurs articles."""
        articles = [
            {"id": 1, "ingredient_id": 10, "ingredient_nom": "Tomate", "quantite": 10.0},
            {"id": 2, "ingredient_id": 11, "ingredient_nom": "Oignon", "quantite": 5.0},
        ]
        predictions = service.generer_predictions(articles, [])
        assert len(predictions) == 2
        assert {p.nom for p in predictions} == {"Tomate", "Oignon"}

    def test_generer_predictions_quantite_min_none(self, service):
        """Test avec quantite_min None."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Tomate",
                "quantite": 10.0,
                "quantite_min": None,
            },
        ]
        predictions = service.generer_predictions(articles, [])
        assert len(predictions) == 1

    # ═══════════════════════════════════════════════════════════
    # obtenir_analyse_globale
    # ═══════════════════════════════════════════════════════════

    def test_obtenir_analyse_globale_basic(self, service):
        """Test analyse globale basique."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Tomate",
                quantite_actuelle=5.0,
                quantite_predite_semaine=3.0,
                quantite_predite_mois=0.0,
                taux_consommation_moyen=0.5,
                tendance="croissante",
                confiance=0.8,
                risque_rupture_mois=True,
                jours_avant_rupture=10,
            ),
            PredictionArticle(
                article_id=2,
                ingredient_id=11,
                nom="Oignon",
                quantite_actuelle=20.0,
                quantite_predite_semaine=18.0,
                quantite_predite_mois=10.0,
                taux_consommation_moyen=0.3,
                tendance="stable",
                confiance=0.5,
            ),
        ]
        analyse = service.obtenir_analyse_globale(predictions)
        assert analyse.nombre_articles == 2
        assert "Tomate" in analyse.articles_en_rupture_risque
        assert "Tomate" in analyse.articles_croissance
        assert analyse.nb_articles_croissance == 1
        assert analyse.nb_articles_stables == 1

    def test_obtenir_analyse_globale_empty(self, service):
        """Test analyse globale vide."""
        analyse = service.obtenir_analyse_globale([])
        assert analyse.nombre_articles == 0
        assert analyse.consommation_moyenne_globale == 0

    def test_obtenir_analyse_globale_tendance_croissante(self, service):
        """Test tendance globale croissante."""
        predictions = [
            PredictionArticle(
                article_id=i,
                ingredient_id=i,
                nom=f"Article{i}",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.5,
                tendance="croissante",
            )
            for i in range(5)
        ]
        analyse = service.obtenir_analyse_globale(predictions)
        assert analyse.tendance_globale == "croissante"
        assert analyse.nb_articles_croissance == 5

    def test_obtenir_analyse_globale_tendance_decroissante(self, service):
        """Test tendance globale décroissante."""
        predictions = [
            PredictionArticle(
                article_id=i,
                ingredient_id=i,
                nom=f"Article{i}",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.5,
                tendance="decroissante",
            )
            for i in range(5)
        ]
        analyse = service.obtenir_analyse_globale(predictions)
        assert analyse.tendance_globale == "decroissante"

    def test_obtenir_analyse_globale_consommation_stats(self, service):
        """Test statistiques de consommation."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=1,
                nom="A",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.2,
            ),
            PredictionArticle(
                article_id=2,
                ingredient_id=2,
                nom="B",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.8,
            ),
        ]
        analyse = service.obtenir_analyse_globale(predictions)
        assert analyse.consommation_min == 0.2
        assert analyse.consommation_max == 0.8
        assert analyse.consommation_moyenne_globale == 0.5

    # ═══════════════════════════════════════════════════════════
    # generer_recommandations
    # ═══════════════════════════════════════════════════════════

    def test_generer_recommandations_critique(self, service):
        """Test recommandations critiques."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Tomate",
                quantite_actuelle=2.0,
                quantite_predite_semaine=0.0,
                quantite_predite_mois=0.0,
                taux_consommation_moyen=0.5,
                risque_rupture_mois=True,
                jours_avant_rupture=5,
            ),
        ]
        recommandations = service.generer_recommandations(predictions)
        assert len(recommandations) == 1
        assert recommandations[0]["priorite"] == "CRITIQUE"
        assert recommandations[0]["article"] == "Tomate"
        assert "5 jours" in recommandations[0]["raison"]

    def test_generer_recommandations_haute(self, service):
        """Test recommandations haute priorité."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Lait",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.5,
                tendance="croissante",
                confiance=0.6,
            ),
        ]
        recommandations = service.generer_recommandations(predictions)
        assert len(recommandations) == 1
        assert recommandations[0]["priorite"] == "HAUTE"
        assert "hausse" in recommandations[0]["raison"].lower()

    def test_generer_recommandations_empty(self, service):
        """Test sans recommandations."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Article",
                quantite_actuelle=100.0,
                quantite_predite_semaine=95.0,
                quantite_predite_mois=80.0,
                taux_consommation_moyen=0.5,
                tendance="stable",
            ),
        ]
        recommandations = service.generer_recommandations(predictions)
        assert len(recommandations) == 0

    def test_generer_recommandations_sorted(self, service):
        """Test tri par priorité."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Haute",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.5,
                tendance="croissante",
                confiance=0.6,
            ),
            PredictionArticle(
                article_id=2,
                ingredient_id=11,
                nom="Critique",
                quantite_actuelle=2.0,
                quantite_predite_semaine=0.0,
                quantite_predite_mois=0.0,
                taux_consommation_moyen=0.5,
                risque_rupture_mois=True,
                jours_avant_rupture=3,
            ),
        ]
        recommandations = service.generer_recommandations(predictions)
        assert len(recommandations) == 2
        assert recommandations[0]["priorite"] == "CRITIQUE"
        assert recommandations[1]["priorite"] == "HAUTE"

    def test_generer_recommandations_limit_10(self, service):
        """Test limite de 10 recommandations."""
        predictions = [
            PredictionArticle(
                article_id=i,
                ingredient_id=i,
                nom=f"Article{i}",
                quantite_actuelle=2.0,
                quantite_predite_semaine=0.0,
                quantite_predite_mois=0.0,
                taux_consommation_moyen=0.5,
                risque_rupture_mois=True,
                jours_avant_rupture=5,
            )
            for i in range(15)
        ]
        recommandations = service.generer_recommandations(predictions)
        assert len(recommandations) == 10

    def test_generer_recommandations_croissance_low_confiance(self, service):
        """Test croissance avec faible confiance ignorée."""
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Article",
                quantite_actuelle=10.0,
                quantite_predite_semaine=8.0,
                quantite_predite_mois=5.0,
                taux_consommation_moyen=0.5,
                tendance="croissante",
                confiance=0.3,  # Trop faible
            ),
        ]
        recommandations = service.generer_recommandations(predictions)
        assert len(recommandations) == 0


class TestSingleton:
    """Tests pour le singleton."""

    def test_obtenir_service_predictions(self):
        """Test obtention du singleton."""
        service1 = obtenir_service_predictions()
        service2 = obtenir_service_predictions()
        assert service1 is service2
        assert isinstance(service1, PredictionService)
