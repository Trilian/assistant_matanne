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

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_charge_tous_projets(self, mock_db, mock_projet_en_cours):
        """Test chargement de tous les projets sans filtre"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.all.return_value = [mock_projet_en_cours]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["nom"] == "Renovation cuisine"
        assert result.iloc[0]["progress"] == 50.0  # 1/2 tasks done

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_charge_projets_avec_filtre_statut(self, mock_db, mock_projet_en_cours):
        """Test chargement des projets filtrés par statut"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [mock_projet_en_cours]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__(statut="en_cours")

        assert len(result) == 1
        mock_query.filter_by.assert_called_with(statut="en_cours")

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_projet_sans_date_fin(self, mock_db):
        """Test projet sans date de fin prévue"""
        projet = MagicMock()
        projet.id = 1
        projet.nom = "Projet sans deadline"
        projet.description = "Test"
        projet.statut = "en_cours"
        projet.priorite = "normale"
        projet.date_fin_prevue = None
        projet.tasks = []

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.all.return_value = [projet]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import charger_projets

        # Bypass cache with __wrapped__
        result = charger_projets.__wrapped__()

        assert result.iloc[0]["jours_restants"] is None
        assert result.iloc[0]["progress"] == 0

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_projets_liste_vide(self, mock_db):
        """Test quand aucun projet n'existe"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

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

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_detecte_projet_priorite_haute(self, mock_db, mock_projet_en_cours):
        """Test détection des projets à priorité haute"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [mock_projet_en_cours]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        assert len(result) >= 1
        priorite_alert = [r for r in result if r["type"] == "PRIORITE"]
        assert len(priorite_alert) == 1

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_detecte_projet_en_retard(self, mock_db, mock_projet_en_retard):
        """Test détection des projets en retard"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [mock_projet_en_retard]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        retard_alerts = [r for r in result if r["type"] == "RETARD"]
        assert len(retard_alerts) == 1
        assert "5 jour(s)" in retard_alerts[0]["message"]

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_projet_priorite_urgente(self, mock_db):
        """Test détection projet avec priorité urgente"""
        projet = MagicMock()
        projet.id = 1
        projet.nom = "Urgence"
        projet.statut = "en_cours"
        projet.priorite = "urgente"
        projet.date_fin_prevue = date.today() + timedelta(days=1)

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [projet]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        priorite_alerts = [r for r in result if r["type"] == "PRIORITE"]
        assert len(priorite_alerts) == 1

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_aucun_projet_urgent(self, mock_db):
        """Test quand aucun projet n'est urgent"""
        projet = MagicMock()
        projet.id = 1
        projet.nom = "Normal"
        projet.statut = "en_cours"
        projet.priorite = "normale"
        projet.date_fin_prevue = date.today() + timedelta(days=30)

        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = [projet]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_projets_urgents

        # Bypass cache with __wrapped__
        result = get_projets_urgents.__wrapped__()

        assert result == []


# ============================================================
# Tests get_stats_projets
# ============================================================


class TestGetStatsProjets:
    """Tests pour get_stats_projets"""

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_calcule_stats_projets(self, mock_db, mock_projet_en_cours, mock_projet_termine):
        """Test calcul des statistiques de projets"""
        mock_session = MagicMock()
        mock_session.query.return_value.count.side_effect = [3, 2, 1]  # total, en_cours, termines
        mock_session.query.return_value.all.return_value = [
            mock_projet_en_cours,
            mock_projet_termine,
        ]
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_stats_projets

        # Bypass cache with __wrapped__
        result = get_stats_projets.__wrapped__()

        assert "total" in result
        assert "en_cours" in result
        assert "termines" in result
        assert "avg_progress" in result

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_stats_projets_sans_taches(self, mock_db):
        """Test statistiques avec projets sans tâches"""
        projet = MagicMock()
        projet.tasks = []

        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 1
        mock_session.query.return_value.all.return_value = [projet]
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_stats_projets

        # Bypass cache with __wrapped__
        result = get_stats_projets.__wrapped__()

        assert result["avg_progress"] == 0

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_stats_aucun_projet(self, mock_db):
        """Test statistiques quand aucun projet n'existe"""
        mock_session = MagicMock()
        mock_session.query.return_value.count.return_value = 0
        mock_session.query.return_value.all.return_value = []
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

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

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_charge_plantes_actives(self, mock_db, mock_plante_a_arroser, mock_garden_log):
        """Test chargement des plantes actives"""
        mock_session = MagicMock()
        # Query pour ElementJardin
        mock_query_items = MagicMock()
        mock_query_items.filter_by.return_value.all.return_value = [mock_plante_a_arroser]
        # Query pour JournalJardin (arrosage)
        mock_query_logs = MagicMock()
        mock_query_logs.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = [
            mock_garden_log
        ]

        def query_side_effect(model):
            if model.__name__ == "ElementJardin":
                return mock_query_items
            return mock_query_logs

        mock_session.query.side_effect = query_side_effect
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import charger_plantes

        # Bypass cache with __wrapped__
        result = charger_plantes.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["nom"] == "Tomates cerises"

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_plante_jamais_arrosee(self, mock_db, mock_plante_a_arroser):
        """Test plante qui n'a jamais été arrosée"""
        mock_session = MagicMock()
        mock_query_items = MagicMock()
        mock_query_items.filter_by.return_value.all.return_value = [mock_plante_a_arroser]
        mock_query_logs = MagicMock()
        mock_query_logs.filter_by.return_value.order_by.return_value.limit.return_value.all.return_value = []

        def query_side_effect(model):
            if model.__name__ == "ElementJardin":
                return mock_query_items
            return mock_query_logs

        mock_session.query.side_effect = query_side_effect
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import charger_plantes

        # Bypass cache with __wrapped__
        result = charger_plantes.__wrapped__()

        assert result.iloc[0]["a_arroser"] == True
        assert result.iloc[0]["jours_depuis_arrosage"] is None

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_aucune_plante(self, mock_db):
        """Test quand le jardin est vide"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

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

    @patch("src.modules.maison.utils.get_recoltes_proches")
    @patch("src.modules.maison.utils.get_plantes_a_arroser")
    @patch("src.modules.maison.utils.charger_plantes")
    def test_calcule_stats_jardin(self, mock_charger, mock_arroser, mock_recoltes):
        """Test calcul des statistiques du jardin"""
        mock_charger.return_value = pd.DataFrame(
            [
                {"id": 1, "nom": "Tomate", "type": "Légume"},
                {"id": 2, "nom": "Basilic", "type": "Aromate"},
            ]
        )
        mock_arroser.return_value = [{"id": 1, "nom": "Tomate"}]
        mock_recoltes.return_value = []

        from src.modules.maison.utils import get_stats_jardin

        # Bypass cache with __wrapped__
        result = get_stats_jardin.__wrapped__()

        assert result["total_plantes"] == 2
        assert result["a_arroser"] == 1
        assert result["categories"] == 2

    @patch("src.modules.maison.utils.get_recoltes_proches")
    @patch("src.modules.maison.utils.get_plantes_a_arroser")
    @patch("src.modules.maison.utils.charger_plantes")
    def test_stats_jardin_vide(self, mock_charger, mock_arroser, mock_recoltes):
        """Test statistiques quand le jardin est vide"""
        mock_charger.return_value = pd.DataFrame()
        mock_arroser.return_value = []
        mock_recoltes.return_value = []

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

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_charge_routines_actives(self, mock_db, mock_routine_active):
        """Test chargement des routines actives"""
        mock_session = MagicMock()
        # Query pour Routine
        mock_query_routines = MagicMock()
        mock_query_routines.filter_by.return_value.all.return_value = [mock_routine_active]
        # Query pour TacheRoutine count
        mock_query_tasks = MagicMock()
        mock_query_tasks.filter.return_value.count.return_value = 1

        def query_side_effect(model):
            if model.__name__ == "Routine":
                return mock_query_routines
            return mock_query_tasks

        mock_session.query.side_effect = query_side_effect
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import charger_routines

        # Bypass cache with __wrapped__
        result = charger_routines.__wrapped__()

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert result.iloc[0]["nom"] == "Ménage hebdomadaire"

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_routines_vides(self, mock_db):
        """Test quand aucune routine n'existe"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

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

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_retourne_taches_non_faites(self, mock_db, mock_routine_task_non_faite):
        """Test retourne les tâches non faites aujourd'hui"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = [mock_routine_task_non_faite]
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_taches_today

        # Bypass cache with __wrapped__
        result = get_taches_today.__wrapped__()

        assert len(result) == 1
        assert result[0]["nom"] == "Laver sols"

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_aucune_tache_a_faire(self, mock_db):
        """Test quand toutes les tâches sont faites"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter.return_value.all.return_value = []
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_taches_today

        # Bypass cache with __wrapped__
        result = get_taches_today.__wrapped__()

        assert result == []


# ============================================================
# Tests get_stats_entretien
# ============================================================


class TestGetStatsEntretien:
    """Tests pour get_stats_entretien"""

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_calcule_stats_entretien(self, mock_db):
        """Test calcul des statistiques d'entretien"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        # Simule les counts: routines actives, total tâches, tâches aujourd'hui
        mock_query.filter_by.return_value.count.side_effect = [5, 3]  # actives, today
        mock_query.count.return_value = 20  # total tâches
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

        from src.modules.maison.utils import get_stats_entretien

        # Bypass cache with __wrapped__
        result = get_stats_entretien.__wrapped__()

        assert "routines_actives" in result
        assert "total_taches" in result
        assert "taches_today" in result
        assert "completion_today" in result

    @patch("src.modules.maison.utils.obtenir_contexte_db")
    def test_stats_sans_taches(self, mock_db):
        """Test statistiques quand aucune tâche n'existe"""
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_query.filter_by.return_value.count.return_value = 0
        mock_query.count.return_value = 0
        mock_session.query.return_value = mock_query
        mock_db.return_value.__enter__ = MagicMock(return_value=mock_session)
        mock_db.return_value.__exit__ = MagicMock(return_value=False)

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

    @patch("src.modules.maison.utils.st")
    def test_nettoie_cache_et_rerun(self, mock_st):
        """Test que la fonction nettoie le cache et relance l'app"""
        mock_st.cache_data = MagicMock()

        from src.modules.maison.utils import clear_maison_cache

        clear_maison_cache()

        mock_st.cache_data.clear.assert_called_once()
        mock_st.rerun.assert_called_once()
