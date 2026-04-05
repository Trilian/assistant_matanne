"""
Tests pour les bridges inter-modules bridges inter-modules (NIM5-NIM8).
"""

import pytest
from decimal import Decimal
from datetime import date, timedelta

from sqlalchemy.orm import Session


class TestBridgeEntretienBudget:
    """Tests pour NIM5: Entretien ? Budget maison."""

    def test_enregistrer_depense_entretien_success(self, test_db: Session):
        """Test l'enregistrement d'une dépense d'entretien."""
        from src.core.models.habitat import TacheEntretien
        from src.services.maison.inter_modules.inter_module_entretien_budget import (
            obtenir_entretien_budget_bridge,
        )

        # Créer une tâche entretien terminée
        tache = TacheEntretien(
            nom="Réparation robinet",
            categorie="maintenance",
            priorite="haute",
            fait=True,
        )
        test_db.add(tache)
        test_db.commit()

        # Enregistrer la dépense via le bridge
        service = obtenir_entretien_budget_bridge()
        result = service.enregistrer_depense_entretien(
            tache_id=tache.id,
            montant_reel=Decimal("150.00"),
            description="Plombier appelé",
            db=test_db,
        )

        # Vérifier le résultat
        assert result is not None
        assert result["montant"] == 150.0
        assert result["categorie"] == "entretien_maintenance"
        assert result["tache_id"] == tache.id

    def test_obtenir_depenses_par_entretien(self, test_db: Session):
        """Test la récupération des dépenses d'entretien."""
        from src.core.models.finances import DepenseMaison
        from src.services.maison.inter_modules.inter_module_entretien_budget import (
            obtenir_entretien_budget_bridge,
        )

        # Créer quelques dépenses
        today = date.today()
        for i in range(3):
            depense = DepenseMaison(
                categorie="entretien_maintenance",
                mois=today.month,
                annee=today.year,
                montant=Decimal(f"{100 + i * 50}"),
                fournisseur=f"Artisan {i}",
            )
            test_db.add(depense)
        test_db.commit()

        # Récupérer les dépenses
        service = obtenir_entretien_budget_bridge()
        resultat = service.obtenir_depenses_par_entretien(limite=10, db=test_db)

        assert len(resultat) >= 3
        assert all(d["categorie"] == "entretien_maintenance" for d in resultat)


class TestBridgeCoursesValidation:
    """Tests pour NIM6: Courses ? Planning validation post-achat."""

    def test_analyser_substitutions_post_achat(self, test_db: Session):
        """Test l'analyse des substitutions après achat."""
        from datetime import datetime
        from src.core.models.courses import ArticleCourses, ListeCourses
        from src.core.models.recettes import Ingredient
        from src.services.cuisine.inter_module_courses_validation import (
            obtenir_courses_validation_bridge,
        )

        # Créer une liste et des articles achetés
        liste = ListeCourses(nom="Courses lundi")
        test_db.add(liste)
        test_db.commit()

        ingredient = Ingredient(nom="Tomate", categorie="légume", unite="kg")
        test_db.add(ingredient)
        test_db.commit()

        article = ArticleCourses(
            liste_id=liste.id,
            ingredient_id=ingredient.id,
            quantite_necessaire=2.0,
            achete=True,
            achete_le=datetime.utcnow(),
        )
        test_db.add(article)
        test_db.commit()

        # Analyser les substitutions
        service = obtenir_courses_validation_bridge()
        substitutions = service.analyser_substitutions_post_achat(db=test_db)

        # Vérifier le résultat (peut être vide si pas de substitution détectée)
        assert isinstance(substitutions, list)

    def test_valider_achete_vs_planifie(self, test_db: Session):
        """Test la validation achat vs planification."""
        from src.core.models.courses import ArticleCourses, ListeCourses
        from src.core.models.recettes import Ingredient
        from src.services.cuisine.inter_module_courses_validation import (
            obtenir_courses_validation_bridge,
        )

        # Créer une liste avec articles
        liste = ListeCourses(nom="Courses test")
        test_db.add(liste)
        test_db.commit()

        ingredient = Ingredient(nom="Lait", categorie="produits laitiers", unite="L")
        test_db.add(ingredient)
        test_db.commit()

        # Ajouter 5 articles, 3 achetés
        for i in range(5):
            article = ArticleCourses(
                liste_id=liste.id,
                ingredient_id=ingredient.id,
                quantite_necessaire=1.0 + i,
                achete=i < 3,
            )
            test_db.add(article)
        test_db.commit()

        # Valider
        service = obtenir_courses_validation_bridge()
        stats = service.valider_achete_vs_planifie(liste_id=liste.id, db=test_db)

        assert stats["total"] == 5
        assert stats["achetes"] == 3
        assert stats["non_achetes"] == 2
        assert stats["taux_completion"] == 60.0


class TestBridgeInventaireFIFO:
    """Tests pour NIM7: Inventaire ? Rotation FIFO."""

    def test_valider_consommation_fifo(self, test_db: Session):
        """Test la validation FIFO."""
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import Ingredient
        from src.services.cuisine.inter_module_inventaire_fifo import (
            obtenir_inventaire_fifo_bridge,
        )

        # Créer un ingrédient
        ingredient = Ingredient(nom="Farine", categorie="poudre", unite="kg")
        test_db.add(ingredient)
        test_db.commit()

        # Ajouter 3 articles du même ingrédient à des dates différentes
        for i in range(3):
            article = ArticleInventaire(
                ingredient_id=ingredient.id,
                quantite=5.0,
                quantite_min=1.0,
                emplacement="placard",
                date_entree=date.today() - timedelta(days=i * 10),
                date_peremption=date.today() + timedelta(days=100 - i * 10),
            )
            test_db.add(article)
        test_db.commit()

        # Valider FIFO
        service = obtenir_inventaire_fifo_bridge()
        resultat = service.valider_consommation_fifo(ingredient_id=ingredient.id, db=test_db)

        assert resultat is not None
        assert "article_prioritaire_id" in resultat
        assert resultat["non_respect_fifo"] is True  # 3 articles en stock
        assert resultat["nombre_autres_articles"] == 2

    def test_obtenir_articles_hors_ordre(self, test_db: Session):
        """Test l'identification des articles hors ordre FIFO."""
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import Ingredient
        from src.services.cuisine.inter_module_inventaire_fifo import (
            obtenir_inventaire_fifo_bridge,
        )

        # Créer un ingrédient
        ingredient = Ingredient(nom="Sucre", categorie="poudre", unite="kg")
        test_db.add(ingredient)
        test_db.commit()

        # Ajouter 2 articles du même ingrédient
        for i in range(2):
            article = ArticleInventaire(
                ingredient_id=ingredient.id,
                quantite=3.0,
                quantite_min=0.5,
                emplacement="placard",
                date_entree=date.today() - timedelta(days=i * 5),
            )
            test_db.add(article)
        test_db.commit()

        # Chercher les problèmes FIFO
        service = obtenir_inventaire_fifo_bridge()
        problemes = service.obtenir_articles_hors_ordre(limite=10, db=test_db)

        assert isinstance(problemes, list)
        if problemes:
            assert "ingredient_id" in problemes[0]
            assert problemes[0]["nombre_articles"] >= 2


class TestBridgeChatEventBus:
    """Tests pour NIM8: Chat IA ? Event Bus."""

    def test_initialisation_cache(self):
        """Test l'initialisation du cache."""
        from src.services.utilitaires.inter_modules.inter_module_chat_event_bus import (
            obtenir_chat_event_bus_bridge,
        )

        service = obtenir_chat_event_bus_bridge()
        assert service is not None
        cache = service.obtenir_contexte_cache()
        assert isinstance(cache, dict)

    def test_rafraichir_contexte_inventaire(self, test_db: Session):
        """Test le rafraîchissement du contexte inventaire."""
        from src.core.models.inventaire import ArticleInventaire
        from src.core.models.recettes import Ingredient
        from src.services.utilitaires.inter_modules.inter_module_chat_event_bus import (
            obtenir_chat_event_bus_bridge,
        )

        # Créer un ingrédient et un article
        ingredient = Ingredient(nom="Ail", categorie="légume", unite="g")
        test_db.add(ingredient)
        test_db.commit()

        article = ArticleInventaire(
            ingredient_id=ingredient.id,
            quantite=100.0,
            quantite_min=10.0,
            emplacement="frigo",
            date_peremption=date.today() + timedelta(days=5),
        )
        test_db.add(article)
        test_db.commit()

        # Rafraîchir le contexte
        service = obtenir_chat_event_bus_bridge()
        contexte = service.rafraichir_contexte_inventaire(db=test_db)

        assert "total_articles" in contexte
        assert "expirant_bientot" in contexte

    def test_rafraichir_contexte_courses(self, test_db: Session):
        """Test le rafraîchissement du contexte courses."""
        from src.core.models.courses import ArticleCourses, ListeCourses
        from src.core.models.recettes import Ingredient
        from src.services.utilitaires.inter_modules.inter_module_chat_event_bus import (
            obtenir_chat_event_bus_bridge,
        )

        # Créer une liste avec articles
        liste = ListeCourses(nom="Courses samedi")
        test_db.add(liste)
        test_db.commit()

        ingredient = Ingredient(nom="Oeufs", categorie="produits laitiers", unite="pièce")
        test_db.add(ingredient)
        test_db.commit()

        # Ajouter des articles
        for i in range(10):
            article = ArticleCourses(
                liste_id=liste.id,
                ingredient_id=ingredient.id,
                quantite_necessaire=1.0,
                achete=i < 6,
            )
            test_db.add(article)
        test_db.commit()

        # Rafraîchir le contexte
        service = obtenir_chat_event_bus_bridge()
        contexte = service.rafraichir_contexte_courses(db=test_db)

        assert "non_achetes" in contexte
        assert "achetes" in contexte
        assert "taux_completion" in contexte

    def test_rafraichir_contexte_budget(self, test_db: Session):
        """Test le rafraîchissement du contexte budget."""
        from src.core.models.finances import DepenseMaison
        from src.services.utilitaires.inter_modules.inter_module_chat_event_bus import (
            obtenir_chat_event_bus_bridge,
        )

        # Créer des dépenses
        today = date.today()
        for i in range(5):
            depense = DepenseMaison(
                categorie="alimentation" if i % 2 == 0 else "énergie",
                mois=today.month,
                annee=today.year,
                montant=Decimal(f"{50 + i * 10}"),
            )
            test_db.add(depense)
        test_db.commit()

        # Rafraîchir le contexte
        service = obtenir_chat_event_bus_bridge()
        contexte = service.rafraichir_contexte_budget(db=test_db)

        assert "nombre_depenses_mois" in contexte
        assert "total_mois" in contexte


@pytest.mark.unit
class TestBridgesIntegration:
    """Tests d'intégration entre les bridges."""

    def test_tous_les_bridges_importent(self):
        """Vérifie que tous les bridges s'importent correctement."""
        from src.services.maison.inter_modules.inter_module_entretien_budget import (
            obtenir_entretien_budget_bridge,
        )
        from src.services.cuisine.inter_module_courses_validation import (
            obtenir_courses_validation_bridge,
        )
        from src.services.cuisine.inter_module_inventaire_fifo import (
            obtenir_inventaire_fifo_bridge,
        )
        from src.services.utilitaires.inter_modules.inter_module_chat_event_bus import (
            obtenir_chat_event_bus_bridge,
        )

        # S'assurer qu'on peut créer les singletons
        bridge1 = obtenir_entretien_budget_bridge()
        bridge2 = obtenir_courses_validation_bridge()
        bridge3 = obtenir_inventaire_fifo_bridge()
        bridge4 = obtenir_chat_event_bus_bridge()

        assert bridge1 is not None
        assert bridge2 is not None
        assert bridge3 is not None
        assert bridge4 is not None

    def test_enregistrement_subscribers_sans_erreur(self):
        """Vérifie que les subscribers s'enregistrent sans erreur."""
        try:
            from src.services.maison.inter_modules.inter_module_entretien_budget import (
                enregistrer_entretien_budget_subscribers,
            )
            from src.services.cuisine.inter_module_courses_validation import (
                enregistrer_courses_validation_subscribers,
            )
            from src.services.cuisine.inter_module_inventaire_fifo import (
                enregistrer_inventaire_fifo_subscribers,
            )
            from src.services.utilitaires.inter_modules.inter_module_chat_event_bus import (
                enregistrer_chat_event_bus_subscribers,
            )

            # Appeler les fonctions d'enregistrement
            enregistrer_entretien_budget_subscribers()
            enregistrer_courses_validation_subscribers()
            enregistrer_inventaire_fifo_subscribers()
            enregistrer_chat_event_bus_subscribers()

            # Si on arrive ici, c'est bon
            assert True
        except Exception as e:
            pytest.fail(f"Erreur lors de l'enregistrement des subscribers: {e}")
