"""
Tests pour src/modules/cuisine/logic/planning_logic.py
"""

from datetime import date, timedelta
from unittest.mock import Mock


class TestGetDebutSemaine:
    """Tests pour get_debut_semaine."""

    def test_debut_semaine_lundi(self):
        """Lundi retourne lui-même."""
        from src.modules.cuisine.planning_utils import get_debut_semaine

        # 2025-02-03 est un lundi
        lundi = date(2025, 2, 3)
        result = get_debut_semaine(lundi)
        assert result == lundi
        assert result.weekday() == 0  # Lundi

    def test_debut_semaine_mercredi(self):
        """Mercredi retourne le lundi précédent."""
        from src.modules.cuisine.planning_utils import get_debut_semaine

        mercredi = date(2025, 2, 5)  # Mercredi
        result = get_debut_semaine(mercredi)
        assert result == date(2025, 2, 3)  # Lundi

    def test_debut_semaine_dimanche(self):
        """Dimanche retourne le lundi précédent."""
        from src.modules.cuisine.planning_utils import get_debut_semaine

        dimanche = date(2025, 2, 9)  # Dimanche
        result = get_debut_semaine(dimanche)
        assert result == date(2025, 2, 3)  # Lundi


class TestGetFinSemaine:
    """Tests pour get_fin_semaine."""

    def test_fin_semaine_dimanche(self):
        """Dimanche retourne lui-même."""
        from src.modules.cuisine.planning_utils import get_fin_semaine

        dimanche = date(2025, 2, 9)
        result = get_fin_semaine(dimanche)
        assert result == dimanche
        assert result.weekday() == 6  # Dimanche

    def test_fin_semaine_lundi(self):
        """Lundi retourne le dimanche suivant."""
        from src.modules.cuisine.planning_utils import get_fin_semaine

        lundi = date(2025, 2, 3)
        result = get_fin_semaine(lundi)
        assert result == date(2025, 2, 9)  # Dimanche


class TestGetDatesSemaine:
    """Tests pour get_dates_semaine."""

    def test_dates_semaine_longueur(self):
        """Retourne 7 dates."""
        from src.modules.cuisine.planning_utils import get_dates_semaine

        result = get_dates_semaine(date(2025, 2, 5))
        assert len(result) == 7

    def test_dates_semaine_ordre(self):
        """Dates du lundi au dimanche."""
        from src.modules.cuisine.planning_utils import get_dates_semaine

        result = get_dates_semaine(date(2025, 2, 5))
        assert result[0].weekday() == 0  # Lundi
        assert result[6].weekday() == 6  # Dimanche

    def test_dates_semaine_consecutives(self):
        """Dates consécutives."""
        from src.modules.cuisine.planning_utils import get_dates_semaine

        result = get_dates_semaine(date(2025, 2, 5))
        for i in range(6):
            assert result[i + 1] - result[i] == timedelta(days=1)


class TestGetNumeroSemaine:
    """Tests pour get_numero_semaine."""

    def test_numero_semaine_janvier(self):
        """Semaine 1 de janvier."""
        from src.modules.cuisine.planning_utils import get_numero_semaine

        result = get_numero_semaine(date(2025, 1, 6))
        assert result >= 1 and result <= 53


class TestOrganiserRepasParJour:
    """Tests pour organiser_repas_par_jour."""

    def test_organiser_par_jour_simple(self):
        """Organisation simple par jour."""
        from src.modules.cuisine.planning_utils import organiser_repas_par_jour

        repas1 = Mock()
        repas1.jour = "Lundi"
        repas2 = Mock()
        repas2.jour = "Lundi"
        repas3 = Mock()
        repas3.jour = "Mardi"

        result = organiser_repas_par_jour([repas1, repas2, repas3])

        assert len(result["Lundi"]) == 2
        assert len(result["Mardi"]) == 1

    def test_organiser_par_jour_vide(self):
        """Liste vide."""
        from src.modules.cuisine.planning_utils import organiser_repas_par_jour

        result = organiser_repas_par_jour([])
        assert result == {}


class TestOrganiserRepasParType:
    """Tests pour organiser_repas_par_type."""

    def test_organiser_par_type_simple(self):
        """Organisation par type de repas."""
        from src.modules.cuisine.planning_utils import organiser_repas_par_type

        repas1 = Mock()
        repas1.type_repas = "déjeuner"
        repas2 = Mock()
        repas2.type_repas = "dîner"
        repas3 = Mock()
        repas3.type_repas = "déjeuner"

        result = organiser_repas_par_type([repas1, repas2, repas3])

        assert len(result["déjeuner"]) == 2
        assert len(result["dîner"]) == 1


class TestCalculerStatistiquesPlanning:
    """Tests pour calculer_statistiques_planning."""

    def test_statistiques_planning_vide(self):
        """Planning sans repas."""
        from src.modules.cuisine.planning_utils import calculer_statistiques_planning

        result = calculer_statistiques_planning(None)

        assert result["total_repas"] == 0
        assert result["taux_completion"] == 0.0

    def test_statistiques_planning_complet(self):
        """Planning avec repas."""
        from src.modules.cuisine.planning_utils import calculer_statistiques_planning

        repas1 = Mock()
        repas1.jour = "Lundi"
        repas1.type_repas = "déjeuner"
        repas2 = Mock()
        repas2.jour = "Lundi"
        repas2.type_repas = "dîner"

        planning = Mock()
        planning.repas = [repas1, repas2]

        result = calculer_statistiques_planning(planning)

        assert result["total_repas"] == 2
        assert result["jours_complets"] == 1


class TestValiderRepas:
    """Tests pour valider_repas."""

    def test_valider_repas_valide(self):
        """Repas valide."""
        from src.modules.cuisine.planning_utils import valider_repas

        data = {"jour": "Lundi", "type_repas": "déjeuner", "recette_id": 1}
        valid, error = valider_repas(data)
        assert valid is True
        assert error is None

    def test_valider_repas_sans_jour(self):
        """Repas sans jour = invalide."""
        from src.modules.cuisine.planning_utils import valider_repas

        data = {"type_repas": "déjeuner", "recette_id": 1}
        valid, error = valider_repas(data)
        assert valid is False
        assert "jour" in error.lower()

    def test_valider_repas_type_invalide(self):
        """Type de repas invalide."""
        from src.modules.cuisine.planning_utils import valider_repas

        data = {
            "jour": "Lundi",
            "type_repas": "goûter",  # Pas dans TYPES_REPAS
            "recette_id": 1,
        }
        valid, error = valider_repas(data)
        assert valid is False
        assert "type" in error.lower()

    def test_valider_repas_sans_recette(self):
        """Repas sans recette = invalide."""
        from src.modules.cuisine.planning_utils import valider_repas

        data = {"jour": "Lundi", "type_repas": "déjeuner"}
        valid, error = valider_repas(data)
        assert valid is False
        assert "recette" in error.lower()


class TestValiderPlanning:
    """Tests pour valider_planning."""

    def test_valider_planning_valide(self):
        """Planning valide."""
        from src.modules.cuisine.planning_utils import valider_planning

        data = {
            "semaine_debut": date(2025, 2, 3),
            "repas": [{"jour": "Lundi", "type_repas": "déjeuner", "recette_id": 1}],
        }
        valid, errors = valider_planning(data)
        assert valid is True
        assert errors == []

    def test_valider_planning_sans_date(self):
        """Planning sans date = invalide."""
        from src.modules.cuisine.planning_utils import valider_planning

        data = {"repas": []}
        valid, errors = valider_planning(data)
        assert valid is False
        assert len(errors) > 0


class TestCalculerCoutPlanning:
    """Tests pour calculer_cout_planning."""

    def test_cout_planning_simple(self):
        """Calcul coût simple."""
        from src.modules.cuisine.planning_utils import calculer_cout_planning

        repas1 = Mock()
        repas1.recette_id = 1
        repas2 = Mock()
        repas2.recette_id = 2

        planning = Mock()
        planning.repas = [repas1, repas2]

        prix = {1: 10.0, 2: 15.0}
        result = calculer_cout_planning(planning, prix)

        assert result == 25.0

    def test_cout_planning_vide(self):
        """Planning vide = coût 0."""
        from src.modules.cuisine.planning_utils import calculer_cout_planning

        result = calculer_cout_planning(None, {})
        assert result == 0.0


class TestCalculerVarietePlanning:
    """Tests pour calculer_variete_planning."""

    def test_variete_planning_normale(self):
        """Variété normale."""
        from src.modules.cuisine.planning_utils import calculer_variete_planning

        repas1 = Mock()
        repas1.recette_id = 1
        repas2 = Mock()
        repas2.recette_id = 2
        repas3 = Mock()
        repas3.recette_id = 1  # Répétition

        planning = Mock()
        planning.repas = [repas1, repas2, repas3]

        result = calculer_variete_planning(planning)

        assert result["recettes_uniques"] == 2
        assert len(result["recettes_repetees"]) == 1

    def test_variete_planning_vide(self):
        """Planning vide."""
        from src.modules.cuisine.planning_utils import calculer_variete_planning

        result = calculer_variete_planning(None)

        assert result["recettes_uniques"] == 0
        assert result["taux_variete"] == 0.0
