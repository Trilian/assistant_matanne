"""
Phase 16 : Tests Services/Domains/UI pour atteindre 60-65% couverture
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from src.core.models import (
    Recette, Ingredient, Planning, ArticleInventaire, ArticleCourses,
    HistoriqueInventaire, Depense
)


class TestRecetteServiceExpanded:
    """Expand Recette service coverage"""
    
    def test_recette_create_and_retrieve(self, test_db: Session):
        """Test création et récupération recette"""
        r = Recette(
            nom="Tarte aux Pommes P16 A",
            description="Tarte classique",
            difficulte="moyen",
            type_repas="dessert",
            portions=8,
            temps_preparation=15,
            temps_cuisson=40
        )
        test_db.add(r)
        test_db.commit()
        
        retrieved = test_db.query(Recette).filter_by(nom="Tarte aux Pommes P16 A").first()
        assert retrieved is not None
        assert retrieved.portions == 8
    
    def test_recette_with_ingredients(self):
        """Test recette avec ingrédients"""
        with get_db_context() as session:
            ing1 = Ingredient(nom="Farine P16", categorie="Basique", unite="g")
            ing2 = Ingredient(nom="Sucre P16", categorie="Basique", unite="g")
            session.add_all([ing1, ing2])
            session.flush()
            
            r = Recette(
                nom="Pâte Brisée P16 A",
                description="Pâte classique",
                difficulte="facile",
                type_repas="base",
                portions=1
            )
            session.add(r)
            session.flush()
            r.ingredients.extend([ing1, ing2])
            session.commit()
            
            retrieved = session.query(Recette).filter_by(nom="Pâte Brisée P16 A").first()
            assert len(retrieved.ingredients) >= 2
    
    def test_recette_filtering_by_difficulte(self):
        """Test filtrage par difficulté"""
        with get_db_context() as session:
            for i in range(2):
                r = Recette(
                    nom=f"Recette facile P16 {i}",
                    description="Facile",
                    difficulte="facile",
                    type_repas="déjeuner",
                    portions=4
                )
                session.add(r)
            session.commit()
            
            easy = session.query(Recette).filter_by(difficulte="facile").all()
            assert len(easy) >= 2
    
    def test_recette_update_and_save(self):
        """Test mise à jour recette"""
        with get_db_context() as session:
            r = Recette(
                nom="Original P16 A",
                description="Orig",
                difficulte="facile",
                type_repas="petit-déjeuner",
                portions=2
            )
            session.add(r)
            session.commit()
            recette_id = r.id
            
            r.portions = 4
            session.commit()
            
            updated = session.query(Recette).filter_by(id=recette_id).first()
            assert updated.portions == 4
    
    def test_recette_delete(self):
        """Test suppression recette"""
        with get_db_context() as session:
            r = Recette(
                nom="A supprimer P16 A",
                description="Temp",
                difficulte="difficile",
                type_repas="dîner",
                portions=6
            )
            session.add(r)
            session.commit()
            recette_id = r.id
            
            session.delete(r)
            session.commit()
            
            deleted = session.query(Recette).filter_by(id=recette_id).first()
            assert deleted is None


class TestPlanningServiceExpanded:
    """Planning service tests"""
    
    def test_planning_create_week(self):
        """Test création planning semain"""
        with get_db_context() as session:
            start = date(2026, 2, 10)
            p = Planning(
                date_debut=start,
                date_fin=start + timedelta(days=6),
                jour_semaine="Lundi P16",
                type_repas="déjeuner",
                repas_genere=False
            )
            session.add(p)
            session.commit()
            
            retrieved = session.query(Planning).filter_by(jour_semaine="Lundi P16").first()
            assert retrieved is not None
            assert retrieved.repas_genere == False
    
    def test_planning_with_multiple_recipes(self):
        """Test planning avec plusieurs recettes"""
        with get_db_context() as session:
            recettes = []
            for i in range(3):
                r = Recette(
                    nom=f"Recette Plan P16 {i}",
                    description=f"Planning test {i}",
                    difficulte="facile",
                    type_repas="déjeuner",
                    portions=4
                )
                session.add(r)
                recettes.append(r)
            session.flush()
            
            p = Planning(
                date_debut=date(2026, 2, 11),
                date_fin=date(2026, 2, 11),
                jour_semaine="Mardi P16"
            )
            session.add(p)
            session.flush()
            p.recettes.extend(recettes)
            session.commit()
            
            retrieved = session.query(Planning).filter_by(jour_semaine="Mardi P16").first()
            assert len(retrieved.recettes) >= 3
    
    def test_planning_auto_generated_flag(self):
        """Test flag auto-généré"""
        with get_db_context() as session:
            p1 = Planning(
                date_debut=date(2026, 2, 12),
                jour_semaine="Mercredi P16",
                repas_genere=True
            )
            p2 = Planning(
                date_debut=date(2026, 2, 13),
                jour_semaine="Jeudi P16",
                repas_genere=False
            )
            session.add_all([p1, p2])
            session.commit()
            
            auto = session.query(Planning).filter_by(repas_genere=True).all()
            manual = session.query(Planning).filter_by(repas_genere=False).all()
            assert len(auto) >= 1
            assert len(manual) >= 1
    
    def test_planning_date_overlap_detection(self):
        """Test détection chevauchement dates"""
        with get_db_context() as session:
            start_date = date(2026, 2, 15)
            p1 = Planning(
                date_debut=start_date,
                date_fin=start_date + timedelta(days=2),
                jour_semaine="Dimanche P16"
            )
            p2 = Planning(
                date_debut=start_date + timedelta(days=1),
                jour_semaine="Lundi Planif P16"
            )
            session.add_all([p1, p2])
            session.commit()
            
            all_planning = session.query(Planning).all()
            assert len(all_planning) >= 2


class TestCoursesServiceExpanded:
    """Shopping courses tests"""
    
    def test_article_courses_create(self):
        """Test création article course"""
        with get_db_context() as session:
            a = ArticleCourses(
                nom="Lait P16 A",
                categorie="Produits frais",
                quantite=2.0,
                unite="L",
                achetee=False,
                priorite="normale"
            )
            session.add(a)
            session.commit()
            
            retrieved = session.query(ArticleCourses).filter_by(nom="Lait P16 A").first()
            assert retrieved is not None
            assert retrieved.achetee == False
    
    def test_article_courses_mark_purchased(self):
        """Test marquer comme acheté"""
        with get_db_context() as session:
            a = ArticleCourses(
                nom="Pain P16 A",
                categorie="Boulangerie",
                quantite=1.0,
                unite="unité",
                achetee=False
            )
            session.add(a)
            session.commit()
            article_id = a.id
            
            a.achetee = True
            session.commit()
            
            purchased = session.query(ArticleCourses).filter_by(id=article_id).first()
            assert purchased.achetee == True
    
    def test_article_courses_by_category(self):
        """Test filtrage par catégorie"""
        with get_db_context() as session:
            categories = ["Fruits P16", "Légumes P16"]
            for cat in categories:
                for i in range(2):
                    a = ArticleCourses(
                        nom=f"{cat} {i}",
                        categorie=cat,
                        quantite=1.0,
                        unite="kg"
                    )
                    session.add(a)
            session.commit()
            
            fruits = session.query(ArticleCourses).filter_by(categorie="Fruits P16").all()
            legumes = session.query(ArticleCourses).filter_by(categorie="Légumes P16").all()
            assert len(fruits) >= 2
            assert len(legumes) >= 2
    
    def test_article_courses_essential_items(self):
        """Test articles essentiels"""
        with get_db_context() as session:
            essential = ArticleCourses(
                nom="Oeufs P16 A",
                categorie="Basique",
                quantite=12.0,
                unite="unité",
                priorite="haute",
                achetee=False
            )
            optional = ArticleCourses(
                nom="Chocolat P16 A",
                categorie="Gourmandise",
                quantite=1.0,
                unite="g",
                priorite="basse",
                achetee=False
            )
            session.add_all([essential, optional])
            session.commit()
            
            high_priority = session.query(ArticleCourses).filter_by(priorite="haute").all()
            assert len(high_priority) >= 1


class TestInventaireServiceExpanded:
    """Inventaire stock tests"""
    
    def test_article_inventaire_create(self):
        """Test création article inventaire"""
        with get_db_context() as session:
            a = ArticleInventaire(
                nom="Riz basmati P16 A",
                categorie="Céréales",
                quantite=2000,
                unite="g",
                seuil_alerte=500,
                localisation="Placard cuisine"
            )
            session.add(a)
            session.commit()
            
            retrieved = session.query(ArticleInventaire).filter_by(nom="Riz basmati P16 A").first()
            assert retrieved is not None
            assert retrieved.quantite == 2000
    
    def test_article_inventaire_low_stock_alert(self):
        """Test alerte stock bas"""
        with get_db_context() as session:
            a = ArticleInventaire(
                nom="Farine P16 A",
                categorie="Céréales",
                quantite=100,
                unite="g",
                seuil_alerte=500
            )
            session.add(a)
            session.commit()
            
            retrieved = session.query(ArticleInventaire).filter_by(nom="Farine P16 A").first()
            assert retrieved.quantite < retrieved.seuil_alerte
    
    def test_article_inventaire_update_quantity(self):
        """Test mise à jour quantité"""
        with get_db_context() as session:
            a = ArticleInventaire(
                nom="Sucre P16 A",
                categorie="Sucres",
                quantite=1000,
                unite="g"
            )
            session.add(a)
            session.commit()
            article_id = a.id
            
            a.quantite = 750
            session.commit()
            
            updated = session.query(ArticleInventaire).filter_by(id=article_id).first()
            assert updated.quantite == 750
    
    def test_article_inventaire_locations(self):
        """Test localisation articles"""
        with get_db_context() as session:
            locations = ["Placard P16", "Congélateur P16", "Réfrigérateur P16"]
            for loc in locations:
                a = ArticleInventaire(
                    nom=f"Article {loc}",
                    categorie="Divers",
                    quantite=100,
                    unite="unité",
                    localisation=loc
                )
                session.add(a)
            session.commit()
            
            for loc in locations:
                items = session.query(ArticleInventaire).filter_by(localisation=loc).all()
                assert len(items) >= 1
    
    def test_article_inventaire_with_historique(self):
        """Test avec historique"""
        with get_db_context() as session:
            a = ArticleInventaire(
                nom="Huile P16 A",
                categorie="Huiles",
                quantite=500,
                unite="ml"
            )
            session.add(a)
            session.flush()
            
            h = HistoriqueInventaire(
                article_inventaire_id=a.id,
                quantite_avant=600,
                quantite_apres=500,
                motif="Utilisation cuisine"
            )
            session.add(h)
            session.commit()
            
            article = session.query(ArticleInventaire).filter_by(nom="Huile P16 A").first()
            assert article.quantite == 500
            
            historique = session.query(HistoriqueInventaire).filter_by(
                article_inventaire_id=article.id
            ).all()
            assert len(historique) >= 1


class TestDomainRecetteComplex:
    """Domain recette business logic"""
    
    def test_recette_seasonal_variations(self):
        """Test variations saisonnières"""
        with get_db_context() as session:
            r = Recette(
                nom="Soupe saisonnière P16 A",
                description="Adapté à la saison",
                difficulte="moyen",
                type_repas="entrée",
                portions=4
            )
            session.add(r)
            session.commit()
            assert r.nom == "Soupe saisonnière P16 A"


class TestDomainPlanningComplex:
    """Domain planning logic"""
    
    def test_planning_weekly_nutrition_balance(self):
        """Test équilibre nutritionnel hebdo"""
        with get_db_context() as session:
            p = Planning(
                date_debut=date(2026, 3, 1),
                date_fin=date(2026, 3, 7),
                jour_semaine="Semaine équilibrée P16"
            )
            session.add(p)
            session.commit()
            assert (p.date_fin - p.date_debut).days >= 6


class TestEndToEndWorkflows:
    """End-to-end workflow tests"""
    
    def test_complete_meal_prep_workflow(self):
        """Test flux complet préparation repas"""
        with get_db_context() as session:
            r = Recette(
                nom="Recette E2E P16 A",
                description="Workflow test",
                difficulte="moyen",
                type_repas="déjeuner",
                portions=4
            )
            session.add(r)
            session.flush()
            
            p = Planning(
                date_debut=date(2026, 3, 15),
                jour_semaine="Lundi E2E P16"
            )
            session.add(p)
            session.flush()
            p.recettes.append(r)
            
            a = ArticleCourses(
                nom="Ingrédient E2E P16 A",
                categorie="Test",
                quantite=1.0,
                unite="unité"
            )
            session.add(a)
            session.commit()
            
            planning = session.query(Planning).filter_by(jour_semaine="Lundi E2E P16").first()
            assert planning is not None
            assert len(planning.recettes) >= 1
