"""
Schémas Pydantic partagés pour les modèles ML prédictifs.

Contient les modèles de données et constantes partagées entre
les 3 modules ML (consommation, anomalies, satisfaction).
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

# Répertoire pour les modèles sérialisés
MODELS_DIR = Path("data/ml_models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)


class PredictionML(BaseModel):
    """Résultat d'une prédiction ML."""

    article: str
    quantite_predite: float
    intervalle_confiance: tuple[float, float] = (0.0, 0.0)
    confiance: float = 0.0  # 0-1
    methode: str = "ml"  # ml ou statistique (fallback)
    horizon_jours: int = 7


class AnomalieDepense(BaseModel):
    """Anomalie détectée dans les dépenses."""

    description: str
    montant: float
    categorie: str
    date: str
    score_anomalie: float  # -1 = anomalie, 1 = normal
    raison: str = ""


class ScoreRepas(BaseModel):
    """Score de satisfaction prédit pour un repas."""

    recette: str
    score_predit: float = Field(ge=0, le=5)
    facteurs_positifs: list[str] = []
    facteurs_negatifs: list[str] = []


__all__ = [
    "MODELS_DIR",
    "PredictionML",
    "AnomalieDepense",
    "ScoreRepas",
]
