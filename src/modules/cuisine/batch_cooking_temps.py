"""
Constantes, calcul de temps et validation du Batch Cooking

Logique pure pour les constantes, calculs de durees et validation.
"""

import logging
from datetime import date, datetime, time, timedelta

from src.core.date_utils import formater_temps

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

JOURS_EMOJI = {
    0: "🟡",  # Lundi
    1: "🟠",  # Mardi
    2: "🐟£",  # Mercredi
    3: "🟢",  # Jeudi
    4: "âš«",  # Vendredi
    5: "🔴",  # Samedi
    6: "🟢",  # Dimanche
}

ROBOTS_INFO = {
    "cookeo": {
        "nom": "Cookeo",
        "emoji": "🍲",
        "peut_parallele": True,
        "description": "Cuiseur multi-fonction",
    },
    "monsieur_cuisine": {
        "nom": "Monsieur Cuisine",
        "emoji": "🤖",
        "peut_parallele": True,
        "description": "Robot cuiseur",
    },
    "airfryer": {
        "nom": "Airfryer",
        "emoji": "🍟",
        "peut_parallele": True,
        "description": "Friteuse sans huile",
    },
    "multicooker": {
        "nom": "Multicooker",
        "emoji": "♨️",
        "peut_parallele": True,
        "description": "Cuiseur polyvalent",
    },
    "four": {
        "nom": "Four",
        "emoji": "🔥",
        "peut_parallele": True,
        "description": "Four traditionnel",
    },
    "plaques": {
        "nom": "Plaques",
        "emoji": "🍳",
        "peut_parallele": False,
        "description": "Plaques de cuisson",
    },
    "robot_patissier": {
        "nom": "Robot Pâtissier",
        "emoji": "🎂",
        "peut_parallele": True,
        "description": "Pour pâtisserie",
    },
    "mixeur": {
        "nom": "Mixeur",
        "emoji": "🥤",
        "peut_parallele": False,
        "description": "Mixeur/blender",
    },
    "hachoir": {
        "nom": "Hachoir",
        "emoji": "🔪",
        "peut_parallele": False,
        "description": "Hachoir electrique",
    },
}

LOCALISATIONS = {
    "frigo": {"nom": "Refrigerateur", "emoji": "🧊", "conservation_max_jours": 5},
    "congelateur": {"nom": "Congelateur", "emoji": "❄️", "conservation_max_jours": 90},
    "temperature_ambiante": {
        "nom": "Temperature ambiante",
        "emoji": "🏠",
        "conservation_max_jours": 2,
    },
}


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE CALCUL DE TEMPS
# ═══════════════════════════════════════════════════════════


def calculer_duree_totale_optimisee(etapes: list[dict]) -> int:
    """
    Calcule la duree totale optimisee en tenant compte de la parallelisation.

    Args:
        etapes: Liste des etapes avec leurs groupes parallèles et durees

    Returns:
        Duree totale estimee en minutes
    """
    if not etapes:
        return 0

    # Grouper par groupe_parallele
    groupes: dict[int, list[dict]] = {}
    for etape in etapes:
        groupe = etape.get("groupe_parallele", 0)
        if groupe not in groupes:
            groupes[groupe] = []
        groupes[groupe].append(etape)

    # Pour chaque groupe, prendre la duree max (car parallèle)
    duree_totale = 0
    for groupe_id in sorted(groupes.keys()):
        etapes_groupe = groupes[groupe_id]
        duree_max_groupe = max(e.get("duree_minutes", 0) for e in etapes_groupe)
        duree_totale += duree_max_groupe

    return duree_totale


def estimer_heure_fin(heure_debut: time, duree_minutes: int) -> time:
    """
    Estime l'heure de fin à partir de l'heure de debut et de la duree.

    Args:
        heure_debut: Heure de debut
        duree_minutes: Duree en minutes

    Returns:
        Heure de fin estimee
    """
    debut_dt = datetime.combine(date.today(), heure_debut)
    fin_dt = debut_dt + timedelta(minutes=duree_minutes)
    return fin_dt.time()


def formater_duree(minutes: int) -> str:
    """Formate une duree en minutes (alias pour formater_temps avec espace)."""
    return formater_temps(minutes, avec_espace=True)


# ═══════════════════════════════════════════════════════════
# FONCTIONS DE VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_session_batch(
    date_session: date,
    recettes_ids: list[int],
    robots: list[str],
) -> dict:
    """
    Valide les donnees d'une session batch cooking.

    Args:
        date_session: Date de la session
        recettes_ids: Liste des IDs de recettes
        robots: Liste des robots disponibles

    Returns:
        Dict avec "valide" (bool) et "erreurs" (list)
    """
    erreurs = []

    # Verifier la date
    if date_session < date.today():
        erreurs.append("La date de session ne peut pas être dans le passé")

    # Verifier les recettes
    if not recettes_ids:
        erreurs.append("Au moins une recette doit être sélectionnée")
    elif len(recettes_ids) > 10:
        erreurs.append("Maximum 10 recettes par session")

    # Verifier les robots
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
) -> dict:
    """
    Valide les donnees d'une preparation.

    Args:
        nom: Nom de la preparation
        portions: Nombre de portions
        conservation_jours: Duree de conservation
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
