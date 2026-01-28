# -*- coding: utf-8 -*-
"""
Tests d'integration pour le module Planning.
"""

import pytest
from datetime import date, timedelta

from src.core.models import (
    Planning,
    Repas,
    Recette,
    RecetteIngredient,
    Ingredient,
    ArticleCourses,
    Routine,
    ArticleInventaire,
)


@pytest.mark.integration
class TestWorkflowPlanificationSemaine:
    """Tests du workflow de planification hebdomadaire."""

    def test_creer_planning_semaine_vide(self, int_db):
        """Creer un nouveau planning de semaine vide."""
        today = date.today()
        debut_semaine = today - timedelta(days=today.weekday())
        fin_semaine = debut_semaine + timedelta(days=6)
        
        planning = Planning(
            nom=f"Semaine du {debut_semaine.strftime('%d/%m')}",
            semaine_debut=debut_semaine,
            semaine_fin=fin_semaine,
            actif=True,
        )
        int_db.add(planning)
        int_db.commit()
        
        planning_db = int_db.query(Planning).filter_by(semaine_debut=debut_semaine).first()
        assert planning_db is not None
        assert planning_db.actif is True

    def test_ajouter_repas_au_planning(self, int_db, planning_semaine, recettes_base):
        """Ajouter des repas a un planning existant."""
        planning = planning_semaine["planning"]
        recette = recettes_base["poulet_roti"]
        date_repas = planning.semaine_debut + timedelta(days=2)
        
        nouveau_repas = Repas(
            planning_id=planning.id,
            date_repas=date_repas,
            type_repas="dejeuner",
            recette_id=recette.id,
            portion_ajustee=4,
            notes="Invites pour le dejeuner",
        )
        int_db.add(nouveau_repas)
        int_db.commit()
        
        repas_db = int_db.query(Repas).filter_by(
            planning_id=planning.id,
            date_repas=date_repas,
            type_repas="dejeuner"
        ).all()
        
        assert len(repas_db) >= 1

    def test_modifier_repas_existant(self, int_db, planning_semaine, recettes_base):
        """Modifier un repas existant."""
        repas = planning_semaine["repas"][0]
        nouvelle_recette = recettes_base["riz_poulet"]
        
        ancienne_recette_id = repas.recette_id
        repas.recette_id = nouvelle_recette.id
        repas.portion_ajustee = 6
        repas.notes = "Modifie - plus de portions"
        
        int_db.commit()
        
        repas_db = int_db.query(Repas).filter_by(id=repas.id).first()
        assert repas_db.recette_id == nouvelle_recette.id
        assert repas_db.portion_ajustee == 6

    def test_supprimer_repas(self, int_db, planning_semaine):
        """Supprimer un repas du planning."""
        repas = planning_semaine["repas"][0]
        repas_id = repas.id
        
        int_db.delete(repas)
        int_db.commit()
        
        repas_supprime = int_db.query(Repas).filter_by(id=repas_id).first()
        assert repas_supprime is None


@pytest.mark.integration
class TestWorkflowPlanningCourses:
    """Tests du workflow planning -> liste de courses."""

    def test_extraire_ingredients_semaine(self, int_db, planning_semaine):
        """Extraire tous les ingredients necessaires pour la semaine."""
        planning = planning_semaine["planning"]
        
        repas_avec_recettes = int_db.query(Repas).filter(
            Repas.planning_id == planning.id,
            Repas.recette_id.isnot(None)
        ).all()
        
        ingredients_agreg = {}
        
        for repas in repas_avec_recettes:
            ingredients_recette = int_db.query(RecetteIngredient).filter_by(
                recette_id=repas.recette_id
            ).all()
            
            for ri in ingredients_recette:
                ingredient = int_db.query(Ingredient).filter_by(id=ri.ingredient_id).first()
                
                recette = int_db.query(Recette).filter_by(id=repas.recette_id).first()
                portion_base = repas.portion_ajustee or 4
                ratio = portion_base / recette.portions if recette.portions > 0 else 1
                quantite_ajustee = ri.quantite * ratio
                
                key = ingredient.id
                if key not in ingredients_agreg:
                    ingredients_agreg[key] = {
                        "nom": ingredient.nom,
                        "quantite": 0,
                        "unite": ri.unite,
                        "categorie": ingredient.categorie,
                    }
                ingredients_agreg[key]["quantite"] += quantite_ajustee
        
        assert len(ingredients_agreg) > 0

    def test_generer_liste_courses_groupee(self, int_db, planning_semaine, ingredients_base):
        """Generer une liste de courses groupee par rayon."""
        # Utiliser les ingredients existants
        besoins = [
            {"ingredient": ingredients_base["Poulet"], "quantite": 2, "rayon": "Boucherie"},
            {"ingredient": ingredients_base["Tomates"], "quantite": 1, "rayon": "Fruits et Legumes"},
            {"ingredient": ingredients_base["Pates"], "quantite": 500, "rayon": "Epicerie"},
            {"ingredient": ingredients_base["Lait"], "quantite": 2, "rayon": "Frais"},
        ]
        
        articles_par_rayon = {}
        for besoin in besoins:
            rayon = besoin["rayon"]
            if rayon not in articles_par_rayon:
                articles_par_rayon[rayon] = []
            
            article = ArticleCourses(
                ingredient_id=besoin["ingredient"].id,
                quantite_necessaire=besoin["quantite"],
                priorite="moyenne",
                achete=False,
                rayon_magasin=rayon,
            )
            int_db.add(article)
            articles_par_rayon[rayon].append(article)
        
        int_db.commit()
        
        assert len(articles_par_rayon) >= 3
        total_articles = sum(len(v) for v in articles_par_rayon.values())
        assert total_articles == len(besoins)


@pytest.mark.integration
class TestWorkflowCalendrier:
    """Tests du workflow calendrier familial."""

    def test_vue_semaine_complete(self, int_db, planning_semaine, routines_base):
        """Afficher une vue semaine complete."""
        planning = planning_semaine["planning"]
        
        jours = []
        current = planning.semaine_debut
        while current <= planning.semaine_fin:
            jours.append(current)
            current += timedelta(days=1)
        
        vue_semaine = {jour: {"repas": [], "routines": []} for jour in jours}
        
        repas_semaine = int_db.query(Repas).filter_by(planning_id=planning.id).all()
        for repas in repas_semaine:
            if repas.date_repas in vue_semaine:
                vue_semaine[repas.date_repas]["repas"].append({
                    "type": repas.type_repas,
                    "recette_id": repas.recette_id,
                })
        
        routines_quotidiennes = int_db.query(Routine).filter_by(
            frequence="quotidien",
            actif=True
        ).all()
        
        for routine in routines_quotidiennes:
            for jour in jours:
                vue_semaine[jour]["routines"].append({"nom": routine.nom})
        
        assert len(vue_semaine) == 7
        jours_avec_repas = sum(1 for j in jours if len(vue_semaine[j]["repas"]) > 0)
        assert jours_avec_repas > 0


@pytest.mark.integration
class TestWorkflowPlanningsMultiples:
    """Tests de gestion de plusieurs plannings."""

    def test_creer_planning_suivant(self, int_db, planning_semaine):
        """Creer le planning de la semaine suivante."""
        planning_actuel = planning_semaine["planning"]
        
        nouvelle_debut = planning_actuel.semaine_fin + timedelta(days=1)
        nouvelle_fin = nouvelle_debut + timedelta(days=6)
        
        nouveau_planning = Planning(
            nom=f"Semaine du {nouvelle_debut.strftime('%d/%m')}",
            semaine_debut=nouvelle_debut,
            semaine_fin=nouvelle_fin,
            actif=True,
        )
        int_db.add(nouveau_planning)
        int_db.commit()
        
        assert nouveau_planning.id != planning_actuel.id
        assert nouveau_planning.semaine_debut == planning_actuel.semaine_fin + timedelta(days=1)

    def test_desactiver_ancien_planning(self, int_db, planning_semaine):
        """Desactiver un ancien planning quand un nouveau est cree."""
        planning_actuel = planning_semaine["planning"]
        
        nouveau_planning = Planning(
            nom="Nouveau planning",
            semaine_debut=date.today(),
            semaine_fin=date.today() + timedelta(days=6),
            actif=True,
        )
        int_db.add(nouveau_planning)
        
        planning_actuel.actif = False
        int_db.commit()
        
        plannings_actifs = int_db.query(Planning).filter_by(actif=True).all()
        assert len(plannings_actifs) == 1
        assert plannings_actifs[0].id == nouveau_planning.id

    def test_copier_planning_template(self, int_db, planning_semaine, recettes_base):
        """Copier un planning existant comme template."""
        planning_source = planning_semaine["planning"]
        repas_source = planning_semaine["repas"]
        
        nouveau_planning = Planning(
            nom="Planning copie",
            semaine_debut=date.today() + timedelta(days=14),
            semaine_fin=date.today() + timedelta(days=20),
            actif=False,
        )
        int_db.add(nouveau_planning)
        int_db.flush()
        
        nouvelle_date_base = nouveau_planning.semaine_debut
        for i, repas in enumerate(repas_source[:5]):
            nouveau_repas = Repas(
                planning_id=nouveau_planning.id,
                date_repas=nouvelle_date_base + timedelta(days=i % 5),
                type_repas=repas.type_repas,
                recette_id=repas.recette_id,
                portion_ajustee=repas.portion_ajustee,
            )
            int_db.add(nouveau_repas)
        
        int_db.commit()
        
        repas_copies = int_db.query(Repas).filter_by(planning_id=nouveau_planning.id).all()
        assert len(repas_copies) == 5


@pytest.mark.integration
class TestStatistiquesPlanning:
    """Tests des statistiques de planning."""

    def test_stats_repas_semaine(self, int_db, planning_semaine):
        """Calculer les statistiques des repas de la semaine."""
        planning = planning_semaine["planning"]
        
        repas = int_db.query(Repas).filter_by(planning_id=planning.id).all()
        
        stats = {
            "total_repas": len(repas),
            "par_type": {},
            "avec_recette": 0,
            "temps_preparation_total": 0,
        }
        
        for r in repas:
            stats["par_type"][r.type_repas] = stats["par_type"].get(r.type_repas, 0) + 1
            
            if r.recette_id:
                stats["avec_recette"] += 1
                recette = int_db.query(Recette).filter_by(id=r.recette_id).first()
                if recette:
                    stats["temps_preparation_total"] += (recette.temps_preparation or 0) + (recette.temps_cuisson or 0)
        
        assert stats["total_repas"] > 0
        assert stats["avec_recette"] <= stats["total_repas"]

    def test_diversite_recettes(self, int_db, planning_semaine):
        """Analyser la diversite des recettes sur la semaine."""
        planning = planning_semaine["planning"]
        
        repas = int_db.query(Repas).filter_by(planning_id=planning.id).all()
        
        recettes_ids = set()
        
        for r in repas:
            if r.recette_id:
                recettes_ids.add(r.recette_id)
        
        diversite = {
            "recettes_uniques": len(recettes_ids),
            "total_repas_avec_recette": len([r for r in repas if r.recette_id]),
        }
        
        assert diversite["recettes_uniques"] >= 1


@pytest.mark.integration
class TestIntegrationMultiModules:
    """Tests d'integration entre planning et autres modules."""

    def test_planning_vers_inventaire(self, int_db, planning_semaine, inventaire_base, ingredients_base):
        """Verifier le stock pour un planning."""
        planning = planning_semaine["planning"]
        
        besoins = {}
        repas = int_db.query(Repas).filter_by(planning_id=planning.id).all()
        
        for r in repas:
            if r.recette_id:
                ingredients = int_db.query(RecetteIngredient).filter_by(recette_id=r.recette_id).all()
                for ri in ingredients:
                    if ri.ingredient_id not in besoins:
                        besoins[ri.ingredient_id] = 0
                    besoins[ri.ingredient_id] += ri.quantite
        
        manquants = []
        
        for ing_id, quantite_besoin in besoins.items():
            stock = int_db.query(ArticleInventaire).filter_by(ingredient_id=ing_id).first()
            stock_dispo = stock.quantite if stock else 0
            
            if stock_dispo < quantite_besoin:
                ingredient = int_db.query(Ingredient).filter_by(id=ing_id).first()
                manquants.append({
                    "ingredient": ingredient.nom if ingredient else "Inconnu",
                    "besoin": quantite_besoin,
                    "stock": stock_dispo,
                    "manquant": quantite_besoin - stock_dispo,
                })
        
        assert isinstance(manquants, list)

    def test_routines_dans_planning_journalier(self, int_db, planning_semaine, routines_base):
        """Integrer routines dans vue planning journalier."""
        planning = planning_semaine["planning"]
        jour = planning.semaine_debut
        
        repas_jour = int_db.query(Repas).filter_by(
            planning_id=planning.id,
            date_repas=jour
        ).all()
        
        routines_actives = int_db.query(Routine).filter_by(
            actif=True,
            frequence="quotidien"
        ).all()
        
        timeline = []
        
        for routine in routines_actives:
            timeline.append({"type": "routine", "nom": routine.nom})
        
        for repas in repas_jour:
            timeline.append({"type": "repas", "nom": repas.type_repas})
        
        assert len(timeline) > 0
