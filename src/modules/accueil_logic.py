"""
Logique métier du module Accueil (dashboard) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CALCULS DE MÉTRIQUES
# ═══════════════════════════════════════════════════════════

def calculer_metriques_dashboard(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Calcule les métriques pour le dashboard d'accueil."""
    recettes = data.get("recettes", [])
    courses = data.get("courses", [])
    activites = data.get("activites", [])
    inventaire = data.get("inventaire", [])
    
    return {
        "total_recettes": len(recettes),
        "courses_actives": len([c for c in courses if not c.get("achete", False)]),
        "activites_semaine": len([a for a in activites if est_cette_semaine(a.get("date"))]),
        "alertes_critiques": compter_alertes_critiques(data)
    }


def compter_alertes_critiques(data: Dict[str, Any]) -> int:
    """Compte le nombre d'alertes critiques."""
    count = 0
    
    # Inventaire expiré
    inventaire = data.get("inventaire", [])
    count += len([i for i in inventaire if i.get("expire", False)])
    
    # Stock bas critique
    count += len([i for i in inventaire if i.get("quantite", 0) == 0])
    
    # Activités en retard
    activites = data.get("activites", [])
    count += len([a for a in activites if est_en_retard(a.get("date"))])
    
    return count


def calculer_statistiques_periode(items: List[Dict[str, Any]], periode: str = "semaine") -> Dict[str, Any]:
    """Calcule les statistiques pour une période."""
    if periode == "jour":
        jours = 1
    elif periode == "semaine":
        jours = 7
    elif periode == "mois":
        jours = 30
    else:
        jours = 365
    
    date_debut = date.today() - timedelta(days=jours)
    
    items_periode = []
    for item in items:
        date_item = item.get("date")
        if isinstance(date_item, str):
            from datetime import datetime
            date_item = datetime.fromisoformat(date_item).date()
        
        if date_item and date_debut <= date_item <= date.today():
            items_periode.append(item)
    
    return {
        "total": len(items_periode),
        "moyenne_jour": len(items_periode) / jours if jours > 0 else 0
    }


# ═══════════════════════════════════════════════════════════
# GESTION DES DATES
# ═══════════════════════════════════════════════════════════

def est_cette_semaine(date_obj: Any) -> bool:
    """Vérifie si une date est dans la semaine actuelle."""
    if isinstance(date_obj, str):
        from datetime import datetime
        date_obj = datetime.fromisoformat(date_obj).date()
    
    if not date_obj:
        return False
    
    today = date.today()
    debut_semaine = today - timedelta(days=today.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    
    return debut_semaine <= date_obj <= fin_semaine


def est_aujourdhui(date_obj: Any) -> bool:
    """Vérifie si une date est aujourd'hui."""
    if isinstance(date_obj, str):
        from datetime import datetime
        date_obj = datetime.fromisoformat(date_obj).date()
    
    return date_obj == date.today()


def est_en_retard(date_obj: Any) -> bool:
    """Vérifie si une date est passée."""
    if isinstance(date_obj, str):
        from datetime import datetime
        date_obj = datetime.fromisoformat(date_obj).date()
    
    return date_obj and date_obj < date.today()


def est_ce_mois(date_obj: Any) -> bool:
    """Vérifie si une date est dans le mois actuel."""
    if isinstance(date_obj, str):
        from datetime import datetime
        date_obj = datetime.fromisoformat(date_obj).date()
    
    if not date_obj:
        return False
    
    today = date.today()
    return date_obj.year == today.year and date_obj.month == today.month


# ═══════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════

def generer_notifications(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Génère les notifications pour l'accueil."""
    notifications = []
    
    # Alertes inventaire
    inventaire = data.get("inventaire", [])
    expires = [i for i in inventaire if i.get("expire")]
    if expires:
        notifications.append({
            "type": "warning",
            "message": f"⚠️ {len(expires)} article(s) expiré(s) dans l'inventaire",
            "priorite": "haute"
        })
    
    # Stock bas
    stock_bas = [i for i in inventaire if i.get("quantite", 0) < i.get("seuil_min", 1)]
    if stock_bas:
        notifications.append({
            "type": "warning",
            "message": f"📦 {len(stock_bas)} article(s) en stock bas",
            "priorite": "moyenne"
        })
    
    # Courses non achetes
    courses = data.get("courses", [])
    non_achetes = [c for c in courses if not c.get("achete")]
    if non_achetes:
        notifications.append({
            "type": "info",
            "message": f"🛒 {len(non_achetes)} article(s) à acheter",
            "priorite": "basse"
        })
    
    # Activités aujourd'hui
    activites = data.get("activites", [])
    aujourdhui = [a for a in activites if est_aujourdhui(a.get("date"))]
    if aujourdhui:
        notifications.append({
            "type": "success",
            "message": f"📅 {len(aujourdhui)} activité(s) prévue(s) aujourd'hui",
            "priorite": "moyenne"
        })
    
    # Activités en retard
    en_retard = [a for a in activites if est_en_retard(a.get("date"))]
    if en_retard:
        notifications.append({
            "type": "danger",
            "message": f"⏰ {len(en_retard)} activité(s) en retard",
            "priorite": "haute"
        })
    
    return notifications


def trier_notifications_par_priorite(notifications: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Trie les notifications par priorité."""
    ordre_priorite = {"haute": 0, "moyenne": 1, "basse": 2}
    return sorted(notifications, key=lambda x: ordre_priorite.get(x.get("priorite", "basse"), 2))


# ═══════════════════════════════════════════════════════════
# RACCOURCIS ET ACTIONS RAPIDES
# ═══════════════════════════════════════════════════════════

def suggerer_actions_rapides(data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Suggère des actions rapides basées sur le contexte."""
    actions = []
    
    # Si courses non vides
    courses = data.get("courses", [])
    if [c for c in courses if not c.get("achete")]:
        actions.append({
            "titre": "Finaliser les courses",
            "icone": "🛒",
            "module": "courses"
        })
    
    # Si activités aujourd'hui
    activites = data.get("activites", [])
    if [a for a in activites if est_aujourdhui(a.get("date"))]:
        actions.append({
            "titre": "Voir les activités du jour",
            "icone": "📅",
            "module": "planning"
        })
    
    # Si stock bas
    inventaire = data.get("inventaire", [])
    if [i for i in inventaire if i.get("quantite", 0) == 0]:
        actions.append({
            "titre": "Réapprovisionner le stock",
            "icone": "📦",
            "module": "inventaire"
        })
    
    # Si aucune recette récente
    recettes = data.get("recettes", [])
    recettes_recentes = [r for r in recettes if est_cette_semaine(r.get("date_creation"))]
    if len(recettes_recentes) == 0:
        actions.append({
            "titre": "Ajouter une nouvelle recette",
            "icone": "🍳",
            "module": "recettes"
        })
    
    return actions


# ═══════════════════════════════════════════════════════════
# RÉSUMÉ ET APERÇU
# ═══════════════════════════════════════════════════════════

def generer_resume_quotidien(data: Dict[str, Any]) -> Dict[str, Any]:
    """Génère un résumé quotidien."""
    activites_jour = [a for a in data.get("activites", []) if est_aujourdhui(a.get("date"))]
    courses_restantes = [c for c in data.get("courses", []) if not c.get("achete")]
    alertes = compter_alertes_critiques(data)
    
    return {
        "date": date.today(),
        "activites_prevues": len(activites_jour),
        "courses_a_faire": len(courses_restantes),
        "alertes": alertes,
        "statut": "OK" if alertes == 0 else "Attention"
    }


def calculer_progression_hebdomadaire(data_semaine: List[Dict[str, Any]]) -> Dict[str, float]:
    """Calcule la progression par rapport à la semaine."""
    if not data_semaine:
        return {"progression": 0.0, "tendance": "stable"}
    
    # Comparer première et dernière moitié
    mid = len(data_semaine) // 2
    if mid == 0:
        return {"progression": 0.0, "tendance": "stable"}
    
    premiere_moitie = len(data_semaine[:mid])
    seconde_moitie = len(data_semaine[mid:])
    
    if premiere_moitie == 0:
        progression = 0.0
        tendance = "stable"
    else:
        progression = ((seconde_moitie - premiere_moitie) / premiere_moitie) * 100
        
        if progression > 10:
            tendance = "hausse"
        elif progression < -10:
            tendance = "baisse"
        else:
            tendance = "stable"
    
    return {
        "progression": progression,
        "tendance": tendance
    }


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════

def formater_metrique(valeur: float, unite: str = "") -> str:
    """Formate une métrique pour l'affichage."""
    if isinstance(valeur, float):
        if valeur >= 1000:
            return f"{valeur/1000:.1f}k{unite}"
        elif valeur >= 100:
            return f"{valeur:.0f}{unite}"
        else:
            return f"{valeur:.1f}{unite}"
    return f"{valeur}{unite}"


def formater_tendance(tendance: str) -> str:
    """Formate une tendance avec emoji."""
    emojis = {
        "hausse": "📈",
        "baisse": "📉",
        "stable": "➡️"
    }
    return f"{emojis.get(tendance, '')} {tendance.capitalize()}"
