"""
Tests complets pour tous les modules *_logic créés.
Objectif: Atteindre 40% de couverture en testant la logique pure.
"""
import pytest
from datetime import date, timedelta, time


# ═══════════════════════════════════════════════════════════
# TESTS PLANNING LOGIC (CUISINE)
# ═══════════════════════════════════════════════════════════

class TestPlanningLogicCuisine:
    """Tests pour planning_logic.py (cuisine)."""
    
    def test_get_debut_semaine(self):
        """Calcul début de semaine."""
        from src.modules.cuisine.planning_logic import get_debut_semaine
        
        # Mercredi 29 jan 2026 → lundi 27 jan
        test_date = date(2026, 1, 29)
        debut = get_debut_semaine(test_date)
        assert debut == date(2026, 1, 27)
        assert debut.weekday() == 0  # Lundi
    
    def test_get_dates_semaine(self):
        """Liste des 7 dates."""
        from src.modules.cuisine.planning_logic import get_dates_semaine
        
        dates = get_dates_semaine(date(2026, 1, 29))
        assert len(dates) == 7
        assert dates[0].weekday() == 0  # Lundi
        assert dates[6].weekday() == 6  # Dimanche
    
    def test_valider_repas_ok(self):
        """Validation repas valide."""
        from src.modules.cuisine.planning_logic import valider_repas
        
        data = {"jour": "Lundi", "type_repas": "déjeuner", "recette_id": 1}
        valid, error = valider_repas(data)
        assert valid is True
        assert error is None
    
    def test_valider_repas_jour_manquant(self):
        """Validation sans jour."""
        from src.modules.cuisine.planning_logic import valider_repas
        
        data = {"type_repas": "déjeuner", "recette_id": 1}
        valid, error = valider_repas(data)
        assert valid is False
        assert "jour" in error.lower()


# ═══════════════════════════════════════════════════════════
# TESTS JARDIN LOGIC (MAISON)
# ═══════════════════════════════════════════════════════════

class TestJardinLogic:
    """Tests pour jardin_logic.py."""
    
    def test_get_saison_actuelle(self):
        """Saison actuelle."""
        from src.modules.maison.jardin_logic import get_saison_actuelle
        
        saison = get_saison_actuelle()
        assert saison in ["Printemps", "Été", "Automne", "Hiver"]
    
    def test_calculer_jours_avant_arrosage(self):
        """Jours avant arrosage."""
        from src.modules.maison.jardin_logic import calculer_jours_avant_arrosage
        
        plante = {
            "dernier_arrosage": date.today() - timedelta(days=5),
            "frequence_arrosage": 7
        }
        jours = calculer_jours_avant_arrosage(plante)
        assert jours == 2
    
    def test_get_plantes_a_arroser(self):
        """Liste plantes à arroser."""
        from src.modules.maison.jardin_logic import get_plantes_a_arroser
        
        plantes = [
            {"nom": "Tomate", "dernier_arrosage": date.today() - timedelta(days=7), "frequence_arrosage": 7},
            {"nom": "Basilic", "dernier_arrosage": date.today() - timedelta(days=1), "frequence_arrosage": 3}
        ]
        
        a_arroser = get_plantes_a_arroser(plantes, jours_avance=1)
        assert len(a_arroser) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS PROJETS LOGIC (MAISON)
# ═══════════════════════════════════════════════════════════

class TestProjetsLogic:
    """Tests pour projets_logic.py."""
    
    def test_calculer_urgence_projet(self):
        """Calcul urgence."""
        from src.modules.maison.projets_logic import calculer_urgence_projet
        
        projet = {
            "priorite": "Moyenne",
            "date_limite": date.today() + timedelta(days=3)
        }
        urgence = calculer_urgence_projet(projet)
        assert urgence == "Urgente"
    
    def test_filtrer_par_statut(self):
        """Filtrage par statut."""
        from src.modules.maison.projets_logic import filtrer_par_statut
        
        projets = [
            {"titre": "P1", "statut": "En cours"},
            {"titre": "P2", "statut": "Terminé"},
            {"titre": "P3", "statut": "En cours"}
        ]
        
        en_cours = filtrer_par_statut(projets, "En cours")
        assert len(en_cours) == 2
    
    def test_calculer_progression(self):
        """Calcul progression."""
        from src.modules.maison.projets_logic import calculer_progression
        
        projet = {"statut": "Terminé"}
        prog = calculer_progression(projet)
        assert prog == 100.0


# ═══════════════════════════════════════════════════════════
# TESTS ENTRETIEN LOGIC (MAISON)
# ═══════════════════════════════════════════════════════════

class TestEntretienLogic:
    """Tests pour entretien_logic.py."""
    
    def test_calculer_prochaine_occurrence(self):
        """Prochaine occurrence."""
        from src.modules.maison.entretien_logic import calculer_prochaine_occurrence
        
        derniere = date(2026, 1, 1)
        prochaine = calculer_prochaine_occurrence(derniere, "Hebdomadaire")
        assert prochaine == date(2026, 1, 8)
    
    def test_get_taches_aujourd_hui(self):
        """Tâches du jour."""
        from src.modules.maison.entretien_logic import get_taches_aujourd_hui
        
        taches = [
            {"titre": "T1", "derniere_execution": date.today() - timedelta(days=7), "frequence": "Hebdomadaire"},
            {"titre": "T2", "derniere_execution": date.today() - timedelta(days=2), "frequence": "Hebdomadaire"}
        ]
        
        aujourdhui = get_taches_aujourd_hui(taches)
        assert len(aujourdhui) >= 1
    
    def test_valider_tache(self):
        """Validation tâche."""
        from src.modules.maison.entretien_logic import valider_tache
        
        data = {"titre": "Ménage", "frequence": "Quotidienne", "categorie": "Ménage"}
        valid, errors = valider_tache(data)
        assert valid is True


# ═══════════════════════════════════════════════════════════
# TESTS SUIVI JULES LOGIC (FAMILLE)
# ═══════════════════════════════════════════════════════════

class TestSuiviJulesLogic:
    """Tests pour suivi_jules_logic.py."""
    
    def test_calculer_age(self):
        """Calcul âge."""
        from src.modules.famille.suivi_jules_logic import calculer_age
        
        naissance = date(2024, 6, 15)
        age = calculer_age(naissance)
        
        assert "annees" in age
        assert "mois" in age
        assert "total_mois" in age
        assert age["total_mois"] > 0
    
    def test_formater_age(self):
        """Formatage âge."""
        from src.modules.famille.suivi_jules_logic import formater_age
        
        age_dict = {"annees": 1, "mois": 7, "jours": 14}
        texte = formater_age(age_dict)
        
        assert "1 an" in texte
        assert "7 mois" in texte
    
    def test_get_etapes_age(self):
        """Étapes développement."""
        from src.modules.famille.suivi_jules_logic import get_etapes_age
        
        etapes = get_etapes_age(18)
        assert isinstance(etapes, list)
        assert len(etapes) > 0


# ═══════════════════════════════════════════════════════════
# TESTS SANTÉ LOGIC (FAMILLE)
# ═══════════════════════════════════════════════════════════

class TestSanteLogic:
    """Tests pour sante_logic.py."""
    
    def test_calculer_progression_objectif(self):
        """Progression objectif."""
        from src.modules.famille.sante_logic import calculer_progression_objectif
        
        objectif = {"valeur_actuelle": 75, "valeur_cible": 100}
        prog = calculer_progression_objectif(objectif)
        
        assert prog["pourcentage"] == 75.0
        assert prog["statut"] == "Presque atteint"
        assert prog["restant"] == 25
    
    def test_valider_objectif(self):
        """Validation objectif."""
        from src.modules.famille.sante_logic import valider_objectif
        
        data = {"titre": "Perdre du poids", "categorie": "Poids", "valeur_cible": 75, "unite": "kg"}
        valid, errors = valider_objectif(data)
        assert valid is True


# ═══════════════════════════════════════════════════════════
# TESTS PLANNING LOGIC (MODULES PLANNING)
# ═══════════════════════════════════════════════════════════

class TestPlanningLogicModules:
    """Tests pour planning_logic.py (modules planning)."""
    
    def test_calculer_charge_jour_vide(self):
        """Charge jour vide."""
        from src.modules.planning.planning_logic import calculer_charge_jour
        
        charge = calculer_charge_jour([])
        assert charge["total_activites"] == 0
        assert charge["niveau"] == "faible"
    
    def test_calculer_charge_jour_charge(self):
        """Charge jour chargé."""
        from src.modules.planning.planning_logic import calculer_charge_jour
        
        activites = [{"titre": f"Act{i}"} for i in range(12)]
        charge = calculer_charge_jour(activites)
        
        assert charge["total_activites"] == 12
        assert charge["niveau"] in ["eleve", "tres_eleve"]
    
    def test_grouper_par_categorie(self):
        """Groupement catégories."""
        from src.modules.planning.planning_logic import grouper_par_categorie
        
        activites = [
            {"titre": "A1", "categorie": "Travail"},
            {"titre": "A2", "categorie": "Loisir"},
            {"titre": "A3", "categorie": "Travail"}
        ]
        
        groupes = grouper_par_categorie(activites)
        assert len(groupes["Travail"]) == 2
        assert len(groupes["Loisir"]) == 1


# ═══════════════════════════════════════════════════════════
# TESTS FAMILLE LOGIC (SHOPPING, ACTIVITÉS, BIEN-ÊTRE)
# ═══════════════════════════════════════════════════════════

class TestFamilleLogic:
    """Tests pour famille_logic.py."""
    
    def test_calculer_cout_liste(self):
        """Coût liste shopping."""
        from src.modules.famille.famille_logic import calculer_cout_liste
        
        articles = [
            {"quantite": 2, "prix_estime": 15.0},
            {"quantite": 1, "prix_estime": 25.0, "prix_reel": 22.0}
        ]
        
        couts = calculer_cout_liste(articles)
        assert couts["estime"] == 55.0
        assert couts["reel"] == 22.0
    
    def test_filtrer_shopping_par_liste(self):
        """Filtrage par liste."""
        from src.modules.famille.famille_logic import filtrer_shopping_par_liste
        
        articles = [
            {"titre": "A1", "liste": "Jules"},
            {"titre": "A2", "liste": "Nous"},
            {"titre": "A3", "liste": "Jules"}
        ]
        
        jules = filtrer_shopping_par_liste(articles, "Jules")
        assert len(jules) == 2
    
    def test_valider_article_shopping(self):
        """Validation article."""
        from src.modules.famille.famille_logic import valider_article_shopping
        
        data = {"titre": "Jouet", "categorie": "Jouets", "quantite": 1}
        valid, errors = valider_article_shopping(data)
        assert valid is True
    
    def test_calculer_score_bien_etre_global(self):
        """Score bien-être."""
        from src.modules.famille.famille_logic import calculer_score_bien_etre_global
        
        entrees = {
            "Sommeil": [{"valeur": 8}, {"valeur": 7}],
            "Nutrition": [{"valeur": 6}, {"valeur": 7}]
        }
        
        score = calculer_score_bien_etre_global(entrees)
        assert "score" in score
        assert "niveau" in score
        assert 0 <= score["score"] <= 10


# ═══════════════════════════════════════════════════════════
# TESTS DE STRUCTURE
# ═══════════════════════════════════════════════════════════

class TestTousLesModulesLogic:
    """Tests de structure pour tous les modules logic."""
    
    def test_tous_modules_importables(self):
        """Tous les modules s'importent."""
        modules = [
            "src.modules.cuisine.planning_logic",
            "src.modules.maison.jardin_logic",
            "src.modules.maison.projets_logic",
            "src.modules.maison.entretien_logic",
            "src.modules.famille.suivi_jules_logic",
            "src.modules.famille.sante_logic",
            "src.modules.planning.planning_logic",
            "src.modules.famille.famille_logic"
        ]
        
        for module_name in modules:
            module = __import__(module_name, fromlist=[''])
            assert module is not None
    
    def test_planning_logic_cuisine_functions(self):
        """Fonctions planning_logic cuisine."""
        from src.modules.cuisine import planning_logic
        
        functions = [
            'get_debut_semaine', 'get_dates_semaine', 'valider_repas',
            'calculer_statistiques_planning', 'generer_structure_semaine'
        ]
        
        for func in functions:
            assert hasattr(planning_logic, func)
    
    def test_jardin_logic_functions(self):
        """Fonctions jardin_logic."""
        from src.modules.maison import jardin_logic
        
        functions = [
            'get_saison_actuelle', 'calculer_jours_avant_arrosage',
            'get_plantes_a_arroser', 'calculer_statistiques_jardin', 'valider_plante'
        ]
        
        for func in functions:
            assert hasattr(jardin_logic, func)
    
    def test_projets_logic_functions(self):
        """Fonctions projets_logic."""
        from src.modules.maison import projets_logic
        
        functions = [
            'calculer_urgence_projet', 'filtrer_par_statut',
            'calculer_statistiques_projets', 'valider_projet', 'calculer_progression'
        ]
        
        for func in functions:
            assert hasattr(projets_logic, func)
    
    def test_planning_logic_modules_functions(self):
        """Fonctions planning_logic modules."""
        from src.modules.planning import planning_logic
        
        functions = [
            'calculer_charge_jour', 'calculer_charge_semaine',
            'detecter_conflits_horaires', 'get_alertes_semaine', 'grouper_par_categorie'
        ]
        
        for func in functions:
            assert hasattr(planning_logic, func)
