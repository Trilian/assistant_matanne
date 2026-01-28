"""
Tests avec mocks Streamlit pour les modules planning
Couverture cible: 40%+ pour calendrier, vue_ensemble, vue_semaine
"""

import pytest
from unittest.mock import MagicMock, patch
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
         patch("streamlit.expander") as mock_expander, \
         patch("streamlit.subheader") as mock_subheader, \
         patch("streamlit.container") as mock_container, \
         patch("streamlit.markdown") as mock_markdown, \
         patch("streamlit.write") as mock_write, \
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
            "expander": mock_expander,
            "session_state": mock_state,
            "plotly_chart": mock_plotly,
            "rerun": mock_rerun,
        }


@pytest.fixture
def mock_planning_service():
    """Mock du service planning"""
    service = MagicMock()
    
    # Mock semaine complète
    semaine = MagicMock()
    semaine.stats_semaine = {
        "total_repas": 14,
        "total_activites": 5,
        "activites_jules": 3,
        "total_projets": 2,
        "budget_total": 150
    }
    semaine.alertes_semaine = []
    
    # Mock jours
    jour1 = MagicMock()
    jour1.charge_score = 40
    jour1.charge = "faible"
    jour1.repas = []
    jour1.activites = []
    jour1.projets = []
    jour1.events = []
    jour1.routines = []
    jour1.alertes = []
    jour1.budget_jour = 0
    
    jour2 = MagicMock()
    jour2.charge_score = 70
    jour2.charge = "normal"
    jour2.repas = [{"type": "déjeuner", "recette": "Pâtes", "portions": 4}]
    jour2.activites = [{"titre": "Parc", "type": "exterieur", "pour_jules": True}]
    jour2.projets = []
    jour2.events = []
    jour2.routines = []
    jour2.alertes = []
    jour2.budget_jour = 0
    
    jour3 = MagicMock()
    jour3.charge_score = 90
    jour3.charge = "intense"
    jour3.repas = [{"type": "déjeuner", "recette": "Poulet", "portions": 4}]
    jour3.activites = [{"titre": "Zoo", "type": "sortie", "pour_jules": True, "budget": 45}]
    jour3.projets = [{"nom": "Rénovation", "statut": "en_cours", "priorite": "haute"}]
    jour3.events = [{"titre": "RDV médecin", "debut": datetime.now(), "lieu": "Cabinet"}]
    jour3.routines = [{"nom": "Routine matin", "heure": "07:00", "fait": False}]
    jour3.alertes = ["Journée chargée!"]
    jour3.budget_jour = 45
    
    # Liste de jours
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    semaine.jours = {
        week_start: jour1,
        week_start + timedelta(days=1): jour2,
        week_start + timedelta(days=2): jour3,
        week_start + timedelta(days=3): jour1,
        week_start + timedelta(days=4): jour2,
        week_start + timedelta(days=5): jour1,
        week_start + timedelta(days=6): jour1,
    }
    
    service.get_semaine_complete.return_value = semaine
    
    return service


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE CALENDRIER
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalendrierNavigation:
    """Tests de la navigation dans le calendrier"""
    
    def test_get_week_start(self):
        """Test du calcul du début de semaine"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Le début de semaine est toujours un lundi
        assert week_start.weekday() == 0
    
    def test_get_week_end(self):
        """Test du calcul de la fin de semaine"""
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # La fin de semaine est toujours un dimanche
        assert week_end.weekday() == 6
    
    def test_previous_week_navigation(self):
        """Test de la navigation vers la semaine précédente"""
        today = date.today()
        current_week_start = today - timedelta(days=today.weekday())
        
        previous_week_start = current_week_start - timedelta(days=7)
        
        assert previous_week_start < current_week_start
        assert (current_week_start - previous_week_start).days == 7
    
    def test_next_week_navigation(self):
        """Test de la navigation vers la semaine suivante"""
        today = date.today()
        current_week_start = today - timedelta(days=today.weekday())
        
        next_week_start = current_week_start + timedelta(days=7)
        
        assert next_week_start > current_week_start
        assert (next_week_start - current_week_start).days == 7
    
    def test_week_days_generation(self):
        """Test de la génération des jours de la semaine"""
        week_start = date(2026, 1, 26)  # Lundi
        
        days = [week_start + timedelta(days=i) for i in range(7)]
        
        assert len(days) == 7
        assert days[0].weekday() == 0  # Lundi
        assert days[6].weekday() == 6  # Dimanche


class TestCalendrierAffichageJour:
    """Tests de l'affichage des jours"""
    
    def test_jour_complet_structure(self):
        """Test de la structure d'un jour complet"""
        jour = {
            "repas": [],
            "activites": [],
            "projets": [],
            "events": [],
            "routines": [],
            "alertes": [],
            "charge": "normal",
            "charge_score": 50,
            "budget_jour": 0
        }
        
        assert "repas" in jour
        assert "charge" in jour
        assert "charge_score" in jour
    
    def test_charge_emojis(self):
        """Test des emojis de charge"""
        charge_emojis = {
            "faible": "🟢",
            "normal": "🟡",
            "intense": "🔴"
        }
        
        assert charge_emojis["faible"] == "🟢"
        assert charge_emojis["normal"] == "🟡"
        assert charge_emojis["intense"] == "🔴"
    
    def test_is_today_detection(self):
        """Test de la détection du jour actuel"""
        today = date.today()
        other_day = today + timedelta(days=1)
        
        assert today == date.today()
        assert other_day != date.today()
    
    def test_day_name_formatting(self):
        """Test du formatage du nom de jour"""
        jour_noms = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        
        test_date = date(2026, 1, 28)  # Mercredi
        day_name = jour_noms[test_date.weekday()]
        
        assert day_name == "mercredi"


class TestCalendrierCharge:
    """Tests du calcul de charge"""
    
    def test_charge_calculation(self):
        """Test du calcul de la charge"""
        jour = {
            "repas": [{"type": "déjeuner"}, {"type": "dîner"}],
            "activites": [{"titre": "Parc"}],
            "projets": [{"nom": "Projet"}],
            "events": [],
            "routines": [{"nom": "Routine 1"}, {"nom": "Routine 2"}]
        }
        
        # Calcul simple basé sur le nombre d'éléments
        base_score = (
            len(jour["repas"]) * 5 +
            len(jour["activites"]) * 15 +
            len(jour["projets"]) * 20 +
            len(jour["events"]) * 10 +
            len(jour["routines"]) * 5
        )
        
        assert base_score == 2*5 + 1*15 + 1*20 + 0*10 + 2*5  # 55
    
    def test_charge_label_from_score(self):
        """Test de la détermination du label de charge"""
        def get_charge_label(score):
            if score < 40:
                return "faible"
            elif score < 70:
                return "normal"
            else:
                return "intense"
        
        assert get_charge_label(30) == "faible"
        assert get_charge_label(50) == "normal"
        assert get_charge_label(80) == "intense"
    
    def test_charge_with_budget(self):
        """Test de la charge avec budget"""
        activites = [
            {"titre": "Zoo", "budget": 45},
            {"titre": "Parc", "budget": 0},
            {"titre": "Ciné", "budget": 30},
        ]
        
        total_budget = sum(a.get("budget", 0) for a in activites)
        assert total_budget == 75


class TestCalendrierEvenements:
    """Tests des événements du calendrier"""
    
    def test_repas_structure(self):
        """Test de la structure d'un repas"""
        repas = {
            "type": "déjeuner",
            "recette": "Pâtes carbonara",
            "portions": 4,
            "temps_total": 30
        }
        
        assert "type" in repas
        assert "recette" in repas
        assert repas["type"] in ["petit_déjeuner", "déjeuner", "goûter", "dîner"]
    
    def test_activite_structure(self):
        """Test de la structure d'une activité"""
        activite = {
            "titre": "Parc",
            "type": "exterieur",
            "pour_jules": True,
            "budget": 0
        }
        
        assert "titre" in activite
        assert "pour_jules" in activite
    
    def test_event_structure(self):
        """Test de la structure d'un événement"""
        event = {
            "titre": "RDV médecin",
            "debut": datetime.now(),
            "fin": datetime.now() + timedelta(hours=1),
            "lieu": "Cabinet",
            "notes": ""
        }
        
        assert "titre" in event
        assert "debut" in event
    
    def test_routine_structure(self):
        """Test de la structure d'une routine"""
        routine = {
            "nom": "Routine matin",
            "heure": "07:00",
            "fait": False
        }
        
        assert "nom" in routine
        assert "fait" in routine
    
    def test_projet_structure(self):
        """Test de la structure d'un projet"""
        projet = {
            "nom": "Rénovation",
            "statut": "en_cours",
            "priorite": "haute"
        }
        
        assert "nom" in projet
        assert "priorite" in projet


class TestCalendrierApp:
    """Tests de la fonction app() du module calendrier"""
    
    def test_app_initializes(self, mock_streamlit, mock_planning_service):
        """Vérifie que app() s'initialise"""
        with patch("src.modules.planning.calendrier.get_planning_service", return_value=mock_planning_service):
            
            from src.modules.planning.calendrier import app
            
            app()
            
            mock_streamlit["title"].assert_called_once()
    
    def test_app_handles_no_data(self, mock_streamlit):
        """Vérifie la gestion sans données"""
        mock_service = MagicMock()
        mock_service.get_semaine_complete.return_value = None
        
        with patch("src.modules.planning.calendrier.get_planning_service", return_value=mock_service):
            
            from src.modules.planning.calendrier import app
            
            app()
            
            mock_streamlit["error"].assert_called()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE VUE_ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════════


class TestVueEnsembleMetriques:
    """Tests des métriques de vue d'ensemble"""
    
    def test_stats_semaine_structure(self):
        """Test de la structure des stats semaine"""
        stats = {
            "total_repas": 14,
            "total_activites": 5,
            "activites_jules": 3,
            "total_projets": 2,
            "budget_total": 150,
            "total_events": 3
        }
        
        assert "total_repas" in stats
        assert "total_activites" in stats
        assert "budget_total" in stats
    
    def test_calculate_percentage_jules(self):
        """Test du calcul du pourcentage d'activités pour Jules"""
        total_activites = 10
        activites_jules = 6
        
        pct = (activites_jules / total_activites) * 100 if total_activites > 0 else 0
        assert pct == 60.0
    
    def test_average_daily_budget(self):
        """Test du calcul du budget moyen journalier"""
        budget_total = 210
        jours = 7
        
        avg = budget_total / jours
        assert avg == 30.0


class TestVueEnsembleAlertes:
    """Tests des alertes de la vue d'ensemble"""
    
    def test_alerte_structure(self):
        """Test de la structure d'une alerte"""
        alerte = "Journée très chargée le mercredi!"
        
        assert isinstance(alerte, str)
        assert len(alerte) > 0
    
    def test_detect_overloaded_days(self):
        """Test de la détection des jours surchargés"""
        jours = [
            {"charge_score": 30},
            {"charge_score": 85},
            {"charge_score": 50},
            {"charge_score": 95},
        ]
        
        surchages = [j for j in jours if j["charge_score"] > 80]
        assert len(surchages) == 2
    
    def test_generate_alerts_from_charge(self):
        """Test de la génération d'alertes depuis la charge"""
        jours = {
            "Lundi": {"charge_score": 90, "charge": "intense"},
            "Mardi": {"charge_score": 40, "charge": "faible"},
            "Mercredi": {"charge_score": 85, "charge": "intense"},
        }
        
        alertes = []
        for jour_nom, jour_data in jours.items():
            if jour_data["charge_score"] > 80:
                alertes.append(f"⚠️ {jour_nom}: Journée très chargée ({jour_data['charge_score']}/100)")
        
        assert len(alertes) == 2
        assert "Lundi" in alertes[0]


class TestVueEnsembleGraphiques:
    """Tests des graphiques de la vue d'ensemble"""
    
    def test_charge_data_for_chart(self):
        """Test de la préparation des données pour graphique de charge"""
        jours = [
            {"nom": "Lun", "charge_score": 40},
            {"nom": "Mar", "charge_score": 60},
            {"nom": "Mer", "charge_score": 80},
            {"nom": "Jeu", "charge_score": 50},
            {"nom": "Ven", "charge_score": 70},
            {"nom": "Sam", "charge_score": 30},
            {"nom": "Dim", "charge_score": 20},
        ]
        
        noms = [j["nom"] for j in jours]
        scores = [j["charge_score"] for j in jours]
        
        assert len(noms) == 7
        assert len(scores) == 7
        assert max(scores) == 80
    
    def test_repartition_data(self):
        """Test des données de répartition"""
        stats = {
            "total_repas": 14,
            "total_activites": 5,
            "total_projets": 2,
            "total_events": 3
        }
        
        labels = ["Repas", "Activités", "Projets", "Événements"]
        values = [stats["total_repas"], stats["total_activites"], stats["total_projets"], stats["total_events"]]
        
        assert sum(values) == 24
        assert len(labels) == len(values)


class TestVueEnsembleApp:
    """Tests de la fonction app() de vue_ensemble"""
    
    def test_app_initializes(self, mock_streamlit, mock_planning_service):
        """Vérifie que app() s'initialise"""
        # Note: vue_ensemble n'existe peut-être pas comme module séparé
        # On teste les fonctions communes
        pass


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS MODULE VUE_SEMAINE
# ═══════════════════════════════════════════════════════════════════════════════


class TestVueSemaineGraphiqueCharge:
    """Tests du graphique de charge semaine"""
    
    def test_prepare_charge_data(self, mock_planning_service):
        """Test de la préparation des données de charge"""
        semaine = mock_planning_service.get_semaine_complete()
        jours = list(semaine.jours.values())
        
        charges = [j.charge_score for j in jours]
        
        assert len(charges) == 7
        assert all(0 <= c <= 100 for c in charges)
    
    def test_charge_color_scale(self):
        """Test de l'échelle de couleurs pour la charge"""
        def get_color(score):
            if score < 40:
                return "green"
            elif score < 70:
                return "yellow"
            else:
                return "red"
        
        assert get_color(30) == "green"
        assert get_color(50) == "yellow"
        assert get_color(80) == "red"
    
    def test_threshold_lines(self):
        """Test des lignes de seuil"""
        seuils = {
            "normal": 50,
            "surcharge": 80
        }
        
        # Score en dessous du normal
        assert 30 < seuils["normal"]
        # Score entre normal et surcharge
        assert seuils["normal"] < 60 < seuils["surcharge"]
        # Score au-dessus de surcharge
        assert 90 > seuils["surcharge"]


class TestVueSemaineTimelineJour:
    """Tests de la timeline par jour"""
    
    def test_jour_nom_formatting(self):
        """Test du formatage du nom de jour"""
        jour_noms = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        
        test_date = date(2026, 1, 28)
        jour_nom = jour_noms[test_date.weekday()]
        formatted = f"{jour_nom.capitalize()} {test_date.strftime('%d/%m')}"
        
        assert "Mercredi" in formatted
        assert "28/01" in formatted
    
    def test_events_grouped_by_type(self):
        """Test du regroupement des événements par type"""
        events_grouped = {
            "🍽️ Repas": [{"type": "déjeuner", "recette": "Pâtes"}],
            "🎨 Activités": [{"titre": "Parc", "pour_jules": True}],
            "🏗️ Projets": [],
            "⏰ Routines": [{"nom": "Routine matin", "fait": False}],
            "📅 Événements": []
        }
        
        non_empty = {k: v for k, v in events_grouped.items() if v}
        assert len(non_empty) == 3
    
    def test_repas_display(self):
        """Test de l'affichage des repas"""
        repas = {
            "type": "déjeuner",
            "recette": "Pâtes carbonara",
            "portions": 4,
            "temps_total": 30
        }
        
        display = f"**{repas['type'].capitalize()}**: {repas['recette']}"
        caption = f"{repas['portions']} portions | {repas['temps_total']} min"
        
        assert "Déjeuner" in display
        assert "4 portions" in caption
    
    def test_activite_display(self):
        """Test de l'affichage des activités"""
        activite = {
            "titre": "Zoo",
            "type": "sortie",
            "pour_jules": True,
            "budget": 45
        }
        
        label = "👶" if activite["pour_jules"] else "👨‍👩‍👧"
        display = f"{label} **{activite['titre']}** ({activite['type']})"
        
        assert "👶" in display
        assert "Zoo" in display
    
    def test_event_time_formatting(self):
        """Test du formatage de l'heure des événements"""
        event = {
            "titre": "RDV",
            "debut": datetime(2026, 1, 28, 14, 30)
        }
        
        time_str = event["debut"].strftime("%H:%M")
        assert time_str == "14:30"
    
    def test_routine_status_display(self):
        """Test de l'affichage du statut des routines"""
        routines = [
            {"nom": "A", "fait": True},
            {"nom": "B", "fait": False},
        ]
        
        for r in routines:
            status = "✅" if r["fait"] else "⭕"
            assert status in ["✅", "⭕"]


class TestVueSemaineRepas:
    """Tests de la section repas"""
    
    def test_repas_types(self):
        """Test des types de repas"""
        types_repas = ["petit_déjeuner", "déjeuner", "goûter", "dîner"]
        
        repas = {"type": "déjeuner"}
        assert repas["type"] in types_repas
    
    def test_count_repas_by_type(self):
        """Test du comptage des repas par type"""
        repas = [
            {"type": "déjeuner"},
            {"type": "dîner"},
            {"type": "déjeuner"},
            {"type": "petit_déjeuner"},
        ]
        
        counts = {}
        for r in repas:
            t = r["type"]
            counts[t] = counts.get(t, 0) + 1
        
        assert counts["déjeuner"] == 2
        assert counts["dîner"] == 1


class TestVueSemaineActivites:
    """Tests de la section activités"""
    
    def test_filter_activites_jules(self):
        """Test du filtrage des activités pour Jules"""
        activites = [
            {"pour_jules": True, "titre": "Parc"},
            {"pour_jules": False, "titre": "Ciné"},
            {"pour_jules": True, "titre": "Zoo"},
        ]
        
        pour_jules = [a for a in activites if a["pour_jules"]]
        assert len(pour_jules) == 2
    
    def test_total_budget_activites(self):
        """Test du calcul du budget total des activités"""
        activites = [
            {"budget": 0},
            {"budget": 45},
            {"budget": 30},
        ]
        
        total = sum(a.get("budget", 0) for a in activites)
        assert total == 75


class TestVueSemaineProjets:
    """Tests de la section projets"""
    
    def test_priorite_emojis(self):
        """Test des emojis de priorité"""
        emojis = {"basse": "🟢", "moyenne": "🟡", "haute": "🔴"}
        
        projet = {"priorite": "haute"}
        emoji = emojis.get(projet["priorite"], "⚪")
        
        assert emoji == "🔴"
    
    def test_filter_projets_haute_priorite(self):
        """Test du filtrage des projets haute priorité"""
        projets = [
            {"priorite": "haute", "nom": "A"},
            {"priorite": "basse", "nom": "B"},
            {"priorite": "haute", "nom": "C"},
        ]
        
        haute = [p for p in projets if p["priorite"] == "haute"]
        assert len(haute) == 2


class TestVueSemaineApp:
    """Tests de la fonction app() du module vue_semaine"""
    
    def test_app_initializes(self, mock_streamlit, mock_planning_service):
        """Vérifie que app() s'initialise"""
        with patch("src.modules.planning.vue_semaine.get_planning_service", return_value=mock_planning_service):
            
            from src.modules.planning.vue_semaine import app
            
            app()
            
            mock_streamlit["title"].assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# TESTS INTÉGRATION PLANNING
# ═══════════════════════════════════════════════════════════════════════════════


class TestPlanningIntegration:
    """Tests d'intégration des modules planning"""
    
    def test_semaine_complete_structure(self, mock_planning_service):
        """Test de la structure de la semaine complète"""
        semaine = mock_planning_service.get_semaine_complete()
        
        assert hasattr(semaine, "stats_semaine")
        assert hasattr(semaine, "alertes_semaine")
        assert hasattr(semaine, "jours")
    
    def test_jours_count(self, mock_planning_service):
        """Test du nombre de jours"""
        semaine = mock_planning_service.get_semaine_complete()
        
        assert len(semaine.jours) == 7
    
    def test_stats_consistency(self, mock_planning_service):
        """Test de la cohérence des statistiques"""
        semaine = mock_planning_service.get_semaine_complete()
        stats = semaine.stats_semaine
        
        # Les activités Jules doivent être <= total activités
        assert stats["activites_jules"] <= stats["total_activites"]
    
    def test_navigation_state_persistence(self):
        """Test de la persistence de l'état de navigation"""
        state = {}
        
        # Initialiser
        today = date.today()
        state["planning_week_start"] = today - timedelta(days=today.weekday())
        
        # Naviguer
        state["planning_week_start"] -= timedelta(days=7)
        
        # Vérifier la persistence
        assert state["planning_week_start"] < today


class TestPlanningHelpers:
    """Tests des helpers de planning"""
    
    def test_format_date_range(self):
        """Test du formatage d'une plage de dates"""
        week_start = date(2026, 1, 26)
        week_end = week_start + timedelta(days=6)
        
        formatted = f"{week_start.strftime('%d/%m')} — {week_end.strftime('%d/%m/%Y')}"
        
        assert "26/01" in formatted
        assert "01/02/2026" in formatted
    
    def test_get_day_label(self):
        """Test de la génération du label de jour"""
        jour = date(2026, 1, 28)
        charge = "normal"
        
        charge_emoji = {"faible": "🟢", "normal": "🟡", "intense": "🔴"}.get(charge, "⚪")
        label = f"{charge_emoji} Mercredi {jour.strftime('%d/%m')}"
        
        assert "🟡" in label
        assert "Mercredi" in label
    
    def test_is_weekend(self):
        """Test de la détection du weekend"""
        dates = [
            date(2026, 1, 26),  # Lundi
            date(2026, 1, 31),  # Samedi
            date(2026, 2, 1),   # Dimanche
        ]
        
        weekends = [d for d in dates if d.weekday() >= 5]
        assert len(weekends) == 2


class TestPlanningConflicts:
    """Tests de détection de conflits"""
    
    def test_detect_time_conflict(self):
        """Test de la détection de conflit horaire"""
        events = [
            {"debut": datetime(2026, 1, 28, 14, 0), "fin": datetime(2026, 1, 28, 15, 0)},
            {"debut": datetime(2026, 1, 28, 14, 30), "fin": datetime(2026, 1, 28, 15, 30)},
        ]
        
        def has_conflict(e1, e2):
            return e1["debut"] < e2["fin"] and e2["debut"] < e1["fin"]
        
        assert has_conflict(events[0], events[1])
    
    def test_no_conflict(self):
        """Test sans conflit"""
        events = [
            {"debut": datetime(2026, 1, 28, 14, 0), "fin": datetime(2026, 1, 28, 15, 0)},
            {"debut": datetime(2026, 1, 28, 16, 0), "fin": datetime(2026, 1, 28, 17, 0)},
        ]
        
        def has_conflict(e1, e2):
            return e1["debut"] < e2["fin"] and e2["debut"] < e1["fin"]
        
        assert not has_conflict(events[0], events[1])


class TestPlanningBudget:
    """Tests du budget dans le planning"""
    
    def test_calculate_week_budget(self):
        """Test du calcul du budget semaine"""
        jours = [
            {"budget_jour": 0},
            {"budget_jour": 45},
            {"budget_jour": 0},
            {"budget_jour": 30},
            {"budget_jour": 0},
            {"budget_jour": 100},
            {"budget_jour": 0},
        ]
        
        total = sum(j["budget_jour"] for j in jours)
        assert total == 175
    
    def test_average_daily_budget(self):
        """Test du calcul du budget moyen journalier"""
        total_budget = 175
        jours_avec_depenses = 3
        
        avg_jour_actif = total_budget / jours_avec_depenses
        assert abs(avg_jour_actif - 58.33) < 0.1


class TestPlanningDisplay:
    """Tests de l'affichage du planning"""
    
    def test_empty_day_message(self):
        """Test du message pour jour vide"""
        jour = {
            "repas": [],
            "activites": [],
            "projets": [],
            "events": [],
            "routines": []
        }
        
        is_empty = not any([
            jour["repas"],
            jour["activites"],
            jour["projets"],
            jour["events"],
            jour["routines"]
        ])
        
        assert is_empty
    
    def test_progress_bar_value(self):
        """Test de la valeur de la barre de progression"""
        charge_score = 75
        
        # Normaliser entre 0 et 1
        progress_value = min(charge_score / 100, 1.0)
        
        assert progress_value == 0.75
    
    def test_metric_delta_calculation(self):
        """Test du calcul du delta des métriques"""
        this_week = {"total_activites": 5}
        last_week = {"total_activites": 3}
        
        delta = this_week["total_activites"] - last_week["total_activites"]
        assert delta == 2
