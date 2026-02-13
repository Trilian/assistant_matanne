"""
Logique metier du module Activites (famille) - Separee de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

import logging
from datetime import date, timedelta
from typing import Any

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TYPES_ACTIVITE = ["Sport", "Culture", "Sortie", "Atelier", "Rendez-vous", "Jeu", "Autre"]
LIEUX = ["Maison", "Parc", "Centre culturel", "École", "Bibliothèque", "Piscine", "Autre"]
CATEGORIES_AGE = ["0-1 an", "1-2 ans", "2-3 ans", "3-5 ans", "5+ ans", "Famille"]


# ═══════════════════════════════════════════════════════════
# FILTRAGE ET TRI
# ═══════════════════════════════════════════════════════════


def filtrer_par_type(activites: list[dict[str, Any]], type_act: str) -> list[dict[str, Any]]:
    """Filtre les activites par type."""
    return [a for a in activites if a.get("type") == type_act]


def filtrer_par_lieu(activites: list[dict[str, Any]], lieu: str) -> list[dict[str, Any]]:
    """Filtre les activites par lieu."""
    return [a for a in activites if a.get("lieu") == lieu]


def filtrer_par_date(
    activites: list[dict[str, Any]], date_debut: date, date_fin: date
) -> list[dict[str, Any]]:
    """Filtre les activites par periode."""
    resultats = []

    for act in activites:
        date_act = act.get("date")
        if isinstance(date_act, str):
            from datetime import datetime

            date_act = datetime.fromisoformat(date_act).date()

        if date_debut <= date_act <= date_fin:
            resultats.append(act)

    return resultats


def get_activites_a_venir(activites: list[dict[str, Any]], jours: int = 7) -> list[dict[str, Any]]:
    """Retourne les activites à venir dans X jours."""
    date_fin = date.today() + timedelta(days=jours)
    return filtrer_par_date(activites, date.today(), date_fin)


def get_activites_passees(activites: list[dict[str, Any]], jours: int = 30) -> list[dict[str, Any]]:
    """Retourne les activites passees des X derniers jours."""
    date_debut = date.today() - timedelta(days=jours)
    return filtrer_par_date(activites, date_debut, date.today())


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_statistiques_activites(activites: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcule les statistiques des activites."""
    total = len(activites)

    if total == 0:
        return {"total": 0, "par_type": {}, "par_lieu": {}, "cout_total": 0.0, "duree_moyenne": 0.0}

    # Par type
    par_type = {}
    for act in activites:
        type_act = act.get("type", "Autre")
        par_type[type_act] = par_type.get(type_act, 0) + 1

    # Par lieu
    par_lieu = {}
    for act in activites:
        lieu = act.get("lieu", "Autre")
        par_lieu[lieu] = par_lieu.get(lieu, 0) + 1

    # Coûts et duree
    cout_total = sum(act.get("cout", 0.0) for act in activites)
    durees = [act.get("duree", 0) for act in activites if act.get("duree")]
    duree_moyenne = sum(durees) / len(durees) if durees else 0.0

    return {
        "total": total,
        "par_type": par_type,
        "par_lieu": par_lieu,
        "cout_total": cout_total,
        "cout_moyen": cout_total / total,
        "duree_moyenne": duree_moyenne,
    }


def calculer_frequence_hebdomadaire(activites: list[dict[str, Any]], semaines: int = 4) -> float:
    """Calcule la frequence hebdomadaire moyenne d'activites."""
    if not activites or semaines == 0:
        return 0.0

    return len(activites) / semaines


# ═══════════════════════════════════════════════════════════
# RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════


def suggerer_activites_age(age_mois: int) -> list[dict[str, str]]:
    """Suggère des activités adaptées à l'âge."""
    suggestions = []

    if age_mois < 12:
        suggestions = [
            {"type": "Jeu", "titre": "Jeux d'éveil", "description": "Hochets, tapis d'éveil"},
            {
                "type": "Sport",
                "titre": "Motricité libre",
                "description": "Temps au sol pour ramper",
            },
            {"type": "Culture", "titre": "Comptines", "description": "Chansons et comptines"},
        ]
    elif age_mois < 24:
        suggestions = [
            {"type": "Jeu", "titre": "Jeux de manipulation", "description": "Empiler, encastrer"},
            {"type": "Sport", "titre": "Marche", "description": "Promenades, parc"},
            {"type": "Culture", "titre": "Histoires", "description": "Livres images"},
        ]
    elif age_mois < 36:
        suggestions = [
            {"type": "Jeu", "titre": "Jeux symboliques", "description": "Poupées, voitures"},
            {"type": "Sport", "titre": "Parcours moteur", "description": "Escalade, vélo"},
            {"type": "Culture", "titre": "Musique", "description": "Instruments simples"},
        ]
    else:
        suggestions = [
            {
                "type": "Atelier",
                "titre": "Activités créatives",
                "description": "Peinture, pâte à modeler",
            },
            {"type": "Sport", "titre": "Sport collectif", "description": "Football, natation"},
            {
                "type": "Culture",
                "titre": "Sorties culturelles",
                "description": "Musées, spectacles",
            },
        ]

    return suggestions


def detecter_desequilibre_types(activites: list[dict[str, Any]]) -> dict[str, Any]:
    """Detecte les desequilibres dans les types d'activites."""
    stats = calculer_statistiques_activites(activites)
    par_type = stats.get("par_type", {})

    if not par_type:
        return {"equilibre": True, "recommandations": []}

    total = stats["total"]
    recommandations = []

    # Verifier si un type est sous-represente (< 15%)
    for type_act in TYPES_ACTIVITE[:3]:  # Sport, Culture, Sortie
        count = par_type.get(type_act, 0)
        pourcentage = (count / total * 100) if total > 0 else 0

        if pourcentage < 15:
            recommandations.append(
                f"Augmenter les activites de type '{type_act}' ({pourcentage:.0f}%)"
            )

    return {"equilibre": len(recommandations) == 0, "recommandations": recommandations}


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_activite(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Valide une activite."""
    erreurs = []

    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")

    if "type" in data and data["type"] not in TYPES_ACTIVITE:
        erreurs.append(f"Type invalide. Valeurs: {', '.join(TYPES_ACTIVITE)}")

    if "date" not in data or not data["date"]:
        erreurs.append("La date est requise")

    if "duree" in data:
        duree = data["duree"]
        if not isinstance(duree, (int, float)) or duree <= 0:
            erreurs.append("La durée doit être > 0")

    if "cout" in data:
        cout = data["cout"]
        if not isinstance(cout, (int, float)) or cout < 0:
            erreurs.append("Le coût doit être >= 0")

    return len(erreurs) == 0, erreurs


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_activite_resume(activite: dict[str, Any]) -> str:
    """Formate le résumé d'une activité."""
    titre = activite.get("titre", "Activité")
    type_act = activite.get("type", "")
    lieu = activite.get("lieu", "")

    parts = [titre]
    if type_act:
        parts.append(f"({type_act})")
    if lieu:
        parts.append(f"@ {lieu}")

    return " ".join(parts)


def grouper_par_mois(activites: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Groupe les activites par mois."""
    groupes = {}

    for act in activites:
        date_act = act.get("date")
        if isinstance(date_act, str):
            from datetime import datetime

            date_act = datetime.fromisoformat(date_act).date()

        if date_act:
            mois_key = date_act.strftime("%Y-%m")
            if mois_key not in groupes:
                groupes[mois_key] = []
            groupes[mois_key].append(act)

    return groupes
