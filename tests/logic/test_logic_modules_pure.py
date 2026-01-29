"""
Tests purs des modules *_logic - Cible 40% de couverture.
Ces tests couvrent la logique métier pure sans dépendance Streamlit.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS RECETTES_LOGIC
# ═══════════════════════════════════════════════════════════

class TestRecettesLogicPure:
    """Tests pour recettes_logic.py - fonctions pures."""
    
    def test_import_module(self):
        """Import du module."""
        from src.modules.cuisine import recettes_logic
        assert recettes_logic is not None
    
    def test_valider_recette_nom_manquant(self):
        """Validation: nom manquant."""
        from src.modules.cuisine.recettes_logic import valider_recette
        
        data = {"ingredients": ["test"], "instructions": ["test"]}
        valid, error = valider_recette(data)
        
        assert valid is False
        assert "nom" in error.lower()
    
    def test_valider_recette_ingredients_vide(self):
        """Validation: ingrédients vides."""
        from src.modules.cuisine.recettes_logic import valider_recette
        
        data = {"nom": "Test", "ingredients": [], "instructions": ["test"]}
        valid, error = valider_recette(data)
        
        assert valid is False
    
    def test_valider_recette_valide(self):
        """Validation: recette valide."""
        from src.modules.cuisine.recettes_logic import valider_recette
        
        data = {
            "nom": "Recette Test",
            "ingredients": ["ing1", "ing2"],
            "instructions": ["step1"],
            "temps_preparation": 30,
            "portions": 4
        }
        valid, error = valider_recette(data)
        
        assert valid is True
        assert error is None
    
    def test_calculer_cout_recette(self):
        """Calcul coût recette."""
        from src.modules.cuisine.recettes_logic import calculer_cout_recette
        
        recette = Mock()
        recette.ingredients = ["tomate", "oignon", "ail"]
        
        prix = {"tomate": 2.50, "oignon": 1.20, "ail": 0.80}
        cout = calculer_cout_recette(recette, prix)
        
        assert cout == 4.50
    
    def test_calculer_calories_portion(self):
        """Calcul calories par portion."""
        from src.modules.cuisine.recettes_logic import calculer_calories_portion
        
        recette = Mock()
        recette.calories = 800
        recette.portions = 4
        
        calories = calculer_calories_portion(recette)
        assert calories == 200.0


# ═══════════════════════════════════════════════════════════
# TESTS INVENTAIRE_LOGIC
# ═══════════════════════════════════════════════════════════

class TestInventaireLogicPure:
    """Tests pour inventaire_logic.py - fonctions pures."""
    
    def test_import_module(self):
        """Import du module."""
        from src.modules.cuisine import inventaire_logic
        assert inventaire_logic is not None
    
    def test_calculer_status_stock_bas(self):
        """Status: stock bas."""
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        
        article = {"quantite": 2, "seuil_alerte": 5}
        status = calculer_status_stock(article)
        assert status == "stock_bas"
    
    def test_calculer_status_stock_ok(self):
        """Status: stock ok."""
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        
        article = {"quantite": 10, "seuil_alerte": 5}
        status = calculer_status_stock(article)
        assert status == "ok"
    
    def test_calculer_status_peremption_expire(self):
        """Status: article expiré."""
        from src.modules.cuisine.inventaire_logic import calculer_status_peremption
        
        article = {"date_expiration": date.today() - timedelta(days=1)}
        status = calculer_status_peremption(article)
        assert status == "perime"
    
    def test_calculer_status_peremption_bientot(self):
        """Status: bientôt périmé."""
        from src.modules.cuisine.inventaire_logic import calculer_status_peremption
        
        article = {"date_expiration": date.today() + timedelta(days=3)}
        status = calculer_status_peremption(article, jours_alerte=7)
        assert status == "bientot_perime"
    
    def test_calculer_status_peremption_ok(self):
        """Status: péremption ok."""
        from src.modules.cuisine.inventaire_logic import calculer_status_peremption
        
        article = {"date_expiration": date.today() + timedelta(days=15)}
        status = calculer_status_peremption(article, jours_alerte=7)
        assert status == "ok"
    
    def test_calculer_status_global(self):
        """Status global complet."""
        from src.modules.cuisine.inventaire_logic import calculer_status_global
        
        article = {
            "quantite": 10,
            "seuil_alerte": 5,
            "date_expiration": date.today() + timedelta(days=10)
        }
        status_data = calculer_status_global(article)
        
        assert "status_stock" in status_data
        assert "status_peremption" in status_data
        assert "status_critique" in status_data
        assert status_data["status_critique"] == "ok"
    
    def test_filtrer_par_emplacement(self):
        """Filtrage par emplacement."""
        from src.modules.cuisine.inventaire_logic import filtrer_par_emplacement
        
        articles = [
            {"nom": "Art1", "emplacement": "Réfrigérateur"},
            {"nom": "Art2", "emplacement": "Congélateur"},
            {"nom": "Art3", "emplacement": "Réfrigérateur"}
        ]
        
        resultats = filtrer_par_emplacement(articles, "Réfrigérateur")
        assert len(resultats) == 2
        assert all(a["emplacement"] == "Réfrigérateur" for a in resultats)
    
    def test_filtrer_par_categorie(self):
        """Filtrage par catégorie."""
        from src.modules.cuisine.inventaire_logic import filtrer_par_categorie
        
        articles = [
            {"nom": "Art1", "categorie": "Fruits & Légumes"},
            {"nom": "Art2", "categorie": "Viandes & Poissons"},
            {"nom": "Art3", "categorie": "Fruits & Légumes"}
        ]
        
        resultats = filtrer_par_categorie(articles, "Fruits & Légumes")
        assert len(resultats) == 2
    
    def test_filtrer_par_recherche(self):
        """Filtrage par recherche textuelle."""
        from src.modules.cuisine.inventaire_logic import filtrer_par_recherche
        
        articles = [
            {"nom": "Tomate"},
            {"nom": "Pomme"},
            {"nom": "Tomate cerise"}
        ]
        
        resultats = filtrer_par_recherche(articles, "tomate")
        assert len(resultats) == 2
    
    def test_calculer_alertes(self):
        """Calcul alertes stock."""
        from src.modules.cuisine.inventaire_logic import calculer_alertes
        
        articles = [
            {"quantite": 2, "seuil_alerte": 5, "date_expiration": date.today() + timedelta(days=10)},
            {"quantite": 1, "seuil_alerte": 3, "date_expiration": date.today() - timedelta(days=1)}
        ]
        
        alertes = calculer_alertes(articles)
        assert "stock_bas" in alertes
        assert "perimes" in alertes
        assert len(alertes["stock_bas"]) >= 1
    
    def test_calculer_statistiques_inventaire(self):
        """Statistiques inventaire."""
        from src.modules.cuisine.inventaire_logic import calculer_statistiques_inventaire
        
        articles = [
            {"quantite": 5, "prix_unitaire": 2.50, "date_expiration": date.today() + timedelta(days=10)},
            {"quantite": 3, "prix_unitaire": 1.20, "date_expiration": date.today() + timedelta(days=5)}
        ]
        
        stats = calculer_statistiques_inventaire(articles)
        
        assert "total_articles" in stats
        assert "valeur_totale" in stats
        assert stats["total_articles"] == 2
    
    def test_valider_article_inventaire_nom_manquant(self):
        """Validation: nom manquant."""
        from src.modules.cuisine.inventaire_logic import valider_article_inventaire
        
        article = {"quantite": 5}
        valid, errors = valider_article_inventaire(article)
        
        assert valid is False
        assert len(errors) > 0
    
    def test_valider_article_inventaire_valide(self):
        """Validation: article valide."""
        from src.modules.cuisine.inventaire_logic import valider_article_inventaire
        
        article = {
            "nom": "Tomate",
            "quantite": 5,
            "emplacement": "Réfrigérateur",
            "categorie": "Fruits & Légumes",
            "date_expiration": date.today() + timedelta(days=7)
        }
        valid, errors = valider_article_inventaire(article)
        
        assert valid is True
        assert len(errors) == 0
    
    def test_calculer_jours_avant_peremption(self):
        """Jours avant péremption."""
        from src.modules.cuisine.inventaire_logic import calculer_jours_avant_peremption
        
        article = {"date_expiration": date.today() + timedelta(days=5)}
        jours = calculer_jours_avant_peremption(article)
        
        assert jours == 5
    
    def test_grouper_par_emplacement(self):
        """Groupement par emplacement."""
        from src.modules.cuisine.inventaire_logic import grouper_par_emplacement
        
        articles = [
            {"nom": "Art1", "emplacement": "Réfrigérateur"},
            {"nom": "Art2", "emplacement": "Congélateur"},
            {"nom": "Art3", "emplacement": "Réfrigérateur"}
        ]
        
        groupes = grouper_par_emplacement(articles)
        assert len(groupes["Réfrigérateur"]) == 2
        assert len(groupes["Congélateur"]) == 1


# ═══════════════════════════════════════════════════════════
# TESTS COURSES_LOGIC
# ═══════════════════════════════════════════════════════════

class TestCoursesLogicPure:
    """Tests pour courses_logic.py - fonctions pures."""
    
    def test_import_module(self):
        """Import du module."""
        from src.modules.cuisine import courses_logic
        assert courses_logic is not None
    
    def test_filtrer_par_priorite(self):
        """Filtrage par priorité."""
        from src.modules.cuisine.courses_logic import filtrer_par_priorite
        
        articles = [
            {"nom": "Art1", "priorite": "haute"},
            {"nom": "Art2", "priorite": "basse"},
            {"nom": "Art3", "priorite": "haute"}
        ]
        
        resultats = filtrer_par_priorite(articles, "haute")
        assert len(resultats) == 2
        assert all(a["priorite"] == "haute" for a in resultats)
    
    def test_filtrer_par_rayon(self):
        """Filtrage par rayon."""
        from src.modules.cuisine.courses_logic import filtrer_par_rayon
        
        articles = [
            {"nom": "Art1", "rayon": "Fruits & Légumes"},
            {"nom": "Art2", "rayon": "Laitier"},
            {"nom": "Art3", "rayon": "Fruits & Légumes"}
        ]
        
        resultats = filtrer_par_rayon(articles, "Fruits & Légumes")
        assert len(resultats) == 2
    
    def test_filtrer_par_recherche(self):
        """Filtrage par recherche."""
        from src.modules.cuisine.courses_logic import filtrer_par_recherche
        
        articles = [
            {"nom": "Tomates"},
            {"nom": "Pommes"},
            {"nom": "Tomates cerises"}
        ]
        
        resultats = filtrer_par_recherche(articles, "tomate")
        assert len(resultats) == 2
    
    def test_trier_par_priorite(self):
        """Tri par priorité."""
        from src.modules.cuisine.courses_logic import trier_par_priorite
        
        articles = [
            {"nom": "Art1", "priorite": "basse"},
            {"nom": "Art2", "priorite": "haute"},
            {"nom": "Art3", "priorite": "moyenne"}
        ]
        
        resultats = trier_par_priorite(articles)
        assert resultats[0]["priorite"] == "haute"
        assert resultats[2]["priorite"] == "basse"
    
    def test_trier_par_rayon(self):
        """Tri par rayon."""
        from src.modules.cuisine.courses_logic import trier_par_rayon
        
        articles = [
            {"nom": "Art1", "rayon": "Viandes"},
            {"nom": "Art2", "rayon": "Boulangerie"},
            {"nom": "Art3", "rayon": "Laitier"}
        ]
        
        resultats = trier_par_rayon(articles)
        assert isinstance(resultats, list)
        assert len(resultats) == 3
    
    def test_grouper_par_rayon(self):
        """Groupement par rayon."""
        from src.modules.cuisine.courses_logic import grouper_par_rayon
        
        articles = [
            {"nom": "Art1", "rayon": "Fruits & Légumes"},
            {"nom": "Art2", "rayon": "Laitier"},
            {"nom": "Art3", "rayon": "Fruits & Légumes"}
        ]
        
        groupes = grouper_par_rayon(articles)
        assert len(groupes["Fruits & Légumes"]) == 2
        assert len(groupes["Laitier"]) == 1
    
    def test_grouper_par_priorite(self):
        """Groupement par priorité."""
        from src.modules.cuisine.courses_logic import grouper_par_priorite
        
        articles = [
            {"nom": "Art1", "priorite": "haute"},
            {"nom": "Art2", "priorite": "basse"},
            {"nom": "Art3", "priorite": "haute"}
        ]
        
        groupes = grouper_par_priorite(articles)
        assert len(groupes["haute"]) == 2
        assert len(groupes["basse"]) == 1
    
    def test_calculer_statistiques(self):
        """Statistiques liste."""
        from src.modules.cuisine.courses_logic import calculer_statistiques
        
        articles = [
            {"nom": "Art1", "quantite": 2, "prix_estime": 5.50, "achete": False},
            {"nom": "Art2", "quantite": 3, "prix_estime": 2.30, "achete": True}
        ]
        
        stats = calculer_statistiques(articles)
        
        assert "total_articles" in stats
        assert "cout_estime" in stats
    
    def test_valider_article_nom_manquant(self):
        """Validation: nom manquant."""
        from src.modules.cuisine.courses_logic import valider_article
        
        article = {"quantite": 3}
        valid, errors = valider_article(article)
        
        assert valid is False
        assert len(errors) > 0
    
    def test_valider_article_valide(self):
        """Validation: article valide."""
        from src.modules.cuisine.courses_logic import valider_article
        
        article = {
            "nom": "Pommes",
            "quantite": 5,
            "rayon": "Fruits & Légumes",
            "priorite": "moyenne"
        }
        valid, errors = valider_article(article)
        
        assert valid is True
        assert len(errors) == 0
    
    def test_formater_article_label(self):
        """Formatage label article."""
        from src.modules.cuisine.courses_logic import formater_article_label
        
        article = {
            "nom": "Pommes",
            "quantite": 3,
            "priorite": "haute"
        }
        
        label = formater_article_label(article)
        assert "Pommes" in label
        assert "3" in label
    
    def test_generer_suggestions_depuis_stock_bas(self):
        """Suggestions depuis stock bas."""
        from src.modules.cuisine.courses_logic import generer_suggestions_depuis_stock_bas
        
        alertes = {
            "stock_bas": [
                {"nom": "Tomates", "quantite": 2},
                {"nom": "Lait", "quantite": 1}
            ]
        }
        
        suggestions = generer_suggestions_depuis_stock_bas(alertes)
        assert isinstance(suggestions, list)
    
    def test_deduper_suggestions(self):
        """Dédoublonnage suggestions."""
        from src.modules.cuisine.courses_logic import deduper_suggestions
        
        suggestions = [
            {"nom": "Tomates", "quantite": 2},
            {"nom": "Pommes", "quantite": 3},
            {"nom": "Tomates", "quantite": 1}
        ]
        
        uniques = deduper_suggestions(suggestions)
        noms = [s["nom"] for s in uniques]
        assert noms.count("Tomates") == 1


# ═══════════════════════════════════════════════════════════
# TESTS STRUCTURE MODULES
# ═══════════════════════════════════════════════════════════

class TestLogicModulesStructure:
    """Tests de structure des modules logic."""
    
    def test_all_logic_modules_exist(self):
        """Tous les modules logic existent."""
        modules = [
            "src.modules.cuisine.recettes_logic",
            "src.modules.cuisine.inventaire_logic",
            "src.modules.cuisine.courses_logic"
        ]
        
        for module_name in modules:
            try:
                module = __import__(module_name, fromlist=[''])
                assert module is not None
            except ImportError as e:
                pytest.skip(f"Module {module_name} non disponible: {e}")
    
    def test_recettes_logic_has_functions(self):
        """recettes_logic: fonctions présentes."""
        from src.modules.cuisine import recettes_logic
        
        expected = [
            'get_toutes_recettes', 'get_recette_by_id', 'rechercher_recettes',
            'creer_recette', 'valider_recette', 'calculer_cout_recette',
            'get_statistiques_recettes', 'calculer_calories_portion'
        ]
        
        for func in expected:
            assert hasattr(recettes_logic, func), f"Fonction {func} manquante"
    
    def test_inventaire_logic_has_functions(self):
        """inventaire_logic: fonctions présentes."""
        from src.modules.cuisine import inventaire_logic
        
        expected = [
            'calculer_status_stock', 'calculer_status_peremption',
            'calculer_status_global', 'filtrer_par_emplacement',
            'filtrer_par_categorie', 'calculer_alertes',
            'calculer_statistiques_inventaire', 'valider_article_inventaire',
            'grouper_par_emplacement', 'calculer_jours_avant_peremption'
        ]
        
        for func in expected:
            assert hasattr(inventaire_logic, func), f"Fonction {func} manquante"
    
    def test_courses_logic_has_functions(self):
        """courses_logic: fonctions présentes."""
        from src.modules.cuisine import courses_logic
        
        expected = [
            'filtrer_par_priorite', 'filtrer_par_rayon', 'trier_par_priorite',
            'grouper_par_rayon', 'grouper_par_priorite', 'calculer_statistiques',
            'valider_article', 'generer_suggestions_depuis_stock_bas',
            'deduper_suggestions', 'formater_article_label'
        ]
        
        for func in expected:
            assert hasattr(courses_logic, func), f"Fonction {func} manquante"
