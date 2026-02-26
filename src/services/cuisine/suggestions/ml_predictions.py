"""
Module ML Prédictif — façade de rétro-compatibilité.

Les 3 modèles ML sont maintenant divisés en modules séparés:
- ml_consommation.py: ModeleConsommationML (GradientBoostingRegressor)
- ml_anomalies.py: DetecteurAnomaliesDepenses (Isolation Forest)
- ml_satisfaction.py: ScoreSatisfactionRepas (RandomForestRegressor)
- ml_schemas.py: Schémas Pydantic partagés (PredictionML, AnomalieDepense, ScoreRepas)

Ce fichier maintient la rétro-compatibilité des imports existants.
"""

from __future__ import annotations

import logging
from typing import Any

from src.services.core.registry import service_factory

# Re-exports depuis les modules séparés
from .ml_anomalies import DetecteurAnomaliesDepenses  # noqa: F401
from .ml_consommation import ModeleConsommationML  # noqa: F401
from .ml_satisfaction import ScoreSatisfactionRepas  # noqa: F401
from .ml_schemas import AnomalieDepense, PredictionML, ScoreRepas  # noqa: F401

logger = logging.getLogger(__name__)

__all__ = [
    "ModeleConsommationML",
    "DetecteurAnomaliesDepenses",
    "ScoreSatisfactionRepas",
    "MLPredictionService",
    "PredictionML",
    "AnomalieDepense",
    "ScoreRepas",
    "obtenir_ml_predictions",
]


# -----------------------------------------------------------
# SERVICE UNIFIÉ
# -----------------------------------------------------------


class MLPredictionService:
    """Service unifié pour toutes les prédictions ML.

    Combine les 3 modèles et fournit une interface cohérente.
    """

    def __init__(self):
        self.consommation = ModeleConsommationML()
        self.anomalies = DetecteurAnomaliesDepenses()
        self.satisfaction = ScoreSatisfactionRepas()

    def entrainer_tous(
        self,
        historique_achats: list[dict] | None = None,
        historique_depenses: list[dict] | None = None,
        historique_repas: list[dict] | None = None,
    ) -> dict[str, Any]:
        """Entraîne tous les modèles disponibles.

        Args:
            historique_achats: Pour prédiction consommation
            historique_depenses: Pour détection anomalies
            historique_repas: Pour score satisfaction

        Returns:
            Dict avec résultats par modèle
        """
        resultats = {}

        if historique_achats:
            resultats["consommation"] = self.consommation.entrainer(historique_achats)
        if historique_depenses:
            resultats["anomalies"] = self.anomalies.entrainer(historique_depenses)
        if historique_repas:
            resultats["satisfaction"] = self.satisfaction.entrainer(historique_repas)

        return resultats

    def statut_modeles(self) -> dict[str, bool]:
        """Vérifie quels modèles sont entraînés."""
        return {
            "consommation": getattr(self.consommation, "_modele", None) is not None,
            "anomalies": getattr(self.anomalies, "_modele", None) is not None,
            "satisfaction": getattr(self.satisfaction, "_modele", None) is not None,
        }


# -----------------------------------------------------------
# SINGLETON
# -----------------------------------------------------------


@service_factory("ml_predictions", tags={"cuisine", "ia", "ml"})
def obtenir_ml_predictions() -> MLPredictionService:
    """Obtient le service ML prédictif (thread-safe via registre)."""
    return MLPredictionService()
