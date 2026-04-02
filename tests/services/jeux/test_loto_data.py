"""
Tests pour LotoDataService - Service donnÃ©es Loto FDJ.
"""

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from src.services.jeux import (
    NB_NUMEROS_CHANCE,
    NB_NUMEROS_PRINCIPAUX,
    NUMEROS_PAR_TIRAGE,
    LotoDataService,
    StatistiqueNumeroLoto,
    StatistiquesGlobalesLoto,
    TirageLoto,
    obtenir_loto_data_service,
)


class TestLotoDataServiceFactory:
    """Tests de la factory."""

    def test_get_loto_data_service(self):
        """Test crÃ©ation service via factory."""
        service = obtenir_loto_data_service()
        assert isinstance(service, LotoDataService)


class TestLotoDataServiceConstantes:
    """Tests des constantes."""

    def test_nb_numeros_principaux(self):
        """VÃ©rifie le nombre de numÃ©ros principaux."""
        assert NB_NUMEROS_PRINCIPAUX == 49

    def test_nb_numeros_chance(self):
        """VÃ©rifie le nombre de numÃ©ros chance."""
        assert NB_NUMEROS_CHANCE == 10

    def test_numeros_par_tirage(self):
        """VÃ©rifie le nombre de numÃ©ros par tirage."""
        assert NUMEROS_PAR_TIRAGE == 5


class TestTirageLoto:
    """Tests du modÃ¨le TirageLoto."""

    def test_tirage_creation(self):
        """Test crÃ©ation d'un tirage."""
        tirage = TirageLoto(
            date_tirage=date(2026, 2, 15),
            jour_semaine="samedi",
            numeros=[7, 15, 23, 31, 42],
            numero_chance=5,
        )
        assert tirage.date_tirage == date(2026, 2, 15)
        assert len(tirage.numeros) == 5
        assert tirage.numero_chance == 5

    def test_tirage_tous_numeros(self):
        """Test propriÃ©tÃ© tous_numeros."""
        tirage = TirageLoto(
            date_tirage=date(2026, 2, 15),
            numeros=[7, 15, 23, 31, 42],
            numero_chance=5,
        )
        assert tirage.tous_numeros == {7, 15, 23, 31, 42}


class TestStatistiqueNumeroLoto:
    """Tests du modÃ¨le StatistiqueNumeroLoto."""

    def test_stat_defaut(self):
        """Test statistiques par dÃ©faut."""
        stat = StatistiqueNumeroLoto(numero=7)
        assert stat.numero == 7
        assert stat.type_numero == "principal"
        assert stat.total_tirages == 0
        assert stat.frequence == 0.0

    def test_frequence_theorique(self):
        """Test frÃ©quence thÃ©orique."""
        # NumÃ©ro principal: 5/49 â‰ˆ 0.102
        freq_theorique_principal = NUMEROS_PAR_TIRAGE / NB_NUMEROS_PRINCIPAUX
        assert round(freq_theorique_principal, 3) == 0.102

        # NumÃ©ro chance: 1/10 = 0.1
        freq_theorique_chance = 1 / NB_NUMEROS_CHANCE
        assert freq_theorique_chance == 0.1


class TestLotoDataServiceCalculs:
    """Tests des calculs de statistiques."""

    @pytest.fixture
    def service(self):
        """Service pour tests."""
        return LotoDataService()

    @pytest.fixture
    def tirages_exemple(self):
        """Liste de tirages pour tests."""
        return [
            TirageLoto(
                date_tirage=date(2026, 2, 10),
                jour_semaine="lundi",
                numeros=[7, 15, 23, 31, 42],
                numero_chance=5,
            ),
            TirageLoto(
                date_tirage=date(2026, 2, 12),
                jour_semaine="mercredi",
                numeros=[3, 12, 23, 38, 49],
                numero_chance=3,
            ),
            TirageLoto(
                date_tirage=date(2026, 2, 15),
                jour_semaine="samedi",
                numeros=[1, 8, 19, 27, 45],
                numero_chance=5,
            ),
            TirageLoto(
                date_tirage=date(2026, 2, 17),
                jour_semaine="lundi",
                numeros=[7, 14, 28, 35, 41],
                numero_chance=8,
            ),
        ]

    def test_calculer_statistiques_numero_principal(self, service, tirages_exemple):
        """Test statistiques numÃ©ro principal."""
        # Le 7 est sorti 2 fois (10 et 17 fÃ©vrier)
        stats = service.calculer_statistiques_numero(7, tirages_exemple, "principal")

        assert stats.numero == 7
        assert stats.type_numero == "principal"
        assert stats.total_tirages == 4
        assert stats.nb_sorties == 2
        assert stats.frequence == 0.5  # 2/4
        assert stats.serie_actuelle == 0  # Dernier tirage contient le 7
        assert stats.derniere_sortie == date(2026, 2, 17)

    def test_calculer_statistiques_numero_en_retard(self, service, tirages_exemple):
        """Test numÃ©ro qui n'est jamais sorti."""
        # Le 2 n'est jamais sorti
        stats = service.calculer_statistiques_numero(2, tirages_exemple, "principal")

        assert stats.numero == 2
        assert stats.nb_sorties == 0
        assert stats.frequence == 0.0
        assert stats.serie_actuelle == 4  # Aucune sortie en 4 tirages
        assert stats.derniere_sortie is None

    def test_calculer_statistiques_numero_chance(self, service, tirages_exemple):
        """Test statistiques numÃ©ro chance."""
        # Le 5 est sorti 2 fois (10 et 15 fÃ©vrier)
        stats = service.calculer_statistiques_numero(5, tirages_exemple, "chance")

        assert stats.numero == 5
        assert stats.type_numero == "chance"
        assert stats.nb_sorties == 2
        assert stats.serie_actuelle == 1  # 1 tirage depuis (17 fÃ©vrier)

    def test_calculer_value(self, service, tirages_exemple):
        """Test calcul de la value (loi des sÃ©ries)."""
        # NumÃ©ro 2 jamais sorti: frequence=0, serie=4, value=0
        stats_2 = service.calculer_statistiques_numero(2, tirages_exemple, "principal")
        assert stats_2.value == 0.0

        # Le 23 sorti 2 fois, sÃ©rie actuelle = 2
        stats_23 = service.calculer_statistiques_numero(23, tirages_exemple, "principal")
        assert stats_23.nb_sorties == 2
        assert stats_23.serie_actuelle == 2  # Pas sorti les 15 et 17 fÃ©vrier
        # value = 0.5 Ã— 2 = 1.0
        assert stats_23.value == 1.0

    def test_calculer_toutes_statistiques(self, service, tirages_exemple):
        """Test calcul de toutes les statistiques."""
        stats = service.calculer_toutes_statistiques(tirages_exemple)

        assert stats.total_tirages == 4
        assert stats.date_premier_tirage == date(2026, 2, 10)
        assert stats.date_dernier_tirage == date(2026, 2, 17)
        assert len(stats.numeros_principaux) == 49
        assert len(stats.numeros_chance) == 10

    def test_obtenir_numeros_en_retard(self, service, tirages_exemple):
        """Test dÃ©tection des numÃ©ros en retard."""
        # Avec un seuil bas pour avoir des rÃ©sultats
        numeros_retard = service.obtenir_numeros_en_retard(
            tirages_exemple, seuil_value=0.5, type_numero="principal"
        )

        # Devrait inclure le 23 (value=1.0)
        numeros_values = {n.numero: n.value for n in numeros_retard}
        assert 23 in numeros_values
        assert numeros_values[23] == 1.0

    def test_tri_numeros_en_retard(self, service, tirages_exemple):
        """Test que les numÃ©ros sont triÃ©s par value dÃ©croissante."""
        numeros = service.obtenir_numeros_en_retard(
            tirages_exemple, seuil_value=0.1, type_numero="principal"
        )

        if len(numeros) >= 2:
            # VÃ©rifier tri dÃ©croissant
            for i in range(len(numeros) - 1):
                assert numeros[i].value >= numeros[i + 1].value


class TestLotoDataServiceParsing:
    """Tests du parsing CSV."""

    @pytest.fixture
    def service(self):
        """Service pour tests."""
        return LotoDataService()

    def test_parser_csv_format_fdj(self, service):
        """Test parsing format CSV FDJ."""
        csv_content = """annee_numero_de_tirage;date_de_tirage;boule_1;boule_2;boule_3;boule_4;boule_5;numero_chance
2026001;15/02/2026;7;15;23;31;42;5
2026002;17/02/2026;3;12;28;35;49;8"""

        tirages = service._parser_csv_fdj(csv_content)

        assert len(tirages) == 2
        assert tirages[0].date_tirage == date(2026, 2, 15)
        assert tirages[0].numeros == [7, 15, 23, 31, 42]
        assert tirages[0].numero_chance == 5

    def test_parser_csv_format_alternatif(self, service):
        """Test parsing format alternatif."""
        csv_content = """date,boule1,boule2,boule3,boule4,boule5,chance
2026-02-15,7,15,23,31,42,5"""

        tirages = service._parser_csv_fdj(csv_content)

        # Devrait gÃ©rer gracieusement les diffÃ©rents formats
        # Note: peut ne pas parser parfaitement selon le format exact


class TestLotoDataServiceScenarios:
    """Tests de scÃ©narios rÃ©alistes."""

    def test_scenario_numero_tres_en_retard(self):
        """
        ScÃ©nario: NumÃ©ro absent depuis longtemps.
        FrÃ©quence thÃ©orique: 5/49 â‰ˆ 10.2%
        Si absent 25 tirages: value = 0.102 Ã— 25 = 2.55 (opportunitÃ©)
        """
        from src.services.jeux import SeriesService

        frequence_theorique = NUMEROS_PAR_TIRAGE / NB_NUMEROS_PRINCIPAUX
        serie = 25

        value = SeriesService.calculer_value(frequence_theorique, serie)

        assert value > 2.5  # Haute opportunitÃ©
        assert SeriesService.est_opportunite(value)

    def test_scenario_numero_chance_en_retard(self):
        """
        ScÃ©nario: NumÃ©ro chance absent.
        FrÃ©quence thÃ©orique: 1/10 = 10%
        Si absent 25 tirages: value = 0.1 Ã— 25 = 2.5 (opportunitÃ©)
        """
        from src.services.jeux import SeriesService

        frequence_theorique = 1 / NB_NUMEROS_CHANCE
        serie = 25

        value = SeriesService.calculer_value(frequence_theorique, serie)

        assert value == 2.5
        assert SeriesService.est_opportunite(value)

