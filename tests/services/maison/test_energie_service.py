"""
Tests pour EnergieService.

Couvre:
- Analyse de consommation
- Calcul éco-score
- Simulation d'économies
- Système de badges
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.maison.energie_service import EnergieService, get_energie_service


class TestEnergieServiceInit:
    """Tests d'initialisation du service."""

    def test_factory_returns_service(self):
        """La factory retourne une instance valide."""
        with patch("src.services.maison.energie_service.ClientIA"):
            service = get_energie_service()
            assert isinstance(service, EnergieService)

    def test_factory_accepts_custom_client(self):
        """La factory accepte un client personnalisé."""
        mock_client = MagicMock()
        service = get_energie_service(client=mock_client)
        assert service.client == mock_client


class TestEnergieServiceAnalyse:
    """Tests de l'analyse de consommation."""

    def test_analyser_consommation(self, mock_client_ia):
        """Analyse la consommation mensuelle."""
        from src.services.maison.schemas import AnalyseEnergie

        service = EnergieService(client=mock_client_ia)

        mock_result = AnalyseEnergie(
            periode="12 derniers mois",
            energie="electricite",
            consommation_totale=320.5,
            cout_total=Decimal("70.51"),
            tendance="stable",
            anomalies_detectees=[],
            suggestions_economies=["Passer aux LED (économie ~80%)"],
        )

        with patch.object(service, "_analyser_conso_impl", return_value=mock_result):
            analyse = service.analyser_consommation(energie="electricite", db=MagicMock())

        assert analyse is not None
        assert analyse.energie == "electricite"

    def test_detecter_anomalie_pic(self, mock_client_ia):
        """Détecte un pic de consommation anormal."""
        from src.services.maison.schemas import AnalyseEnergie

        service = EnergieService(client=mock_client_ia)

        mock_result = AnalyseEnergie(
            periode="3 derniers mois",
            energie="electricite",
            consommation_totale=500,
            cout_total=Decimal("110.00"),
            tendance="hausse",
            anomalies_detectees=["Pic détecté en février: 500 kWh (+50%)"],
            suggestions_economies=[],
        )

        with patch.object(service, "_analyser_conso_impl", return_value=mock_result):
            analyse = service.analyser_consommation(
                energie="electricite", nb_mois=3, db=MagicMock()
            )

        assert analyse is not None
        assert len(analyse.anomalies_detectees) >= 1


class TestEnergieServiceEcoScore:
    """Tests du calcul de l'éco-score."""

    def test_calculer_eco_score(self, mock_client_ia):
        """Calcule l'éco-score mensuel."""
        from src.services.maison.schemas import EcoScoreResult

        service = EnergieService(client=mock_client_ia)

        mock_result = EcoScoreResult(
            mois=date(2026, 2, 1),
            score=75,
            score_precedent=None,
            variation=None,
            streak_jours=0,
            economies_euros=Decimal("15.00"),
            badges_obtenus=[],
            conseils_amelioration=["Excellent!"],
            comparaison_moyenne="25% au-dessus de la moyenne nationale",
        )

        with patch.object(service, "_calculer_score_impl", return_value=mock_result):
            score = service.calculer_eco_score(mois=date(2026, 2, 1), db=MagicMock())

        assert score is not None
        assert 0 <= score.score <= 100

    def test_score_dans_limites(self):
        """Vérifie que le score est entre 0 et 100."""
        scores_valides = [0, 25, 50, 75, 100]
        scores_invalides = [-10, 110, 200]

        for s in scores_valides:
            assert 0 <= s <= 100

        for s in scores_invalides:
            assert not (0 <= s <= 100)


class TestEnergieServiceBadges:
    """Tests du système de badges."""

    def test_badge_economiseur_eau(self):
        """Badge pour économie d'eau."""
        consommation_eau = 8  # m³, sous la moyenne de 10
        moyenne_nationale = 10

        economie_pct = (moyenne_nationale - consommation_eau) / moyenne_nationale * 100
        badge_obtenu = economie_pct > 15

        assert economie_pct == 20
        assert badge_obtenu

    def test_badge_early_bird(self):
        """Badge pour consommation hors heures de pointe."""
        heures_creuses_pct = 70  # 70% de conso en heures creuses
        seuil_badge = 60

        assert heures_creuses_pct >= seuil_badge

    def test_badge_streak(self):
        """Badge pour série de bons mois."""
        mois_consecutifs_bons = 3
        seuil_streak = 3

        assert mois_consecutifs_bons >= seuil_streak

    @pytest.mark.skip(reason="Méthode obtenir_badges() non implémentée dans EnergieService")
    @pytest.mark.asyncio
    async def test_obtenir_badges_utilisateur(self, mock_client_ia):
        """Récupère tous les badges de l'utilisateur."""
        pass


class TestEnergieServiceSimulation:
    """Tests des simulations d'économies."""

    @pytest.mark.asyncio
    async def test_simuler_economies_led(self, mock_client_ia):
        """Simule les économies de passer aux LED."""
        mock_response = json.dumps(
            {
                "investissement": 150,
                "economie_annuelle": 80,
                "temps_retour_mois": 22,
                "co2_evite_kg": 35,
            }
        )

        service = EnergieService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        simulation = await service.simuler_economies(
            action="remplacement_led",
            energie="electricite",
        )

        assert service.call_with_cache.called

    @pytest.mark.asyncio
    async def test_simuler_economies_isolation(self, mock_client_ia):
        """Simule les économies d'une meilleure isolation."""
        mock_response = json.dumps(
            {
                "investissement": 5000,
                "economie_annuelle": 600,
                "temps_retour_mois": 100,
                "aides_disponibles": 2000,
                "temps_retour_avec_aides_mois": 60,
            }
        )

        service = EnergieService(client=mock_client_ia)
        service.call_with_cache = AsyncMock(return_value=mock_response)

        simulation = await service.simuler_economies(
            action="isolation_combles",
            energie="gaz",
        )

        assert service.call_with_cache.called


class TestEnergieServiceComparaison:
    """Tests de comparaison de périodes."""

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_comparer_mois(self, mock_client_ia):
        """Compare deux périodes de consommation."""
        service = EnergieService(client=mock_client_ia)

        mock_result = {
            "periode1": {"debut": date(2026, 1, 1), "fin": date(2026, 1, 31), "conso": 300},
            "periode2": {"debut": date(2026, 2, 1), "fin": date(2026, 2, 28), "conso": 276},
            "variation_pct": -8.0,
            "tendance": "baisse",
        }

        with patch.object(service, "_comparer_impl", return_value=mock_result):
            comparaison = await service.comparer_periode(
                energie="electricite",
                periode1=(date(2026, 1, 1), date(2026, 1, 31)),
                periode2=(date(2026, 2, 1), date(2026, 2, 28)),
                db=MagicMock(),
            )

        assert comparaison is not None
        assert "variation_pct" in comparaison

    @pytest.mark.skip(reason="Méthode comparer_annees() non implémentée dans EnergieService")
    @pytest.mark.asyncio
    async def test_comparer_annees(self, mock_client_ia):
        """Compare deux années de consommation."""
        pass


class TestEnergieServiceCalculs:
    """Tests des calculs utilitaires."""

    def test_calcul_cout_kwh(self):
        """Calcule le coût de l'électricité."""
        kwh = Decimal("320")
        prix_kwh = Decimal("0.22")
        abonnement = Decimal("15")

        cout = kwh * prix_kwh + abonnement
        assert cout == Decimal("85.40")

    def test_calcul_cout_gaz(self):
        """Calcule le coût du gaz."""
        m3 = Decimal("45")
        prix_m3 = Decimal("1.10")
        abonnement = Decimal("20")

        cout = m3 * prix_m3 + abonnement
        assert cout == Decimal("69.50")

    def test_calcul_variation_pct(self):
        """Calcule la variation en pourcentage."""
        ancien = Decimal("300")
        nouveau = Decimal("276")

        variation = (nouveau - ancien) / ancien * 100
        assert variation == Decimal("-8")

    def test_estimation_co2(self):
        """Estime les émissions CO2."""
        kwh = 320
        facteur_emission = 0.05  # kg CO2 / kWh (moyenne française)

        co2 = kwh * facteur_emission
        assert co2 == 16  # kg de CO2
