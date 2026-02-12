"""
Logique mÃetier pour le dashboard central (shared/ui/accueil.py)
"""

from datetime import date, datetime, timedelta
from typing import Any


def calculer_metriques_dashboard() -> dict[str, Any]:
    """
    Calcule les mÃetriques globales du dashboard central
    
    Returns:
        Dictionnaire avec les mÃetriques principales
    """
    return {
        "recettes_total": 0,
        "inventaire_alertes": 0,
        "courses_a_acheter": 0,
        "planning_semaine": 0,
        "timestamp": datetime.now().isoformat(),
    }


def compter_alertes_critiques(alertes: list[dict]) -> int:
    """
    Compte le nombre d'alertes critiques
    
    Args:
        alertes: Liste des alertes
        
    Returns:
        Nombre d'alertes critiques
    """
    if not alertes:
        return 0
    return len([a for a in alertes if a.get("type") == "warning"])


def generer_notifications(
    inventaire_critiques: list[dict] = None,
    peremption_proche: list[dict] = None,
    planning_vide: bool = False
) -> list[dict]:
    """
    GÃenère les notifications du dashboard
    
    Args:
        inventaire_critiques: Articles en stock critique
        peremption_proche: Articles pÃerissables proches pÃeremption
        planning_vide: Si le planning est vide
        
    Returns:
        Liste des notifications
    """
    notifications = []
    
    if inventaire_critiques:
        notifications.append({
            "type": "warning",
            "message": f"{len(inventaire_critiques)} article(s) en stock critique",
            "priorite": "haute"
        })
    
    if peremption_proche:
        notifications.append({
            "type": "warning",
            "message": f"{len(peremption_proche)} article(s) pÃeriment bientôt",
            "priorite": "haute"
        })
    
    if planning_vide:
        notifications.append({
            "type": "info",
            "message": "Aucun planning pour cette semaine",
            "priorite": "basse"
        })
    
    return notifications


def trier_notifications_par_priorite(notifications: list[dict]) -> list[dict]:
    """
    Trie les notifications par prioritÃe (haute â†’ basse)
    
    Args:
        notifications: Liste des notifications
        
    Returns:
        Liste triÃee
    """
    priorites = {"haute": 0, "moyenne": 1, "basse": 2}
    return sorted(
        notifications,
        key=lambda n: priorites.get(n.get("priorite"), 2)
    )


def est_cette_semaine(date_check: date) -> bool:
    """
    VÃerifie si une date est dans cette semaine
    
    Args:
        date_check: Date Ã  vÃerifier
        
    Returns:
        True si c'est cette semaine
    """
    if isinstance(date_check, str):
        date_check = datetime.fromisoformat(date_check).date()
    elif isinstance(date_check, datetime):
        date_check = date_check.date()
    
    aujourd_hui = date.today()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    
    return debut_semaine <= date_check <= fin_semaine


def est_aujourdhui(date_check: date) -> bool:
    """
    VÃerifie si une date est aujourd'hui
    
    Args:
        date_check: Date Ã  vÃerifier
        
    Returns:
        True si c'est aujourd'hui
    """
    if isinstance(date_check, str):
        date_check = datetime.fromisoformat(date_check).date()
    elif isinstance(date_check, datetime):
        date_check = date_check.date()
    
    return date_check == date.today()


def est_en_retard(date_check: date) -> bool:
    """
    VÃerifie si une date est dans le passÃe
    
    Args:
        date_check: Date Ã  vÃerifier
        
    Returns:
        True si la date est passÃee
    """
    if isinstance(date_check, str):
        date_check = datetime.fromisoformat(date_check).date()
    elif isinstance(date_check, datetime):
        date_check = date_check.date()
    
    return date_check < date.today()
