"""
Logique mÃ©tier du module Jardin (maison) - SÃ©parÃ©e de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

CATEGORIES_PLANTES = ["LÃ©gumes", "Fruits", "Herbes", "Fleurs", "Arbres"]
SAISONS = ["Printemps", "Ã‰tÃ©", "Automne", "Hiver"]
STATUS_PLANTES = ["Semis", "Pousse", "Mature", "RÃ©colte", "Dormant"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCUL DES DATES ET SAISONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_saison_actuelle() -> str:
    """
    Retourne la saison actuelle.
    
    Returns:
        Nom de la saison
    """
    today = date.today()
    mois = today.month
    
    if mois in [3, 4, 5]:
        return "Printemps"
    elif mois in [6, 7, 8]:
        return "Ã‰tÃ©"
    elif mois in [9, 10, 11]:
        return "Automne"
    else:
        return "Hiver"


def calculer_jours_avant_arrosage(plante: Dict[str, Any]) -> Optional[int]:
    """
    Calcule combien de jours avant le prochain arrosage.
    
    Args:
        plante: DonnÃ©es de la plante
        
    Returns:
        Nombre de jours (nÃ©gatif si retard)
    """
    if "dernier_arrosage" not in plante or not plante["dernier_arrosage"]:
        return 0
    
    frequence = plante.get("frequence_arrosage", 7)
    dernier = plante["dernier_arrosage"]
    
    if isinstance(dernier, str):
        from datetime import datetime
        dernier = datetime.fromisoformat(dernier).date()
    
    prochain = dernier + timedelta(days=frequence)
    delta = (prochain - date.today()).days
    
    return delta


def calculer_jours_avant_recolte(plante: Dict[str, Any]) -> Optional[int]:
    """
    Calcule combien de jours avant la rÃ©colte.
    
    Args:
        plante: DonnÃ©es de la plante
        
    Returns:
        Nombre de jours
    """
    if "date_recolte_estimee" not in plante or not plante["date_recolte_estimee"]:
        return None
    
    date_recolte = plante["date_recolte_estimee"]
    
    if isinstance(date_recolte, str):
        from datetime import datetime
        date_recolte = datetime.fromisoformat(date_recolte).date()
    
    delta = (date_recolte - date.today()).days
    return delta


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ALERTES ET PRIORITÃ‰S
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_plantes_a_arroser(plantes: List[Dict[str, Any]], jours_avance: int = 1) -> List[Dict[str, Any]]:
    """
    Retourne les plantes qui ont besoin d'arrosage.
    
    Args:
        plantes: Liste des plantes
        jours_avance: Nombre de jours d'anticipation
        
    Returns:
        Liste des plantes Ã  arroser
    """
    resultat = []
    
    for plante in plantes:
        jours = calculer_jours_avant_arrosage(plante)
        if jours is not None and jours <= jours_avance:
            resultat.append({
                **plante,
                "jours_restants": jours,
                "priorite": "urgent" if jours < 0 else "bientot"
            })
    
    return sorted(resultat, key=lambda x: x["jours_restants"])


def get_recoltes_proches(plantes: List[Dict[str, Any]], jours_avance: int = 7) -> List[Dict[str, Any]]:
    """
    Retourne les plantes prÃªtes pour rÃ©colte.
    
    Args:
        plantes: Liste des plantes
        jours_avance: Nombre de jours d'anticipation
        
    Returns:
        Liste des plantes Ã  rÃ©colter
    """
    resultat = []
    
    for plante in plantes:
        jours = calculer_jours_avant_recolte(plante)
        if jours is not None and 0 <= jours <= jours_avance:
            resultat.append({
                **plante,
                "jours_restants": jours
            })
    
    return sorted(resultat, key=lambda x: x["jours_restants"])


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_jardin(plantes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques du jardin.
    
    Args:
        plantes: Liste des plantes
        
    Returns:
        Dictionnaire de statistiques
    """
    total = len(plantes)
    
    # Par catÃ©gorie
    par_categorie = {}
    for plante in plantes:
        cat = plante.get("categorie", "Autre")
        par_categorie[cat] = par_categorie.get(cat, 0) + 1
    
    # Par status
    par_status = {}
    for plante in plantes:
        status = plante.get("status", "Inconnu")
        par_status[status] = par_status.get(status, 0) + 1
    
    # Alertes
    a_arroser = len(get_plantes_a_arroser(plantes))
    a_recolter = len(get_recoltes_proches(plantes))
    
    return {
        "total_plantes": total,
        "par_categorie": par_categorie,
        "par_status": par_status,
        "alertes_arrosage": a_arroser,
        "alertes_recolte": a_recolter
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FILTRAGE ET TRI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def filtrer_par_categorie(plantes: List[Dict[str, Any]], categorie: str) -> List[Dict[str, Any]]:
    """Filtre les plantes par catÃ©gorie."""
    return [p for p in plantes if p.get("categorie") == categorie]


def filtrer_par_status(plantes: List[Dict[str, Any]], status: str) -> List[Dict[str, Any]]:
    """Filtre les plantes par status."""
    return [p for p in plantes if p.get("status") == status]


def filtrer_par_saison(plantes: List[Dict[str, Any]], saison: str) -> List[Dict[str, Any]]:
    """Filtre les plantes par saison de plantation."""
    return [p for p in plantes if saison in p.get("saisons_plantation", [])]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_plante(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide les donnÃ©es d'une plante.
    
    Args:
        data: DonnÃ©es de la plante
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "nom" not in data or not data["nom"]:
        erreurs.append("Le nom est requis")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_PLANTES:
        erreurs.append(f"CatÃ©gorie invalide. Valeurs autorisÃ©es: {', '.join(CATEGORIES_PLANTES)}")
    
    if "frequence_arrosage" in data:
        freq = data["frequence_arrosage"]
        if not isinstance(freq, int) or freq < 1:
            erreurs.append("La frÃ©quence d'arrosage doit Ãªtre >= 1 jour")
    
    return len(erreurs) == 0, erreurs

