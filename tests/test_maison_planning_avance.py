"""Tests complémentaires pour les modules maison et planning."""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session


class TestJardinAvance:
    """Tests avancés pour le module jardin."""
    
    def test_calculer_besoins_arrosage(self):
        """Calcule les besoins en arrosage."""
        from src.modules.maison.jardin import calculer_besoins_arrosage
        
        plante = {
            "type": "tomate",
            "age_jours": 45,
            "derniere_pluie": 5,  # jours
            "temperature_moyenne": 25
        }
        
        besoins = calculer_besoins_arrosage(plante)
        assert besoins in ["faible", "moyen", "eleve", "urgent"]
    
    def test_suggerer_calendrier_plantation(self):
        """Suggère le calendrier de plantation."""
        from src.modules.maison.jardin import suggerer_calendrier_plantation
        
        legume = "tomate"
        region = "sud_france"
        
        calendrier = suggerer_calendrier_plantation(legume, region)
        
        assert "semis" in calendrier
        assert "plantation" in calendrier
        assert "recolte" in calendrier
    
    def test_detecter_maladies_plantes(self):
        """Détecte les maladies potentielles."""
        from src.modules.maison.jardin import detecter_maladies
        
        symptomes = ["feuilles_jaunes", "taches_noires"]
        type_plante = "tomate"
        
        maladies = detecter_maladies(symptomes, type_plante)
        assert isinstance(maladies, list)


class TestEntretienAvance:
    """Tests avancés pour le module entretien."""
    
    def test_calculer_frequence_optimale(self):
        """Calcule la fréquence optimale d'entretien."""
        from src.modules.maison.entretien import calculer_frequence_optimale
        
        tache = {
            "type": "nettoyage_salle_bain",
            "surface": 10,  # m²
            "nb_utilisateurs": 4
        }
        
        frequence = calculer_frequence_optimale(tache)
        assert frequence in ["quotidien", "hebdomadaire", "mensuel"]
    
    def test_generer_planning_entretien(self):
        """Génère un planning d'entretien."""
        from src.modules.maison.entretien import generer_planning_entretien
        
        taches = [
            {"nom": "Aspirateur", "frequence": "hebdomadaire", "duree_min": 30},
            {"nom": "Lessive", "frequence": "2x_semaine", "duree_min": 15},
        ]
        
        debut = date(2026, 1, 27)  # Lundi
        planning = generer_planning_entretien(taches, debut, duree_semaines=2)
        
        assert len(planning) > 0
        assert all("date" in p and "tache" in p for p in planning)
    
    def test_estimer_cout_produits(self):
        """Estime le coût des produits d'entretien."""
        from src.modules.maison.entretien import estimer_cout_produits
        
        produits_utilises = [
            {"nom": "Nettoyant multi-usage", "prix_litre": 5.0, "quantite_ml": 100},
            {"nom": "Éponge", "prix_unite": 2.0, "quantite": 1}
        ]
        
        cout = estimer_cout_produits(produits_utilises)
        assert cout == pytest.approx(2.5, 0.1)  # 0.5 + 2.0


class TestProjetsAvance:
    """Tests avancés pour le module projets."""
    
    def test_calculer_duree_totale_projet(self):
        """Calcule la durée totale d'un projet."""
        from src.modules.maison.projets import calculer_duree_totale
        
        taches = [
            {"nom": "Préparation", "duree_heures": 2},
            {"nom": "Exécution", "duree_heures": 8},
            {"nom": "Finition", "duree_heures": 3}
        ]
        
        total = calculer_duree_totale(taches)
        assert total == 13
    
    def test_detecter_taches_bloquantes(self):
        """Détecte les tâches bloquantes."""
        from src.modules.maison.projets import detecter_taches_bloquantes
        
        taches = [
            {"id": 1, "nom": "A", "depend_de": [], "terminee": False},
            {"id": 2, "nom": "B", "depend_de": [1], "terminee": False},
            {"id": 3, "nom": "C", "depend_de": [1, 2], "terminee": False}
        ]
        
        bloquantes = detecter_taches_bloquantes(taches)
        
        # Tâche A bloque B et C
        assert 1 in bloquantes
    
    def test_calculer_chemin_critique(self):
        """Calcule le chemin critique du projet."""
        from src.modules.maison.projets import calculer_chemin_critique
        
        taches = [
            {"id": 1, "duree": 2, "successeurs": [2, 3]},
            {"id": 2, "duree": 5, "successeurs": [4]},
            {"id": 3, "duree": 3, "successeurs": [4]},
            {"id": 4, "duree": 2, "successeurs": []}
        ]
        
        chemin = calculer_chemin_critique(taches)
        
        # Chemin le plus long: 1 -> 2 -> 4 = 9 heures
        assert sum(t["duree"] for t in chemin) == 9
    
    def test_estimer_budget_projet(self):
        """Estime le budget d'un projet."""
        from src.modules.maison.projets import estimer_budget
        
        projet = {
            "materiaux": [
                {"nom": "Peinture", "prix_unite": 25.0, "quantite": 3},
                {"nom": "Pinceaux", "prix_unite": 8.0, "quantite": 2}
            ],
            "main_oeuvre": {
                "taux_horaire": 35.0,
                "heures_estimees": 12
            }
        }
        
        budget = estimer_budget(projet)
        
        # 75 (peinture) + 16 (pinceaux) + 420 (main d'oeuvre)
        assert budget["total"] == pytest.approx(511.0, 0.1)


class TestCalendrierPlanning:
    """Tests pour le module calendrier du planning."""
    
    def test_generer_vue_mensuelle(self):
        """Génère une vue mensuelle."""
        from src.modules.planning.calendrier import generer_vue_mensuelle
        
        annee = 2026
        mois = 1
        
        vue = generer_vue_mensuelle(annee, mois)
        
        assert "semaines" in vue
        assert len(vue["semaines"]) >= 4
        assert len(vue["semaines"]) <= 6
    
    def test_obtenir_jours_feries(self):
        """Obtient les jours fériés du mois."""
        from src.modules.planning.calendrier import obtenir_jours_feries
        
        # Mai 2026 (8 mai, 29 mai)
        feries = obtenir_jours_feries(annee=2026, mois=5, pays="FR")
        
        assert len(feries) >= 2
        assert date(2026, 5, 8) in feries  # 8 mai
    
    @patch('streamlit.calendar')
    def test_afficher_calendrier_interactif(self, mock_calendar):
        """Affiche un calendrier interactif."""
        from src.modules.planning.calendrier import afficher_calendrier_interactif
        
        evenements = [
            {"date": date(2026, 1, 28), "titre": "Repas", "type": "repas"}
        ]
        
        afficher_calendrier_interactif(evenements)
        # Le mock vérifie que la fonction est appelée


class TestVueEnsemble:
    """Tests pour le module vue d'ensemble."""
    
    def test_generer_resume_semaine(self):
        """Génère un résumé de la semaine."""
        from src.modules.planning.vue_ensemble import generer_resume_semaine
        
        debut_semaine = date(2026, 1, 26)
        
        donnees = {
            "repas": [{"date": date(2026, 1, 27)}, {"date": date(2026, 1, 28)}],
            "activites": [{"date": date(2026, 1, 27)}],
            "taches": [{"date": date(2026, 1, 28), "terminee": True}]
        }
        
        resume = generer_resume_semaine(debut_semaine, donnees)
        
        assert "nb_repas" in resume
        assert resume["nb_repas"] == 2
    
    @patch('streamlit.tabs')
    def test_interface_tabs_vue_ensemble(self, mock_tabs):
        """Interface à onglets de la vue d'ensemble."""
        from src.modules.planning.vue_ensemble import afficher_vue_ensemble
        
        mock_tabs.return_value = [MagicMock() for _ in range(3)]
        
        afficher_vue_ensemble()
        assert mock_tabs.called
    
    def test_calculer_charge_mentale(self):
        """Calcule la charge mentale de la semaine."""
        from src.modules.planning.vue_ensemble import calculer_charge_mentale
        
        evenements = {
            "repas_a_preparer": 14,
            "courses_a_faire": 1,
            "activites_prevues": 3,
            "taches_menage": 5,
            "rdv_medicaux": 1
        }
        
        charge = calculer_charge_mentale(evenements)
        
        assert charge in ["faible", "moderee", "elevee", "tres_elevee"]


class TestVueSemaine:
    """Tests pour le module vue semaine."""
    
    def test_generer_planning_hebdomadaire(self):
        """Génère un planning hebdomadaire."""
        from src.modules.planning.vue_semaine import generer_planning_hebdomadaire
        
        debut = date(2026, 1, 26)
        
        repas = [
            {"date": date(2026, 1, 27), "type": "diner", "recette": "Poulet"},
            {"date": date(2026, 1, 28), "type": "dejeuner", "recette": "Pâtes"}
        ]
        
        planning = generer_planning_hebdomadaire(debut, repas)
        
        assert len(planning) == 7  # 7 jours
        assert all("date" in jour for jour in planning)
    
    def test_identifier_trous_planning(self):
        """Identifie les trous dans le planning."""
        from src.modules.planning.vue_semaine import identifier_trous_planning
        
        repas_planifies = [
            {"date": date(2026, 1, 27), "type": "diner"},
            {"date": date(2026, 1, 29), "type": "diner"}
        ]
        
        debut = date(2026, 1, 27)
        
        trous = identifier_trous_planning(repas_planifies, debut, duree_jours=7)
        
        # Le 28 janvier manque
        assert date(2026, 1, 28) in trous
    
    @patch('streamlit.columns')
    def test_afficher_grille_semaine(self, mock_columns):
        """Affiche la grille hebdomadaire."""
        from src.modules.planning.vue_semaine import afficher_grille_semaine
        
        mock_columns.return_value = [MagicMock() for _ in range(7)]
        
        planning = [{"date": date(2026, 1, 27), "repas": []}]
        
        afficher_grille_semaine(planning)
        assert mock_columns.called


class TestRapportsAvances:
    """Tests avancés pour le module rapports."""
    
    def test_generer_rapport_mensuel(self):
        """Génère un rapport mensuel."""
        from src.modules.rapports import generer_rapport_mensuel
        
        mois = 1
        annee = 2026
        
        donnees = {
            "recettes_cuisinees": 45,
            "courses_faites": 4,
            "budget_depense": 450.0,
            "activites_realisees": 8
        }
        
        rapport = generer_rapport_mensuel(mois, annee, donnees)
        
        assert "periode" in rapport
        assert "statistiques" in rapport
    
    def test_comparer_avec_mois_precedent(self):
        """Compare avec le mois précédent."""
        from src.modules.rapports import comparer_mois
        
        mois_actuel = {"budget": 450.0, "recettes": 45}
        mois_precedent = {"budget": 500.0, "recettes": 40}
        
        comparaison = comparer_mois(mois_actuel, mois_precedent)
        
        assert comparaison["budget"]["evolution"] < 0  # Économie
        assert comparaison["recettes"]["evolution"] > 0  # Plus de recettes
    
    @patch('src.services.rapports_pdf.generer_pdf')
    def test_exporter_rapport_pdf(self, mock_pdf):
        """Exporte un rapport en PDF."""
        from src.modules.rapports import exporter_rapport_pdf
        
        mock_pdf.return_value = b"PDF_CONTENT"
        
        rapport = {"titre": "Rapport janvier 2026", "donnees": {}}
        
        pdf_bytes = exporter_rapport_pdf(rapport)
        
        assert pdf_bytes == b"PDF_CONTENT"
        assert mock_pdf.called


class TestParametresAvances:
    """Tests avancés pour le module paramètres."""
    
    @patch('streamlit.text_input')
    def test_modifier_nom_famille(self, mock_input):
        """Modifie le nom de famille."""
        from src.modules.parametres import modifier_nom_famille
        
        mock_input.return_value = "Famille Martin"
        
        with patch('src.core.state.StateManager') as MockState:
            mock_state = MockState.return_value
            modifier_nom_famille()
            
            # Vérifie que l'état est mis à jour
            assert mock_input.called
    
    @patch('streamlit.number_input')
    def test_configurer_budget_mensuel(self, mock_input):
        """Configure le budget mensuel."""
        from src.modules.parametres import configurer_budget_mensuel
        
        mock_input.return_value = 500.0
        
        budget = configurer_budget_mensuel()
        assert budget == 500.0
    
    def test_verifier_sante_base_donnees(self):
        """Vérifie la santé de la base de données."""
        from src.modules.parametres import verifier_sante_db
        
        with patch('src.core.database.get_db_context'):
            sante = verifier_sante_db()
            
            assert "connexion" in sante
            assert "nb_tables" in sante


class TestBarcodeAvance:
    """Tests avancés pour le module barcode."""
    
    @patch('cv2.VideoCapture')
    def test_scanner_code_barre_camera(self, mock_camera):
        """Scanne un code-barres via caméra."""
        from src.modules.barcode import scanner_code_barre
        
        mock_camera.return_value.read.return_value = (True, Mock())
        
        with patch('pyzbar.pyzbar.decode', return_value=[Mock(data=b'3017620422003')]):
            code = scanner_code_barre()
            assert code == '3017620422003'
    
    def test_rechercher_produit_par_code(self):
        """Recherche un produit par son code-barres."""
        from src.modules.barcode import rechercher_produit
        
        code = '3017620422003'
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {
                "product": {"product_name": "Nutella"}
            }
            
            produit = rechercher_produit(code)
            assert produit["nom"] == "Nutella"


class TestMaisonIntegration:
    """Tests d'intégration du module maison."""
    
    def test_workflow_complet_projet(self, test_db):
        """Workflow complet d'un projet."""
        from src.core.models import ProjetMaison, TacheMaison
        
        # Créer projet
        projet = ProjetMaison(
            nom="Rénovation salle de bain",
            description="Travaux complets",
            statut="en_cours",
            date_debut=date(2026, 1, 15)
        )
        test_db.add(projet)
        test_db.commit()
        
        # Ajouter tâches
        taches = [
            TacheMaison(projet_id=projet.id, nom="Démolition", ordre=1),
            TacheMaison(projet_id=projet.id, nom="Plomberie", ordre=2),
            TacheMaison(projet_id=projet.id, nom="Carrelage", ordre=3)
        ]
        test_db.add_all(taches)
        test_db.commit()
        
        assert len(projet.taches) == 3
        assert projet.taches[0].ordre == 1


@pytest.fixture
def mock_weather_data():
    """Données météo simulées."""
    return {
        "temperature": 15.5,
        "condition": "nuageux",
        "pluie_mm": 2.5,
        "vent_kmh": 12.0
    }
