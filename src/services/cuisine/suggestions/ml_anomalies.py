"""
Modèle ML — Détection d'anomalies de dépenses.

Utilise un Isolation Forest pour identifier les transactions
inhabituelles par montant, catégorie et pattern temporel.

Usage:
    from src.services.cuisine.suggestions.ml_anomalies import DetecteurAnomaliesDepenses

    detecteur = DetecteurAnomaliesDepenses()
    detecteur.entrainer(historique_depenses)
    anomalies = detecteur.detecter(depenses_recentes)
"""

from __future__ import annotations

import logging
import pickle
from datetime import datetime
from typing import Any

import numpy as np

from .ml_schemas import MODELS_DIR, AnomalieDepense

logger = logging.getLogger(__name__)

__all__ = ["DetecteurAnomaliesDepenses"]


class DetecteurAnomaliesDepenses:
    """Détecte les dépenses anormales via Isolation Forest.

    Identifie les transactions inhabituelles par montant, catégorie
    et pattern temporel.
    """

    def __init__(self):
        self._modele = None
        self._scaler = None
        self._categories: list[str] = []
        self._modele_path = MODELS_DIR / "anomalies_model.pkl"
        self._charger()

    def _charger(self) -> bool:
        """Charge le modèle sérialisé."""
        if self._modele_path.exists():
            try:
                with open(self._modele_path, "rb") as f:
                    data = pickle.load(f)  # noqa: S301
                self._modele = data.get("modele")
                self._scaler = data.get("scaler")
                self._categories = data.get("categories", [])
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
                        "categories": self._categories,
                    },
                    f,
                )
        except Exception as e:
            logger.warning(f"Erreur sauvegarde: {e}")

    def _preparer_features(self, depense: dict[str, Any]) -> list[float]:
        """Extrait les features d'une dépense.

        Features:
        - montant
        - jour_semaine
        - mois
        - categorie_index
        - est_weekend
        """
        montant = float(depense.get("montant", 0))
        date_str = depense.get("date", "")
        categorie = depense.get("categorie", "Autre")

        try:
            if isinstance(date_str, str):
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
            elif isinstance(date_str, datetime):
                dt = date_str
            else:
                dt = datetime.now()
        except ValueError:
            dt = datetime.now()

        cat_idx = (
            self._categories.index(categorie)
            if categorie in self._categories
            else len(self._categories)
        )

        return [
            montant,
            float(dt.weekday()),
            float(dt.month),
            float(cat_idx),
            1.0 if dt.weekday() >= 5 else 0.0,
        ]

    def entrainer(
        self,
        historique_depenses: list[dict[str, Any]],
        contamination: float = 0.05,
    ) -> dict[str, Any]:
        """Entraîne le détecteur d'anomalies.

        Args:
            historique_depenses: Liste de dicts avec 'montant', 'date', 'categorie'
            contamination: Proportion attendue d'anomalies (0-0.5)

        Returns:
            Dict avec métriques
        """
        if len(historique_depenses) < 20:
            return {"trained": False, "reason": "insufficient_data"}

        try:
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler

            # Collecter les catégories
            self._categories = sorted(set(d.get("categorie", "Autre") for d in historique_depenses))

            X = [self._preparer_features(d) for d in historique_depenses]
            X_arr = np.array(X)

            self._scaler = StandardScaler()
            X_scaled = self._scaler.fit_transform(X_arr)

            self._modele = IsolationForest(
                n_estimators=100,
                contamination=contamination,
                random_state=42,
            )
            self._modele.fit(X_scaled)

            self._sauvegarder()

            # Compter les anomalies d'entraînement
            preds = self._modele.predict(X_scaled)
            n_anomalies = int(np.sum(preds == -1))

            logger.info(
                f"Détecteur anomalies entraîné: {len(X)} samples, "
                f"{n_anomalies} anomalies ({n_anomalies / len(X) * 100:.1f}%)"
            )

            return {
                "trained": True,
                "n_samples": len(X),
                "n_anomalies_train": n_anomalies,
                "n_categories": len(self._categories),
            }

        except ImportError:
            return {"trained": False, "reason": "sklearn_not_installed"}
        except Exception as e:
            logger.error(f"Erreur entraînement anomalies: {e}")
            return {"trained": False, "reason": str(e)}

    def detecter(
        self,
        depenses: list[dict[str, Any]],
    ) -> list[AnomalieDepense]:
        """Détecte les anomalies dans des dépenses.

        Args:
            depenses: Liste de dépenses à vérifier

        Returns:
            Liste des anomalies détectées
        """
        if not self._modele or not self._scaler:
            return []

        anomalies = []

        try:
            X = [self._preparer_features(d) for d in depenses]
            X_arr = np.array(X)
            X_scaled = self._scaler.transform(X_arr)

            predictions = self._modele.predict(X_scaled)
            scores = self._modele.decision_function(X_scaled)

            for i, (pred, score) in enumerate(zip(predictions, scores, strict=False)):
                if pred == -1:  # Anomalie
                    d = depenses[i]
                    montant = float(d.get("montant", 0))

                    # Déterminer la raison
                    raison = self._analyser_raison(d, score)

                    anomalies.append(
                        AnomalieDepense(
                            description=d.get("description", "Dépense"),
                            montant=montant,
                            categorie=d.get("categorie", "Autre"),
                            date=str(d.get("date", "")),
                            score_anomalie=round(float(score), 3),
                            raison=raison,
                        )
                    )

        except Exception as e:
            logger.error(f"Erreur détection anomalies: {e}")

        return sorted(anomalies, key=lambda a: a.score_anomalie)

    def _analyser_raison(self, depense: dict, score: float) -> str:
        """Analyse la raison probable de l'anomalie."""
        montant = float(depense.get("montant", 0))
        if score < -0.3:
            return f"Montant très inhabituel ({montant:.2f}€)"
        elif score < -0.15:
            return f"Montant inhabituel pour la catégorie ({montant:.2f}€)"
        else:
            return "Pattern de dépense atypique"
