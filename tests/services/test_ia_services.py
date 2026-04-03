"""
Tests pour les 6 nouveaux services IA du Sprint 13.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

# Imports services
from src.services.inventaire.ia_service import InventaireAIService, PredictionConsommation
from src.services.planning.ia_service import PlanningAIService, AnalyseVariete
from src.services.integrations.meteo_impact_ai import MeteoImpactAIService, MeteoContexte
from src.services.integrations.habitudes_ia import HabitudesAIService, AnalyseHabitude
from src.services.maison.projets_ia_service import ProjetsMaisonAIService, EstimationProjet
from src.services.cuisine.nutrition_famille_ia import (
    NutritionFamilleAIService,
    DonneesNutritionnelles,
)


class TestInventaireAIService:
    """Tests pour InventaireAIService"""

    @pytest.fixture
    def service(self):
        with patch("src.services.inventaire.ia_service.obtenir_client_ia"):
            return InventaireAIService()

    def test_predire_consommation(self, service):
        """Test prédiction de consommation"""
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "consommation_hebdo_kg": 1.5,
                "seuil_kg": 4.5,
                "raison": "Basé sur historique",
            }
        )

        result = service.predire_consommation(
            ingredient_nom="Tomate",
            stock_actuel_kg=2.0,
            historique_achat_mensuel=[
                {"date": "2026-04-01", "quantite_kg": 2.0},
                {"date": "2026-03-01", "quantite_kg": 2.0},
            ],
        )

        assert isinstance(result, PredictionConsommation)
        assert result.ingredient_nom == "Tomate"
        assert result.stock_actuel_kg == 2.0
        assert result.consommation_hebdo_kg == 1.5

    def test_analyse_rotation_fifo(self, service):
        """Test analyse FIFO"""
        mock_result = Mock()
        mock_result.ingredient_nom = "Yaourt"
        mock_result.date_expiration = datetime.now() + timedelta(days=2)
        mock_result.jours_avant_expiration = 2
        mock_result.priorite_consommation = 5
        mock_result.recommandation = "Urgent"

        service.call_with_list_parsing_sync = Mock(return_value=[mock_result])

        result = service.analyse_rotation_fifo(
            [
                {
                    "nom": "Yaourt",
                    "date_exp": (datetime.now() + timedelta(days=2)).isoformat(),
                }
            ]
        )

        assert len(result) > 0


class TestPlanningAIService:
    """Tests pour PlanningAIService"""

    @pytest.fixture
    def service(self):
        with patch("src.services.planning.ia_service.obtenir_client_ia"):
            return PlanningAIService()

    @pytest.mark.asyncio
    async def test_analyser_variete_semaine(self, service):
        """Test analyse de variété"""
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "score_variete": 75,
                "proteins_bien_repartis": True,
                "types_cuisines": ["française", "asiatique"],
                "repetitions_problematiques": [],
                "recommandations": ["Ajouter poisson", "Essayer risotto"],
            }
        )

        planning = [
            {"jour": "lundi", "petit_dej": "Oeufs", "midi": "Poulet", "soir": "Pâtes"},
            {"jour": "mardi", "petit_dej": "Yaourt", "midi": "Poisson", "soir": "Riz"},
        ]

        result = await service.analyser_variete_semaine(planning)

        assert isinstance(result, AnalyseVariete)
        assert result.score_variete == 75
        assert result.proteins_bien_repartis is True


class TestMeteoImpactAIService:
    """Tests pour MeteoImpactAIService"""

    @pytest.fixture
    def service(self):
        with patch("src.services.integrations.meteo_impact_ai.obtenir_client_ia"):
            return MeteoImpactAIService()

    @pytest.mark.asyncio
    async def test_analyser_impacts(self, service):
        """Test analyse impacts météo"""
        service.call_with_list_parsing_sync = Mock(return_value=[])

        previsions = [
            {
                "date": "2026-04-05",
                "conditions": "pluie",
                "temp_min": 8,
                "temp_max": 12,
                "humidite": 85,
                "chance_pluie": 80,
                "vent_km_h": 25,
            }
        ]

        result = await service.analyser_impacts(previsions, "printemps")

        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_suggerer_activites_meteo(self, service):
        """Test suggestions activités"""
        service.call_with_cache = AsyncMock(
            return_value="🎯 Jeux intérieurs\n📝 Construire un fort avec coussins"
        )

        result = await service.suggerer_activites_meteo(
            date="2026-04-05",
            conditions="pluie",
            temperature=(8, 12),
        )

        assert isinstance(result, str)
        assert "Jeux" in result or "intérieur" in result.lower()


class TestHabitudesAIService:
    """Tests pour HabitudesAIService"""

    @pytest.fixture
    def service(self):
        with patch("src.services.integrations.habitudes_ia.obtenir_client_ia"):
            return HabitudesAIService()

    @pytest.mark.asyncio
    async def test_analyser_habitude(self, service):
        """Test analyse habitude"""
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "frequence_hebdo": 5,
                "consistency": 0.71,
                "jours_preferres": ["lun", "mar", "mer", "jeu", "ven"],
                "heures_preferees": ["07:30"],
                "status": "etablie",
                "impact_positif": ["Meilleure énergie"],
                "facteurs_decouplage": ["Fin de semaine"],
            }
        )

        historique = [
            {"date": "2026-04-01", "realise": True, "heure": "07:30"},
            {"date": "2026-04-02", "realise": True, "heure": "07:31"},
            {"date": "2026-04-03", "realise": False},
        ]

        result = await service.analyser_habitude("petit-déj", historique)

        assert isinstance(result, AnalyseHabitude)
        assert result.habitude == "petit-déj"


class TestProjetsMaisonAIService:
    """Tests pour ProjetsMaisonAIService"""

    @pytest.fixture
    def service(self):
        with patch("src.services.maison.projets_ia_service.obtenir_client_ia"):
            return ProjetsMaisonAIService()

    @pytest.mark.asyncio
    async def test_estimer_projet(self, service):
        """Test estimation projet"""
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "complexite": "moyen",
                "temps_jours": 3,
                "est_diy": True,
                "competences_requises": ["peinture", "preparation"],
                "materiaux_principaux": ["peinture", "pinceaux"],
                "budget_materialisation": 150,
                "budget_main_oeuvre": None,
                "budget_total_min": 150,
                "budget_total_max": 300,
                "risques": ["Qualité du fini"],
                "etapes_cles": ["Préparation", "Peinture"],
                "prerequisites": ["Vider la pièce"],
                "recommandations": ["Bien aérer"],
            }
        )

        result = await service.estimer_projet(
            "Repeindre la chambre",
            surface_m2=20,
        )

        assert isinstance(result, EstimationProjet)
        assert result.complexite == "moyen"
        assert result.temps_jours == 3


class TestNutritionFamilleAIService:
    """Tests pour NutritionFamilleAIService"""

    @pytest.fixture
    def service(self):
        with patch("src.services.cuisine.nutrition_famille_ia.obtenir_client_ia"):
            return NutritionFamilleAIService()

    @pytest.mark.asyncio
    async def test_analyser_nutrition_personne(self, service):
        """Test analyse nutrition"""
        service.call_with_dict_parsing_sync = Mock(
            return_value={
                "calories_moyenne": 2000,
                "proteines_g": 50,
                "glucides_g": 200,
                "lipides_g": 60,
                "fibres_g": 25,
                "fruits_legumes_portions": 4.5,
                "eau_litres": 1.8,
                "equilibre_score": 75,
            }
        )

        result = await service.analyser_nutrition_personne(
            "Pierre",
            age_ans=35,
            sexe="M",
            activite_niveau="modere",
        )

        assert isinstance(result, DonneesNutritionnelles)
        assert result.personne == "Pierre"
        assert result.calories_moyenne == 2000


# Tests integration registry

def test_services_registered_in_registry():
    """Vérifier que les services sont bien enregistrés"""
    from src.services.core.registry import registre

    # Vérifier que factory functions existent et retournent des instances
    from src.services.inventaire.ia_service import get_inventaire_ai_service
    from src.services.planning.ia_service import get_planning_ai_service
    from src.services.integrations.meteo_impact_ai import get_meteo_impact_ai_service
    from src.services.integrations.habitudes_ia import get_habitudes_ai_service
    from src.services.maison.projets_ia_service import get_projets_maison_ai_service
    from src.services.cuisine.nutrition_famille_ia import get_nutrition_famille_ai_service

    # Vérifier que les fonctions retournent des instances correct
    assert isinstance(get_inventaire_ai_service(), InventaireAIService)
    assert isinstance(get_planning_ai_service(), PlanningAIService)
    assert isinstance(get_meteo_impact_ai_service(), MeteoImpactAIService)
    assert isinstance(get_habitudes_ai_service(), HabitudesAIService)
    assert isinstance(get_projets_maison_ai_service(), ProjetsMaisonAIService)
    assert isinstance(get_nutrition_famille_ai_service(), NutritionFamilleAIService)
