"""
Logique métier du module Vue d'ensemble (planning) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

PERIODES = ["Jour", "Semaine", "Mois", "Année"]
CATEGORIES_TACHES = ["Travail", "Maison", "Famille", "Personnel", "Courses", "Santé"]


# ═══════════════════════════════════════════════════════════
# ANALYSE GLOBALE
# ═══════════════════════════════════════════════════════════

def analyser_charge_globale(evenements: List[Dict[str, Any]], taches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyse la charge globale de travail."""
    total_evenements = len(evenements)
    total_taches = len(taches)
    taches_completees = len([t for t in taches if t.get("complete", False)])
    taches_en_retard = len([t for t in taches if est_en_retard(t)])
    
    # Charge par catégorie
    charge_par_categorie = {}
    for tache in taches:
        cat = tache.get("categorie", "Personnel")
        charge_par_categorie[cat] = charge_par_categorie.get(cat, 0) + 1
    
    # Niveau de charge
    charge_totale = total_evenements + (total_taches - taches_completees)
    
    if charge_totale == 0:
        niveau = "Libre"
    elif charge_totale <= 5:
        niveau = "Léger"
    elif charge_totale <= 15:
        niveau = "Moyen"
    elif charge_totale <= 25:
        niveau = "Élevé"
    else:
        niveau = "Très élevé"
    
    return {
        "total_evenements": total_evenements,
        "total_taches": total_taches,
        "taches_completees": taches_completees,
        "taches_en_retard": taches_en_retard,
        "taux_completion": (taches_completees / total_taches * 100) if total_taches > 0 else 0,
        "charge_par_categorie": charge_par_categorie,
        "niveau_charge": niveau
    }


def est_en_retard(tache: Dict[str, Any]) -> bool:
    """Vérifie si une tâche est en retard."""
    if tache.get("complete", False):
        return False
    
    date_limite = tache.get("date_limite")
    if not date_limite:
        return False
    
    if isinstance(date_limite, str):
        date_limite = datetime.fromisoformat(date_limite).date()
    
    return date_limite < date.today()


# ═══════════════════════════════════════════════════════════
# TENDANCES ET PRÉVISIONS
# ═══════════════════════════════════════════════════════════

def analyser_tendances(historique: List[Dict[str, Any]], jours: int = 30) -> Dict[str, Any]:
    """Analyse les tendances sur une période."""
    date_limite = date.today() - timedelta(days=jours)
    
    # Filtrer historique
    historique_periode = []
    for item in historique:
        date_item = item.get("date")
        if isinstance(date_item, str):
            date_item = datetime.fromisoformat(date_item).date()
        
        if date_item and date_item >= date_limite:
            historique_periode.append(item)
    
    if not historique_periode:
        return {
            "evolution": "stable",
            "moyenne_jour": 0.0,
            "pic_activite": None
        }
    
    # Grouper par jour
    par_jour = {}
    for item in historique_periode:
        date_item = item.get("date")
        if isinstance(date_item, str):
            date_item = datetime.fromisoformat(date_item).date()
        
        jour_key = date_item.strftime("%Y-%m-%d")
        par_jour[jour_key] = par_jour.get(jour_key, 0) + 1
    
    # Moyenne par jour
    moyenne_jour = len(historique_periode) / jours
    
    # Pic d'activité
    if par_jour:
        pic_jour = max(par_jour.items(), key=lambda x: x[1])
        pic_date = datetime.strptime(pic_jour[0], "%Y-%m-%d").date()
        pic_activite = {"date": pic_date, "nombre": pic_jour[1]}
    else:
        pic_activite = None
    
    # Tendance (comparer première et seconde moitié)
    mid = jours // 2
    date_mid = date.today() - timedelta(days=mid)
    
    premiere_moitie = [h for h in historique_periode 
                       if datetime.fromisoformat(str(h.get("date"))).date() < date_mid]
    seconde_moitie = [h for h in historique_periode 
                      if datetime.fromisoformat(str(h.get("date"))).date() >= date_mid]
    
    avg1 = len(premiere_moitie) / mid if mid > 0 else 0
    avg2 = len(seconde_moitie) / mid if mid > 0 else 0
    
    if avg2 > avg1 * 1.2:
        evolution = "hausse"
    elif avg2 < avg1 * 0.8:
        evolution = "baisse"
    else:
        evolution = "stable"
    
    return {
        "evolution": evolution,
        "moyenne_jour": moyenne_jour,
        "pic_activite": pic_activite
    }


def prevoir_charge_prochaine_semaine(evenements: List[Dict[str, Any]], taches: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Prévoit la charge de la semaine prochaine."""
    debut_semaine = date.today() + timedelta(days=7 - date.today().weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    
    # Événements prévus
    evt_semaine = []
    for evt in evenements:
        date_evt = evt.get("date")
        if isinstance(date_evt, str):
            date_evt = datetime.fromisoformat(date_evt).date()
        
        if debut_semaine <= date_evt <= fin_semaine:
            evt_semaine.append(evt)
    
    # Tâches à échéance
    taches_semaine = []
    for tache in taches:
        if tache.get("complete"):
            continue
        
        date_limite = tache.get("date_limite")
        if not date_limite:
            continue
        
        if isinstance(date_limite, str):
            date_limite = datetime.fromisoformat(date_limite).date()
        
        if debut_semaine <= date_limite <= fin_semaine:
            taches_semaine.append(tache)
    
    charge_totale = len(evt_semaine) + len(taches_semaine)
    
    if charge_totale <= 5:
        prevision = "Semaine légère"
    elif charge_totale <= 15:
        prevision = "Semaine normale"
    elif charge_totale <= 25:
        prevision = "Semaine chargée"
    else:
        prevision = "Semaine très chargée"
    
    return {
        "evenements": len(evt_semaine),
        "taches": len(taches_semaine),
        "charge_totale": charge_totale,
        "prevision": prevision
    }


# ═══════════════════════════════════════════════════════════
# PRIORITÉS ET ALERTES
# ═══════════════════════════════════════════════════════════

def identifier_taches_urgentes(taches: List[Dict[str, Any]], jours_seuil: int = 3) -> List[Dict[str, Any]]:
    """Identifie les tâches urgentes."""
    date_seuil = date.today() + timedelta(days=jours_seuil)
    
    urgentes = []
    for tache in taches:
        if tache.get("complete"):
            continue
        
        date_limite = tache.get("date_limite")
        if not date_limite:
            continue
        
        if isinstance(date_limite, str):
            date_limite = datetime.fromisoformat(date_limite).date()
        
        if date_limite <= date_seuil:
            urgentes.append(tache)
    
    return urgentes


def generer_alertes(evenements: List[Dict[str, Any]], taches: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """Génère les alertes pour la vue d'ensemble."""
    alertes = []
    
    # Tâches en retard
    en_retard = [t for t in taches if est_en_retard(t)]
    if en_retard:
        alertes.append({
            "type": "danger",
            "message": f"âš ï¸ {len(en_retard)} tâche(s) en retard"
        })
    
    # Tâches urgentes
    urgentes = identifier_taches_urgentes(taches, 3)
    if urgentes:
        alertes.append({
            "type": "warning",
            "message": f"⏰ {len(urgentes)} tâche(s) urgente(s) (< 3 jours)"
        })
    
    # Événements aujourd'hui
    evt_aujourdhui = []
    for evt in evenements:
        date_evt = evt.get("date")
        if isinstance(date_evt, str):
            date_evt = datetime.fromisoformat(date_evt).date()
        
        if date_evt == date.today():
            evt_aujourdhui.append(evt)
    
    if evt_aujourdhui:
        alertes.append({
            "type": "info",
            "message": f"🎯 {len(evt_aujourdhui)} événement(s) aujourd'hui"
        })
    
    return alertes


# ═══════════════════════════════════════════════════════════
# STATISTIQUES PÉRIODIQUES
# ═══════════════════════════════════════════════════════════

def calculer_statistiques_periode(items: List[Dict[str, Any]], periode: str = "Semaine") -> Dict[str, Any]:
    """Calcule les statistiques pour une période donnée."""
    if periode == "Jour":
        jours = 1
    elif periode == "Semaine":
        jours = 7
    elif periode == "Mois":
        jours = 30
    else:  # Année
        jours = 365
    
    date_debut = date.today() - timedelta(days=jours)
    date_fin = date.today()
    
    items_periode = []
    for item in items:
        date_item = item.get("date")
        if isinstance(date_item, str):
            date_item = datetime.fromisoformat(date_item).date()
        
        if date_item and date_debut <= date_item <= date_fin:
            items_periode.append(item)
    
    return {
        "periode": periode,
        "total": len(items_periode),
        "moyenne_jour": len(items_periode) / jours if jours > 0 else 0
    }


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════

def formater_niveau_charge(niveau: str) -> str:
    """Formate le niveau de charge avec emoji."""
    emojis = {
        "Libre": "😌",
        "Léger": "🙂",
        "Moyen": "😐",
        "Élevé": "😐°",
        "Très élevé": "📥"
    }
    emoji = emojis.get(niveau, "")
    return f"{emoji} {niveau}"


def formater_evolution(evolution: str) -> str:
    """Formate l'évolution avec emoji."""
    emojis = {
        "hausse": "�",
        "baisse": "📉",
        "stable": "➡️"
    }
    emoji = emojis.get(evolution, "")
    return f"{emoji} {evolution.capitalize()}"
