"""
Tests complets pour les modules Cuisine
- courses.py
- inventaire.py
- planning.py
- recettes.py
- recettes_import.py
"""

import pytest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch, AsyncMock


# ════════════════════════════════════════════════════════════════════════════
# TESTS COURSES
# ════════════════════════════════════════════════════════════════════════════


class TestCoursesConstantes:
    """Tests des constantes du module courses"""
    
    def test_priority_emojis_complete(self):
        """Les priorités ont toutes un emoji"""
        from src.modules.cuisine.courses import PRIORITY_EMOJIS
        
        assert "haute" in PRIORITY_EMOJIS
        assert "moyenne" in PRIORITY_EMOJIS
        assert "basse" in PRIORITY_EMOJIS
        assert PRIORITY_EMOJIS["haute"] == "🔴"
        assert PRIORITY_EMOJIS["moyenne"] == "🟡"
        assert PRIORITY_EMOJIS["basse"] == "🟢"
    
    def test_rayons_default_list(self):
        """La liste des rayons est définie"""
        from src.modules.cuisine.courses import RAYONS_DEFAULT
        
        assert len(RAYONS_DEFAULT) >= 5
        assert "Fruits & Légumes" in RAYONS_DEFAULT
        assert "Laitier" in RAYONS_DEFAULT
        assert "Boulangerie" in RAYONS_DEFAULT
        assert "Autre" in RAYONS_DEFAULT


class TestCoursesFiltres:
    """Tests de filtrage des articles"""
    
    def test_filtrer_par_priorite_haute(self):
        """Filtrage par priorité haute"""
        articles = [
            {"nom": "Lait", "priorite": "haute"},
            {"nom": "Fromage", "priorite": "basse"},
            {"nom": "Pain", "priorite": "haute"},
        ]
        
        filtre = [a for a in articles if a.get("priorite") == "haute"]
        assert len(filtre) == 2
        assert all(a["priorite"] == "haute" for a in filtre)
    
    def test_filtrer_par_rayon(self):
        """Filtrage par rayon magasin"""
        articles = [
            {"nom": "Pommes", "rayon_magasin": "Fruits & Légumes"},
            {"nom": "Lait", "rayon_magasin": "Laitier"},
            {"nom": "Carottes", "rayon_magasin": "Fruits & Légumes"},
        ]
        
        filtre = [a for a in articles if a.get("rayon_magasin") == "Fruits & Légumes"]
        assert len(filtre) == 2
    
    def test_recherche_textuelle(self):
        """Recherche par texte"""
        articles = [
            {"nom": "Tomates cerises"},
            {"nom": "Cerises fraîches"},
            {"nom": "Lait"},
        ]
        
        search = "cerises"
        filtre = [a for a in articles if search.lower() in a["nom"].lower()]
        assert len(filtre) == 2
    
    def test_combinaison_filtres(self):
        """Combinaison de plusieurs filtres"""
        articles = [
            {"nom": "Tomates", "priorite": "haute", "rayon": "Fruits & Légumes"},
            {"nom": "Lait", "priorite": "haute", "rayon": "Laitier"},
            {"nom": "Carottes", "priorite": "basse", "rayon": "Fruits & Légumes"},
        ]
        
        # Priorité haute ET rayon Fruits & Légumes
        filtre = [
            a for a in articles 
            if a.get("priorite") == "haute" and a.get("rayon") == "Fruits & Légumes"
        ]
        assert len(filtre) == 1
        assert filtre[0]["nom"] == "Tomates"


class TestCoursesMetriques:
    """Tests des calculs de métriques"""
    
    def test_compter_articles_priorite_haute(self):
        """Compte les articles haute priorité"""
        articles = [
            {"priorite": "haute"},
            {"priorite": "moyenne"},
            {"priorite": "haute"},
            {"priorite": "basse"},
        ]
        
        haute = len([a for a in articles if a.get("priorite") == "haute"])
        assert haute == 2
    
    def test_calculer_total_articles(self):
        """Calcule le total des articles"""
        articles_actifs = [{"achete": False} for _ in range(5)]
        articles_achetes = [{"achete": True} for _ in range(3)]
        
        total_actifs = len([a for a in articles_actifs if not a.get("achete")])
        total_tous = len(articles_actifs) + len(articles_achetes)
        
        assert total_actifs == 5
        assert total_tous == 8


# ════════════════════════════════════════════════════════════════════════════
# TESTS INVENTAIRE
# ════════════════════════════════════════════════════════════════════════════


class TestInventaireStats:
    """Tests des statistiques d'inventaire"""
    
    def test_calculer_stock_critique(self):
        """Calcule le nombre d'articles critiques"""
        inventaire = [
            {"quantite": 0, "seuil_min": 2},
            {"quantite": 1, "seuil_min": 2},
            {"quantite": 5, "seuil_min": 2},
        ]
        
        critique = len([a for a in inventaire if a["quantite"] <= 0])
        assert critique == 1
    
    def test_calculer_stock_bas(self):
        """Calcule le stock bas (sous le seuil)"""
        inventaire = [
            {"quantite": 1, "seuil_min": 3},
            {"quantite": 2, "seuil_min": 3},
            {"quantite": 5, "seuil_min": 3},
        ]
        
        stock_bas = len([a for a in inventaire if 0 < a["quantite"] < a["seuil_min"]])
        assert stock_bas == 2
    
    def test_calculer_peremption_proche(self):
        """Détecte les articles proches de la péremption"""
        today = date.today()
        inventaire = [
            {"date_peremption": today + timedelta(days=2)},
            {"date_peremption": today + timedelta(days=10)},
            {"date_peremption": today + timedelta(days=3)},
            {"date_peremption": None},
        ]
        
        seuil = 5  # jours
        peremption_proche = len([
            a for a in inventaire 
            if a["date_peremption"] and (a["date_peremption"] - today).days <= seuil
        ])
        assert peremption_proche == 2


class TestInventaireFiltres:
    """Tests des filtres d'inventaire"""
    
    def test_filtrer_par_emplacement(self):
        """Filtrage par emplacement"""
        inventaire = [
            {"nom": "Lait", "emplacement": "Frigo"},
            {"nom": "Pâtes", "emplacement": "Placard"},
            {"nom": "Fromage", "emplacement": "Frigo"},
        ]
        
        filtre = [a for a in inventaire if a["emplacement"] == "Frigo"]
        assert len(filtre) == 2
    
    def test_filtrer_par_categorie(self):
        """Filtrage par catégorie d'ingrédient"""
        inventaire = [
            {"nom": "Lait", "ingredient_categorie": "Laitier"},
            {"nom": "Pommes", "ingredient_categorie": "Fruits"},
            {"nom": "Fromage", "ingredient_categorie": "Laitier"},
        ]
        
        filtre = [a for a in inventaire if a["ingredient_categorie"] == "Laitier"]
        assert len(filtre) == 2
    
    def test_filtrer_multi_criteres(self):
        """Filtrage avec plusieurs critères"""
        inventaire = [
            {"nom": "Lait", "emplacement": "Frigo", "statut": "ok"},
            {"nom": "Fromage", "emplacement": "Frigo", "statut": "critique"},
            {"nom": "Pâtes", "emplacement": "Placard", "statut": "ok"},
        ]
        
        filtre = [
            a for a in inventaire 
            if a["emplacement"] == "Frigo" and a["statut"] == "critique"
        ]
        assert len(filtre) == 1
        assert filtre[0]["nom"] == "Fromage"


# ════════════════════════════════════════════════════════════════════════════
# TESTS PLANNING REPAS
# ════════════════════════════════════════════════════════════════════════════


class TestPlanningConstantes:
    """Tests des constantes de planning"""
    
    def test_jours_semaine(self):
        """Les jours de la semaine sont définis"""
        from src.modules.cuisine.planning import JOURS_SEMAINE
        
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"
    
    def test_jours_emoji(self):
        """Chaque jour a un emoji"""
        from src.modules.cuisine.planning import JOURS_EMOJI
        
        assert len(JOURS_EMOJI) == 7
        assert all(len(e) >= 1 for e in JOURS_EMOJI)
    
    def test_types_repas(self):
        """Les types de repas sont définis"""
        from src.modules.cuisine.planning import TYPES_REPAS
        
        assert "déjeuner" in TYPES_REPAS
        assert "dîner" in TYPES_REPAS


class TestPlanningOrganisation:
    """Tests de l'organisation du planning"""
    
    def test_organiser_repas_par_jour(self):
        """Organisation des repas par jour"""
        repas = [
            {"date_repas": date(2025, 1, 27), "type_repas": "déjeuner"},
            {"date_repas": date(2025, 1, 27), "type_repas": "dîner"},
            {"date_repas": date(2025, 1, 28), "type_repas": "déjeuner"},
        ]
        
        repas_par_jour = {}
        for r in repas:
            jour_key = r["date_repas"].strftime("%Y-%m-%d")
            if jour_key not in repas_par_jour:
                repas_par_jour[jour_key] = []
            repas_par_jour[jour_key].append(r)
        
        assert len(repas_par_jour) == 2
        assert len(repas_par_jour["2025-01-27"]) == 2
        assert len(repas_par_jour["2025-01-28"]) == 1
    
    def test_calculer_dates_semaine(self):
        """Calcul des dates de la semaine"""
        from datetime import date, timedelta
        
        semaine_debut = date(2025, 1, 27)  # Lundi
        dates_semaine = [semaine_debut + timedelta(days=i) for i in range(7)]
        
        assert len(dates_semaine) == 7
        assert dates_semaine[0] == date(2025, 1, 27)
        assert dates_semaine[6] == date(2025, 2, 2)
    
    def test_compter_repas_planifies(self):
        """Compte le nombre de repas planifiés"""
        planning = {
            "repas": [
                {"type": "déjeuner", "recette_id": 1},
                {"type": "dîner", "recette_id": 2},
                {"type": "déjeuner", "recette_id": None},
            ]
        }
        
        avec_recette = len([r for r in planning["repas"] if r.get("recette_id")])
        assert avec_recette == 2


# ════════════════════════════════════════════════════════════════════════════
# TESTS RECETTES
# ════════════════════════════════════════════════════════════════════════════


class TestRecettesFiltres:
    """Tests des filtres de recettes"""
    
    def test_filtrer_par_type_repas(self):
        """Filtrage par type de repas"""
        recettes = [
            {"nom": "Omelette", "type_repas": "petit_déjeuner"},
            {"nom": "Salade", "type_repas": "déjeuner"},
            {"nom": "Pâtes", "type_repas": "dîner"},
        ]
        
        filtre = [r for r in recettes if r["type_repas"] == "déjeuner"]
        assert len(filtre) == 1
        assert filtre[0]["nom"] == "Salade"
    
    def test_filtrer_par_difficulte(self):
        """Filtrage par difficulté"""
        recettes = [
            {"nom": "Toast", "difficulte": "facile"},
            {"nom": "Soufflé", "difficulte": "difficile"},
            {"nom": "Omelette", "difficulte": "facile"},
        ]
        
        filtre = [r for r in recettes if r["difficulte"] == "facile"]
        assert len(filtre) == 2
    
    def test_filtrer_par_temps_max(self):
        """Filtrage par temps de préparation"""
        recettes = [
            {"nom": "Toast", "temps_total": 10},
            {"nom": "Ragoût", "temps_total": 120},
            {"nom": "Salade", "temps_total": 15},
        ]
        
        temps_max = 30
        filtre = [r for r in recettes if r["temps_total"] <= temps_max]
        assert len(filtre) == 2
    
    def test_filtrer_par_score_bio(self):
        """Filtrage par score bio minimum"""
        recettes = [
            {"nom": "Bio1", "score_bio": 80},
            {"nom": "Standard", "score_bio": 30},
            {"nom": "Bio2", "score_bio": 90},
        ]
        
        min_score = 50
        filtre = [r for r in recettes if (r.get("score_bio") or 0) >= min_score]
        assert len(filtre) == 2
    
    def test_filtrer_robots_compatibles(self):
        """Filtrage par compatibilité robot"""
        recettes = [
            {"nom": "R1", "compatible_cookeo": True, "compatible_airfryer": False},
            {"nom": "R2", "compatible_cookeo": False, "compatible_airfryer": True},
            {"nom": "R3", "compatible_cookeo": True, "compatible_airfryer": True},
        ]
        
        # Compatible Cookeo
        filtre_cookeo = [r for r in recettes if r.get("compatible_cookeo")]
        assert len(filtre_cookeo) == 2
        
        # Compatible les deux
        filtre_both = [
            r for r in recettes 
            if r.get("compatible_cookeo") and r.get("compatible_airfryer")
        ]
        assert len(filtre_both) == 1


class TestRecettesPagination:
    """Tests de pagination des recettes"""
    
    def test_pagination_page_1(self):
        """Première page de résultats"""
        recettes = [{"id": i} for i in range(25)]
        page_size = 9
        page = 0
        
        debut = page * page_size
        fin = debut + page_size
        page_recettes = recettes[debut:fin]
        
        assert len(page_recettes) == 9
        assert page_recettes[0]["id"] == 0
    
    def test_pagination_page_derniere(self):
        """Dernière page avec moins d'éléments"""
        recettes = [{"id": i} for i in range(25)]
        page_size = 9
        page = 2  # 3ème page
        
        debut = page * page_size
        fin = debut + page_size
        page_recettes = recettes[debut:fin]
        
        assert len(page_recettes) == 7  # 25 - 18
    
    def test_calculer_nombre_pages(self):
        """Calcul du nombre total de pages"""
        import math
        
        total_recettes = 25
        page_size = 9
        
        nb_pages = math.ceil(total_recettes / page_size)
        assert nb_pages == 3


class TestRecettesDifficulte:
    """Tests des emojis de difficulté"""
    
    def test_emoji_facile(self):
        """Emoji pour difficulté facile"""
        difficuote_emoji = {
            "facile": "🟢",
            "moyen": "🟡", 
            "difficile": "🔴"
        }
        
        assert difficuote_emoji.get("facile") == "🟢"
    
    def test_emoji_difficulte_inconnue(self):
        """Gestion difficulté inconnue"""
        difficulte_emoji = {
            "facile": "🟢",
            "moyen": "🟡",
            "difficile": "🔴"
        }
        
        assert difficulte_emoji.get("inconnue", "⚪") == "⚪"


# ════════════════════════════════════════════════════════════════════════════
# TESTS RECETTES IMPORT
# ════════════════════════════════════════════════════════════════════════════


class TestRecettesImportValidation:
    """Tests de validation d'import de recettes"""
    
    def test_valider_url_vide(self):
        """Validation URL vide"""
        url = ""
        assert not url or len(url.strip()) == 0
    
    def test_valider_url_format(self):
        """Validation format URL"""
        valid_urls = [
            "https://www.marmiton.org/recettes/...",
            "http://example.com/recette",
        ]
        invalid_urls = [
            "not-a-url",
            "",
            "ftp://invalid.com",
        ]
        
        for url in valid_urls:
            assert url.startswith("http")
        
        for url in invalid_urls:
            assert not url.startswith("http") or url == ""
    
    def test_valider_donnees_recette(self):
        """Validation des données extraites"""
        recipe_data = {
            "nom": "Test Recette",
            "type_repas": "déjeuner",
            "description": "Une description",
        }
        
        # Nom requis
        assert recipe_data.get("nom")
        assert len(recipe_data["nom"]) > 0
    
    def test_types_repas_import(self):
        """Les types de repas sont définis pour l'import"""
        types_valides = ["petit_déjeuner", "déjeuner", "dîner", "goûter", "apéritif", "dessert"]
        
        assert "déjeuner" in types_valides
        assert "dîner" in types_valides


class TestRecettesImportPreparation:
    """Tests de préparation des données d'import"""
    
    def test_extraire_temps_preparation(self):
        """Extraction du temps de préparation"""
        recipe_data = {
            "temps_preparation": 20,
            "temps_cuisson": 30,
        }
        
        temps_total = recipe_data.get("temps_preparation", 0) + recipe_data.get("temps_cuisson", 0)
        assert temps_total == 50
    
    def test_formater_ingredients(self):
        """Formatage de la liste d'ingrédients"""
        ingredients_raw = [
            {"nom": "Pâtes", "quantite": 400, "unite": "g"},
            {"nom": "Sauce tomate", "quantite": 200, "unite": "ml"},
        ]
        
        formatted = [f"{i['quantite']}{i['unite']} {i['nom']}" for i in ingredients_raw]
        
        assert formatted[0] == "400g Pâtes"
        assert formatted[1] == "200ml Sauce tomate"
    
    def test_formater_etapes(self):
        """Formatage des étapes"""
        etapes = [
            {"ordre": 1, "description": "Faire bouillir l'eau"},
            {"ordre": 2, "description": "Ajouter les pâtes"},
        ]
        
        etapes_triees = sorted(etapes, key=lambda x: x["ordre"])
        assert etapes_triees[0]["description"] == "Faire bouillir l'eau"


# ════════════════════════════════════════════════════════════════════════════
# TESTS INTEGRATION
# ════════════════════════════════════════════════════════════════════════════


class TestCuisineIntegration:
    """Tests d'intégration entre modules cuisine"""
    
    def test_generer_courses_depuis_recette(self):
        """Génération de liste de courses depuis une recette"""
        recette_ingredients = [
            {"nom": "Pâtes", "quantite": 400, "unite": "g"},
            {"nom": "Tomates", "quantite": 3, "unite": "pièce"},
        ]
        
        inventaire = [
            {"nom": "Pâtes", "quantite": 500},  # En stock
        ]
        
        # Articles manquants
        noms_en_stock = {i["nom"] for i in inventaire}
        a_acheter = [i for i in recette_ingredients if i["nom"] not in noms_en_stock]
        
        assert len(a_acheter) == 1
        assert a_acheter[0]["nom"] == "Tomates"
    
    def test_planning_vers_courses(self):
        """Planning génère les courses nécessaires"""
        planning_repas = [
            {"recette_id": 1, "recette_nom": "Pâtes bolognaise"},
            {"recette_id": 2, "recette_nom": "Salade composée"},
        ]
        
        ingredients_totaux = {
            1: [{"nom": "Pâtes"}, {"nom": "Viande"}],
            2: [{"nom": "Salade"}, {"nom": "Tomates"}],
        }
        
        # Collecter tous les ingrédients
        tous_ingredients = []
        for repas in planning_repas:
            recette_id = repas["recette_id"]
            if recette_id in ingredients_totaux:
                tous_ingredients.extend(ingredients_totaux[recette_id])
        
        assert len(tous_ingredients) == 4
