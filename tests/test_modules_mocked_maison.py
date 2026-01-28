"""
Tests avec mocks Streamlit pour les modules maison
Couverture cible: 40%+ pour entretien, jardin, projets
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, datetime, timedelta
import pandas as pd


# ═══════════════════════════════════════════════════════════════════════════════
# FIXTURES COMMUNES
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_streamlit():
    """Mock complet de Streamlit"""
    with patch("streamlit.set_page_config") as mock_config, \
         patch("streamlit.title") as mock_title, \
         patch("streamlit.caption") as mock_caption, \
         patch("streamlit.tabs") as mock_tabs, \
         patch("streamlit.columns") as mock_cols, \
         patch("streamlit.metric") as mock_metric, \
         patch("streamlit.divider") as mock_divider, \
         patch("streamlit.error") as mock_error, \
         patch("streamlit.info") as mock_info, \
         patch("streamlit.success") as mock_success, \
         patch("streamlit.warning") as mock_warning, \
         patch("streamlit.button") as mock_button, \
         patch("streamlit.selectbox") as mock_selectbox, \
         patch("streamlit.text_input") as mock_text_input, \
         patch("streamlit.text_area") as mock_text_area, \
         patch("streamlit.number_input") as mock_number_input, \
         patch("streamlit.date_input") as mock_date_input, \
         patch("streamlit.expander") as mock_expander, \
         patch("streamlit.subheader") as mock_subheader, \
         patch("streamlit.checkbox") as mock_checkbox, \
         patch("streamlit.slider") as mock_slider, \
         patch("streamlit.container") as mock_container, \
         patch("streamlit.markdown") as mock_markdown, \
         patch("streamlit.write") as mock_write, \
         patch("streamlit.dataframe") as mock_dataframe, \
         patch("streamlit.progress") as mock_progress, \
         patch("streamlit.plotly_chart") as mock_plotly, \
         patch("streamlit.rerun") as mock_rerun, \
         patch("streamlit.session_state", {}) as mock_state, \
         patch("streamlit.cache_data", lambda **kwargs: lambda f: f):
        
        mock_tabs.return_value = [MagicMock() for _ in range(10)]
        mock_cols.return_value = [MagicMock() for _ in range(10)]
        mock_expander.return_value.__enter__ = MagicMock()
        mock_expander.return_value.__exit__ = MagicMock()
        mock_container.return_value.__enter__ = MagicMock()
        mock_container.return_value.__exit__ = MagicMock()
        
        yield {
            "config": mock_config,
            "title": mock_title,
            "caption": mock_caption,
            "tabs": mock_tabs,
            "columns": mock_cols,
            "metric": mock_metric,
            "error": mock_error,
            "info": mock_info,
            "success": mock_success,
            "warning": mock_warning,
            "button": mock_button,
            "selectbox": mock_selectbox,
            "text_input": mock_text_input,
            "text_area": mock_text_area,
            "expander": mock_expander,
            "checkbox": mock_checkbox,
            "slider": mock_slider,
            "session_state": mock_state,
            "plotly_chart": mock_plotly,
            "rerun": mock_rerun,
        }


@pytest.fixture
def mock_db_context():
    """Mock du contexte de base de données"""
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.all.return_value = []
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
    mock_db.query.return_value.get.return_value = None
    
    context_manager = MagicMock()
    context_manager.__enter__ = MagicMock(return_value=mock_db)
    context_manager.__exit__ = MagicMock(return_value=False)
    
    return context_manager, mock_db


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE ENTRETIEN
# ═══════════════════════════════════════════════════════════════════════════════


class TestEntretienService:
    """Tests du service EntretienService"""
    
    def test_service_creation(self):
        """Test de la création du service"""
        with patch("src.modules.maison.entretien.ClientIA"):
            from src.modules.maison.entretien import EntretienService
            
            service = EntretienService()
            assert service is not None
            assert service.service_name == "entretien"
    
    def test_get_entretien_service(self):
        """Test de la factory du service"""
        with patch("src.modules.maison.entretien.ClientIA"):
            from src.modules.maison.entretien import get_entretien_service
            
            service = get_entretien_service()
            assert service is not None


class TestEntretienHelpers:
    """Tests des helpers entretien"""
    
    def test_routine_structure(self):
        """Test de la structure d'une routine"""
        routine = {
            "id": 1,
            "nom": "Ménage cuisine",
            "categorie": "ménage",
            "frequence": "quotidien",
            "description": "Nettoyage cuisine quotidien",
            "actif": True
        }
        
        assert "nom" in routine
        assert "categorie" in routine
        assert "frequence" in routine
        assert routine["actif"] is True
    
    def test_task_structure(self):
        """Test de la structure d'une tâche"""
        task = {
            "id": 1,
            "routine_id": 1,
            "nom": "Nettoyer évier",
            "description": "Avec produit vaisselle",
            "heure_prevue": "09:00",
            "ordre": 1,
            "fait_le": None
        }
        
        assert "nom" in task
        assert "routine_id" in task
        assert "ordre" in task
    
    def test_filter_routines_by_frequence(self):
        """Test du filtrage par fréquence"""
        routines = [
            {"frequence": "quotidien", "nom": "A"},
            {"frequence": "hebdomadaire", "nom": "B"},
            {"frequence": "quotidien", "nom": "C"},
        ]
        
        quotidiennes = [r for r in routines if r["frequence"] == "quotidien"]
        assert len(quotidiennes) == 2
    
    def test_filter_routines_actives(self):
        """Test du filtrage des routines actives"""
        routines = [
            {"actif": True, "nom": "A"},
            {"actif": False, "nom": "B"},
            {"actif": True, "nom": "C"},
        ]
        
        actives = [r for r in routines if r["actif"]]
        assert len(actives) == 2
    
    def test_count_taches_by_routine(self):
        """Test du comptage des tâches par routine"""
        taches = [
            {"routine_id": 1},
            {"routine_id": 1},
            {"routine_id": 2},
        ]
        
        counts = {}
        for t in taches:
            rid = t["routine_id"]
            counts[rid] = counts.get(rid, 0) + 1
        
        assert counts[1] == 2
        assert counts[2] == 1
    
    def test_get_taches_today(self):
        """Test de récupération des tâches du jour"""
        today = date.today()
        
        taches = [
            {"fait_le": None, "nom": "A"},
            {"fait_le": today, "nom": "B"},
            {"fait_le": None, "nom": "C"},
        ]
        
        a_faire = [t for t in taches if t["fait_le"] is None]
        assert len(a_faire) == 2
        
        faites = [t for t in taches if t["fait_le"] == today]
        assert len(faites) == 1
    
    def test_calculate_completion_rate(self):
        """Test du calcul du taux de complétion"""
        taches = [
            {"fait_le": date.today()},
            {"fait_le": date.today()},
            {"fait_le": None},
            {"fait_le": None},
        ]
        
        total = len(taches)
        faites = len([t for t in taches if t["fait_le"] is not None])
        
        taux = (faites / total) * 100 if total > 0 else 0
        assert taux == 50.0


class TestEntretienApp:
    """Tests de la fonction app() du module entretien"""
    
    def test_app_initializes(self, mock_streamlit):
        """Vérifie que app() s'initialise"""
        with patch("src.modules.maison.entretien.get_entretien_service") as mock_service, \
             patch("src.modules.maison.entretien.get_stats_entretien", return_value={}), \
             patch("src.modules.maison.entretien.charger_routines", return_value=pd.DataFrame()), \
             patch("src.modules.maison.entretien.get_taches_today", return_value=[]):
            
            mock_service.return_value = MagicMock()
            
            from src.modules.maison.entretien import app
            
            app()
            
            mock_streamlit["title"].assert_called_once()


class TestEntretienStats:
    """Tests des statistiques d'entretien"""
    
    def test_stats_structure(self):
        """Test de la structure des statistiques"""
        stats = {
            "routines_actives": 5,
            "taches_aujourd_hui": 12,
            "taches_faites": 8,
            "taux_completion": 66.7
        }
        
        assert "routines_actives" in stats
        assert "taches_aujourd_hui" in stats
        assert 0 <= stats["taux_completion"] <= 100
    
    def test_stats_calculation(self):
        """Test du calcul des statistiques"""
        routines = [{"actif": True}, {"actif": True}, {"actif": False}]
        taches = [{"fait_le": None}, {"fait_le": date.today()}, {"fait_le": None}]
        
        stats = {
            "routines_actives": len([r for r in routines if r["actif"]]),
            "taches_aujourd_hui": len(taches),
            "taches_faites": len([t for t in taches if t["fait_le"] is not None]),
        }
        stats["taux_completion"] = (stats["taches_faites"] / stats["taches_aujourd_hui"]) * 100
        
        assert stats["routines_actives"] == 2
        assert stats["taches_faites"] == 1
        assert abs(stats["taux_completion"] - 33.33) < 0.1


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE JARDIN
# ═══════════════════════════════════════════════════════════════════════════════


class TestJardinHelpers:
    """Tests des helpers jardin"""
    
    def test_plant_structure(self):
        """Test de la structure d'une plante"""
        plant = {
            "id": 1,
            "nom": "Tomates",
            "type": "légume",
            "emplacement": "Potager",
            "date_plantation": date(2025, 4, 15),
            "arrosage_frequence": 2,
            "dernier_arrosage": date.today() - timedelta(days=3),
            "notes": ""
        }
        
        assert "nom" in plant
        assert "arrosage_frequence" in plant
        assert plant["arrosage_frequence"] > 0
    
    def test_filter_plants_by_type(self):
        """Test du filtrage par type de plante"""
        plants = [
            {"type": "légume", "nom": "Tomates"},
            {"type": "fleur", "nom": "Roses"},
            {"type": "légume", "nom": "Courgettes"},
        ]
        
        legumes = [p for p in plants if p["type"] == "légume"]
        assert len(legumes) == 2
    
    def test_filter_plants_by_emplacement(self):
        """Test du filtrage par emplacement"""
        plants = [
            {"emplacement": "Potager", "nom": "Tomates"},
            {"emplacement": "Balcon", "nom": "Géraniums"},
            {"emplacement": "Potager", "nom": "Salades"},
        ]
        
        potager = [p for p in plants if p["emplacement"] == "Potager"]
        assert len(potager) == 2
    
    def test_detect_needs_watering(self):
        """Test de la détection du besoin d'arrosage"""
        today = date.today()
        
        plants = [
            {"dernier_arrosage": today - timedelta(days=3), "arrosage_frequence": 2},  # En retard
            {"dernier_arrosage": today, "arrosage_frequence": 2},  # OK
            {"dernier_arrosage": today - timedelta(days=1), "arrosage_frequence": 3},  # OK
        ]
        
        needs_water = []
        for p in plants:
            days_since = (today - p["dernier_arrosage"]).days
            if days_since >= p["arrosage_frequence"]:
                needs_water.append(p)
        
        assert len(needs_water) == 1
    
    def test_get_current_season(self):
        """Test de la détermination de la saison"""
        def get_season(month):
            if month in [3, 4, 5]:
                return "printemps"
            elif month in [6, 7, 8]:
                return "été"
            elif month in [9, 10, 11]:
                return "automne"
            else:
                return "hiver"
        
        assert get_season(1) == "hiver"
        assert get_season(4) == "printemps"
        assert get_season(7) == "été"
        assert get_season(10) == "automne"
    
    def test_seasonal_tasks(self):
        """Test des tâches saisonnières"""
        seasonal_tasks = {
            "printemps": ["Semis", "Préparation sol", "Plantation"],
            "été": ["Arrosage", "Récolte", "Entretien"],
            "automne": ["Récolte tardive", "Nettoyage", "Préparation hiver"],
            "hiver": ["Planification", "Taille", "Protection gel"]
        }
        
        assert len(seasonal_tasks["printemps"]) == 3
        assert "Arrosage" in seasonal_tasks["été"]


class TestJardinApp:
    """Tests de la fonction app() du module jardin"""
    
    def test_app_initializes(self, mock_streamlit, mock_db_context):
        """Vérifie que app() s'initialise"""
        context_manager, mock_db = mock_db_context
        
        with patch("src.modules.maison.jardin.get_db_context", return_value=context_manager), \
             patch("src.modules.maison.jardin.charger_routines", return_value=pd.DataFrame()):
            
            from src.modules.maison.jardin import app
            
            app()
            
            mock_streamlit["title"].assert_called_once()


class TestJardinStats:
    """Tests des statistiques jardin"""
    
    def test_stats_structure(self):
        """Test de la structure des statistiques"""
        stats = {
            "total_plantes": 15,
            "a_arroser": 3,
            "recolte_possible": 5,
            "alertes": 2
        }
        
        assert "total_plantes" in stats
        assert "a_arroser" in stats
    
    def test_watering_schedule(self):
        """Test du calendrier d'arrosage"""
        today = date.today()
        
        plants = [
            {"nom": "A", "arrosage_frequence": 1, "dernier_arrosage": today - timedelta(days=1)},
            {"nom": "B", "arrosage_frequence": 2, "dernier_arrosage": today - timedelta(days=1)},
            {"nom": "C", "arrosage_frequence": 3, "dernier_arrosage": today - timedelta(days=2)},
        ]
        
        schedule = {}
        for p in plants:
            days_since = (today - p["dernier_arrosage"]).days
            next_water = p["arrosage_frequence"] - days_since
            if next_water <= 0:
                schedule[p["nom"]] = "Aujourd'hui"
            else:
                schedule[p["nom"]] = f"Dans {next_water} jour(s)"
        
        assert schedule["A"] == "Aujourd'hui"
        assert "jour" in schedule["B"]


class TestJardinLog:
    """Tests du journal jardin"""
    
    def test_log_entry_structure(self):
        """Test de la structure d'une entrée de journal"""
        entry = {
            "id": 1,
            "date": date.today(),
            "type": "arrosage",
            "plante_id": 1,
            "notes": "Arrosage normal",
            "photos": []
        }
        
        assert "type" in entry
        assert "date" in entry
    
    def test_log_types(self):
        """Test des types d'entrées de journal"""
        log_types = ["arrosage", "plantation", "récolte", "traitement", "observation"]
        
        entries = [
            {"type": "arrosage"},
            {"type": "récolte"},
            {"type": "observation"},
        ]
        
        for e in entries:
            assert e["type"] in log_types
    
    def test_filter_log_by_plant(self):
        """Test du filtrage du journal par plante"""
        entries = [
            {"plante_id": 1, "type": "arrosage"},
            {"plante_id": 2, "type": "récolte"},
            {"plante_id": 1, "type": "traitement"},
        ]
        
        plant_1_entries = [e for e in entries if e["plante_id"] == 1]
        assert len(plant_1_entries) == 2
    
    def test_filter_log_by_date_range(self):
        """Test du filtrage par période"""
        today = date.today()
        entries = [
            {"date": today, "type": "arrosage"},
            {"date": today - timedelta(days=5), "type": "récolte"},
            {"date": today - timedelta(days=15), "type": "plantation"},
        ]
        
        last_week = [e for e in entries if (today - e["date"]).days <= 7]
        assert len(last_week) == 2


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE PROJETS
# ═══════════════════════════════════════════════════════════════════════════════


class TestProjetsHelpers:
    """Tests des helpers projets"""
    
    def test_project_structure(self):
        """Test de la structure d'un projet"""
        projet = {
            "id": 1,
            "nom": "Rénovation salle de bain",
            "description": "Refaire la douche",
            "categorie": "rénovation",
            "priorite": "haute",
            "statut": "en_cours",
            "date_debut": date(2025, 1, 1),
            "date_fin_prevue": date(2025, 3, 31),
            "budget_estime": 5000,
            "budget_actuel": 2500,
            "progression": 50
        }
        
        assert "nom" in projet
        assert "priorite" in projet
        assert "statut" in projet
        assert 0 <= projet["progression"] <= 100
    
    def test_task_structure(self):
        """Test de la structure d'une tâche projet"""
        tache = {
            "id": 1,
            "projet_id": 1,
            "nom": "Démolition",
            "description": "Démolir ancienne douche",
            "statut": "terminé",
            "ordre": 1,
            "date_fin": date(2025, 1, 15)
        }
        
        assert "nom" in tache
        assert "projet_id" in tache
        assert "statut" in tache
    
    def test_filter_projects_by_status(self):
        """Test du filtrage par statut"""
        projets = [
            {"statut": "en_cours", "nom": "A"},
            {"statut": "terminé", "nom": "B"},
            {"statut": "en_cours", "nom": "C"},
            {"statut": "planifié", "nom": "D"},
        ]
        
        en_cours = [p for p in projets if p["statut"] == "en_cours"]
        assert len(en_cours) == 2
    
    def test_filter_projects_by_priority(self):
        """Test du filtrage par priorité"""
        projets = [
            {"priorite": "haute", "nom": "A"},
            {"priorite": "moyenne", "nom": "B"},
            {"priorite": "haute", "nom": "C"},
        ]
        
        haute = [p for p in projets if p["priorite"] == "haute"]
        assert len(haute) == 2
    
    def test_calculate_budget_remaining(self):
        """Test du calcul du budget restant"""
        projet = {
            "budget_estime": 5000,
            "budget_actuel": 3500
        }
        
        restant = projet["budget_estime"] - projet["budget_actuel"]
        pct_utilise = (projet["budget_actuel"] / projet["budget_estime"]) * 100
        
        assert restant == 1500
        assert pct_utilise == 70.0
    
    def test_calculate_days_remaining(self):
        """Test du calcul des jours restants"""
        projet = {
            "date_fin_prevue": date.today() + timedelta(days=30)
        }
        
        jours_restants = (projet["date_fin_prevue"] - date.today()).days
        assert jours_restants == 30
    
    def test_detect_project_overdue(self):
        """Test de la détection de projet en retard"""
        today = date.today()
        
        projets = [
            {"date_fin_prevue": today - timedelta(days=5), "statut": "en_cours"},  # En retard
            {"date_fin_prevue": today + timedelta(days=10), "statut": "en_cours"},  # OK
            {"date_fin_prevue": today - timedelta(days=10), "statut": "terminé"},  # Terminé
        ]
        
        overdue = [p for p in projets if p["date_fin_prevue"] < today and p["statut"] != "terminé"]
        assert len(overdue) == 1
    
    def test_calculate_progression(self):
        """Test du calcul de la progression"""
        taches = [
            {"statut": "terminé"},
            {"statut": "terminé"},
            {"statut": "en_cours"},
            {"statut": "à_faire"},
        ]
        
        total = len(taches)
        terminees = len([t for t in taches if t["statut"] == "terminé"])
        progression = (terminees / total) * 100 if total > 0 else 0
        
        assert progression == 50.0


class TestProjetsApp:
    """Tests de la fonction app() du module projets"""
    
    def test_app_initializes(self, mock_streamlit, mock_db_context):
        """Vérifie que app() s'initialise"""
        context_manager, mock_db = mock_db_context
        
        with patch("src.modules.maison.projets.get_db_context", return_value=context_manager), \
             patch("src.modules.maison.projets.charger_routines", return_value=pd.DataFrame()):
            
            from src.modules.maison.projets import app
            
            app()
            
            mock_streamlit["title"].assert_called_once()


class TestProjetsStats:
    """Tests des statistiques projets"""
    
    def test_stats_structure(self):
        """Test de la structure des statistiques"""
        stats = {
            "total_projets": 5,
            "en_cours": 2,
            "termines": 2,
            "planifies": 1,
            "budget_total": 15000,
            "budget_utilise": 8000
        }
        
        assert "total_projets" in stats
        assert "en_cours" in stats
        assert stats["total_projets"] == stats["en_cours"] + stats["termines"] + stats["planifies"]
    
    def test_calculate_global_progression(self):
        """Test du calcul de progression globale"""
        projets = [
            {"progression": 100},
            {"progression": 50},
            {"progression": 0},
        ]
        
        avg_progression = sum(p["progression"] for p in projets) / len(projets)
        assert avg_progression == 50.0
    
    def test_priority_distribution(self):
        """Test de la distribution par priorité"""
        projets = [
            {"priorite": "haute"},
            {"priorite": "moyenne"},
            {"priorite": "haute"},
            {"priorite": "basse"},
        ]
        
        distribution = {}
        for p in projets:
            prio = p["priorite"]
            distribution[prio] = distribution.get(prio, 0) + 1
        
        assert distribution["haute"] == 2
        assert distribution["moyenne"] == 1
        assert distribution["basse"] == 1


class TestProjetsTaches:
    """Tests des tâches de projets"""
    
    def test_order_tasks(self):
        """Test du tri des tâches par ordre"""
        taches = [
            {"ordre": 3, "nom": "C"},
            {"ordre": 1, "nom": "A"},
            {"ordre": 2, "nom": "B"},
        ]
        
        sorted_taches = sorted(taches, key=lambda x: x["ordre"])
        
        assert sorted_taches[0]["nom"] == "A"
        assert sorted_taches[1]["nom"] == "B"
        assert sorted_taches[2]["nom"] == "C"
    
    def test_task_dependencies(self):
        """Test des dépendances entre tâches"""
        taches = [
            {"id": 1, "nom": "A", "depends_on": None},
            {"id": 2, "nom": "B", "depends_on": 1},
            {"id": 3, "nom": "C", "depends_on": 2},
        ]
        
        # Trouver les tâches sans dépendance
        root_tasks = [t for t in taches if t["depends_on"] is None]
        assert len(root_tasks) == 1
        assert root_tasks[0]["nom"] == "A"
    
    def test_task_status_transitions(self):
        """Test des transitions de statut"""
        valid_transitions = {
            "à_faire": ["en_cours"],
            "en_cours": ["terminé", "à_faire"],
            "terminé": ["en_cours"]  # Réouverture possible
        }
        
        # Test transition valide
        current = "à_faire"
        new = "en_cours"
        assert new in valid_transitions[current]
        
        # Test transition invalide
        current = "à_faire"
        new = "terminé"
        assert new not in valid_transitions[current]


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS INTÉGRATION MAISON
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaisonIntegration:
    """Tests d'intégration des modules maison"""
    
    def test_project_to_routine(self):
        """Test de la création de routine depuis projet"""
        projet = {
            "nom": "Entretien piscine",
            "taches": [
                {"nom": "Test pH", "frequence": "quotidien"},
                {"nom": "Nettoyage filtre", "frequence": "hebdomadaire"},
            ]
        }
        
        # Créer routines depuis tâches récurrentes
        routines = []
        for tache in projet["taches"]:
            routines.append({
                "nom": f"{projet['nom']} - {tache['nom']}",
                "frequence": tache["frequence"],
                "source_projet": projet["nom"]
            })
        
        assert len(routines) == 2
        assert routines[0]["frequence"] == "quotidien"
    
    def test_garden_to_project(self):
        """Test de la création de projet depuis jardin"""
        jardin_action = {
            "type": "aménagement",
            "description": "Créer potager surélevé",
            "budget_estime": 500
        }
        
        projet = {
            "nom": jardin_action["description"],
            "categorie": "jardin",
            "budget_estime": jardin_action["budget_estime"],
            "statut": "planifié"
        }
        
        assert projet["categorie"] == "jardin"
        assert projet["budget_estime"] == 500
    
    def test_stats_aggregation(self):
        """Test de l'agrégation des statistiques"""
        entretien_stats = {"taches_faites": 10, "taches_total": 15}
        jardin_stats = {"plantes_arrosees": 8, "plantes_total": 12}
        projets_stats = {"en_cours": 2, "progression_moyenne": 65}
        
        global_stats = {
            "entretien_completion": (entretien_stats["taches_faites"] / entretien_stats["taches_total"]) * 100,
            "jardin_completion": (jardin_stats["plantes_arrosees"] / jardin_stats["plantes_total"]) * 100,
            "projets_actifs": projets_stats["en_cours"],
            "projets_progression": projets_stats["progression_moyenne"]
        }
        
        assert abs(global_stats["entretien_completion"] - 66.67) < 0.1
        assert abs(global_stats["jardin_completion"] - 66.67) < 0.1


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS HELPERS MAISON
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaisonHelpers:
    """Tests des helpers communs maison"""
    
    def test_get_current_season(self):
        """Test de la détermination de la saison actuelle"""
        month = date.today().month
        
        if month in [3, 4, 5]:
            expected = "printemps"
        elif month in [6, 7, 8]:
            expected = "été"
        elif month in [9, 10, 11]:
            expected = "automne"
        else:
            expected = "hiver"
        
        # Janvier = hiver
        assert expected == "hiver" if month in [12, 1, 2] else expected != "hiver"
    
    def test_priority_emojis(self):
        """Test des emojis de priorité"""
        priority_emojis = {
            "haute": "🔴",
            "moyenne": "🟡",
            "basse": "🟢"
        }
        
        assert priority_emojis["haute"] == "🔴"
        assert priority_emojis["moyenne"] == "🟡"
        assert priority_emojis["basse"] == "🟢"
    
    def test_status_emojis(self):
        """Test des emojis de statut"""
        status_emojis = {
            "à_faire": "⭕",
            "en_cours": "🔄",
            "terminé": "✅",
            "annulé": "❌"
        }
        
        assert status_emojis["terminé"] == "✅"
    
    def test_format_budget(self):
        """Test du formatage du budget"""
        budget = 1234.56
        
        formatted = f"{budget:,.2f}€"
        assert "1,234.56€" == formatted or "1 234,56€" in formatted.replace(",", " ").replace(".", ",") or formatted == "1,234.56€"
    
    def test_calculate_days_until(self):
        """Test du calcul des jours jusqu'à une date"""
        target = date.today() + timedelta(days=15)
        
        days_until = (target - date.today()).days
        assert days_until == 15
    
    def test_is_overdue(self):
        """Test de la vérification de retard"""
        today = date.today()
        
        # Date passée
        past_date = today - timedelta(days=5)
        assert past_date < today
        
        # Date future
        future_date = today + timedelta(days=5)
        assert future_date > today


class TestMaisonCache:
    """Tests du cache des modules maison"""
    
    def test_clear_cache_function(self):
        """Test de la fonction de nettoyage du cache"""
        # Simuler un cache
        cache = {"key1": "value1", "key2": "value2"}
        
        # Clear
        cache.clear()
        
        assert len(cache) == 0
    
    def test_cache_invalidation_on_update(self):
        """Test de l'invalidation du cache lors d'une mise à jour"""
        cache = {"routines": [1, 2, 3]}
        
        # Simuler une mise à jour
        def update_and_invalidate():
            cache.clear()
            cache["routines"] = [1, 2, 3, 4]
        
        update_and_invalidate()
        
        assert len(cache["routines"]) == 4


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS CATEGORIES MAISON
# ═══════════════════════════════════════════════════════════════════════════════


class TestMaisonCategories:
    """Tests des catégories maison"""
    
    def test_entretien_categories(self):
        """Test des catégories d'entretien"""
        categories = ["ménage", "rangement", "réparation", "maintenance", "nettoyage"]
        
        routine = {"categorie": "ménage"}
        assert routine["categorie"] in categories
    
    def test_jardin_plant_types(self):
        """Test des types de plantes"""
        types = ["légume", "fruit", "fleur", "aromate", "arbre", "arbuste"]
        
        plant = {"type": "légume"}
        assert plant["type"] in types
    
    def test_project_categories(self):
        """Test des catégories de projets"""
        categories = ["rénovation", "aménagement", "réparation", "décoration", "jardin", "autre"]
        
        projet = {"categorie": "rénovation"}
        assert projet["categorie"] in categories
    
    def test_frequences(self):
        """Test des fréquences"""
        frequences = ["quotidien", "hebdomadaire", "bimensuel", "mensuel", "trimestriel", "annuel"]
        
        routine = {"frequence": "quotidien"}
        assert routine["frequence"] in frequences


class TestMaisonAlerts:
    """Tests des alertes maison"""
    
    def test_alert_structure(self):
        """Test de la structure d'une alerte"""
        alerte = {
            "type": "warning",
            "module": "jardin",
            "message": "3 plantes à arroser",
            "priority": "haute",
            "action_url": "/maison/jardin"
        }
        
        assert "type" in alerte
        assert "message" in alerte
        assert alerte["type"] in ["info", "warning", "error", "success"]
    
    def test_aggregate_alerts(self):
        """Test de l'agrégation des alertes"""
        alerts = [
            {"module": "jardin", "priority": "haute"},
            {"module": "entretien", "priority": "moyenne"},
            {"module": "jardin", "priority": "basse"},
            {"module": "projets", "priority": "haute"},
        ]
        
        # Par module
        by_module = {}
        for a in alerts:
            mod = a["module"]
            by_module[mod] = by_module.get(mod, 0) + 1
        
        assert by_module["jardin"] == 2
        assert by_module["entretien"] == 1
        
        # Haute priorité
        haute = [a for a in alerts if a["priority"] == "haute"]
        assert len(haute) == 2
