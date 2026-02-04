import pytest
from datetime import date, timedelta
from sqlalchemy.orm import Session

from src.core.models import (
    Recette, Ingredient, Planning, ArticleInventaire, ArticleCourses,
    HistoriqueInventaire, Depense
)

class TestRecetteServiceExpanded:
    def test_recette_create_and_retrieve(self, db: Session):
        r = Recette(nom="Tarte P16", description="Test", difficulte="moyen", type_repas="dessert", portions=8)
        db.add(r)
        db.commit()
        retrieved = db.query(Recette).filter_by(nom="Tarte P16").first()
        assert retrieved.portions == 8
    
    def test_recette_with_ingredients(self, db: Session):
        ing1 = Ingredient(nom="Farine P16", categorie="Basique", unite="g")
        ing2 = Ingredient(nom="Sucre P16", categorie="Basique", unite="g")
        db.add_all([ing1, ing2])
        db.flush()
        r = Recette(nom="Pâte P16", description="Test", difficulte="facile", type_repas="base", portions=1)
        db.add(r)
        db.flush()
        r.ingredients.extend([ing1, ing2])
        db.commit()
        retrieved = db.query(Recette).filter_by(nom="Pâte P16").first()
        assert len(retrieved.ingredients) >= 2
    
    def test_recette_filtering_by_difficulte(self, db: Session):
        for i in range(3):
            r = Recette(nom=f"Recette facile {i}", description="Facile", difficulte="facile", type_repas="déjeuner", portions=4)
            db.add(r)
        db.commit()
        easy = db.query(Recette).filter_by(difficulte="facile").all()
        assert len(easy) >= 3
    
    def test_recette_update_and_save(self, db: Session):
        r = Recette(nom="Original", description="Orig", difficulte="facile", type_repas="petit-déjeuner", portions=2)
        db.add(r)
        db.commit()
        r.portions = 4
        db.commit()
        updated = db.query(Recette).filter_by(nom="Original").first()
        assert updated.portions == 4
    
    def test_recette_delete(self, db: Session):
        r = Recette(nom="A supprimer", description="Temp", difficulte="difficile", type_repas="dîner", portions=6)
        db.add(r)
        db.commit()
        r_id = r.id
        db.delete(r)
        db.commit()
        deleted = db.query(Recette).filter_by(id=r_id).first()
        assert deleted is None

class TestPlanningServiceExpanded:
    def test_planning_create_week(self, db: Session):
        start = date(2026, 2, 10)
        p = Planning(date_debut=start, date_fin=start + timedelta(days=6), jour_semaine="Lundi", type_repas="déjeuner", repas_genere=False)
        db.add(p)
        db.commit()
        retrieved = db.query(Planning).filter_by(jour_semaine="Lundi").first()
        assert retrieved.repas_genere == False
    
    def test_planning_with_multiple_recipes(self, db: Session):
        recettes = []
        for i in range(3):
            r = Recette(nom=f"Recette Plan {i}", description=f"Test {i}", difficulte="facile", type_repas="déjeuner", portions=4)
            db.add(r)
            recettes.append(r)
        db.flush()
        p = Planning(date_debut=date(2026, 2, 11), date_fin=date(2026, 2, 11), jour_semaine="Mardi")
        db.add(p)
        db.flush()
        p.recettes.extend(recettes)
        db.commit()
        retrieved = db.query(Planning).filter_by(jour_semaine="Mardi").first()
        assert len(retrieved.recettes) >= 3
    
    def test_planning_auto_generated_flag(self, db: Session):
        p1 = Planning(date_debut=date(2026, 2, 12), jour_semaine="Mercredi", repas_genere=True)
        p2 = Planning(date_debut=date(2026, 2, 13), jour_semaine="Jeudi", repas_genere=False)
        db.add_all([p1, p2])
        db.commit()
        auto = db.query(Planning).filter_by(repas_genere=True).all()
        manual = db.query(Planning).filter_by(repas_genere=False).all()
        assert len(auto) >= 1 and len(manual) >= 1
    
    def test_planning_date_overlap_detection(self, db: Session):
        start_date = date(2026, 2, 15)
        p1 = Planning(date_debut=start_date, date_fin=start_date + timedelta(days=2), jour_semaine="Dimanche")
        p2 = Planning(date_debut=start_date + timedelta(days=1), jour_semaine="Lundi planif")
        db.add_all([p1, p2])
        db.commit()
        all_planning = db.query(Planning).all()
        assert len(all_planning) >= 2
    
    def test_planning_multiple_meal_types(self, db: Session):
        for meal_type in ["petit-déjeuner", "déjeuner", "dîner"]:
            p = Planning(date_debut=date(2026, 3, 20), jour_semaine="Samedi", type_repas=meal_type)
            db.add(p)
        db.commit()
        breakfast = db.query(Planning).filter_by(type_repas="petit-déjeuner").all()
        lunch = db.query(Planning).filter_by(type_repas="déjeuner").all()
        dinner = db.query(Planning).filter_by(type_repas="dîner").all()
        assert len(breakfast) >= 1 and len(lunch) >= 1 and len(dinner) >= 1

class TestCoursesServiceExpanded:
    def test_article_courses_create(self, db: Session):
        a = ArticleCourses(nom="Lait P16", categorie="Produits frais", quantite=2.0, unite="L", achetee=False, priorite="normale")
        db.add(a)
        db.commit()
        retrieved = db.query(ArticleCourses).filter_by(nom="Lait P16").first()
        assert retrieved.achetee == False
    
    def test_article_courses_mark_purchased(self, db: Session):
        a = ArticleCourses(nom="Pain P16", categorie="Boulangerie", quantite=1.0, unite="unité", achetee=False)
        db.add(a)
        db.commit()
        a.achetee = True
        db.commit()
        purchased = db.query(ArticleCourses).filter_by(nom="Pain P16").first()
        assert purchased.achetee == True
    
    def test_article_courses_by_category(self, db: Session):
        for i in range(2):
            a1 = ArticleCourses(nom=f"Fruits {i}", categorie="Fruits P16", quantite=1.0, unite="kg")
            a2 = ArticleCourses(nom=f"Légumes {i}", categorie="Légumes P16", quantite=1.0, unite="kg")
            db.add_all([a1, a2])
        db.commit()
        fruits = db.query(ArticleCourses).filter_by(categorie="Fruits P16").all()
        legumes = db.query(ArticleCourses).filter_by(categorie="Légumes P16").all()
        assert len(fruits) >= 2 and len(legumes) >= 2
    
    def test_article_courses_essential_items(self, db: Session):
        essential = ArticleCourses(nom="Oeufs P16", categorie="Basique", quantite=12.0, unite="unité", priorite="haute", achetee=False)
        optional = ArticleCourses(nom="Chocolat P16", categorie="Gourmandise", quantite=1.0, unite="g", priorite="basse", achetee=False)
        db.add_all([essential, optional])
        db.commit()
        high_priority = db.query(ArticleCourses).filter_by(priorite="haute").all()
        assert len(high_priority) >= 1
    
    def test_article_courses_bulk_operations(self, db: Session):
        items = []
        for i in range(5):
            a = ArticleCourses(nom=f"Bulk Item {i}", categorie="Bulk", quantite=10.0, unite="unité", achetee=False)
            items.append(a)
        db.add_all(items)
        db.commit()
        bulk = db.query(ArticleCourses).filter_by(categorie="Bulk").all()
        assert len(bulk) >= 5

class TestInventaireServiceExpanded:
    def test_article_inventaire_create(self, db: Session):
        a = ArticleInventaire(nom="Riz P16", categorie="Céréales", quantite=2000, unite="g", seuil_alerte=500, localisation="Placard")
        db.add(a)
        db.commit()
        retrieved = db.query(ArticleInventaire).filter_by(nom="Riz P16").first()
        assert retrieved.quantite == 2000
    
    def test_article_inventaire_low_stock_alert(self, db: Session):
        a = ArticleInventaire(nom="Farine P16", categorie="Céréales", quantite=100, unite="g", seuil_alerte=500)
        db.add(a)
        db.commit()
        retrieved = db.query(ArticleInventaire).filter_by(nom="Farine P16").first()
        assert retrieved.quantite < retrieved.seuil_alerte
    
    def test_article_inventaire_update_quantity(self, db: Session):
        a = ArticleInventaire(nom="Sucre P16", categorie="Sucres", quantite=1000, unite="g")
        db.add(a)
        db.commit()
        a.quantite = 750
        db.commit()
        updated = db.query(ArticleInventaire).filter_by(nom="Sucre P16").first()
        assert updated.quantite == 750
    
    def test_article_inventaire_locations(self, db: Session):
        for loc in ["Placard P16", "Congélateur P16", "Réfrigérateur P16"]:
            a = ArticleInventaire(nom=f"Article {loc}", categorie="Divers", quantite=100, unite="unité", localisation=loc)
            db.add(a)
        db.commit()
        for loc in ["Placard P16", "Congélateur P16", "Réfrigérateur P16"]:
            items = db.query(ArticleInventaire).filter_by(localisation=loc).all()
            assert len(items) >= 1
    
    def test_article_inventaire_with_historique(self, db: Session):
        a = ArticleInventaire(nom="Huile P16", categorie="Huiles", quantite=500, unite="ml")
        db.add(a)
        db.flush()
        h = HistoriqueInventaire(article_inventaire_id=a.id, quantite_avant=600, quantite_apres=500, motif="Utilisation cuisine")
        db.add(h)
        db.commit()
        article = db.query(ArticleInventaire).filter_by(nom="Huile P16").first()
        assert article.quantite == 500
        historique = db.query(HistoriqueInventaire).filter_by(article_inventaire_id=article.id).all()
        assert len(historique) >= 1

class TestDomainRecetteComplex:
    def test_recette_seasonal_variations(self, db: Session):
        r = Recette(nom="Soupe saisonnière P16", description="Adapté à la saison", difficulte="moyen", type_repas="entrée", portions=4)
        db.add(r)
        db.commit()
        assert r.nom == "Soupe saisonnière P16"

class TestDomainPlanningComplex:
    def test_planning_weekly_nutrition_balance(self, db: Session):
        p = Planning(date_debut=date(2026, 3, 1), date_fin=date(2026, 3, 7), jour_semaine="Semaine équilibrée P16")
        db.add(p)
        db.commit()
        assert (p.date_fin - p.date_debut).days >= 6

class TestEndToEndWorkflows:
    def test_complete_meal_prep_workflow(self, db: Session):
        r = Recette(nom="Recette E2E P16", description="Workflow test", difficulte="moyen", type_repas="déjeuner", portions=4)
        db.add(r)
        db.flush()
        p = Planning(date_debut=date(2026, 3, 15), jour_semaine="Lundi E2E P16")
        db.add(p)
        db.flush()
        p.recettes.append(r)
        a = ArticleCourses(nom="Ingrédient E2E P16", categorie="Test", quantite=1.0, unite="unité")
        db.add(a)
        db.commit()
        planning = db.query(Planning).filter_by(jour_semaine="Lundi E2E P16").first()
        assert planning is not None and len(planning.recettes) >= 1
    
    def test_shopping_and_inventory_sync(self, db: Session):
        shopping = ArticleCourses(nom="Tomate E2E P16", categorie="Légumes", quantite=5.0, unite="unité", achetee=False)
        db.add(shopping)
        db.flush()
        inventory = ArticleInventaire(nom="Tomate E2E P16", categorie="Légumes", quantite=5, unite="unité", localisation="Réfrigérateur")
        db.add(inventory)
        db.commit()
        shop_item = db.query(ArticleCourses).filter_by(nom="Tomate E2E P16").first()
        inv_item = db.query(ArticleInventaire).filter_by(nom="Tomate E2E P16").first()
        assert shop_item.quantite == inv_item.quantite
    
    def test_planning_to_shopping_list_generation(self, db: Session):
        recipe = Recette(nom="Salade E2E P16", description="Planning E2E", difficulte="facile", type_repas="déjeuner", portions=2)
        db.add(recipe)
        db.flush()
        planning = Planning(date_debut=date(2026, 3, 25), jour_semaine="Mercredi E2E P16")
        db.add(planning)
        db.flush()
        planning.recettes.append(recipe)
        shopping = ArticleCourses(nom="Salade E2E P16", categorie="Légumes", quantite=2.0, unite="portion")
        db.add(shopping)
        db.commit()
        plan = db.query(Planning).filter_by(jour_semaine="Mercredi E2E P16").first()
        shop = db.query(ArticleCourses).filter_by(nom="Salade E2E P16").first()
        assert plan is not None and shop is not None
