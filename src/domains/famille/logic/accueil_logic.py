"""
Logique mÃ©tier du module Accueil - SÃ©parÃ©e de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import datetime, timedelta, date
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

JULIUS_BIRTHDAY = date(2023, 10, 26)  # Date de naissance de Julius

NOTIFICATION_TYPES = {
    "critique": {"emoji": "ðŸš¨", "color": "red"},
    "alerte": {"emoji": "âš ï¸", "color": "orange"},
    "info": {"emoji": "â„¹ï¸", "color": "blue"},
    "succes": {"emoji": "âœ…", "color": "green"},
}

DASHBOARD_SECTIONS = [
    "metriques",
    "alertes",
    "activites_recentes",
    "suggestions_ia",
    "planning_jour",
]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCULS JULIUS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_age_julius(date_reference: Optional[date] = None) -> dict:
    """
    Calcule l'Ã¢ge de Julius en mois et jours.
    
    Args:
        date_reference: Date de rÃ©fÃ©rence (par dÃ©faut aujourd'hui)
        
    Returns:
        Dictionnaire avec mois, jours, total_jours
    """
    date_ref = date_reference or date.today()
    
    delta = date_ref - JULIUS_BIRTHDAY
    total_jours = delta.days
    
    # Calcul des mois
    mois = 0
    date_temp = JULIUS_BIRTHDAY
    
    while True:
        # Ajouter un mois
        if date_temp.month == 12:
            next_month = date(date_temp.year + 1, 1, date_temp.day)
        else:
            try:
                next_month = date(date_temp.year, date_temp.month + 1, date_temp.day)
            except ValueError:
                # GÃ©rer les mois avec moins de jours
                if date_temp.month + 1 == 2:
                    next_month = date(date_temp.year, date_temp.month + 1, 28)
                else:
                    next_month = date(date_temp.year, date_temp.month + 1, 30)
        
        if next_month > date_ref:
            break
        
        date_temp = next_month
        mois += 1
    
    # Calcul des jours restants
    jours = (date_ref - date_temp).days
    
    return {
        "mois": mois,
        "jours": jours,
        "total_jours": total_jours,
        "date_naissance": JULIUS_BIRTHDAY.isoformat(),
    }


def calculer_semaines_julius(date_reference: Optional[date] = None) -> int:
    """
    Calcule l'Ã¢ge de Julius en semaines.
    
    Args:
        date_reference: Date de rÃ©fÃ©rence (par dÃ©faut aujourd'hui)
        
    Returns:
        Nombre de semaines
    """
    date_ref = date_reference or date.today()
    delta = date_ref - JULIUS_BIRTHDAY
    return delta.days // 7


def formater_age_julius(date_reference: Optional[date] = None) -> str:
    """
    Formate l'Ã¢ge de Julius de maniÃ¨re lisible.
    
    Args:
        date_reference: Date de rÃ©fÃ©rence
        
    Returns:
        ChaÃ®ne formatÃ©e (ex: "19 mois et 5 jours")
    """
    age = calculer_age_julius(date_reference)
    
    if age["jours"] == 0:
        return f"{age['mois']} mois"
    elif age["jours"] == 1:
        return f"{age['mois']} mois et 1 jour"
    else:
        return f"{age['mois']} mois et {age['jours']} jours"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# MÃ‰TRIQUES DASHBOARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_metriques_recettes(recettes: list[dict]) -> dict:
    """
    Calcule les mÃ©triques liÃ©es aux recettes.
    
    Args:
        recettes: Liste des recettes
        
    Returns:
        Dictionnaire des mÃ©triques
    """
    if not recettes:
        return {
            "total": 0,
            "favoris": 0,
            "cette_semaine": 0,
            "moyenne_temps": 0,
        }
    
    maintenant = datetime.now()
    debut_semaine = maintenant - timedelta(days=maintenant.weekday())
    
    favoris = len([r for r in recettes if r.get("favori")])
    
    cette_semaine = len([
        r for r in recettes
        if r.get("derniere_utilisation") and r["derniere_utilisation"] >= debut_semaine
    ])
    
    temps_total = sum(r.get("temps_preparation", 0) for r in recettes)
    moyenne_temps = temps_total / len(recettes) if recettes else 0
    
    return {
        "total": len(recettes),
        "favoris": favoris,
        "cette_semaine": cette_semaine,
        "moyenne_temps": round(moyenne_temps),
    }


def calculer_metriques_inventaire(articles: list[dict]) -> dict:
    """
    Calcule les mÃ©triques liÃ©es Ã  l'inventaire.
    
    Args:
        articles: Liste des articles de l'inventaire
        
    Returns:
        Dictionnaire des mÃ©triques
    """
    if not articles:
        return {
            "total": 0,
            "alertes": 0,
            "perimes": 0,
            "valeur_totale": 0,
        }
    
    aujourd_hui = date.today()
    
    alertes = 0
    perimes = 0
    valeur_totale = 0
    
    for article in articles:
        # Comptage alertes stock
        quantite = article.get("quantite", 0)
        seuil_alerte = article.get("seuil_alerte", 5)
        if quantite <= seuil_alerte:
            alertes += 1
        
        # Comptage pÃ©rimÃ©s
        date_peremption = article.get("date_peremption")
        if date_peremption:
            if isinstance(date_peremption, datetime):
                date_peremption = date_peremption.date()
            if date_peremption < aujourd_hui:
                perimes += 1
        
        # Valeur totale
        valeur_totale += quantite * article.get("prix_unitaire", 0)
    
    return {
        "total": len(articles),
        "alertes": alertes,
        "perimes": perimes,
        "valeur_totale": round(valeur_totale, 2),
    }


def calculer_metriques_courses(listes: list[dict]) -> dict:
    """
    Calcule les mÃ©triques liÃ©es aux courses.
    
    Args:
        listes: Liste des listes de courses (avec articles)
        
    Returns:
        Dictionnaire des mÃ©triques
    """
    if not listes:
        return {
            "listes_actives": 0,
            "articles_a_acheter": 0,
            "articles_achetes": 0,
            "taux_completion": 0,
        }
    
    listes_actives = len([l for l in listes if not l.get("archivee")])
    
    articles_a_acheter = 0
    articles_achetes = 0
    
    for liste in listes:
        if not liste.get("archivee"):
            for article in liste.get("articles", []):
                if article.get("achete"):
                    articles_achetes += 1
                else:
                    articles_a_acheter += 1
    
    total = articles_a_acheter + articles_achetes
    taux = (articles_achetes / total * 100) if total > 0 else 0
    
    return {
        "listes_actives": listes_actives,
        "articles_a_acheter": articles_a_acheter,
        "articles_achetes": articles_achetes,
        "taux_completion": round(taux, 1),
    }


def calculer_metriques_planning(evenements: list[dict]) -> dict:
    """
    Calcule les mÃ©triques liÃ©es au planning.
    
    Args:
        evenements: Liste des Ã©vÃ©nements planifiÃ©s
        
    Returns:
        Dictionnaire des mÃ©triques
    """
    if not evenements:
        return {
            "total_evenements": 0,
            "aujourd_hui": 0,
            "cette_semaine": 0,
            "prochains_7_jours": 0,
        }
    
    aujourd_hui = date.today()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    dans_7_jours = aujourd_hui + timedelta(days=7)
    
    count_aujourd_hui = 0
    count_semaine = 0
    count_7_jours = 0
    
    for evt in evenements:
        date_evt = evt.get("date")
        if not date_evt:
            continue
        
        if isinstance(date_evt, datetime):
            date_evt = date_evt.date()
        
        if date_evt == aujourd_hui:
            count_aujourd_hui += 1
        
        if debut_semaine <= date_evt <= fin_semaine:
            count_semaine += 1
        
        if aujourd_hui <= date_evt <= dans_7_jours:
            count_7_jours += 1
    
    return {
        "total_evenements": len(evenements),
        "aujourd_hui": count_aujourd_hui,
        "cette_semaine": count_semaine,
        "prochains_7_jours": count_7_jours,
    }


def calculer_metriques_sante(entrees: list[dict] = None) -> dict:
    """
    Calcule les mÃ©triques de santÃ©/bien-Ãªtre.
    
    Args:
        entrees: Liste des entrÃ©es de suivi santÃ©
        
    Returns:
        Dictionnaire des mÃ©triques santÃ©
    """
    entrees = entrees or []
    if not entrees:
        return {
            "derniere_entree": None,
            "humeur_moyenne": None,
            "energie_moyenne": None,
            "entrees_semaine": 0,
        }
    
    # Calculs basiques
    humeurs = [e.get("humeur", 5) for e in entrees if e.get("humeur")]
    energies = [e.get("energie", 5) for e in entrees if e.get("energie")]
    
    return {
        "derniere_entree": entrees[0] if entrees else None,
        "humeur_moyenne": sum(humeurs) / len(humeurs) if humeurs else None,
        "energie_moyenne": sum(energies) / len(energies) if energies else None,
        "entrees_semaine": len([e for e in entrees if _est_cette_semaine(e.get("date"))]),
    }


def calculer_metriques_budget(transactions: list[dict] = None) -> dict:
    """
    Calcule les mÃ©triques de budget.
    
    Args:
        transactions: Liste des transactions
        
    Returns:
        Dictionnaire des mÃ©triques budget
    """
    transactions = transactions or []
    if not transactions:
        return {
            "total_mois": 0,
            "depenses_courses": 0,
            "solde": 0,
            "tendance": "stable",
        }
    
    # Calculs basiques
    depenses = sum(t.get("montant", 0) for t in transactions if t.get("type") == "depense")
    revenus = sum(t.get("montant", 0) for t in transactions if t.get("type") == "revenu")
    
    return {
        "total_mois": depenses,
        "depenses_courses": sum(t.get("montant", 0) for t in transactions if t.get("categorie") == "courses"),
        "solde": revenus - depenses,
        "tendance": "hausse" if depenses > 0 else "stable",
    }


def _est_cette_semaine(date_val) -> bool:
    """VÃ©rifie si une date est dans cette semaine."""
    if date_val is None:
        return False
    if isinstance(date_val, str):
        try:
            date_val = datetime.fromisoformat(date_val).date()
        except ValueError:
            return False
    if isinstance(date_val, datetime):
        date_val = date_val.date()
    
    aujourd_hui = date.today()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    return debut_semaine <= date_val <= fin_semaine


def calculer_metriques_globales(
    recettes: list[dict] = None,
    inventaire: list[dict] = None,
    courses: list[dict] = None,
    planning: list[dict] = None
) -> dict:
    """
    Calcule toutes les mÃ©triques du dashboard.
    
    Args:
        recettes: Liste des recettes
        inventaire: Liste de l'inventaire
        courses: Liste des listes de courses
        planning: Liste des Ã©vÃ©nements
        
    Returns:
        Dictionnaire complet des mÃ©triques
    """
    return {
        "julius": calculer_age_julius(),
        "recettes": calculer_metriques_recettes(recettes or []),
        "inventaire": calculer_metriques_inventaire(inventaire or []),
        "courses": calculer_metriques_courses(courses or []),
        "planning": calculer_metriques_planning(planning or []),
        "timestamp": datetime.now().isoformat(),
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# NOTIFICATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def generer_notifications_inventaire(articles: list[dict]) -> list[dict]:
    """
    GÃ©nÃ¨re les notifications liÃ©es Ã  l'inventaire.
    
    Args:
        articles: Liste des articles de l'inventaire
        
    Returns:
        Liste de notifications
    """
    notifications = []
    aujourd_hui = date.today()
    dans_3_jours = aujourd_hui + timedelta(days=3)
    
    for article in articles:
        nom = article.get("ingredient_nom", "Article")
        quantite = article.get("quantite", 0)
        
        # Stock critique
        seuil_critique = article.get("seuil_critique", 2)
        if quantite <= seuil_critique:
            notifications.append({
                "type": "critique",
                "titre": f"Stock critique: {nom}",
                "message": f"Seulement {quantite} en stock",
                "module": "inventaire",
                "priorite": 1,
            })
            continue
        
        # Stock bas
        seuil_alerte = article.get("seuil_alerte", 5)
        if quantite <= seuil_alerte:
            notifications.append({
                "type": "alerte",
                "titre": f"Stock bas: {nom}",
                "message": f"{quantite} en stock",
                "module": "inventaire",
                "priorite": 2,
            })
        
        # PÃ©remption
        date_peremption = article.get("date_peremption")
        if date_peremption:
            if isinstance(date_peremption, datetime):
                date_peremption = date_peremption.date()
            
            if date_peremption < aujourd_hui:
                notifications.append({
                    "type": "critique",
                    "titre": f"Article pÃ©rimÃ©: {nom}",
                    "message": f"PÃ©rimÃ© depuis le {date_peremption.strftime('%d/%m')}",
                    "module": "inventaire",
                    "priorite": 0,
                })
            elif date_peremption <= dans_3_jours:
                jours = (date_peremption - aujourd_hui).days
                notifications.append({
                    "type": "alerte",
                    "titre": f"PÃ©remption proche: {nom}",
                    "message": f"PÃ©rime dans {jours} jour(s)",
                    "module": "inventaire",
                    "priorite": 1,
                })
    
    return notifications


def generer_notifications_courses(listes: list[dict]) -> list[dict]:
    """
    GÃ©nÃ¨re les notifications liÃ©es aux courses.
    
    Args:
        listes: Liste des listes de courses
        
    Returns:
        Liste de notifications
    """
    notifications = []
    
    articles_haute_priorite = 0
    for liste in listes:
        if liste.get("archivee"):
            continue
        
        for article in liste.get("articles", []):
            if not article.get("achete") and article.get("priorite") == "haute":
                articles_haute_priorite += 1
    
    if articles_haute_priorite > 0:
        notifications.append({
            "type": "alerte",
            "titre": "Articles urgents",
            "message": f"{articles_haute_priorite} article(s) haute prioritÃ© Ã  acheter",
            "module": "courses",
            "priorite": 2,
        })
    
    return notifications


def generer_notifications_planning(evenements: list[dict]) -> list[dict]:
    """
    GÃ©nÃ¨re les notifications liÃ©es au planning.
    
    Args:
        evenements: Liste des Ã©vÃ©nements
        
    Returns:
        Liste de notifications
    """
    notifications = []
    aujourd_hui = date.today()
    
    evt_aujourd_hui = []
    for evt in evenements:
        date_evt = evt.get("date")
        if not date_evt:
            continue
        if isinstance(date_evt, datetime):
            date_evt = date_evt.date()
        
        if date_evt == aujourd_hui:
            evt_aujourd_hui.append(evt)
    
    if evt_aujourd_hui:
        notifications.append({
            "type": "info",
            "titre": f"{len(evt_aujourd_hui)} Ã©vÃ©nement(s) aujourd'hui",
            "message": ", ".join(e.get("titre", "?") for e in evt_aujourd_hui[:3]),
            "module": "planning",
            "priorite": 3,
        })
    
    return notifications


def generer_notifications_globales(
    inventaire: list[dict] = None,
    courses: list[dict] = None,
    planning: list[dict] = None
) -> list[dict]:
    """
    GÃ©nÃ¨re toutes les notifications du dashboard.
    
    Args:
        inventaire: Liste de l'inventaire
        courses: Liste des listes de courses
        planning: Liste des Ã©vÃ©nements
        
    Returns:
        Liste de notifications triÃ©es par prioritÃ©
    """
    notifications = []
    
    notifications.extend(generer_notifications_inventaire(inventaire or []))
    notifications.extend(generer_notifications_courses(courses or []))
    notifications.extend(generer_notifications_planning(planning or []))
    
    # Trier par prioritÃ© (0 = plus urgent)
    notifications.sort(key=lambda n: n.get("priorite", 99))
    
    return notifications


def generer_notifications_critiques(
    inventaire: list[dict] = None,
    courses: list[dict] = None,
    planning: list[dict] = None
) -> list[dict]:
    """
    GÃ©nÃ¨re uniquement les notifications critiques du dashboard.
    
    Args:
        inventaire: Liste de l'inventaire
        courses: Liste des listes de courses
        planning: Liste des Ã©vÃ©nements
        
    Returns:
        Liste de notifications critiques uniquement
    """
    toutes = generer_notifications_globales(inventaire, courses, planning)
    return [n for n in toutes if n.get("type") == "critique"]


def generer_suggestions_actions(
    inventaire: list[dict] = None,
    courses: list[dict] = None,
    planning: list[dict] = None
) -> list[dict]:
    """
    GÃ©nÃ¨re des suggestions d'actions basÃ©es sur l'Ã©tat actuel.
    
    Args:
        inventaire: Liste de l'inventaire
        courses: Liste des listes de courses
        planning: Liste des Ã©vÃ©nements
        
    Returns:
        Liste de suggestions d'actions
    """
    suggestions = []
    
    # Suggestions basÃ©es sur l'inventaire
    if inventaire:
        articles_bas = [a for a in inventaire if a.get("quantite", 0) < a.get("seuil_alerte", 5)]
        if articles_bas:
            suggestions.append({
                "titre": "ðŸ“¦ Faire les courses",
                "description": f"{len(articles_bas)} article(s) en stock bas",
                "priorite": 1,
                "action": "courses",
            })
    
    # Suggestions basÃ©es sur le planning
    if planning:
        today = date.today()
        evt_aujourd_hui = [e for e in planning if _parse_date_evenement(e) == today]
        if evt_aujourd_hui:
            suggestions.append({
                "titre": "ðŸ“… Ã‰vÃ©nements aujourd'hui",
                "description": f"{len(evt_aujourd_hui)} Ã©vÃ©nement(s) prÃ©vu(s)",
                "priorite": 2,
                "action": "planning",
            })
    
    return sorted(suggestions, key=lambda s: s.get("priorite", 99))


def _parse_date_evenement(evt: dict) -> Optional[date]:
    """Parse la date d'un Ã©vÃ©nement."""
    date_str = evt.get("date") or evt.get("date_debut")
    if isinstance(date_str, date):
        return date_str
    if isinstance(date_str, datetime):
        return date_str.date()
    if isinstance(date_str, str):
        try:
            return datetime.fromisoformat(date_str).date()
        except ValueError:
            return None
    return None


def compter_notifications_par_type(notifications: list[dict]) -> dict:
    """
    Compte les notifications par type.
    
    Args:
        notifications: Liste des notifications
        
    Returns:
        Dictionnaire {type: count}
    """
    counts = {key: 0 for key in NOTIFICATION_TYPES.keys()}
    
    for notif in notifications:
        notif_type = notif.get("type", "info")
        if notif_type in counts:
            counts[notif_type] += 1
    
    return counts


def filtrer_notifications(notifications: list[dict], type_filtre: Optional[str] = None) -> list[dict]:
    """
    Filtre les notifications par type.
    
    Args:
        notifications: Liste des notifications
        type_filtre: Type Ã  filtrer ou None pour tout
        
    Returns:
        Liste filtrÃ©e
    """
    if not type_filtre or type_filtre == "tous":
        return notifications
    
    return [n for n in notifications if n.get("type") == type_filtre]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ACTIVITÃ‰S RÃ‰CENTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_activite_recente(activite: dict) -> dict:
    """
    Formate une activitÃ© rÃ©cente pour l'affichage.
    
    Args:
        activite: Dictionnaire de l'activitÃ©
        
    Returns:
        ActivitÃ© formatÃ©e
    """
    type_activite = activite.get("type", "autre")
    
    icones = {
        "recette": "ðŸ³",
        "courses": "ðŸ›’",
        "inventaire": "ðŸ“¦",
        "planning": "ðŸ“…",
        "famille": "ðŸ‘¨â€ðŸ‘©â€ðŸ‘¦",
        "autre": "ðŸ“",
    }
    
    return {
        "icone": icones.get(type_activite, "ðŸ“"),
        "titre": activite.get("titre", "ActivitÃ©"),
        "description": activite.get("description", ""),
        "timestamp": activite.get("timestamp"),
        "type": type_activite,
        "ago": calculer_temps_ecoule(activite.get("timestamp")),
    }


def calculer_temps_ecoule(timestamp: Optional[datetime]) -> str:
    """
    Calcule le temps Ã©coulÃ© depuis un timestamp.
    
    Args:
        timestamp: Datetime de l'Ã©vÃ©nement
        
    Returns:
        ChaÃ®ne formatÃ©e (ex: "il y a 2 heures")
    """
    if not timestamp:
        return "Date inconnue"
    
    maintenant = datetime.now()
    delta = maintenant - timestamp
    
    if delta.days > 7:
        return f"le {timestamp.strftime('%d/%m')}"
    elif delta.days > 1:
        return f"il y a {delta.days} jours"
    elif delta.days == 1:
        return "hier"
    elif delta.seconds > 3600:
        heures = delta.seconds // 3600
        return f"il y a {heures}h"
    elif delta.seconds > 60:
        minutes = delta.seconds // 60
        return f"il y a {minutes} min"
    else:
        return "Ã  l'instant"


def trier_activites_par_date(activites: list[dict], limit: int = 10) -> list[dict]:
    """
    Trie les activitÃ©s par date (plus rÃ©centes en premier).
    
    Args:
        activites: Liste des activitÃ©s
        limit: Nombre maximum d'activitÃ©s Ã  retourner
        
    Returns:
        Liste triÃ©e et limitÃ©e
    """
    def sort_key(activite):
        timestamp = activite.get("timestamp")
        if not timestamp:
            return datetime.min
        return timestamp
    
    sorted_activites = sorted(activites, key=sort_key, reverse=True)
    return sorted_activites[:limit]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def generer_suggestions_actions(metriques: dict, notifications: list[dict]) -> list[dict]:
    """
    GÃ©nÃ¨re des suggestions d'actions basÃ©es sur les mÃ©triques.
    
    Args:
        metriques: MÃ©triques du dashboard
        notifications: Liste des notifications
        
    Returns:
        Liste de suggestions
    """
    suggestions = []
    
    # Suggestions basÃ©es sur l'inventaire
    inv_metriques = metriques.get("inventaire", {})
    if inv_metriques.get("alertes", 0) > 5:
        suggestions.append({
            "action": "Mettre Ã  jour l'inventaire",
            "raison": f"{inv_metriques['alertes']} articles en alerte",
            "priorite": 1,
            "module": "inventaire",
        })
    
    if inv_metriques.get("perimes", 0) > 0:
        suggestions.append({
            "action": "Retirer les articles pÃ©rimÃ©s",
            "raison": f"{inv_metriques['perimes']} article(s) pÃ©rimÃ©(s)",
            "priorite": 0,
            "module": "inventaire",
        })
    
    # Suggestions basÃ©es sur les courses
    courses_metriques = metriques.get("courses", {})
    if courses_metriques.get("articles_a_acheter", 0) > 10:
        suggestions.append({
            "action": "Planifier les courses",
            "raison": f"{courses_metriques['articles_a_acheter']} articles Ã  acheter",
            "priorite": 2,
            "module": "courses",
        })
    
    # Suggestions basÃ©es sur le planning
    planning_metriques = metriques.get("planning", {})
    if planning_metriques.get("aujourd_hui", 0) > 0:
        suggestions.append({
            "action": "Consulter le planning du jour",
            "raison": f"{planning_metriques['aujourd_hui']} Ã©vÃ©nement(s) aujourd'hui",
            "priorite": 1,
            "module": "planning",
        })
    
    # Trier par prioritÃ©
    suggestions.sort(key=lambda s: s.get("priorite", 99))
    
    return suggestions


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE DASHBOARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_metrique_card(titre: str, valeur: Any, unite: str = "", icone: str = "ðŸ“Š") -> dict:
    """
    Formate une carte mÃ©trique pour l'affichage.
    
    Args:
        titre: Titre de la mÃ©trique
        valeur: Valeur Ã  afficher
        unite: UnitÃ© (optionnel)
        icone: Emoji/icÃ´ne
        
    Returns:
        Dictionnaire formatÃ©
    """
    return {
        "titre": titre,
        "valeur": valeur,
        "unite": unite,
        "icone": icone,
        "display": f"{valeur}{unite}" if unite else str(valeur),
    }


def generer_cartes_metriques(metriques: dict) -> list[dict]:
    """
    GÃ©nÃ¨re les cartes mÃ©triques Ã  afficher.
    
    Args:
        metriques: Dictionnaire des mÃ©triques globales
        
    Returns:
        Liste de cartes formatÃ©es
    """
    julius = metriques.get("julius", {})
    recettes = metriques.get("recettes", {})
    inventaire = metriques.get("inventaire", {})
    courses = metriques.get("courses", {})
    
    return [
        formater_metrique_card(
            "Julius",
            f"{julius.get('mois', 0)}m {julius.get('jours', 0)}j",
            icone="ðŸ‘¶"
        ),
        formater_metrique_card(
            "Recettes",
            recettes.get("total", 0),
            icone="ðŸ³"
        ),
        formater_metrique_card(
            "Stock alertes",
            inventaire.get("alertes", 0),
            icone="âš ï¸"
        ),
        formater_metrique_card(
            "Ã€ acheter",
            courses.get("articles_a_acheter", 0),
            icone="ðŸ›’"
        ),
    ]

