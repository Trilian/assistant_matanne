"""
Système d'analyse intelligent des paris.

Classe principale AnalyseurParis pour:
- Analyse complète de matchs
- Détection de value bets
- Génération de résumés pour les parieurs
- Analyse des tendances de buts
"""

import logging
from datetime import datetime
from typing import Any

from src.services.jeux.prediction_service import predire_over_under, predire_resultat_match

from .forme import calculer_forme_equipe, calculer_historique_face_a_face

logger = logging.getLogger(__name__)


class AnalyseurParis:
    """
    Classe principale pour l'analyse intelligente des paris sportifs.

    Fournit une interface unifiée pour:
    - Analyser des matchs individuels
    - Détecter les value bets
    - Générer des analyses complètes
    - Calculer les tendances
    """

    def __init__(self, cache_enabled: bool = True):
        """
        Initialise l'analyseur.

        Args:
            cache_enabled: Active le cache des analyses
        """
        self._cache: dict[str, Any] = {}
        self._cache_enabled = cache_enabled
        self._historique_analyses: list[dict] = []

    def analyser_match(
        self,
        equipe_dom_id: int,
        equipe_ext_id: int,
        matchs_dom: list[dict],
        matchs_ext: list[dict],
        matchs_h2h: list[dict],
        cotes: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """
        Analyse complète d'un match.

        Args:
            equipe_dom_id: ID équipe domicile
            equipe_ext_id: ID équipe extérieur
            matchs_dom: Derniers matchs équipe domicile
            matchs_ext: Derniers matchs équipe extérieur
            matchs_h2h: Historique face-à-face
            cotes: Cotes des bookmakers

        Returns:
            Analyse complète avec prédiction
        """
        forme_dom = calculer_forme_equipe(matchs_dom, equipe_dom_id)
        forme_ext = calculer_forme_equipe(matchs_ext, equipe_ext_id)
        h2h = calculer_historique_face_a_face(matchs_h2h, equipe_dom_id, equipe_ext_id)

        prediction = predire_resultat_match(forme_dom, forme_ext, h2h, cotes)
        over_under = predire_over_under(forme_dom, forme_ext)

        analyse = {
            "timestamp": datetime.now().isoformat(),
            "equipes": {"domicile": equipe_dom_id, "exterieur": equipe_ext_id},
            "formes": {"domicile": forme_dom, "exterieur": forme_ext},
            "h2h": h2h,
            "prediction": prediction,
            "over_under": over_under,
            "value_bets": self.calculer_value_bet(prediction, cotes) if cotes else [],
        }

        self._historique_analyses.append(
            {
                "match_id": f"{equipe_dom_id}_{equipe_ext_id}",
                "timestamp": analyse["timestamp"],
                "prediction": prediction["prediction"],
            }
        )

        return analyse

    def analyser_serie_complete(
        self, matchs_a_analyser: list[dict[str, Any]], donnees_matchs: dict[int, dict]
    ) -> list[dict[str, Any]]:
        """
        Analyse une série de matchs (journée de championnat).

        Args:
            matchs_a_analyser: Liste de matchs à analyser
            donnees_matchs: Données historiques par équipe

        Returns:
            Liste d'analyses triées par confiance
        """
        analyses = []

        for match in matchs_a_analyser:
            eq_dom = match.get("equipe_domicile_id")
            eq_ext = match.get("equipe_exterieur_id")

            if not eq_dom or not eq_ext:
                continue

            donnees = donnees_matchs.get(eq_dom, {})
            matchs_dom = donnees.get("matchs_recents", [])

            donnees = donnees_matchs.get(eq_ext, {})
            matchs_ext = donnees.get("matchs_recents", [])

            matchs_h2h = match.get("h2h", [])
            cotes = match.get("cotes")

            try:
                analyse = self.analyser_match(
                    eq_dom, eq_ext, matchs_dom, matchs_ext, matchs_h2h, cotes
                )
                analyse["match_info"] = match
                analyses.append(analyse)
            except Exception as e:
                logger.warning(f"Erreur analyse match {eq_dom} vs {eq_ext}: {e}")

        # Trier par confiance décroissante
        analyses.sort(key=lambda x: x["prediction"]["confiance"], reverse=True)

        return analyses

    def calculer_value_bet(
        self, prediction: dict[str, Any], cotes: dict[str, float]
    ) -> list[dict[str, Any]]:
        """
        Identifie les value bets (paris à valeur positive).

        Un value bet existe quand la cote proposée est supérieure
        à ce que les probabilités réelles suggèrent.
        """
        if not cotes:
            return []

        value_bets = []
        probas = prediction["probabilites"]

        mappings = [
            ("1", "domicile", probas["domicile"]),
            ("N", "nul", probas["nul"]),
            ("2", "exterieur", probas["exterieur"]),
        ]

        for code, cle_cote, proba in mappings:
            cote = cotes.get(cle_cote, 0)
            if cote <= 1:
                continue

            proba_decimal = proba / 100
            cote_juste = 1 / proba_decimal if proba_decimal > 0 else 0

            ev = (proba_decimal * cote) - 1

            if ev > 0.05:  # Seuil minimal 5%
                value_bets.append(
                    {
                        "type": code,
                        "cote_actuelle": cote,
                        "cote_juste": round(cote_juste, 2),
                        "probabilite": proba,
                        "ev": round(ev * 100, 1),
                        "niveau": "excellent"
                        if ev > 0.15
                        else "bon"
                        if ev > 0.08
                        else "acceptable",
                    }
                )

        value_bets.sort(key=lambda x: x["ev"], reverse=True)
        return value_bets

    def analyser_tendance_buts(
        self, matchs: list[dict[str, Any]], equipe_id: int | None = None
    ) -> dict[str, Any]:
        """
        Analyse la tendance des buts (over/under patterns).
        """
        if not matchs:
            return {"tendance": "inconnu", "stats": {}}

        over_1_5 = 0
        over_2_5 = 0
        over_3_5 = 0
        btts = 0
        clean_sheets = 0

        for match in matchs:
            score_dom = match.get("score_domicile", 0) or 0
            score_ext = match.get("score_exterieur", 0) or 0
            total = score_dom + score_ext

            if total > 1.5:
                over_1_5 += 1
            if total > 2.5:
                over_2_5 += 1
            if total > 3.5:
                over_3_5 += 1
            if score_dom > 0 and score_ext > 0:
                btts += 1

            if equipe_id:
                est_dom = match.get("equipe_domicile_id") == equipe_id
                buts_encaisses = score_ext if est_dom else score_dom
                if buts_encaisses == 0:
                    clean_sheets += 1

        nb = len(matchs)
        stats = {
            "over_1_5": round(over_1_5 / nb * 100, 1),
            "over_2_5": round(over_2_5 / nb * 100, 1),
            "over_3_5": round(over_3_5 / nb * 100, 1),
            "btts": round(btts / nb * 100, 1),
            "clean_sheets": round(clean_sheets / nb * 100, 1) if equipe_id else None,
            "buts_moyens": round(
                sum(
                    (m.get("score_domicile", 0) or 0) + (m.get("score_exterieur", 0) or 0)
                    for m in matchs
                )
                / nb,
                2,
            ),
        }

        if stats["over_2_5"] > 65:
            tendance = "très offensif"
        elif stats["over_2_5"] > 50:
            tendance = "offensif"
        elif stats["over_2_5"] < 35:
            tendance = "très défensif"
        elif stats["over_2_5"] < 45:
            tendance = "défensif"
        else:
            tendance = "équilibré"

        return {"tendance": tendance, "stats": stats}


def generer_analyse_complete(
    match: dict[str, Any],
    matchs_equipe_dom: list[dict],
    matchs_equipe_ext: list[dict],
    matchs_h2h: list[dict],
    cotes: dict[str, float] | None = None,
    championnat: str | None = None,
) -> dict[str, Any]:
    """
    Génère une analyse complète d'un match pour affichage.

    Fonction de haut niveau combinant toutes les analyses.
    """
    analyseur = AnalyseurParis()

    equipe_dom_id = match.get("equipe_domicile_id")
    equipe_ext_id = match.get("equipe_exterieur_id")

    analyse = analyseur.analyser_match(
        equipe_dom_id, equipe_ext_id, matchs_equipe_dom, matchs_equipe_ext, matchs_h2h, cotes
    )

    # Ajouter analyse tendance buts
    tendance_buts = analyseur.analyser_tendance_buts(matchs_equipe_dom + matchs_equipe_ext)
    analyse["tendance_buts"] = tendance_buts

    # Ajouter info match
    analyse["match"] = {
        "equipe_domicile": match.get("equipe_domicile", "?"),
        "equipe_exterieur": match.get("equipe_exterieur", "?"),
        "date": match.get("date"),
        "championnat": championnat or match.get("championnat", "?"),
    }

    # Générer le résumé
    analyse["resume"] = generer_resume_parieur(analyse)

    return analyse


def generer_resume_parieur(analyse: dict[str, Any]) -> str:
    """
    Génère un résumé textuel concis pour le parieur.
    """
    lines = []

    prediction = analyse.get("prediction", {})
    match_info = analyse.get("match", {})

    dom = match_info.get("equipe_domicile", "Dom")
    ext = match_info.get("equipe_exterieur", "Ext")

    lines.append(f"## 🎯 {dom} vs {ext}")
    lines.append("")

    # Prédiction principale
    pred = prediction.get("prediction", "?")
    confiance = prediction.get("confiance", 0)
    probas = prediction.get("probabilites", {})

    labels = {"1": dom, "N": "Nul", "2": ext}
    lines.append(f"**Prédiction**: {labels.get(pred, pred)} ({confiance:.0f}% confiance)")
    lines.append(
        f"Probas: {dom} {probas.get('domicile', 0):.0f}% | Nul {probas.get('nul', 0):.0f}% | {ext} {probas.get('exterieur', 0):.0f}%"
    )
    lines.append("")

    # Forme des équipes
    formes = analyse.get("formes", {})
    forme_dom = formes.get("domicile", {})
    forme_ext = formes.get("exterieur", {})

    lines.append(
        f"**Forme**: {dom} {forme_dom.get('forme_str', '?')} ({forme_dom.get('score', 0):.0f}pts) vs {ext} {forme_ext.get('forme_str', '?')} ({forme_ext.get('score', 0):.0f}pts)"
    )

    # Séries et alertes
    alertes = []

    if forme_dom.get("matchs_sans_nul", 0) >= 5:
        alertes.append(f"⚠️ {dom}: {forme_dom['matchs_sans_nul']} matchs sans nul")
    if forme_ext.get("matchs_sans_nul", 0) >= 5:
        alertes.append(f"⚠️ {ext}: {forme_ext['matchs_sans_nul']} matchs sans nul")

    if forme_dom.get("serie_en_cours"):
        if (
            "D" in forme_dom["serie_en_cours"]
            and int(forme_dom["serie_en_cours"].replace("D", "")) >= 3
        ):
            alertes.append(f"📉 {dom} en série noire")
    if forme_ext.get("serie_en_cours"):
        if (
            "V" in forme_ext["serie_en_cours"]
            and int(forme_ext["serie_en_cours"].replace("V", "")) >= 3
        ):
            alertes.append(f"🔥 {ext} en forme!")

    if alertes:
        lines.append("")
        lines.extend(alertes)

    # Value bets
    value_bets = analyse.get("value_bets", [])
    if value_bets:
        lines.append("")
        lines.append("**💎 Value Bets détectés:**")
        for vb in value_bets[:2]:
            lines.append(f"  - {vb['type']} @ {vb['cote_actuelle']:.2f} (EV: +{vb['ev']:.0f}%)")

    # Over/Under
    over_under = analyse.get("over_under", {})
    if over_under:
        pred_ou = over_under.get("prediction", "?")
        buts = over_under.get("buts_attendus", 0)
        lines.append("")
        lines.append(f"**Buts**: {pred_ou.upper()} 2.5 ({buts:.1f} attendus)")

    # Conseil final
    conseil = prediction.get("conseil", "")
    if conseil:
        lines.append("")
        lines.append(f"**💡 {conseil}**")

    return "\n".join(lines)
