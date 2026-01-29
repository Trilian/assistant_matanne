"""
Logique métier du module Suivi Jules (famille) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

HUMEURS = ["😊 Joyeux", "😌 Calme", "😴 Fatigué", "😢 Triste", "😠 Irritable"]
CATEGORIES_MILESTONE = ["Motricité", "Langage", "Social", "Cognitif", "Autonomie"]


# ═══════════════════════════════════════════════════════════
# CALCUL DE L'ÂGE
# ═══════════════════════════════════════════════════════════

def calculer_age(date_naissance: date) -> Dict[str, int]:
    """
    Calcule l'âge détaillé depuis la date de naissance.
    
    Args:
        date_naissance: Date de naissance
        
    Returns:
        Dictionnaire {années, mois, jours, total_mois}
    """
    today = date.today()
    
    # Années
    annees = today.year - date_naissance.year
    
    # Mois
    mois = today.month - date_naissance.month
    if mois < 0:
        annees -= 1
        mois += 12
    
    # Jours
    jours = today.day - date_naissance.day
    if jours < 0:
        # Reculer d'un mois
        mois -= 1
        if mois < 0:
            annees -= 1
            mois += 12
        
        # Calculer jours du mois précédent
        mois_precedent = today.month - 1
        annee_ref = today.year
        if mois_precedent == 0:
            mois_precedent = 12
            annee_ref -= 1
        
        from calendar import monthrange
        _, jours_mois = monthrange(annee_ref, mois_precedent)
        jours += jours_mois
    
    # Total en mois
    total_mois = annees * 12 + mois
    
    return {
        "annees": annees,
        "mois": mois,
        "jours": jours,
        "total_mois": total_mois
    }


def formater_age(age_dict: Dict[str, int]) -> str:
    """
    Formate l'âge de manière lisible.
    
    Args:
        age_dict: Dictionnaire d'âge de calculer_age()
        
    Returns:
        Chaîne formatée
    """
    annees = age_dict["annees"]
    mois = age_dict["mois"]
    jours = age_dict["jours"]
    
    parties = []
    
    if annees > 0:
        parties.append(f"{annees} an{'s' if annees > 1 else ''}")
    
    if mois > 0 or annees == 0:
        parties.append(f"{mois} mois")
    
    if jours > 0 and annees == 0:
        parties.append(f"{jours} jour{'s' if jours > 1 else ''}")
    
    return " et ".join(parties)


# ═══════════════════════════════════════════════════════════
# ÉTAPES DE DÉVELOPPEMENT
# ═══════════════════════════════════════════════════════════

ETAPES_DEVELOPPEMENT = {
    12: [
        {"categorie": "Motricité", "description": "Marche seul"},
        {"categorie": "Langage", "description": "Dit quelques mots"},
        {"categorie": "Social", "description": "Imite les adultes"}
    ],
    18: [
        {"categorie": "Motricité", "description": "Monte les escaliers"},
        {"categorie": "Langage", "description": "Vocabulaire de 20-50 mots"},
        {"categorie": "Autonomie", "description": "Boit au verre seul"}
    ],
    24: [
        {"categorie": "Motricité", "description": "Court, saute"},
        {"categorie": "Langage", "description": "Phrases de 2-3 mots"},
        {"categorie": "Social", "description": "Joue à côté d'autres enfants"}
    ],
    36: [
        {"categorie": "Motricité", "description": "Pédale sur tricycle"},
        {"categorie": "Langage", "description": "Phrases complètes"},
        {"categorie": "Autonomie", "description": "S'habille partiellement seul"}
    ]
}


def get_etapes_age(age_mois: int) -> List[Dict[str, str]]:
    """
    Retourne les étapes de développement attendues pour un âge.
    
    Args:
        age_mois: Âge en mois
        
    Returns:
        Liste des étapes
    """
    # Trouver la tranche d'âge la plus proche
    tranches = sorted(ETAPES_DEVELOPPEMENT.keys())
    
    for tranche in reversed(tranches):
        if age_mois >= tranche:
            return ETAPES_DEVELOPPEMENT[tranche]
    
    # Si trop jeune, retourner première tranche
    if tranches:
        return ETAPES_DEVELOPPEMENT[tranches[0]]
    
    return []


# ═══════════════════════════════════════════════════════════
# STATISTIQUES BIEN-ÊTRE
# ═══════════════════════════════════════════════════════════

def calculer_moyenne_sommeil(entrees: List[Dict[str, Any]], jours: int = 7) -> float:
    """
    Calcule la moyenne d'heures de sommeil.
    
    Args:
        entrees: Liste des entrées bien-être
        jours: Nombre de jours à analyser
        
    Returns:
        Moyenne d'heures de sommeil
    """
    date_limite = date.today() - timedelta(days=jours)
    
    sommeils = []
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite:
            sommeil = entree.get("heures_sommeil")
            if sommeil:
                sommeils.append(sommeil)
    
    return sum(sommeils) / len(sommeils) if sommeils else 0.0


def analyser_humeurs(entrees: List[Dict[str, Any]], jours: int = 7) -> Dict[str, Any]:
    """
    Analyse les humeurs sur une période.
    
    Args:
        entrees: Liste des entrées bien-être
        jours: Nombre de jours à analyser
        
    Returns:
        Statistiques d'humeur
    """
    date_limite = date.today() - timedelta(days=jours)
    
    compteur = {}
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite:
            humeur = entree.get("humeur", "Neutre")
            compteur[humeur] = compteur.get(humeur, 0) + 1
    
    # Humeur dominante
    humeur_dominante = max(compteur.items(), key=lambda x: x[1])[0] if compteur else None
    
    return {
        "distribution": compteur,
        "humeur_dominante": humeur_dominante,
        "total_entrees": sum(compteur.values())
    }


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════

def valider_entree_bien_etre(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide une entrée bien-être.
    
    Args:
        data: Données de l'entrée
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "humeur" in data and data["humeur"] not in HUMEURS:
        erreurs.append(f"Humeur invalide. Valeurs autorisées: {', '.join(HUMEURS)}")
    
    if "heures_sommeil" in data:
        sommeil = data["heures_sommeil"]
        if not isinstance(sommeil, (int, float)) or not (0 <= sommeil <= 24):
            erreurs.append("Les heures de sommeil doivent être entre 0 et 24")
    
    return len(erreurs) == 0, erreurs


def valider_milestone(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide un milestone.
    
    Args:
        data: Données du milestone
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_MILESTONE:
        erreurs.append(f"Catégorie invalide. Valeurs autorisées: {', '.join(CATEGORIES_MILESTONE)}")
    
    return len(erreurs) == 0, erreurs
