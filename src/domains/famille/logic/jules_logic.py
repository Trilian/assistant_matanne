"""
Logique mÃ©tier du module Jules (suivi enfant) - SÃ©parÃ©e de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, timedelta
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

ETAPES_DEVELOPPEMENT = {
    "0-3": ["Sourire social", "Suit des yeux", "Tient sa tÃªte"],
    "3-6": ["Rit aux Ã©clats", "Attrape objets", "Se retourne"],
    "6-9": ["Babille", "Tient assis", "Pince pouce-index"],
    "9-12": ["Dit papa/maman", "Rampe/marche Ã  4 pattes", "Fait au revoir"],
    "12-18": ["Premiers mots", "Marche seul", "Pointe du doigt"],
    "18-24": ["Phrases 2 mots", "Court", "Monte escaliers"],
    "24-36": ["Phrases complÃ¨tes", "Saute", "PÃ©dale tricycle"]
}

CATEGORIES_MILESTONES = ["MotricitÃ©", "Langage", "Social", "Cognitif"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# CALCULS Ã‚GE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def calculer_age_mois(date_naissance: date, date_reference: Optional[date] = None) -> int:
    """Calcule l'Ã¢ge en mois."""
    if date_reference is None:
        date_reference = date.today()
    
    if isinstance(date_naissance, str):
        from datetime import datetime
        date_naissance = datetime.fromisoformat(date_naissance).date()
    
    if isinstance(date_reference, str):
        from datetime import datetime
        date_reference = datetime.fromisoformat(date_reference).date()
    
    mois = (date_reference.year - date_naissance.year) * 12
    mois += date_reference.month - date_naissance.month
    
    # Ajuster si le jour n'est pas encore atteint
    if date_reference.day < date_naissance.day:
        mois -= 1
    
    return max(0, mois)


def calculer_age_annees_mois(date_naissance: date, date_reference: Optional[date] = None) -> Dict[str, int]:
    """Calcule l'Ã¢ge en annÃ©es et mois."""
    mois_total = calculer_age_mois(date_naissance, date_reference)
    
    annees = mois_total // 12
    mois = mois_total % 12
    
    return {
        "annees": annees,
        "mois": mois,
        "mois_total": mois_total
    }


def formater_age(date_naissance: date, date_reference: Optional[date] = None) -> str:
    """Formate l'Ã¢ge de maniÃ¨re lisible."""
    age = calculer_age_annees_mois(date_naissance, date_reference)
    
    if age["annees"] == 0:
        return f"{age['mois']} mois"
    elif age["mois"] == 0:
        return f"{age['annees']} an" if age["annees"] == 1 else f"{age['annees']} ans"
    else:
        ans_txt = "an" if age["annees"] == 1 else "ans"
        return f"{age['annees']} {ans_txt} et {age['mois']} mois"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Ã‰TAPES DE DÃ‰VELOPPEMENT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def get_tranche_age(age_mois: int) -> str:
    """Retourne la tranche d'Ã¢ge."""
    if age_mois < 3:
        return "0-3"
    elif age_mois < 6:
        return "3-6"
    elif age_mois < 9:
        return "6-9"
    elif age_mois < 12:
        return "9-12"
    elif age_mois < 18:
        return "12-18"
    elif age_mois < 24:
        return "18-24"
    elif age_mois < 36:
        return "24-36"
    else:
        return "36+"


def get_etapes_attendues(age_mois: int) -> List[str]:
    """Retourne les Ã©tapes attendues pour l'Ã¢ge."""
    tranche = get_tranche_age(age_mois)
    return ETAPES_DEVELOPPEMENT.get(tranche, [])


def get_prochaines_etapes(age_mois: int) -> List[str]:
    """Retourne les prochaines Ã©tapes Ã  venir."""
    age_suivant = age_mois + 3  # 3 mois d'avance
    tranche = get_tranche_age(age_suivant)
    return ETAPES_DEVELOPPEMENT.get(tranche, [])


def calculer_progression_etapes(etapes_realisees: List[Dict[str, Any]], age_mois: int) -> Dict[str, Any]:
    """Calcule la progression dans les Ã©tapes."""
    etapes_attendues = get_etapes_attendues(age_mois)
    
    if not etapes_attendues:
        return {
            "total_attendu": 0,
            "total_realise": 0,
            "pourcentage": 0.0,
            "en_avance": 0
        }
    
    # Compter Ã©tapes rÃ©alisÃ©es de la tranche actuelle
    noms_attendus = set(etapes_attendues)
    noms_realises = {e.get("nom") for e in etapes_realisees}
    
    realise_tranche = len(noms_attendus.intersection(noms_realises))
    
    # Compter Ã©tapes en avance (tranches suivantes)
    en_avance = 0
    for etape in etapes_realisees:
        if etape.get("nom") not in noms_attendus:
            age_etape = etape.get("age_mois", age_mois)
            if age_etape > age_mois:
                en_avance += 1
    
    pourcentage = (realise_tranche / len(etapes_attendues) * 100) if etapes_attendues else 0
    
    return {
        "total_attendu": len(etapes_attendues),
        "total_realise": realise_tranche,
        "pourcentage": pourcentage,
        "en_avance": en_avance
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SUIVI CROISSANCE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def analyser_courbe_croissance(mesures: List[Dict[str, Any]], type_mesure: str = "poids") -> Dict[str, Any]:
    """Analyse une courbe de croissance (poids, taille)."""
    if not mesures:
        return {
            "tendance": "stable",
            "derniere_valeur": 0.0,
            "evolution": 0.0,
            "moyenne": 0.0
        }
    
    # Trier par date
    mesures_triees = sorted(mesures, key=lambda x: x.get("date", date.today()))
    
    valeurs = [m.get(type_mesure, 0.0) for m in mesures_triees]
    derniere = valeurs[-1] if valeurs else 0.0
    
    # Tendance (comparer derniÃ¨re et avant-derniÃ¨re)
    if len(valeurs) >= 2:
        diff = valeurs[-1] - valeurs[-2]
        if diff > 0.5:  # Seuil positif
            tendance = "hausse"
        elif diff < -0.5:  # Seuil nÃ©gatif
            tendance = "baisse"
        else:
            tendance = "stable"
        
        # Ã‰volution en %
        evolution = (diff / valeurs[-2] * 100) if valeurs[-2] > 0 else 0
    else:
        tendance = "stable"
        evolution = 0.0
    
    moyenne = sum(valeurs) / len(valeurs) if valeurs else 0.0
    
    return {
        "tendance": tendance,
        "derniere_valeur": derniere,
        "evolution": evolution,
        "moyenne": moyenne,
        "nombre_mesures": len(valeurs)
    }


def calculer_percentile_indicatif(valeur: float, age_mois: int, type_mesure: str = "poids") -> str:
    """Donne une indication de percentile (simplifiÃ©e)."""
    # DonnÃ©es indicatives moyennes (garÃ§on, approximatif)
    moyennes_poids = {
        0: 3.5, 3: 6.0, 6: 8.0, 9: 9.0, 12: 10.0,
        18: 11.5, 24: 12.5, 36: 15.0
    }
    
    moyennes_taille = {
        0: 50, 3: 61, 6: 68, 9: 72, 12: 76,
        18: 82, 24: 87, 36: 96
    }
    
    # Trouver rÃ©fÃ©rence la plus proche
    if type_mesure == "poids":
        ref = moyennes_poids
    else:
        ref = moyennes_taille
    
    ages_disponibles = sorted(ref.keys())
    age_ref = min(ages_disponibles, key=lambda x: abs(x - age_mois))
    valeur_ref = ref[age_ref]
    
    ratio = valeur / valeur_ref
    
    if ratio < 0.85:
        return "Sous la moyenne"
    elif ratio < 0.95:
        return "LÃ©gÃ¨rement sous la moyenne"
    elif ratio < 1.05:
        return "Dans la moyenne"
    elif ratio < 1.15:
        return "LÃ©gÃ¨rement au-dessus"
    else:
        return "Au-dessus de la moyenne"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# ANALYSE SANTÃ‰ ET BIEN-ÃŠTRE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def analyser_sommeil(entrees: List[Dict[str, Any]], jours: int = 7) -> Dict[str, Any]:
    """Analyse le sommeil de l'enfant."""
    date_limite = date.today() - timedelta(days=jours)
    
    heures_par_jour = []
    for entree in entrees:
        date_entree = entree.get("date")
        if isinstance(date_entree, str):
            from datetime import datetime
            date_entree = datetime.fromisoformat(date_entree).date()
        
        if date_entree >= date_limite:
            heures = entree.get("heures_sommeil", 0)
            if heures:
                heures_par_jour.append(heures)
    
    if not heures_par_jour:
        return {
            "moyenne": 0.0,
            "qualite": "Inconnu",
            "recommandation": ""
        }
    
    moyenne = sum(heures_par_jour) / len(heures_par_jour)
    
    # Recommandations par Ã¢ge (pour un jeune enfant)
    if moyenne >= 12:
        qualite = "Excellent"
        recommandation = "Sommeil suffisant pour le dÃ©veloppement"
    elif moyenne >= 10:
        qualite = "Bon"
        recommandation = "Sommeil adÃ©quat"
    elif moyenne >= 8:
        qualite = "Moyen"
        recommandation = "Augmenter lÃ©gÃ¨rement le temps de sommeil"
    else:
        qualite = "Insuffisant"
        recommandation = "Consulter pour amÃ©liorer le sommeil"
    
    return {
        "moyenne": moyenne,
        "qualite": qualite,
        "recommandation": recommandation
    }


def analyser_humeurs(entrees: List[Dict[str, Any]], jours: int = 7) -> Dict[str, Any]:
    """Analyse les humeurs de l'enfant."""
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
    
    humeur_dominante = None
    if compteur:
        humeur_dominante = max(compteur.items(), key=lambda x: x[1])[0]
    
    return {
        "distribution": compteur,
        "humeur_dominante": humeur_dominante,
        "total_entrees": sum(compteur.values())
    }


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# VALIDATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def valider_mesure(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Valide une mesure de croissance."""
    erreurs = []
    
    if "date" not in data or not data["date"]:
        erreurs.append("La date est requise")
    
    if "poids" in data:
        poids = data["poids"]
        if not isinstance(poids, (int, float)) or poids <= 0 or poids > 50:
            erreurs.append("Poids invalide (doit Ãªtre entre 0 et 50 kg)")
    
    if "taille" in data:
        taille = data["taille"]
        if not isinstance(taille, (int, float)) or taille <= 0 or taille > 150:
            erreurs.append("Taille invalide (doit Ãªtre entre 0 et 150 cm)")
    
    return len(erreurs) == 0, erreurs


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FORMATAGE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

def formater_milestone(milestone: Dict[str, Any]) -> str:
    """Formate un milestone."""
    nom = milestone.get("nom", "Ã‰tape")
    categorie = milestone.get("categorie", "")
    
    if categorie:
        return f"{nom} ({categorie})"
    return nom


def grouper_milestones_par_categorie(milestones: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Groupe les milestones par catÃ©gorie."""
    groupes = {cat: [] for cat in CATEGORIES_MILESTONES}
    
    for ms in milestones:
        cat = ms.get("categorie", "Autre")
        if cat not in groupes:
            groupes[cat] = []
        groupes[cat].append(ms)
    
    return groupes

