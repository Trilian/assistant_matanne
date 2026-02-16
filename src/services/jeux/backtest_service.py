"""
Service de Backtesting pour la Loi des Séries.

Permet de tester la stratégie sur des données historiques:
- Paris sportifs: Vérifier si les marchés "en retard" finissent par sortir
- Loto: Vérifier si les numéros "en retard" finissent par sortir

⚠️ RAPPEL IMPORTANT: Le backtesting sur données historiques ne garantit
AUCUN résultat futur. Les jeux de hasard restent du hasard.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from src.services.jeux.series_service import (
    SEUIL_VALUE_ALERTE,
    SEUIL_VALUE_HAUTE,
    SeriesService,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


class ResultatPrediction(str, Enum):
    """Résultat d'une prédiction."""

    CORRECT = "correct"  # La prédiction s'est réalisée
    INCORRECT = "incorrect"  # La prédiction ne s'est pas réalisée
    EN_COURS = "en_cours"  # Pas encore de résultat


@dataclass
class Prediction:
    """Une prédiction basée sur la loi des séries."""

    identifiant: str  # Ex: "Ligue1_More_2_5" ou "Numero_7"
    type_jeu: str  # "paris" ou "loto"
    value_initiale: float
    serie_initiale: int
    frequence: float
    date_prediction: datetime
    seuil_utilise: float
    resultat: ResultatPrediction = ResultatPrediction.EN_COURS
    date_realisation: datetime | None = None
    tirages_avant_realisation: int | None = None

    @property
    def etait_opportunite(self) -> bool:
        """Était classée comme opportunité."""
        return self.value_initiale >= SEUIL_VALUE_ALERTE


@dataclass
class ResultatBacktest:
    """Résultat d'un backtest complet."""

    type_jeu: str
    periode_debut: datetime
    periode_fin: datetime
    nb_predictions: int
    nb_correctes: int
    nb_incorrectes: int
    nb_en_cours: int
    taux_reussite: float  # nb_correctes / (nb_correctes + nb_incorrectes)
    predictions: list[Prediction] = field(default_factory=list)

    # Métriques détaillées
    tirages_moyens_avant_realisation: float = 0.0
    value_moyenne_reussites: float = 0.0
    value_moyenne_echecs: float = 0.0

    # Avertissement
    avertissement: str = (
        "⚠️ Ces résultats sont basés sur des données HISTORIQUES. "
        "Ils ne garantissent AUCUN résultat futur. "
        "Les jeux de hasard restent du hasard."
    )


@dataclass
class StatistiquesBacktest:
    """Statistiques globales de backtesting."""

    total_backtests: int
    taux_reussite_global: float
    meilleur_seuil: float
    pire_seuil: float
    correlation_value_reussite: float  # -1 à 1


# ═══════════════════════════════════════════════════════════
# SERVICE BACKTESTING
# ═══════════════════════════════════════════════════════════


class BacktestService:
    """
    Service de backtesting pour la loi des séries.

    Permet de tester rétrospectivement si les opportunités
    détectées se sont réalisées dans les tirages/matchs suivants.

    ⚠️ IMPORTANT: Un bon taux de réussite historique ne garantit
    aucun résultat futur. Chaque événement est indépendant.
    """

    # Nombre max de tirages/matchs à attendre pour une réalisation
    MAX_TIRAGES_ATTENTE_LOTO = 50
    MAX_MATCHS_ATTENTE_PARIS = 30

    def __init__(self):
        """Initialise le service."""
        pass

    # ───────────────────────────────────────────────────────────────
    # BACKTESTING LOTO
    # ───────────────────────────────────────────────────────────────

    def backtester_loto(
        self,
        tirages_historiques: list[dict[str, Any]],
        seuil_value: float = SEUIL_VALUE_ALERTE,
        max_tirages_attente: int | None = None,
    ) -> ResultatBacktest:
        """
        Backteste la loi des séries sur l'historique Loto.

        Stratégie testée:
        1. Pour chaque tirage t, identifier les numéros "en retard"
        2. Vérifier si ces numéros sortent dans les N tirages suivants
        3. Calculer le taux de réussite

        Args:
            tirages_historiques: Liste des tirages (plus récent en premier)
            seuil_value: Seuil de value pour considérer un numéro "en retard"
            max_tirages_attente: Nombre max de tirages à attendre

        Returns:
            ResultatBacktest avec les statistiques
        """
        if max_tirages_attente is None:
            max_tirages_attente = self.MAX_TIRAGES_ATTENTE_LOTO

        if len(tirages_historiques) < 100:
            logger.warning("Historique trop court pour un backtest fiable")

        # Inverser pour avoir l'ordre chronologique
        tirages = list(reversed(tirages_historiques))
        predictions: list[Prediction] = []

        # Pour chaque point dans l'historique (sauf les derniers)
        for i in range(50, len(tirages) - max_tirages_attente):
            # Historique jusqu'à ce point
            historique_partiel = tirages[:i]

            # Calculer les numéros en retard à ce moment
            numeros_retard = self._calculer_numeros_retard_loto(historique_partiel, seuil_value)

            # Pour chaque numéro en retard
            for num_info in numeros_retard:
                # Vérifier s'il sort dans les tirages suivants
                tirages_suivants = tirages[i : i + max_tirages_attente]
                realisation = self._verifier_realisation_loto(num_info["numero"], tirages_suivants)

                prediction = Prediction(
                    identifiant=f"Numero_{num_info['numero']}",
                    type_jeu="loto",
                    value_initiale=num_info["value"],
                    serie_initiale=num_info["serie"],
                    frequence=num_info["frequence"],
                    date_prediction=historique_partiel[-1].get(
                        "date", datetime.now() - timedelta(days=i)
                    ),
                    seuil_utilise=seuil_value,
                    resultat=(
                        ResultatPrediction.CORRECT
                        if realisation["realise"]
                        else ResultatPrediction.INCORRECT
                    ),
                    tirages_avant_realisation=realisation.get("tirages"),
                )
                predictions.append(prediction)

        return self._calculer_resultat(predictions, "loto")

    def _calculer_numeros_retard_loto(
        self,
        tirages: list[dict[str, Any]],
        seuil_value: float,
    ) -> list[dict[str, Any]]:
        """Calcule les numéros en retard pour un historique donné."""
        # Simuler le calcul de séries pour chaque numéro
        numeros_retard = []
        nb_tirages = len(tirages)

        for numero in range(1, 50):  # 1-49 pour Loto
            # Compter dernière apparition
            serie = 0
            for t in reversed(tirages):
                numeros = t.get("numeros", []) or t.get("boules", [])
                if numero in numeros:
                    break
                serie += 1

            # Calculer fréquence
            nb_sorties = sum(
                1 for t in tirages if numero in (t.get("numeros", []) or t.get("boules", []))
            )
            frequence = nb_sorties / nb_tirages if nb_tirages > 0 else 0

            # Calculer value
            value = frequence * serie

            if value >= seuil_value:
                numeros_retard.append(
                    {
                        "numero": numero,
                        "value": value,
                        "serie": serie,
                        "frequence": frequence,
                    }
                )

        return numeros_retard

    def _verifier_realisation_loto(
        self,
        numero: int,
        tirages_suivants: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Vérifie si un numéro sort dans les tirages suivants."""
        for i, tirage in enumerate(tirages_suivants):
            numeros = tirage.get("numeros", []) or tirage.get("boules", [])
            if numero in numeros:
                return {"realise": True, "tirages": i + 1}

        return {"realise": False, "tirages": None}

    # ───────────────────────────────────────────────────────────────
    # BACKTESTING PARIS SPORTIFS
    # ───────────────────────────────────────────────────────────────

    def backtester_paris(
        self,
        matchs_historiques: list[dict[str, Any]],
        marche: str,
        seuil_value: float = SEUIL_VALUE_ALERTE,
        max_matchs_attente: int | None = None,
    ) -> ResultatBacktest:
        """
        Backteste la loi des séries sur l'historique Paris sportifs.

        Args:
            matchs_historiques: Liste des matchs avec résultats
            marche: Marché à tester (ex: "More_2_5", "BTTS_Yes")
            seuil_value: Seuil de value
            max_matchs_attente: Nombre max de matchs à attendre

        Returns:
            ResultatBacktest avec les statistiques
        """
        if max_matchs_attente is None:
            max_matchs_attente = self.MAX_MATCHS_ATTENTE_PARIS

        # Inverser pour ordre chronologique
        matchs = list(reversed(matchs_historiques))
        predictions: list[Prediction] = []

        # Pour chaque point dans l'historique
        for i in range(20, len(matchs) - max_matchs_attente):
            historique_partiel = matchs[:i]

            # Vérifier si le marché est "en retard" à ce moment
            stats = self._calculer_stats_marche(historique_partiel, marche)

            if stats["value"] >= seuil_value:
                # Vérifier réalisation
                matchs_suivants = matchs[i : i + max_matchs_attente]
                realisation = self._verifier_realisation_paris(marche, matchs_suivants)

                prediction = Prediction(
                    identifiant=f"Paris_{marche}",
                    type_jeu="paris",
                    value_initiale=stats["value"],
                    serie_initiale=stats["serie"],
                    frequence=stats["frequence"],
                    date_prediction=historique_partiel[-1].get(
                        "date", datetime.now() - timedelta(days=i)
                    ),
                    seuil_utilise=seuil_value,
                    resultat=(
                        ResultatPrediction.CORRECT
                        if realisation["realise"]
                        else ResultatPrediction.INCORRECT
                    ),
                    tirages_avant_realisation=realisation.get("matchs"),
                )
                predictions.append(prediction)

        return self._calculer_resultat(predictions, "paris")

    def _calculer_stats_marche(
        self,
        matchs: list[dict[str, Any]],
        marche: str,
    ) -> dict[str, Any]:
        """Calcule les statistiques pour un marché donné."""
        nb_matchs = len(matchs)
        if nb_matchs == 0:
            return {"value": 0, "serie": 0, "frequence": 0}

        # Compter série actuelle (matchs sans réalisation)
        serie = 0
        for match in reversed(matchs):
            if self._marche_realise(match, marche):
                break
            serie += 1

        # Compter fréquence
        nb_realisations = sum(1 for m in matchs if self._marche_realise(m, marche))
        frequence = nb_realisations / nb_matchs

        # Calculer value
        value = frequence * serie

        return {"value": value, "serie": serie, "frequence": frequence}

    def _marche_realise(self, match: dict[str, Any], marche: str) -> bool:
        """Vérifie si un marché s'est réalisé pour un match."""
        score_domicile = match.get("score_domicile", 0)
        score_exterieur = match.get("score_exterieur", 0)
        total_buts = score_domicile + score_exterieur

        marche_lower = marche.lower()

        if "more_2_5" in marche_lower or "plus_2_5" in marche_lower:
            return total_buts > 2.5
        elif "less_2_5" in marche_lower or "moins_2_5" in marche_lower:
            return total_buts < 2.5
        elif "btts_yes" in marche_lower:
            return score_domicile > 0 and score_exterieur > 0
        elif "btts_no" in marche_lower:
            return score_domicile == 0 or score_exterieur == 0
        elif marche_lower == "1":  # Victoire domicile
            return score_domicile > score_exterieur
        elif marche_lower == "x":  # Nul
            return score_domicile == score_exterieur
        elif marche_lower == "2":  # Victoire extérieur
            return score_exterieur > score_domicile

        return False

    def _verifier_realisation_paris(
        self,
        marche: str,
        matchs_suivants: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Vérifie si un marché se réalise dans les matchs suivants."""
        for i, match in enumerate(matchs_suivants):
            if self._marche_realise(match, marche):
                return {"realise": True, "matchs": i + 1}

        return {"realise": False, "matchs": None}

    # ───────────────────────────────────────────────────────────────
    # CALCUL DES RÉSULTATS
    # ───────────────────────────────────────────────────────────────

    def _calculer_resultat(
        self,
        predictions: list[Prediction],
        type_jeu: str,
    ) -> ResultatBacktest:
        """Calcule les statistiques à partir des prédictions."""
        if not predictions:
            return ResultatBacktest(
                type_jeu=type_jeu,
                periode_debut=datetime.now(),
                periode_fin=datetime.now(),
                nb_predictions=0,
                nb_correctes=0,
                nb_incorrectes=0,
                nb_en_cours=0,
                taux_reussite=0.0,
            )

        nb_correctes = sum(1 for p in predictions if p.resultat == ResultatPrediction.CORRECT)
        nb_incorrectes = sum(1 for p in predictions if p.resultat == ResultatPrediction.INCORRECT)
        nb_en_cours = sum(1 for p in predictions if p.resultat == ResultatPrediction.EN_COURS)

        total_termines = nb_correctes + nb_incorrectes
        taux_reussite = nb_correctes / total_termines if total_termines > 0 else 0.0

        # Métriques détaillées
        reussites = [p for p in predictions if p.resultat == ResultatPrediction.CORRECT]
        echecs = [p for p in predictions if p.resultat == ResultatPrediction.INCORRECT]

        tirages_moyens = 0.0
        if reussites:
            tirages_valides = [
                p.tirages_avant_realisation
                for p in reussites
                if p.tirages_avant_realisation is not None
            ]
            if tirages_valides:
                tirages_moyens = sum(tirages_valides) / len(tirages_valides)

        value_moyenne_reussites = (
            sum(p.value_initiale for p in reussites) / len(reussites) if reussites else 0.0
        )
        value_moyenne_echecs = (
            sum(p.value_initiale for p in echecs) / len(echecs) if echecs else 0.0
        )

        return ResultatBacktest(
            type_jeu=type_jeu,
            periode_debut=min(p.date_prediction for p in predictions),
            periode_fin=max(p.date_prediction for p in predictions),
            nb_predictions=len(predictions),
            nb_correctes=nb_correctes,
            nb_incorrectes=nb_incorrectes,
            nb_en_cours=nb_en_cours,
            taux_reussite=taux_reussite,
            predictions=predictions,
            tirages_moyens_avant_realisation=tirages_moyens,
            value_moyenne_reussites=value_moyenne_reussites,
            value_moyenne_echecs=value_moyenne_echecs,
        )

    # ───────────────────────────────────────────────────────────────
    # ANALYSE COMPARATIVE
    # ───────────────────────────────────────────────────────────────

    def comparer_seuils(
        self,
        tirages_ou_matchs: list[dict[str, Any]],
        type_jeu: str,
        seuils: list[float] | None = None,
        marche: str | None = None,
    ) -> list[ResultatBacktest]:
        """
        Compare les performances de différents seuils de value.

        Args:
            tirages_ou_matchs: Données historiques
            type_jeu: "loto" ou "paris"
            seuils: Liste de seuils à tester
            marche: Marché à tester (pour paris)

        Returns:
            Liste de ResultatBacktest pour chaque seuil
        """
        if seuils is None:
            seuils = [1.5, 2.0, 2.5, 3.0, 3.5]

        resultats = []

        for seuil in seuils:
            if type_jeu == "loto":
                resultat = self.backtester_loto(tirages_ou_matchs, seuil_value=seuil)
            elif type_jeu == "paris" and marche:
                resultat = self.backtester_paris(
                    tirages_ou_matchs, marche=marche, seuil_value=seuil
                )
            else:
                continue

            resultats.append(resultat)
            logger.info(
                f"Seuil {seuil}: {resultat.taux_reussite:.1%} "
                f"({resultat.nb_correctes}/{resultat.nb_predictions})"
            )

        return resultats

    def generer_rapport(self, resultat: ResultatBacktest) -> str:
        """
        Génère un rapport textuel du backtest.

        Args:
            resultat: Résultat du backtest

        Returns:
            Rapport formaté
        """
        lignes = [
            "=" * 60,
            f"RAPPORT DE BACKTEST - {resultat.type_jeu.upper()}",
            "=" * 60,
            "",
            f"Période: {resultat.periode_debut.strftime('%d/%m/%Y')} - "
            f"{resultat.periode_fin.strftime('%d/%m/%Y')}",
            "",
            "RÉSULTATS:",
            f"  - Prédictions totales: {resultat.nb_predictions}",
            f"  - Correctes: {resultat.nb_correctes} ({resultat.taux_reussite:.1%})",
            f"  - Incorrectes: {resultat.nb_incorrectes}",
            "",
            "MÉTRIQUES:",
            f"  - Tirages/matchs moyens avant réalisation: {resultat.tirages_moyens_avant_realisation:.1f}",
            f"  - Value moyenne des réussites: {resultat.value_moyenne_reussites:.2f}",
            f"  - Value moyenne des échecs: {resultat.value_moyenne_echecs:.2f}",
            "",
            "=" * 60,
            resultat.avertissement,
            "=" * 60,
        ]

        return "\n".join(lignes)


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


_backtest_service_instance: BacktestService | None = None


def get_backtest_service() -> BacktestService:
    """Factory pour obtenir le service de backtesting (singleton)."""
    global _backtest_service_instance
    if _backtest_service_instance is None:
        _backtest_service_instance = BacktestService()
    return _backtest_service_instance


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════

__all__ = [
    # Classes
    "BacktestService",
    "ResultatBacktest",
    "Prediction",
    "ResultatPrediction",
    "StatistiquesBacktest",
    # Factory
    "get_backtest_service",
]
