"""
Logique métier du module Santé (famille) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

CATEGORIES_OBJECTIF = ["Sport", "Nutrition", "Sommeil", "Hydratation", "Poids", "Autre"]
UNITES = ["kg", "km", "heures", "litres", "calories", "min", "fois"]
TYPES_ACTIVITE = ["Marche", "Course", "Vélo", "Natation", "Musculation", "Yoga", "Autre"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# PROGRESSION DES OBJECTIFS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_progression_objectif(objectif: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule la progression d'un objectif.
    
    Args:
        objectif: Données de l'objectif
        
    Returns:
        Dictionnaire avec progression
    """
    valeur_actuelle = objectif.get("valeur_actuelle", 0.0)
    valeur_cible = objectif.get("valeur_cible", 100.0)
    
    if valeur_cible == 0:
        pourcentage = 0.0
    else:
        pourcentage = (valeur_actuelle / valeur_cible) * 100
    
    # Statut
    if pourcentage >= 100:
        statut = "Atteint"
    elif pourcentage >= 75:
        statut = "Presque atteint"
    elif pourcentage >= 50:
        statut = "En bonne voie"
    elif pourcentage >= 25:
        statut = "En cours"
    else:
        statut = "Démarrage"
    
    return {
        "pourcentage": min(pourcentage, 100.0),
        "statut": statut,
        "restant": max(valeur_cible - valeur_actuelle, 0)
    }


def estimer_date_achevement(objectif: Dict[str, Any], entrees_recentes: List[Dict[str, Any]]) -> Optional[date]:
    """
    Estime la date d'achèvement d'un objectif basé sur la progression récente.
    
    Args:
        objectif: Données de l'objectif
        entrees_recentes: Historique des progressions
        
    Returns:
        Date estimée ou None
    """
    if not entrees_recentes or len(entrees_recentes) < 2:
        return None
    
    valeur_actuelle = objectif.get("valeur_actuelle", 0.0)
    valeur_cible = objectif.get("valeur_cible", 100.0)
    
    if valeur_actuelle >= valeur_cible:
        return date.today()
    
    # Calculer progression moyenne par jour
    periode_jours = 7
    entrees_periode = entrees_recentes[-periode_jours:]
    
    if len(entrees_periode) < 2:
        return None
    
    progression_totale = entrees_periode[-1].get("valeur", 0) - entrees_periode[0].get("valeur", 0)
    progression_par_jour = progression_totale / len(entrees_periode)
    
    if progression_par_jour <= 0:
        return None
    
    restant = valeur_cible - valeur_actuelle
    jours_restants = int(restant / progression_par_jour)
    
    return date.today() + timedelta(days=jours_restants)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_sante(objectifs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques santé globales.
    
    Args:
        objectifs: Liste des objectifs
        
    Returns:
        Dictionnaire de statistiques
    """
    total = len(objectifs)
    
    if total == 0:
        return {
            "total_objectifs": 0,
            "atteints": 0,
            "en_cours": 0,
            "taux_reussite": 0.0,
            "par_categorie": {}
        }
    
    # Compter par statut
    atteints = 0
    en_cours = 0
    
    for objectif in objectifs:
        prog = calculer_progression_objectif(objectif)
        if prog["statut"] == "Atteint":
            atteints += 1
        else:
            en_cours += 1
    
    # Par catégorie
    par_categorie = {}
    for objectif in objectifs:
        cat = objectif.get("categorie", "Autre")
        par_categorie[cat] = par_categorie.get(cat, 0) + 1
    
    return {
        "total_objectifs": total,
        "atteints": atteints,
        "en_cours": en_cours,
        "taux_reussite": (atteints / total * 100) if total > 0 else 0.0,
        "par_categorie": par_categorie
    }


def analyser_activites(entrees: List[Dict[str, Any]], jours: int = 30) -> Dict[str, Any]:
    """
    Analyse les activités sportives sur une période.
    
    Args:
        entrees: Liste des entrées d'activité
        jours: Nombre de jours à analyser
        
    Returns:
        Statistiques d'activités
    """
    date_limite = date.today() - timedelta(days=jours)
    
    entrees_periode = []
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite:
            entrees_periode.append(entree)
    
    # Par type d'activité
    par_type = {}
    duree_totale = 0
    
    for entree in entrees_periode:
        type_act = entree.get("type_activite", "Autre")
        par_type[type_act] = par_type.get(type_act, 0) + 1
        
        duree = entree.get("duree", 0)
        duree_totale += duree
    
    # Fréquence par semaine
    frequence_hebdo = len(entrees_periode) / (jours / 7) if jours > 0 else 0
    
    return {
        "total_seances": len(entrees_periode),
        "par_type": par_type,
        "duree_totale_minutes": duree_totale,
        "duree_moyenne": duree_totale / len(entrees_periode) if entrees_periode else 0,
        "frequence_hebdo": frequence_hebdo
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_objectif(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide un objectif santé.
    
    Args:
        data: Données de l'objectif
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_OBJECTIF:
        erreurs.append(f"Catégorie invalide. Valeurs autorisées: {', '.join(CATEGORIES_OBJECTIF)}")
    
    if "valeur_cible" in data:
        cible = data["valeur_cible"]
        if not isinstance(cible, (int, float)) or cible <= 0:
            erreurs.append("La valeur cible doit être > 0")
    
    if "unite" in data and data["unite"] not in UNITES:
        erreurs.append(f"Unité invalide. Valeurs autorisées: {', '.join(UNITES)}")
    
    return len(erreurs) == 0, erreurs


def valider_entree_activite(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide une entrée d'activité.
    
    Args:
        data: Données de l'activité
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "type_activite" in data and data["type_activite"] not in TYPES_ACTIVITE:
        erreurs.append(f"Type d'activité invalide. Valeurs autorisées: {', '.join(TYPES_ACTIVITE)}")
    
    if "duree" in data:
        duree = data["duree"]
        if not isinstance(duree, (int, float)) or duree <= 0:
            erreurs.append("La durée doit être > 0")
    
    return len(erreurs) == 0, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_objectif_label(objectif: Dict[str, Any]) -> str:
    """
    Formate le label d'un objectif.
    
    Args:
        objectif: Données de l'objectif
        
    Returns:
        Label formaté
    """
    titre = objectif.get("titre", "Objectif")
    prog = calculer_progression_objectif(objectif)
    
    return f"{titre} - {prog['pourcentage']:.0f}% ({prog['statut']})"


def formater_activite_resume(entree: Dict[str, Any]) -> str:
    """
    Formate le résumé d'une activité.
    
    Args:
        entree: Données de l'activité
        
    Returns:
        Résumé formaté
    """
    type_act = entree.get("type_activite", "Activité")
    duree = entree.get("duree", 0)
    
    return f"{type_act} - {duree} min"

