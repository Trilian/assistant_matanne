"""
Statistiques et analyse des performances de paris.

FonctionnalitÃes:
- Calcul des performances (gains, ROI)
- Analyse des tendances par championnat
- Suivi des streaks
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def calculer_performance_paris(paris: List[Dict[str, Any]], periode_jours: int = 30) -> Dict[str, Any]:
    """
    Calcule les statistiques de performance sur une pÃeriode.
    
    Args:
        paris: Liste des paris effectuÃes
        periode_jours: Nombre de jours Ã  analyser
        
    Returns:
        MÃetriques de performance
    """
    if not paris:
        return {
            "nb_paris": 0,
            "gagnes": 0,
            "perdus": 0,
            "taux_reussite": 0.0,
            "gain_total": 0.0,
            "roi": 0.0,
            "meilleur_gain": 0.0,
            "pire_perte": 0.0,
            "streak_actuel": None
        }
    
    date_limite = datetime.now() - timedelta(days=periode_jours)
    paris_recents = [
        p for p in paris 
        if p.get("date") and p["date"] >= date_limite
    ]
    
    if not paris_recents:
        paris_recents = paris
    
    gagnes = [p for p in paris_recents if p.get("resultat") == "gagne"]
    perdus = [p for p in paris_recents if p.get("resultat") == "perdu"]
    
    mise_totale = sum(p.get("mise", 0) for p in paris_recents)
    gains_bruts = sum(
        p.get("mise", 0) * p.get("cote", 1) 
        for p in gagnes
    )
    gain_net = gains_bruts - mise_totale
    
    gains_individuels = [p.get("mise", 0) * (p.get("cote", 1) - 1) for p in gagnes]
    pertes_individuelles = [-p.get("mise", 0) for p in perdus]
    
    # Calcul du streak actuel
    streak = None
    if paris_recents:
        paris_tries = sorted(paris_recents, key=lambda x: x.get("date") or datetime.min, reverse=True)
        premier_resultat = paris_tries[0].get("resultat")
        count = 0
        for p in paris_tries:
            if p.get("resultat") == premier_resultat:
                count += 1
            else:
                break
        if count >= 2:
            streak = f"{count} {'gagnÃes' if premier_resultat == 'gagne' else 'perdus'}"
    
    nb_paris = len(paris_recents)
    return {
        "nb_paris": nb_paris,
        "gagnes": len(gagnes),
        "perdus": len(perdus),
        "en_cours": nb_paris - len(gagnes) - len(perdus),
        "taux_reussite": round(len(gagnes) / nb_paris * 100, 1) if nb_paris > 0 else 0.0,
        "mise_totale": round(mise_totale, 2),
        "gain_brut": round(gains_bruts, 2),
        "gain_net": round(gain_net, 2),
        "roi": round(gain_net / mise_totale * 100, 1) if mise_totale > 0 else 0.0,
        "meilleur_gain": round(max(gains_individuels) if gains_individuels else 0.0, 2),
        "pire_perte": round(min(pertes_individuelles) if pertes_individuelles else 0.0, 2),
        "streak_actuel": streak
    }


def analyser_tendances_championnat(
    matchs: List[Dict[str, Any]], 
    championnat: str
) -> Dict[str, Any]:
    """
    Analyse les tendances d'un championnat.
    
    Args:
        matchs: Matchs du championnat
        championnat: Nom du championnat
        
    Returns:
        Tendances dÃetectÃees
    """
    if not matchs:
        return {
            "championnat": championnat,
            "nb_matchs": 0,
            "stats": {},
            "tendances": []
        }
    
    stats = {
        "victoires_dom": 0,
        "nuls": 0,
        "victoires_ext": 0,
        "buts_total": 0,
        "matchs_over_2_5": 0,
        "matchs_btts": 0  # Both Teams To Score
    }
    
    equipes_stats = defaultdict(lambda: {"v": 0, "n": 0, "d": 0, "bp": 0, "bc": 0})
    
    for match in matchs:
        score_dom = match.get("score_domicile", 0) or 0
        score_ext = match.get("score_exterieur", 0) or 0
        
        if score_dom > score_ext:
            stats["victoires_dom"] += 1
        elif score_ext > score_dom:
            stats["victoires_ext"] += 1
        else:
            stats["nuls"] += 1
        
        total_buts = score_dom + score_ext
        stats["buts_total"] += total_buts
        
        if total_buts > 2.5:
            stats["matchs_over_2_5"] += 1
        
        if score_dom > 0 and score_ext > 0:
            stats["matchs_btts"] += 1
        
        # Stats par Ãequipe
        eq_dom = match.get("equipe_domicile_id")
        eq_ext = match.get("equipe_exterieur_id")
        
        if eq_dom:
            equipes_stats[eq_dom]["bp"] += score_dom
            equipes_stats[eq_dom]["bc"] += score_ext
            if score_dom > score_ext:
                equipes_stats[eq_dom]["v"] += 1
            elif score_dom < score_ext:
                equipes_stats[eq_dom]["d"] += 1
            else:
                equipes_stats[eq_dom]["n"] += 1
        
        if eq_ext:
            equipes_stats[eq_ext]["bp"] += score_ext
            equipes_stats[eq_ext]["bc"] += score_dom
            if score_ext > score_dom:
                equipes_stats[eq_ext]["v"] += 1
            elif score_ext < score_dom:
                equipes_stats[eq_ext]["d"] += 1
            else:
                equipes_stats[eq_ext]["n"] += 1
    
    nb_matchs = len(matchs)
    
    stats["pct_victoires_dom"] = round(stats["victoires_dom"] / nb_matchs * 100, 1)
    stats["pct_nuls"] = round(stats["nuls"] / nb_matchs * 100, 1)
    stats["pct_victoires_ext"] = round(stats["victoires_ext"] / nb_matchs * 100, 1)
    stats["buts_par_match"] = round(stats["buts_total"] / nb_matchs, 2)
    stats["pct_over_2_5"] = round(stats["matchs_over_2_5"] / nb_matchs * 100, 1)
    stats["pct_btts"] = round(stats["matchs_btts"] / nb_matchs * 100, 1)
    
    # DÃetecter les tendances
    tendances = []
    
    if stats["pct_victoires_dom"] > 50:
        tendances.append(f"ðŸ  Forte domination domicile ({stats['pct_victoires_dom']}%)")
    elif stats["pct_victoires_dom"] < 35:
        tendances.append(f"âœˆï¸ Bons rÃesultats extÃerieurs ({stats['pct_victoires_ext']}%)")
    
    if stats["pct_nuls"] > 30:
        tendances.append(f"ðŸ¤ Beaucoup de nuls ({stats['pct_nuls']}%)")
    
    if stats["pct_over_2_5"] > 55:
        tendances.append(f"âš½ Championnat offensif ({stats['buts_par_match']:.1f} buts/match)")
    elif stats["pct_over_2_5"] < 40:
        tendances.append(f"ðŸ›¡ï¸ Championnat dÃefensif ({stats['buts_par_match']:.1f} buts/match)")
    
    if stats["pct_btts"] > 55:
        tendances.append(f"âœ… BTTS frÃequent ({stats['pct_btts']}%)")
    
    return {
        "championnat": championnat,
        "nb_matchs": nb_matchs,
        "stats": stats,
        "tendances": tendances,
        "equipes_stats": dict(equipes_stats)
    }


def calculer_regularite_equipe(matchs: List[Dict[str, Any]], equipe_id: int) -> Dict[str, Any]:
    """
    Calcule la rÃegularitÃe d'une Ãequipe (variance des performances).
    
    Une Ãequipe rÃegulière est plus prÃevisible pour les paris.
    """
    if not matchs:
        return {"regularite": 0, "niveau": "inconnu"}
    
    resultats = []
    for match in matchs:
        est_dom = match.get("equipe_domicile_id") == equipe_id
        score_eq = match.get("score_domicile" if est_dom else "score_exterieur", 0) or 0
        score_adv = match.get("score_exterieur" if est_dom else "score_domicile", 0) or 0
        
        diff = score_eq - score_adv
        resultats.append(diff)
    
    if len(resultats) < 3:
        return {"regularite": 50, "niveau": "insuffisant"}
    
    # Calculer la variance
    moyenne = sum(resultats) / len(resultats)
    variance = sum((r - moyenne) ** 2 for r in resultats) / len(resultats)
    ecart_type = variance ** 0.5
    
    # Score de rÃegularitÃe (inverse de la variance)
    regularite = max(0, 100 - ecart_type * 20)
    
    if regularite > 70:
        niveau = "très rÃegulier"
    elif regularite > 50:
        niveau = "rÃegulier"
    elif regularite > 30:
        niveau = "irrÃegulier"
    else:
        niveau = "très irrÃegulier"
    
    return {
        "regularite": round(regularite, 1),
        "niveau": niveau,
        "ecart_type": round(ecart_type, 2),
        "moyenne_diff_buts": round(moyenne, 2)
    }
