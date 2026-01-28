"""
Tests pour les modules logic (courses_logic, inventaire_logic, accueil_logic)
Tests simplifiés et robustes pour augmenter la couverture
"""

import pytest
from datetime import datetime, date, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS COURSES LOGIC
# ═══════════════════════════════════════════════════════════

class TestCoursesLogicConstants:
    """Tests pour les constantes de courses_logic"""
    
    def test_priority_emojis(self):
        from src.modules.cuisine.courses_logic import PRIORITY_EMOJIS
        assert "haute" in PRIORITY_EMOJIS
        assert PRIORITY_EMOJIS["haute"] == "🔴"
    
    def test_priority_order(self):
        from src.modules.cuisine.courses_logic import PRIORITY_ORDER
        assert PRIORITY_ORDER["haute"] < PRIORITY_ORDER["basse"]
    
    def test_rayons_default(self):
        from src.modules.cuisine.courses_logic import RAYONS_DEFAULT
        assert "Fruits & Légumes" in RAYONS_DEFAULT


class TestCoursesLogicFiltres:
    """Tests filtrage courses"""
    
    def test_filtrer_par_priorite(self):
        from src.modules.cuisine.courses_logic import filtrer_par_priorite
        articles = [{"nom": "A", "priorite": "haute"}, {"nom": "B", "priorite": "basse"}]
        assert len(filtrer_par_priorite(articles, "haute")) == 1
    
    def test_trier_par_priorite(self):
        from src.modules.cuisine.courses_logic import trier_par_priorite
        articles = [{"nom": "A", "priorite": "basse"}, {"nom": "B", "priorite": "haute"}]
        trie = trier_par_priorite(articles)
        assert trie[0]["priorite"] == "haute"
    
    def test_grouper_par_priorite(self):
        from src.modules.cuisine.courses_logic import grouper_par_priorite
        articles = [{"nom": "A", "priorite": "haute"}, {"nom": "B", "priorite": "haute"}]
        groupes = grouper_par_priorite(articles)
        assert len(groupes["haute"]) == 2


class TestCoursesLogicSuggestions:
    """Tests suggestions courses"""
    
    def test_deduper_suggestions(self):
        from src.modules.cuisine.courses_logic import deduper_suggestions
        suggestions = [
            {"ingredient_nom": "Lait", "quantite_necessaire": 1, "priorite": "haute"},
            {"ingredient_nom": "lait", "quantite_necessaire": 2, "priorite": "basse"},
            {"ingredient_nom": "Pain", "quantite_necessaire": 1, "priorite": "normale"}
        ]
        deduped = deduper_suggestions(suggestions)
        # "Lait" et "lait" fusionnés = 2 éléments
        assert len(deduped) == 2
        # Vérifier cumul des quantités
        lait = [s for s in deduped if s["ingredient_nom"].lower() == "lait"][0]
        assert lait["quantite_necessaire"] == 3


# ═══════════════════════════════════════════════════════════
# TESTS INVENTAIRE LOGIC
# ═══════════════════════════════════════════════════════════

class TestInventaireLogicConstants:
    """Tests constantes inventaire"""
    
    def test_emplacements(self):
        from src.modules.cuisine.inventaire_logic import EMPLACEMENTS
        assert "Réfrigérateur" in EMPLACEMENTS
    
    def test_categories(self):
        from src.modules.cuisine.inventaire_logic import CATEGORIES
        assert "Produits laitiers" in CATEGORIES
    
    def test_status_config(self):
        from src.modules.cuisine.inventaire_logic import STATUS_CONFIG
        assert "ok" in STATUS_CONFIG


class TestInventaireLogicCalculs:
    """Tests calculs inventaire"""
    
    def test_calculer_status_stock_ok(self):
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        article = {"quantite": 10, "seuil_alerte": 5, "seuil_critique": 2}
        assert calculer_status_stock(article) == "ok"
    
    def test_calculer_status_stock_critique(self):
        from src.modules.cuisine.inventaire_logic import calculer_status_stock
        article = {"quantite": 0, "seuil_alerte": 10, "seuil_critique": 2}
        assert calculer_status_stock(article) == "critique"


class TestInventaireLogicAlertes:
    """Tests alertes inventaire"""
    
    def test_compter_alertes(self):
        from src.modules.cuisine.inventaire_logic import compter_alertes
        alertes = {"critique": [{"nom": "A"}], "stock_bas": [], "perime": [], "bientot_perime": []}
        counts = compter_alertes(alertes)
        assert counts["critique"] == 1
    
    def test_alertes_critiques_existent(self):
        from src.modules.cuisine.inventaire_logic import alertes_critiques_existent
        assert alertes_critiques_existent({"critique": [{"nom": "A"}], "perime": []}) is True
        assert alertes_critiques_existent({"critique": [], "perime": []}) is False


class TestInventaireLogicValidation:
    """Tests validation inventaire"""
    
    def test_valider_article_valide(self):
        from src.modules.cuisine.inventaire_logic import valider_article_inventaire
        article = {"ingredient_nom": "Lait", "quantite": 5, "seuil_alerte": 3, "seuil_critique": 1}
        valide, erreurs = valider_article_inventaire(article)
        assert valide is True
    
    def test_valider_article_invalide(self):
        from src.modules.cuisine.inventaire_logic import valider_article_inventaire
        article = {"ingredient_nom": "", "quantite": -5}
        valide, erreurs = valider_article_inventaire(article)
        assert valide is False


# ═══════════════════════════════════════════════════════════
# TESTS ACCUEIL LOGIC
# ═══════════════════════════════════════════════════════════

class TestAccueilLogicConstants:
    """Tests constantes accueil"""
    
    def test_julius_birthday(self):
        from src.modules.famille.accueil_logic import JULIUS_BIRTHDAY
        assert isinstance(JULIUS_BIRTHDAY, date)
    
    def test_notification_types(self):
        from src.modules.famille.accueil_logic import NOTIFICATION_TYPES
        assert isinstance(NOTIFICATION_TYPES, dict)
    
    def test_dashboard_sections(self):
        from src.modules.famille.accueil_logic import DASHBOARD_SECTIONS
        assert isinstance(DASHBOARD_SECTIONS, list)


class TestAccueilLogicAge:
    """Tests calcul d'âge"""
    
    def test_calculer_age_julius(self):
        from src.modules.famille.accueil_logic import calculer_age_julius
        age = calculer_age_julius()
        assert isinstance(age, dict)
    
    def test_formater_age_julius(self):
        from src.modules.famille.accueil_logic import formater_age_julius
        formatted = formater_age_julius()
        assert isinstance(formatted, str)
    
    def test_calculer_semaines_julius(self):
        from src.modules.famille.accueil_logic import calculer_semaines_julius
        semaines = calculer_semaines_julius()
        assert semaines > 0


class TestAccueilLogicNotifications:
    """Tests notifications accueil"""
    
    def test_compter_notifications_par_type(self):
        from src.modules.famille.accueil_logic import compter_notifications_par_type
        notifications = [{"type": "info"}, {"type": "info"}]
        counts = compter_notifications_par_type(notifications)
        assert isinstance(counts, dict)
    
    def test_filtrer_notifications(self):
        from src.modules.famille.accueil_logic import filtrer_notifications
        notifications = [{"type": "info"}, {"type": "alerte"}]
        filtered = filtrer_notifications(notifications, "info")
        assert len(filtered) == 1


class TestAccueilLogicMetriques:
    """Tests métriques accueil"""
    
    def test_calculer_metriques_recettes(self):
        from src.modules.famille.accueil_logic import calculer_metriques_recettes
        recettes = [{"nom": "R1", "temps_preparation": 30}]
        metriques = calculer_metriques_recettes(recettes)
        assert isinstance(metriques, dict)
    
    def test_calculer_temps_ecoule(self):
        from src.modules.famille.accueil_logic import calculer_temps_ecoule
        result = calculer_temps_ecoule(datetime.now())
        assert isinstance(result, str)


# ═══════════════════════════════════════════════════════════
# TESTS PERFORMANCE MODULE
# ═══════════════════════════════════════════════════════════

class TestPerformanceOptimizations:
    """Tests module performance"""
    
    def test_redis_cache_import(self):
        from src.core.performance_optimizations import RedisCache
        assert RedisCache is not None
    
    def test_query_optimizer_import(self):
        from src.core.performance_optimizations import QueryOptimizer
        assert QueryOptimizer is not None
    
    def test_lazy_image_loader_import(self):
        from src.core.performance_optimizations import LazyImageLoader
        assert LazyImageLoader is not None
    
    def test_helper_functions(self):
        from src.core.performance_optimizations import get_redis_cache, get_lazy_image_loader
        assert callable(get_redis_cache)
        assert callable(get_lazy_image_loader)


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION LOGIC MODULES
# ═══════════════════════════════════════════════════════════

class TestLogicModulesIntegration:
    """Tests intégration modules logic"""
    
    def test_courses_logic_import(self):
        from src.modules.cuisine import courses_logic
        assert hasattr(courses_logic, 'PRIORITY_EMOJIS')
        assert hasattr(courses_logic, 'filtrer_par_priorite')
    
    def test_inventaire_logic_import(self):
        from src.modules.cuisine import inventaire_logic
        assert hasattr(inventaire_logic, 'EMPLACEMENTS')
        assert hasattr(inventaire_logic, 'calculer_status_stock')
    
    def test_accueil_logic_import(self):
        from src.modules.famille import accueil_logic
        assert hasattr(accueil_logic, 'JULIUS_BIRTHDAY')
        assert hasattr(accueil_logic, 'calculer_age_julius')
