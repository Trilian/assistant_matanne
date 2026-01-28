"""Tests complémentaires pour les modules famille à faible couverture."""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session


class TestSuiviJulesAvance:
    """Tests avancés pour le suivi de Jules."""
    
    def test_calculer_percentile_croissance(self):
        """Calcule le percentile de croissance."""
        from src.modules.famille.suivi_jules import calculer_percentile
        
        taille_actuelle = 85.0  # cm
        age_mois = 19
        
        percentile = calculer_percentile(taille_actuelle, age_mois, type_mesure="taille")
        assert 0 <= percentile <= 100
    
    def test_suggestions_activites_age(self):
        """Suggère des activités selon l'âge."""
        from src.modules.famille.suivi_jules import suggerer_activites_selon_age
        
        age_mois = 19
        suggestions = suggerer_activites_selon_age(age_mois)
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
    
    def test_alerte_retard_developpement(self):
        """Détecte les retards de développement."""
        from src.modules.famille.suivi_jules import verifier_retards_developpement
        
        jalons = [
            {"nom": "marche", "age_attendu": 12, "age_atteint": 15, "atteint": True},
            {"nom": "premiers_mots", "age_attendu": 12, "age_atteint": None, "atteint": False}
        ]
        
        alertes = verifier_retards_developpement(jalons, age_actuel=19)
        assert isinstance(alertes, list)


class TestBienEtreAvance:
    """Tests avancés pour le bien-être."""
    
    def test_analyse_tendance_humeur(self):
        """Analyse la tendance d'humeur."""
        from src.modules.famille.bien_etre import analyser_tendance_humeur
        
        historique = [
            {"date": date(2026, 1, 20), "humeur": 4},
            {"date": date(2026, 1, 21), "humeur": 3},
            {"date": date(2026, 1, 22), "humeur": 3},
            {"date": date(2026, 1, 23), "humeur": 2},
        ]
        
        tendance = analyser_tendance_humeur(historique)
        assert tendance in ["amelioration", "degradation", "stable"]
    
    def test_recommandations_selon_humeur(self):
        """Recommande des actions selon l'humeur."""
        from src.modules.famille.bien_etre import recommander_actions
        
        humeur_moyenne = 2.5
        recommandations = recommander_actions(humeur_moyenne)
        
        assert isinstance(recommandations, list)
        assert len(recommandations) > 0
    
    @patch('streamlit.line_chart')
    def test_graphique_evolution_humeur(self, mock_chart):
        """Affiche l'évolution de l'humeur."""
        from src.modules.famille.bien_etre import afficher_evolution_humeur
        
        donnees = [
            {"date": "2026-01-20", "humeur": 4},
            {"date": "2026-01-21", "humeur": 3},
        ]
        
        afficher_evolution_humeur(donnees)
        assert mock_chart.called


class TestRoutinesAvancees:
    """Tests avancés pour les routines."""
    
    def test_calculer_temps_total_routine(self):
        """Calcule la durée totale d'une routine."""
        from src.modules.famille.routines import calculer_temps_total
        
        taches = [
            {"duree_minutes": 10},
            {"duree_minutes": 15},
            {"duree_minutes": 20},
        ]
        
        total = calculer_temps_total(taches)
        assert total == 45
    
    def test_optimiser_ordre_taches(self):
        """Optimise l'ordre des tâches."""
        from src.modules.famille.routines import optimiser_ordre_taches
        
        taches = [
            {"nom": "Petit déjeuner", "priorite": 2, "ordre": 3},
            {"nom": "Se laver", "priorite": 3, "ordre": 1},
            {"nom": "S'habiller", "priorite": 1, "ordre": 2},
        ]
        
        optimisees = optimiser_ordre_taches(taches)
        
        # La tâche la plus prioritaire doit être en premier
        assert optimisees[0]["priorite"] == 3
    
    def test_detecter_routine_incomplete(self):
        """Détecte les routines incomplètes."""
        from src.modules.famille.routines import detecter_routine_incomplete
        
        routine = {
            "taches": [
                {"nom": "Tâche 1", "terminee": True},
                {"nom": "Tâche 2", "terminee": False},
                {"nom": "Tâche 3", "terminee": True},
            ]
        }
        
        est_incomplete = detecter_routine_incomplete(routine)
        assert est_incomplete is True


class TestActivitesAvancees:
    """Tests avancés pour les activités."""
    
    def test_filtrer_activites_par_meteo(self):
        """Filtre les activités selon la météo."""
        from src.modules.famille.activites import filtrer_par_meteo
        
        activites = [
            {"nom": "Parc", "interieur": False},
            {"nom": "Musée", "interieur": True},
            {"nom": "Zoo", "interieur": False},
        ]
        
        meteo_pluvieuse = {"condition": "pluie"}
        
        recommandees = filtrer_par_meteo(activites, meteo_pluvieuse)
        
        # Ne devrait recommander que les activités intérieures
        assert all(act["interieur"] for act in recommandees)
    
    def test_calculer_budget_activite(self):
        """Calcule le budget d'une activité."""
        from src.modules.famille.activites import calculer_budget_activite
        
        activite = {
            "prix_adulte": 15.0,
            "prix_enfant": 10.0,
            "nb_adultes": 2,
            "nb_enfants": 1
        }
        
        total = calculer_budget_activite(activite)
        assert total == 40.0  # 2*15 + 1*10
    
    def test_suggerer_activites_age_enfant(self):
        """Suggère des activités selon l'âge."""
        from src.modules.famille.activites import suggerer_selon_age
        
        age_enfant = 19  # mois
        suggestions = suggerer_selon_age(age_enfant)
        
        assert isinstance(suggestions, list)
        # Pour 19 mois: parc, zoo, activités simples
        assert any("parc" in s["nom"].lower() for s in suggestions)


class TestSanteAvancee:
    """Tests avancés pour le module santé."""
    
    def test_calculer_imc_enfant(self):
        """Calcule l'IMC pour un enfant."""
        from src.modules.famille.sante import calculer_imc
        
        poids = 12.5  # kg
        taille = 0.85  # m
        
        imc = calculer_imc(poids, taille)
        assert 10 < imc < 25  # Plage normale pour enfant
    
    def test_interpreter_imc_enfant(self):
        """Interprète l'IMC selon l'âge."""
        from src.modules.famille.sante import interpreter_imc
        
        imc = 16.5
        age_mois = 19
        
        interpretation = interpreter_imc(imc, age_mois)
        assert interpretation in ["insuffisance", "normal", "surpoids", "obesite"]
    
    def test_rappel_vaccinations(self):
        """Génère des rappels de vaccinations."""
        from src.modules.famille.sante import generer_rappels_vaccins
        
        date_naissance = date(2024, 6, 15)
        vaccins_faits = [
            {"nom": "DTCaP", "date": date(2024, 8, 15)},
            {"nom": "RRO", "date": date(2025, 6, 20)},
        ]
        
        rappels = generer_rappels_vaccins(date_naissance, vaccins_faits)
        assert isinstance(rappels, list)


class TestShoppingAvance:
    """Tests avancés pour le module shopping."""
    
    def test_categoriser_article_automatique(self):
        """Catégorise automatiquement un article."""
        from src.modules.famille.shopping import categoriser_automatique
        
        assert categoriser_automatique("Couches Pampers") == "bebe"
        assert categoriser_automatique("Lait infantile") == "bebe"
        assert categoriser_automatique("Jouet Fisher-Price") == "jouets"
    
    def test_detecter_besoin_urgent(self):
        """Détecte les besoins urgents."""
        from src.modules.famille.shopping import detecter_urgence
        
        stock_actuel = 2
        consommation_journaliere = 6  # couches par jour
        
        est_urgent = detecter_urgence(stock_actuel, consommation_journaliere)
        assert est_urgent is True  # Stock < 1 jour
    
    def test_suggerer_quantite_optimale(self):
        """Suggère une quantité d'achat optimale."""
        from src.modules.famille.shopping import suggerer_quantite_optimale
        
        consommation_mensuelle = 180  # couches
        stock_actuel = 20
        
        quantite = suggerer_quantite_optimale(
            consommation_mensuelle=consommation_mensuelle,
            stock_actuel=stock_actuel,
            jours_autonomie_cible=30
        )
        
        assert quantite > 0
        assert quantite >= consommation_mensuelle - stock_actuel


class TestIntegrationCuisineCourses:
    """Tests pour l'intégration cuisine/courses."""
    
    def test_extraire_ingredients_depuis_planning(self):
        """Extrait les ingrédients depuis le planning."""
        from src.modules.famille.integration_cuisine_courses import extraire_ingredients_planning
        
        planning = [
            {"recette_id": 1, "portions": 4},
            {"recette_id": 2, "portions": 2},
        ]
        
        with patch('src.services.recettes.RecetteService') as MockService:
            mock_service = MockService.return_value
            mock_service.obtenir_recette.side_effect = [
                Mock(ingredients=[{"nom": "Poulet", "quantite": 1, "unite": "kg"}]),
                Mock(ingredients=[{"nom": "Pâtes", "quantite": 500, "unite": "g"}])
            ]
            
            ingredients = extraire_ingredients_planning(planning)
            assert len(ingredients) == 2
    
    def test_verifier_stock_disponible(self):
        """Vérifie la disponibilité des ingrédients."""
        from src.modules.famille.integration_cuisine_courses import verifier_disponibilite_stock
        
        ingredients_requis = [
            {"nom": "Poulet", "quantite": 1, "unite": "kg"},
            {"nom": "Tomates", "quantite": 500, "unite": "g"}
        ]
        
        stock_actuel = [
            {"nom": "Poulet", "quantite": 2, "unite": "kg"},
            {"nom": "Tomates", "quantite": 200, "unite": "g"}
        ]
        
        manquants = verifier_disponibilite_stock(ingredients_requis, stock_actuel)
        
        # Les tomates sont insuffisantes
        assert len(manquants) == 1
        assert manquants[0]["nom"] == "Tomates"


class TestAccueilFamille:
    """Tests pour l'accueil famille."""
    
    @patch('streamlit.metric')
    def test_afficher_resume_jules(self, mock_metric):
        """Affiche le résumé de Jules."""
        from src.modules.famille.accueil import afficher_resume_jules
        
        donnees = {
            "age_jours": 580,
            "taille": 85.0,
            "poids": 12.5,
            "dernier_jalon": "Premiers pas"
        }
        
        afficher_resume_jules(donnees)
        assert mock_metric.call_count >= 2
    
    @patch('streamlit.progress')
    def test_afficher_progression_routines(self, mock_progress):
        """Affiche la progression des routines."""
        from src.modules.famille.accueil import afficher_progression_routines
        
        routines = [
            {"nom": "Matin", "taches_terminees": 5, "taches_total": 7},
            {"nom": "Soir", "taches_terminees": 3, "taches_total": 5}
        ]
        
        afficher_progression_routines(routines)
        assert mock_progress.call_count == 2


class TestJulesModule:
    """Tests pour le module jules.py."""
    
    def test_calculer_age_exact(self):
        """Calcule l'âge exact en mois et jours."""
        from src.modules.famille.jules import calculer_age_exact
        
        date_naissance = date(2024, 6, 15)
        date_reference = date(2026, 1, 28)
        
        age = calculer_age_exact(date_naissance, date_reference)
        
        assert "mois" in age
        assert "jours" in age
        assert age["mois"] == 19
    
    @patch('streamlit.tabs')
    def test_interface_tabs_jules(self, mock_tabs):
        """Teste l'interface à onglets."""
        from src.modules.famille.jules import afficher_interface_jules
        
        mock_tabs.return_value = [MagicMock() for _ in range(4)]
        
        afficher_interface_jules()
        assert mock_tabs.called


@pytest.fixture
def mock_famille_db(test_db: Session):
    """Données de test pour la famille."""
    from src.core.models import ProfilEnfant
    
    enfant = ProfilEnfant(
        prenom="Jules",
        date_naissance=date(2024, 6, 15),
        sexe="M",
        poids_naissance=3.5,
        taille_naissance=50.0
    )
    test_db.add(enfant)
    test_db.commit()
    
    return enfant
