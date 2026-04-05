"""
Tests unitaires pour JardinAnomaliesIAService.

Couvre: détection d'anomalies jardin via IA.
"""

import pytest
from unittest.mock import Mock

from src.services.maison.ia.jardin_anomalies_ia import (
    JardinAnomaliesIAService,
    AnomalieJardin,
    AnomaliesJardinResponse,
)


class TestJardinAnomaliesIAService:
    """Tests pour le service de détection d'anomalies jardin."""

    @pytest.fixture
    def service(self):
        return JardinAnomaliesIAService()

    def test_aucune_plante(self, service):
        """Liste de plantes vide → score 100, message informatif."""
        result = service.detecter_anomalies(plantes=[])
        assert result.score_sante_jardin == 100.0
        assert len(result.recommandations_generales) > 0
        assert result.anomalies == []

    def test_detection_avec_plantes(self, service):
        """Plantes fournies → IA retourne des anomalies."""
        service.call_with_parsing_sync = Mock(
            return_value=AnomaliesJardinResponse(
                anomalies=[
                    AnomalieJardin(
                        plante="Tomate",
                        type_anomalie="stress_hydrique",
                        severite="moyenne",
                        description="Manque d'eau détecté",
                        action_recommandee="Augmenter l'arrosage",
                    )
                ],
                recommandations_generales=["Penser à pailler"],
                score_sante_jardin=72.0,
            )
        )
        plantes = [
            {"nom": "Tomate", "date_plantation": "2026-03-15", "etat": "jaunissement", "frequence_arrosage": "2x/semaine"},
            {"nom": "Basilic", "date_plantation": "2026-03-20", "etat": "normal", "frequence_arrosage": "quotidien"},
        ]
        result = service.detecter_anomalies(plantes=plantes, saison="printemps")
        assert len(result.anomalies) == 1
        assert result.anomalies[0].plante == "Tomate"
        assert result.anomalies[0].type_anomalie == "stress_hydrique"
        assert result.score_sante_jardin == 72.0

    def test_ia_none_fallback(self, service):
        """IA retourne None → score 50 par défaut."""
        service.call_with_parsing_sync = Mock(return_value=None)
        result = service.detecter_anomalies(
            plantes=[{"nom": "Rose", "etat": "normal"}]
        )
        assert result.score_sante_jardin == 50.0
        assert "indisponible" in result.recommandations_generales[0].lower()

    def test_avec_meteo(self, service):
        """Données météo incluses dans le prompt."""
        service.call_with_parsing_sync = Mock(
            return_value=AnomaliesJardinResponse(
                score_sante_jardin=80.0,
                recommandations_generales=["Protéger du gel"],
            )
        )
        plantes = [{"nom": "Lavande", "etat": "normal"}]
        meteo = [
            {"date": "2026-04-01", "temperature_min": -2, "temperature_max": 8, "pluie_mm": 0},
        ]
        result = service.detecter_anomalies(plantes=plantes, meteo_recente=meteo, saison="printemps")
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        assert "-2" in prompt  # La météo est dans le prompt

    def test_limite_20_plantes(self, service):
        """Maximum 20 plantes dans le prompt."""
        service.call_with_parsing_sync = Mock(
            return_value=AnomaliesJardinResponse(score_sante_jardin=70.0)
        )
        plantes = [{"nom": f"Plante{i}", "etat": "normal"} for i in range(30)]
        service.detecter_anomalies(plantes=plantes)
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        # Plante29 ne devrait pas y être (index 20+)
        assert "Plante20" not in prompt
