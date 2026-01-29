"""
Logique métier du module Calendrier (planning) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
MOIS_ANNEE = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", 
              "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# NAVIGATION CALENDRIER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_premier_jour_mois(annee: int, mois: int) -> date:
    """Retourne le premier jour du mois."""
    return date(annee, mois, 1)


def get_dernier_jour_mois(annee: int, mois: int) -> date:
    """Retourne le dernier jour du mois."""
    if mois == 12:
        return date(annee, 12, 31)
    else:
        return date(annee, mois + 1, 1) - timedelta(days=1)


def get_jours_mois(annee: int, mois: int) -> List[date]:
    """Retourne tous les jours d'un mois."""
    premier = get_premier_jour_mois(annee, mois)
    dernier = get_dernier_jour_mois(annee, mois)
    
    jours = []
    jour_actuel = premier
    
    while jour_actuel <= dernier:
        jours.append(jour_actuel)
        jour_actuel += timedelta(days=1)
    
    return jours


def get_semaines_mois(annee: int, mois: int) -> List[List[Optional[date]]]:
    """Retourne les semaines du mois avec padding pour l'alignement."""
    jours = get_jours_mois(annee, mois)
    premier_jour = jours[0]
    
    # Padding début (lundi = 0)
    jour_semaine_debut = premier_jour.weekday()
    semaines = [[None] * jour_semaine_debut]
    
    semaine_courante = semaines[0]
    
    for jour in jours:
        if len(semaine_courante) == 7:
            semaine_courante = []
            semaines.append(semaine_courante)
        semaine_courante.append(jour)
    
    # Padding fin
    while len(semaine_courante) < 7:
        semaine_courante.append(None)
    
    return semaines


def get_mois_precedent(annee: int, mois: int) -> Tuple[int, int]:
    """Retourne (année, mois) du mois précédent."""
    if mois == 1:
        return (annee - 1, 12)
    else:
        return (annee, mois - 1)


def get_mois_suivant(annee: int, mois: int) -> Tuple[int, int]:
    """Retourne (année, mois) du mois suivant."""
    if mois == 12:
        return (annee + 1, 1)
    else:
        return (annee, mois + 1)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰VÃ‰NEMENTS CALENDRIER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

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


def filtrer_evenements_mois(evenements: List[Dict[str, Any]], annee: int, mois: int) -> List[Dict[str, Any]]:
    """Filtre les événements d'un mois."""
    premier = get_premier_jour_mois(annee, mois)
    dernier = get_dernier_jour_mois(annee, mois)
    
    resultats = []
    
    for evt in evenements:
        date_evt = evt.get("date")
        if isinstance(date_evt, str):
            date_evt = datetime.fromisoformat(date_evt).date()
        
        if premier <= date_evt <= dernier:
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


def compter_evenements_par_jour(evenements: List[Dict[str, Any]], jour: date) -> int:
    """Compte le nombre d'événements pour un jour."""
    return len(filtrer_evenements_jour(evenements, jour))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES CALENDRIER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_mois(evenements: List[Dict[str, Any]], annee: int, mois: int) -> Dict[str, Any]:
    """Calcule les statistiques du mois."""
    evt_mois = filtrer_evenements_mois(evenements, annee, mois)
    
    if not evt_mois:
        return {
            "total": 0,
            "par_type": {},
            "jour_plus_charge": None,
            "jours_libres": get_nombre_jours_mois(annee, mois)
        }
    
    # Par type
    par_type = {}
    for evt in evt_mois:
        type_evt = evt.get("type", "Autre")
        par_type[type_evt] = par_type.get(type_evt, 0) + 1
    
    # Jour le plus chargé
    groupes = grouper_evenements_par_jour(evt_mois)
    jour_plus_charge = max(groupes.items(), key=lambda x: len(x[1]))[0] if groupes else None
    
    # Jours libres
    jours_avec_evt = len(groupes)
    total_jours = get_nombre_jours_mois(annee, mois)
    jours_libres = total_jours - jours_avec_evt
    
    return {
        "total": len(evt_mois),
        "par_type": par_type,
        "jour_plus_charge": jour_plus_charge,
        "jours_libres": jours_libres
    }


def get_nombre_jours_mois(annee: int, mois: int) -> int:
    """Retourne le nombre de jours dans un mois."""
    return len(get_jours_mois(annee, mois))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_date_complete(date_obj: date, inclure_jour: bool = True) -> str:
    """Formate une date complète en français."""
    if inclure_jour:
        jour_semaine = JOURS_SEMAINE[date_obj.weekday()]
        return f"{jour_semaine} {date_obj.day} {MOIS_ANNEE[date_obj.month - 1]} {date_obj.year}"
    else:
        return f"{date_obj.day} {MOIS_ANNEE[date_obj.month - 1]} {date_obj.year}"


def formater_mois_annee(annee: int, mois: int) -> str:
    """Formate mois et année."""
    return f"{MOIS_ANNEE[mois - 1]} {annee}"


def est_aujourdhui(jour: date) -> bool:
    """Vérifie si un jour est aujourd'hui."""
    return jour == date.today()


def est_weekend(jour: date) -> bool:
    """Vérifie si un jour est un weekend."""
    return jour.weekday() >= 5  # Samedi=5, Dimanche=6


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_date_mois(annee: int, mois: int) -> tuple[bool, Optional[str]]:
    """Valide une date de mois."""
    if not 1 <= mois <= 12:
        return False, "Le mois doit être entre 1 et 12"
    
    if annee < 2000 or annee > 2100:
        return False, "L'année doit être entre 2000 et 2100"
    
    return True, None

