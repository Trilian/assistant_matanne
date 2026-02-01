"""
Logique métier du module Batch Cooking - Séparée de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

from datetime import date, datetime, time, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
JOURS_EMOJI = {
    0: "🟡",  # Lundi
    1: "🟠",  # Mardi
    2: "🟣",  # Mercredi
    3: "🟢",  # Jeudi
    4: "⚫",  # Vendredi
    5: "🔴",  # Samedi
    6: "🟢",  # Dimanche
}

ROBOTS_INFO = {
    "cookeo": {"nom": "Cookeo", "emoji": "🍲", "peut_parallele": True, "description": "Cuiseur multi-fonction"},
    "monsieur_cuisine": {"nom": "Monsieur Cuisine", "emoji": "🤖", "peut_parallele": True, "description": "Robot cuiseur"},
    "airfryer": {"nom": "Airfryer", "emoji": "🍟", "peut_parallele": True, "description": "Friteuse sans huile"},
    "multicooker": {"nom": "Multicooker", "emoji": "♨️", "peut_parallele": True, "description": "Cuiseur polyvalent"},
    "four": {"nom": "Four", "emoji": "🔥", "peut_parallele": True, "description": "Four traditionnel"},
    "plaques": {"nom": "Plaques", "emoji": "🍳", "peut_parallele": False, "description": "Plaques de cuisson"},
    "robot_patissier": {"nom": "Robot Pâtissier", "emoji": "🎂", "peut_parallele": True, "description": "Pour pâtisserie"},
    "mixeur": {"nom": "Mixeur", "emoji": "🥤", "peut_parallele": False, "description": "Mixeur/blender"},
    "hachoir": {"nom": "Hachoir", "emoji": "🔪", "peut_parallele": False, "description": "Hachoir électrique"},
}

LOCALISATIONS = {
    "frigo": {"nom": "Réfrigérateur", "emoji": "🧊", "conservation_max_jours": 5},
    "congelateur": {"nom": "Congélateur", "emoji": "❄️", "conservation_max_jours": 90},
    "temperature_ambiante": {"nom": "Température ambiante", "emoji": "🏠", "conservation_max_jours": 2},
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE CALCUL DE TEMPS
# ═══════════════════════════════════════════════════════════

def calculer_duree_totale_optimisee(etapes: List[Dict[str, Any]]) -> int:
    """
    Calcule la durée totale optimisée en tenant compte de la parallélisation.
    
    Args:
        etapes: Liste des étapes avec leurs groupes parallèles et durées
        
    Returns:
        Durée totale estimée en minutes
    """
    if not etapes:
        return 0
    
    # Grouper par groupe_parallele
    groupes: Dict[int, List[Dict]] = {}
    for etape in etapes:
        groupe = etape.get("groupe_parallele", 0)
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append(etape)
    
    # Pour chaque groupe, prendre la durée max (car parallèle)
    duree_totale = 0
    for groupe_id in sorted(groupes.keys()):
        etapes_groupe = groupes[groupe_id]
        duree_max_groupe = max(e.get("duree_minutes", 0) for e in etapes_groupe)
        duree_totale += duree_max_groupe
    
    return duree_totale


def estimer_heure_fin(heure_debut: time, duree_minutes: int) -> time:
    """
    Estime l'heure de fin à partir de l'heure de début et de la durée.
    
    Args:
        heure_debut: Heure de début
        duree_minutes: Durée en minutes
        
    Returns:
        Heure de fin estimée
    """
    debut_dt = datetime.combine(date.today(), heure_debut)
    fin_dt = debut_dt + timedelta(minutes=duree_minutes)
    return fin_dt.time()


def formater_duree(minutes: int) -> str:
    """
    Formate une durée en minutes en texte lisible.
    
    Args:
        minutes: Durée en minutes
        
    Returns:
        Texte formaté (ex: "2h30" ou "45 min")
    """
    if minutes < 60:
        return f"{minutes} min"
    heures = minutes // 60
    mins_restantes = minutes % 60
    if mins_restantes == 0:
        return f"{heures}h"
    return f"{heures}h{mins_restantes:02d}"


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE VALIDATION
# ═══════════════════════════════════════════════════════════

def valider_session_batch(
    date_session: date,
    recettes_ids: List[int],
    robots: List[str],
) -> Dict[str, Any]:
    """
    Valide les données d'une session batch cooking.
    
    Args:
        date_session: Date de la session
        recettes_ids: Liste des IDs de recettes
        robots: Liste des robots disponibles
        
    Returns:
        Dict avec "valide" (bool) et "erreurs" (list)
    """
    erreurs = []
    
    # Vérifier la date
    if date_session < date.today():
        erreurs.append("La date de session ne peut pas être dans le passé")
    
    # Vérifier les recettes
    if not recettes_ids:
        erreurs.append("Au moins une recette doit être sélectionnée")
    elif len(recettes_ids) > 10:
        erreurs.append("Maximum 10 recettes par session")
    
    # Vérifier les robots
    robots_valides = set(ROBOTS_INFO.keys())
    robots_inconnus = set(robots) - robots_valides
    if robots_inconnus:
        erreurs.append(f"Robots inconnus: {', '.join(robots_inconnus)}")
    
    return {
        "valide": len(erreurs) == 0,
        "erreurs": erreurs,
    }


def valider_preparation(
    nom: str,
    portions: int,
    conservation_jours: int,
    localisation: str,
) -> Dict[str, Any]:
    """
    Valide les données d'une préparation.
    
    Args:
        nom: Nom de la préparation
        portions: Nombre de portions
        conservation_jours: Durée de conservation
        localisation: Lieu de stockage
        
    Returns:
        Dict avec "valide" (bool) et "erreurs" (list)
    """
    erreurs = []
    
    if not nom or len(nom) < 3:
        erreurs.append("Le nom doit faire au moins 3 caractères")
    
    if portions < 1 or portions > 20:
        erreurs.append("Le nombre de portions doit être entre 1 et 20")
    
    if localisation not in LOCALISATIONS:
        erreurs.append(f"Localisation invalide: {localisation}")
    else:
        max_jours = LOCALISATIONS[localisation]["conservation_max_jours"]
        if conservation_jours > max_jours:
            erreurs.append(f"Conservation max pour {localisation}: {max_jours} jours")
    
    return {
        "valide": len(erreurs) == 0,
        "erreurs": erreurs,
    }


# ═══════════════════════════════════════════════════════════
# FONCTIONS D'OPTIMISATION
# ═══════════════════════════════════════════════════════════

def optimiser_ordre_etapes(etapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Optimise l'ordre des étapes pour minimiser le temps total.
    
    Stratégie:
    1. Démarrer par les cuissons longues (supervision)
    2. Paralléliser les tâches manuelles pendant les supervisions
    3. Regrouper les utilisations d'un même robot
    
    Args:
        etapes: Liste des étapes non ordonnées
        
    Returns:
        Liste des étapes réordonnées avec groupes parallèles assignés
    """
    if not etapes:
        return []
    
    # Séparer supervision vs actif
    etapes_supervision = [e for e in etapes if e.get("est_supervision", False)]
    etapes_actives = [e for e in etapes if not e.get("est_supervision", False)]
    
    # Trier supervisions par durée décroissante (lancer les plus longues d'abord)
    etapes_supervision.sort(key=lambda e: e.get("duree_minutes", 0), reverse=True)
    
    # Trier actives par robot puis par durée
    etapes_actives.sort(key=lambda e: (
        ",".join(e.get("robots", [])),
        e.get("duree_minutes", 0)
    ))
    
    # Assigner les groupes parallèles
    resultat = []
    groupe_actuel = 0
    
    # Alterner: supervision longue -> tâches actives pendant ce temps
    for supervision in etapes_supervision:
        supervision["groupe_parallele"] = groupe_actuel
        supervision["ordre"] = len(resultat) + 1
        resultat.append(supervision)
        
        # Ajouter des tâches actives en parallèle si possible
        temps_dispo = supervision.get("duree_minutes", 0)
        temps_utilise = 0
        
        i = 0
        while i < len(etapes_actives) and temps_utilise < temps_dispo:
            etape = etapes_actives[i]
            duree = etape.get("duree_minutes", 0)
            
            # Vérifier qu'on peut faire cette tâche en parallèle
            robots_etape = set(etape.get("robots", []))
            robots_supervision = set(supervision.get("robots", []))
            
            # Si pas de conflit de robot, on peut paralléliser
            if not robots_etape.intersection(robots_supervision):
                if temps_utilise + duree <= temps_dispo:
                    etape["groupe_parallele"] = groupe_actuel
                    etape["ordre"] = len(resultat) + 1
                    resultat.append(etape)
                    etapes_actives.pop(i)
                    temps_utilise += duree
                    continue
            i += 1
        
        groupe_actuel += 1
    
    # Ajouter les étapes actives restantes
    for etape in etapes_actives:
        etape["groupe_parallele"] = groupe_actuel
        etape["ordre"] = len(resultat) + 1
        resultat.append(etape)
        groupe_actuel += 1
    
    return resultat


def detecter_conflits_robots(etapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Détecte les conflits d'utilisation de robots dans les étapes parallèles.
    
    Args:
        etapes: Liste des étapes avec groupes parallèles
        
    Returns:
        Liste des conflits détectés
    """
    conflits = []
    
    # Grouper par groupe_parallele
    groupes: Dict[int, List[Dict]] = {}
    for etape in etapes:
        groupe = etape.get("groupe_parallele", 0)
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append(etape)
    
    # Vérifier chaque groupe
    for groupe_id, etapes_groupe in groupes.items():
        if len(etapes_groupe) < 2:
            continue
            
        robots_utilises: Dict[str, List[str]] = {}
        
        for etape in etapes_groupe:
            for robot in etape.get("robots", []):
                if robot not in robots_utilises:
                    robots_utilises[robot] = []
                robots_utilises[robot].append(etape.get("titre", "?"))
        
        # Détecter les doublons
        for robot, etapes_robot in robots_utilises.items():
            if len(etapes_robot) > 1:
                # Vérifier si le robot peut être parallélisé
                robot_info = ROBOTS_INFO.get(robot, {})
                if not robot_info.get("peut_parallele", True):
                    conflits.append({
                        "groupe": groupe_id,
                        "robot": robot,
                        "etapes": etapes_robot,
                        "message": f"Le {robot_info.get('nom', robot)} ne peut pas être utilisé en parallèle",
                    })
    
    return conflits


# ═══════════════════════════════════════════════════════════
# FONCTIONS POUR MODE JULES
# ═══════════════════════════════════════════════════════════

def filtrer_etapes_bruyantes(etapes: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """
    Sépare les étapes bruyantes des étapes calmes.
    
    Args:
        etapes: Liste des étapes
        
    Returns:
        Dict avec "bruyantes" et "calmes"
    """
    bruyantes = [e for e in etapes if e.get("alerte_bruit", False)]
    calmes = [e for e in etapes if not e.get("alerte_bruit", False)]
    
    return {
        "bruyantes": bruyantes,
        "calmes": calmes,
    }


def identifier_moments_jules(etapes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Identifie les moments où Jules peut participer/observer.
    
    Critères:
    - Pas de manipulation dangereuse
    - Pas trop bruyant
    - Activité visuelle intéressante
    
    Args:
        etapes: Liste des étapes
        
    Returns:
        Liste des moments adaptés à Jules
    """
    moments_jules = []
    
    activites_securisees = [
        "mélanger", "verser", "décorer", "observer", "toucher",
        "sentir", "goûter", "ranger", "nettoyer"
    ]
    
    for etape in etapes:
        titre = etape.get("titre", "").lower()
        description = etape.get("description", "").lower()
        
        # Vérifier si activité sécurisée
        est_securise = any(act in titre or act in description for act in activites_securisees)
        
        # Vérifier si pas bruyant
        est_calme = not etape.get("alerte_bruit", False)
        
        # Vérifier si pas de température dangereuse
        temp = etape.get("temperature")
        est_froid = temp is None or temp < 50
        
        if est_securise and est_calme and est_froid:
            moments_jules.append({
                **etape,
                "conseil_jules": "✅ Jules peut participer en mélangeant/observant",
            })
        elif etape.get("est_supervision", False) and est_calme:
            moments_jules.append({
                **etape,
                "conseil_jules": "👀 Jules peut observer depuis sa chaise haute",
            })
    
    return moments_jules


def generer_planning_jules(
    etapes: List[Dict[str, Any]],
    heure_debut: time,
    heure_sieste_debut: time = time(13, 0),
    heure_sieste_fin: time = time(15, 0),
) -> Dict[str, Any]:
    """
    Génère un planning adapté aux horaires de Jules.
    
    Args:
        etapes: Liste des étapes
        heure_debut: Heure de début de la session
        heure_sieste_debut: Heure de début de la sieste
        heure_sieste_fin: Heure de fin de la sieste
        
    Returns:
        Planning avec conseils pour Jules
    """
    etapes_bruyantes = filtrer_etapes_bruyantes(etapes)
    
    # Calculer les horaires
    heure_actuelle = datetime.combine(date.today(), heure_debut)
    sieste_debut_dt = datetime.combine(date.today(), heure_sieste_debut)
    sieste_fin_dt = datetime.combine(date.today(), heure_sieste_fin)
    
    planning = {
        "avant_sieste": [],
        "pendant_sieste": [],
        "apres_sieste": [],
        "conseils": [],
    }
    
    for etape in etapes:
        duree = timedelta(minutes=etape.get("duree_minutes", 10))
        heure_fin_etape = heure_actuelle + duree
        
        if heure_fin_etape <= sieste_debut_dt:
            planning["avant_sieste"].append(etape)
        elif heure_actuelle >= sieste_fin_dt:
            planning["apres_sieste"].append(etape)
        else:
            planning["pendant_sieste"].append(etape)
        
        heure_actuelle = heure_fin_etape
    
    # Conseils
    if etapes_bruyantes["bruyantes"]:
        nb_bruyantes_sieste = sum(
            1 for e in planning["pendant_sieste"] 
            if e.get("alerte_bruit", False)
        )
        if nb_bruyantes_sieste > 0:
            planning["conseils"].append(
                f"⚠️ {nb_bruyantes_sieste} étape(s) bruyante(s) pendant la sieste - "
                "Réorganiser si possible"
            )
    
    return planning


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE STATISTIQUES
# ═══════════════════════════════════════════════════════════

def calculer_statistiques_session(session_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcule les statistiques d'une session batch cooking.
    
    Args:
        session_data: Données de la session
        
    Returns:
        Dict de statistiques
    """
    etapes = session_data.get("etapes", [])
    preparations = session_data.get("preparations", [])
    
    # Stats étapes
    nb_etapes = len(etapes)
    etapes_terminees = sum(1 for e in etapes if e.get("statut") == "terminee")
    duree_estimee = sum(e.get("duree_minutes", 0) for e in etapes)
    duree_optimisee = calculer_duree_totale_optimisee(etapes)
    
    # Stats préparations
    nb_preparations = len(preparations)
    portions_totales = sum(p.get("portions_initiales", 0) for p in preparations)
    
    # Stats robots
    robots_utilises = set()
    for etape in etapes:
        robots_utilises.update(etape.get("robots", []))
    
    return {
        "nb_etapes": nb_etapes,
        "etapes_terminees": etapes_terminees,
        "progression_pct": (etapes_terminees / nb_etapes * 100) if nb_etapes > 0 else 0,
        "duree_estimee_brute": duree_estimee,
        "duree_estimee_optimisee": duree_optimisee,
        "gain_temps_pct": ((duree_estimee - duree_optimisee) / duree_estimee * 100) if duree_estimee > 0 else 0,
        "nb_preparations": nb_preparations,
        "portions_totales": portions_totales,
        "robots_utilises": list(robots_utilises),
        "nb_robots": len(robots_utilises),
    }


def calculer_historique_batch(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calcule les statistiques sur l'historique des sessions.
    
    Args:
        sessions: Liste des sessions passées
        
    Returns:
        Dict de statistiques historiques
    """
    if not sessions:
        return {
            "nb_sessions": 0,
            "temps_moyen_session": 0,
            "portions_moyennes": 0,
            "robot_prefere": None,
        }
    
    # Calculs
    nb_sessions = len(sessions)
    temps_total = sum(s.get("duree_reelle", 0) or s.get("duree_estimee", 0) for s in sessions)
    portions_total = sum(s.get("nb_portions_preparees", 0) for s in sessions)
    
    # Robot le plus utilisé
    compteur_robots: Dict[str, int] = {}
    for session in sessions:
        for robot in session.get("robots_utilises", []):
            compteur_robots[robot] = compteur_robots.get(robot, 0) + 1
    
    robot_prefere = max(compteur_robots.items(), key=lambda x: x[1])[0] if compteur_robots else None
    
    return {
        "nb_sessions": nb_sessions,
        "temps_moyen_session": temps_total / nb_sessions if nb_sessions > 0 else 0,
        "portions_moyennes": portions_total / nb_sessions if nb_sessions > 0 else 0,
        "robot_prefere": robot_prefere,
        "robots_compteur": compteur_robots,
    }
