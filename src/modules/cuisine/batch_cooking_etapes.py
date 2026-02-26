"""
Optimisation et ordonnancement des etapes du Batch Cooking

Logique pure pour l'optimisation de l'ordre des etapes et detection de conflits.
"""

import logging

from .batch_cooking_temps import ROBOTS_INFO

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# FONCTIONS D'OPTIMISATION
# ═══════════════════════════════════════════════════════════


def optimiser_ordre_etapes(etapes: list[dict]) -> list[dict]:
    """
    Optimise l'ordre des etapes pour minimiser le temps total.

    Strategie:
    1. Demarrer par les cuissons longues (supervision)
    2. Paralleliser les tâches manuelles pendant les supervisions
    3. Regrouper les utilisations d'un même robot

    Args:
        etapes: Liste des etapes non ordonnees

    Returns:
        Liste des etapes reordonnees avec groupes parallèles assignes
    """
    if not etapes:
        return []

    # Separer supervision vs actif
    etapes_supervision = [e for e in etapes if e.get("est_supervision", False)]
    etapes_actives = [e for e in etapes if not e.get("est_supervision", False)]

    # Trier supervisions par duree decroissante (lancer les plus longues d'abord)
    etapes_supervision.sort(key=lambda e: e.get("duree_minutes", 0), reverse=True)

    # Trier actives par robot puis par duree
    etapes_actives.sort(key=lambda e: (",".join(e.get("robots", [])), e.get("duree_minutes", 0)))

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

            # Verifier qu'on peut faire cette tâche en parallèle
            robots_etape = set(etape.get("robots", []))
            robots_supervision = set(supervision.get("robots", []))

            # Si pas de conflit de robot, on peut paralleliser
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

    # Ajouter les etapes actives restantes
    for etape in etapes_actives:
        etape["groupe_parallele"] = groupe_actuel
        etape["ordre"] = len(resultat) + 1
        resultat.append(etape)
        groupe_actuel += 1

    return resultat


def detecter_conflits_robots(etapes: list[dict]) -> list[dict]:
    """
    Detecte les conflits d'utilisation de robots dans les etapes parallèles.

    Args:
        etapes: Liste des etapes avec groupes parallèles

    Returns:
        Liste des conflits detectes
    """
    conflits = []

    # Grouper par groupe_parallele
    groupes: dict[int, list[dict]] = {}
    for etape in etapes:
        groupe = etape.get("groupe_parallele", 0)
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append(etape)

    # Verifier chaque groupe
    for groupe_id, etapes_groupe in groupes.items():
        if len(etapes_groupe) < 2:
            continue

        robots_utilises: dict[str, list[str]] = {}

        for etape in etapes_groupe:
            for robot in etape.get("robots", []):
                if robot not in robots_utilises:
                    robots_utilises[robot] = []
                robots_utilises[robot].append(etape.get("titre", "?"))

        # Detecter les doublons
        for robot, etapes_robot in robots_utilises.items():
            if len(etapes_robot) > 1:
                # Verifier si le robot peut être parallelise
                robot_info = ROBOTS_INFO.get(robot, {})
                if not robot_info.get("peut_parallele", True):
                    conflits.append(
                        {
                            "groupe": groupe_id,
                            "robot": robot,
                            "etapes": etapes_robot,
                            "message": f"Le {robot_info.get('nom', robot)} ne peut pas être utilise en parallèle",
                        }
                    )

    return conflits
