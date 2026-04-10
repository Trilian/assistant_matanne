"""
Service d'analyse des patterns statistiques pour la détection de biais cognitifs.

Implémente des tests statistiques rigoureux pour :
- Régression vers la moyenne (z-score)
- Hot hand fallacy (runs test)
- Gambler's fallacy (test d'indépendance Chi-square)

Tous les tests suivent le principe que chaque événement est statistiquement indépendant.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import numpy as np
from scipy import stats
from sqlalchemy.orm import Session

from src.core.decorators import avec_session_db
from src.core.exceptions import ErreurBaseDeDonnees
from src.core.logging import logger
from src.core.models import Match, PariSportif


@dataclass
class ResultatTest:
    """Résultat d'un test statistique."""

    alerte: bool
    severite: str  # "faible", "moyenne", "elevee"
    message: str
    details: dict[str, Any]
    type_pattern: str  # "regression_moyenne", "hot_hand", "gamblers_fallacy"


class SeriesStatistiquesService:
    """
    Service d'analyse des patterns statistiques dans les paris sportifs.

    Détecte les biais cognitifs en appliquant des tests statistiques rigoureux.
    """

    def __init__(self, db: Session):
        self.db = db

    def test_regression_moyenne(
        self, paris: list[PariSportif], seuil_z: float = 2.0
    ) -> ResultatTest:
        """
        Test de régression vers la moyenne via z-score.

        Détecte si une série de gains/pertes anormale qui suggère un retour vers
        la moyenne statistique. Un z-score >2.0 indique une anomalie statistique.

        Attention : Ce n'est PAS une prédiction. Chaque pari reste indépendant.
        Le z-score mesure uniquement l'écart par rapport à la distribution normale.

        Args:
            paris: Liste des paris récents (min 10 recommandé)
            seuil_z: Seuil du z-score pour déclencher alerte (défaut 2.0 = 95% confiance)

        Returns:
            ResultatTest avec alerte si z-score dépasse seuil
        """
        if len(paris) < 10:
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Pas assez de paris pour analyse statistique (min 10 requis)",
                details={"nb_paris": len(paris), "z_score": None},
                type_pattern="regression_moyenne",
            )

        # Calculer gains/pertes (profit = gain - mise)
        profits = []
        for pari in paris:
            if pari.statut == "gagne":
                profit = (pari.gain or 0) - pari.mise
            elif pari.statut == "perdu":
                profit = -pari.mise
            else:
                continue  # Ignorer paris en attente

            profits.append(float(profit))

        if len(profits) < 10:
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Pas assez de paris terminés pour analyse",
                details={"nb_paris_termines": len(profits)},
                type_pattern="regression_moyenne",
            )

        # Calculer statistiques
        moyenne = np.mean(profits)
        ecart_type = np.std(profits, ddof=1)

        if ecart_type == 0:
            # Tous les paris identiques - cas pathologique
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Écart-type nul (tous paris identiques)",
                details={"moyenne": moyenne, "ecart_type": 0},
                type_pattern="regression_moyenne",
            )

        # Z-score des 5 derniers paris (moyenne récente vs globale)
        derniers_profits = profits[-5:]
        moyenne_recente = np.mean(derniers_profits)

        # Z-score = (x - μ) / (σ / sqrt(n))
        z_score = (moyenne_recente - moyenne) / (ecart_type / np.sqrt(len(derniers_profits)))

        alerte = abs(z_score) > seuil_z

        if alerte:
            if z_score > 0:
                tendance = "série de gains bien supérieure à la moyenne"
                conseil = "Attention à la confiance excessive. Chaque pari reste indépendant."
            else:
                tendance = "série de pertes bien inférieure à la moyenne"
                conseil = "Éviter de 'se refaire'. Chaque pari est indépendant du précédent."

            message = (
                f"Régression vers moyenne détectée: {tendance}. "
                f"Un retour vers la moyenne statistique est attendu sur le long terme, "
                f"mais ne prédit pas le résultat du prochain pari. {conseil}"
            )
            severite = "elevee" if abs(z_score) > 3.0 else "moyenne"
        else:
            message = "Pas d'anomalie statistique détectée (variation normale)"
            severite = "faible"

        return ResultatTest(
            alerte=alerte,
            severite=severite,
            message=message,
            details={
                "z_score": round(z_score, 2),
                "moyenne_globale": round(moyenne, 2),
                "moyenne_recente": round(moyenne_recente, 2),
                "ecart_type": round(ecart_type, 2),
                "nb_paris": len(profits),
                "seuil": seuil_z,
            },
            type_pattern="regression_moyenne",
        )

    def test_hot_hand_fallacy(
        self, paris: list[PariSportif], seuil_p: float = 0.05
    ) -> ResultatTest:
        """
        Test runs pour détecter le biais de la "main chaude" (hot hand fallacy).

        Utilise le runs test (test des séquences) pour vérifier si les victoires/défaites
        alternent de manière non-aléatoire. Un pattern d'alternance peut indiquer :
        - Trop d'alternances : joueur change stratégie après chaque résultat (gambler's fallacy)
        - Trop peu d'alternances : joueur mise plus après gains (hot hand fallacy)

        Args:
            paris: Liste des paris récents (min 20 recommandé)
            seuil_p: Seuil p-value (défaut 0.05)

        Returns:
            ResultatTest avec alerte si p-value < seuil
        """
        if len(paris) < 20:
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Pas assez de paris pour runs test (min 20 requis)",
                details={"nb_paris": len(paris)},
                type_pattern="hot_hand",
            )

        # Créer séquence binaire (1=gagne, 0=perdu)
        sequence = []
        for pari in paris:
            if pari.statut == "gagne":
                sequence.append(1)
            elif pari.statut == "perdu":
                sequence.append(0)

        if len(sequence) < 20:
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Pas assez de paris terminés",
                details={"nb_paris_termines": len(sequence)},
                type_pattern="hot_hand",
            )

        # Runs test de Wald-Wolfowitz
        try:
            _, p_value = stats.runs_test(np.array(sequence))
        except Exception as e:
            logger.error(f"Erreur runs test: {e}")
            return ResultatTest(
                alerte=False,
                severite="faible",
                message=f"Erreur calcul runs test: {e}",
                details={},
                type_pattern="hot_hand",
            )

        alerte = p_value < seuil_p

        if alerte:
            # Compter runs (séquences consécutives)
            nb_runs = 1
            for i in range(1, len(sequence)):
                if sequence[i] != sequence[i - 1]:
                    nb_runs += 1

            # Nombre attendu de runs pour séquence aléatoire
            n1 = sum(sequence)  # Nb de 1 (gains)
            n0 = len(sequence) - n1  # Nb de 0 (pertes)
            expected_runs = (2 * n1 * n0) / (n1 + n0) + 1

            if nb_runs < expected_runs:
                pattern_type = "clustering"
                message = (
                    "Pattern 'Hot Hand' détecté: séquences de gains/pertes groupées. "
                    "Attention au biais cognitif : croire qu'une série continue indéfiniment. "
                    "Rappel : chaque pari est statistiquement indépendant."
                )
            else:
                pattern_type = "alternation"
                message = (
                    "Pattern d'alternance excessive détecté. "
                    "Attention au biais 'Gambler's Fallacy' : changer systématiquement après perte/gain. "
                    "Rappel : le résultat précédent n'influence pas le suivant."
                )

            severite = "elevee" if p_value < 0.01 else "moyenne"
        else:
            message = "Pas de pattern Hot Hand détecté (séquence conforme au hasard)"
            severite = "faible"
            pattern_type = "normal"

        return ResultatTest(
            alerte=alerte,
            severite=severite,
            message=message,
            details={
                "p_value": round(p_value, 4),
                "pattern_type": pattern_type,
                "nb_paris": len(sequence),
                "taux_victoire": round(sum(sequence) / len(sequence) * 100, 1),
                "seuil": seuil_p,
            },
            type_pattern="hot_hand",
        )

    def test_gamblers_fallacy(
        self, paris: list[PariSportif], seuil_p: float = 0.05
    ) -> ResultatTest:
        """
        Test Chi-square d'indépendance pour détecter gambler's fallacy.

        Vérifie si la mise varie en fonction du résultat précédent.
        Gambler's fallacy : augmenter mise après perte en espérant "se refaire".

        Args:
            paris: Liste des paris récents (min 30 recommandé)
            seuil_p: Seuil p-value (défaut 0.05)

        Returns:
            ResultatTest avec alerte si dépendance détectée
        """
        if len(paris) < 30:
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Pas assez de paris pour test indépendance (min 30 requis)",
                details={"nb_paris": len(paris)},
                type_pattern="gamblers_fallacy",
            )

        # Préparer données: paris[i].mise dépend-elle de paris[i-1].resultat ?
        paris_termines = [p for p in paris if p.statut in ("gagne", "perdu")]

        if len(paris_termines) < 30:
            return ResultatTest(
                alerte=False,
                severite="faible",
                message="Pas assez de paris terminés",
                details={"nb_paris_termines": len(paris_termines)},
                type_pattern="gamblers_fallacy",
            )

        # Construire table contingence : mise (élevée/faible) vs résultat précédent (gain/perte)
        mises = [float(p.mise) for p in paris_termines]
        mediane_mise = np.median(mises)

        # Tableau 2x2: [après gain: élevée, faible] [après perte: élevée, faible]
        table = [
            [0, 0],
            [0, 0],
        ]  # [[apres_gain_eleve, apres_gain_faible], [apres_perte_eleve, apres_perte_faible]]

        for i in range(1, len(paris_termines)):
            pari_actuel = paris_termines[i]
            pari_precedent = paris_termines[i - 1]

            mise_elevee = pari_actuel.mise >= mediane_mise
            perte_precedente = pari_precedent.statut == "perdu"

            if perte_precedente:
                table[1][0 if mise_elevee else 1] += 1
            else:
                table[0][0 if mise_elevee else 1] += 1

        # Test Chi-square
        try:
            chi2, p_value, _, _ = stats.chi2_contingency(table)
        except Exception as e:
            logger.error(f"Erreur Chi-square: {e}")
            return ResultatTest(
                alerte=False,
                severite="faible",
                message=f"Erreur calcul Chi-square: {e}",
                details={},
                type_pattern="gamblers_fallacy",
            )

        alerte = p_value < seuil_p

        if alerte:
            # Analyser la direction de la dépendance
            pct_eleve_apres_perte = (
                table[1][0] / (table[1][0] + table[1][1]) * 100 if sum(table[1]) > 0 else 0
            )
            pct_eleve_apres_gain = (
                table[0][0] / (table[0][0] + table[0][1]) * 100 if sum(table[0]) > 0 else 0
            )

            if pct_eleve_apres_perte > pct_eleve_apres_gain + 10:
                message = (
                    "Gambler's Fallacy détecté: tu augmentes les mises après pertes. "
                    "Attention : 'se refaire' est un biais cognitif dangereux. "
                    "Chaque pari est indépendant, le précédent n'influence pas le suivant. "
                    "Respecte un budget fixe par pari."
                )
                severite = "elevee"
            elif pct_eleve_apres_gain > pct_eleve_apres_perte + 10:
                message = (
                    "Pattern 'House Money Effect' détecté: tu augmentes après gains. "
                    "Attention au risque de tout perdre rapidement. "
                    "Maintiens une gestion de bankroll constante."
                )
                severite = "moyenne"
            else:
                message = "Dépendance statistique détectée entre mises et résultats précédents"
                severite = "moyenne"
        else:
            message = "Pas de Gambler's Fallacy détectée (mises indépendantes des résultats)"
            severite = "faible"

        return ResultatTest(
            alerte=alerte,
            severite=severite,
            message=message,
            details={
                "p_value": round(p_value, 4),
                "chi2": round(chi2, 2),
                "table_contingence": table,
                "mediane_mise": round(mediane_mise, 2),
                "nb_paris": len(paris_termines) - 1,  # -1 car on compare paris[i] avec paris[i-1]
                "seuil": seuil_p,
            },
            type_pattern="gamblers_fallacy",
        )

    @avec_session_db
    def analyser_patterns_utilisateur(
        self, user_id: int | None = None, nb_paris: int = 50, db: Session = None
    ) -> dict[str, ResultatTest]:
        """
        Analyse tous les patterns statistiques pour un utilisateur.

        Exécute les 3 tests et retourne un dict de résultats.

        Args:
            user_id: ID utilisateur (None = tous les paris)
            nb_paris: Nombre de paris récents à analyser
            db: Session DB (injectée par décorateur)

        Returns:
            Dict avec clés "regression_moyenne", "hot_hand", "gamblers_fallacy"
        """
        if db is None:
            raise ErreurBaseDeDonnees("Session DB requise")

        # Récupérer paris récents
        query = db.query(PariSportif).order_by(PariSportif.cree_le.desc())

        if user_id:
            query = query.filter(PariSportif.user_id == user_id)

        paris = query.limit(nb_paris).all()

        return {
            "regression_moyenne": self.test_regression_moyenne(paris),
            "hot_hand": self.test_hot_hand_fallacy(paris),
            "gamblers_fallacy": self.test_gamblers_fallacy(paris),
        }
