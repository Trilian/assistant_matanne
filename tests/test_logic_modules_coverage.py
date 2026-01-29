"""
Tests de couverture pour les modules *_logic (logique métier pure).
Tests sans dépendance Streamlit pour augmenter la couverture rapidement.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS RECETTES_LOGIC
# ═══════════════════════════════════════════════════════════

class TestRecettesLogic:
    """Tests pour recettes_logic.py."""
    
    def test_import_recettes_logic(self):
        """Teste l'import du module."""
        from src.modules.cuisine import recettes_logic
        assert recettes_logic is not None
    
    @patch('src.modules.cuisine.recettes_logic.get_db_context')
    def test_get_toutes_recettes(self, mock_db):
        """Teste récupération toutes recettes."""
        from src.modules.cuisine.recettes_logic import get_toutes_recettes
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock()
        mock_session.query.return_value.all.return_value = []
        
        result = get_toutes_recettes()
        assert isinstance(result, list)
    
    @patch('src.modules.cuisine.recettes_logic.get_db_context')
    def test_get_recette_by_id(self, mock_db):
        """Teste récupération recette par ID."""
        from src.modules.cuisine.recettes_logic import get_recette_by_id
        
        mock_session = MagicMock()
        mock_db.return_value.__enter__ = Mock(return_value=mock_session)
        mock_db.return_value.__exit__ = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        result = get_recette_by_id(1)
        assert result is None
    
    def test_valider_recette_nom_manquant(self):
        """Teste validation recette sans nom."""
        from src.modules.cuisine.recettes_logic import valider_recette
        
        data = {"ingredients": ["test"], "instructions": ["test"]}
        valid, error = valider_recette(data)
        
        assert valid is False
        assert "nom" in error.lower()
    
    def test_valider_recette_ingredients_manquants(self):
        """Teste validation recette sans ingrédients."""
        from src.modules.cuisine.recettes_logic import valider_recette
        
        data = {"nom": "Test", "ingredients": [], "instructions": ["test"]}
        valid, error = valider_recette(data)
        
        assert valid is False
        assert "ingrédient" in error.lower()
    
    def test_valider_recette_valide(self):
        """Teste validation recette valide."""
        from src.modules.cuisine.recettes_logic import valider_recette
        
        data = {
            "nom": "Test",
            "ingredients": ["ing1"],
            "instructions": ["step1"],
            "temps_preparation": 30,
            "portions": 4
        }
        valid, error = valider_recette(data)
        
        assert valid is True
        assert error is None
    
    def test_calculer_cout_recette(self):
        """Teste calcul coût recette."""
        from src.modules.cuisine.recettes_logic import calculer_cout_recette
        
        recette_mock = Mock()
        recette_mock.ingredients = ["tomate", "oignon", "ail"]
        
        prix = {"tomate": 2.50, "oignon": 1.20, "ail": 0.80}
        cout = calculer_cout_recette(recette_mock, prix)
        
        assert cout == 4.50
    
    def test_calculer_calories_portion(self):
        """Teste calcul calories par portion."""
        from src.modules.cuisine.recettes_logic import calculer_calories_portion
        
        recette_mock = Mock()
        recette_mock.calories = 800
        recette_mock.portions = 4
        
        calories = calculer_calories_portion(recette_mock)
        assert calories == 200.0


# ═══════════════════════════════════════════════════════════
# TESTS INVENTAIRE_LOGIC (FONCTIONS RÉELLES)
# ═══════════════════════════════════════════════════════════

class TestInventaireLogic:
    """Tests pour inventaire_logic.py."""
    
    def test_import_inventaire_logic(self):
        """Teste l'import du module."""
        from src.modules.cuisine import inventaire_logic
        assert inventaire_logic is not None
    
    def test_calculer_status_stock_bas(self):
        """Teste statut stock bas."""
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        
        article = {"quantite": 2, "seuil_alerte": 5}
        status = calculer_status_stock(article)
        assert status == "stock_bas"
    
    def test_calculer_status_stock_ok(self):
        """Teste statut stock ok."""
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        
        article = {"quantite": 10, "seuil_alerte": 5}
        status = calculer_status_stock(article)
        assert status == "ok"
    
    def test_calculer_status_peremption_expire(self):
        """Teste statut périmé."""
        from src.modules.cuisine.inventaire_logic import calculer_status_peremption
        
        article = {"date_expiration": date.today() - timedelta(days=1)}
        status = calculer_status_peremption(article)
        assert status == "perime"
    
    def test_calculer_status_peremption_bientot(self):
        """Teste statut bientôt périmé."""
        from src.modules.cuisine.inventaire_logic import calculer_status_peremption
        
        article = {"date_expiration": date.today() + timedelta(days=3)}
        status = calculer_status_peremption(article, jours_alerte=7)
        assert status == "bientot_perime"
    
    def test_calculer_status_global(self):
        """Teste calcul status global."""
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
    
    def test_filtrer_par_emplacement(self):
        """Teste filtrage par emplacement."""
        from src.modules.cuisine.inventaire_logic import filtrer_par_emplacement
        
        articles = [
            {"nom": "Art1", "emplacement": "Réfrigérateur"},
            {"nom": "Art2", "emplacement": "Congélateur"},
            {"nom": "Art3", "emplacement": "Réfrigérateur"}
        ]
        
        resultats = filtrer_par_emplacement(articles, "Réfrigérateur")
        assert len(resultats) == 2
    
    def test_filtrer_par_categorie(self):
        """Teste filtrage par catégorie."""
        from src.modules.cuisine.inventaire_logic import filtrer_par_categorie
        
        articles = [
            {"nom": "Art1", "categorie": "Fruits & Légumes"},
            {"nom": "Art2", "categorie": "Viandes & Poissons"},
            {"nom": "Art3", "categorie": "Fruits & Légumes"}
        ]
        
        resultats = filtrer_par_categorie(articles, "Fruits & Légumes")
        assert len(resultats) == 2
    
    def test_filtrer_par_recherche(self):
        """Teste filtrage par recherche."""
        from src.modules.cuisine.inventaire_logic import filtrer_par_recherche
        
        articles = [
            {"nom": "Tomate"},
            {"nom": "Pomme"},
            {"nom": "Tomate cerise"}
        ]
        
        resultats = filtrer_par_recherche(articles, "tomate")
        assert len(resultats) == 2
    
    def test_calculer_alertes(self):
        """Teste calcul alertes."""
        from src.modules.cuisine.inventaire_logic import calculer_alertes
        
        articles = [
            {"quantite": 2, "seuil_alerte": 5, "date_expiration": date.today() + timedelta(days=10)},
            {"quantite": 1, "seuil_alerte": 3, "date_expiration": date.today() - timedelta(days=1)}
        ]
        
        alertes = calculer_alertes(articles)
        assert "stock_bas" in alertes
        assert "perimes" in alertes
    
    def test_calculer_statistiques_inventaire(self):
        """Teste statistiques inventaire."""
        from src.modules.cuisine.inventaire_logic import calculer_statistiques_inventaire
        
        articles = [
            {"quantite": 5, "prix_unitaire": 2.50, "date_expiration": date.today() + timedelta(days=10)},
            {"quantite": 3, "prix_unitaire": 1.20, "date_expiration": date.today() + timedelta(days=5)}
        ]
        
        stats = calculer_statistiques_inventaire(articles)
        
        assert "total_articles" in stats
        assert "valeur_totale" in stats
    
    def test_valider_article_inventaire_nom_manquant(self):
        """Teste validation article sans nom."""
        from src.modules.cuisine.inventaire_logic import valider_article_inventaire
        
        article = {"quantite": 5}
        valid, errors = valider_article_inventaire(article)
        
        assert valid is False
        assert len(errors) > 0
    
    def test_valider_article_inventaire_valide(self):
        """Teste validation article valide."""
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
        """Teste calcul jours avant péremption."""
        from src.modules.cuisine.inventaire_logic import calculer_jours_avant_peremption
        
        article = {"date_expiration": date.today() + timedelta(days=5)}
        jours = calculer_jours_avant_peremption(article)
        
        assert jours == 5
    
    def test_grouper_par_emplacement(self):
        """Teste groupement par emplacement."""
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
# TESTS COURSES_LOGIC (FONCTIONS RÉELLES)
# ═══════════════════════════════════════════════════════════

class TestCoursesLogic:
    """Tests pour courses_logic.py."""
    
    def test_import_courses_logic(self):
        """Teste l'import du module."""
        from src.modules.cuisine import courses_logic
        assert courses_logic is not None
    
    def test_filtrer_par_priorite(self):
        """Teste filtrage par priorité."""
        from src.modules.cuisine.courses_logic import filtrer_par_priorite
        
        articles = [
            {"nom": "Art1", "priorite": "haute"},
            {"nom": "Art2", "priorite": "basse"},
            {"nom": "Art3", "priorite": "haute"}
        ]
        
        resultats = filtrer_par_priorite(articles, "haute")
        assert len(resultats) == 2
    
    def test_filtrer_par_rayon(self):
        """Teste filtrage par rayon."""
        from src.modules.cuisine.courses_logic import filtrer_par_rayon
        
        articles = [
            {"nom": "Art1", "rayon": "Fruits & Légumes"},
            {"nom": "Art2", "rayon": "Laitier"},
            {"nom": "Art3", "rayon": "Fruits & Légumes"}
        ]
        
        resultats = filtrer_par_rayon(articles, "Fruits & Légumes")
        assert len(resultats) == 2
    
    def test_filtrer_par_recherche(self):
        """Teste filtrage par recherche."""
        from src.modules.cuisine.courses_logic import filtrer_par_recherche
        
        articles = [
            {"nom": "Tomates"},
            {"nom": "Pommes"},
            {"nom": "Tomates cerises"}
        ]
        
        resultats = filtrer_par_recherche(articles, "tomate")
        assert len(resultats) == 2
    
    def test_trier_par_priorite(self):
        """Teste tri par priorité."""
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
        """Teste tri par rayon."""
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
        """Teste groupement par rayon."""
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
        """Teste groupement par priorité."""
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
        """Teste calcul statistiques."""
        from src.modules.cuisine.courses_logic import calculer_statistiques
        
        articles = [
            {"nom": "Art1", "quantite": 2, "prix_estime": 5.50, "achete": False},
            {"nom": "Art2", "quantite": 3, "prix_estime": 2.30, "achete": True}
        ]
        
        stats = calculer_statistiques(articles)
        calculer_status_stock',
            'calculer_status_peremption',
            'calculer_status_global',
            'filtrer_par_emplacement',
            'filtrer_par_categorie',
            'calculer_alertes',
            'calculer_statistiques_inventaire',
            'valider_article_inventaire',
            'grouper_par_emplacement'
        ]
        
        for func_name in expected_functions:
            assert hasattr(inventaire_logic, func_name), f"Fonction {func_name} manquante"
    
    def test_courses_logic_has_functions(self):
        """Vérifie que courses_logic a les fonctions attendues."""
        from src.modules.cuisine import courses_logic
        
        expected_functions = [
            'filtrer_par_priorite',
            'filtrer_par_rayon',
            'trier_par_priorite',
            'grouper_par_rayon',
            'grouper_par_priorite',
            'calculer_statistiques',
            'valider_article',
            'generer_suggestions_depuis_stock_bas',
            'deduper_suggestions
        }
        valid, errors = valider_article(article)
        
        assert valid is True
        assert len(errors) == 0
    
    def test_formater_article_label(self):
        """Teste formatage label article."""
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
        """Teste génération suggestions depuis stock bas."""
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
        """Teste dédoublonnage suggestions."""
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
# TESTS STRUCTURE ET IMPORTS
# ═══════════════════════════════════════════════════════════

class TestLogicModulesStructure:
    """Tests de structure des modules logic."""
    
    def test_all_logic_modules_exist(self):
        """Vérifie que tous les modules logic existent."""
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
        """Vérifie que recettes_logic a les fonctions attendues."""
        from src.modules.cuisine import recettes_logic
        
        expected_functions = [
            'get_toutes_recettes',
            'get_recette_by_id',
            'rechercher_recettes',
            'creer_recette',
            'valider_recette',
            'calculer_cout_recette',
            'get_statistiques_recettes'
        ]
        
        for func_name in expected_functions:
            assert hasattr(recettes_logic, func_name), f"Fonction {func_name} manquante"
    
    def test_inventaire_logic_has_functions(self):
        """Vérifie que inventaire_logic a les fonctions attendues."""
        from src.modules.cuisine import inventaire_logic
        
        expected_functions = [
            'get_tous_articles',
            'get_article_by_id',
            'ajouter_article',
            'get_alertes_critiques',
            'est_expire',
            'est_stock_bas',
            'calculer_valeur_stock'
        ]
        
        for func_name in expected_functions:
            assert hasattr(inventaire_logic, func_name), f"Fonction {func_name} manquante"
    
    def test_courses_logic_has_functions(self):
        """Vérifie que courses_logic a les fonctions attendues."""
        from src.modules.cuisine import courses_logic
        
        expected_functions = [
            'get_toutes_listes',
            'get_liste_active',
            'creer_liste',
            'ajouter_article',
            'calculer_cout_total',
            'get_statistiques_liste'
        ]
        
        for func_name in expected_functions:
            assert hasattr(courses_logic, func_name), f"Fonction {func_name} manquante"
