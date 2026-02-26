"""
Modèle ML — Score de satisfaction des repas.

Utilise un RandomForestRegressor pour prédire un score 0-5 basé sur:
- Type de repas (déjeuner, dîner)
- Nombre d'ingrédients
- Temps de préparation
- Catégorie (rapide, élaboré, etc.)
- Jour de la semaine

Usage:
    from src.services.cuisine.suggestions.ml_satisfaction import ScoreSatisfactionRepas

    scorer = ScoreSatisfactionRepas()
    scorer.entrainer(historique_repas)
    score = scorer.predire(recette_features)
"""

from __future__ import annotations

import logging
import pickle
from datetime import datetime
from statistics import mean
from typing import Any

import numpy as np

from .ml_schemas import MODELS_DIR, ScoreRepas

logger = logging.getLogger(__name__)

__all__ = ["ScoreSatisfactionRepas"]


class ScoreSatisfactionRepas:
    """Prédit le score de satisfaction d'un repas.

    Utilise RandomForest pour prédire un score 0-5 basé sur:
    - Type de repas (déjeuner, dîner)
    - Nombre d'ingrédients
    - Temps de préparation
    - Catégorie (rapide, élaboré, etc.)
    - Jour de la semaine
    """

    def __init__(self):
        self._modele = None
        self._scaler = None
        self._categories_recettes: list[str] = []
        self._modele_path = MODELS_DIR / "satisfaction_model.pkl"
        self._charger()

    def _charger(self) -> bool:
        """Charge le modèle sérialisé."""
        if self._modele_path.exists():
            try:
                with open(self._modele_path, "rb") as f:
                    data = pickle.load(f)  # noqa: S301
                self._modele = data.get("modele")
                self._scaler = data.get("scaler")
                self._categories_recettes = data.get("categories", [])
                return True
            except Exception:
                pass
        return False

    def _sauvegarder(self) -> None:
        """Sauvegarde le modèle."""
        try:
            with open(self._modele_path, "wb") as f:
                pickle.dump(
                    {
                        "modele": self._modele,
                        "scaler": self._scaler,
                        "categories": self._categories_recettes,
                    },
                    f,
                )
        except Exception as e:
            logger.warning(f"Erreur sauvegarde: {e}")

    def _preparer_features(self, recette: dict[str, Any]) -> list[float]:
        """Extrait les features d'une recette.

        Features:
        - nb_ingredients
        - temps_preparation (min)
        - temps_cuisson (min)
        - categorie_index
        - jour_semaine
        - est_weekend
        - nb_personnes
        """
        nb_ingredients = float(recette.get("nb_ingredients", 5))
        temps_prep = float(recette.get("temps_preparation", 30))
        temps_cuisson = float(recette.get("temps_cuisson", 30))
        categorie = recette.get("categorie", "Autre")
        nb_personnes = float(recette.get("nb_personnes", 4))

        # Date (si disponible)
        date_str = recette.get("date", "")
        try:
            if isinstance(date_str, str) and date_str:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            elif isinstance(date_str, datetime):
                dt = date_str
            else:
                dt = datetime.now()
        except ValueError:
            dt = datetime.now()

        cat_idx = (
            self._categories_recettes.index(categorie)
            if categorie in self._categories_recettes
            else len(self._categories_recettes)
        )

        return [
            nb_ingredients,
            temps_prep,
            temps_cuisson,
            float(cat_idx),
            float(dt.weekday()),
            1.0 if dt.weekday() >= 5 else 0.0,
            nb_personnes,
        ]

    def entrainer(
        self,
        historique_repas: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Entraîne le modèle de satisfaction.

        Args:
            historique_repas: Liste avec features + 'note' (0-5)

        Returns:
            Métriques d'entraînement
        """
        if len(historique_repas) < 15:
            return {"trained": False, "reason": "insufficient_data"}

        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.preprocessing import StandardScaler

            self._categories_recettes = sorted(
                set(r.get("categorie", "Autre") for r in historique_repas)
            )

            X = []
            y = []
            for repas in historique_repas:
                note = float(repas.get("note", 0))
                if 0 <= note <= 5:
                    X.append(self._preparer_features(repas))
                    y.append(note)

            if len(X) < 10:
                return {"trained": False, "reason": "insufficient_rated_data"}

            X_arr = np.array(X)
            y_arr = np.array(y)

            self._scaler = StandardScaler()
            X_scaled = self._scaler.fit_transform(X_arr)

            self._modele = RandomForestRegressor(
                n_estimators=50,
                max_depth=6,
                random_state=42,
            )
            self._modele.fit(X_scaled, y_arr)

            score = self._modele.score(X_scaled, y_arr)

            self._sauvegarder()

            logger.info(f"Modèle satisfaction entraîné: R² = {score:.3f}")
            return {
                "trained": True,
                "r2_score": round(score, 3),
                "n_samples": len(X),
                "note_moyenne": round(mean(y), 2),
            }

        except ImportError:
            return {"trained": False, "reason": "sklearn_not_installed"}
        except Exception as e:
            logger.error(f"Erreur entraînement satisfaction: {e}")
            return {"trained": False, "reason": str(e)}

    def predire(
        self,
        recette: dict[str, Any],
    ) -> ScoreRepas:
        """Prédit le score de satisfaction d'une recette.

        Args:
            recette: Dict avec features de la recette

        Returns:
            ScoreRepas
        """
        nom = recette.get("nom", "Recette")

        if not self._modele or not self._scaler:
            return ScoreRepas(recette=nom, score_predit=3.0)

        try:
            features = self._preparer_features(recette)
            X = np.array([features])
            X_scaled = self._scaler.transform(X)
            score = float(self._modele.predict(X_scaled)[0])
            score = max(0.0, min(5.0, score))

            # Analyser les facteurs
            facteurs_pos = []
            facteurs_neg = []

            temps_total = float(recette.get("temps_preparation", 30)) + float(
                recette.get("temps_cuisson", 30)
            )
            if temps_total <= 30:
                facteurs_pos.append("Préparation rapide")
            elif temps_total > 90:
                facteurs_neg.append("Temps de préparation long")

            nb_ing = int(recette.get("nb_ingredients", 5))
            if nb_ing <= 5:
                facteurs_pos.append("Peu d'ingrédients")
            elif nb_ing > 12:
                facteurs_neg.append("Beaucoup d'ingrédients")

            if features[5] == 1.0:  # Weekend
                facteurs_pos.append("Weekend (plus de temps)")

            return ScoreRepas(
                recette=nom,
                score_predit=round(score, 1),
                facteurs_positifs=facteurs_pos,
                facteurs_negatifs=facteurs_neg,
            )

        except Exception as e:
            logger.error(f"Erreur prédiction satisfaction: {e}")
            return ScoreRepas(recette=nom, score_predit=3.0)
