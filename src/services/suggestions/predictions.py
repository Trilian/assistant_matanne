"""
Service Prévisions ML pour Inventaire
Analyse historique + prédictions de consommation
"""

import logging
from datetime import datetime
from statistics import mean, stdev
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class PredictionArticle(BaseModel):
    """Prédiction pour un article"""

    article_id: int
    ingredient_id: int
    nom: str
    quantite_actuelle: float
    quantite_predite_semaine: float
    quantite_predite_mois: float
    taux_consommation_moyen: float  # Par jour
    tendance: str = "stable"  # stable, croissante, decroissante
    confiance: float = 0.0  # 0-1
    risque_rupture_mois: bool = False
    jours_avant_rupture: int | None = None


class AnalysePrediction(BaseModel):
    """Analyse complète des prédictions"""

    date_analyse: datetime = Field(default_factory=datetime.utcnow)
    nombre_articles: int
    articles_en_rupture_risque: list[str]
    articles_croissance: list[str]
    articles_decroissance: list[str]
    consommation_moyenne_globale: float
    consommation_min: float = 0.0
    consommation_max: float = 0.0
    nb_articles_croissance: int = 0
    nb_articles_decroissance: int = 0
    nb_articles_stables: int = 0
    tendance_globale: str


class PredictionService:
    """Service pour prédictions ML basiques"""

    def __init__(self):
        self.min_data_points = 3  # Min historique pour prédire

    def analyser_historique_article(
        self,
        article_id: int,
        historique: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Analyse l'historique d'un article pour détecter patterns.

        Args:
            article_id: ID de l'article
            historique: Liste des modifications historiques

        Returns:
            Dict avec taux consommation, tendance, etc
        """
        if not historique or len(historique) < self.min_data_points:
            return None

        # Filtre les modifications pour cet article
        modifications = [
            h
            for h in historique
            if h.get("article_id") == article_id
            and h.get("type_modification") == "modification_quantite"
        ]

        if len(modifications) < self.min_data_points:
            return None

        # Extrait les changements de quantité
        changes = []
        for mod in sorted(modifications, key=lambda x: x.get("date_modification", "")):
            qty_avant = mod.get("quantite_avant", 0)
            qty_apres = mod.get("quantite_apres", 0)
            change = qty_avant - qty_apres  # Positif = consommation

            if change > 0:  # Seulement consommations
                changes.append(
                    {
                        "change": change,
                        "date": mod.get("date_modification"),
                    }
                )

        if not changes:
            return None

        # Calcule statistiques
        changements = [c["change"] for c in changes]
        taux_moyen = mean(changements) if changements else 0
        variance = stdev(changements) if len(changements) > 1 else 0

        # Détecte tendance (croissance/décroissance)
        if len(changements) >= 2:
            premiers = changements[: len(changements) // 2]
            derniers = changements[len(changements) // 2 :]
            tendance_value = mean(derniers) - mean(premiers)

            if tendance_value > variance * 0.1:
                tendance = "croissante"
            elif tendance_value < -variance * 0.1:
                tendance = "decroissante"
            else:
                tendance = "stable"
        else:
            tendance = "stable"

        return {
            "taux_consommation_moyen": taux_moyen,  # Par jour (environ)
            "variance": variance,
            "nombre_modifications": len(changements),
            "tendance": tendance,
            "confiance": min(1.0, len(changements) / 10.0),  # Max confiance à 10+ points
        }

    def predire_quantite(
        self,
        quantite_actuelle: float,
        taux_consommation: float,
        jours: int = 30,
    ) -> float:
        """Prédit la quantité future.

        Args:
            quantite_actuelle: Stock actuel
            taux_consommation: Consommation/jour moyenne
            jours: Nombre de jours à prédire

        Returns:
            Quantité estimée dans N jours
        """
        consommation_projetee = taux_consommation * jours
        quantite_predite = quantite_actuelle - consommation_projetee

        return max(0, quantite_predite)  # Pas de quantité négative

    def detecter_rupture_risque(
        self,
        quantite_actuelle: float,
        quantite_min: float,
        taux_consommation: float,
    ) -> tuple[bool, int | None]:
        """Détecte si rupture de stock risquée.

        Args:
            quantite_actuelle: Stock actuel
            quantite_min: Seuil minimum
            taux_consommation: Consommation/jour

        Returns:
            (risque, jours_avant_rupture)
        """
        if taux_consommation <= 0:
            return False, None

        jours_avant_rupture = (quantite_actuelle - quantite_min) / taux_consommation

        # Risque si < 14 jours (2 semaines)
        risque = jours_avant_rupture < 14

        return risque, int(jours_avant_rupture) if jours_avant_rupture > 0 else 0

    def generer_predictions(
        self,
        articles: list[dict[str, Any]],
        historique_complet: list[dict[str, Any]],
    ) -> list[PredictionArticle]:
        """Génère prédictions pour tous les articles.

        Args:
            articles: Liste des articles actuels
            historique_complet: Historique complet

        Returns:
            Liste de prédictions
        """
        predictions = []

        for article in articles:
            article_id = article["id"]
            ingredient_id = article["ingredient_id"]
            nom = article["ingredient_nom"]
            quantite_actuelle = article["quantite"]
            quantite_min = article.get("quantite_min", 0) or 0

            # Analyse historique
            analyse = self.analyser_historique_article(article_id, historique_complet)

            if analyse:
                # Historique disponible
                taux = analyse["taux_consommation_moyen"]
                tendance = analyse["tendance"]
                confiance = analyse["confiance"]
            else:
                # Pas d'historique - utiliser valeurs par défaut
                # Assumer consommation modérée
                taux = max(0.5, quantite_min * 0.1) if quantite_min > 0 else 0.5
                tendance = "stable"
                confiance = 0.3

            # Prédictions
            qty_semaine = self.predire_quantite(quantite_actuelle, taux, 7)
            qty_mois = self.predire_quantite(quantite_actuelle, taux, 30)

            # Risque rupture
            risque, jours = self.detecter_rupture_risque(quantite_actuelle, quantite_min, taux)

            prediction = PredictionArticle(
                article_id=article_id,
                ingredient_id=ingredient_id,
                nom=nom,
                quantite_actuelle=quantite_actuelle,
                quantite_predite_semaine=qty_semaine,
                quantite_predite_mois=qty_mois,
                taux_consommation_moyen=taux,
                tendance=tendance,
                confiance=confiance,
                risque_rupture_mois=risque,
                jours_avant_rupture=jours,
            )

            predictions.append(prediction)

        return predictions

    def obtenir_analyse_globale(
        self,
        predictions: list[PredictionArticle],
    ) -> AnalysePrediction:
        """Obtient analyse globale des prédictions.

        Args:
            predictions: Liste de prédictions

        Returns:
            Analyse globale
        """
        articles_rupture = [p.nom for p in predictions if p.risque_rupture_mois]
        articles_croissance = [p.nom for p in predictions if p.tendance == "croissante"]
        articles_decroissance = [p.nom for p in predictions if p.tendance == "decroissante"]

        consommation_globale = (
            mean([p.taux_consommation_moyen for p in predictions]) if predictions else 0
        )

        # Tendance globale
        tendances = [p.tendance for p in predictions]
        croissantes = len([t for t in tendances if t == "croissante"])
        decroissantes = len([t for t in tendances if t == "decroissante"])
        stables = len(predictions) - croissantes - decroissantes

        if croissantes > decroissantes * 1.5:
            tendance_globale = "croissante"
        elif decroissantes > croissantes * 1.5:
            tendance_globale = "decroissante"
        else:
            tendance_globale = "stable"

        # Consommations min/max
        taux_consommation = [
            p.taux_consommation_moyen for p in predictions if p.taux_consommation_moyen > 0
        ]
        consommation_min = min(taux_consommation) if taux_consommation else 0.0
        consommation_max = max(taux_consommation) if taux_consommation else 0.0

        return AnalysePrediction(
            nombre_articles=len(predictions),
            articles_en_rupture_risque=articles_rupture,
            articles_croissance=articles_croissance,
            articles_decroissance=articles_decroissance,
            consommation_moyenne_globale=consommation_globale,
            consommation_min=consommation_min,
            consommation_max=consommation_max,
            nb_articles_croissance=croissantes,
            nb_articles_decroissance=decroissantes,
            nb_articles_stables=stables,
            tendance_globale=tendance_globale,
        )

    def generer_recommandations(
        self,
        predictions: list[PredictionArticle],
    ) -> list[dict[str, Any]]:
        """Génère recommandations d'achat.

        Args:
            predictions: Liste de prédictions

        Returns:
            Liste de recommandations
        """
        recommandations = []

        for pred in predictions:
            # Critique: risque rupture dans 2 semaines
            if (
                pred.risque_rupture_mois
                and pred.jours_avant_rupture
                and pred.jours_avant_rupture < 14
            ):
                quantite_recommandee = pred.taux_consommation_moyen * 30  # 1 mois
                recommandations.append(
                    {
                        "article": pred.nom,
                        "priorite": "CRITIQUE",
                        "raison": f"Rupture risquée dans {pred.jours_avant_rupture} jours",
                        "quantite_acheter": quantite_recommandee,
                        "icone": "🚨",
                    }
                )

            # Croissance: consommation augmente
            elif pred.tendance == "croissante" and pred.confiance > 0.5:
                quantite_recommandee = pred.taux_consommation_moyen * 45  # 1.5 mois
                recommandations.append(
                    {
                        "article": pred.nom,
                        "priorite": "HAUTE",
                        "raison": "Consommation en hausse, anticiper",
                        "quantite_acheter": quantite_recommandee,
                        "icone": "📈",
                    }
                )

        # Trier par priorité
        priorite_ordre = {"CRITIQUE": 0, "HAUTE": 1}
        recommandations.sort(key=lambda x: priorite_ordre.get(x["priorite"], 2))

        return recommandations[:10]  # Top 10


# Singleton global
_prediction_service: PredictionService | None = None


def obtenir_service_predictions() -> PredictionService:
    """Obtient l'instance singleton"""
    global _prediction_service

    if _prediction_service is None:
        _prediction_service = PredictionService()
        logger.info("✅ Service de prédictions ML initialisé")

    return _prediction_service
