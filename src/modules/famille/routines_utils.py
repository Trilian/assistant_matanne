"""
Logique metier du module Routines (famille) - Separee de l'UI
Ce module contient toute la logique pure, testable sans Streamlit
"""

import logging
from datetime import date, time, timedelta
from typing import Any

from src.core.constants import JOURS_SEMAINE
from src.core.date_utils import formater_temps

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════
# CONSTANTES LOCALES
# ═══════════════════════════════════════════════════════════

MOMENTS_JOURNEE = ["Matin", "Midi", "Après-midi", "Soir", "Nuit"]
TYPES_ROUTINE = ["Réveil", "Repas", "Sieste", "Bain", "Coucher", "Soins", "Autre"]


# ═══════════════════════════════════════════════════════════
# GESTION DU TEMPS
# ═══════════════════════════════════════════════════════════


def get_moment_journee(heure: time) -> str:
    """Determine le moment de la journee d'après l'heure."""
    if isinstance(heure, str):
        from datetime import datetime

        heure = datetime.fromisoformat(heure).time()

    h = heure.hour

    if 5 <= h < 12:
        return "Matin"
    elif 12 <= h < 14:
        return "Midi"
    elif 14 <= h < 18:
        return "Après-midi"
    elif 18 <= h < 22:
        return "Soir"
    else:
        return "Nuit"


def calculer_duree_routine(routines: list[dict[str, Any]]) -> int:
    """Calcule la duree totale d'une sequence de routines (en minutes)."""
    duree_totale = 0

    for routine in routines:
        duree = routine.get("duree", 0)
        duree_totale += duree

    return duree_totale


def calculer_heure_fin(heure_debut: time, duree_minutes: int) -> time:
    """Calcule l'heure de fin d'après le debut et la duree."""
    from datetime import datetime

    if isinstance(heure_debut, str):
        heure_debut = datetime.fromisoformat(heure_debut).time()

    debut_dt = datetime.combine(date.today(), heure_debut)
    fin_dt = debut_dt + timedelta(minutes=duree_minutes)

    return fin_dt.time()


# ═══════════════════════════════════════════════════════════
# FILTRAGE ET ORGANISATION
# ═══════════════════════════════════════════════════════════


def filtrer_par_moment(routines: list[dict[str, Any]], moment: str) -> list[dict[str, Any]]:
    """Filtre les routines par moment de la journee."""
    return [r for r in routines if r.get("moment") == moment]


def filtrer_par_jour(routines: list[dict[str, Any]], jour: str) -> list[dict[str, Any]]:
    """Filtre les routines par jour de la semaine."""
    resultats = []

    for routine in routines:
        jours_actifs = routine.get("jours_actifs", JOURS_SEMAINE)
        if jour in jours_actifs:
            resultats.append(routine)

    return resultats


def get_routines_aujourdhui(routines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retourne les routines du jour actuel."""
    jour_actuel = JOURS_SEMAINE[date.today().weekday()]
    return filtrer_par_jour(routines, jour_actuel)


def grouper_par_moment(routines: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Groupe les routines par moment de la journee."""
    groupes = {moment: [] for moment in MOMENTS_JOURNEE}

    for routine in routines:
        moment = routine.get("moment", "Autre")
        if moment in groupes:
            groupes[moment].append(routine)
        else:
            if "Autre" not in groupes:
                groupes["Autre"] = []
            groupes["Autre"].append(routine)

    return groupes


def trier_par_heure(routines: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Trie les routines par heure de debut."""

    def get_heure_key(routine):
        heure = routine.get("heure")
        if not heure:
            return time(23, 59)
        if isinstance(heure, str):
            from datetime import datetime

            heure = datetime.fromisoformat(heure).time()
        return heure

    return sorted(routines, key=get_heure_key)


# ═══════════════════════════════════════════════════════════
# STATISTIQUES ET ANALYSE
# ═══════════════════════════════════════════════════════════


def calculer_statistiques_routines(routines: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcule les statistiques des routines."""
    total = len(routines)

    if total == 0:
        return {"total": 0, "par_type": {}, "par_moment": {}, "duree_totale_jour": 0}

    # Par type
    par_type = {}
    for routine in routines:
        type_r = routine.get("type", "Autre")
        par_type[type_r] = par_type.get(type_r, 0) + 1

    # Par moment
    par_moment = {}
    for routine in routines:
        moment = routine.get("moment", "Autre")
        par_moment[moment] = par_moment.get(moment, 0) + 1

    # Duree totale
    duree_totale = calculer_duree_routine(routines)

    return {
        "total": total,
        "par_type": par_type,
        "par_moment": par_moment,
        "duree_totale_jour": duree_totale,
    }


def analyser_regularite(
    historique: list[dict[str, Any]], routine_id: int, jours: int = 7
) -> dict[str, Any]:
    """Analyse la regularite d'execution d'une routine."""
    date_limite = date.today() - timedelta(days=jours)

    executions = []
    for entry in historique:
        if entry.get("routine_id") == routine_id:
            date_exec = entry.get("date")
            if isinstance(date_exec, str):
                from datetime import datetime

                date_exec = datetime.fromisoformat(date_exec).date()

            if date_exec >= date_limite:
                executions.append(entry)

    taux_realisation = (len(executions) / jours * 100) if jours > 0 else 0

    # Regularite
    if taux_realisation >= 90:
        regularite = "Excellent"
    elif taux_realisation >= 70:
        regularite = "Bon"
    elif taux_realisation >= 50:
        regularite = "Moyen"
    else:
        regularite = "Faible"

    return {
        "executions": len(executions),
        "jours_analyses": jours,
        "taux_realisation": taux_realisation,
        "regularite": regularite,
    }


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS
# ═══════════════════════════════════════════════════════════


def suggerer_routines_age(age_mois: int) -> list[dict[str, Any]]:
    """Suggère des routines adaptées à l'âge."""
    suggestions = []

    # Routines communes
    suggestions.append(
        {"titre": "Réveil", "type": "Réveil", "moment": "Matin", "heure": "07:00", "duree": 15}
    )

    if age_mois < 12:
        suggestions.extend(
            [
                {
                    "titre": "Sieste matin",
                    "type": "Sieste",
                    "moment": "Matin",
                    "heure": "10:00",
                    "duree": 60,
                },
                {
                    "titre": "Sieste après-midi",
                    "type": "Sieste",
                    "moment": "Après-midi",
                    "heure": "14:00",
                    "duree": 90,
                },
                {"titre": "Bain", "type": "Bain", "moment": "Soir", "heure": "19:00", "duree": 20},
                {
                    "titre": "Coucher",
                    "type": "Coucher",
                    "moment": "Soir",
                    "heure": "20:00",
                    "duree": 15,
                },
            ]
        )
    elif age_mois < 24:
        suggestions.extend(
            [
                {
                    "titre": "Sieste après-midi",
                    "type": "Sieste",
                    "moment": "Après-midi",
                    "heure": "13:30",
                    "duree": 120,
                },
                {"titre": "Bain", "type": "Bain", "moment": "Soir", "heure": "19:30", "duree": 25},
                {
                    "titre": "Coucher",
                    "type": "Coucher",
                    "moment": "Soir",
                    "heure": "20:30",
                    "duree": 20,
                },
            ]
        )
    else:
        suggestions.extend(
            [
                {
                    "titre": "Sieste (optionnelle)",
                    "type": "Sieste",
                    "moment": "Après-midi",
                    "heure": "14:00",
                    "duree": 60,
                },
                {"titre": "Bain", "type": "Bain", "moment": "Soir", "heure": "20:00", "duree": 30},
                {
                    "titre": "Coucher",
                    "type": "Coucher",
                    "moment": "Soir",
                    "heure": "21:00",
                    "duree": 20,
                },
            ]
        )

    return suggestions


def detecter_conflits_horaires(routines: list[dict[str, Any]]) -> list[tuple[dict, dict]]:
    """Detecte les conflits d'horaires entre routines."""
    conflits = []
    routines_triees = trier_par_heure(routines)

    for i in range(len(routines_triees)):
        r1 = routines_triees[i]
        heure1 = r1.get("heure")
        duree1 = r1.get("duree", 0)

        if not heure1:
            continue

        if isinstance(heure1, str):
            from datetime import datetime

            heure1 = datetime.fromisoformat(heure1).time()

        fin1 = calculer_heure_fin(heure1, duree1)

        for j in range(i + 1, len(routines_triees)):
            r2 = routines_triees[j]
            heure2 = r2.get("heure")

            if not heure2:
                continue

            if isinstance(heure2, str):
                from datetime import datetime

                heure2 = datetime.fromisoformat(heure2).time()

            # Verifier chevauchement
            if heure2 < fin1:
                conflits.append((r1, r2))

    return conflits


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_routine(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Valide une routine."""
    erreurs = []

    if "titre" not in data or not data["titre"]:
        erreurs.append("Le titre est requis")

    if "type" in data and data["type"] not in TYPES_ROUTINE:
        erreurs.append(f"Type invalide. Valeurs: {', '.join(TYPES_ROUTINE)}")

    if "moment" in data and data["moment"] not in MOMENTS_JOURNEE:
        erreurs.append(f"Moment invalide. Valeurs: {', '.join(MOMENTS_JOURNEE)}")

    if "duree" in data:
        duree = data["duree"]
        if not isinstance(duree, int) or duree <= 0:
            erreurs.append("La durée doit être > 0")

    return len(erreurs) == 0, erreurs


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_heure(heure: time) -> str:
    """Formate une heure."""
    if isinstance(heure, str):
        from datetime import datetime

        heure = datetime.fromisoformat(heure).time()

    return heure.strftime("%H:%M")


def formater_duree(minutes: int) -> str:
    """Formate une duree en minutes (alias pour formater_temps)."""
    return formater_temps(minutes)
