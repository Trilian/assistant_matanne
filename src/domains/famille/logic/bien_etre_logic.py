"""
Logique métier du module Bien-être (famille) - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

CATEGORIES_BIEN_ETRE = ["Sommeil", "Nutrition", "Activité physique", "Mental", "Social", "Hydratation"]
HUMEURS = ["😊 Joyeux", "😌 Calme", "😐 Neutre", "😢 Triste", "😠 Irritable", "😴 Fatigué"]
NIVEAUX_ENERGIE = ["Très bas", "Bas", "Moyen", "Bon", "Excellent"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSE DES TENDANCES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def analyser_tendance(entrees: List[Dict[str, Any]], categorie: str, jours: int = 7) -> Dict[str, Any]:
    """
    Analyse la tendance d'une catégorie de bien-être.
    
    Args:
        entrees: Liste des entrées
        categorie: Catégorie à analyser
        jours: Période d'analyse
        
    Returns:
        Statistiques de tendance
    """
    date_limite = date.today() - timedelta(days=jours)
    
    entrees_categorie = []
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite and entree.get("categorie") == categorie:
            entrees_categorie.append(entree)
    
    if not entrees_categorie:
        return {
            "total": 0,
            "moyenne": 0.0,
            "tendance": "stable",
            "evolution": 0.0
        }
    
    # Calculer moyenne des valeurs
    valeurs = [e.get("valeur", 0) for e in entrees_categorie]
    moyenne = sum(valeurs) / len(valeurs)
    
    # Déterminer tendance (comparer première et dernière moitié)
    mid = len(valeurs) // 2
    if mid > 0:
        moyenne_debut = sum(valeurs[:mid]) / mid
        moyenne_fin = sum(valeurs[mid:]) / (len(valeurs) - mid)
        
        if moyenne_fin > moyenne_debut * 1.1:
            tendance = "hausse"
        elif moyenne_fin < moyenne_debut * 0.9:
            tendance = "baisse"
        else:
            tendance = "stable"
        
        evolution = ((moyenne_fin - moyenne_debut) / moyenne_debut * 100) if moyenne_debut > 0 else 0
    else:
        tendance = "stable"
        evolution = 0.0
    
    return {
        "total": len(entrees_categorie),
        "moyenne": moyenne,
        "tendance": tendance,
        "evolution": evolution
    }


def calculer_score_global(entrees_par_categorie: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Calcule un score global de bien-être.
    
    Args:
        entrees_par_categorie: Entrées groupées par catégorie
        
    Returns:
        Score et détails
    """
    scores_par_categorie = {}
    
    for cat, entrees in entrees_par_categorie.items():
        if entrees:
            valeurs = [e.get("valeur", 0) for e in entrees]
            scores_par_categorie[cat] = sum(valeurs) / len(valeurs)
        else:
            scores_par_categorie[cat] = 0
    
    # Score global (moyenne des catégories)
    if scores_par_categorie:
        score_global = sum(scores_par_categorie.values()) / len(scores_par_categorie)
    else:
        score_global = 0
    
    # Niveau
    if score_global >= 8:
        niveau = "Excellent"
    elif score_global >= 6:
        niveau = "Bon"
    elif score_global >= 4:
        niveau = "Moyen"
    else:
        niveau = "Faible"
    
    return {
        "score": score_global,
        "niveau": niveau,
        "par_categorie": scores_par_categorie
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSES SPÉCIFIQUES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def analyser_sommeil(entrees: List[Dict[str, Any]], jours: int = 7) -> Dict[str, Any]:
    """Analyse spécifique du sommeil."""
    date_limite = date.today() - timedelta(days=jours)
    
    heures_sommeil = []
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite and entree.get("categorie") == "Sommeil":
            heures = entree.get("heures_sommeil") or entree.get("valeur", 0)
            if heures:
                heures_sommeil.append(heures)
    
    if not heures_sommeil:
        return {
            "moyenne": 0.0,
            "qualite": "Inconnu",
            "regularite": "Inconnu"
        }
    
    moyenne = sum(heures_sommeil) / len(heures_sommeil)
    
    # Qualité basée sur moyenne
    if moyenne >= 8:
        qualite = "Excellent"
    elif moyenne >= 7:
        qualite = "Bon"
    elif moyenne >= 6:
        qualite = "Moyen"
    else:
        qualite = "Insuffisant"
    
    # Régularité (écart-type)
    variance = sum((h - moyenne) ** 2 for h in heures_sommeil) / len(heures_sommeil)
    ecart_type = variance ** 0.5
    
    if ecart_type < 0.5:
        regularite = "Très régulier"
    elif ecart_type < 1:
        regularite = "Régulier"
    else:
        regularite = "Irrégulier"
    
    return {
        "moyenne": moyenne,
        "qualite": qualite,
        "regularite": regularite,
        "ecart_type": ecart_type
    }


def analyser_humeurs(entrees: List[Dict[str, Any]], jours: int = 7) -> Dict[str, Any]:
    """Analyse des humeurs."""
    date_limite = date.today() - timedelta(days=jours)
    
    compteur = {}
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite:
            humeur = entree.get("humeur", "💰 Neutre")
            compteur[humeur] = compteur.get(humeur, 0) + 1
    
    # Humeur dominante
    humeur_dominante = None
    if compteur:
        humeur_dominante = max(compteur.items(), key=lambda x: x[1])[0]
    
    return {
        "distribution": compteur,
        "humeur_dominante": humeur_dominante,
        "total_entrees": sum(compteur.values())
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# RECOMMANDATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def generer_recommandations(scores: Dict[str, float]) -> List[str]:
    """Génère des recommandations basées sur les scores."""
    recommandations = []
    
    for categorie, score in scores.items():
        if score < 5:
            if categorie == "Sommeil":
                recommandations.append("🗑️ Améliorer la qualité du sommeil (routine, horaires réguliers)")
            elif categorie == "Nutrition":
                recommandations.append("📅 Équilibrer l'alimentation (fruits, légumes, hydratation)")
            elif categorie == "Activité physique":
                recommandations.append("💡 Augmenter l'activité physique (30min/jour minimum)")
            elif categorie == "Mental":
                recommandations.append("🧹 Prendre du temps pour soi (méditation, relaxation)")
            elif categorie == "Social":
                recommandations.append("🎯 Renforcer les liens sociaux (famille, amis)")
    
    return recommandations


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_entree_bien_etre(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Valide une entrée bien-être."""
    erreurs = []
    
    if "categorie" not in data or not data["categorie"]:
        erreurs.append("La catégorie est requise")
    
    if "categorie" in data and data["categorie"] not in CATEGORIES_BIEN_ETRE:
        erreurs.append(f"Catégorie invalide. Valeurs: {', '.join(CATEGORIES_BIEN_ETRE)}")
    
    if "valeur" in data:
        val = data["valeur"]
        if not isinstance(val, (int, float)) or not (0 <= val <= 10):
            erreurs.append("La valeur doit être entre 0 et 10")
    
    if "humeur" in data and data["humeur"] not in HUMEURS:
        erreurs.append(f"Humeur invalide. Valeurs: {', '.join(HUMEURS)}")
    
    return len(erreurs) == 0, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_evolution(evolution: float) -> str:
    """Formate une évolution en pourcentage."""
    if evolution > 0:
        return f"👶 +{evolution:.1f}%"
    elif evolution < 0:
        return f"🍽️ {evolution:.1f}%"
    else:
        return "âž¡ï¸ Stable"


def grouper_par_semaine(entrees: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Groupe les entrées par semaine."""
    groupes = {}
    
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree:
            # Calculer numéro de semaine
            semaine = date_entree.isocalendar()[1]
            annee = date_entree.year
            key = f"{annee}-S{semaine}"
            
            if key not in groupes:
                groupes[key] = []
            groupes[key].append(entree)
    
    return groupes

