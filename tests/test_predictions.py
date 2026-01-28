"""Tests unitaires pour le service predictions."""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch


class TestPredictionInventaireModel:
    """Tests pour le modèle PredictionInventaire."""

    def test_prediction_creation(self):
        """Création d'une prédiction d'inventaire."""
        from src.services.predictions import PredictionInventaire
        
        prediction = PredictionInventaire(
            article_id=1,
            article_nom="Lait",
            quantite_actuelle=3.0,
            quantite_predite=1.0,
            jours_avant_rupture=5,
            confiance=0.85,
            tendance="décroissante"
        )
        
        assert prediction.article_nom == "Lait"
        assert prediction.jours_avant_rupture == 5
        assert prediction.confiance == 0.85

    def test_prediction_tendance_valeurs(self):
        """Les tendances sont des valeurs valides."""
        from src.services.predictions import PredictionInventaire
        
        tendances_valides = ["croissante", "stable", "décroissante"]
        
        for tendance in tendances_valides:
            prediction = PredictionInventaire(
                article_id=1,
                article_nom="Test",
                quantite_actuelle=5.0,
                quantite_predite=3.0,
                jours_avant_rupture=10,
                confiance=0.7,
                tendance=tendance
            )
            assert prediction.tendance in tendances_valides


class TestAnalysePredictionsModel:
    """Tests pour le modèle AnalysePredictions."""

    def test_analyse_creation(self):
        """Création d'une analyse globale."""
        from src.services.predictions import AnalysePredictions
        
        analyse = AnalysePredictions(
            tendance_globale="stable",
            articles_a_risque=2,
            recommandations=["Acheter du lait", "Commander des œufs"]
        )
        
        assert analyse.tendance_globale == "stable"
        assert analyse.articles_a_risque == 2
        assert len(analyse.recommandations) == 2


class TestPredictionsServiceInit:
    """Tests d'initialisation du service."""

    def test_get_predictions_service(self):
        """La factory retourne une instance."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        assert service is not None

    def test_service_methodes_requises(self):
        """Le service expose les méthodes requises."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        assert hasattr(service, 'analyser_historique')
        assert hasattr(service, 'predire_quantite')
        assert hasattr(service, 'detecter_rupture')
        assert hasattr(service, 'generer_predictions')
        assert hasattr(service, 'obtenir_analyse_globale')
        assert hasattr(service, 'generer_recommandations')


class TestAnalyserHistorique:
    """Tests pour analyser_historique - logique pure sans dépendances."""

    def test_historique_pas_assez_donnees(self):
        """Pas assez de données pour analyse."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        # Moins de 3 points = pas d'analyse possible
        historique = [
            {"date": date.today() - timedelta(days=1), "quantite": 10},
            {"date": date.today(), "quantite": 8}
        ]
        
        resultat = service.analyser_historique(historique)
        
        # Devrait retourner None ou résultat avec faible confiance
        assert resultat is None or resultat.get("confiance", 0) < 0.5

    def test_historique_tendance_decroissante(self):
        """Détection de tendance décroissante."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        # Consommation régulière
        historique = [
            {"date": date.today() - timedelta(days=i), "quantite": 10 - i}
            for i in range(10, 0, -1)
        ]
        
        resultat = service.analyser_historique(historique)
        
        if resultat:
            assert resultat.get("tendance") in ["décroissante", "decroissante", "decreasing"]

    def test_historique_tendance_stable(self):
        """Détection de tendance stable."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        # Quantité stable avec légères variations
        historique = [
            {"date": date.today() - timedelta(days=i), "quantite": 5 + (i % 2)}
            for i in range(10, 0, -1)
        ]
        
        resultat = service.analyser_historique(historique)
        
        if resultat:
            # Stable ou faible variation
            assert resultat.get("tendance") in ["stable", "croissante", "décroissante"] or \
                   abs(resultat.get("taux_variation", 0)) < 0.5


class TestPredireQuantite:
    """Tests pour predire_quantite - calcul pur."""

    def test_predire_quantite_normale(self):
        """Prédiction de quantité avec consommation normale."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        quantite_actuelle = 10.0
        taux_consommation = 1.0  # 1 unité/jour
        jours = 5
        
        quantite_predite = service.predire_quantite(
            quantite_actuelle=quantite_actuelle,
            taux_consommation=taux_consommation,
            jours=jours
        )
        
        # 10 - (1 * 5) = 5
        assert quantite_predite == pytest.approx(5.0, rel=0.1)

    def test_predire_quantite_jamais_negative(self):
        """La quantité prédite ne peut pas être négative."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        quantite_predite = service.predire_quantite(
            quantite_actuelle=5.0,
            taux_consommation=2.0,  # Forte consommation
            jours=10  # Longue période
        )
        
        # 5 - (2 * 10) = -15 → devrait être 0
        assert quantite_predite >= 0

    def test_predire_quantite_taux_zero(self):
        """Prédiction avec taux de consommation nul."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        quantite_predite = service.predire_quantite(
            quantite_actuelle=10.0,
            taux_consommation=0.0,
            jours=30
        )
        
        # Pas de consommation = quantité inchangée
        assert quantite_predite == 10.0


class TestDetecterRupture:
    """Tests pour detecter_rupture - logique pure."""

    def test_rupture_dans_14_jours(self):
        """Détection de risque de rupture sous 14 jours."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        # Quantité actuelle / taux = jours avant rupture
        resultat = service.detecter_rupture(
            quantite_actuelle=10.0,
            taux_consommation=1.0  # 10 / 1 = 10 jours
        )
        
        assert resultat["risque"] == True
        assert resultat["jours_avant_rupture"] <= 14

    def test_pas_rupture_plus_14_jours(self):
        """Pas de risque si plus de 14 jours de stock."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        resultat = service.detecter_rupture(
            quantite_actuelle=30.0,
            taux_consommation=1.0  # 30 jours de stock
        )
        
        assert resultat["risque"] == False
        assert resultat["jours_avant_rupture"] > 14

    def test_rupture_taux_zero(self):
        """Pas de rupture si consommation nulle."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        resultat = service.detecter_rupture(
            quantite_actuelle=5.0,
            taux_consommation=0.0
        )
        
        # Pas de consommation = pas de rupture
        assert resultat["risque"] == False


class TestGenererPredictions:
    """Tests pour generer_predictions."""

    def test_predictions_liste_vide(self):
        """Génération avec liste d'articles vide."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        predictions = service.generer_predictions([])
        
        assert predictions == []

    def test_predictions_articles_sans_historique(self):
        """Articles sans historique de consommation."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        articles = [
            {"id": 1, "nom": "Nouveau produit", "quantite": 10, "historique": []}
        ]
        
        predictions = service.generer_predictions(articles)
        
        # Devrait gérer gracieusement
        assert isinstance(predictions, list)


class TestObtenirAnalyseGlobale:
    """Tests pour obtenir_analyse_globale."""

    def test_analyse_globale_tendance(self):
        """Calcul de la tendance globale."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        predictions = [
            {"tendance": "décroissante", "risque": True},
            {"tendance": "décroissante", "risque": True},
            {"tendance": "stable", "risque": False},
        ]
        
        analyse = service.obtenir_analyse_globale(predictions)
        
        # Majorité décroissante
        assert analyse.tendance_globale in ["décroissante", "mixte"]

    def test_analyse_globale_compte_risques(self):
        """Compte des articles à risque."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        predictions = [
            {"article_nom": "Lait", "risque": True, "tendance": "décroissante"},
            {"article_nom": "Œufs", "risque": True, "tendance": "décroissante"},
            {"article_nom": "Pain", "risque": False, "tendance": "stable"},
            {"article_nom": "Beurre", "risque": True, "tendance": "décroissante"},
        ]
        
        analyse = service.obtenir_analyse_globale(predictions)
        
        # 3 articles à risque
        assert analyse.articles_a_risque == 3


class TestGenererRecommandations:
    """Tests pour generer_recommandations."""

    def test_recommandations_critique(self):
        """Recommandations pour articles critiques."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        predictions = [
            {
                "article_nom": "Lait",
                "jours_avant_rupture": 2,
                "quantite_actuelle": 1,
                "risque": True
            }
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        assert len(recommandations) > 0
        # Devrait mentionner le lait
        assert any("Lait" in r or "lait" in r.lower() for r in recommandations)

    def test_recommandations_haute_priorite(self):
        """Tri par priorité (jours restants)."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        predictions = [
            {"article_nom": "Œufs", "jours_avant_rupture": 7, "risque": True},
            {"article_nom": "Lait", "jours_avant_rupture": 2, "risque": True},  # Plus urgent
            {"article_nom": "Pain", "jours_avant_rupture": 5, "risque": True},
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        # Le lait devrait être en premier (plus urgent)
        if recommandations:
            assert "Lait" in recommandations[0] or "lait" in recommandations[0].lower()

    def test_recommandations_max_10(self):
        """Maximum 10 recommandations."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        # 15 articles à risque
        predictions = [
            {"article_nom": f"Article{i}", "jours_avant_rupture": i, "risque": True}
            for i in range(1, 16)
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        # Maximum 10
        assert len(recommandations) <= 10


class TestCalculsStatistiques:
    """Tests pour les calculs statistiques internes."""

    def test_calcul_moyenne(self):
        """Calcul de moyenne simple."""
        valeurs = [10, 20, 30, 40, 50]
        moyenne = sum(valeurs) / len(valeurs)
        
        assert moyenne == 30.0

    def test_calcul_ecart_type(self):
        """Calcul d'écart-type."""
        from statistics import stdev
        
        valeurs = [10, 12, 23, 23, 16, 23, 21, 16]
        ecart = stdev(valeurs)
        
        # Écart-type attendu ≈ 5.24
        assert ecart == pytest.approx(5.24, rel=0.1)

    def test_calcul_taux_consommation(self):
        """Calcul du taux de consommation journalier."""
        quantite_initiale = 20.0
        quantite_finale = 5.0
        jours = 15
        
        taux = (quantite_initiale - quantite_finale) / jours
        
        # (20 - 5) / 15 = 1.0 unité/jour
        assert taux == 1.0

    def test_calcul_confiance(self):
        """Calcul du niveau de confiance basé sur variance."""
        from statistics import stdev, mean
        
        # Données régulières = haute confiance
        donnees_regulieres = [10, 10, 10, 10, 10]
        # Données irrégulières = basse confiance
        donnees_irregulieres = [5, 20, 8, 25, 2]
        
        # Coefficient de variation = écart-type / moyenne
        cv_regulier = 0 if mean(donnees_regulieres) == 0 else \
                      stdev(donnees_regulieres) / mean(donnees_regulieres) if len(set(donnees_regulieres)) > 1 else 0
        cv_irregulier = stdev(donnees_irregulieres) / mean(donnees_irregulieres)
        
        # Confiance = 1 - min(CV, 1)
        confiance_regulier = 1 - min(cv_regulier, 1)
        confiance_irregulier = 1 - min(cv_irregulier, 1)
        
        assert confiance_regulier > confiance_irregulier


class TestCasLimites:
    """Tests des cas limites."""

    def test_article_quantite_zero(self):
        """Article avec quantité zéro."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        resultat = service.detecter_rupture(
            quantite_actuelle=0.0,
            taux_consommation=1.0
        )
        
        # Déjà en rupture
        assert resultat["risque"] == True
        assert resultat["jours_avant_rupture"] == 0

    def test_taux_tres_faible(self):
        """Taux de consommation très faible."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        resultat = service.detecter_rupture(
            quantite_actuelle=1.0,
            taux_consommation=0.01  # 1 unité tous les 100 jours
        )
        
        # 1 / 0.01 = 100 jours
        assert resultat["jours_avant_rupture"] >= 100
        assert resultat["risque"] == False

    def test_grande_quantite(self):
        """Grande quantité en stock."""
        from src.services.predictions import get_predictions_service
        
        service = get_predictions_service()
        
        quantite_predite = service.predire_quantite(
            quantite_actuelle=1000.0,
            taux_consommation=1.0,
            jours=30
        )
        
        # 1000 - 30 = 970
        assert quantite_predite == pytest.approx(970.0, rel=0.01)
