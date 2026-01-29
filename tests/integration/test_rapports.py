"""
Tests pour le module Rapports PDF

Tests unitaires:
- Schemas Pydantic (RapportStocks, RapportBudget, AnalyseGaspillage)
- Structure des données de rapport
- Validation et calculs
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime, timedelta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SCHEMAS PYDANTIC RAPPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRapportsPDFService:
    """Tests pour les schémas de rapports PDF"""

    def test_rapport_stocks_schema_default(self):
        """Test schéma RapportStocks avec valeurs par défaut"""
        from src.services.rapports_pdf import RapportStocks
        
        rapport = RapportStocks()
        
        assert rapport.periode_jours == 7
        assert rapport.articles_total == 0
        assert rapport.articles_faible_stock == []
        assert rapport.articles_perimes == []
        assert rapport.valeur_stock_total == 0.0
        assert rapport.categories_resumee == {}

    def test_rapport_stocks_schema_custom(self):
        """Test schéma RapportStocks avec valeurs personnalisées"""
        from src.services.rapports_pdf import RapportStocks
        
        rapport = RapportStocks(
            periode_jours=30,
            articles_total=150,
            articles_faible_stock=[{"nom": "Lait", "quantite": 1}],
            valeur_stock_total=450.50
        )
        
        assert rapport.periode_jours == 30
        assert rapport.articles_total == 150
        assert len(rapport.articles_faible_stock) == 1
        assert rapport.valeur_stock_total == 450.50

    def test_rapport_budget_schema(self):
        """Test schéma RapportBudget"""
        from src.services.rapports_pdf import RapportBudget
        
        rapport = RapportBudget(
            depenses_total=350.00,
            depenses_par_categorie={"Alimentation": 200, "Transport": 150}
        )
        
        assert rapport.depenses_total == 350.00
        assert rapport.periode_jours == 30  # Défaut
        assert len(rapport.depenses_par_categorie) == 2

    def test_analyse_gaspillage_schema(self):
        """Test schéma AnalyseGaspillage"""
        from src.services.rapports_pdf import AnalyseGaspillage
        
        analyse = AnalyseGaspillage(
            articles_perimes_total=5,
            valeur_perdue=25.50,
            recommandations=["Vérifier les dates", "Planifier les repas"]
        )
        
        assert analyse.articles_perimes_total == 5
        assert analyse.valeur_perdue == 25.50
        assert len(analyse.recommandations) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DONNÃ‰ES RAPPORTS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestRapportData:
    """Tests pour les données de rapports"""

    def test_rapport_stocks_structure(self):
        """Test structure données rapport stocks"""
        rapport_data = {
            "titre": "Rapport Stocks Hebdomadaire",
            "date_generation": datetime.now().isoformat(),
            "periode": "7 jours",
            "sections": {
                "resume": {
                    "total_articles": 150,
                    "valeur_totale": 450.50,
                    "articles_faible_stock": 12,
                    "articles_perimes": 3
                },
                "categories": [
                    {"nom": "Fruits", "quantite": 25, "valeur": 45.00},
                    {"nom": "Légumes", "quantite": 30, "valeur": 35.00},
                ]
            }
        }
        
        assert "titre" in rapport_data
        assert "sections" in rapport_data
        assert "resume" in rapport_data["sections"]
        assert rapport_data["sections"]["resume"]["total_articles"] == 150

    def test_rapport_budget_structure(self):
        """Test structure données rapport budget"""
        rapport_data = {
            "titre": "Rapport Budget Mensuel",
            "mois": "2026-01",
            "budget_total": 800.00,
            "depenses_total": 650.00,
            "solde": 150.00,
            "categories": [
                {"nom": "Alimentation", "budget": 400, "depense": 380},
                {"nom": "Transport", "budget": 200, "depense": 150},
            ],
            "tendance": "positif"
        }
        
        assert rapport_data["solde"] == rapport_data["budget_total"] - rapport_data["depenses_total"]
        assert rapport_data["tendance"] == "positif"

    def test_calculate_budget_percentage(self):
        """Test calcul pourcentage budget utilisé"""
        budget = 500.00
        depenses = 350.00
        
        pourcentage = (depenses / budget) * 100
        
        assert pourcentage == 70.0

    def test_detect_budget_alert(self):
        """Test détection alerte budget"""
        budget = 500.00
        depenses = 475.00  # 95% utilisé
        seuil_alerte = 80  # Alerte à 80%
        
        pourcentage = (depenses / budget) * 100
        alerte = pourcentage >= seuil_alerte
        
        assert alerte is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS ANALYSE GASPILLAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestAnalyseGaspillage:
    """Tests pour l'analyse du gaspillage alimentaire"""

    def test_calculate_gaspillage_value(self):
        """Test calcul valeur gaspillage"""
        articles_jetes = [
            {"nom": "Yaourt", "quantite": 2, "prix_unitaire": 1.50},
            {"nom": "Pain", "quantite": 1, "prix_unitaire": 2.00},
            {"nom": "Lait", "quantite": 0.5, "prix_unitaire": 1.20},
        ]
        
        valeur_totale = sum(
            a["quantite"] * a["prix_unitaire"] 
            for a in articles_jetes
        )
        
        assert valeur_totale == 5.60  # 3.00 + 2.00 + 0.60

    def test_gaspillage_by_category(self):
        """Test gaspillage par catégorie"""
        articles_jetes = [
            {"categorie": "Produits laitiers", "valeur": 5.00},
            {"categorie": "Produits laitiers", "valeur": 3.00},
            {"categorie": "Fruits", "valeur": 2.50},
        ]
        
        from collections import defaultdict
        gaspillage_par_categorie = defaultdict(float)
        
        for article in articles_jetes:
            gaspillage_par_categorie[article["categorie"]] += article["valeur"]
        
        assert gaspillage_par_categorie["Produits laitiers"] == 8.00
        assert gaspillage_par_categorie["Fruits"] == 2.50

    def test_gaspillage_trend(self):
        """Test tendance gaspillage"""
        historique = [
            {"mois": "2025-11", "valeur": 45.00},
            {"mois": "2025-12", "valeur": 38.00},
            {"mois": "2026-01", "valeur": 30.00},
        ]
        
        # Tendance = comparaison premier et dernier mois
        variation = historique[-1]["valeur"] - historique[0]["valeur"]
        tendance = "amélioration" if variation < 0 else "dégradation"
        
        assert tendance == "amélioration"
        assert variation == -15.00


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FORMAT PDF
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestPDFFormat:
    """Tests pour le formatage PDF"""

    def test_pdf_header_format(self):
        """Test format en-tête PDF"""
        header = {
            "titre": "Rapport Hebdomadaire",
            "sous_titre": "Semaine du 20 au 26 janvier 2026",
            "logo": None,
            "date_generation": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        
        assert "titre" in header
        assert "/" in header["date_generation"]

    def test_pdf_table_format(self):
        """Test format tableau PDF"""
        table_data = {
            "headers": ["Article", "Quantité", "Unité", "Prix"],
            "rows": [
                ["Lait", "2", "L", "2.40 â‚¬"],
                ["Pain", "1", "u", "1.50 â‚¬"],
            ],
            "footer": ["Total", "", "", "3.90 â‚¬"]
        }
        
        assert len(table_data["headers"]) == 4
        assert len(table_data["rows"]) == 2
        assert table_data["footer"][-1] == "3.90 â‚¬"

    def test_currency_format(self):
        """Test formatage devise"""
        montant = 1234.56
        
        formatted = f"{montant:,.2f} â‚¬".replace(",", " ")
        
        assert formatted == "1 234.56 â‚¬"

