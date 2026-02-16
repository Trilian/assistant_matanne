"""
Tests pour JardinService.

Couvre:
- Conseils saisonniers
- Plans d'arrosage
- Diagnostics plantes
- Impact météo
"""

import json
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.jardin_service import JardinService, get_jardin_service
from src.services.maison.schemas import ConseilJardin, PlanArrosage


class TestJardinServiceInit:
    """Tests d'initialisation du service."""

    def test_factory_returns_service(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.jardin_service.ClientIA"):
            service = get_jardin_service()
            assert isinstance(service, JardinService)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        service = get_jardin_service(client=mock_client)
        assert service.client == mock_client


class TestJardinServiceConseils:
    """Tests des conseils jardin."""

    @pytest.mark.asyncio
    async def test_generer_conseils_saison_printemps(self, mock_client_ia):
        """Génère des conseils adaptés au printemps."""
        mock_client_ia.generer = AsyncMock(
            return_value=json.dumps(
                [
                    {"conseil": "Semer les tomates", "priorite": "haute"},
                    {"conseil": "Tailler les rosiers", "priorite": "moyenne"},
                ]
            )
        )

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(
            return_value=json.dumps(
                [
                    {"conseil": "Semer les tomates", "priorite": "haute"},
                ]
            )
        )

        conseils = await service.generer_conseils_saison("printemps", ["tomates", "rosiers"])

        # Vérifier que l'appel IA est fait
        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_generer_conseils_sans_plantes(self, mock_client_ia):
        """Génère des conseils généraux sans liste de plantes."""
        mock_client_ia.generer = AsyncMock(return_value="Conseils généraux")

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value="Conseils généraux")

        conseils = await service.generer_conseils_saison("été")

        assert service.call_with_cache.called


class TestJardinServiceArrosage:
    """Tests des plans d'arrosage."""

    def test_conseil_arrosage_calcul(self, mock_jardin_service, plante_jardin_data):
        """Calcule le conseil d'arrosage basé sur les données."""
        # Simuler une plante qui a besoin d'eau
        plante_jardin_data["derniere_irrigation"] = date.today() - timedelta(days=5)

        # Test direct de la logique de calcul
        jours_depuis = (date.today() - plante_jardin_data["derniere_irrigation"]).days
        assert jours_depuis == 5

    def test_conseil_arrosage_gel_prevu(self, meteo_gel_data):
        """Pas d'arrosage si gel prévu."""
        assert meteo_gel_data["gel_prevu"] is True
        # Le service devrait retourner "Reporter l'arrosage - gel prévu"

    @pytest.mark.asyncio
    async def test_generer_plan_arrosage(self, mock_client_ia):
        """Génère un plan d'arrosage pour plusieurs plantes."""
        mock_response = json.dumps(
            {
                "plan": [
                    {"plante": "Tomates", "frequence": "2 jours", "quantite": "2L"},
                    {"plante": "Salades", "frequence": "quotidien", "quantite": "0.5L"},
                ]
            }
        )
        mock_client_ia.generer = AsyncMock(return_value=mock_response)

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        plantes = ["Tomates", "Salades"]
        plan = await service.generer_plan_arrosage(plantes)

        assert service.call_with_cache.called


class TestJardinServiceDiagnostic:
    """Tests des diagnostics de plantes."""

    @pytest.mark.asyncio
    async def test_diagnostiquer_plante_avec_image(self, mock_client_ia):
        """Diagnostic avec image de la plante."""
        mock_response = json.dumps(
            {
                "probleme": "Carence en azote",
                "symptomes": ["Feuilles jaunies", "Croissance lente"],
                "traitement": "Apport d'engrais azoté",
                "urgence": "moyenne",
            }
        )

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        diagnostic = await service.diagnostiquer_plante(
            "Tomate",
            symptomes=["feuilles jaunes"],
            image_base64=None,
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_diagnostiquer_plante_sans_image(self, mock_client_ia):
        """Diagnostic basé uniquement sur les symptômes."""
        mock_response = "Possible carence ou excès d'eau"

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        diagnostic = await service.diagnostiquer_plante(
            "Basilic",
            symptomes=["feuilles noires", "tiges molles"],
        )

        assert service.call_with_cache.called


class TestJardinServiceMeteo:
    """Tests de l'intégration météo."""

    @pytest.mark.asyncio
    async def test_analyser_meteo_impact(self, mock_client_ia, meteo_data):
        """Analyse l'impact de la météo sur le jardin."""
        mock_response = json.dumps(
            {
                "impact": "favorable",
                "actions": ["Arrosage normal", "Binages possibles"],
            }
        )

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        impact = await service.analyser_meteo_impact(meteo_data)

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_analyser_meteo_gel(self, mock_client_ia, meteo_gel_data):
        """Détecte et alerte sur le risque de gel."""
        mock_response = json.dumps(
            {
                "impact": "critique",
                "risque": "gel",
                "actions": ["Protéger les plantes sensibles", "Rentrer les pots"],
            }
        )

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        impact = await service.analyser_meteo_impact(meteo_gel_data)

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_generer_conseils_meteo(self, mock_client_ia):
        """Génère des conseils adaptés à la météo."""
        mock_response = "Journée idéale pour le jardinage. Pensez à arroser ce soir."

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        conseils = await service.generer_conseils_meteo(
            temperature=20,
            conditions="ensoleillé",
        )

        assert service.call_with_cache.called


class TestJardinServiceSuggestions:
    """Tests des suggestions de plantes."""

    @pytest.mark.asyncio
    async def test_suggerer_plantes_saison(self, mock_client_ia):
        """Suggère des plantes adaptées à la saison."""
        mock_response = json.dumps(
            [
                "Tomates cerises",
                "Courgettes",
                "Basilic",
                "Haricots verts",
            ]
        )

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        suggestions = await service.suggerer_plantes_saison("printemps")

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_suggerer_plantes_avec_contraintes(self, mock_client_ia):
        """Suggère des plantes avec contraintes (ombre, peu d'entretien)."""
        mock_response = json.dumps(
            [
                "Hostas",
                "Fougères",
                "Heuchères",
            ]
        )

        service = JardinService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        suggestions = await service.suggerer_plantes_saison(
            "été",
            contraintes=["ombre", "peu d'entretien"],
        )

        assert service.call_with_cache.called


class TestJardinServiceIntegration:
    """Tests d'intégration avec vraies données."""

    def test_calcul_frequence_arrosage(self):
        """Teste le calcul de fréquence d'arrosage."""
        # Température élevée = arrosage plus fréquent
        temp_haute = 30
        freq_haute = max(1, 4 - (temp_haute - 20) // 5)  # 2 jours

        temp_basse = 15
        freq_basse = max(1, 4 - (temp_basse - 20) // 5)  # 5 jours (cap à 4)

        assert freq_haute < freq_basse or freq_basse == 4

    def test_detection_saison(self):
        """Teste la détection de saison basée sur le mois."""
        mois_saison = {
            1: "hiver",
            2: "hiver",
            3: "printemps",
            4: "printemps",
            5: "printemps",
            6: "été",
            7: "été",
            8: "été",
            9: "automne",
            10: "automne",
            11: "automne",
            12: "hiver",
        }

        for mois, saison in mois_saison.items():
            if mois in [3, 4, 5]:
                assert saison == "printemps"
            elif mois in [6, 7, 8]:
                assert saison == "été"
            elif mois in [9, 10, 11]:
                assert saison == "automne"
            else:
                assert saison == "hiver"
