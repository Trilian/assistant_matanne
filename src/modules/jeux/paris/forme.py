"""
Calcul de forme des équipes.

Fonctionnalités:
- Score de forme basé sur les 5 derniers matchs
- Détection de séries (victoires, défaites, nuls)
- Tendance (hausse/baisse/stable)
"""

import logging
from typing import Any

from .constants import BONUS_NUL_PAR_MATCH, POIDS_FORME, SEUIL_SERIE_SANS_NUL

logger = logging.getLogger(__name__)


def calculer_forme_equipe(matchs_recents: list[dict[str, Any]], equipe_id: int) -> dict[str, Any]:
    """
    Calcule la forme d'une équipe sur ses derniers matchs.

    Args:
        matchs_recents: Liste des matchs récents (du plus ancien au plus récent)
        equipe_id: ID de l'équipe à analyser

    Returns:
        Dict avec score de forme, tendance, stats
    """
    if not matchs_recents:
        return {
            "score": 50.0,
            "forme_str": "?????",
            "tendance": "inconnue",
            "victoires": 0,
            "nuls": 0,
            "defaites": 0,
            "buts_marques": 0,
            "buts_encaisses": 0,
            "serie_en_cours": None,
        }

    # Prendre les 5 derniers matchs max
    matchs = matchs_recents[-5:] if len(matchs_recents) > 5 else matchs_recents

    score_total = 0.0
    poids_total = 0.0
    forme_lettres = []
    victoires, nuls, defaites = 0, 0, 0
    buts_marques, buts_encaisses = 0, 0
    serie = []

    for i, match in enumerate(reversed(matchs)):  # Du plus récent au plus ancien
        poids = POIDS_FORME[i] if i < len(POIDS_FORME) else 0.3
        poids_total += poids

        # Déterminer si victoire/nul/défaite pour cette équipe
        est_domicile = match.get("equipe_domicile_id") == equipe_id
        score_dom = match.get("score_domicile", 0) or 0
        score_ext = match.get("score_exterieur", 0) or 0

        if est_domicile:
            buts_marques += score_dom
            buts_encaisses += score_ext
            if score_dom > score_ext:
                resultat = "V"
                victoires += 1
                score_total += 100 * poids
            elif score_dom < score_ext:
                resultat = "D"
                defaites += 1
                score_total += 0 * poids
            else:
                resultat = "N"
                nuls += 1
                score_total += 40 * poids
        else:
            buts_marques += score_ext
            buts_encaisses += score_dom
            if score_ext > score_dom:
                resultat = "V"
                victoires += 1
                score_total += 100 * poids
            elif score_ext < score_dom:
                resultat = "D"
                defaites += 1
                score_total += 0 * poids
            else:
                resultat = "N"
                nuls += 1
                score_total += 40 * poids

        forme_lettres.append(resultat)
        serie.append(resultat)

    # Score normalisé (0-100)
    score_forme = score_total / poids_total if poids_total > 0 else 50.0

    # Déterminer la tendance
    if len(forme_lettres) >= 3:
        recents = forme_lettres[:3]
        if recents.count("V") >= 2:
            tendance = "hausse"
        elif recents.count("D") >= 2:
            tendance = "baisse"
        else:
            tendance = "stable"
    else:
        tendance = "inconnue"

    # Série en cours
    serie_en_cours = None
    if serie:
        premier = serie[0]
        compte = 1
        for r in serie[1:]:
            if r == premier:
                compte += 1
            else:
                break
        if compte >= 2:
            serie_en_cours = f"{compte}{premier}"  # ex: "3V" ou "2D"

    return {
        "score": round(score_forme, 1),
        "forme_str": "".join(forme_lettres),
        "tendance": tendance,
        "victoires": victoires,
        "nuls": nuls,
        "defaites": defaites,
        "buts_marques": buts_marques,
        "buts_encaisses": buts_encaisses,
        "serie_en_cours": serie_en_cours,
        "nb_matchs": len(matchs),
        "matchs_sans_nul": calculer_serie_sans_nul(forme_lettres),
    }


def calculer_serie_sans_nul(forme_lettres: list[str]) -> int:
    """
    Calcule le nombre de matchs consécutifs sans nul.

    Principe statistique: En moyenne ~25% des matchs sont nuls.
    Si une équipe n'a pas fait de nul depuis longtemps, la probabilité
    d'en faire un augmente (régression vers la moyenne).
    """
    count = 0
    for resultat in forme_lettres:
        if resultat == "N":
            break
        count += 1
    return count


def calculer_bonus_nul_regression(matchs_sans_nul_dom: int, matchs_sans_nul_ext: int) -> float:
    """
    Calcule le bonus de probabilité de nul basé sur les séries sans nul.

    Si les 2 équipes n'ont pas fait de nul depuis longtemps,
    la probabilité d'un nul augmente significativement.
    """
    bonus = 0.0

    # Bonus équipe domicile
    if matchs_sans_nul_dom >= SEUIL_SERIE_SANS_NUL:
        excedent = matchs_sans_nul_dom - SEUIL_SERIE_SANS_NUL + 1
        bonus += min(0.15, excedent * BONUS_NUL_PAR_MATCH)

    # Bonus équipe extérieur
    if matchs_sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
        excedent = matchs_sans_nul_ext - SEUIL_SERIE_SANS_NUL + 1
        bonus += min(0.15, excedent * BONUS_NUL_PAR_MATCH)

    # Bonus combo si les DEUX équipes ont une longue série sans nul
    if matchs_sans_nul_dom >= SEUIL_SERIE_SANS_NUL and matchs_sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
        bonus += 0.05

    return min(0.25, bonus)


def calculer_historique_face_a_face(
    matchs_h2h: list[dict[str, Any]], equipe_dom_id: int, equipe_ext_id: int
) -> dict[str, Any]:
    """
    Analyse l'historique des confrontations directes.

    Args:
        matchs_h2h: Matchs entre les deux équipes
        equipe_dom_id: ID équipe qui joue à domicile
        equipe_ext_id: ID équipe qui joue à l'extérieur

    Returns:
        Stats des face-à-face
    """
    if not matchs_h2h:
        return {
            "nb_matchs": 0,
            "victoires_dom": 0,
            "victoires_ext": 0,
            "nuls": 0,
            "avantage": None,
            "derniere_confrontation": None,
        }

    vic_dom, vic_ext, nuls = 0, 0, 0
    buts_dom, buts_ext = 0, 0

    for match in matchs_h2h:
        score_d = match.get("score_domicile", 0) or 0
        score_e = match.get("score_exterieur", 0) or 0

        if match.get("equipe_domicile_id") == equipe_dom_id:
            buts_dom += score_d
            buts_ext += score_e
            if score_d > score_e:
                vic_dom += 1
            elif score_e > score_d:
                vic_ext += 1
            else:
                nuls += 1
        else:
            buts_dom += score_e
            buts_ext += score_d
            if score_e > score_d:
                vic_dom += 1
            elif score_d > score_e:
                vic_ext += 1
            else:
                nuls += 1

    # Déterminer l'avantage
    if vic_dom > vic_ext + 1:
        avantage = "domicile"
    elif vic_ext > vic_dom + 1:
        avantage = "exterieur"
    else:
        avantage = "equilibre"

    return {
        "nb_matchs": len(matchs_h2h),
        "victoires_dom": vic_dom,
        "victoires_ext": vic_ext,
        "nuls": nuls,
        "buts_dom": buts_dom,
        "buts_ext": buts_ext,
        "avantage": avantage,
        "derniere_confrontation": matchs_h2h[-1] if matchs_h2h else None,
    }
