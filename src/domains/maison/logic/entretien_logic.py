"""
Logique métier du module Entretien (maison) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

FREQUENCES = ["Quotidienne", "Hebdomadaire", "Mensuelle", "Trimestrielle", "Annuelle"]
CATEGORIES_TACHE = ["Ménage", "Maintenance", "Contrôle", "Autre"]
PIECES = ["Cuisine", "Salon", "Chambre", "Salle de bain", "Bureau", "Extérieur", "Garage", "Autre"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCUL DES DATES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_prochaine_occurrence(derniere_execution: date, frequence: str) -> date:
    """
    Calcule la prochaine date d'exécution d'une tâche.
    
    Args:
        derniere_execution: Date de la dernière exécution
        frequence: Fréquence de la tâche
        
    Returns:
        Date de la prochaine occurrence
    """
    if frequence == "Quotidienne":
        return derniere_execution + timedelta(days=1)
    elif frequence == "Hebdomadaire":
        return derniere_execution + timedelta(days=7)
    elif frequence == "Mensuelle":
        # Approximation: 30 jours
        return derniere_execution + timedelta(days=30)
    elif frequence == "Trimestrielle":
        return derniere_execution + timedelta(days=90)
    elif frequence == "Annuelle":
        return derniere_execution + timedelta(days=365)
    else:
        return derniere_execution + timedelta(days=7)


def calculer_jours_avant_tache(tache: Dict[str, Any]) -> Optional[int]:
    """
    Calcule combien de jours avant la prochaine occurrence.
    
    Args:
        tache: Données de la tâche
        
    Returns:
        Nombre de jours (négatif si retard)
    """
    derniere = tache.get("derniere_execution")
    frequence = tache.get("frequence", "Hebdomadaire")
    
    if not derniere:
        return 0  # À faire immédiatement
    
    if isinstance(derniere, str):
        from datetime import datetime
        derniere = datetime.fromisoformat(derniere).date()
    
    prochaine = calculer_prochaine_occurrence(derniere, frequence)
    delta = (prochaine - date.today()).days
    
    return delta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ALERTES ET PRIORITÉS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_taches_aujourd_hui(taches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retourne les tâches à faire aujourd'hui.
    
    Args:
        taches: Liste des tâches
        
    Returns:
        Liste des tâches du jour
    """
    resultat = []
    
    for tache in taches:
        jours = calculer_jours_avant_tache(tache)
        if jours is not None and jours <= 0:
            resultat.append({
                **tache,
                "jours_retard": abs(jours) if jours < 0 else 0
            })
    
    return sorted(resultat, key=lambda x: x["jours_retard"], reverse=True)


def get_taches_semaine(taches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retourne les tâches de la semaine.
    
    Args:
        taches: Liste des tâches
        
    Returns:
        Liste des tâches de la semaine
    """
    resultat = []
    
    for tache in taches:
        jours = calculer_jours_avant_tache(tache)
        if jours is not None and 0 <= jours <= 7:
            resultat.append({
                **tache,
                "jours_restants": jours
            })
    
    return sorted(resultat, key=lambda x: x["jours_restants"])


def get_taches_en_retard(taches: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Retourne les tâches en retard.
    
    Args:
        taches: Liste des tâches
        
    Returns:
        Liste des tâches en retard
    """
    resultat = []
    
    for tache in taches:
        jours = calculer_jours_avant_tache(tache)
        if jours is not None and jours < 0:
            resultat.append({
                **tache,
                "jours_retard": abs(jours)
            })
    
    return sorted(resultat, key=lambda x: x["jours_retard"], reverse=True)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FILTRAGE ET TRI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def filtrer_par_categorie(taches: List[Dict[str, Any]], categorie: str) -> List[Dict[str, Any]]:
    """Filtre les tâches par catégorie."""
    return [t for t in taches if t.get("categorie") == categorie]


def filtrer_par_piece(taches: List[Dict[str, Any]], piece: str) -> List[Dict[str, Any]]:
    """Filtre les tâches par pièce."""
    return [t for t in taches if t.get("piece") == piece]


def filtrer_par_frequence(taches: List[Dict[str, Any]], frequence: str) -> List[Dict[str, Any]]:
    """Filtre les tâches par fréquence."""
    return [t for t in taches if t.get("frequence") == frequence]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_entretien(taches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques d'entretien.
    
    Args:
        taches: Liste des tâches
        
    Returns:
        Dictionnaire de statistiques
    """
    total = len(taches)
    
    # Par catégorie
    par_categorie = {}
    for tache in taches:
        cat = tache.get("categorie", "Autre")
        par_categorie[cat] = par_categorie.get(cat, 0) + 1
    
    # Par fréquence
    par_frequence = {}
    for tache in taches:
        freq = tache.get("frequence", "Hebdomadaire")
        par_frequence[freq] = par_frequence.get(freq, 0) + 1
    
    # Alertes
    aujourd_hui = len(get_taches_aujourd_hui(taches))
    en_retard = len(get_taches_en_retard(taches))
    semaine = len(get_taches_semaine(taches))
    
    return {
        "total_taches": total,
        "par_categorie": par_categorie,
        "par_frequence": par_frequence,
        "aujourd_hui": aujourd_hui,
        "en_retard": en_retard,
        "cette_semaine": semaine
    }


def calculer_taux_completion(taches: List[Dict[str, Any]], periode_jours: int = 30) -> float:
    """
    Calcule le taux de complétion des tâches.
    
    Args:
        taches: Liste des tâches
        periode_jours: Période de calcul en jours
        
    Returns:
        Taux de complétion (0-100)
    """
    if not taches:
        return 0.0
    
    date_debut = date.today() - timedelta(days=periode_jours)
    
    # Compter tâches attendues vs complétées
    attendues = 0
    completees = 0
    
    for tache in taches:
        frequence = tache.get("frequence", "Hebdomadaire")
        
        # Calculer nombre d'occurrences attendues
        if frequence == "Quotidienne":
            occurrences = periode_jours
        elif frequence == "Hebdomadaire":
            occurrences = periode_jours // 7
        elif frequence == "Mensuelle":
            occurrences = periode_jours // 30
        else:
            occurrences = 1
        
        attendues += occurrences
        
        # Compter complétées (simplification)
        derniere = tache.get("derniere_execution")
        if derniere:
            if isinstance(derniere, str):
                from datetime import datetime
                derniere = datetime.fromisoformat(derniere).date()
            
            if derniere >= date_debut:
                completees += 1
    
    return (completees / attendues * 100) if attendues > 0 else 0.0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_tache(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide les données d'une tâche.
    
    Args:
        data: Données de la tâche
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "frequence" in data and data["frequence"] not in FREQUENCES:
        erreurs.append(f"Fréquence invalide. Valeurs autorisées: {', '.join(FREQUENCES)}")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_TACHE:
        erreurs.append(f"Catégorie invalide. Valeurs autorisées: {', '.join(CATEGORIES_TACHE)}")
    
    return len(erreurs) == 0, erreurs


def grouper_par_piece(taches: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groupe les tâches par pièce.
    
    Args:
        taches: Liste des tâches
        
    Returns:
        Dictionnaire {piece: [taches]}
    """
    groupes = {}
    
    for tache in taches:
        piece = tache.get("piece", "Autre")
        if piece not in groupes:
            groupes[piece] = []
        groupes[piece].append(tache)
    
    return groupes

