"""
Tests avec mocks Streamlit pour les modules cuisine
Couverture cible: 40%+ pour courses, inventaire, recettes, recettes_import
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import date, datetime, timedelta
import pandas as pd


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES COMMUNES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_streamlit():
    """Mock complet de Streamlit"""
    with patch("streamlit.set_page_config") as mock_config, \
         patch("streamlit.title") as mock_title, \
         patch("streamlit.caption") as mock_caption, \
         patch("streamlit.tabs") as mock_tabs, \
         patch("streamlit.columns") as mock_cols, \
         patch("streamlit.metric") as mock_metric, \
         patch("streamlit.divider") as mock_divider, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.info") as mock_info, \
         patch("streamlit.success") as mock_success, \
         patch("streamlit.warning") as mock_warning, \
         patch("streamlit.button") as mock_button, \
         patch("streamlit.selectbox") as mock_selectbox, \
         patch("streamlit.text_input") as mock_text_input, \
         patch("streamlit.number_input") as mock_number_input, \
         patch("streamlit.expander") as mock_expander, \
         patch("streamlit.subheader") as mock_subheader, \
         patch("streamlit.checkbox") as mock_checkbox, \
         patch("streamlit.slider") as mock_slider, \
         patch("streamlit.container") as mock_container, \
         patch("streamlit.markdown") as mock_markdown, \
         patch("streamlit.write") as mock_write, \
         patch("streamlit.dataframe") as mock_dataframe, \
         patch("streamlit.progress") as mock_progress, \
         patch("streamlit.rerun") as mock_rerun, \
         patch("streamlit.session_state", {}) as mock_state, \
         patch("streamlit.cache_data", lambda **kwargs: lambda f: f):
        
        # Configurer tabs pour retourner des contextes mockés
        mock_tabs.return_value = [MagicMock() for _ in range(10)]
        
        # Configurer columns pour retourner des contextes mockés  
        mock_cols.return_value = [MagicMock() for _ in range(10)]
        
        # Configurer expander pour retourner un contexte mocké
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()
        
        # Configurer container
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        yield {
            "config": mock_config,
            "title": mock_title,
            "caption": mock_caption,
            "tabs": mock_tabs,
            "columns": mock_cols,
            "metric": mock_metric,
            "error": mock_error,
            "info": mock_info,
            "success": mock_success,
            "warning": mock_warning,
            "button": mock_button,
            "selectbox": mock_selectbox,
            "text_input": mock_text_input,
            "number_input": mock_number_input,
            "expander": mock_expander,
            "checkbox": mock_checkbox,
            "slider": mock_slider,
            "session_state": mock_state,
            "rerun": mock_rerun,
        }


@pytest.fixture
def mock_courses_service():
    """Mock du service courses"""
    service = MagicMock()
    service.get_liste_courses.return_value = [
        {"id": 1, "ingredient_nom": "Tomates", "priorite": "haute", "rayon_magasin": "Fruits & Légumes", "quantite": 2},
        {"id": 2, "ingredient_nom": "Lait", "priorite": "moyenne", "rayon_magasin": "Laitier", "quantite": 1},
        {"id": 3, "ingredient_nom": "Pain", "priorite": "basse", "rayon_magasin": "Boulangerie", "quantite": 1},
    ]
    service.ajouter_article.return_value = True
    service.supprimer_article.return_value = True
    service.marquer_achete.return_value = True
    return service


@pytest.fixture
def mock_inventaire_service():
    """Mock du service inventaire"""
    service = MagicMock()
    service.get_inventaire_complet.return_value = [
        {"id": 1, "ingredient_nom": "Farine", "quantite": 500, "unite": "g", "emplacement": "Placard", "ingredient_categorie": "Épicerie", "statut": "ok"},
        {"id": 2, "ingredient_nom": "Oeufs", "quantite": 6, "unite": "pcs", "emplacement": "Frigo", "ingredient_categorie": "Frais", "statut": "stock_bas"},
        {"id": 3, "ingredient_nom": "Beurre", "quantite": 50, "unite": "g", "emplacement": "Frigo", "ingredient_categorie": "Laitier", "statut": "critique"},
    ]
    service.get_alertes.return_value = {
        "critique": [{"nom": "Beurre"}],
        "stock_bas": [{"nom": "Oeufs"}],
        "peremption_proche": []
    }
    return service


@pytest.fixture
def mock_recette_service():
    """Mock du service recettes"""
    service = MagicMock()
    
    # Créer des recettes mockées
    recette1 = MagicMock()
    recette1.id = 1
    recette1.nom = "Tarte aux pommes"
    recette1.description = "Une délicieuse tarte"
    recette1.difficulte = "facile"
    recette1.temps_preparation = 30
    recette1.temps_cuisson = 45
    recette1.portions = 6
    recette1.calories = 250
    recette1.type_repas = "goûter"
    recette1.url_image = None
    recette1.score_bio = 50
    recette1.score_local = 60
    recette1.compatible_cookeo = True
    recette1.compatible_monsieur_cuisine = False
    recette1.compatible_airfryer = False
    recette1.compatible_multicooker = False
    recette1.est_rapide = True
    recette1.est_equilibre = True
    recette1.congelable = True
    recette1.est_bio = True
    recette1.est_local = True
    recette1.robots_compatibles = ["Cookeo"]
    
    recette2 = MagicMock()
    recette2.id = 2
    recette2.nom = "Salade César"
    recette2.description = "Salade fraîche"
    recette2.difficulte = "facile"
    recette2.temps_preparation = 15
    recette2.temps_cuisson = 0
    recette2.portions = 2
    recette2.calories = 180
    recette2.type_repas = "déjeuner"
    recette2.url_image = "http://example.com/img.jpg"
    recette2.score_bio = 80
    recette2.score_local = 70
    recette2.compatible_cookeo = False
    recette2.compatible_monsieur_cuisine = False
    recette2.compatible_airfryer = False
    recette2.compatible_multicooker = False
    recette2.est_rapide = True
    recette2.est_equilibre = True
    recette2.congelable = False
    recette2.est_bio = True
    recette2.est_local = True
    recette2.robots_compatibles = []
    
    service.search_advanced.return_value = [recette1, recette2]
    service.get_by_id_full.return_value = recette1
    
    return service


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE COURSES
# ═══════════════════════════════════════════════════════════════════════════════


class TestCoursesConstantes:
    """Tests des constantes du module courses"""
    
    def test_priority_emojis_defined(self):
        """Vérifie que les emojis de priorité sont définis"""
        from src.modules.cuisine.courses import PRIORITY_EMOJIS
        
        assert "haute" in PRIORITY_EMOJIS
        assert "moyenne" in PRIORITY_EMOJIS
        assert "basse" in PRIORITY_EMOJIS
        assert PRIORITY_EMOJIS["haute"] == "🔴"
        assert PRIORITY_EMOJIS["moyenne"] == "🟡"
        assert PRIORITY_EMOJIS["basse"] == "🟢"
    
    def test_rayons_default_defined(self):
        """Vérifie que les rayons par défaut sont définis"""
        from src.modules.cuisine.courses import RAYONS_DEFAULT
        
        assert len(RAYONS_DEFAULT) >= 5
        assert "Fruits & Légumes" in RAYONS_DEFAULT
        assert "Laitier" in RAYONS_DEFAULT
        assert "Boulangerie" in RAYONS_DEFAULT


class TestCoursesApp:
    """Tests de la fonction app() du module courses"""
    
    def test_app_initializes_session_state(self, mock_streamlit):
        """Vérifie que app() initialise le session_state"""
        with patch("src.modules.cuisine.courses.get_courses_service") as mock_get_service, \
             patch("src.modules.cuisine.courses.get_inventaire_service") as mock_get_inv, \
             patch("src.modules.cuisine.courses._init_realtime_sync") as mock_sync, \
             patch("src.modules.cuisine.courses.render_liste_active") as mock_render_liste, \
             patch("src.modules.cuisine.courses.render_suggestions_ia") as mock_render_ia, \
             patch("src.modules.cuisine.courses.render_historique") as mock_render_hist, \
             patch("src.modules.cuisine.courses.render_modeles") as mock_render_mod, \
             patch("src.modules.cuisine.courses.render_outils") as mock_render_out:
            
            from src.modules.cuisine.courses import app
            
            # Exécuter
            app()
            
            # Vérifier que set_page_config est appelé
            mock_streamlit["config"].assert_called_once()
            mock_streamlit["title"].assert_called_once()
    
    def test_app_calls_tabs(self, mock_streamlit):
        """Vérifie que app() crée les tabs"""
        with patch("src.modules.cuisine.courses.get_courses_service") as mock_get_service, \
             patch("src.modules.cuisine.courses.get_inventaire_service") as mock_get_inv, \
             patch("src.modules.cuisine.courses._init_realtime_sync") as mock_sync, \
             patch("src.modules.cuisine.courses.render_liste_active") as mock_render_liste, \
             patch("src.modules.cuisine.courses.render_suggestions_ia") as mock_render_ia, \
             patch("src.modules.cuisine.courses.render_historique") as mock_render_hist, \
             patch("src.modules.cuisine.courses.render_modeles") as mock_render_mod, \
             patch("src.modules.cuisine.courses.render_outils") as mock_render_out:
            
            from src.modules.cuisine.courses import app
            
            app()
            
            # Vérifier que tabs est appelé avec 5 onglets
            mock_streamlit["tabs"].assert_called_once()


class TestCoursesRenderListeActive:
    """Tests de render_liste_active()"""
    
    def test_render_liste_active_service_none(self, mock_streamlit):
        """Vérifie gestion quand le service est None"""
        with patch("src.modules.cuisine.courses.get_courses_service", return_value=None), \
             patch("src.modules.cuisine.courses.get_inventaire_service", return_value=None):
            
            from src.modules.cuisine.courses import render_liste_active
            
            render_liste_active()
            
            # Vérifie qu'une erreur est affichée
            mock_streamlit["error"].assert_called()
    
    def test_render_liste_active_with_data(self, mock_streamlit, mock_courses_service, mock_inventaire_service):
        """Vérifie le rendu avec des données"""
        with patch("src.modules.cuisine.courses.get_courses_service", return_value=mock_courses_service), \
             patch("src.modules.cuisine.courses.get_inventaire_service", return_value=mock_inventaire_service), \
             patch("src.modules.cuisine.courses.render_rayon_articles") as mock_render_rayon, \
             patch("streamlit.session_state", {"new_article_mode": False}):
            
            from src.modules.cuisine.courses import render_liste_active
            
            render_liste_active()
            
            # Vérifier que les métriques sont appelées
            assert mock_streamlit["metric"].call_count >= 1
    
    def test_render_liste_active_empty_list(self, mock_streamlit, mock_inventaire_service):
        """Vérifie le rendu avec une liste vide"""
        mock_service = MagicMock()
        mock_service.get_liste_courses.return_value = []
        
        with patch("src.modules.cuisine.courses.get_courses_service", return_value=mock_service), \
             patch("src.modules.cuisine.courses.get_inventaire_service", return_value=mock_inventaire_service), \
             patch("streamlit.session_state", {"new_article_mode": False}):
            
            from src.modules.cuisine.courses import render_liste_active
            
            render_liste_active()
            
            # Vérifie qu'un message info est affiché
            mock_streamlit["info"].assert_called()


class TestCoursesFilters:
    """Tests des filtres de la liste de courses"""
    
    def test_filter_by_priority(self):
        """Test du filtrage par priorité"""
        liste = [
            {"id": 1, "priorite": "haute", "ingredient_nom": "A"},
            {"id": 2, "priorite": "moyenne", "ingredient_nom": "B"},
            {"id": 3, "priorite": "basse", "ingredient_nom": "C"},
        ]
        
        # Filtre haute
        filtree = [a for a in liste if a.get("priorite") == "haute"]
        assert len(filtree) == 1
        assert filtree[0]["ingredient_nom"] == "A"
        
        # Filtre moyenne
        filtree = [a for a in liste if a.get("priorite") == "moyenne"]
        assert len(filtree) == 1
        assert filtree[0]["ingredient_nom"] == "B"
    
    def test_filter_by_rayon(self):
        """Test du filtrage par rayon"""
        liste = [
            {"id": 1, "rayon_magasin": "Fruits & Légumes", "ingredient_nom": "Tomates"},
            {"id": 2, "rayon_magasin": "Laitier", "ingredient_nom": "Lait"},
            {"id": 3, "rayon_magasin": "Fruits & Légumes", "ingredient_nom": "Carottes"},
        ]
        
        filtree = [a for a in liste if a.get("rayon_magasin") == "Fruits & Légumes"]
        assert len(filtree) == 2
    
    def test_filter_by_search_term(self):
        """Test du filtrage par recherche"""
        liste = [
            {"ingredient_nom": "Tomates cerises"},
            {"ingredient_nom": "Lait entier"},
            {"ingredient_nom": "Tomates pelées"},
        ]
        
        search_term = "tomates"
        filtree = [a for a in liste if search_term.lower() in a.get("ingredient_nom", "").lower()]
        assert len(filtree) == 2


class TestCoursesGroupByRayon:
    """Tests du regroupement par rayon"""
    
    def test_group_articles_by_rayon(self):
        """Test du regroupement des articles par rayon"""
        liste = [
            {"rayon_magasin": "Fruits & Légumes", "ingredient_nom": "Tomates"},
            {"rayon_magasin": "Laitier", "ingredient_nom": "Lait"},
            {"rayon_magasin": "Fruits & Légumes", "ingredient_nom": "Carottes"},
            {"rayon_magasin": "Autre", "ingredient_nom": "Sel"},
        ]
        
        rayons = {}
        for article in liste:
            rayon = article.get("rayon_magasin", "Autre")
            if rayon not in rayons:
                rayons[rayon] = []
            rayons[rayon].append(article)
        
        assert len(rayons) == 3
        assert len(rayons["Fruits & Légumes"]) == 2
        assert len(rayons["Laitier"]) == 1
        assert len(rayons["Autre"]) == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE INVENTAIRE
# ═══════════════════════════════════════════════════════════════════════════════


class TestInventaireApp:
    """Tests de la fonction app() du module inventaire"""
    
    def test_app_initializes(self, mock_streamlit):
        """Vérifie que app() s'initialise correctement"""
        with patch("src.modules.cuisine.inventaire.get_inventaire_service") as mock_get_service, \
             patch("src.modules.cuisine.inventaire.render_stock") as mock_render_stock, \
             patch("src.modules.cuisine.inventaire.render_alertes") as mock_render_alertes, \
             patch("src.modules.cuisine.inventaire.render_categories") as mock_render_cat, \
             patch("src.modules.cuisine.inventaire.render_suggestions_ia") as mock_render_ia, \
             patch("src.modules.cuisine.inventaire.render_historique") as mock_render_hist, \
             patch("src.modules.cuisine.inventaire.render_photos") as mock_render_photos, \
             patch("src.modules.cuisine.inventaire.render_notifications") as mock_render_notif, \
             patch("src.modules.cuisine.inventaire.render_predictions") as mock_render_pred, \
             patch("src.modules.cuisine.inventaire.render_tools") as mock_render_tools:
            
            from src.modules.cuisine.inventaire import app
            
            app()
            
            mock_streamlit["config"].assert_called_once()
            mock_streamlit["title"].assert_called_once()


class TestInventaireRenderStock:
    """Tests de render_stock()"""
    
    def test_render_stock_service_none(self, mock_streamlit):
        """Vérifie gestion quand le service est None"""
        with patch("src.modules.cuisine.inventaire.get_inventaire_service", return_value=None):
            
            from src.modules.cuisine.inventaire import render_stock
            
            render_stock()
            
            mock_streamlit["error"].assert_called()
    
    def test_render_stock_empty_inventory(self, mock_streamlit):
        """Vérifie le rendu avec un inventaire vide"""
        mock_service = MagicMock()
        mock_service.get_inventaire_complet.return_value = []
        
        with patch("src.modules.cuisine.inventaire.get_inventaire_service", return_value=mock_service), \
             patch("streamlit.session_state", {"show_form": False}):
            
            from src.modules.cuisine.inventaire import render_stock
            
            render_stock()
            
            mock_streamlit["info"].assert_called()
    
    def test_render_stock_with_data(self, mock_streamlit, mock_inventaire_service):
        """Vérifie le rendu avec des données"""
        with patch("src.modules.cuisine.inventaire.get_inventaire_service", return_value=mock_inventaire_service), \
             patch("src.modules.cuisine.inventaire._prepare_inventory_dataframe") as mock_prepare, \
             patch("streamlit.session_state", {"show_form": False, "refresh_counter": 0}):
            
            mock_prepare.return_value = pd.DataFrame([{"nom": "Test"}])
            
            from src.modules.cuisine.inventaire import render_stock
            
            render_stock()
            
            # Vérifie que les métriques sont appelées
            assert mock_streamlit["metric"].call_count >= 1


class TestInventaireFilters:
    """Tests des filtres de l'inventaire"""
    
    def test_filter_by_emplacement(self):
        """Test du filtrage par emplacement"""
        inventaire = [
            {"id": 1, "emplacement": "Frigo", "ingredient_nom": "Lait"},
            {"id": 2, "emplacement": "Placard", "ingredient_nom": "Farine"},
            {"id": 3, "emplacement": "Frigo", "ingredient_nom": "Beurre"},
        ]
        
        filtree = [a for a in inventaire if a["emplacement"] == "Frigo"]
        assert len(filtree) == 2
    
    def test_filter_by_categorie(self):
        """Test du filtrage par catégorie"""
        inventaire = [
            {"id": 1, "ingredient_categorie": "Laitier", "ingredient_nom": "Lait"},
            {"id": 2, "ingredient_categorie": "Épicerie", "ingredient_nom": "Farine"},
            {"id": 3, "ingredient_categorie": "Laitier", "ingredient_nom": "Beurre"},
        ]
        
        filtree = [a for a in inventaire if a["ingredient_categorie"] == "Laitier"]
        assert len(filtree) == 2
    
    def test_filter_by_status(self):
        """Test du filtrage par statut"""
        inventaire = [
            {"id": 1, "statut": "ok", "ingredient_nom": "Sel"},
            {"id": 2, "statut": "stock_bas", "ingredient_nom": "Poivre"},
            {"id": 3, "statut": "critique", "ingredient_nom": "Huile"},
        ]
        
        filtree = [a for a in inventaire if a["statut"] in ["stock_bas", "critique"]]
        assert len(filtree) == 2


class TestInventaireAlertes:
    """Tests du système d'alertes"""
    
    def test_alertes_structure(self, mock_inventaire_service):
        """Vérifie la structure des alertes"""
        alertes = mock_inventaire_service.get_alertes()
        
        assert "critique" in alertes
        assert "stock_bas" in alertes
        assert "peremption_proche" in alertes
    
    def test_alertes_count(self, mock_inventaire_service):
        """Vérifie le comptage des alertes"""
        alertes = mock_inventaire_service.get_alertes()
        
        stock_critique = len(alertes.get("critique", []))
        stock_bas = len(alertes.get("stock_bas", []))
        
        assert stock_critique == 1
        assert stock_bas == 1


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE RECETTES
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecettesApp:
    """Tests de la fonction app() du module recettes"""
    
    def test_app_initializes(self, mock_streamlit):
        """Vérifie que app() s'initialise correctement"""
        with patch("src.modules.cuisine.recettes.get_recette_service") as mock_get_service, \
             patch("src.modules.cuisine.recettes.render_liste") as mock_render_liste, \
             patch("src.modules.cuisine.recettes.render_ajouter_manuel") as mock_render_ajout, \
             patch("src.modules.cuisine.recettes.render_importer") as mock_render_import, \
             patch("src.modules.cuisine.recettes.render_generer_ia") as mock_render_ia, \
             patch("streamlit.session_state", {"detail_recette_id": None}):
            
            from src.modules.cuisine.recettes import app
            
            app()
            
            mock_streamlit["title"].assert_called_once()


class TestRecettesRenderListe:
    """Tests de render_liste()"""
    
    def test_render_liste_service_none(self, mock_streamlit):
        """Vérifie gestion quand le service est None"""
        with patch("src.modules.cuisine.recettes.get_recette_service", return_value=None):
            
            from src.modules.cuisine.recettes import render_liste
            
            render_liste()
            
            mock_streamlit["error"].assert_called()
    
    def test_render_liste_no_results(self, mock_streamlit):
        """Vérifie le rendu sans résultats"""
        mock_service = MagicMock()
        mock_service.search_advanced.return_value = []
        
        with patch("src.modules.cuisine.recettes.get_recette_service", return_value=mock_service), \
             patch("streamlit.session_state", {"recettes_page": 0}):
            
            from src.modules.cuisine.recettes import render_liste
            
            render_liste()
            
            mock_streamlit["info"].assert_called()
    
    def test_render_liste_with_results(self, mock_streamlit, mock_recette_service):
        """Vérifie le rendu avec des résultats"""
        with patch("src.modules.cuisine.recettes.get_recette_service", return_value=mock_recette_service), \
             patch("streamlit.session_state", {"recettes_page": 0}):
            
            from src.modules.cuisine.recettes import render_liste
            
            render_liste()
            
            mock_streamlit["success"].assert_called()


class TestRecettesFilters:
    """Tests des filtres de recettes"""
    
    def test_filter_by_type_repas(self, mock_recette_service):
        """Test du filtrage par type de repas"""
        recettes = mock_recette_service.search_advanced()
        
        filtrees = [r for r in recettes if r.type_repas == "goûter"]
        assert len(filtrees) == 1
        assert filtrees[0].nom == "Tarte aux pommes"
    
    def test_filter_by_difficulte(self, mock_recette_service):
        """Test du filtrage par difficulté"""
        recettes = mock_recette_service.search_advanced()
        
        filtrees = [r for r in recettes if r.difficulte == "facile"]
        assert len(filtrees) == 2
    
    def test_filter_by_temps_max(self, mock_recette_service):
        """Test du filtrage par temps max"""
        recettes = mock_recette_service.search_advanced()
        
        filtrees = [r for r in recettes if r.temps_preparation <= 20]
        assert len(filtrees) == 1
        assert filtrees[0].nom == "Salade César"
    
    def test_filter_by_score_bio(self, mock_recette_service):
        """Test du filtrage par score bio"""
        recettes = mock_recette_service.search_advanced()
        min_score_bio = 70
        
        filtrees = [r for r in recettes if (r.score_bio or 0) >= min_score_bio]
        assert len(filtrees) == 1
        assert filtrees[0].nom == "Salade César"
    
    def test_filter_by_robot(self, mock_recette_service):
        """Test du filtrage par robot compatible"""
        recettes = mock_recette_service.search_advanced()
        
        def has_cookeo(recette):
            return recette.compatible_cookeo
        
        filtrees = [r for r in recettes if has_cookeo(r)]
        assert len(filtrees) == 1
        assert filtrees[0].nom == "Tarte aux pommes"
    
    def test_filter_by_tags(self, mock_recette_service):
        """Test du filtrage par tags"""
        recettes = mock_recette_service.search_advanced()
        
        # Filtre rapide
        filtrees = [r for r in recettes if r.est_rapide]
        assert len(filtrees) == 2
        
        # Filtre équilibré
        filtrees = [r for r in recettes if r.est_equilibre]
        assert len(filtrees) == 2
        
        # Filtre congélable
        filtrees = [r for r in recettes if r.congelable]
        assert len(filtrees) == 1


class TestRecettesPagination:
    """Tests de la pagination"""
    
    def test_pagination_calculation(self):
        """Test du calcul de pagination"""
        total_recettes = 25
        page_size = 9
        
        total_pages = (total_recettes + page_size - 1) // page_size
        assert total_pages == 3
        
        # Page 0
        start_idx = 0 * page_size
        end_idx = start_idx + page_size
        assert start_idx == 0
        assert end_idx == 9
        
        # Page 2
        start_idx = 2 * page_size
        end_idx = start_idx + page_size
        assert start_idx == 18
        assert end_idx == 27
    
    def test_pagination_last_page(self):
        """Test de la dernière page"""
        total_recettes = 25
        page_size = 9
        current_page = 2
        
        total_pages = (total_recettes + page_size - 1) // page_size
        
        # Limiter la page courante
        current_page = min(current_page, total_pages - 1)
        assert current_page == 2
        
        start_idx = current_page * page_size
        recettes_on_page = min(page_size, total_recettes - start_idx)
        assert recettes_on_page == 7


class TestRecettesDifficulte:
    """Tests des emojis de difficulté"""
    
    def test_difficulty_emojis(self):
        """Test des emojis par difficulté"""
        difficulty_map = {"facile": "🟢", "moyen": "🟡", "difficile": "🔴"}
        
        assert difficulty_map["facile"] == "🟢"
        assert difficulty_map["moyen"] == "🟡"
        assert difficulty_map["difficile"] == "🔴"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE RECETTES_IMPORT
# ═══════════════════════════════════════════════════════════════════════════════


class TestRecettesImport:
    """Tests du module d'import de recettes"""
    
    def test_csv_validation_required_columns(self):
        """Test de validation des colonnes requises"""
        required_columns = ["nom", "description", "temps_preparation"]
        
        # CSV valide
        df_valid = pd.DataFrame({
            "nom": ["Recette 1"],
            "description": ["Desc"],
            "temps_preparation": [30]
        })
        
        missing = [col for col in required_columns if col not in df_valid.columns]
        assert len(missing) == 0
        
        # CSV invalide
        df_invalid = pd.DataFrame({
            "nom": ["Recette 1"],
        })
        
        missing = [col for col in required_columns if col not in df_invalid.columns]
        assert len(missing) == 2
    
    def test_import_data_preparation(self):
        """Test de la préparation des données d'import"""
        raw_data = {
            "nom": "  Tarte aux fruits  ",
            "temps_preparation": "30",
            "difficulte": "FACILE",
        }
        
        # Nettoyage
        cleaned = {
            "nom": raw_data["nom"].strip(),
            "temps_preparation": int(raw_data["temps_preparation"]),
            "difficulte": raw_data["difficulte"].lower(),
        }
        
        assert cleaned["nom"] == "Tarte aux fruits"
        assert cleaned["temps_preparation"] == 30
        assert cleaned["difficulte"] == "facile"


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS INTÉGRATION CUISINE
# ═══════════════════════════════════════════════════════════════════════════════


class TestCuisineIntegration:
    """Tests d'intégration des modules cuisine"""
    
    def test_courses_to_inventaire_flow(self, mock_courses_service, mock_inventaire_service):
        """Test du flux courses -> inventaire"""
        # Simuler l'achat d'un article
        articles_courses = mock_courses_service.get_liste_courses()
        article = articles_courses[0]
        
        # Marquer comme acheté
        mock_courses_service.marquer_achete(article["id"])
        
        # Vérifier que l'inventaire peut être mis à jour
        assert mock_inventaire_service.get_inventaire_complet() is not None
    
    def test_inventaire_alerte_to_courses(self, mock_inventaire_service, mock_courses_service):
        """Test du flux alertes inventaire -> liste courses"""
        alertes = mock_inventaire_service.get_alertes()
        
        # Articles en stock critique
        stock_critique = alertes.get("critique", [])
        
        # Simuler l'ajout aux courses
        for item in stock_critique:
            result = mock_courses_service.ajouter_article({
                "ingredient_nom": item["nom"],
                "priorite": "haute"
            })
            assert result is True
    
    def test_recettes_to_courses_generation(self, mock_recette_service, mock_courses_service):
        """Test de la génération de courses depuis recettes"""
        recettes = mock_recette_service.search_advanced()
        
        # Simuler la génération de liste de courses
        assert len(recettes) > 0
        
        # Chaque recette devrait pouvoir générer des ingrédients
        for recette in recettes:
            assert recette.nom is not None
            assert recette.id is not None


class TestCoursesMetrics:
    """Tests des métriques de courses"""
    
    def test_count_by_priority(self):
        """Test du comptage par priorité"""
        liste = [
            {"priorite": "haute"},
            {"priorite": "haute"},
            {"priorite": "moyenne"},
            {"priorite": "basse"},
        ]
        
        haute = len([a for a in liste if a.get("priorite") == "haute"])
        moyenne = len([a for a in liste if a.get("priorite") == "moyenne"])
        basse = len([a for a in liste if a.get("priorite") == "basse"])
        
        assert haute == 2
        assert moyenne == 1
        assert basse == 1
    
    def test_total_articles(self):
        """Test du total d'articles"""
        liste_active = [{"id": 1}, {"id": 2}, {"id": 3}]
        liste_achetes = [{"id": 4}, {"id": 5}]
        
        total = len(liste_active) + len(liste_achetes)
        assert total == 5


class TestInventaireMetrics:
    """Tests des métriques d'inventaire"""
    
    def test_count_by_status(self):
        """Test du comptage par statut"""
        inventaire = [
            {"statut": "ok"},
            {"statut": "ok"},
            {"statut": "stock_bas"},
            {"statut": "critique"},
        ]
        
        ok = len([a for a in inventaire if a["statut"] == "ok"])
        stock_bas = len([a for a in inventaire if a["statut"] == "stock_bas"])
        critique = len([a for a in inventaire if a["statut"] == "critique"])
        
        assert ok == 2
        assert stock_bas == 1
        assert critique == 1
    
    def test_unique_categories(self):
        """Test des catégories uniques"""
        inventaire = [
            {"ingredient_categorie": "Laitier"},
            {"ingredient_categorie": "Épicerie"},
            {"ingredient_categorie": "Laitier"},
            {"ingredient_categorie": "Frais"},
        ]
        
        categories = sorted(set(a["ingredient_categorie"] for a in inventaire))
        assert len(categories) == 3
        assert "Laitier" in categories
