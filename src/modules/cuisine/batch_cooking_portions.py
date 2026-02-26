"""
Mode Jules et statistiques du Batch Cooking

Logique pure pour la gestion du mode Jules (bebe) et les statistiques de sessions.
"""

import logging
from datetime import date, datetime, time, timedelta

from .batch_cooking_temps import calculer_duree_totale_optimisee

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# FONCTIONS POUR MODE JULES
# ═══════════════════════════════════════════════════════════


def filtrer_etapes_bruyantes(etapes: list[dict]) -> dict[str, list[dict]]:
    """
    Separe les etapes bruyantes des etapes calmes.

    Args:
        etapes: Liste des etapes

    Returns:
        Dict avec "bruyantes" et "calmes"
    """
    bruyantes = [e for e in etapes if e.get("alerte_bruit", False)]
    calmes = [e for e in etapes if not e.get("alerte_bruit", False)]

    return {
        "bruyantes": bruyantes,
        "calmes": calmes,
    }


def identifier_moments_jules(etapes: list[dict]) -> list[dict]:
    """
    Identifie les moments où Jules peut participer/observer.

    Critères:
    - Pas de manipulation dangereuse
    - Pas trop bruyant
    - Activite visuelle interessante

    Args:
        etapes: Liste des etapes

    Returns:
        Liste des moments adaptes à Jules
    """
    moments_jules = []

    activites_securisees = [
        "melanger",
        "verser",
        "decorer",
        "observer",
        "toucher",
        "sentir",
        "goûter",
        "ranger",
        "nettoyer",
    ]

    for etape in etapes:
        titre = etape.get("titre", "").lower()
        description = etape.get("description", "").lower()

        # Verifier si activite securisee
        est_securise = any(act in titre or act in description for act in activites_securisees)

        # Verifier si pas bruyant
        est_calme = not etape.get("alerte_bruit", False)

        # Verifier si pas de temperature dangereuse
        temp = etape.get("temperature")
        est_froid = temp is None or temp < 50

        if est_securise and est_calme and est_froid:
            moments_jules.append(
                {
                    **etape,
                    "conseil_jules": "✅ Jules peut participer en melangeant/observant",
                }
            )
        elif etape.get("est_supervision", False) and est_calme:
            moments_jules.append(
                {
                    **etape,
                    "conseil_jules": "👀 Jules peut observer depuis sa chaise haute",
                }
            )

    return moments_jules


def generer_planning_jules(
    etapes: list[dict],
    heure_debut: time,
    heure_sieste_debut: time = time(13, 0),
    heure_sieste_fin: time = time(15, 0),
) -> dict:
    """
    Genère un planning adapte aux horaires de Jules.

    Args:
        etapes: Liste des etapes
        heure_debut: Heure de debut de la session
        heure_sieste_debut: Heure de debut de la sieste
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
            1 for e in planning["pendant_sieste"] if e.get("alerte_bruit", False)
        )
        if nb_bruyantes_sieste > 0:
            planning["conseils"].append(
                f"⚠️ {nb_bruyantes_sieste} etape(s) bruyante(s) pendant la sieste - "
                "Reorganiser si possible"
            )

    return planning


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_statistiques_session(session_data: dict) -> dict:
    """
    Calcule les statistiques d'une session batch cooking.

    Args:
        session_data: Donnees de la session

    Returns:
        Dict de statistiques
    """
    etapes = session_data.get("etapes", [])
    preparations = session_data.get("preparations", [])

    # Stats etapes
    nb_etapes = len(etapes)
    etapes_terminees = sum(1 for e in etapes if e.get("statut") == "terminee")
    duree_estimee = sum(e.get("duree_minutes", 0) for e in etapes)
    duree_optimisee = calculer_duree_totale_optimisee(etapes)

    # Stats preparations
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
        "gain_temps_pct": ((duree_estimee - duree_optimisee) / duree_estimee * 100)
        if duree_estimee > 0
        else 0,
        "nb_preparations": nb_preparations,
        "portions_totales": portions_totales,
        "robots_utilises": list(robots_utilises),
        "nb_robots": len(robots_utilises),
    }


def calculer_historique_batch(sessions: list[dict]) -> dict:
    """
    Calcule les statistiques sur l'historique des sessions.

    Args:
        sessions: Liste des sessions passees

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

    # Robot le plus utilise
    compteur_robots: dict[str, int] = {}
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
