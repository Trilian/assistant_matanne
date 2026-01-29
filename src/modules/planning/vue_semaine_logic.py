"""
Logique métier du module Vue semaine (planning) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, datetime, time, timedelta
from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
HEURES_JOURNEE = list(range(0, 24))


# ═══════════════════════════════════════════════════════════
# NAVIGATION SEMAINE
# ═══════════════════════════════════════════════════════════

def get_debut_semaine(date_ref: Optional[date] = None) -> date:
    """Retourne le lundi de la semaine (début)."""
    if date_ref is None:
        date_ref = date.today()
    
    return date_ref - timedelta(days=date_ref.weekday())


def get_fin_semaine(date_ref: Optional[date] = None) -> date:
    """Retourne le dimanche de la semaine (fin)."""
    debut = get_debut_semaine(date_ref)
    return debut + timedelta(days=6)


def get_jours_semaine(date_ref: Optional[date] = None) -> List[date]:
    """Retourne tous les jours de la semaine."""
    debut = get_debut_semaine(date_ref)
    return [debut + timedelta(days=i) for i in range(7)]


def get_semaine_precedente(date_ref: date) -> date:
    """Retourne une date de la semaine précédente."""
    return date_ref - timedelta(days=7)


def get_semaine_suivante(date_ref: date) -> date:
    """Retourne une date de la semaine suivante."""
    return date_ref + timedelta(days=7)


def get_numero_semaine(date_ref: Optional[date] = None) -> int:
    """Retourne le numéro de semaine dans l'année."""
    if date_ref is None:
        date_ref = date.today()
    
    return date_ref.isocalendar()[1]


# ═══════════════════════════════════════════════════════════
# FILTRAGE ÉVÉNEMENTS
# ═══════════════════════════════════════════════════════════

def filtrer_evenements_semaine(evenements: List[Dict[str, Any]], date_ref: Optional[date] = None) -> List[Dict[str, Any]]:
    """Filtre les événements de la semaine."""
    debut = get_debut_semaine(date_ref)
    fin = get_fin_semaine(date_ref)
    
    resultats = []
    for evt in evenements:
        date_evt = evt.get("date")
        if isinstance(date_evt, str):
            date_evt = datetime.fromisoformat(date_evt).date()
        
        if debut <= date_evt <= fin:
            resultats.append(evt)
    
    return resultats


def filtrer_evenements_jour(evenements: List[Dict[str, Any]], jour: date) -> List[Dict[str, Any]]:
    """Filtre les événements d'un jour spécifique."""
    resultats = []
    
    for evt in evenements:
        date_evt = evt.get("date")
        if isinstance(date_evt, str):
            date_evt = datetime.fromisoformat(date_evt).date()
        
        if date_evt == jour:
            resultats.append(evt)
    
    return resultats


def grouper_evenements_par_jour(evenements: List[Dict[str, Any]]) -> Dict[date, List[Dict[str, Any]]]:
    """Groupe les événements par jour."""
    groupes = {}
    
    for evt in evenements:
        date_evt = evt.get("date")
        if isinstance(date_evt, str):
            date_evt = datetime.fromisoformat(date_evt).date()
        
        if date_evt not in groupes:
            groupes[date_evt] = []
        groupes[date_evt].append(evt)
    
    return groupes


def trier_evenements_par_heure(evenements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Trie les événements par heure."""
    def get_heure_key(evt):
        heure = evt.get("heure")
        if not heure:
            return time(0, 0)
        if isinstance(heure, str):
            heure = datetime.fromisoformat(heure).time()
        return heure
    
    return sorted(evenements, key=get_heure_key)


# ═══════════════════════════════════════════════════════════
# ANALYSE SEMAINE
# ═══════════════════════════════════════════════════════════

def calculer_charge_semaine(evenements: List[Dict[str, Any]], date_ref: Optional[date] = None) -> Dict[str, Any]:
    """Calcule la charge de travail de la semaine."""
    evt_semaine = filtrer_evenements_semaine(evenements, date_ref)
    jours = get_jours_semaine(date_ref)
    
    # Charge par jour
    charge_par_jour = {}
    for jour in jours:
        evt_jour = filtrer_evenements_jour(evt_semaine, jour)
        charge_par_jour[jour] = len(evt_jour)
    
    # Jour le plus chargé
    if charge_par_jour:
        jour_plus_charge = max(charge_par_jour.items(), key=lambda x: x[1])
    else:
        jour_plus_charge = None
    
    # Jours libres
    jours_libres = sum(1 for count in charge_par_jour.values() if count == 0)
    
    return {
        "total_evenements": len(evt_semaine),
        "charge_par_jour": charge_par_jour,
        "jour_plus_charge": jour_plus_charge,
        "jours_libres": jours_libres,
        "charge_moyenne": len(evt_semaine) / 7
    }


def detecter_conflits_horaires(evenements: List[Dict[str, Any]]) -> List[Tuple[Dict, Dict]]:
    """Détecte les conflits d'horaires dans la semaine."""
    conflits = []
    
    # Grouper par jour
    par_jour = grouper_evenements_par_jour(evenements)
    
    for jour, evt_jour in par_jour.items():
        evt_tries = trier_evenements_par_heure(evt_jour)
        
        for i in range(len(evt_tries)):
            evt1 = evt_tries[i]
            heure1 = evt1.get("heure")
            duree1 = evt1.get("duree", 60)  # minutes
            
            if not heure1:
                continue
            
            if isinstance(heure1, str):
                heure1 = datetime.fromisoformat(heure1).time()
            
            # Calculer heure de fin
            dt1 = datetime.combine(jour, heure1)
            fin1 = (dt1 + timedelta(minutes=duree1)).time()
            
            for j in range(i + 1, len(evt_tries)):
                evt2 = evt_tries[j]
                heure2 = evt2.get("heure")
                
                if not heure2:
                    continue
                
                if isinstance(heure2, str):
                    heure2 = datetime.fromisoformat(heure2).time()
                
                # Vérifier chevauchement
                if heure2 < fin1:
                    conflits.append((evt1, evt2))
    
    return conflits


def calculer_temps_libre(evenements: List[Dict[str, Any]], date_ref: Optional[date] = None) -> Dict[date, int]:
    """Calcule le temps libre par jour (en minutes)."""
    evt_semaine = filtrer_evenements_semaine(evenements, date_ref)
    jours = get_jours_semaine(date_ref)
    
    temps_libre = {}
    
    for jour in jours:
        evt_jour = filtrer_evenements_jour(evt_semaine, jour)
        
        # Calculer temps occupé
        temps_occupe = sum(evt.get("duree", 60) for evt in evt_jour)
        
        # Temps libre (sur 16h de veille = 960 min)
        temps_libre[jour] = max(0, 960 - temps_occupe)
    
    return temps_libre


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════

def calculer_statistiques_semaine(evenements: List[Dict[str, Any]], date_ref: Optional[date] = None) -> Dict[str, Any]:
    """Calcule les statistiques de la semaine."""
    evt_semaine = filtrer_evenements_semaine(evenements, date_ref)
    
    if not evt_semaine:
        return {
            "total": 0,
            "par_type": {},
            "duree_totale": 0,
            "duree_moyenne": 0
        }
    
    # Par type
    par_type = {}
    for evt in evt_semaine:
        type_evt = evt.get("type", "Autre")
        par_type[type_evt] = par_type.get(type_evt, 0) + 1
    
    # Durées
    duree_totale = sum(evt.get("duree", 60) for evt in evt_semaine)
    duree_moyenne = duree_totale / len(evt_semaine)
    
    return {
        "total": len(evt_semaine),
        "par_type": par_type,
        "duree_totale": duree_totale,
        "duree_moyenne": duree_moyenne
    }


# ═══════════════════════════════════════════════════════════
# RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════

def suggerer_creneaux_libres(evenements: List[Dict[str, Any]], jour: date, duree_minutes: int = 60) -> List[Dict[str, Any]]:
    """Suggère des créneaux libres dans la journée."""
    evt_jour = filtrer_evenements_jour(evenements, jour)
    evt_tries = trier_evenements_par_heure(evt_jour)
    
    creneaux_libres = []
    
    # Plage de travail: 8h-20h
    heure_debut = time(8, 0)
    heure_fin = time(20, 0)
    
    heure_actuelle = heure_debut
    
    for evt in evt_tries:
        heure_evt = evt.get("heure")
        if not heure_evt:
            continue
        
        if isinstance(heure_evt, str):
            heure_evt = datetime.fromisoformat(heure_evt).time()
        
        # Si gap suffisant avant l'événement
        dt_actuelle = datetime.combine(jour, heure_actuelle)
        dt_evt = datetime.combine(jour, heure_evt)
        
        gap_minutes = (dt_evt - dt_actuelle).total_seconds() / 60
        
        if gap_minutes >= duree_minutes:
            creneaux_libres.append({
                "debut": heure_actuelle,
                "fin": heure_evt,
                "duree": int(gap_minutes)
            })
        
        # Avancer après l'événement
        duree_evt = evt.get("duree", 60)
        dt_fin_evt = dt_evt + timedelta(minutes=duree_evt)
        heure_actuelle = dt_fin_evt.time()
    
    # Vérifier gap jusqu'à la fin de journée
    dt_actuelle = datetime.combine(jour, heure_actuelle)
    dt_fin = datetime.combine(jour, heure_fin)
    gap_final = (dt_fin - dt_actuelle).total_seconds() / 60
    
    if gap_final >= duree_minutes:
        creneaux_libres.append({
            "debut": heure_actuelle,
            "fin": heure_fin,
            "duree": int(gap_final)
        })
    
    return creneaux_libres


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════

def formater_periode_semaine(date_ref: Optional[date] = None) -> str:
    """Formate la période de la semaine."""
    debut = get_debut_semaine(date_ref)
    fin = get_fin_semaine(date_ref)
    
    return f"Semaine {get_numero_semaine(date_ref)} : {debut.strftime('%d/%m')} - {fin.strftime('%d/%m/%Y')}"


def formater_heure(heure: time) -> str:
    """Formate une heure."""
    if isinstance(heure, str):
        heure = datetime.fromisoformat(heure).time()
    
    return heure.strftime("%H:%M")
