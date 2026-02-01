"""
Logique métier Paris Sportifs - Prédictions et analyses
Ce module contient toute la logique pure, testable sans Streamlit.

Algorithme de prédiction basé sur:
- Forme récente (5 derniers matchs) avec pondération décroissante
- Historique face-à-face (head-to-head)
- Avantage domicile/extérieur (~55% victoires à domicile statistiquement)
- Tendances de buts (over/under)
- Régression vers la moyenne
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List, Tuple
from decimal import Decimal
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════

CHAMPIONNATS = [
    "Ligue 1",
    "Premier League", 
    "La Liga",
    "Serie A",
    "Bundesliga",
    "Champions League",
    "Europa League"
]

# Pondération pour la forme récente (match le plus récent = plus de poids)
POIDS_FORME = [1.0, 0.85, 0.70, 0.55, 0.40]  # 5 derniers matchs

# Avantage domicile moyen (basé sur stats historiques)
AVANTAGE_DOMICILE = 0.12  # +12% de chances de victoire à domicile

# Seuils de confiance pour les prédictions
SEUIL_CONFIANCE_HAUTE = 65
SEUIL_CONFIANCE_MOYENNE = 50

# Seuils pour la régression des nuls (loi des grands nombres)
SEUIL_SERIE_SANS_NUL = 5  # Après 5 matchs sans nul, proba augmente
BONUS_NUL_PAR_MATCH = 0.03  # +3% par match supplémentaire sans nul


# ═══════════════════════════════════════════════════════════════════
# CALCUL DE FORME
# ═══════════════════════════════════════════════════════════════════

def calculer_forme_equipe(matchs_recents: List[Dict[str, Any]], equipe_id: int) -> Dict[str, Any]:
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
            "score": 50.0,  # Neutre
            "forme_str": "?????",
            "tendance": "inconnue",
            "victoires": 0,
            "nuls": 0,
            "defaites": 0,
            "buts_marques": 0,
            "buts_encaisses": 0,
            "serie_en_cours": None
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
        "forme_str": "".join(forme_lettres),  # ex: "VVNDV"
        "tendance": tendance,
        "victoires": victoires,
        "nuls": nuls,
        "defaites": defaites,
        "buts_marques": buts_marques,
        "buts_encaisses": buts_encaisses,
        "serie_en_cours": serie_en_cours,
        "nb_matchs": len(matchs),
        "matchs_sans_nul": calculer_serie_sans_nul(forme_lettres)
    }


def calculer_serie_sans_nul(forme_lettres: List[str]) -> int:
    """
    Calcule le nombre de matchs consécutifs sans nul.
    
    Principe statistique: En moyenne ~25% des matchs sont nuls.
    Si une équipe n'a pas fait de nul depuis longtemps, la probabilité
    d'en faire un augmente (régression vers la moyenne).
    """
    count = 0
    for resultat in forme_lettres:  # Du plus récent au plus ancien
        if resultat == "N":
            break
        count += 1
    return count


def calculer_bonus_nul_regression(matchs_sans_nul_dom: int, matchs_sans_nul_ext: int) -> float:
    """
    Calcule le bonus de probabilité de nul basé sur les séries sans nul.
    
    Si les 2 équipes n'ont pas fait de nul depuis longtemps,
    la probabilité d'un nul augmente significativement.
    
    Statistiques:
    - Match nul moyen: ~25%
    - Après 5 matchs sans nul: +15% pour chaque équipe
    - Après 8 matchs sans nul: +24% (presque doublé!)
    """
    bonus = 0.0
    
    # Bonus équipe domicile
    if matchs_sans_nul_dom >= SEUIL_SERIE_SANS_NUL:
        excedent = matchs_sans_nul_dom - SEUIL_SERIE_SANS_NUL + 1
        bonus += min(0.15, excedent * BONUS_NUL_PAR_MATCH)  # Cap à 15%
    
    # Bonus équipe extérieur  
    if matchs_sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
        excedent = matchs_sans_nul_ext - SEUIL_SERIE_SANS_NUL + 1
        bonus += min(0.15, excedent * BONUS_NUL_PAR_MATCH)  # Cap à 15%
    
    # Si les DEUX équipes ont une longue série sans nul = encore plus probable
    if matchs_sans_nul_dom >= SEUIL_SERIE_SANS_NUL and matchs_sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
        bonus += 0.05  # Bonus combo
    
    return min(0.25, bonus)  # Cap total à 25%


def calculer_historique_face_a_face(matchs_h2h: List[Dict[str, Any]], 
                                     equipe_dom_id: int,
                                     equipe_ext_id: int) -> Dict[str, Any]:
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
            "derniere_confrontation": None
        }
    
    vic_dom, vic_ext, nuls = 0, 0, 0
    buts_dom, buts_ext = 0, 0
    
    for match in matchs_h2h:
        score_d = match.get("score_domicile", 0) or 0
        score_e = match.get("score_exterieur", 0) or 0
        
        # Qui était à domicile dans ce match?
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
        "derniere_confrontation": matchs_h2h[-1] if matchs_h2h else None
    }


# ═══════════════════════════════════════════════════════════════════
# PRÉDICTION PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

def predire_resultat_match(
    forme_domicile: Dict[str, Any],
    forme_exterieur: Dict[str, Any],
    h2h: Dict[str, Any],
    cotes: Optional[Dict[str, float]] = None,
    facteurs_supplementaires: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Prédit le résultat d'un match en combinant plusieurs facteurs.
    
    Algorithme:
    1. Score de forme (40% du poids)
    2. Avantage domicile fixe (+12%)
    3. Historique H2H (20% du poids)
    4. Ajustement selon les cotes bookmakers (10%)
    5. Facteurs contextuels (10%)
    
    Args:
        forme_domicile: Stats forme équipe domicile
        forme_exterieur: Stats forme équipe extérieur
        h2h: Historique confrontations directes
        cotes: Cotes des bookmakers (optionnel)
        facteurs_supplementaires: Fatigue, blessures, etc.
        
    Returns:
        Prédiction avec probabilités et confiance
    """
    # === Étape 1: Probabilités de base selon la forme ===
    score_dom = forme_domicile.get("score", 50)
    score_ext = forme_exterieur.get("score", 50)
    
    # Convertir en probabilités brutes
    total = score_dom + score_ext + 50  # +50 pour le nul
    proba_dom = score_dom / total
    proba_ext = score_ext / total
    proba_nul = 50 / total
    
    # === Étape 2: Avantage domicile ===
    proba_dom += AVANTAGE_DOMICILE
    proba_ext -= AVANTAGE_DOMICILE * 0.7  # L'extérieur perd moins que le domicile gagne
    proba_nul -= AVANTAGE_DOMICILE * 0.3
    
    # === Étape 3: Ajustement H2H ===
    if h2h.get("nb_matchs", 0) >= 3:
        avantage = h2h.get("avantage")
        if avantage == "domicile":
            proba_dom += 0.05
            proba_ext -= 0.03
            proba_nul -= 0.02
        elif avantage == "exterieur":
            proba_ext += 0.05
            proba_dom -= 0.03
            proba_nul -= 0.02
    
    # === Étape 4: Régression vers la moyenne ===
    # Si une équipe a une série de défaites, elle a statistiquement plus de chances de gagner
    serie_dom = forme_domicile.get("serie_en_cours")
    serie_ext = forme_exterieur.get("serie_en_cours")
    
    if serie_dom and "D" in serie_dom:
        nb_defaites = int(serie_dom.replace("D", ""))
        if nb_defaites >= 3:
            proba_dom += 0.03 * (nb_defaites - 2)  # Bonus croissant
            logger.info(f"Régression moyenne: {nb_defaites}D consécutives → +{0.03 * (nb_defaites - 2):.1%}")
    
    if serie_ext and "D" in serie_ext:
        nb_defaites = int(serie_ext.replace("D", ""))
        if nb_defaites >= 3:
            proba_ext += 0.03 * (nb_defaites - 2)
    
    # Inversement, série de victoires = risque de fin
    if serie_dom and "V" in serie_dom:
        nb_victoires = int(serie_dom.replace("V", ""))
        if nb_victoires >= 5:
            proba_dom -= 0.02  # Petite correction
    
    if serie_ext and "V" in serie_ext:
        nb_victoires = int(serie_ext.replace("V", ""))
        if nb_victoires >= 5:
            proba_ext -= 0.02
    
    # === Étape 4b: Régression des nuls (NOUVEAU) ===
    # Si les équipes n'ont pas fait de nul depuis longtemps, proba nul augmente
    matchs_sans_nul_dom = forme_domicile.get("matchs_sans_nul", 0)
    matchs_sans_nul_ext = forme_exterieur.get("matchs_sans_nul", 0)
    
    bonus_nul = calculer_bonus_nul_regression(matchs_sans_nul_dom, matchs_sans_nul_ext)
    if bonus_nul > 0:
        proba_nul += bonus_nul
        # Réduire les autres probas proportionnellement
        proba_dom -= bonus_nul * 0.5
        proba_ext -= bonus_nul * 0.5
        logger.info(f"Bonus nul régression: {matchs_sans_nul_dom}+{matchs_sans_nul_ext} matchs sans nul → +{bonus_nul:.1%}")
    
    # === Étape 5: Ajustement selon les cotes (si disponibles) ===
    if cotes:
        cote_dom = cotes.get("domicile", 2.0)
        cote_nul = cotes.get("nul", 3.5)
        cote_ext = cotes.get("exterieur", 3.0)
        
        # Probabilités implicites des bookmakers
        proba_impl_dom = 1 / cote_dom
        proba_impl_nul = 1 / cote_nul
        proba_impl_ext = 1 / cote_ext
        total_impl = proba_impl_dom + proba_impl_nul + proba_impl_ext
        
        # Normaliser (enlever la marge bookmaker)
        proba_impl_dom /= total_impl
        proba_impl_nul /= total_impl
        proba_impl_ext /= total_impl
        
        # Mixer avec notre modèle (10% bookmakers)
        proba_dom = proba_dom * 0.9 + proba_impl_dom * 0.1
        proba_nul = proba_nul * 0.9 + proba_impl_nul * 0.1
        proba_ext = proba_ext * 0.9 + proba_impl_ext * 0.1
    
    # === Normalisation finale ===
    total = proba_dom + proba_nul + proba_ext
    proba_dom /= total
    proba_nul /= total
    proba_ext /= total
    
    # === Déterminer la prédiction ===
    probas = {"1": proba_dom, "N": proba_nul, "2": proba_ext}
    prediction = max(probas, key=probas.get)
    meilleure_proba = probas[prediction]
    
    # === Calcul de la confiance ===
    # Plus l'écart entre les probas est grand, plus on est confiant
    probas_triees = sorted(probas.values(), reverse=True)
    ecart = probas_triees[0] - probas_triees[1]
    confiance = min(95, 40 + ecart * 150)  # 40% de base + bonus écart
    
    # Ajuster confiance selon quantité de données
    if forme_domicile.get("nb_matchs", 0) < 3 or forme_exterieur.get("nb_matchs", 0) < 3:
        confiance *= 0.8  # Moins de données = moins confiant
    
    # === Générer les raisons ===
    raisons = []
    
    if score_dom > score_ext + 15:
        raisons.append(f"Forme domicile supérieure ({forme_domicile.get('forme_str', '?')})")
    elif score_ext > score_dom + 15:
        raisons.append(f"Forme extérieur supérieure ({forme_exterieur.get('forme_str', '?')})")
    
    if serie_dom and "D" in serie_dom and int(serie_dom.replace("D", "")) >= 3:
        raisons.append(f"Régression attendue après {serie_dom}")
    
    if h2h.get("avantage") == "domicile":
        raisons.append("Historique favorable à domicile")
    elif h2h.get("avantage") == "exterieur":
        raisons.append("Historique favorable à l'extérieur")
    
    raisons.append("Avantage terrain (+12% domicile)")
    
    # Raisons pour le nul
    if bonus_nul > 0.05:
        if matchs_sans_nul_dom >= SEUIL_SERIE_SANS_NUL:
            raisons.append(f"⚠️ {matchs_sans_nul_dom} matchs sans nul (dom) → nul probable")
        if matchs_sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
            raisons.append(f"⚠️ {matchs_sans_nul_ext} matchs sans nul (ext) → nul probable")
        if matchs_sans_nul_dom >= SEUIL_SERIE_SANS_NUL and matchs_sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
            raisons.append("🔥 COMBO: Les 2 équipes sans nul depuis longtemps!")
    
    return {
        "prediction": prediction,  # "1", "N", "2"
        "probabilites": {
            "domicile": round(proba_dom * 100, 1),
            "nul": round(proba_nul * 100, 1),
            "exterieur": round(proba_ext * 100, 1)
        },
        "confiance": round(confiance, 1),
        "raisons": raisons,
        "niveau_confiance": (
            "haute" if confiance >= SEUIL_CONFIANCE_HAUTE 
            else "moyenne" if confiance >= SEUIL_CONFIANCE_MOYENNE 
            else "faible"
        ),
        "conseil": generer_conseil_pari(prediction, confiance, cotes)
    }


def generer_conseil_pari(prediction: str, confiance: float, 
                         cotes: Optional[Dict[str, float]] = None,
                         proba_nul: float = 0.25) -> str:
    """
    Génère un conseil de pari CONCRET basé sur la prédiction et la confiance.
    
    Conseils professionnels de paris:
    1. Ne jamais parier plus de 5% de sa bankroll
    2. Chercher les value bets (EV > 0)
    3. Éviter les accumulateurs (combos)
    4. Les nuls sont souvent sous-cotés
    """
    labels = {"1": "Victoire domicile", "N": "Match nul", "2": "Victoire extérieur"}
    conseils = []
    
    # Conseil principal selon confiance
    if confiance >= SEUIL_CONFIANCE_HAUTE:
        conseils.append(f"✅ **PARIER**: {labels[prediction]} (confiance {confiance:.0f}%)")
        conseils.append("💰 Mise suggérée: 3-5% de ta bankroll")
    elif confiance >= SEUIL_CONFIANCE_MOYENNE:
        conseils.append(f"⚠️ **PRUDENT**: {labels[prediction]} risqué")
        conseils.append("💰 Mise suggérée: 1-2% max")
    else:
        conseils.append("❌ **ÉVITER** ce match - trop incertain")
        conseils.append("💡 Attends un match plus clair")
        return " | ".join(conseils)
    
    # Analyse Value Bet si cotes disponibles
    if cotes:
        cle_cote = {"1": "domicile", "N": "nul", "2": "exterieur"}[prediction]
        cote_pred = cotes.get(cle_cote, 2.0)
        proba_modele = confiance / 100
        
        # Expected Value = (proba × cote) - 1
        ev = (proba_modele * cote_pred) - 1
        
        if ev > 0.15:
            conseils.append(f"🔥 **VALUE BET**: Cote {cote_pred:.2f} trop haute! (EV: +{ev:.0%})")
        elif ev > 0.05:
            conseils.append(f"💎 Value détectée (EV: +{ev:.0%})")
        elif ev < -0.1:
            conseils.append(f"⛔ Cote trop basse, pas rentable (EV: {ev:.0%})")
    
    # Conseil spécial pour les nuls
    if proba_nul > 0.30:
        conseils.append("🎯 **ASTUCE**: Proba nul élevée, regarde la cote nul!")
    
    return " | ".join(conseils)


def generer_conseils_avances(
    forme_dom: Dict[str, Any],
    forme_ext: Dict[str, Any],
    cotes: Optional[Dict[str, float]] = None
) -> List[Dict[str, str]]:
    """
    Génère des conseils avancés de paris basés sur l'analyse.
    
    Returns:
        Liste de conseils avec type, message et niveau de confiance
    """
    conseils = []
    
    # 1. Conseil série sans nul
    matchs_sans_nul_dom = forme_dom.get("matchs_sans_nul", 0)
    matchs_sans_nul_ext = forme_ext.get("matchs_sans_nul", 0)
    
    if matchs_sans_nul_dom >= 6 or matchs_sans_nul_ext >= 6:
        total_sans_nul = matchs_sans_nul_dom + matchs_sans_nul_ext
        conseils.append({
            "type": "🎯 MATCH NUL",
            "message": f"Les équipes n'ont pas fait de nul depuis {matchs_sans_nul_dom}+{matchs_sans_nul_ext} matchs. "
                      f"Statistiquement, un nul devient très probable!",
            "niveau": "haute" if total_sans_nul >= 10 else "moyenne",
            "mise_suggere": "2-3%" if total_sans_nul >= 10 else "1-2%"
        })
    
    # 2. Conseil série défaites → rebond
    serie_dom = forme_dom.get("serie_en_cours", "")
    serie_ext = forme_ext.get("serie_en_cours", "")
    
    if serie_dom and "D" in serie_dom and int(serie_dom.replace("D", "")) >= 4:
        nb = int(serie_dom.replace("D", ""))
        conseils.append({
            "type": "📈 REBOND ATTENDU",
            "message": f"L'équipe domicile a perdu {nb} matchs d'affilée. "
                      f"À domicile, un rebond est statistiquement probable.",
            "niveau": "moyenne",
            "mise_suggere": "1-2%"
        })
    
    # 3. Conseil Over/Under selon les formes
    buts_moy_dom = (forme_dom.get("buts_marques", 0) + forme_dom.get("buts_encaisses", 0)) / max(1, forme_dom.get("nb_matchs", 1))
    buts_moy_ext = (forme_ext.get("buts_marques", 0) + forme_ext.get("buts_encaisses", 0)) / max(1, forme_ext.get("nb_matchs", 1))
    buts_attendus = (buts_moy_dom + buts_moy_ext) / 2
    
    if buts_attendus > 3.0:
        conseils.append({
            "type": "⚽ OVER 2.5",
            "message": f"Moyenne de {buts_attendus:.1f} buts/match entre ces équipes. "
                      f"Un Over 2.5 est probable!",
            "niveau": "moyenne",
            "mise_suggere": "1-2%"
        })
    elif buts_attendus < 2.0:
        conseils.append({
            "type": "🛡️ UNDER 2.5",
            "message": f"Équipes défensives ({buts_attendus:.1f} buts/match). "
                      f"Un Under 2.5 est intéressant.",
            "niveau": "moyenne",
            "mise_suggere": "1-2%"
        })
    
    # 4. Conseil Value Bet
    if cotes:
        cote_nul = cotes.get("nul", 3.5)
        if cote_nul >= 3.8 and (matchs_sans_nul_dom >= 4 or matchs_sans_nul_ext >= 4):
            conseils.append({
                "type": "💎 VALUE BET NUL",
                "message": f"Cote nul à {cote_nul:.2f} + série sans nul = opportunité!",
                "niveau": "haute",
                "mise_suggere": "2-3%"
            })
    
    return conseils


# ═══════════════════════════════════════════════════════════════════
# ANALYSE OVER/UNDER
# ═══════════════════════════════════════════════════════════════════

def predire_over_under(
    forme_domicile: Dict[str, Any],
    forme_exterieur: Dict[str, Any],
    seuil: float = 2.5
) -> Dict[str, Any]:
    """
    Prédit si le match aura plus ou moins de X buts.
    
    Args:
        forme_domicile: Stats équipe domicile
        forme_exterieur: Stats équipe extérieur
        seuil: Seuil de buts (généralement 2.5)
        
    Returns:
        Prédiction over/under avec probabilités
    """
    nb_matchs_dom = forme_domicile.get("nb_matchs", 1) or 1
    nb_matchs_ext = forme_exterieur.get("nb_matchs", 1) or 1
    
    # Moyenne de buts par match
    buts_marques_dom = forme_domicile.get("buts_marques", 0) / nb_matchs_dom
    buts_encaisses_dom = forme_domicile.get("buts_encaisses", 0) / nb_matchs_dom
    buts_marques_ext = forme_exterieur.get("buts_marques", 0) / nb_matchs_ext
    buts_encaisses_ext = forme_exterieur.get("buts_encaisses", 0) / nb_matchs_ext
    
    # Estimation buts attendus pour ce match
    buts_attendus = (buts_marques_dom + buts_encaisses_ext) / 2 + \
                    (buts_marques_ext + buts_encaisses_dom) / 2
    
    # Probabilité over
    # Utiliser une approximation simple (distribution normale)
    ecart_seuil = buts_attendus - seuil
    
    if ecart_seuil > 0.8:
        proba_over = 0.75
    elif ecart_seuil > 0.3:
        proba_over = 0.60
    elif ecart_seuil > -0.3:
        proba_over = 0.50
    elif ecart_seuil > -0.8:
        proba_over = 0.40
    else:
        proba_over = 0.25
    
    prediction = "over" if proba_over > 0.5 else "under"
    
    return {
        "prediction": prediction,
        "seuil": seuil,
        "buts_attendus": round(buts_attendus, 2),
        "probabilite_over": round(proba_over * 100, 1),
        "probabilite_under": round((1 - proba_over) * 100, 1),
        "confiance": round(abs(proba_over - 0.5) * 200, 1)  # 0-100
    }


# ═══════════════════════════════════════════════════════════════════
# CALCUL ROI & PERFORMANCE
# ═══════════════════════════════════════════════════════════════════

def calculer_performance_paris(paris: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques de performance sur une liste de paris.
    
    Args:
        paris: Liste des paris avec résultats
        
    Returns:
        Stats de performance (ROI, taux réussite, etc.)
    """
    if not paris:
        return {
            "nb_paris": 0,
            "mises_totales": Decimal("0.00"),
            "gains_totaux": Decimal("0.00"),
            "roi": 0.0,
            "taux_reussite": 0.0,
            "meilleur_pari": None,
            "pire_pari": None
        }
    
    mises = Decimal("0.00")
    gains = Decimal("0.00")
    gagnes = 0
    perdus = 0
    meilleur = None
    pire = None
    meilleur_gain = Decimal("-9999")
    pire_perte = Decimal("9999")
    
    for pari in paris:
        mise = Decimal(str(pari.get("mise", 0)))
        gain = Decimal(str(pari.get("gain", 0))) if pari.get("gain") else Decimal("0")
        statut = pari.get("statut", "en_attente")
        
        if statut == "en_attente":
            continue
            
        mises += mise
        
        if statut == "gagne":
            gagnes += 1
            gains += gain
            if gain > meilleur_gain:
                meilleur_gain = gain
                meilleur = pari
        elif statut == "perdu":
            perdus += 1
            perte = -mise
            if perte < pire_perte:
                pire_perte = perte
                pire = pari
    
    total_decides = gagnes + perdus
    
    return {
        "nb_paris": len(paris),
        "nb_decides": total_decides,
        "gagnes": gagnes,
        "perdus": perdus,
        "mises_totales": mises,
        "gains_totaux": gains,
        "profit": gains - mises,
        "roi": float((gains - mises) / mises * 100) if mises > 0 else 0.0,
        "taux_reussite": (gagnes / total_decides * 100) if total_decides > 0 else 0.0,
        "meilleur_pari": meilleur,
        "pire_pari": pire
    }


def analyser_tendances_championnat(matchs: List[Dict[str, Any]], 
                                    championnat: str) -> Dict[str, Any]:
    """
    Analyse les tendances d'un championnat (% domicile, moyenne buts, etc.)
    
    Args:
        matchs: Liste des matchs du championnat
        championnat: Nom du championnat
        
    Returns:
        Statistiques du championnat
    """
    if not matchs:
        return {
            "championnat": championnat,
            "nb_matchs": 0,
            "victoires_domicile_pct": 0,
            "nuls_pct": 0,
            "victoires_exterieur_pct": 0,
            "moyenne_buts": 0
        }
    
    vic_dom, nuls, vic_ext = 0, 0, 0
    total_buts = 0
    
    for match in matchs:
        if not match.get("joue"):
            continue
            
        score_d = match.get("score_domicile", 0) or 0
        score_e = match.get("score_exterieur", 0) or 0
        total_buts += score_d + score_e
        
        if score_d > score_e:
            vic_dom += 1
        elif score_e > score_d:
            vic_ext += 1
        else:
            nuls += 1
    
    total = vic_dom + nuls + vic_ext
    
    return {
        "championnat": championnat,
        "nb_matchs": total,
        "victoires_domicile_pct": round(vic_dom / total * 100, 1) if total > 0 else 0,
        "nuls_pct": round(nuls / total * 100, 1) if total > 0 else 0,
        "victoires_exterieur_pct": round(vic_ext / total * 100, 1) if total > 0 else 0,
        "moyenne_buts": round(total_buts / total, 2) if total > 0 else 0
    }


# ═══════════════════════════════════════════════════════════════════
# 🧠 SYSTÈME DE CONSEILS INTELLIGENTS
# ═══════════════════════════════════════════════════════════════════

class AnalyseurParis:
    """
    Système d'analyse intelligent pour les paris sportifs.
    
    Combine plusieurs techniques:
    - Analyse statistique (tendances, séries, régression)
    - Détection de patterns (historique)
    - Calcul de value bets (EV)
    - Score de confiance pondéré
    """
    
    # Poids des différents facteurs dans le score final
    POIDS = {
        "forme": 0.25,
        "domicile": 0.15,
        "serie": 0.15,
        "h2h": 0.15,
        "value_bet": 0.20,
        "tendance_buts": 0.10
    }
    
    # Seuils pour les recommandations
    SEUIL_RECOMMANDE = 65  # Score min pour recommander un pari
    SEUIL_PRUDENT = 50
    SEUIL_EVITER = 35
    
    @staticmethod
    def analyser_serie_complete(forme_lettres: str) -> Dict[str, Any]:
        """
        Analyse complète d'une série de résultats.
        
        Détecte:
        - Série en cours (VVVV, DDD, NNN)
        - Tendance (hausse/baisse/stable)
        - Probabilité de continuation vs rupture
        """
        if not forme_lettres or forme_lettres == "?????":
            return {"serie": None, "tendance": "inconnue", "proba_rupture": 0.5}
        
        # Série en cours
        serie_actuelle = forme_lettres[0]
        longueur_serie = 1
        for c in forme_lettres[1:]:
            if c == serie_actuelle:
                longueur_serie += 1
            else:
                break
        
        # Probabilité de rupture (régression vers la moyenne)
        # Plus la série est longue, plus elle a de chances de s'arrêter
        proba_rupture = min(0.85, 0.35 + (longueur_serie - 1) * 0.12)
        
        # Tendance sur les 5 derniers
        victoires = forme_lettres.count("V")
        defaites = forme_lettres.count("D")
        nuls = forme_lettres.count("N")
        
        if victoires >= 3:
            tendance = "hausse"
        elif defaites >= 3:
            tendance = "baisse"
        else:
            tendance = "stable"
        
        return {
            "serie": f"{longueur_serie}{serie_actuelle}" if longueur_serie >= 2 else None,
            "longueur": longueur_serie,
            "type_serie": serie_actuelle,
            "tendance": tendance,
            "proba_rupture": round(proba_rupture, 2),
            "stats": {"V": victoires, "N": nuls, "D": defaites}
        }
    
    @staticmethod
    def calculer_value_bet(proba_estimee: float, cote: float) -> Dict[str, Any]:
        """
        Calcule si un pari est une value bet.
        
        Value Bet = quand la probabilité réelle > probabilité implicite de la cote
        Expected Value (EV) = (proba × cote) - 1
        
        - EV > 0: Pari rentable à long terme
        - EV > 0.10: Bonne opportunité
        - EV > 0.20: Excellente opportunité
        """
        if cote <= 1.0:
            return {"is_value": False, "ev": -1, "qualite": "invalide"}
        
        proba_implicite = 1 / cote
        ev = (proba_estimee * cote) - 1
        
        # Qualité de l'opportunité
        if ev > 0.20:
            qualite = "excellente"
            emoji = "🔥"
        elif ev > 0.10:
            qualite = "bonne"
            emoji = "💎"
        elif ev > 0.05:
            qualite = "correcte"
            emoji = "✅"
        elif ev > 0:
            qualite = "marginale"
            emoji = "⚠️"
        else:
            qualite = "negative"
            emoji = "❌"
        
        return {
            "is_value": ev > 0,
            "ev": round(ev, 3),
            "ev_pct": round(ev * 100, 1),
            "proba_implicite": round(proba_implicite, 3),
            "ecart_proba": round(proba_estimee - proba_implicite, 3),
            "qualite": qualite,
            "emoji": emoji
        }
    
    @staticmethod
    def analyser_tendance_buts(forme: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyse la tendance de buts (over/under).
        """
        nb_matchs = forme.get("nb_matchs", 1) or 1
        buts_marques = forme.get("buts_marques", 0)
        buts_encaisses = forme.get("buts_encaisses", 0)
        
        moy_marques = buts_marques / nb_matchs
        moy_encaisses = buts_encaisses / nb_matchs
        moy_total = moy_marques + moy_encaisses
        
        # Classification
        if moy_total > 3.5:
            profil = "très_offensif"
            emoji = "⚽⚽⚽"
        elif moy_total > 2.8:
            profil = "offensif"
            emoji = "⚽⚽"
        elif moy_total > 2.0:
            profil = "equilibre"
            emoji = "⚖️"
        elif moy_total > 1.5:
            profil = "defensif"
            emoji = "🛡️"
        else:
            profil = "très_defensif"
            emoji = "🛡️🛡️"
        
        return {
            "moy_marques": round(moy_marques, 2),
            "moy_encaisses": round(moy_encaisses, 2),
            "moy_total": round(moy_total, 2),
            "profil": profil,
            "emoji": emoji,
            "recommandation_over": moy_total > 2.5
        }


def generer_analyse_complete(
    forme_dom: Dict[str, Any],
    forme_ext: Dict[str, Any],
    h2h: Dict[str, Any] = None,
    cotes: Dict[str, float] = None,
    championnat: str = None
) -> Dict[str, Any]:
    """
    Génère une analyse COMPLÈTE et intelligente d'un match.
    
    Returns:
        Dict avec:
        - score_global: Score de 0-100 sur la fiabilité de l'analyse
        - recommandation_principale: Le meilleur pari à faire
        - conseils: Liste de conseils détaillés
        - alertes: Signaux importants à considérer
        - stats_detaillees: Toutes les stats
    """
    analyseur = AnalyseurParis()
    conseils = []
    alertes = []
    
    # ═══════════════════════════════════════════════════════════
    # 1. ANALYSE DES SÉRIES
    # ═══════════════════════════════════════════════════════════
    serie_dom = analyseur.analyser_serie_complete(forme_dom.get("forme_str", ""))
    serie_ext = analyseur.analyser_serie_complete(forme_ext.get("forme_str", ""))
    
    # Conseil série domicile
    if serie_dom.get("serie"):
        type_s = serie_dom["type_serie"]
        long_s = serie_dom["longueur"]
        proba_rupt = serie_dom["proba_rupture"]
        
        if type_s == "V" and long_s >= 3:
            alertes.append({
                "type": "serie_victoires_dom",
                "emoji": "🔥",
                "titre": f"Série de {long_s} victoires (Dom)",
                "message": f"Attention: {proba_rupt:.0%} de chances que ça s'arrête",
                "impact": "prudence_dom"
            })
        elif type_s == "D" and long_s >= 3:
            conseils.append({
                "type": "rebond_attendu",
                "emoji": "📈",
                "titre": f"Rebond probable (Dom)",
                "message": f"Après {long_s} défaites, probabilité de victoire augmentée",
                "confiance": min(75, 50 + long_s * 5),
                "pari_suggere": "1",
                "mise": "2-3%"
            })
        elif type_s == "N" and long_s >= 2:
            alertes.append({
                "type": "serie_nuls_dom",
                "emoji": "⚖️",
                "titre": f"Équipe dom très équilibrée",
                "message": f"{long_s} nuls consécutifs - profil défensif?",
                "impact": "considerer_nul"
            })
    
    # Conseil série extérieur
    if serie_ext.get("serie"):
        type_s = serie_ext["type_serie"]
        long_s = serie_ext["longueur"]
        
        if type_s == "V" and long_s >= 3:
            conseils.append({
                "type": "forme_ext_excellente",
                "emoji": "✈️🔥",
                "titre": "Extérieur en grande forme",
                "message": f"{long_s} victoires d'affilée - équipe en confiance",
                "confiance": min(70, 50 + long_s * 4),
                "pari_suggere": "2",
                "mise": "2%"
            })
        elif type_s == "D" and long_s >= 4:
            alertes.append({
                "type": "crise_ext",
                "emoji": "📉",
                "titre": "Extérieur en crise",
                "message": f"{long_s} défaites - éviter de parier sur eux",
                "impact": "eviter_2"
            })
    
    # ═══════════════════════════════════════════════════════════
    # 2. ANALYSE RÉGRESSION VERS LA MOYENNE (Tous les résultats)
    # ═══════════════════════════════════════════════════════════
    sans_nul_dom = forme_dom.get("matchs_sans_nul", 0)
    sans_nul_ext = forme_ext.get("matchs_sans_nul", 0)
    
    # Nuls
    if sans_nul_dom >= 5 or sans_nul_ext >= 5:
        bonus_confiance = min(30, (sans_nul_dom + sans_nul_ext - 8) * 5)
        conseils.append({
            "type": "regression_nul",
            "emoji": "🎯",
            "titre": "Match Nul statistiquement probable",
            "message": f"Dom: {sans_nul_dom} matchs sans nul, Ext: {sans_nul_ext} matchs sans nul. "
                      f"La loi des grands nombres suggère un nul.",
            "confiance": 55 + bonus_confiance,
            "pari_suggere": "N",
            "mise": "2-3%" if (sans_nul_dom + sans_nul_ext) >= 10 else "1-2%"
        })
    
    # ═══════════════════════════════════════════════════════════
    # 3. ANALYSE TENDANCE BUTS
    # ═══════════════════════════════════════════════════════════
    buts_dom = analyseur.analyser_tendance_buts(forme_dom)
    buts_ext = analyseur.analyser_tendance_buts(forme_ext)
    
    moy_totale = (buts_dom["moy_total"] + buts_ext["moy_total"]) / 2
    
    if moy_totale > 3.2:
        conseils.append({
            "type": "over_25",
            "emoji": "⚽⚽⚽",
            "titre": "Over 2.5 très probable",
            "message": f"Moyenne combinée: {moy_totale:.1f} buts/match. "
                      f"Les deux équipes marquent beaucoup.",
            "confiance": min(75, 50 + (moy_totale - 2.5) * 15),
            "pari_suggere": "Over 2.5",
            "mise": "2-3%"
        })
    elif moy_totale < 2.0:
        conseils.append({
            "type": "under_25",
            "emoji": "🛡️",
            "titre": "Under 2.5 intéressant",
            "message": f"Moyenne combinée: {moy_totale:.1f} buts/match. "
                      f"Match défensif attendu.",
            "confiance": min(70, 50 + (2.5 - moy_totale) * 15),
            "pari_suggere": "Under 2.5",
            "mise": "2%"
        })
    
    # BTTS (Both Teams To Score)
    if buts_dom["moy_marques"] > 1.2 and buts_ext["moy_marques"] > 1.2:
        conseils.append({
            "type": "btts",
            "emoji": "⚽⚽",
            "titre": "Les 2 équipes marquent (BTTS)",
            "message": f"Dom: {buts_dom['moy_marques']:.1f} buts/match, "
                      f"Ext: {buts_ext['moy_marques']:.1f} buts/match",
            "confiance": 60,
            "pari_suggere": "BTTS Oui",
            "mise": "1-2%"
        })
    
    # ═══════════════════════════════════════════════════════════
    # 4. ANALYSE VALUE BETS (si cotes disponibles)
    # ═══════════════════════════════════════════════════════════
    value_bets = []
    
    if cotes:
        # Calculer nos probas estimées
        score_dom = forme_dom.get("score", 50)
        score_ext = forme_ext.get("score", 50)
        total = score_dom + score_ext + 40
        
        proba_dom = (score_dom + 12) / total  # +12 pour avantage domicile
        proba_ext = score_ext / total
        proba_nul = 40 / total
        
        # Ajuster pour la régression nuls
        if sans_nul_dom + sans_nul_ext >= 8:
            bonus = min(0.15, (sans_nul_dom + sans_nul_ext - 8) * 0.02)
            proba_nul += bonus
            proba_dom -= bonus / 2
            proba_ext -= bonus / 2
        
        # Normaliser
        total_p = proba_dom + proba_nul + proba_ext
        proba_dom /= total_p
        proba_nul /= total_p
        proba_ext /= total_p
        
        # Vérifier value bets
        for pari, proba, cote_key in [
            ("1", proba_dom, "domicile"),
            ("N", proba_nul, "nul"),
            ("2", proba_ext, "exterieur")
        ]:
            cote = cotes.get(cote_key, 2.0)
            vb = analyseur.calculer_value_bet(proba, cote)
            
            if vb["is_value"]:
                value_bets.append({
                    "pari": pari,
                    "cote": cote,
                    "proba_estimee": round(proba * 100, 1),
                    "ev": vb["ev_pct"],
                    "qualite": vb["qualite"],
                    "emoji": vb["emoji"]
                })
                
                if vb["qualite"] in ["excellente", "bonne"]:
                    conseils.append({
                        "type": "value_bet",
                        "emoji": vb["emoji"],
                        "titre": f"VALUE BET détectée: {pari}",
                        "message": f"Cote {cote:.2f} trop haute! "
                                  f"Notre estimation: {proba*100:.0f}% vs cote implicite {1/cote*100:.0f}%. "
                                  f"EV: +{vb['ev_pct']:.1f}%",
                        "confiance": min(80, 60 + vb["ev_pct"]),
                        "pari_suggere": pari,
                        "mise": "3-5%" if vb["qualite"] == "excellente" else "2-3%"
                    })
    
    # ═══════════════════════════════════════════════════════════
    # 5. ANALYSE DOMICILE/EXTÉRIEUR
    # ═══════════════════════════════════════════════════════════
    diff_forme = forme_dom.get("score", 50) - forme_ext.get("score", 50)
    
    if diff_forme > 25:
        conseils.append({
            "type": "favori_clair",
            "emoji": "🏠💪",
            "titre": "Domicile grand favori",
            "message": f"Écart de forme significatif (+{diff_forme:.0f} pts). "
                      f"Victoire domicile probable.",
            "confiance": min(75, 55 + diff_forme * 0.5),
            "pari_suggere": "1",
            "mise": "2-3%"
        })
    elif diff_forme < -20:
        conseils.append({
            "type": "upset_possible",
            "emoji": "✈️💪",
            "titre": "Extérieur en meilleure forme",
            "message": f"L'extérieur a {-diff_forme:.0f} pts de forme en plus. "
                      f"Attention au piège!",
            "confiance": min(65, 50 - diff_forme * 0.4),
            "pari_suggere": "2 ou N",
            "mise": "1-2%"
        })
    
    # ═══════════════════════════════════════════════════════════
    # 6. SCORE GLOBAL ET RECOMMANDATION
    # ═══════════════════════════════════════════════════════════
    
    # Trier les conseils par confiance
    conseils.sort(key=lambda x: x.get("confiance", 0), reverse=True)
    
    # Recommandation principale
    if conseils:
        meilleur = conseils[0]
        recommandation = {
            "pari": meilleur.get("pari_suggere", "?"),
            "confiance": meilleur.get("confiance", 50),
            "raison": meilleur.get("titre", ""),
            "mise": meilleur.get("mise", "1%")
        }
    else:
        recommandation = {
            "pari": "Éviter",
            "confiance": 30,
            "raison": "Pas assez de signaux clairs",
            "mise": "0%"
        }
    
    # Score global de fiabilité (basé sur quantité de données)
    nb_matchs_total = forme_dom.get("nb_matchs", 0) + forme_ext.get("nb_matchs", 0)
    score_donnees = min(100, nb_matchs_total * 10)
    score_conseils = len(conseils) * 10
    score_global = min(100, (score_donnees + score_conseils) / 2)
    
    return {
        "score_global": round(score_global),
        "recommandation": recommandation,
        "conseils": conseils[:5],  # Top 5 conseils
        "alertes": alertes,
        "value_bets": value_bets,
        "stats": {
            "forme_dom": forme_dom.get("score", 50),
            "forme_ext": forme_ext.get("score", 50),
            "serie_dom": serie_dom,
            "serie_ext": serie_ext,
            "buts_dom": buts_dom,
            "buts_ext": buts_ext,
            "moy_buts_match": moy_totale
        }
    }


def generer_resume_parieur(analyse: Dict[str, Any]) -> str:
    """
    Génère un résumé textuel friendly pour le parieur.
    """
    reco = analyse.get("recommandation", {})
    conseils = analyse.get("conseils", [])
    alertes = analyse.get("alertes", [])
    
    lignes = []
    
    # Recommandation principale
    confiance = reco.get("confiance", 0)
    if confiance >= 65:
        lignes.append(f"✅ **RECOMMANDÉ**: {reco.get('pari')} (confiance {confiance}%)")
    elif confiance >= 50:
        lignes.append(f"⚠️ **POSSIBLE**: {reco.get('pari')} (confiance {confiance}%)")
    else:
        lignes.append(f"❌ **À ÉVITER** - Match trop incertain")
    
    lignes.append(f"💰 Mise suggérée: {reco.get('mise', '?')}")
    lignes.append(f"📊 Raison: {reco.get('raison', '?')}")
    
    # Alertes importantes
    if alertes:
        lignes.append("\n⚠️ **ALERTES:**")
        for alerte in alertes[:2]:
            lignes.append(f"  {alerte['emoji']} {alerte['titre']}")
    
    return "\n".join(lignes)
