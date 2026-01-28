# -*- coding: utf-8 -*-
"""
Tests d'integration pour le module Cuisine.
"""

import pytest
from datetime import date, timedelta

from src.core.models import (
    Recette,
    Ingredient,
    RecetteIngredient,
    EtapeRecette,
    ArticleInventaire,
    ArticleCourses,
)


@pytest.mark.integration
class TestWorkflowRecettesComplet:
    """Tests du workflow complet de gestion des recettes."""

    def test_creer_recette_avec_ingredients_et_etapes(self, int_db, ingredients_base):
        """Creer une nouvelle recette complete."""
        recette = Recette(
            nom="Gratin dauphinois",
            description="Gratin de pommes de terre cremeux",
            temps_preparation=20,
            temps_cuisson=60,
            portions=6,
            difficulte="moyen",
            type_repas="diner",
            saison="hiver",
        )
        int_db.add(recette)
        int_db.flush()
        
        int_db.add(RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredients_base["Lait"].id,
            quantite=500,
            unite="mL"
        ))
        int_db.add(RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredients_base["Beurre"].id,
            quantite=30,
            unite="g"
        ))
        
        etapes = [
            EtapeRecette(recette_id=recette.id, ordre=1, description="Prechauffer four a 180C"),
            EtapeRecette(recette_id=recette.id, ordre=2, description="Eplucher pommes de terre"),
            EtapeRecette(recette_id=recette.id, ordre=3, description="Couper en fines tranches"),
        ]
        for etape in etapes:
            int_db.add(etape)
        
        int_db.commit()
        
        recette_db = int_db.query(Recette).filter_by(nom="Gratin dauphinois").first()
        assert recette_db is not None
        
        ingredients_recette = int_db.query(RecetteIngredient).filter_by(
            recette_id=recette_db.id
        ).all()
        assert len(ingredients_recette) == 2
        
        etapes_recette = int_db.query(EtapeRecette).filter_by(
            recette_id=recette_db.id
        ).order_by(EtapeRecette.ordre).all()
        assert len(etapes_recette) == 3

    def test_modifier_recette_existante(self, int_db, recettes_base, ingredients_base):
        """Modifier une recette existante."""
        recette = recettes_base["pates_tomate"]
        
        recette.portions = 6
        recette.temps_preparation = 15
        
        int_db.add(RecetteIngredient(
            recette_id=recette.id,
            ingredient_id=ingredients_base["Huile olive"].id,
            quantite=2,
            unite="cuilleres"
        ))
        
        int_db.commit()
        
        recette_db = int_db.query(Recette).filter_by(id=recette.id).first()
        assert recette_db.portions == 6
        
        ingredients_count = int_db.query(RecetteIngredient).filter_by(
            recette_id=recette.id
        ).count()
        assert ingredients_count >= 3

    def test_filtrer_recettes_par_criteres(self, int_db, recettes_base):
        """Filtrer les recettes par criteres."""
        recette_rapide = Recette(
            nom="Omelette rapide",
            temps_preparation=5,
            temps_cuisson=5,
            portions=2,
            difficulte="facile",
            type_repas="dejeuner",
        )
        int_db.add(recette_rapide)
        int_db.commit()
        
        recettes_faciles = int_db.query(Recette).filter_by(difficulte="facile").all()
        assert len(recettes_faciles) >= 2
        
        recettes_rapides = int_db.query(Recette).filter(
            (Recette.temps_preparation + Recette.temps_cuisson) < 30
        ).all()
        assert len(recettes_rapides) >= 1


@pytest.mark.integration
class TestWorkflowInventaireCourses:
    """Tests du workflow inventaire vers liste de courses."""

    def test_detecter_stock_bas(self, int_db, inventaire_base):
        """Detecter les articles en stock bas."""
        articles_bas = int_db.query(ArticleInventaire).filter(
            ArticleInventaire.quantite < ArticleInventaire.quantite_min
        ).all()
        
        assert len(articles_bas) >= 2

    def test_detecter_peremption_proche(self, int_db, inventaire_base):
        """Detecter les articles proches de la peremption."""
        seuil = date.today() + timedelta(days=5)
        
        articles_peremption = int_db.query(ArticleInventaire).filter(
            ArticleInventaire.date_peremption.isnot(None),
            ArticleInventaire.date_peremption <= seuil
        ).all()
        
        assert len(articles_peremption) >= 1


@pytest.mark.integration
class TestCycleVieInventaire:
    """Tests du cycle de vie complet des articles inventaire."""

    def test_ajouter_article_inventaire(self, int_db, ingredients_base):
        """Ajouter un nouvel article a l'inventaire."""
        article = ArticleInventaire(
            ingredient_id=ingredients_base["Sel"].id,
            quantite=500,
            quantite_min=100,
            emplacement="Placard",
        )
        int_db.add(article)
        int_db.commit()
        
        article_db = int_db.query(ArticleInventaire).filter_by(
            ingredient_id=ingredients_base["Sel"].id
        ).first()
        assert article_db is not None
        assert article_db.quantite == 500

    def test_mettre_a_jour_quantite(self, int_db, inventaire_base):
        """Mettre a jour la quantite d'un article."""
        article = inventaire_base[0]
        ancienne_quantite = article.quantite
        
        article.quantite -= 0.5
        int_db.commit()
        
        article_db = int_db.query(ArticleInventaire).filter_by(id=article.id).first()
        assert article_db.quantite == ancienne_quantite - 0.5


@pytest.mark.integration
class TestStatistiquesCuisine:
    """Tests des statistiques du module cuisine."""

    def test_compter_recettes_par_type(self, int_db, recettes_base):
        """Compter les recettes par type de repas."""
        types_count = {}
        
        recettes = int_db.query(Recette).all()
        for recette in recettes:
            type_repas = recette.type_repas or "non_defini"
            types_count[type_repas] = types_count.get(type_repas, 0) + 1
        
        assert len(types_count) >= 1

    def test_calculer_valeur_inventaire(self, int_db, inventaire_base):
        """Calculer la valeur totale de l'inventaire."""
        articles = int_db.query(ArticleInventaire).all()
        
        total_articles = len(articles)
        total_quantite = sum(a.quantite for a in articles)
        
        assert total_articles >= 4
        assert total_quantite > 0
