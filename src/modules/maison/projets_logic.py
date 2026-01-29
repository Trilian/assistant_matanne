"""
Logique métier du module Projets (maison) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

STATUTS_PROJET = ["À faire", "En cours", "Terminé", "En pause"]
PRIORITES = ["Basse", "Moyenne", "Haute", "Urgente"]
CATEGORIES_PROJET = ["Rénovation", "Décoration", "Réparation", "Amélioration", "Autre"]


# ═══════════════════════════════════════════════════════════
# CALCUL DES PRIORITÉS ET URGENCES
# ═══════════════════════════════════════════════════════════

def calculer_urgence_projet(projet: Dict[str, Any]) -> str:
    """
    Calcule le niveau d'urgence d'un projet.
    
    Args:
        projet: Données du projet
        
    Returns:
        Niveau d'urgence
    """
    priorite = projet.get("priorite", "Moyenne")
    date_limite = projet.get("date_limite")
    
    if not date_limite:
        return priorite
    
    if isinstance(date_limite, str):
        from datetime import datetime
        date_limite = datetime.fromisoformat(date_limite).date()
    
    jours_restants = (date_limite - date.today()).days
    
    # Urgent si moins de 7 jours ou déjà priorité haute
    if jours_restants < 7 or priorite == "Urgente":
        return "Urgente"
    elif jours_restants < 14 and priorite in ["Haute", "Moyenne"]:
        return "Haute"
    else:
        return priorite


def calculer_jours_restants(projet: Dict[str, Any]) -> Optional[int]:
    """
    Calcule les jours restants avant la date limite.
    
    Args:
        projet: Données du projet
        
    Returns:
        Nombre de jours (négatif si dépassé)
    """
    date_limite = projet.get("date_limite")
    
    if not date_limite:
        return None
    
    if isinstance(date_limite, str):
        from datetime import datetime
        date_limite = datetime.fromisoformat(date_limite).date()
    
    return (date_limite - date.today()).days


# ═══════════════════════════════════════════════════════════
# FILTRAGE ET TRI
# ═══════════════════════════════════════════════════════════

def filtrer_par_statut(projets: List[Dict[str, Any]], statut: str) -> List[Dict[str, Any]]:
    """Filtre les projets par statut."""
    return [p for p in projets if p.get("statut") == statut]


def filtrer_par_priorite(projets: List[Dict[str, Any]], priorite: str) -> List[Dict[str, Any]]:
    """Filtre les projets par priorité."""
    return [p for p in projets if p.get("priorite") == priorite]


def filtrer_par_categorie(projets: List[Dict[str, Any]], categorie: str) -> List[Dict[str, Any]]:
    """Filtre les projets par catégorie."""
    return [p for p in projets if p.get("categorie") == categorie]


def get_projets_urgents(projets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retourne les projets urgents.
    
    Args:
        projets: Liste des projets
        
    Returns:
        Liste des projets urgents triés
    """
    urgents = []
    
    for projet in projets:
        urgence = calculer_urgence_projet(projet)
        if urgence == "Urgente":
            jours = calculer_jours_restants(projet)
            urgents.append({
                **projet,
                "urgence": urgence,
                "jours_restants": jours
            })
    
    # Trier par jours restants
    return sorted(urgents, key=lambda x: x.get("jours_restants") or 999)


def get_projets_en_cours(projets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retourne les projets en cours."""
    return filtrer_par_statut(projets, "En cours")


def get_projets_a_faire(projets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Retourne les projets à faire."""
    return filtrer_par_statut(projets, "À faire")


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════

def calculer_statistiques_projets(projets: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques des projets.
    
    Args:
        projets: Liste des projets
        
    Returns:
        Dictionnaire de statistiques
    """
    total = len(projets)
    
    # Par statut
    par_statut = {}
    for projet in projets:
        statut = projet.get("statut", "Inconnu")
        par_statut[statut] = par_statut.get(statut, 0) + 1
    
    # Par priorité
    par_priorite = {}
    for projet in projets:
        priorite = projet.get("priorite", "Moyenne")
        par_priorite[priorite] = par_priorite.get(priorite, 0) + 1
    
    # Urgents
    urgents = len(get_projets_urgents(projets))
    
    # Taux de complétion
    termines = par_statut.get("Terminé", 0)
    taux_completion = (termines / total * 100) if total > 0 else 0.0
    
    return {
        "total": total,
        "par_statut": par_statut,
        "par_priorite": par_priorite,
        "urgents": urgents,
        "taux_completion": taux_completion
    }


def calculer_budget_total(projets: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calcule les budgets total, dépensé et restant.
    
    Args:
        projets: Liste des projets
        
    Returns:
        Dictionnaire avec budgets
    """
    budget_total = 0.0
    budget_depense = 0.0
    
    for projet in projets:
        budget_total += projet.get("budget", 0.0)
        budget_depense += projet.get("cout_reel", 0.0)
    
    return {
        "budget_total": budget_total,
        "budget_depense": budget_depense,
        "budget_restant": budget_total - budget_depense
    }


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

def valider_projet(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide les données d'un projet.
    
    Args:
        data: Données du projet
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "statut" in data and data["statut"] not in STATUTS_PROJET:
        erreurs.append(f"Statut invalide. Valeurs autorisées: {', '.join(STATUTS_PROJET)}")
    
    if "priorite" in data and data["priorite"] not in PRIORITES:
        erreurs.append(f"Priorité invalide. Valeurs autorisées: {', '.join(PRIORITES)}")
    
    if "budget" in data:
        budget = data["budget"]
        if not isinstance(budget, (int, float)) or budget < 0:
            erreurs.append("Le budget doit être >= 0")
    
    return len(erreurs) == 0, erreurs


def calculer_progression(projet: Dict[str, Any]) -> float:
    """
    Calcule le pourcentage de progression d'un projet.
    
    Args:
        projet: Données du projet
        
    Returns:
        Pourcentage (0-100)
    """
    statut = projet.get("statut", "À faire")
    
    if statut == "Terminé":
        return 100.0
    elif statut == "En cours":
        # Si des tâches sont définies, calculer basé sur elles
        if "taches" in projet:
            taches = projet["taches"]
            if taches:
                completees = sum(1 for t in taches if t.get("completee", False))
                return (completees / len(taches)) * 100
        return 50.0  # Estimation par défaut
    else:
        return 0.0
