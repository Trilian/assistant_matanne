"""
Tests complets pour src/services/predictions.py
Objectif: Atteindre 80%+ de couverture

Tests couvrant:
- analyser_historique_article avec diffÃ©rentes tendances
- predire_quantite avec valeurs positives/nÃ©gatives
- detecter_rupture_risque avec diffÃ©rents scÃ©narios
- generer_predictions avec/sans historique
- obtenir_analyse_globale avec prÃ©dictions mixtes
- generer_recommandations avec articles critiques/croissants
"""
import pytest
from datetime import datetime, timedelta
from statistics import mean


class TestPredictionServiceMethods:
    """Tests des mÃ©thodes principales de PredictionService."""

    @pytest.fixture
    def service(self):
        """CrÃ©e une instance du service."""
        from src.services.predictions import PredictionService
        return PredictionService()

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TESTS analyser_historique_article
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def test_analyser_historique_tendance_stable(self, service):
        """Historique avec consommation stable."""
        now = datetime.now()
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
                "date_modification": (now - timedelta(days=5)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 8,
                "quantite_apres": 6,
                "date_modification": (now - timedelta(days=3)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 6,
                "quantite_apres": 4,
                "date_modification": (now - timedelta(days=1)).isoformat(),
            },
        ]
        result = service.analyser_historique_article(1, historique)
        
        assert result is not None
        assert result["tendance"] == "stable"
        assert result["taux_consommation_moyen"] == 2.0

    def test_analyser_historique_tendance_croissante(self, service):
        """Historique avec consommation en hausse."""
        now = datetime.now()
        # Consommation qui augmente: 1, 2, 3, 4, 5, 6
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 20,
                "quantite_apres": 19,  # -1
                "date_modification": (now - timedelta(days=10)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 19,
                "quantite_apres": 17,  # -2
                "date_modification": (now - timedelta(days=8)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 17,
                "quantite_apres": 14,  # -3
                "date_modification": (now - timedelta(days=6)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 14,
                "quantite_apres": 10,  # -4
                "date_modification": (now - timedelta(days=4)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 5,  # -5
                "date_modification": (now - timedelta(days=2)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 5,
                "quantite_apres": -1,  # -6
                "date_modification": (now - timedelta(days=1)).isoformat(),
            },
        ]
        result = service.analyser_historique_article(1, historique)
        
        assert result is not None
        assert result["tendance"] == "croissante"
        assert result["taux_consommation_moyen"] > 0

    def test_analyser_historique_tendance_decroissante(self, service):
        """Historique avec consommation en baisse."""
        now = datetime.now()
        # Consommation qui diminue: 6, 5, 4, 3, 2, 1
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 50,
                "quantite_apres": 44,  # -6
                "date_modification": (now - timedelta(days=6)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 44,
                "quantite_apres": 39,  # -5
                "date_modification": (now - timedelta(days=5)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 39,
                "quantite_apres": 35,  # -4
                "date_modification": (now - timedelta(days=4)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 35,
                "quantite_apres": 32,  # -3
                "date_modification": (now - timedelta(days=3)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 32,
                "quantite_apres": 30,  # -2
                "date_modification": (now - timedelta(days=2)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 30,
                "quantite_apres": 29,  # -1
                "date_modification": (now - timedelta(days=1)).isoformat(),
            },
        ]
        result = service.analyser_historique_article(1, historique)
        
        assert result is not None
        assert result["tendance"] == "decroissante"

    def test_analyser_historique_confiance_calculation(self, service):
        """VÃ©rifie le calcul de confiance basÃ© sur le nombre de points."""
        now = datetime.now()
        # 5 points â†’ confiance = 0.5
        historique = []
        for i in range(5):
            historique.append({
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 30 - i * 2,
                "quantite_apres": 28 - i * 2,
                "date_modification": (now - timedelta(days=5 - i)).isoformat(),
            })
        
        result = service.analyser_historique_article(1, historique)
        
        assert result is not None
        assert result["confiance"] == 0.5  # 5/10

    def test_analyser_historique_confiance_max(self, service):
        """Confiance plafonnÃ©e Ã  1.0."""
        now = datetime.now()
        # 15 points â†’ confiance = min(1.0, 15/10) = 1.0
        historique = []
        for i in range(15):
            historique.append({
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 50 - i * 2,
                "quantite_apres": 48 - i * 2,
                "date_modification": (now - timedelta(days=15 - i)).isoformat(),
            })
        
        result = service.analyser_historique_article(1, historique)
        
        assert result is not None
        assert result["confiance"] == 1.0

    def test_analyser_historique_mixed_types(self, service):
        """Filtre les types de modification non pertinents."""
        now = datetime.now()
        historique = [
            # Modification quantitÃ© (valide)
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 8,
                "date_modification": (now - timedelta(days=3)).isoformat(),
            },
            # Autre type (ignorÃ©)
            {
                "article_id": 1,
                "type_modification": "ajout",
                "quantite_avant": 0,
                "quantite_apres": 20,
                "date_modification": (now - timedelta(days=2)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 8,
                "quantite_apres": 6,
                "date_modification": (now - timedelta(days=2)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 6,
                "quantite_apres": 4,
                "date_modification": (now - timedelta(days=1)).isoformat(),
            },
        ]
        result = service.analyser_historique_article(1, historique)
        
        assert result is not None
        assert result["nombre_modifications"] == 3  # Seulement les modifications_quantite avec consommation

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TESTS predire_quantite
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def test_predire_quantite_normal(self, service):
        """PrÃ©diction normale avec stock suffisant."""
        result = service.predire_quantite(
            quantite_actuelle=100,
            taux_consommation=2.0,
            jours=30
        )
        # 100 - (2 * 30) = 100 - 60 = 40
        assert result == 40

    def test_predire_quantite_negative_returns_zero(self, service):
        """PrÃ©diction nÃ©gative retourne 0."""
        result = service.predire_quantite(
            quantite_actuelle=10,
            taux_consommation=5.0,
            jours=30
        )
        # 10 - (5 * 30) = 10 - 150 = -140 â†’ 0
        assert result == 0

    def test_predire_quantite_zero_consumption(self, service):
        """Consommation nulle garde la quantitÃ©."""
        result = service.predire_quantite(
            quantite_actuelle=50,
            taux_consommation=0,
            jours=30
        )
        assert result == 50

    def test_predire_quantite_short_period(self, service):
        """PrÃ©diction sur pÃ©riode courte (7 jours)."""
        result = service.predire_quantite(
            quantite_actuelle=100,
            taux_consommation=3.0,
            jours=7
        )
        # 100 - (3 * 7) = 100 - 21 = 79
        assert result == 79

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TESTS detecter_rupture_risque
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def test_detecter_rupture_taux_zero(self, service):
        """Taux consommation 0 â†’ pas de risque."""
        risque, jours = service.detecter_rupture_risque(
            quantite_actuelle=10,
            quantite_min=5,
            taux_consommation=0
        )
        assert risque is False
        assert jours is None

    def test_detecter_rupture_taux_negatif(self, service):
        """Taux consommation nÃ©gatif â†’ pas de risque."""
        risque, jours = service.detecter_rupture_risque(
            quantite_actuelle=10,
            quantite_min=5,
            taux_consommation=-1
        )
        assert risque is False
        assert jours is None

    def test_detecter_rupture_risque_eleve(self, service):
        """Rupture dans < 14 jours â†’ RISQUE."""
        risque, jours = service.detecter_rupture_risque(
            quantite_actuelle=15,
            quantite_min=5,
            taux_consommation=2.0
        )
        # (15 - 5) / 2 = 5 jours â†’ risque car < 14
        assert risque is True
        assert jours == 5

    def test_detecter_rupture_limite(self, service):
        """Rupture dans exactement 14 jours â†’ PAS de risque (< 14)."""
        risque, jours = service.detecter_rupture_risque(
            quantite_actuelle=33,
            quantite_min=5,
            taux_consommation=2.0
        )
        # (33 - 5) / 2 = 14 jours â†’ pas de risque car >= 14
        assert risque is False
        assert jours == 14

    def test_detecter_rupture_sans_risque(self, service):
        """Rupture dans > 14 jours â†’ pas de risque."""
        risque, jours = service.detecter_rupture_risque(
            quantite_actuelle=100,
            quantite_min=10,
            taux_consommation=2.0
        )
        # (100 - 10) / 2 = 45 jours â†’ pas de risque
        assert risque is False
        assert jours == 45

    def test_detecter_rupture_deja_en_dessous(self, service):
        """QuantitÃ© dÃ©jÃ  en dessous du min â†’ jours = 0."""
        risque, jours = service.detecter_rupture_risque(
            quantite_actuelle=3,
            quantite_min=5,
            taux_consommation=1.0
        )
        # (3 - 5) / 1 = -2 â†’ 0
        assert risque is True
        assert jours == 0

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TESTS generer_predictions
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def test_generer_predictions_avec_historique(self, service):
        """GÃ©nÃ¨re prÃ©dictions avec historique disponible."""
        now = datetime.now()
        
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Lait",
                "quantite": 5,
                "quantite_min": 2,
            }
        ]
        
        historique = [
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 10,
                "quantite_apres": 9,
                "date_modification": (now - timedelta(days=3)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 9,
                "quantite_apres": 8,
                "date_modification": (now - timedelta(days=2)).isoformat(),
            },
            {
                "article_id": 1,
                "type_modification": "modification_quantite",
                "quantite_avant": 8,
                "quantite_apres": 7,
                "date_modification": (now - timedelta(days=1)).isoformat(),
            },
        ]
        
        predictions = service.generer_predictions(articles, historique)
        
        assert len(predictions) == 1
        assert predictions[0].article_id == 1
        assert predictions[0].nom == "Lait"
        assert predictions[0].taux_consommation_moyen == 1.0
        assert predictions[0].tendance == "stable"

    def test_generer_predictions_sans_historique(self, service):
        """GÃ©nÃ¨re prÃ©dictions sans historique (valeurs par dÃ©faut)."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Farine",
                "quantite": 500,
                "quantite_min": 100,
            }
        ]
        
        predictions = service.generer_predictions(articles, [])
        
        assert len(predictions) == 1
        assert predictions[0].article_id == 1
        assert predictions[0].tendance == "stable"
        assert predictions[0].confiance == 0.3  # Valeur par dÃ©faut sans historique
        # Taux par dÃ©faut: max(0.5, quantite_min * 0.1) = max(0.5, 10) = 10
        assert predictions[0].taux_consommation_moyen == 10

    def test_generer_predictions_sans_quantite_min(self, service):
        """GÃ©nÃ¨re prÃ©dictions sans quantite_min dÃ©fini."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Sel",
                "quantite": 200,
            }
        ]
        
        predictions = service.generer_predictions(articles, [])
        
        assert len(predictions) == 1
        # Sans quantite_min, taux par dÃ©faut = 0.5
        assert predictions[0].taux_consommation_moyen == 0.5

    def test_generer_predictions_multiple_articles(self, service):
        """GÃ©nÃ¨re prÃ©dictions pour plusieurs articles."""
        articles = [
            {
                "id": 1,
                "ingredient_id": 10,
                "ingredient_nom": "Lait",
                "quantite": 5,
                "quantite_min": 2,
            },
            {
                "id": 2,
                "ingredient_id": 20,
                "ingredient_nom": "Oeufs",
                "quantite": 12,
                "quantite_min": 6,
            },
        ]
        
        predictions = service.generer_predictions(articles, [])
        
        assert len(predictions) == 2
        assert predictions[0].nom == "Lait"
        assert predictions[1].nom == "Oeufs"

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TESTS obtenir_analyse_globale
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def test_obtenir_analyse_globale_empty(self, service):
        """Analyse globale avec liste vide."""
        from src.services.predictions import PredictionArticle
        
        analyse = service.obtenir_analyse_globale([])
        
        assert analyse.nombre_articles == 0
        assert analyse.consommation_moyenne_globale == 0
        assert analyse.tendance_globale == "stable"

    def test_obtenir_analyse_globale_mixed(self, service):
        """Analyse globale avec prÃ©dictions mixtes."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Lait",
                quantite_actuelle=5,
                quantite_predite_semaine=3,
                quantite_predite_mois=0,
                taux_consommation_moyen=1.0,
                tendance="croissante",
                confiance=0.8,
                risque_rupture_mois=True,
                jours_avant_rupture=10,
            ),
            PredictionArticle(
                article_id=2,
                ingredient_id=20,
                nom="Oeufs",
                quantite_actuelle=12,
                quantite_predite_semaine=10,
                quantite_predite_mois=6,
                taux_consommation_moyen=0.5,
                tendance="stable",
                confiance=0.7,
            ),
            PredictionArticle(
                article_id=3,
                ingredient_id=30,
                nom="Beurre",
                quantite_actuelle=2,
                quantite_predite_semaine=1,
                quantite_predite_mois=0,
                taux_consommation_moyen=0.3,
                tendance="decroissante",
                confiance=0.6,
            ),
        ]
        
        analyse = service.obtenir_analyse_globale(predictions)
        
        assert analyse.nombre_articles == 3
        assert analyse.articles_en_rupture_risque == ["Lait"]
        assert analyse.articles_croissance == ["Lait"]
        assert analyse.articles_decroissance == ["Beurre"]
        assert analyse.nb_articles_croissance == 1
        assert analyse.nb_articles_decroissance == 1
        assert analyse.nb_articles_stables == 1
        # Consommation moyenne: (1.0 + 0.5 + 0.3) / 3 = 0.6
        assert 0.59 < analyse.consommation_moyenne_globale < 0.61
        assert analyse.consommation_min == 0.3
        assert analyse.consommation_max == 1.0

    def test_obtenir_analyse_globale_tendance_croissante(self, service):
        """Tendance globale croissante."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=i,
                ingredient_id=i * 10,
                nom=f"Article{i}",
                quantite_actuelle=10,
                quantite_predite_semaine=8,
                quantite_predite_mois=5,
                taux_consommation_moyen=0.5,
                tendance="croissante" if i <= 3 else "stable",
                confiance=0.5,
            )
            for i in range(1, 5)
        ]
        
        analyse = service.obtenir_analyse_globale(predictions)
        
        # 3 croissantes, 1 stable â†’ croissantes > stables * 1.5 ? Non (3 > 1.5)
        # En fait la condition est: croissantes > decroissantes * 1.5
        # Ici decroissantes = 0, donc 3 > 0 * 1.5 = 3 > 0 â†’ VRAI
        assert analyse.tendance_globale == "croissante"

    def test_obtenir_analyse_globale_tendance_decroissante(self, service):
        """Tendance globale dÃ©croissante."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=i,
                ingredient_id=i * 10,
                nom=f"Article{i}",
                quantite_actuelle=10,
                quantite_predite_semaine=8,
                quantite_predite_mois=5,
                taux_consommation_moyen=0.5,
                tendance="decroissante" if i <= 3 else "stable",
                confiance=0.5,
            )
            for i in range(1, 5)
        ]
        
        analyse = service.obtenir_analyse_globale(predictions)
        
        # 3 dÃ©croissantes, 0 croissantes â†’ dÃ©croissantes > croissantes * 1.5
        assert analyse.tendance_globale == "decroissante"

    def test_obtenir_analyse_globale_with_zero_consumption(self, service):
        """Articles avec consommation 0 sont exclus du min/max."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Actif",
                quantite_actuelle=10,
                quantite_predite_semaine=8,
                quantite_predite_mois=5,
                taux_consommation_moyen=2.0,
                tendance="stable",
                confiance=0.5,
            ),
            PredictionArticle(
                article_id=2,
                ingredient_id=20,
                nom="Inactif",
                quantite_actuelle=50,
                quantite_predite_semaine=50,
                quantite_predite_mois=50,
                taux_consommation_moyen=0.0,  # Pas de consommation
                tendance="stable",
                confiance=0.5,
            ),
        ]
        
        analyse = service.obtenir_analyse_globale(predictions)
        
        # Le 0.0 est exclu du calcul min/max
        assert analyse.consommation_min == 2.0
        assert analyse.consommation_max == 2.0

    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
    # TESTS generer_recommandations
    # â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

    def test_generer_recommandations_critique(self, service):
        """Recommandation CRITIQUE pour rupture < 14 jours."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Lait",
                quantite_actuelle=5,
                quantite_predite_semaine=2,
                quantite_predite_mois=0,
                taux_consommation_moyen=1.0,
                tendance="stable",
                confiance=0.8,
                risque_rupture_mois=True,
                jours_avant_rupture=5,  # < 14 â†’ CRITIQUE
            ),
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        assert len(recommandations) == 1
        assert recommandations[0]["article"] == "Lait"
        assert recommandations[0]["priorite"] == "CRITIQUE"
        assert "5 jours" in recommandations[0]["raison"]
        assert recommandations[0]["icone"] == "ðŸš¨"

    def test_generer_recommandations_haute_croissance(self, service):
        """Recommandation HAUTE pour consommation croissante."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Oeufs",
                quantite_actuelle=12,
                quantite_predite_semaine=8,
                quantite_predite_mois=2,
                taux_consommation_moyen=2.0,
                tendance="croissante",
                confiance=0.7,  # > 0.5 â†’ recommandation
                risque_rupture_mois=False,
            ),
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        assert len(recommandations) == 1
        assert recommandations[0]["article"] == "Oeufs"
        assert recommandations[0]["priorite"] == "HAUTE"
        assert "hausse" in recommandations[0]["raison"].lower()
        assert recommandations[0]["icone"] == "ðŸ“ˆ"

    def test_generer_recommandations_croissance_confiance_faible(self, service):
        """Pas de recommandation si confiance < 0.5."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Sel",
                quantite_actuelle=100,
                quantite_predite_semaine=90,
                quantite_predite_mois=70,
                taux_consommation_moyen=1.0,
                tendance="croissante",
                confiance=0.4,  # < 0.5 â†’ pas de recommandation
                risque_rupture_mois=False,
            ),
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        assert len(recommandations) == 0

    def test_generer_recommandations_tri_priorite(self, service):
        """Recommandations triÃ©es par prioritÃ© (CRITIQUE avant HAUTE)."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Croissance",
                quantite_actuelle=50,
                quantite_predite_semaine=40,
                quantite_predite_mois=20,
                taux_consommation_moyen=1.0,
                tendance="croissante",
                confiance=0.8,
                risque_rupture_mois=False,
            ),
            PredictionArticle(
                article_id=2,
                ingredient_id=20,
                nom="Critique",
                quantite_actuelle=5,
                quantite_predite_semaine=2,
                quantite_predite_mois=0,
                taux_consommation_moyen=0.5,
                tendance="stable",
                confiance=0.9,
                risque_rupture_mois=True,
                jours_avant_rupture=3,
            ),
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        assert len(recommandations) == 2
        assert recommandations[0]["priorite"] == "CRITIQUE"
        assert recommandations[1]["priorite"] == "HAUTE"

    def test_generer_recommandations_limite_10(self, service):
        """Limite les recommandations Ã  10."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=i,
                ingredient_id=i * 10,
                nom=f"Article{i}",
                quantite_actuelle=5,
                quantite_predite_semaine=2,
                quantite_predite_mois=0,
                taux_consommation_moyen=1.0,
                tendance="stable",
                confiance=0.9,
                risque_rupture_mois=True,
                jours_avant_rupture=5,
            )
            for i in range(1, 15)  # 14 articles critiques
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        assert len(recommandations) == 10

    def test_generer_recommandations_empty(self, service):
        """Pas de recommandation si pas de prÃ©dictions."""
        recommandations = service.generer_recommandations([])
        assert recommandations == []

    def test_generer_recommandations_risque_sans_jours(self, service):
        """Article avec risque_rupture_mois mais jours_avant_rupture None."""
        from src.services.predictions import PredictionArticle
        
        predictions = [
            PredictionArticle(
                article_id=1,
                ingredient_id=10,
                nom="Test",
                quantite_actuelle=5,
                quantite_predite_semaine=2,
                quantite_predite_mois=0,
                taux_consommation_moyen=1.0,
                tendance="stable",
                confiance=0.9,
                risque_rupture_mois=True,
                jours_avant_rupture=None,  # None
            ),
        ]
        
        recommandations = service.generer_recommandations(predictions)
        
        # Condition: jours_avant_rupture and jours_avant_rupture < 14
        # None â†’ falsy â†’ pas de recommandation CRITIQUE
        assert len(recommandations) == 0


class TestObteniServicePredictionsSingleton:
    """Tests du singleton."""

    def test_obtenir_service_predictions_singleton(self):
        """Factory retourne un singleton."""
        from src.services.predictions import obtenir_service_predictions
        
        service1 = obtenir_service_predictions()
        service2 = obtenir_service_predictions()
        
        assert service1 is service2

    def test_obtenir_service_predictions_is_prediction_service(self):
        """Factory retourne une instance de PredictionService."""
        from src.services.predictions import obtenir_service_predictions, PredictionService
        
        service = obtenir_service_predictions()
        assert isinstance(service, PredictionService)


class TestSchemasPrediction:
    """Tests des schÃ©mas Pydantic."""

    def test_prediction_article_with_defaults(self):
        """PredictionArticle avec valeurs par dÃ©faut."""
        from src.services.predictions import PredictionArticle
        
        pred = PredictionArticle(
            article_id=1,
            ingredient_id=10,
            nom="Test",
            quantite_actuelle=100,
            quantite_predite_semaine=90,
            quantite_predite_mois=70,
            taux_consommation_moyen=1.0,
        )
        
        assert pred.tendance == "stable"
        assert pred.confiance == 0.0
        assert pred.risque_rupture_mois is False
        assert pred.jours_avant_rupture is None

    def test_analyse_prediction_date_auto(self):
        """AnalysePrediction gÃ©nÃ¨re date automatiquement."""
        from src.services.predictions import AnalysePrediction
        
        analyse = AnalysePrediction(
            nombre_articles=5,
            articles_en_rupture_risque=[],
            articles_croissance=[],
            articles_decroissance=[],
            consommation_moyenne_globale=1.0,
            tendance_globale="stable",
        )
        
        assert analyse.date_analyse is not None
        assert isinstance(analyse.date_analyse, datetime)
