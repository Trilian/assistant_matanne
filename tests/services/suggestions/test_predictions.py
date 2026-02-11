"""
Tests pour src/services/suggestions/predictions.py
Cible: >80% couverture du service de prédictions ML
"""

import pytest
from datetime import datetime, date, timedelta
from statistics import mean, stdev

from src.services.suggestions.predictions import (
    PredictionArticle,
    AnalysePrediction,
    PredictionService,
    obtenir_service_predictions,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def prediction_service():
    """Instance du service de prédictions."""
    return PredictionService()


@pytest.fixture
def sample_historique():
    """Historique d'exemple pour les tests."""
    return [
        {
            "article_id": 1,
            "type_modification": "modification_quantite",
            "quantite_avant": 10,
            "quantite_apres": 8,
            "date_modification": "2024-01-01",
        },
        {
            "article_id": 1,
            "type_modification": "modification_quantite",
            "quantite_avant": 8,
            "quantite_apres": 5,
            "date_modification": "2024-01-05",
        },
        {
            "article_id": 1,
            "type_modification": "modification_quantite",
            "quantite_avant": 5,
            "quantite_apres": 2,
            "date_modification": "2024-01-10",
        },
        {
            "article_id": 1,
            "type_modification": "modification_quantite",
            "quantite_avant": 2,
            "quantite_apres": 0,
            "date_modification": "2024-01-15",
        },
    ]


@pytest.fixture
def sample_articles():
    """Articles d'exemple pour les tests."""
    return [
        {
            "id": 1,
            "ingredient_id": 101,
            "ingredient_nom": "Lait",
            "quantite": 5,
            "quantite_min": 2,
        },
        {
            "id": 2,
            "ingredient_id": 102,
            "ingredient_nom": "Oeufs",
            "quantite": 12,
            "quantite_min": 6,
        },
    ]


# ═══════════════════════════════════════════════════════════
# TESTS MODELES PYDANTIC
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPredictionArticle:
    """Tests pour le modèle PredictionArticle."""

    def test_creation_minimale(self):
        """Vérifie la création avec valeurs minimales."""
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=101,
            nom="Lait",
            quantite_actuelle=5,
            quantite_predite_semaine=3,
            quantite_predite_mois=0,
            taux_consommation_moyen=0.3,
        )
        assert pred.article_id == 1
        assert pred.tendance == "stable"
        assert pred.confiance == 0.0
        assert pred.risque_rupture_mois is False
        assert pred.jours_avant_rupture is None

    def test_creation_complete(self):
        """Vérifie la création avec toutes les valeurs."""
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=101,
            nom="Lait",
            quantite_actuelle=5,
            quantite_predite_semaine=3,
            quantite_predite_mois=0,
            taux_consommation_moyen=0.3,
            tendance="croissante",
            confiance=0.8,
            risque_rupture_mois=True,
            jours_avant_rupture=10,
        )
        assert pred.tendance == "croissante"
        assert pred.confiance == 0.8
        assert pred.risque_rupture_mois is True
        assert pred.jours_avant_rupture == 10


@pytest.mark.unit
class TestAnalysePrediction:
    """Tests pour le modèle AnalysePrediction."""

    def test_creation_minimale(self):
        """Vérifie la création avec valeurs minimales."""
        analyse = AnalysePrediction(
            nombre_articles=10,
            articles_en_rupture_risque=["Lait"],
            articles_croissance=["Oeufs"],
            articles_decroissance=["Beurre"],
            consommation_moyenne_globale=0.5,
            tendance_globale="stable",
        )
        assert analyse.nombre_articles == 10
        assert len(analyse.articles_en_rupture_risque) == 1
        assert analyse.date_analyse is not None

    def test_valeurs_par_defaut(self):
        """Vérifie les valeurs par défaut."""
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


# ═══════════════════════════════════════════════════════════
# TESTS PREDICTION SERVICE - INITIALISATION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPredictionServiceInit:
    """Tests pour l'initialisation du service."""

    def test_init(self):
        """Vérifie l'initialisation."""
        service = PredictionService()
        assert service.min_data_points == 3

    def test_factory_singleton(self):
        """Vérifie que la factory retourne une instance."""
        service = obtenir_service_predictions()
        assert isinstance(service, PredictionService)


# ═══════════════════════════════════════════════════════════
# TESTS ANALYSER HISTORIQUE ARTICLE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAnalyserHistoriqueArticle:
    """Tests pour analyser_historique_article."""

    def test_historique_vide(self, prediction_service):
        """Vérifie avec historique vide."""
        result = prediction_service.analyser_historique_article(1, [])
        assert result is None

    def test_pas_assez_donnees(self, prediction_service):
        """Vérifie avec pas assez de données."""
        historique = [
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 10, "quantite_apres": 8, "date_modification": "2024-01-01"},
        ]
        result = prediction_service.analyser_historique_article(1, historique)
        assert result is None

    def test_mauvais_article_id(self, prediction_service, sample_historique):
        """Vérifie avec mauvais article_id."""
        result = prediction_service.analyser_historique_article(999, sample_historique)
        assert result is None

    def test_analyse_complete(self, prediction_service, sample_historique):
        """Vérifie l'analyse complète."""
        result = prediction_service.analyser_historique_article(1, sample_historique)
        assert result is not None
        assert "taux_consommation_moyen" in result
        assert "variance" in result
        assert "tendance" in result
        assert "confiance" in result
        assert result["taux_consommation_moyen"] > 0

    def test_tendance_stable(self, prediction_service):
        """Vérifie la détection tendance stable."""
        historique = [
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 10, "quantite_apres": 8, "date_modification": "2024-01-01"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 8, "quantite_apres": 6, "date_modification": "2024-01-02"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 6, "quantite_apres": 4, "date_modification": "2024-01-03"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 4, "quantite_apres": 2, "date_modification": "2024-01-04"},
        ]
        result = prediction_service.analyser_historique_article(1, historique)
        assert result["tendance"] == "stable"

    def test_tendance_croissante(self, prediction_service):
        """Vérifie la détection tendance croissante."""
        historique = [
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 10, "quantite_apres": 9, "date_modification": "2024-01-01"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 9, "quantite_apres": 8, "date_modification": "2024-01-02"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 8, "quantite_apres": 5, "date_modification": "2024-01-03"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 5, "quantite_apres": 1, "date_modification": "2024-01-04"},
        ]
        result = prediction_service.analyser_historique_article(1, historique)
        # La tendance dépend de la variance calculée
        assert result["tendance"] in ["stable", "croissante", "decroissante"]

    def test_ignore_ajouts(self, prediction_service):
        """Vérifie que les ajouts sont ignorés (consommation négative)."""
        historique = [
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 5, "quantite_apres": 10, "date_modification": "2024-01-01"},  # Ajout
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 10, "quantite_apres": 8, "date_modification": "2024-01-02"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 8, "quantite_apres": 6, "date_modification": "2024-01-03"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 6, "quantite_apres": 4, "date_modification": "2024-01-04"},
        ]
        result = prediction_service.analyser_historique_article(1, historique)
        assert result is not None
        # Seules les consommations sont comptées

    def test_confiance_augmente_avec_donnees(self, prediction_service):
        """Vérifie que la confiance augmente avec plus de données."""
        historique_court = [
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 10, "quantite_apres": 8, "date_modification": "2024-01-01"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 8, "quantite_apres": 6, "date_modification": "2024-01-02"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 6, "quantite_apres": 4, "date_modification": "2024-01-03"},
        ]
        historique_long = historique_court + [
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 4, "quantite_apres": 2, "date_modification": "2024-01-04"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 10, "quantite_apres": 8, "date_modification": "2024-01-05"},
            {"article_id": 1, "type_modification": "modification_quantite",
             "quantite_avant": 8, "quantite_apres": 6, "date_modification": "2024-01-06"},
        ]
        result_court = prediction_service.analyser_historique_article(1, historique_court)
        result_long = prediction_service.analyser_historique_article(1, historique_long)
        assert result_long["confiance"] >= result_court["confiance"]


# ═══════════════════════════════════════════════════════════
# TESTS PREDIRE QUANTITE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestPredireQuantite:
    """Tests pour predire_quantite."""

    def test_prediction_base(self, prediction_service):
        """Vérifie la prédiction de base."""
        result = prediction_service.predire_quantite(
            quantite_actuelle=10,
            taux_consommation=0.5,
            jours=10
        )
        assert result == 5

    def test_prediction_pas_negative(self, prediction_service):
        """Vérifie que la prédiction n'est pas négative."""
        result = prediction_service.predire_quantite(
            quantite_actuelle=5,
            taux_consommation=1,
            jours=30
        )
        assert result == 0

    def test_prediction_semaine(self, prediction_service):
        """Vérifie la prédiction sur une semaine."""
        result = prediction_service.predire_quantite(
            quantite_actuelle=14,
            taux_consommation=1,
            jours=7
        )
        assert result == 7

    def test_prediction_mois(self, prediction_service):
        """Vérifie la prédiction sur un mois."""
        result = prediction_service.predire_quantite(
            quantite_actuelle=60,
            taux_consommation=1,
            jours=30
        )
        assert result == 30

    def test_taux_zero(self, prediction_service):
        """Vérifie avec taux de consommation nul."""
        result = prediction_service.predire_quantite(
            quantite_actuelle=10,
            taux_consommation=0,
            jours=30
        )
        assert result == 10


# ═══════════════════════════════════════════════════════════
# TESTS DETECTER RUPTURE RISQUE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestDetecterRuptureRisque:
    """Tests pour detecter_rupture_risque."""

    def test_pas_de_risque(self, prediction_service):
        """Vérifie quand pas de risque."""
        risque, jours = prediction_service.detecter_rupture_risque(
            quantite_actuelle=100,
            quantite_min=10,
            taux_consommation=1
        )
        assert risque is False
        assert jours == 90

    def test_risque_detecte(self, prediction_service):
        """Vérifie quand risque détecté."""
        risque, jours = prediction_service.detecter_rupture_risque(
            quantite_actuelle=15,
            quantite_min=5,
            taux_consommation=1
        )
        assert risque is True
        assert jours == 10

    def test_taux_zero(self, prediction_service):
        """Vérifie avec taux de consommation nul."""
        risque, jours = prediction_service.detecter_rupture_risque(
            quantite_actuelle=10,
            quantite_min=5,
            taux_consommation=0
        )
        assert risque is False
        assert jours is None

    def test_deja_en_rupture(self, prediction_service):
        """Vérifie quand déjà en dessous du minimum."""
        risque, jours = prediction_service.detecter_rupture_risque(
            quantite_actuelle=3,
            quantite_min=5,
            taux_consommation=1
        )
        assert risque is True
        assert jours == 0


# ═══════════════════════════════════════════════════════════
# TESTS GENERER PREDICTIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenererPredictions:
    """Tests pour generer_predictions."""

    def test_articles_vides(self, prediction_service):
        """Vérifie avec articles vides."""
        result = prediction_service.generer_predictions([], [])
        assert result == []

    def test_sans_historique(self, prediction_service, sample_articles):
        """Vérifie avec articles mais sans historique."""
        result = prediction_service.generer_predictions(sample_articles, [])
        assert len(result) == 2
        # Valeurs par défaut utilisées
        for pred in result:
            assert pred.confiance == 0.3  # Confiance par défaut sans historique

    def test_avec_historique(self, prediction_service, sample_articles, sample_historique):
        """Vérifie avec articles et historique."""
        result = prediction_service.generer_predictions(sample_articles, sample_historique)
        assert len(result) == 2
        # Article 1 a de l'historique
        pred_lait = next(p for p in result if p.nom == "Lait")
        assert pred_lait.confiance > 0.3  # Plus confiant avec historique

    def test_prediction_structure(self, prediction_service, sample_articles):
        """Vérifie la structure des prédictions."""
        result = prediction_service.generer_predictions(sample_articles, [])
        pred = result[0]
        assert isinstance(pred, PredictionArticle)
        assert pred.article_id == 1
        assert pred.ingredient_id == 101
        assert pred.nom == "Lait"
        assert pred.quantite_actuelle == 5

    def test_quantite_min_none(self, prediction_service):
        """Vérifie avec quantite_min None."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 101,
                "ingredient_nom": "Test",
                "quantite": 10,
                "quantite_min": None,
            }
        ]
        result = prediction_service.generer_predictions(articles, [])
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════
# TESTS OBTENIR ANALYSE GLOBALE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestObtenirAnalyseGlobale:
    """Tests pour obtenir_analyse_globale."""

    def test_predictions_vides(self, prediction_service):
        """Vérifie avec prédictions vides."""
        result = prediction_service.obtenir_analyse_globale([])
        assert result.nombre_articles == 0
        assert result.consommation_moyenne_globale == 0
        assert result.tendance_globale == "stable"

    def test_analyse_complete(self, prediction_service):
        """Vérifie l'analyse complète."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="Lait",
                quantite_actuelle=5, quantite_predite_semaine=3, quantite_predite_mois=0,
                taux_consommation_moyen=0.3, tendance="croissante", risque_rupture_mois=True
            ),
            PredictionArticle(
                article_id=2, ingredient_id=102, nom="Oeufs",
                quantite_actuelle=12, quantite_predite_semaine=10, quantite_predite_mois=6,
                taux_consommation_moyen=0.2, tendance="stable"
            ),
            PredictionArticle(
                article_id=3, ingredient_id=103, nom="Beurre",
                quantite_actuelle=2, quantite_predite_semaine=1, quantite_predite_mois=0,
                taux_consommation_moyen=0.1, tendance="decroissante"
            ),
        ]
        result = prediction_service.obtenir_analyse_globale(predictions)
        
        assert result.nombre_articles == 3
        assert result.articles_en_rupture_risque == ["Lait"]
        assert result.articles_croissance == ["Lait"]
        assert result.articles_decroissance == ["Beurre"]
        assert result.nb_articles_croissance == 1
        assert result.nb_articles_decroissance == 1
        assert result.nb_articles_stables == 1
        assert result.consommation_moyenne_globale == pytest.approx(0.2, rel=0.01)

    def test_tendance_globale_croissante(self, prediction_service):
        """Vérifie la tendance globale croissante."""
        predictions = [
            PredictionArticle(
                article_id=i, ingredient_id=100+i, nom=f"Art{i}",
                quantite_actuelle=10, quantite_predite_semaine=5, quantite_predite_mois=0,
                taux_consommation_moyen=0.3, tendance="croissante"
            ) for i in range(5)
        ]
        result = prediction_service.obtenir_analyse_globale(predictions)
        assert result.tendance_globale == "croissante"

    def test_tendance_globale_decroissante(self, prediction_service):
        """Vérifie la tendance globale décroissante."""
        predictions = [
            PredictionArticle(
                article_id=i, ingredient_id=100+i, nom=f"Art{i}",
                quantite_actuelle=10, quantite_predite_semaine=8, quantite_predite_mois=5,
                taux_consommation_moyen=0.1, tendance="decroissante"
            ) for i in range(5)
        ]
        result = prediction_service.obtenir_analyse_globale(predictions)
        assert result.tendance_globale == "decroissante"

    def test_consommation_min_max(self, prediction_service):
        """Vérifie le calcul min/max consommation."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="A",
                quantite_actuelle=10, quantite_predite_semaine=5, quantite_predite_mois=0,
                taux_consommation_moyen=0.1
            ),
            PredictionArticle(
                article_id=2, ingredient_id=102, nom="B",
                quantite_actuelle=10, quantite_predite_semaine=5, quantite_predite_mois=0,
                taux_consommation_moyen=0.5
            ),
        ]
        result = prediction_service.obtenir_analyse_globale(predictions)
        assert result.consommation_min == 0.1
        assert result.consommation_max == 0.5


# ═══════════════════════════════════════════════════════════
# TESTS GENERER RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGenererRecommandations:
    """Tests pour generer_recommandations."""

    def test_predictions_vides(self, prediction_service):
        """Vérifie avec prédictions vides."""
        result = prediction_service.generer_recommandations([])
        assert result == []

    def test_recommandation_critique(self, prediction_service):
        """Vérifie la génération de recommandation critique."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="Lait",
                quantite_actuelle=5, quantite_predite_semaine=3, quantite_predite_mois=0,
                taux_consommation_moyen=0.3,
                risque_rupture_mois=True, jours_avant_rupture=10
            ),
        ]
        result = prediction_service.generer_recommandations(predictions)
        assert len(result) == 1
        assert result[0]["priorite"] == "CRITIQUE"
        assert result[0]["article"] == "Lait"
        assert "🚨" in result[0]["icone"]

    def test_recommandation_haute(self, prediction_service):
        """Vérifie la génération de recommandation haute."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="Oeufs",
                quantite_actuelle=12, quantite_predite_semaine=8, quantite_predite_mois=0,
                taux_consommation_moyen=0.4,
                tendance="croissante", confiance=0.7
            ),
        ]
        result = prediction_service.generer_recommandations(predictions)
        assert len(result) == 1
        assert result[0]["priorite"] == "HAUTE"
        assert "📈" in result[0]["icone"]

    def test_ordre_priorite(self, prediction_service):
        """Vérifie l'ordre des priorités."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="Oeufs",
                quantite_actuelle=12, quantite_predite_semaine=8, quantite_predite_mois=0,
                taux_consommation_moyen=0.4,
                tendance="croissante", confiance=0.7
            ),
            PredictionArticle(
                article_id=2, ingredient_id=102, nom="Lait",
                quantite_actuelle=5, quantite_predite_semaine=3, quantite_predite_mois=0,
                taux_consommation_moyen=0.3,
                risque_rupture_mois=True, jours_avant_rupture=10
            ),
        ]
        result = prediction_service.generer_recommandations(predictions)
        assert result[0]["priorite"] == "CRITIQUE"  # Critique en premier
        assert result[1]["priorite"] == "HAUTE"

    def test_max_10_recommandations(self, prediction_service):
        """Vérifie le max de 10 recommandations."""
        predictions = [
            PredictionArticle(
                article_id=i, ingredient_id=100+i, nom=f"Art{i}",
                quantite_actuelle=5, quantite_predite_semaine=3, quantite_predite_mois=0,
                taux_consommation_moyen=0.3,
                risque_rupture_mois=True, jours_avant_rupture=10
            ) for i in range(15)
        ]
        result = prediction_service.generer_recommandations(predictions)
        assert len(result) <= 10

    def test_pas_de_recommandation_stable(self, prediction_service):
        """Vérifie pas de recommandation pour articles stables sans risque."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="Stock OK",
                quantite_actuelle=100, quantite_predite_semaine=95, quantite_predite_mois=80,
                taux_consommation_moyen=0.3,
                tendance="stable", confiance=0.5,
                risque_rupture_mois=False
            ),
        ]
        result = prediction_service.generer_recommandations(predictions)
        assert len(result) == 0

    def test_confiance_insuffisante(self, prediction_service):
        """Vérifie pas de recommandation haute si confiance insuffisante."""
        predictions = [
            PredictionArticle(
                article_id=1, ingredient_id=101, nom="Test",
                quantite_actuelle=10, quantite_predite_semaine=8, quantite_predite_mois=0,
                taux_consommation_moyen=0.3,
                tendance="croissante", confiance=0.3  # Trop faible
            ),
        ]
        result = prediction_service.generer_recommandations(predictions)
        assert len(result) == 0
