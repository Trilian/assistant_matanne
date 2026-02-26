"""
Module ML Prédictif — Innovation 3.3.

Modèles scikit-learn pour :
- Prédiction de consommation hebdomadaire (régression)
- Détection d'anomalies de dépenses (Isolation Forest)
- Score de satisfaction des repas (classification)

Compatible Streamlit Cloud (scikit-learn est pur Python/Cython).

Usage:
    from src.services.cuisine.suggestions.ml_predictions import (
        ModeleConsommationML,
        DetecteurAnomaliesDepenses,
        ScoreSatisfactionRepas,
        obtenir_ml_predictions,
    )

    # Prédiction consommation
    modele = ModeleConsommationML()
    modele.entrainer(historique_achats)
    prediction = modele.predire("tomates", horizon_jours=7)

    # Anomalies dépenses
    detecteur = DetecteurAnomaliesDepenses()
    detecteur.entrainer(historique_depenses)
    anomalies = detecteur.detecter(depenses_recentes)

    # Score satisfaction
    scorer = ScoreSatisfactionRepas()
    scorer.entrainer(historique_repas)
    score = scorer.predire(recette_features)
"""

from __future__ import annotations

import logging
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

__all__ = [
    "ModeleConsommationML",
    "DetecteurAnomaliesDepenses",
    "ScoreSatisfactionRepas",
    "PredictionML",
    "AnomalieDepense",
    "obtenir_ml_predictions",
]

# Répertoire pour les modèles sérialisés
MODELS_DIR = Path("data/ml_models")
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════
# SCHEMAS
# ═══════════════════════════════════════════════════════════


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


# ═══════════════════════════════════════════════════════════
# MODÈLE 1: Prédiction de Consommation
# ═══════════════════════════════════════════════════════════


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
                    data = pickle.load(f)
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


# ═══════════════════════════════════════════════════════════
# MODÈLE 2: Détection d'Anomalies de Dépenses
# ═══════════════════════════════════════════════════════════


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
                    data = pickle.load(f)
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
                f"{n_anomalies} anomalies ({n_anomalies/len(X)*100:.1f}%)"
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


# ═══════════════════════════════════════════════════════════
# MODÈLE 3: Score de Satisfaction des Repas
# ═══════════════════════════════════════════════════════════


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
                    data = pickle.load(f)
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


# ═══════════════════════════════════════════════════════════
# SERVICE UNIFIÉ
# ═══════════════════════════════════════════════════════════


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
            "consommation": self.consommation._modele is not None,
            "anomalies": self.anomalies._modele is not None,
            "satisfaction": self.satisfaction._modele is not None,
        }


# ═══════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════

from src.services.core.registry import service_factory


@service_factory("ml_predictions", tags={"cuisine", "ia", "ml"})
def obtenir_ml_predictions() -> MLPredictionService:
    """Obtient le service ML prédictif (thread-safe via registre)."""
    return MLPredictionService()
