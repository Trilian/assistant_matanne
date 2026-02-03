"""
Phase 15D - Tests Métier Supplémentaires

Expansion des tests Phase 15 pour atteindre 35% de couverture.
Cible: Services métier avec données réelles + workflows complets

Objectif: +3% couverture (32% → 35%)
"""

import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS DES RECETTES MÉTIER
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestRecettesMetier:
    """Tests complets des fonctionnalités recettes."""
    
    def test_recette_simple_creation(self, recette_factory):
        """Créer une recette simple et valider les propriétés."""
        recette = recette_factory.create(
            nom="Pâtes Carbonara",
            temps_preparation=15,
            temps_cuisson=20,
            portions=4
        )
        assert recette.nom == "Pâtes Carbonara"
        assert recette.temps_preparation == 15
        assert recette.temps_cuisson == 20
        assert recette.portions == 4
    
    def test_recette_avec_difficulte(self, recette_factory):
        """Tester les niveaux de difficulté."""
        facile = recette_factory.create(nom="Œuf dur", difficulte="facile")
        moyen = recette_factory.create(nom="Boeuf Bourguignon", difficulte="moyen")
        difficile = recette_factory.create(nom="Sauce Béarnaise", difficulte="difficile")
        
        assert facile.difficulte == "facile"
        assert moyen.difficulte == "moyen"
        assert difficile.difficulte == "difficile"
    
    def test_recette_par_saison(self, recette_factory):
        """Tester les recettes par saison."""
        printemps = recette_factory.create(nom="Salade légère", saison="printemps")
        ete = recette_factory.create(nom="Gazpacho", saison="été")
        automne = recette_factory.create(nom="Pot-au-feu", saison="automne")
        hiver = recette_factory.create(nom="Raclette", saison="hiver")
        
        assert printemps.saison == "printemps"
        assert ete.saison == "été"
        assert automne.saison == "automne"
        assert hiver.saison == "hiver"
    
    def test_recette_type_repas(self, recette_factory):
        """Tester les types de repas."""
        petit_dej = recette_factory.create(nom="Croissant", type_repas="petit-déjeuner")
        dejeuner = recette_factory.create(nom="Sandwich", type_repas="déjeuner")
        diner = recette_factory.create(nom="Gratin", type_repas="dîner")
        
        assert petit_dej.type_repas == "petit-déjeuner"
        assert dejeuner.type_repas == "déjeuner"
        assert diner.type_repas == "dîner"
    
    def test_recette_description_longue(self, recette_factory):
        """Tester une description détaillée."""
        desc = "Une délicieuse recette traditionnelle française avec des ingrédients de qualité."
        recette = recette_factory.create(
            nom="Coq au Vin",
            description=desc
        )
        assert recette.description == desc
    
    def test_recette_portions_variees(self, recette_factory):
        """Tester différents nombres de portions."""
        for portions in [1, 2, 4, 6, 8, 12]:
            recette = recette_factory.create(
                nom=f"Recette {portions}p",
                portions=portions
            )
            assert recette.portions == portions


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS DES INGRÉDIENTS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestIngredientsMetier:
    """Tests des ingrédients et catalogue."""
    
    def test_ingredient_categories(self, ingredient_factory):
        """Tester les catégories d'ingrédients."""
        categories = ["Fruits", "Légumes", "Protéines", "Produits laitiers", "Épices"]
        ingredients = []
        
        for cat in categories:
            ing = ingredient_factory.create(nom=f"Test_{cat}", categorie=cat)
            ingredients.append(ing)
        
        assert len(ingredients) == 5
        for i, ing in enumerate(ingredients):
            assert ing.categorie == categories[i]
    
    def test_ingredient_unites(self, ingredient_factory):
        """Tester les différentes unités de mesure."""
        unites = ["g", "kg", "ml", "L", "pièce", "cuillère à café", "tasse"]
        ingredients = []
        
        for unite in unites:
            ing = ingredient_factory.create(nom=f"Test_{unite}", unite=unite)
            ingredients.append(ing)
        
        assert len(ingredients) == 7
        for i, ing in enumerate(ingredients):
            assert ing.unite == unites[i]
    
    def test_ingredient_multiple_creation(self, ingredient_factory):
        """Créer et récupérer plusieurs ingrédients."""
        noms = ["Tomate", "Oignon", "Ail", "Poivron", "Courgette"]
        ingredients = [ingredient_factory.create(nom=nom) for nom in noms]
        
        assert len(ingredients) == 5
        for i, ing in enumerate(ingredients):
            assert ing.nom == noms[i]


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS DU PLANNING
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestPlanningMetier:
    """Tests complets du planning et des semaines."""
    
    def test_planning_semaine_complete(self, planning_factory):
        """Tester un planning d'une semaine complète."""
        debut = date(2026, 2, 2)  # Lundi
        planning = planning_factory.create(
            nom="Semaine du 2 février",
            semaine_debut=debut
        )
        
        assert planning.semaine_debut == debut
        assert planning.semaine_fin == debut + timedelta(days=6)
        assert planning.actif is True
    
    def test_planning_multiple_semaines(self, planning_factory):
        """Tester plusieurs plannings successifs."""
        plannings = []
        debut = date(2026, 2, 2)
        
        for i in range(4):
            sem_debut = debut + timedelta(weeks=i)
            planning = planning_factory.create(
                nom=f"Semaine {i+1}",
                semaine_debut=sem_debut
            )
            plannings.append(planning)
        
        assert len(plannings) == 4
        for i, planning in enumerate(plannings):
            expected_debut = debut + timedelta(weeks=i)
            assert planning.semaine_debut == expected_debut
    
    def test_planning_ia_vs_manuel(self, planning_factory):
        """Comparer plannings générés par IA vs manuels."""
        manuel = planning_factory.create(nom="Manuel", genere_par_ia=False)
        auto = planning_factory.create(nom="Auto IA", genere_par_ia=True)
        
        assert manuel.genere_par_ia is False
        assert auto.genere_par_ia is True
    
    def test_planning_dates_coherentes(self, planning_factory, db: Session):
        """Valider la cohérence des dates du planning."""
        planning = planning_factory.create(nom="Cohérent")
        
        # Vérifier que fin = début + 6 jours
        delta = planning.semaine_fin - planning.semaine_debut
        assert delta.days == 6


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS D'INVENTAIRE
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestInventaireMetier:
    """Tests de gestion d'inventaire."""
    
    def test_article_inventaire_creation(self, ingredient_factory, db: Session):
        """Créer un article d'inventaire."""
        from src.core.models import ArticleInventaire
        
        ing = ingredient_factory.create(nom="Farine")
        article = ArticleInventaire(
            ingredient_id=ing.id,
            quantite=1.5,
            quantite_min=0.5,
            emplacement="Placard cuisine"
        )
        db.add(article)
        db.commit()
        
        found = db.query(ArticleInventaire).filter_by(ingredient_id=ing.id).first()
        assert found is not None
        assert found.quantite == 1.5
        assert found.emplacement == "Placard cuisine"
    
    def test_stock_multiple_articles(self, ingredient_factory, db: Session):
        """Gérer plusieurs articles en stock."""
        from src.core.models import ArticleInventaire
        
        articles_data = [
            ("Riz", 2.0, "Placard"),
            ("Pâtes", 1.5, "Placard"),
            ("Huile d'olive", 0.5, "Étagère"),
        ]
        
        articles = []
        for nom, qty, lieu in articles_data:
            ing = ingredient_factory.create(nom=nom)
            article = ArticleInventaire(
                ingredient_id=ing.id,
                quantite=qty,
                quantite_min=0.2,
                emplacement=lieu
            )
            db.add(article)
            articles.append(article)
        
        db.commit()
        
        # Récupérer tous les articles
        all_articles = db.query(ArticleInventaire).all()
        assert len(all_articles) >= 3


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS DES LISTES DE COURSES
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestListesCoursesMetier:
    """Tests de gestion des listes de courses."""
    
    def test_article_courses_simple(self, ingredient_factory, db: Session):
        """Créer un article de liste de courses."""
        from src.core.models import ArticleCourses
        
        ing = ingredient_factory.create(nom="Tomate")
        article = ArticleCourses(
            ingredient_id=ing.id,
            quantite_necessaire=2.0,
            rayon_magasin="Fruits & Légumes"
        )
        db.add(article)
        db.commit()
        
        found = db.query(ArticleCourses).filter_by(ingredient_id=ing.id).first()
        assert found is not None
        assert found.quantite_necessaire == 2.0
        assert found.achete is False
    
    def test_liste_courses_complete(self, ingredient_factory, db: Session):
        """Créer une liste de courses complète."""
        from src.core.models import ArticleCourses
        
        courses_items = [
            ("Tomate", 1.5, "Fruits & Légumes", "haute"),
            ("Oignon", 0.5, "Fruits & Légumes", "moyenne"),
            ("Œufs", 12.0, "Laitier", "haute"),
            ("Pain", 1.0, "Boulangerie", "moyenne"),
            ("Lait", 1.0, "Laitier", "moyenne"),
        ]
        
        articles = []
        for nom, qty, rayon, priorite in courses_items:
            ing = ingredient_factory.create(nom=nom)
            article = ArticleCourses(
                ingredient_id=ing.id,
                quantite_necessaire=qty,
                rayon_magasin=rayon,
                priorite=priorite
            )
            db.add(article)
            articles.append(article)
        
        db.commit()
        
        # Compter les articles à haute priorité
        haute_priorite = db.query(ArticleCourses).filter_by(priorite="haute").all()
        assert len(haute_priorite) >= 2
    
    def test_article_courses_marqué_achete(self, ingredient_factory, db: Session):
        """Tester le marquage d'articles comme achetés."""
        from src.core.models import ArticleCourses
        
        ing = ingredient_factory.create(nom="Beurre")
        article = ArticleCourses(
            ingredient_id=ing.id,
            quantite_necessaire=0.250,
            achete=False
        )
        db.add(article)
        db.commit()
        
        # Marquer comme acheté
        article.achete = True
        db.commit()
        
        found = db.query(ArticleCourses).filter_by(ingredient_id=ing.id).first()
        assert found.achete is True


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS DE WORKFLOWS COMPLETS
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestWorkflowsComplets:
    """Tests des workflows métier complets."""
    
    def test_workflow_recette_vers_courses(self, recette_factory, ingredient_factory, db: Session):
        """Workflow: Créer recette → Ajouter ingrédients → Générer courses."""
        from src.core.models import Recette, Ingredient, ArticleCourses
        
        # 1. Créer recette
        recette = recette_factory.create(nom="Omelette déluxe")
        
        # 2. Créer ingrédients
        oeufs = ingredient_factory.create(nom="Œufs", unite="pièce")
        beurre = ingredient_factory.create(nom="Beurre", unite="g")
        fromage = ingredient_factory.create(nom="Fromage", unite="g")
        
        # 3. Générer article courses pour œufs
        article = ArticleCourses(
            ingredient_id=oeufs.id,
            quantite_necessaire=6.0,
            rayon_magasin="Laitier",
            priorite="haute"
        )
        db.add(article)
        db.commit()
        
        # Vérifications
        assert db.query(Recette).filter_by(nom="Omelette déluxe").first() is not None
        assert db.query(Ingredient).filter_by(nom="Œufs").first() is not None
        assert db.query(ArticleCourses).filter_by(ingredient_id=oeufs.id).first() is not None
    
    def test_workflow_planning_semaine(self, recette_factory, planning_factory, db: Session):
        """Workflow: Créer planning → Ajouter recettes."""
        from src.core.models import Planning, Recette
        
        # 1. Créer planning
        planning = planning_factory.create(nom="Semaine du 9 février")
        
        # 2. Créer recettes pour la semaine
        recettes_semaine = [
            recette_factory.create(nom="Pâtes", type_repas="dîner"),
            recette_factory.create(nom="Poisson", type_repas="dîner"),
            recette_factory.create(nom="Poulet", type_repas="dîner"),
        ]
        
        # Vérifications
        assert planning.nom == "Semaine du 9 février"
        assert len(recettes_semaine) == 3
        
        # Récupérer les recettes
        all_recipes = db.query(Recette).all()
        assert len(all_recipes) >= 3
    
    def test_workflow_inventaire_vers_courses(self, ingredient_factory, db: Session):
        """Workflow: Vérifier stock bas → Générer courses."""
        from src.core.models import ArticleInventaire, ArticleCourses
        
        # 1. Créer article en stock
        ing = ingredient_factory.create(nom="Lait")
        article_stock = ArticleInventaire(
            ingredient_id=ing.id,
            quantite=0.3,
            quantite_min=0.5,  # Stock bas
            emplacement="Frigo"
        )
        db.add(article_stock)
        db.commit()
        
        # 2. Créer article courses pour réapprovisionner
        article_courses = ArticleCourses(
            ingredient_id=ing.id,
            quantite_necessaire=1.0,
            rayon_magasin="Laitier"
        )
        db.add(article_courses)
        db.commit()
        
        # Vérifications
        found_stock = db.query(ArticleInventaire).filter_by(ingredient_id=ing.id).first()
        found_courses = db.query(ArticleCourses).filter_by(ingredient_id=ing.id).first()
        
        assert found_stock.quantite < found_stock.quantite_min  # Stock bas confirmé
        assert found_courses is not None


# ═══════════════════════════════════════════════════════════════════════════════════
# TESTS DE REQUÊTES COMPLEXES
# ═══════════════════════════════════════════════════════════════════════════════════

@pytest.mark.integration
class TestRequetesComplexes:
    """Tests des requêtes et filtres complexes."""
    
    def test_recettes_par_difficulte(self, recette_factory, db: Session):
        """Récupérer recettes filtrées par difficulté."""
        from src.core.models import Recette
        
        # Créer recettes de différentes difficultés
        for _ in range(2):
            recette_factory.create(nom="Simple", difficulte="facile")
        for _ in range(3):
            recette_factory.create(nom="Complexe", difficulte="difficile")
        
        # Récupérer par difficulté
        faciles = db.query(Recette).filter_by(difficulte="facile").all()
        difficiles = db.query(Recette).filter_by(difficulte="difficile").all()
        
        assert len(faciles) >= 2
        assert len(difficiles) >= 3
    
    def test_plannings_date_range(self, planning_factory, db: Session):
        """Récupérer plannings dans une plage de dates."""
        from src.core.models import Planning
        
        debut = date(2026, 2, 2)
        
        # Créer plusieurs plannings
        for i in range(4):
            sem_debut = debut + timedelta(weeks=i)
            planning_factory.create(
                nom=f"Planning {i}",
                semaine_debut=sem_debut
            )
        
        # Récupérer plannings actifs
        actifs = db.query(Planning).filter_by(actif=True).all()
        assert len(actifs) >= 4
    
    def test_articles_par_categorie(self, ingredient_factory, db: Session):
        """Récupérer articles par catégorie."""
        from src.core.models import Ingredient
        
        # Créer ingrédients de différentes catégories avec noms uniques
        for i in range(2):
            ingredient_factory.create(nom=f"Legume{i}", categorie="Légumes")
        for i in range(3):
            ingredient_factory.create(nom=f"Fruit{i}", categorie="Fruits")
        
        # Récupérer par catégorie
        legumes = db.query(Ingredient).filter_by(categorie="Légumes").all()
        fruits = db.query(Ingredient).filter_by(categorie="Fruits").all()
        
        assert len(legumes) >= 2
        assert len(fruits) >= 3
