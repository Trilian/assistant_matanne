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
        "nb_matchs": len(matchs)
    }


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
                         cotes: Optional[Dict[str, float]] = None) -> str:
    """
    Génère un conseil de pari basé sur la prédiction et la confiance.
    """
    labels = {"1": "Victoire domicile", "N": "Match nul", "2": "Victoire extérieur"}
    
    if confiance >= SEUIL_CONFIANCE_HAUTE:
        conseil = f"✅ {labels[prediction]} recommandé (confiance haute)"
    elif confiance >= SEUIL_CONFIANCE_MOYENNE:
        conseil = f"⚠️ {labels[prediction]} possible mais risqué"
    else:
        conseil = f"❌ Match trop incertain - éviter de parier"
    
    # Vérifier la value bet si cotes disponibles
    if cotes and confiance >= SEUIL_CONFIANCE_MOYENNE:
        proba_modele = confiance / 100
        cote_pred = cotes.get({
            "1": "domicile", 
            "N": "nul", 
            "2": "exterieur"
        }[prediction], 2.0)
        
        expected_value = (proba_modele * cote_pred) - 1
        if expected_value > 0.1:
            conseil += f" | 💰 Value bet détectée (EV: +{expected_value:.1%})"
    
    return conseil


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
