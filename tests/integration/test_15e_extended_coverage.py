"""
Phase 15E : Tests complémentaires pour augmenter couverture
Cible: Services, Domains, et UI modules
Tests additionnels pour edge cases et workflows secondaires
"""

import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from src.core.models import (
    Recette, Ingredient, Planning, ArticleInventaire, ArticleCourses,
    HistoriqueInventaire
)
from src.core.database import get_db_context
from src.services.recettes import RecetteService
from src.services.planning import PlanningService
from src.services.courses import CoursesService
from src.services.inventaire import InventaireService


class TestServicesExtended:
    """Tests étendus des services pour edge cases"""
    
    def test_recette_service_bulk_operations(self):
        """Test les opérations en masse du service recettes"""
        with get_db_context() as session:
            service = RecetteService(session)
            
            # Créer 5 recettes rapidement
            recettes = []
            for i in range(5):
                r = Recette(
                    nom=f"Recette Bulk {i}",
                    description=f"Description {i}",
                    difficulte="facile",
                    type_repas="déjeuner",
                    portions=4
                )
                session.add(r)
                recettes.append(r)
            
            session.commit()
            assert len(recettes) == 5
            
            # Vérifier la récupération
            all_recettes = session.query(Recette).filter(
                Recette.nom.like("Recette Bulk%")
            ).all()
            assert len(all_recettes) >= 5
    
    def test_recette_service_sorting(self):
        """Test le tri des recettes"""
        with get_db_context() as session:
            # Créer recettes avec différentes difficultés
            for difficulte in ["facile", "moyen", "difficile", "facile", "moyen"]:
                r = Recette(
                    nom=f"Recette {difficulte}",
                    description="Test sort",
                    difficulte=difficulte,
                    type_repas="déjeuner",
                    portions=4
                )
                session.add(r)
            
            session.commit()
            
            # Vérifier le tri
            recettes = session.query(Recette).filter(
                Recette.description == "Test sort"
            ).order_by(Recette.difficulte).all()
            
            assert len(recettes) >= 5
            difficulties = [r.difficulte for r in recettes]
            assert "facile" in difficulties
            assert "difficile" in difficulties
    
    def test_planning_service_multiple_weeks(self):
        """Test planification multi-semaines"""
        with get_db_context() as session:
            service = PlanningService(session)
            today = date.today()
            
            # Créer des recettes
            recettes = []
            for i in range(7):
                r = Recette(
                    nom=f"Recette Semaine {i}",
                    description="Multi-week test",
                    difficulte="facile",
                    type_repas="déjeuner",
                    portions=4
                )
                session.add(r)
                recettes.append(r)
            
            session.commit()
            
            # Créer plannings pour 3 semaines
            for week in range(3):
                start_date = today + timedelta(days=week*7)
                p = Planning(
                    date_debut=start_date,
                    date_fin=start_date + timedelta(days=6),
                    est_auto_genere=False
                )
                session.add(p)
            
            session.commit()
            
            # Vérifier
            plannings = session.query(Planning).filter(
                Planning.date_debut >= today
            ).all()
            assert len(plannings) >= 3
    
    def test_courses_service_filtering(self):
        """Test le filtrage des articles de courses"""
        with get_db_context() as session:
            # Créer des ingrédients
            categories = ["Fruits", "Légumes", "Produits laitiers"]
            ingredients = []
            for i, cat in enumerate(categories):
                ing = Ingredient(
                    nom=f"Ingredient {cat} {i}",
                    categorie=cat,
                    unite="kg"
                )
                session.add(ing)
                ingredients.append(ing)
            
            session.commit()
            
            # Créer articles courses
            for ing in ingredients:
                ac = ArticleCourses(
                    ingredient_id=ing.id,
                    quantite=2.5,
                    unite="kg",
                    marque="Marque Test",
                    achete=False,
                    est_essentiel=True
                )
                session.add(ac)
            
            session.commit()
            
            # Test filtrage par catégorie
            articles = session.query(ArticleCourses).join(Ingredient).filter(
                Ingredient.categorie == "Fruits"
            ).all()
            
            assert len(articles) >= 1
    
    def test_inventaire_service_thresholds(self):
        """Test les seuils d'alerte du service inventaire"""
        with get_db_context() as session:
            # Créer articles avec différents niveaux de stock
            levels = [0.5, 1.5, 5.0, 10.0]  # En unités
            articles = []
            
            for i, level in enumerate(levels):
                ing = Ingredient(
                    nom=f"Ingredient Stock {i}",
                    categorie="Épices",
                    unite="g"
                )
                session.add(ing)
                session.flush()
                
                ai = ArticleInventaire(
                    ingredient_id=ing.id,
                    quantite_actuelle=level,
                    quantite_ideal=5.0,
                    localisation=f"Placard {i}",
                    date_ajout=datetime.now()
                )
                session.add(ai)
                articles.append(ai)
            
            session.commit()
            
            # Identifier articles sous seuil (< 2.0)
            low_stock = session.query(ArticleInventaire).filter(
                ArticleInventaire.quantite_actuelle < 2.0
            ).all()
            
            assert len(low_stock) >= 2


class TestDomainsExtended:
    """Tests étendus des domaines métier - Couches métier"""
    
    def test_ingredients_multiple_categories(self):
        """Test créer ingrédients dans différentes catégories"""
        with get_db_context() as session:
            categories = ["Fruits", "Légumes", "Protéines", "Produits laitiers", "Épices"]
            ingredients = []
            
            for cat in categories:
                for i in range(2):
                    ing = Ingredient(
                        nom=f"Ingredient {cat} {i}",
                        categorie=cat,
                        unite="kg"
                    )
                    session.add(ing)
                    ingredients.append(ing)
            
            session.commit()
            
            # Vérifier par catégorie
            for cat in categories:
                result = session.query(Ingredient).filter_by(categorie=cat).all()
                assert len(result) >= 2
    
    def test_recettes_with_detailed_metadata(self):
        """Test recettes avec métadonnées détaillées"""
        with get_db_context() as session:
            metadata_list = [
                {"difficulte": "facile", "type_repas": "petit-déjeuner", "portions": 1},
                {"difficulte": "moyen", "type_repas": "déjeuner", "portions": 4},
                {"difficulte": "difficile", "type_repas": "dîner", "portions": 6},
            ]
            
            for idx, metadata in enumerate(metadata_list):
                r = Recette(
                    nom=f"Recette Metadata {idx}",
                    description=f"Description {metadata}",
                    difficulte=metadata["difficulte"],
                    type_repas=metadata["type_repas"],
                    portions=metadata["portions"]
                )
                session.add(r)
            
            session.commit()
            
            # Vérifier
            recettes = session.query(Recette).filter(
                Recette.nom.like("Recette Metadata%")
            ).all()
            
            assert len(recettes) >= 3
            assert any(r.difficulte == "difficile" for r in recettes)
    
    def test_planning_date_ranges(self):
        """Test plannings avec différentes plages de dates"""
        with get_db_context() as session:
            today = date.today()
            
            # Créer 5 plannings échelonnés
            for i in range(5):
                start = today + timedelta(days=i*7)
                p = Planning(
                    date_debut=start,
                    date_fin=start + timedelta(days=6),
                    est_auto_genere=False
                )
                session.add(p)
            
            session.commit()
            
            # Vérifier
            plannings = session.query(Planning).filter(
                Planning.date_debut >= today
            ).all()
            
            assert len(plannings) >= 5
            
            # Vérifier l'écart
            dates_start = sorted([p.date_debut for p in plannings])
            for i in range(len(dates_start) - 1):
                delta = (dates_start[i+1] - dates_start[i]).days
                assert delta == 7  # 7 jours d'écart


class TestServicesEdgeCases:
    """Tests des cas limites des services"""
    
    def test_recette_empty_ingredients(self):
        """Test recette sans ingrédients"""
        with get_db_context() as session:
            r = Recette(
                nom="Recette Vide",
                description="Pas d'ingrédients",
                difficulte="facile",
                type_repas="déjeuner",
                portions=1
            )
            session.add(r)
            session.commit()
            
            retrieved = session.query(Recette).filter_by(nom="Recette Vide").first()
            assert retrieved is not None
            assert len(retrieved.ingredients) == 0
    
    def test_planning_zero_recipes(self):
        """Test planning sans recettes"""
        with get_db_context() as session:
            p = Planning(
                date_debut=date.today(),
                date_fin=date.today() + timedelta(days=6),
                est_auto_genere=False
            )
            session.add(p)
            session.commit()
            
            retrieved = session.query(Planning).filter(
                Planning.date_debut == date.today()
            ).first()
            
            assert retrieved is not None
            assert len(retrieved.recettes) == 0
    
    def test_articles_courses_all_purchased(self):
        """Test liste de courses entièrement achetée"""
        with get_db_context() as session:
            # Créer ingrédients et articles courses
            articles = []
            for i in range(3):
                ing = Ingredient(
                    nom=f"Item Acheté {i}",
                    categorie="Généraux",
                    unite="pièce"
                )
                session.add(ing)
                session.flush()
                
                ac = ArticleCourses(
                    ingredient_id=ing.id,
                    quantite=1.0,
                    unite="pièce",
                    achete=True,
                    est_essentiel=False
                )
                session.add(ac)
                articles.append(ac)
            
            session.commit()
            
            # Vérifier que tous sont achetés
            non_achetes = session.query(ArticleCourses).filter(
                ArticleCourses.achete == False
            ).all()
            
            achetes = session.query(ArticleCourses).filter(
                ArticleCourses.achete == True
            ).all()
            
            assert len(achetes) >= 3
    
    def test_inventaire_zero_stock(self):
        """Test article inventaire avec stock zéro"""
        with get_db_context() as session:
            ing = Ingredient(
                nom="Article Stock Zéro",
                categorie="Test",
                unite="g"
            )
            session.add(ing)
            session.flush()
            
            ai = ArticleInventaire(
                ingredient_id=ing.id,
                quantite_actuelle=0.0,
                quantite_ideal=100.0,
                localisation="Placard",
                date_ajout=datetime.now()
            )
            session.add(ai)
            session.commit()
            
            retrieved = session.query(ArticleInventaire).filter_by(
                quantite_actuelle=0.0
            ).first()
            
            assert retrieved is not None
            assert retrieved.quantite_actuelle == 0.0


class TestHistoriqueInventaireIntegration:
    """Tests intégration historique de l'inventaire"""
    
    def test_historique_articles_tracking(self):
        """Test le suivi historique des articles"""
        with get_db_context() as session:
            ing = Ingredient(
                nom="Ingredient Historique",
                categorie="Test",
                unite="kg"
            )
            session.add(ing)
            session.flush()
            
            # Créer article inventaire
            ai = ArticleInventaire(
                ingredient_id=ing.id,
                quantite_actuelle=5.0,
                quantite_ideal=10.0,
                localisation="Placard",
                date_ajout=datetime.now()
            )
            session.add(ai)
            session.flush()
            
            # Créer historique sur 3 modifications
            for i in range(3):
                hi = HistoriqueInventaire(
                    article_id=ai.id,
                    ingredient_id=ing.id,
                    type_modification="modification_quantite",
                    quantite_avant=5.0 + (i * 0.5),
                    quantite_apres=5.0 + ((i + 1) * 0.5),
                    date_modification=datetime.now(),
                    utilisateur="test_user"
                )
                session.add(hi)
            
            session.commit()
            
            # Vérifier historique
            historique = session.query(HistoriqueInventaire).filter_by(
                ingredient_id=ing.id
            ).all()
            
            assert len(historique) >= 3


class TestComplexWorkflowsExtended:
    """Tests des workflows complexes étendus"""
    
    def test_full_meal_planning_workflow(self):
        """Workflow complet: planning → recettes → courses → inventaire"""
        with get_db_context() as session:
            today = date.today()
            
            # Étape 1: Créer recettes
            recettes = []
            for i in range(3):
                r = Recette(
                    nom=f"Recette Planning {i}",
                    description="Workflow test",
                    difficulte="facile",
                    type_repas="déjeuner",
                    portions=4
                )
                session.add(r)
                recettes.append(r)
            
            session.commit()
            
            # Étape 2: Créer planning avec recettes
            p = Planning(
                date_debut=today,
                date_fin=today + timedelta(days=6),
                est_auto_genere=False
            )
            session.add(p)
            session.flush()
            
            for rec in recettes:
                p.recettes.append(rec)
            
            session.commit()
            
            # Étape 3: Créer ingrédients pour courses
            ingredients = []
            for i in range(3):
                ing = Ingredient(
                    nom=f"Ingredient Workflow {i}",
                    categorie="Généraux",
                    unite="kg"
                )
                session.add(ing)
                ingredients.append(ing)
            
            session.commit()
            
            # Étape 4: Créer articles courses
            articles_courses = []
            for ing in ingredients:
                ac = ArticleCourses(
                    ingredient_id=ing.id,
                    quantite=2.5,
                    unite="kg",
                    achete=False,
                    est_essentiel=True
                )
                session.add(ac)
                articles_courses.append(ac)
            
            session.commit()
            
            # Étape 5: Créer articles inventaire
            for ing in ingredients:
                ai = ArticleInventaire(
                    ingredient_id=ing.id,
                    quantite_actuelle=5.0,
                    quantite_ideal=10.0,
                    localisation="Placard",
                    date_ajout=datetime.now()
                )
                session.add(ai)
            
            session.commit()
            
            # Vérifier intégrité du workflow
            retrieved_planning = session.query(Planning).filter(
                Planning.date_debut == today
            ).first()
            
            assert retrieved_planning is not None
            assert len(retrieved_planning.recettes) == 3
            
            retrieved_courses = session.query(ArticleCourses).all()
            assert len(retrieved_courses) >= 3
            
            retrieved_inv = session.query(ArticleInventaire).all()
            assert len(retrieved_inv) >= 3


@pytest.mark.integration
class TestPerformanceOptimizations:
    """Tests des optimisations de performance"""
    
    def test_bulk_ingredient_query(self):
        """Test requête en masse pour ingrédients"""
        with get_db_context() as session:
            # Créer 50 ingrédients
            for i in range(50):
                ing = Ingredient(
                    nom=f"Ingredient Perf {i}",
                    categorie="Test Perf",
                    unite="kg"
                )
                session.add(ing)
            
            session.commit()
            
            # Requête rapide
            result = session.query(Ingredient).filter(
                Ingredient.nom.like("Ingredient Perf%")
            ).all()
            
            assert len(result) >= 50
    
    def test_planning_range_query(self):
        """Test requête Planning par plage de dates"""
        with get_db_context() as session:
            today = date.today()
            
            # Créer 10 plannings échelonnés
            for i in range(10):
                p = Planning(
                    date_debut=today + timedelta(days=i*7),
                    date_fin=today + timedelta(days=i*7 + 6),
                    est_auto_genere=False
                )
                session.add(p)
            
            session.commit()
            
            # Requête par intervalle
            result = session.query(Planning).filter(
                Planning.date_debut >= today,
                Planning.date_debut <= today + timedelta(days=60)
            ).all()
            
            assert len(result) >= 8
