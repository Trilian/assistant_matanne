"""
Tests complets des modules *_logic.py - Architecture refactorisée
Tests purs de logique métier sans dépendance Streamlit/DB
"""
import pytest
from datetime import date, timedelta, time


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CUISINE: RECETTES_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestRecettesLogic:
    def test_valider_recette_valide(self):
        from src.domains.cuisine.logic.recettes_logic import valider_recette
        
        data = {
            "nom": "PÃ¢tes Carbonara",
            "ingredients": ["pÃ¢tes", "lardons", "oeufs"],
            "instructions": ["Cuire les pÃ¢tes", "Mélanger"],
            "portions": 4  # Requis et doit être > 0
        }
        valid, error = valider_recette(data)
        assert valid is True
        assert error is None
    
    def test_valider_recette_nom_manquant(self):
        from src.domains.cuisine.logic.recettes_logic import valider_recette
        
        data = {"ingredients": ["test"], "instructions": ["test"], "portions": 2}
        valid, error = valider_recette(data)
        assert valid is False
        assert error is not None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CUISINE: INVENTAIRE_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestInventaireLogic:
    def test_calculer_status_stock_ok(self):
        from src.domains.cuisine.logic.inventaire_logic import calculer_status_stock
        
        article = {"quantite": 10, "seuil_alerte": 5}
        status = calculer_status_stock(article)
        assert status == "ok"
    
    def test_calculer_status_stock_bas(self):
        from src.domains.cuisine.logic.inventaire_logic import calculer_status_stock
        
        article = {"quantite": 2, "seuil_alerte": 5, "seuil_critique": 1}
        status = calculer_status_stock(article)
        assert status == "stock_bas"
    
    def test_calculer_status_peremption_expire(self):
        from src.domains.cuisine.logic.inventaire_logic import calculer_status_peremption
        
        article = {"date_peremption": date.today() - timedelta(days=1)}
        status = calculer_status_peremption(article)
        assert status == "perime"
    
    def test_filtrer_par_emplacement(self):
        from src.domains.cuisine.logic.inventaire_logic import filtrer_par_emplacement
        
        articles = [
            {"nom": "Tomate", "emplacement": "Réfrigérateur"},
            {"nom": "PÃ¢tes", "emplacement": "Placard"},
            {"nom": "Lait", "emplacement": "Réfrigérateur"}
        ]
        resultats = filtrer_par_emplacement(articles, "Réfrigérateur")
        assert len(resultats) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CUISINE: COURSES_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCoursesLogic:
    def test_filtrer_par_priorite(self):
        from src.domains.cuisine.logic.courses_logic import filtrer_par_priorite
        
        articles = [
            {"nom": "Lait", "priorite": "haute"},
            {"nom": "Cookies", "priorite": "basse"},
            {"nom": "Pain", "priorite": "haute"}
        ]
        resultats = filtrer_par_priorite(articles, "haute")
        assert len(resultats) == 2
    
    def test_grouper_par_rayon(self):
        from src.domains.cuisine.logic.courses_logic import grouper_par_rayon
        
        articles = [
            {"nom": "Tomate", "rayon_magasin": "Fruits & Légumes"},
            {"nom": "Lait", "rayon_magasin": "Laitier"},
            {"nom": "Pomme", "rayon_magasin": "Fruits & Légumes"}
        ]
        groupes = grouper_par_rayon(articles)
        assert len(groupes["Fruits & Légumes"]) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MAISON: JARDIN_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestJardinLogic:
    def test_get_saison_actuelle(self):
        from src.domains.maison.logic.jardin_logic import get_saison_actuelle
        
        saison = get_saison_actuelle()  # Pas de paramètre, utilise date.today()
        # Les saisons attendues: printemps, été, automne, hiver
        assert saison in ["printemps", "été", "automne", "hiver"]
    
    def test_calculer_jours_avant_arrosage(self):
        from src.domains.maison.logic.jardin_logic import calculer_jours_avant_arrosage
        
        plante = {"dernier_arrosage": date.today() - timedelta(days=2), "frequence_arrosage": 5}
        jours = calculer_jours_avant_arrosage(plante)
        assert jours == 3


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MAISON: PROJETS_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestProjetsLogic:
    def test_calculer_urgence_projet(self):
        from src.domains.maison.logic.projets_logic import calculer_urgence_projet
        
        projet = {"priorite": "haute", "date_echeance": date.today() + timedelta(days=2)}
        urgence = calculer_urgence_projet(projet)
        assert urgence in ["critique", "haute", "moyenne", "basse"]
    
    def test_filtrer_par_statut(self):
        from src.domains.maison.logic.projets_logic import filtrer_par_statut
        
        projets = [
            {"titre": "P1", "statut": "en_cours"},
            {"titre": "P2", "statut": "termine"},
            {"titre": "P3", "statut": "en_cours"}
        ]
        resultats = filtrer_par_statut(projets, "en_cours")
        assert len(resultats) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MAISON: ENTRETIEN_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestEntretienLogic:
    def test_calculer_prochaine_occurrence(self):
        from src.domains.maison.logic.entretien_logic import calculer_prochaine_occurrence
        
        prochaine = calculer_prochaine_occurrence(date.today(), "hebdomadaire")
        assert prochaine == date.today() + timedelta(days=7)
    
    def test_get_taches_aujourd_hui(self):
        from src.domains.maison.logic.entretien_logic import get_taches_aujourd_hui, calculer_prochaine_occurrence
        
        taches = [
            {
                "titre": "T1", 
                "derniere_execution": date.today() - timedelta(days=7), 
                "frequence": "hebdomadaire"
            },
            {
                "titre": "T2", 
                "derniere_execution": date.today() - timedelta(days=1), 
                "frequence": "hebdomadaire"
            }
        ]
        resultats = get_taches_aujourd_hui(taches)
        assert len(resultats) >= 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FAMILLE: ACTIVITES_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestActivitesLogic:
    def test_filtrer_par_type(self):
        from src.domains.famille.logic.activites_logic import filtrer_par_type
        
        activites = [
            {"titre": "A1", "type": "Sport"},
            {"titre": "A2", "type": "Culture"},
            {"titre": "A3", "type": "Sport"}
        ]
        resultats = filtrer_par_type(activites, "Sport")
        assert len(resultats) == 2
    
    def test_calculer_statistiques_activites(self):
        from src.domains.famille.logic.activites_logic import calculer_statistiques_activites
        
        activites = [
            {"type": "Sport", "cout": 20, "duree": 60},
            {"type": "Culture", "cout": 15, "duree": 90}
        ]
        stats = calculer_statistiques_activites(activites)
        assert stats["total"] == 2
        assert stats["cout_total"] == 35


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FAMILLE: BIEN_ETRE_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBienEtreLogic:
    def test_analyser_tendance(self):
        from src.domains.famille.logic.bien_etre_logic import analyser_tendance
        
        entrees = [
            {"date": date.today(), "categorie": "Sommeil", "valeur": 7},
            {"date": date.today() - timedelta(days=1), "categorie": "Sommeil", "valeur": 8}
        ]
        tendance = analyser_tendance(entrees, "Sommeil", jours=7)
        assert "moyenne" in tendance
        assert "tendance" in tendance
    
    def test_analyser_sommeil(self):
        from src.domains.famille.logic.bien_etre_logic import analyser_sommeil
        
        entrees = [
            {"date": date.today(), "heures_sommeil": 8},
            {"date": date.today() - timedelta(days=1), "heures_sommeil": 7}
        ]
        analyse = analyser_sommeil(entrees, jours=7)
        assert "moyenne" in analyse
        assert "qualite" in analyse


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FAMILLE: SHOPPING_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestShoppingLogic:
    def test_calculer_cout_liste(self):
        from src.domains.famille.logic.shopping_logic import calculer_cout_liste
        
        articles = [
            {"quantite": 2, "prix_estime": 5.50},
            {"quantite": 3, "prix_estime": 2.30}
        ]
        couts = calculer_cout_liste(articles)
        assert couts["estime"] == 17.90
    
    def test_filtrer_par_liste(self):
        from src.domains.famille.logic.shopping_logic import filtrer_par_liste
        
        articles = [
            {"titre": "A1", "liste": "Jules"},
            {"titre": "A2", "liste": "Nous"},
            {"titre": "A3", "liste": "Jules"}
        ]
        resultats = filtrer_par_liste(articles, "Jules")
        assert len(resultats) == 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FAMILLE: ROUTINES_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestRoutinesLogic:
    def test_get_moment_journee(self):
        from src.domains.famille.logic.routines_logic import get_moment_journee
        
        moment = get_moment_journee(time(10, 30))
        assert moment == "Matin"
        
        moment = get_moment_journee(time(15, 0))
        assert moment == "Après-midi"
    
    def test_calculer_duree_routine(self):
        from src.domains.famille.logic.routines_logic import calculer_duree_routine
        
        routines = [
            {"duree": 15},
            {"duree": 20},
            {"duree": 10}
        ]
        duree_totale = calculer_duree_routine(routines)
        assert duree_totale == 45


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FAMILLE: JULES_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestJulesLogic:
    def test_calculer_age_mois(self):
        from src.domains.famille.logic.jules_logic import calculer_age_mois
        
        date_naissance = date(2024, 6, 22)
        date_ref = date(2026, 1, 29)
        age_mois = calculer_age_mois(date_naissance, date_ref)
        assert age_mois == 19
    
    def test_formater_age(self):
        from src.domains.famille.logic.jules_logic import formater_age
        
        date_naissance = date(2024, 6, 22)
        date_ref = date(2026, 1, 29)
        age_str = formater_age(date_naissance, date_ref)
        assert "1 an" in age_str and "7 mois" in age_str
    
    def test_get_tranche_age(self):
        from src.domains.famille.logic.jules_logic import get_tranche_age
        
        tranche = get_tranche_age(19)
        assert tranche == "18-24"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PLANNING: CALENDRIER_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestCalendrierLogic:
    def test_get_jours_mois(self):
        from src.domains.planning.logic.calendrier_logic import get_jours_mois
        
        jours = get_jours_mois(2026, 1)
        assert len(jours) == 31
    
    def test_get_mois_suivant(self):
        from src.domains.planning.logic.calendrier_logic import get_mois_suivant
        
        annee, mois = get_mois_suivant(2026, 1)
        assert annee == 2026 and mois == 2
        
        annee, mois = get_mois_suivant(2026, 12)
        assert annee == 2027 and mois == 1
    
    def test_formater_date_complete(self):
        from src.domains.planning.logic.calendrier_logic import formater_date_complete
        
        formatted = formater_date_complete(date(2026, 1, 29))
        assert "Jeudi" in formatted
        assert "29" in formatted
        assert "Janvier" in formatted


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PLANNING: VUE_ENSEMBLE_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestVueEnsembleLogic:
    def test_analyser_charge_globale(self):
        from src.domains.planning.logic.vue_ensemble_logic import analyser_charge_globale
        
        evenements = [{"titre": "E1"}, {"titre": "E2"}]
        taches = [
            {"titre": "T1", "complete": False},
            {"titre": "T2", "complete": True}
        ]
        
        analyse = analyser_charge_globale(evenements, taches)
        assert analyse["total_evenements"] == 2
        assert analyse["taches_completees"] == 1
    
    def test_identifier_taches_urgentes(self):
        from src.domains.planning.logic.vue_ensemble_logic import identifier_taches_urgentes
        
        taches = [
            {"titre": "T1", "date_limite": date.today() + timedelta(days=1), "complete": False},
            {"titre": "T2", "date_limite": date.today() + timedelta(days=10), "complete": False}
        ]
        
        urgentes = identifier_taches_urgentes(taches, jours_seuil=3)
        assert len(urgentes) == 1


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PLANNING: VUE_SEMAINE_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestVueSemaineLogic:
    def test_get_debut_semaine(self):
        from src.domains.planning.logic.vue_semaine_logic import get_debut_semaine
        
        debut = get_debut_semaine(date(2026, 1, 29))  # Jeudi
        assert debut.weekday() == 0  # Lundi
    
    def test_get_jours_semaine(self):
        from src.domains.planning.logic.vue_semaine_logic import get_jours_semaine
        
        jours = get_jours_semaine(date(2026, 1, 29))
        assert len(jours) == 7
        assert jours[0].weekday() == 0  # Lundi
    
    def test_calculer_charge_semaine(self):
        from src.domains.planning.logic.vue_semaine_logic import calculer_charge_semaine
        
        evenements = [
            {"date": date.today(), "duree": 60},
            {"date": date.today(), "duree": 90}
        ]
        
        charge = calculer_charge_semaine(evenements, date.today())
        assert "total_evenements" in charge


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROOT: ACCUEIL_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestAccueilLogic:
    def test_calculer_metriques_dashboard(self):
        from src.domains.shared.logic.accueil_logic import calculer_metriques_dashboard
        
        data = {
            "recettes": [{"nom": "R1"}, {"nom": "R2"}],
            "courses": [{"achete": False}, {"achete": True}],
            "activites": [{"date": date.today()}],
            "inventaire": []
        }
        
        metriques = calculer_metriques_dashboard(data)
        assert metriques["total_recettes"] == 2
        assert metriques["courses_actives"] == 1
    
    def test_est_cette_semaine(self):
        from src.domains.shared.logic.accueil_logic import est_cette_semaine
        
        assert est_cette_semaine(date.today()) is True
        assert est_cette_semaine(date.today() - timedelta(days=10)) is False
    
    def test_generer_notifications(self):
        from src.domains.shared.logic.accueil_logic import generer_notifications
        
        data = {
            "inventaire": [{"expire": True}],
            "courses": [{"achete": False}],
            "activites": []
        }
        
        notifs = generer_notifications(data)
        assert len(notifs) > 0
        assert any("inventaire" in n["message"].lower() for n in notifs)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROOT: BARCODE_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestBarcodeLogic:
    def test_valider_code_barres_valide(self):
        from src.domains.shared.logic.barcode_logic import valider_code_barres
        
        valide, erreur = valider_code_barres("3017620422003")  # EAN-13
        assert valide is True
        assert erreur is None
    
    def test_valider_code_barres_invalide(self):
        from src.domains.shared.logic.barcode_logic import valider_code_barres
        
        valide, erreur = valider_code_barres("12345")
        assert valide is False
        assert "court" in erreur.lower()
    
    def test_detecter_type_code_barres(self):
        from src.domains.shared.logic.barcode_logic import detecter_type_code_barres
        
        assert detecter_type_code_barres("3017620422003") == "EAN-13"
        assert detecter_type_code_barres("12345678") == "EAN-8"
    
    def test_formater_code_barres(self):
        from src.domains.shared.logic.barcode_logic import formater_code_barres
        
        formatted = formater_code_barres("3017620422003")
        assert " " in formatted
    
    def test_valider_checksum_ean13(self):
        from src.domains.shared.logic.barcode_logic import valider_checksum_ean13
        
        # Code valide connu
        assert valider_checksum_ean13("3017620422003") is True


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROOT: PARAMETRES_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestParametresLogic:
    def test_valider_parametres_valide(self):
        from src.domains.shared.logic.parametres_logic import valider_parametres
        
        data = {
            "nom_famille": "Dupont",
            "email": "test@example.com",
            "devise": "EUR",
            "langue": "fr"
        }
        
        valide, erreurs = valider_parametres(data)
        assert valide is True
        assert len(erreurs) == 0
    
    def test_valider_email_valide(self):
        from src.domains.shared.logic.parametres_logic import valider_email
        
        valide, erreur = valider_email("test@example.com")
        assert valide is True
    
    def test_valider_email_invalide(self):
        from src.domains.shared.logic.parametres_logic import valider_email
        
        valide, erreur = valider_email("invalide")
        assert valide is False
    
    def test_comparer_versions(self):
        from src.domains.shared.logic.parametres_logic import comparer_versions
        
        assert comparer_versions("1.2.3", "1.3.0") == -1
        assert comparer_versions("2.0.0", "1.9.9") == 1
        assert comparer_versions("1.5.0", "1.5.0") == 0
    
    def test_generer_config_defaut(self):
        from src.domains.shared.logic.parametres_logic import generer_config_defaut
        
        config = generer_config_defaut()
        assert "nom_famille" in config
        assert "devise" in config
        assert config["devise"] == "EUR"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ROOT: RAPPORTS_LOGIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestRapportsLogic:
    def test_generer_rapport_synthese(self):
        from src.modules.rapports_logic import generer_rapport_synthese
        
        data = {
            "recettes": [{"nom": "R1"}],
            "courses": [{"nom": "C1"}]
        }
        
        rapport = generer_rapport_synthese(data, periode="mois")
        assert "titre" in rapport
        assert "statistiques" in rapport
        assert rapport["periode"] == "mois"
    
    def test_calculer_statistiques_periode(self):
        from src.modules.rapports_logic import calculer_statistiques_periode
        
        items = [
            {"date": date.today()},
            {"date": date.today() - timedelta(days=1)}
        ]
        
        stats = calculer_statistiques_periode(items, date.today() - timedelta(days=7), date.today())
        assert stats["total"] == 2
    
    def test_formater_rapport_texte(self):
        from src.modules.rapports_logic import formater_rapport_texte
        
        rapport = {
            "titre": "Test Rapport",
            "periode": "mois",
            "date_debut": date.today(),
            "date_fin": date.today(),
            "date_generation": date.today(),
            "statistiques": {"recettes": 5},
            "sections": {"recettes": {"total": 5}}
        }
        
        texte = formater_rapport_texte(rapport)
        assert "Test Rapport" in texte.upper()
        assert "mois" in texte


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODULES ADDITIONNELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestAccueilLogicFamille:
    def test_import_module(self):
        from src.modules.famille import accueil_logic
        assert accueil_logic is not None


class TestSuiviJulesLogic:
    def test_import_module(self):
        from src.modules.famille import suivi_jules_logic
        assert suivi_jules_logic is not None


class TestSanteLogic:
    def test_import_module(self):
        from src.modules.famille import sante_logic
        assert sante_logic is not None


