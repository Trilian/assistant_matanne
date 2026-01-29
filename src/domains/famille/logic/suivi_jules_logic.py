"""
Logique mÃ©tier du module Suivi Jules (famille) - SÃ©parÃ©e de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

HUMEURS = ["ðŸ˜Š Joyeux", "ðŸ˜Œ Calme", "ðŸ˜´ FatiguÃ©", "ðŸ˜¢ Triste", "ðŸ˜  Irritable"]
CATEGORIES_MILESTONE = ["MotricitÃ©", "Langage", "Social", "Cognitif", "Autonomie"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCUL DE L'Ã‚GE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_age(date_naissance: date) -> Dict[str, int]:
    """
    Calcule l'Ã¢ge dÃ©taillÃ© depuis la date de naissance.
    
    Args:
        date_naissance: Date de naissance
        
    Returns:
        Dictionnaire {annÃ©es, mois, jours, total_mois}
    """
    today = date.today()
    
    # AnnÃ©es
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
        
        # Calculer jours du mois prÃ©cÃ©dent
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
    Formate l'Ã¢ge de maniÃ¨re lisible.
    
    Args:
        age_dict: Dictionnaire d'Ã¢ge de calculer_age()
        
    Returns:
        ChaÃ®ne formatÃ©e
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰TAPES DE DÃ‰VELOPPEMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

ETAPES_DEVELOPPEMENT = {
    12: [
        {"categorie": "MotricitÃ©", "description": "Marche seul"},
        {"categorie": "Langage", "description": "Dit quelques mots"},
        {"categorie": "Social", "description": "Imite les adultes"}
    ],
    18: [
        {"categorie": "MotricitÃ©", "description": "Monte les escaliers"},
        {"categorie": "Langage", "description": "Vocabulaire de 20-50 mots"},
        {"categorie": "Autonomie", "description": "Boit au verre seul"}
    ],
    24: [
        {"categorie": "MotricitÃ©", "description": "Court, saute"},
        {"categorie": "Langage", "description": "Phrases de 2-3 mots"},
        {"categorie": "Social", "description": "Joue Ã  cÃ´tÃ© d'autres enfants"}
    ],
    36: [
        {"categorie": "MotricitÃ©", "description": "PÃ©dale sur tricycle"},
        {"categorie": "Langage", "description": "Phrases complÃ¨tes"},
        {"categorie": "Autonomie", "description": "S'habille partiellement seul"}
    ]
}


def get_etapes_age(age_mois: int) -> List[Dict[str, str]]:
    """
    Retourne les Ã©tapes de dÃ©veloppement attendues pour un Ã¢ge.
    
    Args:
        age_mois: Ã‚ge en mois
        
    Returns:
        Liste des Ã©tapes
    """
    # Trouver la tranche d'Ã¢ge la plus proche
    tranches = sorted(ETAPES_DEVELOPPEMENT.keys())
    
    for tranche in reversed(tranches):
        if age_mois >= tranche:
            return ETAPES_DEVELOPPEMENT[tranche]
    
    # Si trop jeune, retourner premiÃ¨re tranche
    if tranches:
        return ETAPES_DEVELOPPEMENT[tranches[0]]
    
    return []


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES BIEN-ÃŠTRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_moyenne_sommeil(entrees: List[Dict[str, Any]], jours: int = 7) -> float:
    """
    Calcule la moyenne d'heures de sommeil.
    
    Args:
        entrees: Liste des entrÃ©es bien-Ãªtre
        jours: Nombre de jours Ã  analyser
        
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
    Analyse les humeurs sur une pÃ©riode.
    
    Args:
        entrees: Liste des entrÃ©es bien-Ãªtre
        jours: Nombre de jours Ã  analyser
        
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


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_entree_bien_etre(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide une entrÃ©e bien-Ãªtre.
    
    Args:
        data: DonnÃ©es de l'entrÃ©e
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "humeur" in data and data["humeur"] not in HUMEURS:
        erreurs.append(f"Humeur invalide. Valeurs autorisÃ©es: {', '.join(HUMEURS)}")
    
    if "heures_sommeil" in data:
        sommeil = data["heures_sommeil"]
        if not isinstance(sommeil, (int, float)) or not (0 <= sommeil <= 24):
            erreurs.append("Les heures de sommeil doivent Ãªtre entre 0 et 24")
    
    return len(erreurs) == 0, erreurs


def valider_milestone(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide un milestone.
    
    Args:
        data: DonnÃ©es du milestone
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_MILESTONE:
        erreurs.append(f"CatÃ©gorie invalide. Valeurs autorisÃ©es: {', '.join(CATEGORIES_MILESTONE)}")
    
    return len(erreurs) == 0, erreurs

