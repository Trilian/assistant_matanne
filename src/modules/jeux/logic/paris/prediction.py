"""
Prédiction des résultats de matchs.

Algorithme de prédiction basé sur:
- Forme récente (5 derniers matchs)
- Avantage domicile (+12%)
- Historique face-à-face
- Régression vers la moyenne
- Cotes des bookmakers
"""

from typing import Dict, Any, Optional, List
import logging

from .constants import AVANTAGE_DOMICILE, SEUIL_CONFIANCE_HAUTE, SEUIL_CONFIANCE_MOYENNE
from .forme import calculer_bonus_nul_regression

logger = logging.getLogger(__name__)


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
    
    Returns:
        Prédiction avec probabilités et confiance
    """
    # Étape 1: Probabilités de base selon la forme
    score_dom = forme_domicile.get("score", 50)
    score_ext = forme_exterieur.get("score", 50)
    
    total = score_dom + score_ext + 50
    proba_dom = score_dom / total
    proba_ext = score_ext / total
    proba_nul = 50 / total
    
    # Étape 2: Avantage domicile
    proba_dom += AVANTAGE_DOMICILE
    proba_ext -= AVANTAGE_DOMICILE * 0.7
    proba_nul -= AVANTAGE_DOMICILE * 0.3
    
    # Étape 3: Ajustement H2H
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
    
    # Étape 4: Régression vers la moyenne
    serie_dom = forme_domicile.get("serie_en_cours")
    serie_ext = forme_exterieur.get("serie_en_cours")
    
    if serie_dom and "D" in serie_dom:
        nb_defaites = int(serie_dom.replace("D", ""))
        if nb_defaites >= 3:
            proba_dom += 0.03 * (nb_defaites - 2)
    
    if serie_ext and "D" in serie_ext:
        nb_defaites = int(serie_ext.replace("D", ""))
        if nb_defaites >= 3:
            proba_ext += 0.03 * (nb_defaites - 2)
    
    if serie_dom and "V" in serie_dom:
        nb_victoires = int(serie_dom.replace("V", ""))
        if nb_victoires >= 5:
            proba_dom -= 0.02
    
    if serie_ext and "V" in serie_ext:
        nb_victoires = int(serie_ext.replace("V", ""))
        if nb_victoires >= 5:
            proba_ext -= 0.02
    
    # Étape 4b: Régression des nuls
    matchs_sans_nul_dom = forme_domicile.get("matchs_sans_nul", 0)
    matchs_sans_nul_ext = forme_exterieur.get("matchs_sans_nul", 0)
    
    bonus_nul = calculer_bonus_nul_regression(matchs_sans_nul_dom, matchs_sans_nul_ext)
    if bonus_nul > 0:
        proba_nul += bonus_nul
        proba_dom -= bonus_nul * 0.5
        proba_ext -= bonus_nul * 0.5
    
    # Étape 5: Ajustement selon les cotes
    if cotes:
        cote_dom = cotes.get("domicile", 2.0)
        cote_nul = cotes.get("nul", 3.5)
        cote_ext = cotes.get("exterieur", 3.0)
        
        proba_impl_dom = 1 / cote_dom
        proba_impl_nul = 1 / cote_nul
        proba_impl_ext = 1 / cote_ext
        total_impl = proba_impl_dom + proba_impl_nul + proba_impl_ext
        
        proba_impl_dom /= total_impl
        proba_impl_nul /= total_impl
        proba_impl_ext /= total_impl
        
        proba_dom = proba_dom * 0.9 + proba_impl_dom * 0.1
        proba_nul = proba_nul * 0.9 + proba_impl_nul * 0.1
        proba_ext = proba_ext * 0.9 + proba_impl_ext * 0.1
    
    # Normalisation finale
    total = proba_dom + proba_nul + proba_ext
    proba_dom /= total
    proba_nul /= total
    proba_ext /= total
    
    # Déterminer la prédiction
    probas = {"1": proba_dom, "N": proba_nul, "2": proba_ext}
    prediction = max(probas, key=probas.get)
    meilleure_proba = probas[prediction]
    
    # Calcul de la confiance
    probas_triees = sorted(probas.values(), reverse=True)
    ecart = probas_triees[0] - probas_triees[1]
    confiance = min(95, 40 + ecart * 150)
    
    if forme_domicile.get("nb_matchs", 0) < 3 or forme_exterieur.get("nb_matchs", 0) < 3:
        confiance *= 0.8
    
    # Générer les raisons
    raisons = _generer_raisons(
        forme_domicile, forme_exterieur, h2h, 
        serie_dom, serie_ext, bonus_nul,
        matchs_sans_nul_dom, matchs_sans_nul_ext
    )
    
    return {
        "prediction": prediction,
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


def _generer_raisons(
    forme_dom: Dict, forme_ext: Dict, h2h: Dict,
    serie_dom: str, serie_ext: str, bonus_nul: float,
    sans_nul_dom: int, sans_nul_ext: int
) -> List[str]:
    """Génère les raisons de la prédiction."""
    from .constants import SEUIL_SERIE_SANS_NUL
    
    raisons = []
    score_dom = forme_dom.get("score", 50)
    score_ext = forme_ext.get("score", 50)
    
    if score_dom > score_ext + 15:
        raisons.append(f"Forme domicile supérieure ({forme_dom.get('forme_str', '?')})")
    elif score_ext > score_dom + 15:
        raisons.append(f"Forme extérieur supérieure ({forme_ext.get('forme_str', '?')})")
    
    if serie_dom and "D" in serie_dom and int(serie_dom.replace("D", "")) >= 3:
        raisons.append(f"Régression attendue après {serie_dom}")
    
    if h2h.get("avantage") == "domicile":
        raisons.append("Historique favorable à domicile")
    elif h2h.get("avantage") == "exterieur":
        raisons.append("Historique favorable à l'extérieur")
    
    raisons.append("Avantage terrain (+12% domicile)")
    
    if bonus_nul > 0.05:
        if sans_nul_dom >= SEUIL_SERIE_SANS_NUL:
            raisons.append(f"⚠️ {sans_nul_dom} matchs sans nul (dom) → nul probable")
        if sans_nul_ext >= SEUIL_SERIE_SANS_NUL:
            raisons.append(f"⚠️ {sans_nul_ext} matchs sans nul (ext) → nul probable")
    
    return raisons


def generer_conseil_pari(
    prediction: str, 
    confiance: float, 
    cotes: Optional[Dict[str, float]] = None,
    proba_nul: float = 0.25
) -> str:
    """
    Génère un conseil de pari CONCRET basé sur la prédiction et la confiance.
    """
    labels = {"1": "Victoire domicile", "N": "Match nul", "2": "Victoire extérieur"}
    conseils = []
    
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
    
    if cotes:
        cle_cote = {"1": "domicile", "N": "nul", "2": "exterieur"}[prediction]
        cote_pred = cotes.get(cle_cote, 2.0)
        proba_modele = confiance / 100
        ev = (proba_modele * cote_pred) - 1
        
        if ev > 0.15:
            conseils.append(f"🔥 **VALUE BET**: Cote {cote_pred:.2f} trop haute! (EV: +{ev:.0%})")
        elif ev > 0.05:
            conseils.append(f"💎 Value détectée (EV: +{ev:.0%})")
        elif ev < -0.1:
            conseils.append(f"⛔ Cote trop basse, pas rentable (EV: {ev:.0%})")
    
    if proba_nul > 0.30:
        conseils.append("🎯 **ASTUCE**: Proba nul élevée, regarde la cote nul!")
    
    return " | ".join(conseils)


def predire_over_under(
    forme_domicile: Dict[str, Any],
    forme_exterieur: Dict[str, Any],
    seuil: float = 2.5
) -> Dict[str, Any]:
    """
    Prédit si le match aura plus ou moins de X buts.
    """
    nb_matchs_dom = forme_domicile.get("nb_matchs", 1) or 1
    nb_matchs_ext = forme_exterieur.get("nb_matchs", 1) or 1
    
    buts_marques_dom = forme_domicile.get("buts_marques", 0) / nb_matchs_dom
    buts_encaisses_dom = forme_domicile.get("buts_encaisses", 0) / nb_matchs_dom
    buts_marques_ext = forme_exterieur.get("buts_marques", 0) / nb_matchs_ext
    buts_encaisses_ext = forme_exterieur.get("buts_encaisses", 0) / nb_matchs_ext
    
    buts_attendus = (buts_marques_dom + buts_encaisses_ext) / 2 + \
                    (buts_marques_ext + buts_encaisses_dom) / 2
    
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
        "confiance": round(abs(proba_over - 0.5) * 200, 1)
    }


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
