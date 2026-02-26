"""
Tests pour src/modules/maison/utils.py

Tests des fonctions utilitaires pour les modules Projets, Jardin et Entretien.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

# ============================================================
# Fixtures - Projets
# ============================================================


@pytest.fixture
def mock_projet_en_cours():
    """Fixture pour un projet en cours"""
    projet = MagicMock()
    projet.id = 1
    projet.nom = "Renovation cuisine"
    projet.description = "Refaire la cuisine entière"
    projet.statut = "en_cours"
    projet.priorite = "haute"
    projet.date_fin_prevue = date.today() + timedelta(days=30)

    # Tasks mock
    task1 = MagicMock()
    task1.statut = "termine"
    task2 = MagicMock()
    task2.statut = "en_cours"
    projet.tasks = [task1, task2]

    return projet


@pytest.fixture
def mock_projet_en_retard():
    """Fixture pour un projet en retard"""
    projet = MagicMock()
    projet.id = 2
    projet.nom = "Peinture salon"
    projet.description = "Repeindre le salon"
    projet.statut = "en_cours"
    projet.priorite = "normale"
    projet.date_fin_prevue = date.today() - timedelta(days=5)
    projet.tasks = []
    return projet


@pytest.fixture
def mock_projet_termine():
    """Fixture pour un projet terminé"""
    projet = MagicMock()
    projet.id = 3
    projet.nom = "Installation étagères"
    projet.description = "Installer des étagères"
    projet.statut = "termine"
    projet.priorite = "basse"
    projet.date_fin_prevue = date.today() - timedelta(days=10)

    task1 = MagicMock()
    task1.statut = "termine"
    projet.tasks = [task1]

    return projet


# ============================================================
# Fixtures - Jardin
# ============================================================


@pytest.fixture
def mock_plante_a_arroser():
    """Fixture pour une plante qui a besoin d'eau"""
    plante = MagicMock()
    plante.id = 1
    plante.nom = "Tomates cerises"
    plante.type = "Légume"
    plante.location = "Potager Nord"
    plante.date_plantation = date.today() - timedelta(days=60)
    plante.date_recolte_prevue = date.today() + timedelta(days=30)
    plante.statut = "actif"
    plante.notes = "Variété Roma"
    return plante


@pytest.fixture
def mock_plante_recolte_proche():
    """Fixture pour une plante à récolter bientôt"""
    plante = MagicMock()
    plante.id = 2
    plante.nom = "Courgettes"
    plante.type = "Légume"
    plante.location = "Potager Sud"
    plante.date_plantation = date.today() - timedelta(days=90)
    plante.date_recolte_prevue = date.today() + timedelta(days=3)
    plante.statut = "actif"
    plante.notes = None
    return plante


@pytest.fixture
def mock_garden_log():
    """Fixture pour un log d'arrosage"""
    log = MagicMock()
    log.id = 1
    log.garden_item_id = 1
    log.action = "arrosage"
    log.date = date.today() - timedelta(days=3)
    return log


# ============================================================
# Fixtures - Entretien
# ============================================================


@pytest.fixture
def mock_routine_active():
    """Fixture pour une routine active"""
    routine = MagicMock()
    routine.id = 1
    routine.nom = "Ménage hebdomadaire"
    routine.categorie = "Nettoyage"
    routine.frequence = "hebdomadaire"
    routine.actif = True
    routine.description = "Grand ménage de la maison"

    task1 = MagicMock()
    task1.id = 1
    task1.nom = "Aspirateur"
    task1.routine_id = 1
    task1.fait_le = date.today()
    task1.heure_prevue = "10:00"
    task1.description = "Passer l'aspirateur partout"

    task2 = MagicMock()
    task2.id = 2
    task2.nom = "Poussière"
    task2.routine_id = 1
    task2.fait_le = None
    task2.heure_prevue = "11:00"
    task2.description = "Enlever la poussière"

    routine.tasks = [task1, task2]
    return routine


@pytest.fixture
def mock_routine_task_non_faite():
    """Fixture pour une tâche non faite"""
    task = MagicMock()
    task.id = 10
    task.nom = "Laver sols"
    task.routine_id = 1
    task.fait_le = date.today() - timedelta(days=1)  # Pas fait aujourd'hui
    task.heure_prevue = "14:00"
    task.description = "Laver tous les sols"
    return task


# ============================================================
# Tests charger_projets
# ============================================================


class TestChargerProjets:
    """Tests pour charger_projets"""

    @patch("src.modules.maison.utils._get_projets_service")
    def test_charge_tous_projets(self, mock_get_service, mock_projet_en_cours):
        """Test chargement de tous les projets sans filtre"""
        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [mock_projet_en_cours]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["nom"] == "Renovation cuisine"
        assert result.iloc[0]["progress"] == 50.0  # 1/2 tasks done
        mock_service.obtenir_projets.assert_called_once_with(statut=None)

    @patch("src.modules.maison.utils._get_projets_service")
    def test_charge_projets_avec_filtre_statut(self, mock_get_service, mock_projet_en_cours):
        """Test chargement des projets filtrés par statut"""
        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [mock_projet_en_cours]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__(statut="en_cours")

        assert len(result) == 1
        mock_service.obtenir_projets.assert_called_once_with(statut="en_cours")

    @patch("src.modules.maison.utils._get_projets_service")
    def test_projet_sans_date_fin(self, mock_get_service):
        """Test projet sans date de fin prévue"""
        projet = MagicMock()
        projet.id = 1
        projet.nom = "Projet sans deadline"
        projet.description = "Test"
        projet.statut = "en_cours"
        projet.priorite = "normale"
        projet.date_fin_prevue = None
        projet.tasks = []

        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [projet]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__()

        assert result.iloc[0]["jours_restants"] is None
        assert result.iloc[0]["progress"] == 0

    @patch("src.modules.maison.utils._get_projets_service")
    def test_projets_liste_vide(self, mock_get_service):
        """Test quand aucun projet n'existe"""
        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = []
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ============================================================
# Tests get_projets_urgents
# ============================================================


class TestGetProjetsUrgents:
    """Tests pour get_projets_urgents"""

    @patch("src.modules.maison.utils._get_projets_service")
    def test_detecte_projet_priorite_haute(self, mock_get_service, mock_projet_en_cours):
        """Test détection des projets à priorité haute"""
        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [mock_projet_en_cours]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        assert len(result) >= 1
        priorite_alert = [r for r in result if r["type"] == "PRIORITE"]
        assert len(priorite_alert) == 1
        mock_service.obtenir_projets.assert_called_once_with(statut="en_cours")

    @patch("src.modules.maison.utils._get_projets_service")
    def test_detecte_projet_en_retard(self, mock_get_service, mock_projet_en_retard):
        """Test détection des projets en retard"""
        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [mock_projet_en_retard]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        retard_alerts = [r for r in result if r["type"] == "RETARD"]
        assert len(retard_alerts) == 1
        assert "5 jour(s)" in retard_alerts[0]["message"]

    @patch("src.modules.maison.utils._get_projets_service")
    def test_projet_priorite_urgente(self, mock_get_service):
        """Test détection projet avec priorité urgente"""
        projet = MagicMock()
        projet.id = 1
        projet.nom = "Urgence"
        projet.statut = "en_cours"
        projet.priorite = "urgente"
        projet.date_fin_prevue = date.today() + timedelta(days=1)

        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [projet]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        priorite_alerts = [r for r in result if r["type"] == "PRIORITE"]
        assert len(priorite_alerts) == 1

    @patch("src.modules.maison.utils._get_projets_service")
    def test_aucun_projet_urgent(self, mock_get_service):
        """Test quand aucun projet n'est urgent"""
        projet = MagicMock()
        projet.id = 1
        projet.nom = "Normal"
        projet.statut = "en_cours"
        projet.priorite = "normale"
        projet.date_fin_prevue = date.today() + timedelta(days=30)

        mock_service = MagicMock()
        mock_service.obtenir_projets.return_value = [projet]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        assert result == []


# ============================================================
# Tests get_stats_projets
# ============================================================


class TestGetStatsProjets:
    """Tests pour get_stats_projets"""

    @patch("src.modules.maison.utils._get_projets_service")
    def test_calcule_stats_projets(
        self, mock_get_service, mock_projet_en_cours, mock_projet_termine
    ):
        """Test calcul des statistiques de projets"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_projets.return_value = {
            "total": 3,
            "en_cours": 2,
            "termines": 1,
            "avg_progress": 50.0,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_projets

        # Bypass cache with __wrapped__
        result = get_stats_projets.__wrapped__()

        assert "total" in result
        assert "en_cours" in result
        assert "termines" in result
        assert "avg_progress" in result
        mock_service.obtenir_stats_projets.assert_called_once()

    @patch("src.modules.maison.utils._get_projets_service")
    def test_stats_projets_sans_taches(self, mock_get_service):
        """Test statistiques avec projets sans tâches"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_projets.return_value = {
            "total": 1,
            "en_cours": 1,
            "termines": 0,
            "avg_progress": 0,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_projets

        # Bypass cache with __wrapped__
        result = get_stats_projets.__wrapped__()

        assert result["avg_progress"] == 0

    @patch("src.modules.maison.utils._get_projets_service")
    def test_stats_aucun_projet(self, mock_get_service):
        """Test statistiques quand aucun projet n'existe"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_projets.return_value = {
            "total": 0,
            "en_cours": 0,
            "termines": 0,
            "avg_progress": 0,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_projets

        # Bypass cache with __wrapped__
        result = get_stats_projets.__wrapped__()

        assert result["total"] == 0
        assert result["avg_progress"] == 0


# ============================================================
# Tests charger_plantes
# ============================================================


class TestChargerPlantes:
    """Tests pour charger_plantes"""

    @patch("src.modules.maison.utils._get_jardin_service")
    def test_charge_plantes_actives(self, mock_get_service, mock_plante_a_arroser, mock_garden_log):
        """Test chargement des plantes actives"""
        # Add dernier_arrosage attribute (3 days ago)
        mock_plante_a_arroser.dernier_arrosage = date.today() - timedelta(days=3)

        mock_service = MagicMock()
        mock_service.obtenir_plantes.return_value = [mock_plante_a_arroser]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_plantes

        # Bypass cache with __wrapped__
        result = charger_plantes.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["nom"] == "Tomates cerises"
        mock_service.obtenir_plantes.assert_called_once()

    @patch("src.modules.maison.utils._get_jardin_service")
    def test_plante_jamais_arrosee(self, mock_get_service, mock_plante_a_arroser):
        """Test plante qui n'a jamais été arrosée"""
        # Plant never watered
        mock_plante_a_arroser.dernier_arrosage = None

        mock_service = MagicMock()
        mock_service.obtenir_plantes.return_value = [mock_plante_a_arroser]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_plantes

        # Bypass cache with __wrapped__
        result = charger_plantes.__wrapped__()

        assert result.iloc[0]["a_arroser"] == True
        assert result.iloc[0]["jours_depuis_arrosage"] is None

    @patch("src.modules.maison.utils._get_jardin_service")
    def test_aucune_plante(self, mock_get_service):
        """Test quand le jardin est vide"""
        mock_service = MagicMock()
        mock_service.obtenir_plantes.return_value = []
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_plantes

        # Bypass cache with __wrapped__
        result = charger_plantes.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ============================================================
# Tests get_plantes_a_arroser
# ============================================================


class TestGetPlantesAArroser:
    """Tests pour get_plantes_a_arroser"""

    @patch("src.modules.maison.utils.charger_plantes")
    def test_retourne_plantes_a_arroser(self, mock_charger):
        """Test retourne les plantes qui ont besoin d'eau"""
        mock_charger.return_value = pd.DataFrame(
            [
                {"id": 1, "nom": "Tomate", "a_arroser": True},
                {"id": 2, "nom": "Carotte", "a_arroser": False},
            ]
        )

        from src.modules.maison.utils import get_plantes_a_arroser

        # Bypass cache with __wrapped__
        result = get_plantes_a_arroser.__wrapped__()

        assert len(result) == 1
        assert result[0]["nom"] == "Tomate"

    @patch("src.modules.maison.utils.charger_plantes")
    def test_liste_vide_si_toutes_arrosees(self, mock_charger):
        """Test retourne liste vide si toutes les plantes sont arrosées"""
        mock_charger.return_value = pd.DataFrame([{"id": 1, "nom": "Tomate", "a_arroser": False}])

        from src.modules.maison.utils import get_plantes_a_arroser

        # Bypass cache with __wrapped__
        result = get_plantes_a_arroser.__wrapped__()

        assert result == []

    @patch("src.modules.maison.utils.charger_plantes")
    def test_liste_vide_si_jardin_vide(self, mock_charger):
        """Test retourne liste vide si aucune plante"""
        mock_charger.return_value = pd.DataFrame()

        from src.modules.maison.utils import get_plantes_a_arroser

        # Bypass cache with __wrapped__
        result = get_plantes_a_arroser.__wrapped__()

        assert result == []


# ============================================================
# Tests get_recoltes_proches
# ============================================================


class TestGetRecoltesProches:
    """Tests pour get_recoltes_proches"""

    @patch("src.modules.maison.utils.charger_plantes")
    def test_retourne_recoltes_dans_7_jours(self, mock_charger):
        """Test retourne les récoltes dans les 7 prochains jours"""
        mock_charger.return_value = pd.DataFrame(
            [
                {"id": 1, "nom": "Courgette", "recolte": date.today() + timedelta(days=3)},
                {"id": 2, "nom": "Tomate", "recolte": date.today() + timedelta(days=20)},
            ]
        )

        from src.modules.maison.utils import get_recoltes_proches

        # Bypass cache with __wrapped__
        result = get_recoltes_proches.__wrapped__()

        assert len(result) == 1
        assert result[0]["nom"] == "Courgette"

    @patch("src.modules.maison.utils.charger_plantes")
    def test_exclut_recoltes_passees(self, mock_charger):
        """Test exclut les récoltes déjà passées"""
        mock_charger.return_value = pd.DataFrame(
            [{"id": 1, "nom": "Ancienne", "recolte": date.today() - timedelta(days=5)}]
        )

        from src.modules.maison.utils import get_recoltes_proches

        # Bypass cache with __wrapped__
        result = get_recoltes_proches.__wrapped__()

        assert result == []

    @patch("src.modules.maison.utils.charger_plantes")
    def test_plantes_sans_date_recolte(self, mock_charger):
        """Test ignore les plantes sans date de récolte"""
        mock_charger.return_value = pd.DataFrame([{"id": 1, "nom": "Plante", "recolte": None}])

        from src.modules.maison.utils import get_recoltes_proches

        # Bypass cache with __wrapped__
        result = get_recoltes_proches.__wrapped__()

        assert result == []


# ============================================================
# Tests get_stats_jardin
# ============================================================


class TestGetStatsJardin:
    """Tests pour get_stats_jardin"""

    @patch("src.modules.maison.utils._get_jardin_service")
    def test_calcule_stats_jardin(self, mock_get_service):
        """Test calcul des statistiques du jardin"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_jardin.return_value = {
            "total_plantes": 2,
            "a_arroser": 1,
            "recoltes_proches": 0,
            "categories": 2,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_jardin

        # Bypass cache with __wrapped__
        result = get_stats_jardin.__wrapped__()

        assert result["total_plantes"] == 2
        assert result["a_arroser"] == 1
        assert result["categories"] == 2
        mock_service.obtenir_stats_jardin.assert_called_once()

    @patch("src.modules.maison.utils._get_jardin_service")
    def test_stats_jardin_vide(self, mock_get_service):
        """Test statistiques quand le jardin est vide"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_jardin.return_value = {
            "total_plantes": 0,
            "a_arroser": 0,
            "recoltes_proches": 0,
            "categories": 0,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_jardin

        # Bypass cache with __wrapped__
        result = get_stats_jardin.__wrapped__()

        assert result["total_plantes"] == 0
        assert result["categories"] == 0


# ============================================================
# Tests get_saison
# ============================================================


class TestGetSaison:
    """Tests pour get_saison"""

    @patch("src.modules.maison.utils.date")
    def test_retourne_printemps(self, mock_date):
        """Test retourne Printemps pour mars-mai"""
        mock_today = MagicMock()
        mock_today.month = 4
        mock_date.today.return_value = mock_today

        from src.modules.maison.utils import get_saison

        result = get_saison()

        assert result == "Printemps"

    @patch("src.modules.maison.utils.date")
    def test_retourne_ete(self, mock_date):
        """Test retourne Été pour juin-août"""
        mock_today = MagicMock()
        mock_today.month = 7
        mock_date.today.return_value = mock_today

        from src.modules.maison.utils import get_saison

        result = get_saison()

        assert result == "Éte"

    @patch("src.modules.maison.utils.date")
    def test_retourne_automne(self, mock_date):
        """Test retourne Automne pour septembre-novembre"""
        mock_today = MagicMock()
        mock_today.month = 10
        mock_date.today.return_value = mock_today

        from src.modules.maison.utils import get_saison

        result = get_saison()

        assert result == "Automne"

    @patch("src.modules.maison.utils.date")
    def test_retourne_hiver(self, mock_date):
        """Test retourne Hiver pour décembre-février"""
        mock_today = MagicMock()
        mock_today.month = 1
        mock_date.today.return_value = mock_today

        from src.modules.maison.utils import get_saison

        result = get_saison()

        assert result == "Hiver"


# ============================================================
# Tests charger_routines
# ============================================================


class TestChargerRoutines:
    """Tests pour charger_routines"""

    @patch("src.modules.maison.utils._get_entretien_service")
    def test_charge_routines_actives(self, mock_get_service, mock_routine_active):
        """Test chargement des routines actives"""
        mock_service = MagicMock()
        mock_service.obtenir_routines.return_value = [mock_routine_active]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_routines

        # Bypass cache with __wrapped__
        result = charger_routines.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["nom"] == "Ménage hebdomadaire"
        mock_service.obtenir_routines.assert_called_once()

    @patch("src.modules.maison.utils._get_entretien_service")
    def test_routines_vides(self, mock_get_service):
        """Test quand aucune routine n'existe"""
        mock_service = MagicMock()
        mock_service.obtenir_routines.return_value = []
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import charger_routines

        # Bypass cache with __wrapped__
        result = charger_routines.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0


# ============================================================
# Tests get_taches_today
# ============================================================


class TestGetTachesToday:
    """Tests pour get_taches_today"""

    @patch("src.modules.maison.utils._get_entretien_service")
    def test_retourne_taches_non_faites(self, mock_get_service, mock_routine_task_non_faite):
        """Test retourne les tâches non faites aujourd'hui"""
        mock_service = MagicMock()
        mock_service.obtenir_taches_du_jour.return_value = [mock_routine_task_non_faite]
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_taches_today

        # Bypass cache with __wrapped__
        result = get_taches_today.__wrapped__()

        assert len(result) == 1
        assert result[0]["nom"] == "Laver sols"
        mock_service.obtenir_taches_du_jour.assert_called_once()

    @patch("src.modules.maison.utils._get_entretien_service")
    def test_aucune_tache_a_faire(self, mock_get_service):
        """Test quand toutes les tâches sont faites"""
        mock_service = MagicMock()
        mock_service.obtenir_taches_du_jour.return_value = []
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_taches_today

        # Bypass cache with __wrapped__
        result = get_taches_today.__wrapped__()

        assert result == []


# ============================================================
# Tests get_stats_entretien
# ============================================================


class TestGetStatsEntretien:
    """Tests pour get_stats_entretien"""

    @patch("src.modules.maison.utils._get_entretien_service")
    def test_calcule_stats_entretien(self, mock_get_service):
        """Test calcul des statistiques d'entretien"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_entretien.return_value = {
            "routines_actives": 5,
            "total_taches": 20,
            "taches_today": 3,
            "completion_today": 15.0,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_entretien

        # Bypass cache with __wrapped__
        result = get_stats_entretien.__wrapped__()

        assert "routines_actives" in result
        assert "total_taches" in result
        assert "taches_today" in result
        assert "completion_today" in result
        mock_service.obtenir_stats_entretien.assert_called_once()

    @patch("src.modules.maison.utils._get_entretien_service")
    def test_stats_sans_taches(self, mock_get_service):
        """Test statistiques quand aucune tâche n'existe"""
        mock_service = MagicMock()
        mock_service.obtenir_stats_entretien.return_value = {
            "routines_actives": 0,
            "total_taches": 0,
            "taches_today": 0,
            "completion_today": 0,
        }
        mock_get_service.return_value = mock_service

        from src.modules.maison.utils import get_stats_entretien

        # Bypass cache with __wrapped__
        result = get_stats_entretien.__wrapped__()

        assert result["total_taches"] == 0
        assert result["completion_today"] == 0


# ============================================================
# Tests clear_maison_cache
# ============================================================


class TestClearMaisonCache:
    """Tests pour clear_maison_cache"""

    @patch("src.modules.maison.utils.rerun")
    @patch("src.modules.maison.utils.st")
    def test_nettoie_cache_et_rerun(self, mock_st, mock_rerun):
        """Test que la fonction nettoie le cache et relance l'app"""
        mock_st.cache_data = MagicMock()

        from src.modules.maison.utils import clear_maison_cache

        clear_maison_cache()

        mock_st.cache_data.clear.assert_called_once()
        mock_rerun.assert_called_once()
