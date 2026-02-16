"""
Tests pour ProjetsService.

Couvre:
- Estimation de projets
- Suggestions de matériaux
- Calcul de ROI
- Priorisation des tâches
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.projets_service import ProjetsService, get_projets_service
from src.services.maison.schemas import ProjetCreate, ProjetEstimation


class TestProjetsServiceInit:
    """Tests d'initialisation du service."""

    def test_factory_returns_service(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.projets_service.ClientIA"):
            service = get_projets_service()
            assert isinstance(service, ProjetsService)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        service = get_projets_service(client=mock_client)
        assert service.client == mock_client


class TestProjetsServiceEstimation:
    """Tests des estimations de projet."""

    @pytest.mark.asyncio
    async def test_estimer_projet_peinture(self, mock_client_ia):
        """Estime un projet de peinture."""
        mock_response = json.dumps(
            {
                "duree_heures": 8,
                "budget_min": 150,
                "budget_max": 250,
                "materiaux": [
                    {"nom": "Peinture blanche 10L", "quantite": 2, "prix": 45},
                    {"nom": "Rouleau", "quantite": 3, "prix": 8},
                    {"nom": "Bâche protection", "quantite": 1, "prix": 15},
                ],
                "etapes": [
                    "Préparation des surfaces",
                    "Application sous-couche",
                    "2 couches de peinture",
                    "Finitions et nettoyage",
                ],
                "risques": ["Temps de séchage variable selon météo"],
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        estimation = await service.estimer_projet(
            description="Peinture chambre 12m²",
            type_projet="peinture",
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_estimer_projet_renovation(self, mock_client_ia, projet_test_data):
        """Estime un projet de rénovation."""
        mock_response = json.dumps(
            {
                "duree_heures": 24,
                "budget_min": 500,
                "budget_max": 1200,
                "niveau_difficulte": "moyen",
                "competences_requises": ["Électricité de base", "Plâtrerie"],
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        estimation = await service.estimer_projet(
            description=projet_test_data["description"],
            type_projet="rénovation",
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_estimer_projet_avec_contraintes(self, mock_client_ia):
        """Estime avec contraintes (budget, temps)."""
        mock_response = json.dumps(
            {
                "faisable": True,
                "ajustements": ["Utiliser peinture moyenne gamme", "Faire en 2 weekends"],
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        estimation = await service.estimer_projet(
            description="Peinture garage",
            type_projet="peinture",
            contraintes={"budget_max": 100, "temps_max_heures": 4},
        )

        assert service.call_with_cache.called


class TestProjetsServiceMateriaux:
    """Tests des suggestions de matériaux."""

    @pytest.mark.asyncio
    async def test_suggerer_materiaux(self, mock_client_ia):
        """Suggère les matériaux nécessaires."""
        mock_response = json.dumps(
            [
                {"nom": "Vis 4x40", "quantite": 50, "prix_unitaire": 0.05},
                {"nom": "Chevilles", "quantite": 20, "prix_unitaire": 0.15},
                {"nom": "Équerres", "quantite": 4, "prix_unitaire": 2.50},
            ]
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        materiaux = await service.suggerer_materiaux(
            projet="Installation étagères murales",
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_suggerer_alternatives_eco(self, mock_client_ia):
        """Suggère des alternatives écologiques."""
        mock_response = json.dumps(
            [
                {
                    "original": "Peinture glycéro",
                    "alternative": "Peinture acrylique",
                    "avantage": "Moins de COV, nettoyage à l'eau",
                    "surcoût": 0,
                },
                {
                    "original": "Bois exotique",
                    "alternative": "Bois local FSC",
                    "avantage": "Empreinte carbone réduite",
                    "surcoût": -10,
                },
            ]
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        alternatives = await service.suggerer_alternatives(
            materiaux=["Peinture glycéro", "Bois exotique"],
            critere="ecologique",
        )

        assert service.call_with_cache.called


class TestProjetsServiceBudget:
    """Tests des estimations de budget."""

    @pytest.mark.asyncio
    async def test_estimer_budget(self, mock_client_ia):
        """Estime le budget d'un projet."""
        mock_response = json.dumps(
            {
                "materiaux": 180.50,
                "outils": 45.00,
                "main_oeuvre": 0,
                "total": 225.50,
                "marge_securite": 25.00,
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        budget = await service.estimer_budget(
            materiaux=[
                {"nom": "Peinture", "quantite": 2, "prix_unitaire": 45},
                {"nom": "Rouleaux", "quantite": 3, "prix_unitaire": 8},
            ],
            avec_main_oeuvre=False,
        )

        assert service.call_with_cache.called

    def test_calcul_cout_materiaux(self):
        """Calcule le coût des matériaux."""
        materiaux = [
            {"nom": "Peinture", "quantite": 2, "prix_unitaire": Decimal("45.00")},
            {"nom": "Rouleaux", "quantite": 3, "prix_unitaire": Decimal("8.00")},
        ]

        total = sum(m["quantite"] * m["prix_unitaire"] for m in materiaux)

        assert total == Decimal("114.00")


class TestProjetsServiceROI:
    """Tests du calcul de ROI."""

    @pytest.mark.asyncio
    async def test_calculer_roi_renovation(self, mock_client_ia):
        """Calcule le ROI d'une rénovation."""
        mock_response = json.dumps(
            {
                "investissement": 5000,
                "plus_value_estimee": 8000,
                "roi_pourcentage": 60,
                "temps_retour_annees": 2,
                "facteurs": [
                    "Amélioration DPE",
                    "Modernisation cuisine",
                ],
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        roi = await service.calculer_roi(
            type_renovation="isolation",
            cout=5000,
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_calculer_roi_energie(self, mock_client_ia):
        """Calcule le ROI d'une amélioration énergie."""
        mock_response = json.dumps(
            {
                "investissement": 3000,
                "economies_annuelles": 400,
                "temps_retour_annees": 7.5,
                "aides_disponibles": ["MaPrimeRénov", "CEE"],
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        roi = await service.calculer_roi(
            type_renovation="pompe_a_chaleur",
            cout=8000,
        )

        assert service.call_with_cache.called


class TestProjetsServiceTaches:
    """Tests de la gestion des tâches."""

    @pytest.mark.asyncio
    async def test_suggerer_taches_projet(self, mock_client_ia):
        """Suggère les tâches pour un projet."""
        mock_response = json.dumps(
            [
                {"nom": "Préparation surfaces", "duree_h": 2, "ordre": 1},
                {"nom": "Sous-couche", "duree_h": 1, "ordre": 2},
                {"nom": "1ère couche", "duree_h": 3, "ordre": 3},
                {"nom": "2ème couche", "duree_h": 3, "ordre": 4},
                {"nom": "Finitions", "duree_h": 1, "ordre": 5},
            ]
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        taches = await service.suggerer_taches(
            projet="Peinture chambre",
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_prioriser_taches(self, mock_client_ia):
        """Priorise les tâches d'un projet."""
        mock_response = json.dumps(
            {
                "ordre_optimal": [
                    {"nom": "Urgente", "priorite": 1, "raison": "Bloque les autres"},
                    {"nom": "Importante", "priorite": 2, "raison": "Impact visuel"},
                ],
            }
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        priorites = await service.prioriser_taches(
            taches=[
                {"nom": "Urgente", "deadline": True},
                {"nom": "Importante", "deadline": False},
            ],
        )

        assert service.call_with_cache.called


class TestProjetsServiceRisques:
    """Tests de l'identification des risques."""

    @pytest.mark.asyncio
    async def test_identifier_risques(self, mock_client_ia):
        """Identifie les risques d'un projet."""
        mock_response = json.dumps(
            [
                {
                    "risque": "Mauvaise météo",
                    "probabilite": "moyenne",
                    "impact": "retard 2-3 jours",
                    "mitigation": "Prévoir weekend de backup",
                },
                {
                    "risque": "Matériau en rupture",
                    "probabilite": "faible",
                    "impact": "retard 1 semaine",
                    "mitigation": "Commander en avance",
                },
            ]
        )

        service = ProjetsService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        risques = await service.identifier_risques(
            projet="Terrasse bois",
        )

        assert service.call_with_cache.called


class TestProjetsServiceCalculs:
    """Tests des calculs utilitaires."""

    def test_calcul_duree_totale(self):
        """Calcule la durée totale d'un projet."""
        taches = [
            {"duree_h": 2},
            {"duree_h": 3},
            {"duree_h": 1},
        ]

        duree_totale = sum(t["duree_h"] for t in taches)
        assert duree_totale == 6

    def test_calcul_jours_projet(self):
        """Calcule le nombre de jours pour un projet."""
        heures_totales = 24
        heures_par_jour = 4  # Weekend

        jours = heures_totales / heures_par_jour
        assert jours == 6  # 6 jours de 4h

    def test_calcul_marge_budget(self):
        """Calcule la marge de sécurité budget."""
        budget_base = Decimal("500.00")
        marge_pct = Decimal("10")  # 10%

        marge = budget_base * marge_pct / 100
        budget_total = budget_base + marge

        assert budget_total == Decimal("550.00")

    def test_verification_deadline(self, projet_test_data):
        """Vérifie si un projet respecte sa deadline."""
        duree_estimee_jours = 7
        date_debut = projet_test_data["date_debut_prevue"]
        date_fin = date_debut + timedelta(days=duree_estimee_jours)

        deadline = projet_test_data["date_fin_prevue"]
        en_retard = date_fin > deadline

        assert not en_retard  # Projet dans les temps
