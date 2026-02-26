"""
Modèle ML — Prédiction de consommation hebdomadaire.

Utilise un GradientBoostingRegressor avec features temporelles
(jour semaine, mois, semaine année, tendance) pour prédire
la consommation d'articles.

Usage:
    from src.services.cuisine.suggestions.ml_consommation import ModeleConsommationML

    modele = ModeleConsommationML()
    modele.entrainer(historique_achats)
    prediction = modele.predire("tomates", horizon_jours=7)
"""

from __future__ import annotations

import logging
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from .ml_schemas import MODELS_DIR, PredictionML

logger = logging.getLogger(__name__)

__all__ = ["ModeleConsommationML"]


class ModeleConsommationML:
    """Prédit la consommation d'articles via régression.

    Utilise un GradientBoostingRegressor avec features temporelles
    (jour semaine, mois, semaine année, tendance).
    """

    def __init__(self):
        self._modele = None
        self._scaler = None
        self._articles_connus: set[str] = set()
        self._modele_path = MODELS_DIR / "consommation_model.pkl"

        # Charger modèle existant
        self._charger()

    def _charger(self) -> bool:
        """Charge un modèle sérialisé s'il existe."""
        if self._modele_path.exists():
            try:
                with open(self._modele_path, "rb") as f:
                    data = pickle.load(f)  # noqa: S301
                self._modele = data.get("modele")
                self._scaler = data.get("scaler")
                self._articles_connus = data.get("articles", set())
                logger.info(f"Modèle consommation chargé ({len(self._articles_connus)} articles)")
                return True
            except Exception as e:
                logger.warning(f"Erreur chargement modèle: {e}")
        return False

    def _sauvegarder(self) -> None:
        """Sauvegarde le modèle sur disque."""
        try:
            with open(self._modele_path, "wb") as f:
                pickle.dump(
                    {
                        "modele": self._modele,
                        "scaler": self._scaler,
                        "articles": self._articles_connus,
                    },
                    f,
                )
            logger.info("Modèle consommation sauvegardé")
        except Exception as e:
            logger.warning(f"Erreur sauvegarde modèle: {e}")

    def _extraire_features(self, date_val: datetime) -> list[float]:
        """Extrait les features temporelles d'une date.

        Features:
        - jour_semaine (0-6)
        - mois (1-12)
        - semaine_annee (1-52)
        - est_weekend (0/1)
        - jour_mois (1-31)
        """
        return [
            float(date_val.weekday()),
            float(date_val.month),
            float(date_val.isocalendar()[1]),
            1.0 if date_val.weekday() >= 5 else 0.0,
            float(date_val.day),
        ]

    def entrainer(
        self,
        historique: list[dict[str, Any]],
        min_points: int = 10,
    ) -> dict[str, Any]:
        """Entraîne le modèle sur l'historique d'achats.

        Args:
            historique: Liste de dicts avec 'date', 'article', 'quantite'
            min_points: Minimum de points pour entraîner

        Returns:
            Dict avec métriques d'entraînement
        """
        if len(historique) < min_points:
            logger.info(f"Pas assez de données ({len(historique)} < {min_points})")
            return {"trained": False, "reason": "insufficient_data"}

        try:
            from sklearn.ensemble import GradientBoostingRegressor
            from sklearn.preprocessing import StandardScaler

            # Préparer les données
            X = []
            y = []

            for item in historique:
                date_str = item.get("date", "")
                quantite = float(item.get("quantite", 0))
                article = item.get("article", "")

                if not date_str or quantite <= 0:
                    continue

                try:
                    if isinstance(date_str, str):
                        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    elif isinstance(date_str, datetime):
                        dt = date_str
                    else:
                        continue
                except ValueError:
                    continue

                features = self._extraire_features(dt)
                # Ajouter un hash de l'article comme feature
                article_hash = float(hash(article.lower()) % 1000) / 1000.0
                features.append(article_hash)

                X.append(features)
                y.append(quantite)
                self._articles_connus.add(article.lower())

            if len(X) < min_points:
                return {"trained": False, "reason": "insufficient_valid_data"}

            X_arr = np.array(X)
            y_arr = np.array(y)

            # Scaler
            self._scaler = StandardScaler()
            X_scaled = self._scaler.fit_transform(X_arr)

            # Entraîner
            self._modele = GradientBoostingRegressor(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
            )
            self._modele.fit(X_scaled, y_arr)

            # Score
            score = self._modele.score(X_scaled, y_arr)

            # Sauvegarder
            self._sauvegarder()

            logger.info(f"Modèle entraîné: R² = {score:.3f}, {len(X)} samples")
            return {
                "trained": True,
                "r2_score": round(score, 3),
                "n_samples": len(X),
                "n_articles": len(self._articles_connus),
            }

        except ImportError:
            logger.warning("scikit-learn non installé pour le modèle ML")
            return {"trained": False, "reason": "sklearn_not_installed"}
        except Exception as e:
            logger.error(f"Erreur entraînement: {e}")
            return {"trained": False, "reason": str(e)}

    def predire(
        self,
        article: str,
        horizon_jours: int = 7,
        date_depart: datetime | None = None,
    ) -> PredictionML:
        """Prédit la consommation d'un article.

        Args:
            article: Nom de l'article
            horizon_jours: Nombre de jours de prévision
            date_depart: Date de début (défaut: maintenant)

        Returns:
            PredictionML
        """
        date_depart = date_depart or datetime.now()

        if self._modele is None or self._scaler is None:
            # Fallback statistique
            return PredictionML(
                article=article,
                quantite_predite=0.0,
                confiance=0.0,
                methode="statistique",
                horizon_jours=horizon_jours,
            )

        try:
            # Prédire pour chaque jour de l'horizon
            predictions_jour = []
            article_hash = float(hash(article.lower()) % 1000) / 1000.0

            for j in range(horizon_jours):
                dt = date_depart + timedelta(days=j)
                features = self._extraire_features(dt)
                features.append(article_hash)
                x = np.array([features])
                x_scaled = self._scaler.transform(x)
                pred = max(0, self._modele.predict(x_scaled)[0])
                predictions_jour.append(pred)

            total = sum(predictions_jour)
            # Intervalle de confiance simplifié (±20%)
            ic_bas = total * 0.8
            ic_haut = total * 1.2

            confiance = min(1.0, 0.5 + len(self._articles_connus) / 100.0)
            if article.lower() not in self._articles_connus:
                confiance *= 0.5

            return PredictionML(
                article=article,
                quantite_predite=round(total, 2),
                intervalle_confiance=(round(ic_bas, 2), round(ic_haut, 2)),
                confiance=round(confiance, 2),
                methode="ml",
                horizon_jours=horizon_jours,
            )

        except Exception as e:
            logger.error(f"Erreur prédiction: {e}")
            return PredictionML(
                article=article,
                quantite_predite=0.0,
                confiance=0.0,
                methode="erreur",
                horizon_jours=horizon_jours,
            )
