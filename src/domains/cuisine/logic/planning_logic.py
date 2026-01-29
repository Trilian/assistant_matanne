"""
Logique mÃ©tier du module Planning (cuisine) - SÃ©parÃ©e de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta, datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
JOURS_EMOJI = ["ðŸŸ¡", "ðŸŸ ", "ðŸŸ£", "ðŸ”µ", "ðŸŸ¢", "âš«", "ðŸ”´"]
TYPES_REPAS = ["dÃ©jeuner", "dÃ®ner"]
REGIMES = ["Omnivore", "VÃ©gÃ©tarien", "VÃ©gan", "Sans gluten"]
TEMPS_CUISINE = ["Rapide (< 30 min)", "Moyen (30-60 min)", "Long (> 60 min)"]
BUDGETS = ["Bas (< 20â‚¬)", "Moyen (20-40â‚¬)", "Haut (> 40â‚¬)"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FONCTIONS DE CALCUL DE DATES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_debut_semaine(date_ref: date = None) -> date:
    """
    Retourne le lundi de la semaine donnÃ©e.
    
    Args:
        date_ref: Date de rÃ©fÃ©rence (aujourd'hui par dÃ©faut)
        
    Returns:
        Date du lundi de la semaine
    """
    if date_ref is None:
        date_ref = date.today()
    
    debut = date_ref - timedelta(days=date_ref.weekday())
    return debut


def get_fin_semaine(date_ref: date = None) -> date:
    """
    Retourne le dimanche de la semaine donnÃ©e.
    
    Args:
        date_ref: Date de rÃ©fÃ©rence (aujourd'hui par dÃ©faut)
        
    Returns:
        Date du dimanche de la semaine
    """
    debut = get_debut_semaine(date_ref)
    return debut + timedelta(days=6)


def get_dates_semaine(date_ref: date = None) -> List[date]:
    """
    Retourne la liste des 7 dates de la semaine.
    
    Args:
        date_ref: Date de rÃ©fÃ©rence (aujourd'hui par dÃ©faut)
        
    Returns:
        Liste des 7 dates (lundi Ã  dimanche)
    """
    debut = get_debut_semaine(date_ref)
    return [debut + timedelta(days=i) for i in range(7)]


def get_numero_semaine(date_ref: date = None) -> int:
    """
    Retourne le numÃ©ro de semaine ISO.
    
    Args:
        date_ref: Date de rÃ©fÃ©rence (aujourd'hui par dÃ©faut)
        
    Returns:
        NumÃ©ro de semaine (1-53)
    """
    if date_ref is None:
        date_ref = date.today()
    
    return date_ref.isocalendar()[1]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ORGANISATION DES REPAS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def organiser_repas_par_jour(repas: List[Any]) -> Dict[str, List[Any]]:
    """
    Organise une liste de repas par jour.
    
    Args:
        repas: Liste d'objets Repas
        
    Returns:
        Dictionnaire {jour: [repas]}
    """
    repas_par_jour = {}
    
    for r in repas:
        jour = r.jour if hasattr(r, 'jour') else None
        if jour:
            if jour not in repas_par_jour:
                repas_par_jour[jour] = []
            repas_par_jour[jour].append(r)
    
    return repas_par_jour


def organiser_repas_par_type(repas: List[Any]) -> Dict[str, List[Any]]:
    """
    Organise une liste de repas par type (dÃ©jeuner/dÃ®ner).
    
    Args:
        repas: Liste d'objets Repas
        
    Returns:
        Dictionnaire {type_repas: [repas]}
    """
    repas_par_type = {}
    
    for r in repas:
        type_repas = r.type_repas if hasattr(r, 'type_repas') else "autre"
        if type_repas not in repas_par_type:
            repas_par_type[type_repas] = []
        repas_par_type[type_repas].append(r)
    
    return repas_par_type


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# STATISTIQUES ET MÃ‰TRIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_statistiques_planning(planning: Any) -> Dict[str, Any]:
    """
    Calcule les statistiques d'un planning.
    
    Args:
        planning: Objet Planning avec repas
        
    Returns:
        Dictionnaire de statistiques
    """
    if not planning or not hasattr(planning, 'repas'):
        return {
            "total_repas": 0,
            "repas_dejeuner": 0,
            "repas_diner": 0,
            "jours_complets": 0,
            "taux_completion": 0.0
        }
    
    repas = planning.repas or []
    repas_par_jour = organiser_repas_par_jour(repas)
    repas_par_type = organiser_repas_par_type(repas)
    
    # Compter jours complets (2 repas)
    jours_complets = sum(1 for jr in repas_par_jour.values() if len(jr) >= 2)
    
    return {
        "total_repas": len(repas),
        "repas_dejeuner": len(repas_par_type.get("dÃ©jeuner", [])),
        "repas_diner": len(repas_par_type.get("dÃ®ner", [])),
        "jours_complets": jours_complets,
        "taux_completion": (len(repas) / 14.0) * 100 if repas else 0.0
    }


def calculer_cout_planning(planning: Any, prix_recettes: Dict[int, float]) -> float:
    """
    Calcule le coÃ»t total d'un planning.
    
    Args:
        planning: Objet Planning avec repas
        prix_recettes: Dictionnaire {recette_id: prix}
        
    Returns:
        CoÃ»t total en euros
    """
    if not planning or not hasattr(planning, 'repas'):
        return 0.0
    
    cout_total = 0.0
    for repas in (planning.repas or []):
        recette_id = repas.recette_id if hasattr(repas, 'recette_id') else None
        if recette_id and recette_id in prix_recettes:
            cout_total += prix_recettes[recette_id]
    
    return cout_total


def calculer_variete_planning(planning: Any) -> Dict[str, Any]:
    """
    Calcule les mÃ©triques de variÃ©tÃ© d'un planning.
    
    Args:
        planning: Objet Planning avec repas
        
    Returns:
        Dictionnaire avec mÃ©triques de variÃ©tÃ©
    """
    if not planning or not hasattr(planning, 'repas'):
        return {
            "recettes_uniques": 0,
            "taux_variete": 0.0,
            "recettes_repetees": []
        }
    
    repas = planning.repas or []
    recettes_ids = [r.recette_id for r in repas if hasattr(r, 'recette_id')]
    recettes_uniques = set(recettes_ids)
    
    # Trouver rÃ©pÃ©titions
    from collections import Counter
    compteur = Counter(recettes_ids)
    repetees = [(rid, count) for rid, count in compteur.items() if count > 1]
    
    return {
        "recettes_uniques": len(recettes_uniques),
        "taux_variete": (len(recettes_uniques) / len(recettes_ids) * 100) if recettes_ids else 0.0,
        "recettes_repetees": repetees
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_repas(data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Valide les donnÃ©es d'un repas.
    
    Args:
        data: DonnÃ©es du repas
        
    Returns:
        (est_valide, message_erreur)
    """
    # Jour requis
    if "jour" not in data or not data["jour"]:
        return False, "Le jour est requis"
    
    # Type repas requis
    if "type_repas" not in data or not data["type_repas"]:
        return False, "Le type de repas est requis"
    
    # VÃ©rifier type repas valide
    if data["type_repas"] not in TYPES_REPAS:
        return False, f"Type de repas invalide. Valeurs autorisÃ©es: {', '.join(TYPES_REPAS)}"
    
    # Recette requise
    if "recette_id" not in data or not data["recette_id"]:
        return False, "Une recette doit Ãªtre sÃ©lectionnÃ©e"
    
    return True, None


def valider_planning(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Valide les donnÃ©es d'un planning complet.
    
    Args:
        data: DonnÃ©es du planning
        
    Returns:
        (est_valide, liste_erreurs)
    """
    erreurs = []
    
    # Semaine dÃ©but requise
    if "semaine_debut" not in data or not data["semaine_debut"]:
        erreurs.append("La date de dÃ©but de semaine est requise")
    
    # Repas
    if "repas" in data and data["repas"]:
        for i, repas in enumerate(data["repas"]):
            valide, erreur = valider_repas(repas)
            if not valide:
                erreurs.append(f"Repas {i+1}: {erreur}")
    
    return len(erreurs) == 0, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# GÃ‰NÃ‰RATION ET SUGGESTIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def generer_structure_semaine() -> Dict[str, List[str]]:
    """
    GÃ©nÃ¨re la structure vide d'une semaine (7 jours, 2 repas/jour).
    
    Returns:
        Dictionnaire {jour: [types_repas]}
    """
    structure = {}
    for jour in JOURS_SEMAINE:
        structure[jour] = TYPES_REPAS.copy()
    return structure


def calculer_contraintes_ia(preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convertit les prÃ©fÃ©rences utilisateur en contraintes pour l'IA.
    
    Args:
        preferences: PrÃ©fÃ©rences utilisateur (rÃ©gimes, temps, budget, etc.)
        
    Returns:
        Contraintes formatÃ©es pour l'IA
    """
    contraintes = {
        "regimes": preferences.get("regimes", ["Omnivore"]),
        "temps_max": preferences.get("temps_cuisine", "Moyen (30-60 min)"),
        "budget_max": preferences.get("budget", "Moyen (20-40â‚¬)"),
        "variete_min": preferences.get("variete", True),
        "equilibre": preferences.get("equilibre", True)
    }
    
    # Mapper temps cuisine en minutes
    temps_map = {
        "Rapide (< 30 min)": 30,
        "Moyen (30-60 min)": 60,
        "Long (> 60 min)": 120
    }
    contraintes["temps_max_minutes"] = temps_map.get(contraintes["temps_max"], 60)
    
    return contraintes


def formater_historique_planning(plannings: List[Any]) -> List[Dict[str, Any]]:
    """
    Formate une liste de plannings pour l'affichage historique.
    
    Args:
        plannings: Liste d'objets Planning
        
    Returns:
        Liste de dictionnaires formatÃ©s
    """
    resultats = []
    
    for p in plannings:
        stats = calculer_statistiques_planning(p)
        
        resultats.append({
            "id": p.id,
            "semaine_debut": p.semaine_debut,
            "semaine_fin": p.semaine_fin if hasattr(p, 'semaine_fin') else p.semaine_debut + timedelta(days=6),
            "total_repas": stats["total_repas"],
            "genere_par_ia": p.genere_par_ia if hasattr(p, 'genere_par_ia') else False,
            "taux_completion": stats["taux_completion"],
            "created_at": p.created_at if hasattr(p, 'created_at') else None
        })
    
    return resultats

