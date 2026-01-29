"""
Logique métier du module Routines (famille) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, time, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

MOMENTS_JOURNEE = ["Matin", "Midi", "Après-midi", "Soir", "Nuit"]
TYPES_ROUTINE = ["Réveil", "Repas", "Sieste", "Bain", "Coucher", "Soins", "Autre"]
JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GESTION DU TEMPS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_moment_journee(heure: time) -> str:
    """Détermine le moment de la journée d'après l'heure."""
    if isinstance(heure, str):
        from datetime import datetime
        heure = datetime.fromisoformat(heure).time()
    
    h = heure.hour
    
    if 5 <= h < 12:
        return "Matin"
    elif 12 <= h < 14:
        return "Midi"
    elif 14 <= h < 18:
        return "Après-midi"
    elif 18 <= h < 22:
        return "Soir"
    else:
        return "Nuit"


def calculer_duree_routine(routines: List[Dict[str, Any]]) -> int:
    """Calcule la durée totale d'une séquence de routines (en minutes)."""
    duree_totale = 0
    
    for routine in routines:
        duree = routine.get("duree", 0)
        duree_totale += duree
    
    return duree_totale


def calculer_heure_fin(heure_debut: time, duree_minutes: int) -> time:
    """Calcule l'heure de fin d'après le début et la durée."""
    from datetime import datetime
    
    if isinstance(heure_debut, str):
        heure_debut = datetime.fromisoformat(heure_debut).time()
    
    debut_dt = datetime.combine(date.today(), heure_debut)
    fin_dt = debut_dt + timedelta(minutes=duree_minutes)
    
    return fin_dt.time()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FILTRAGE ET ORGANISATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def filtrer_par_moment(routines: List[Dict[str, Any]], moment: str) -> List[Dict[str, Any]]:
    """Filtre les routines par moment de la journée."""
    return [r for r in routines if r.get("moment") == moment]


def filtrer_par_jour(routines: List[Dict[str, Any]], jour: str) -> List[Dict[str, Any]]:
    """Filtre les routines par jour de la semaine."""
    resultats = []
    
    for routine in routines:
        jours_actifs = routine.get("jours_actifs", JOURS_SEMAINE)
        if jour in jours_actifs:
            resultats.append(routine)
    
    return resultats


def get_routines_aujourdhui(routines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retourne les routines du jour actuel."""
    jour_actuel = JOURS_SEMAINE[date.today().weekday()]
    return filtrer_par_jour(routines, jour_actuel)


def grouper_par_moment(routines: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Groupe les routines par moment de la journée."""
    groupes = {moment: [] for moment in MOMENTS_JOURNEE}
    
    for routine in routines:
        moment = routine.get("moment", "Autre")
        if moment in groupes:
            groupes[moment].append(routine)
        else:
            if "Autre" not in groupes:
                groupes["Autre"] = []
            groupes["Autre"].append(routine)
    
    return groupes


def trier_par_heure(routines: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trie les routines par heure de début."""
    def get_heure_key(routine):
        heure = routine.get("heure")
        if not heure:
            return time(23, 59)
        if isinstance(heure, str):
            from datetime import datetime
            heure = datetime.fromisoformat(heure).time()
        return heure
    
    return sorted(routines, key=get_heure_key)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES ET ANALYSE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_routines(routines: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcule les statistiques des routines."""
    total = len(routines)
    
    if total == 0:
        return {
            "total": 0,
            "par_type": {},
            "par_moment": {},
            "duree_totale_jour": 0
        }
    
    # Par type
    par_type = {}
    for routine in routines:
        type_r = routine.get("type", "Autre")
        par_type[type_r] = par_type.get(type_r, 0) + 1
    
    # Par moment
    par_moment = {}
    for routine in routines:
        moment = routine.get("moment", "Autre")
        par_moment[moment] = par_moment.get(moment, 0) + 1
    
    # Durée totale
    duree_totale = calculer_duree_routine(routines)
    
    return {
        "total": total,
        "par_type": par_type,
        "par_moment": par_moment,
        "duree_totale_jour": duree_totale
    }


def analyser_regularite(historique: List[Dict[str, Any]], routine_id: int, jours: int = 7) -> Dict[str, Any]:
    """Analyse la régularité d'exécution d'une routine."""
    date_limite = date.today() - timedelta(days=jours)
    
    executions = []
    for entry in historique:
        if entry.get("routine_id") == routine_id:
            date_exec = entry.get("date")
            if isinstance(date_exec, str):
                from datetime import datetime
                date_exec = datetime.fromisoformat(date_exec).date()
            
            if date_exec >= date_limite:
                executions.append(entry)
    
    taux_realisation = (len(executions) / jours * 100) if jours > 0 else 0
    
    # Régularité
    if taux_realisation >= 90:
        regularite = "Excellent"
    elif taux_realisation >= 70:
        regularite = "Bon"
    elif taux_realisation >= 50:
        regularite = "Moyen"
    else:
        regularite = "Faible"
    
    return {
        "executions": len(executions),
        "jours_analyses": jours,
        "taux_realisation": taux_realisation,
        "regularite": regularite
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def suggerer_routines_age(age_mois: int) -> List[Dict[str, Any]]:
    """Suggère des routines adaptées à l'Ã¢ge."""
    suggestions = []
    
    # Routines communes
    suggestions.append({
        "titre": "Réveil",
        "type": "Réveil",
        "moment": "Matin",
        "heure": "07:00",
        "duree": 15
    })
    
    if age_mois < 12:
        suggestions.extend([
            {"titre": "Sieste matin", "type": "Sieste", "moment": "Matin", "heure": "10:00", "duree": 60},
            {"titre": "Sieste après-midi", "type": "Sieste", "moment": "Après-midi", "heure": "14:00", "duree": 90},
            {"titre": "Bain", "type": "Bain", "moment": "Soir", "heure": "19:00", "duree": 20},
            {"titre": "Coucher", "type": "Coucher", "moment": "Soir", "heure": "20:00", "duree": 15}
        ])
    elif age_mois < 24:
        suggestions.extend([
            {"titre": "Sieste après-midi", "type": "Sieste", "moment": "Après-midi", "heure": "13:30", "duree": 120},
            {"titre": "Bain", "type": "Bain", "moment": "Soir", "heure": "19:30", "duree": 25},
            {"titre": "Coucher", "type": "Coucher", "moment": "Soir", "heure": "20:30", "duree": 20}
        ])
    else:
        suggestions.extend([
            {"titre": "Sieste (optionnelle)", "type": "Sieste", "moment": "Après-midi", "heure": "14:00", "duree": 60},
            {"titre": "Bain", "type": "Bain", "moment": "Soir", "heure": "20:00", "duree": 30},
            {"titre": "Coucher", "type": "Coucher", "moment": "Soir", "heure": "21:00", "duree": 20}
        ])
    
    return suggestions


def detecter_conflits_horaires(routines: List[Dict[str, Any]]) -> List[tuple[Dict, Dict]]:
    """Détecte les conflits d'horaires entre routines."""
    conflits = []
    routines_triees = trier_par_heure(routines)
    
    for i in range(len(routines_triees)):
        r1 = routines_triees[i]
        heure1 = r1.get("heure")
        duree1 = r1.get("duree", 0)
        
        if not heure1:
            continue
        
        if isinstance(heure1, str):
            from datetime import datetime
            heure1 = datetime.fromisoformat(heure1).time()
        
        fin1 = calculer_heure_fin(heure1, duree1)
        
        for j in range(i + 1, len(routines_triees)):
            r2 = routines_triees[j]
            heure2 = r2.get("heure")
            
            if not heure2:
                continue
            
            if isinstance(heure2, str):
                from datetime import datetime
                heure2 = datetime.fromisoformat(heure2).time()
            
            # Vérifier chevauchement
            if heure2 < fin1:
                conflits.append((r1, r2))
    
    return conflits


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_routine(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Valide une routine."""
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "type" in data and data["type"] not in TYPES_ROUTINE:
        erreurs.append(f"Type invalide. Valeurs: {', '.join(TYPES_ROUTINE)}")
    
    if "moment" in data and data["moment"] not in MOMENTS_JOURNEE:
        erreurs.append(f"Moment invalide. Valeurs: {', '.join(MOMENTS_JOURNEE)}")
    
    if "duree" in data:
        duree = data["duree"]
        if not isinstance(duree, int) or duree <= 0:
            erreurs.append("La durée doit être > 0")
    
    return len(erreurs) == 0, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_heure(heure: time) -> str:
    """Formate une heure."""
    if isinstance(heure, str):
        from datetime import datetime
        heure = datetime.fromisoformat(heure).time()
    
    return heure.strftime("%H:%M")


def formater_duree(minutes: int) -> str:
    """Formate une durée."""
    if minutes < 60:
        return f"{minutes}min"
    else:
        heures = minutes // 60
        mins = minutes % 60
        if mins > 0:
            return f"{heures}h{mins:02d}"
        else:
            return f"{heures}h"

