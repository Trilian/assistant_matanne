"""
Fonctions utilitaires pures pour les routines familiales.

Ce module contient la logique métier pure (sans dépendances Streamlit/DB)
pour le filtrage, les statistiques, la validation et les recommandations de routines.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, time, timedelta

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

JOURS_SEMAINE: list[str] = [
    "Lundi",
    "Mardi",
    "Mercredi",
    "Jeudi",
    "Vendredi",
    "Samedi",
    "Dimanche",
]

MOMENTS_JOURNEE: list[str] = [
    "Matin",
    "Midi",
    "Après-midi",
    "Soir",
    "Nuit",
]

TYPES_ROUTINE: list[str] = [
    "Réveil",
    "Repas",
    "Sieste",
    "Bain",
    "Coucher",
    "Jeu",
    "Activité",
    "Soin",
]


# ═══════════════════════════════════════════════════════════
# HELPERS INTERNES
# ═══════════════════════════════════════════════════════════


def _parse_time(t: time | str | None) -> time | None:
    """Convertit une heure string ISO en objet time si nécessaire."""
    if t is None:
        return None
    if isinstance(t, str):
        return datetime.fromisoformat(t).time()
    return t


def _jour_francais(weekday: int) -> str:
    """Retourne le nom français du jour à partir de weekday (0=lundi)."""
    return JOURS_SEMAINE[weekday]


# ═══════════════════════════════════════════════════════════
# GESTION DU TEMPS
# ═══════════════════════════════════════════════════════════


def get_moment_journee(heure: time | str) -> str:
    """Détermine le moment de la journée pour une heure donnée.

    Plages horaires:
        - Matin: 5h-12h
        - Midi: 12h-14h
        - Après-midi: 14h-18h
        - Soir: 18h-22h
        - Nuit: 22h-5h

    Args:
        heure: Objet time ou string ISO.

    Returns:
        Moment de la journée ('Matin', 'Midi', 'Après-midi', 'Soir', 'Nuit').
    """
    t = _parse_time(heure)
    if t is None:
        return "Inconnu"

    h = t.hour
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


def calculer_duree_routine(routines: list[dict]) -> int:
    """Calcule la durée totale d'une liste de routines en minutes.

    Args:
        routines: Liste de dicts avec clé 'duree' (en minutes).

    Returns:
        Durée totale en minutes.
    """
    return sum(r.get("duree", 0) for r in routines)


def calculer_heure_fin(debut: time | str, duree_minutes: int) -> time:
    """Calcule l'heure de fin étant donné un début et une durée.

    Args:
        debut: Heure de début (time ou string ISO).
        duree_minutes: Durée en minutes.

    Returns:
        Heure de fin.
    """
    t = _parse_time(debut)
    if t is None:
        raise ValueError("L'heure de début ne peut pas être None.")

    dt = datetime(2000, 1, 1, t.hour, t.minute, t.second)
    dt_fin = dt + timedelta(minutes=duree_minutes)
    return dt_fin.time()


# ═══════════════════════════════════════════════════════════
# FILTRAGE ET ORGANISATION
# ═══════════════════════════════════════════════════════════


def filtrer_par_moment(routines: list[dict], moment: str) -> list[dict]:
    """Filtre les routines par moment de la journée.

    Args:
        routines: Liste de dicts avec clé 'moment'.
        moment: Moment à filtrer (ex: 'Matin').

    Returns:
        Sous-liste des routines correspondant au moment.
    """
    return [r for r in routines if r.get("moment") == moment]


def filtrer_par_jour(routines: list[dict], jour: str) -> list[dict]:
    """Filtre les routines actives pour un jour donné.

    Args:
        routines: Liste de dicts avec clé 'jours_actifs' (list[str]).
        jour: Jour à filtrer (ex: 'Lundi').

    Returns:
        Sous-liste des routines actives ce jour-là.
    """
    return [r for r in routines if jour in r.get("jours_actifs", JOURS_SEMAINE)]


def trier_par_heure(routines: list[dict]) -> list[dict]:
    """Trie les routines par heure croissante. Les routines sans heure vont à la fin.

    Args:
        routines: Liste de dicts avec clé 'heure' (time, str ou None).

    Returns:
        Liste triée par heure.
    """

    def sort_key(r: dict) -> tuple[int, time]:
        t = _parse_time(r.get("heure"))
        if t is None:
            return (1, time(23, 59, 59))
        return (0, t)

    return sorted(routines, key=sort_key)


def grouper_par_moment(routines: list[dict]) -> dict[str, list[dict]]:
    """Groupe les routines par moment de la journée.

    Les moments inconnus sont regroupés sous 'Autre'.

    Args:
        routines: Liste de dicts avec clé 'moment'.

    Returns:
        Dict {moment: [routines]}.
    """
    groupes: dict[str, list[dict]] = defaultdict(list)
    for r in routines:
        moment = r.get("moment", "Autre")
        if moment not in MOMENTS_JOURNEE:
            moment = "Autre"
        groupes[moment].append(r)
    return dict(groupes)


def get_routines_aujourdhui(routines: list[dict]) -> list[dict]:
    """Retourne les routines actives pour le jour actuel.

    Args:
        routines: Liste de dicts avec clé 'jours_actifs'.

    Returns:
        Sous-liste des routines actives aujourd'hui.
    """
    jour = _jour_francais(date.today().weekday())
    return filtrer_par_jour(routines, jour)


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_statistiques_routines(routines: list[dict]) -> dict:
    """Calcule des statistiques agrégées sur une liste de routines.

    Args:
        routines: Liste de dicts avec clés 'type', 'moment'.

    Returns:
        Dict avec 'total', 'par_type', 'par_moment'.
    """
    total = len(routines)
    if total == 0:
        return {"total": 0, "par_type": {}, "par_moment": {}}

    par_type: dict[str, int] = defaultdict(int)
    par_moment: dict[str, int] = defaultdict(int)

    for r in routines:
        par_type[r.get("type", "Inconnu")] += 1
        par_moment[r.get("moment", "Inconnu")] += 1

    return {
        "total": total,
        "par_type": dict(par_type),
        "par_moment": dict(par_moment),
    }


def detecter_conflits_horaires(routines: list[dict]) -> list[dict]:
    """Détecte les conflits d'horaires entre routines.

    Deux routines sont en conflit si l'une commence avant la fin de l'autre.

    Args:
        routines: Liste de dicts avec clés 'titre', 'heure' (time), 'duree' (minutes).

    Returns:
        Liste de dicts décrivant les conflits trouvés.
    """
    conflits: list[dict] = []
    triees = trier_par_heure(routines)

    for i in range(len(triees)):
        t_i = _parse_time(triees[i].get("heure"))
        d_i = triees[i].get("duree", 0)
        if t_i is None:
            continue

        fin_i = calculer_heure_fin(t_i, d_i)

        for j in range(i + 1, len(triees)):
            t_j = _parse_time(triees[j].get("heure"))
            if t_j is None:
                continue

            # Conflit si j commence avant la fin de i
            if t_j < fin_i:
                conflits.append(
                    {
                        "routine_a": triees[i].get("titre", "?"),
                        "routine_b": triees[j].get("titre", "?"),
                        "heure_a": t_i,
                        "heure_b": t_j,
                    }
                )

    return conflits


def analyser_regularite(
    historique: list[dict],
    routine_id: int,
    jours: int = 7,
) -> dict:
    """Analyse la régularité d'exécution d'une routine.

    Args:
        historique: Liste de dicts avec clés 'routine_id', 'date'.
        routine_id: ID de la routine à analyser.
        jours: Fenêtre d'analyse en jours.

    Returns:
        Dict avec 'executions', 'jours', 'taux_realisation', 'regularite'.
    """
    executions = [h for h in historique if h.get("routine_id") == routine_id]
    nb = len(executions)
    taux = (nb / jours * 100) if jours > 0 else 0.0

    if taux >= 90:
        regularite = "Excellent"
    elif taux >= 70:
        regularite = "Bon"
    elif taux >= 50:
        regularite = "Moyen"
    else:
        regularite = "Faible"

    return {
        "executions": nb,
        "jours": jours,
        "taux_realisation": round(taux, 1),
        "regularite": regularite,
    }


# ═══════════════════════════════════════════════════════════
# SUGGESTIONS
# ═══════════════════════════════════════════════════════════

_ROUTINES_PAR_AGE: dict[str, list[dict]] = {
    "bebe": [
        {"type": "Réveil", "titre": "Réveil", "moment": "Matin", "duree": 15},
        {"type": "Repas", "titre": "Biberon/Tétée", "moment": "Matin", "duree": 30},
        {"type": "Sieste", "titre": "Sieste matin", "moment": "Matin", "duree": 90},
        {"type": "Repas", "titre": "Repas midi", "moment": "Midi", "duree": 30},
        {"type": "Sieste", "titre": "Sieste après-midi", "moment": "Après-midi", "duree": 120},
        {"type": "Bain", "titre": "Bain", "moment": "Soir", "duree": 20},
        {"type": "Coucher", "titre": "Coucher", "moment": "Soir", "duree": 30},
    ],
    "1-2 ans": [
        {"type": "Réveil", "titre": "Réveil", "moment": "Matin", "duree": 15},
        {"type": "Repas", "titre": "Petit-déjeuner", "moment": "Matin", "duree": 30},
        {"type": "Activité", "titre": "Activité matinale", "moment": "Matin", "duree": 60},
        {"type": "Repas", "titre": "Déjeuner", "moment": "Midi", "duree": 30},
        {"type": "Sieste", "titre": "Sieste après-midi", "moment": "Après-midi", "duree": 90},
        {"type": "Jeu", "titre": "Jeux libres", "moment": "Après-midi", "duree": 60},
        {"type": "Bain", "titre": "Bain", "moment": "Soir", "duree": 20},
        {"type": "Coucher", "titre": "Coucher", "moment": "Soir", "duree": 30},
    ],
    "2+ ans": [
        {"type": "Réveil", "titre": "Réveil", "moment": "Matin", "duree": 15},
        {"type": "Repas", "titre": "Petit-déjeuner", "moment": "Matin", "duree": 30},
        {"type": "Activité", "titre": "Activité éducative", "moment": "Matin", "duree": 60},
        {"type": "Repas", "titre": "Déjeuner", "moment": "Midi", "duree": 30},
        {"type": "Sieste", "titre": "Sieste (optionnelle)", "moment": "Après-midi", "duree": 60},
        {"type": "Jeu", "titre": "Jeux créatifs", "moment": "Après-midi", "duree": 60},
        {"type": "Bain", "titre": "Bain", "moment": "Soir", "duree": 20},
        {"type": "Coucher", "titre": "Coucher", "moment": "Soir", "duree": 30},
    ],
}


def suggerer_routines_age(age_mois: int) -> list[dict]:
    """Suggère des routines adaptées à l'âge de l'enfant.

    Args:
        age_mois: Âge de l'enfant en mois.

    Returns:
        Liste de dicts avec 'type', 'titre', 'moment', 'duree'.
    """
    if age_mois < 12:
        return _ROUTINES_PAR_AGE["bebe"]
    elif age_mois < 24:
        return _ROUTINES_PAR_AGE["1-2 ans"]
    else:
        return _ROUTINES_PAR_AGE["2+ ans"]


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_routine(data: dict) -> tuple[bool, list[str]]:
    """Valide les données d'une routine.

    Args:
        data: Dict avec les champs de la routine.

    Returns:
        Tuple (valide: bool, erreurs: list[str]).
    """
    erreurs: list[str] = []

    if not data.get("titre"):
        erreurs.append("Le titre est obligatoire.")

    type_routine = data.get("type")
    if type_routine and type_routine not in TYPES_ROUTINE:
        erreurs.append(
            f"Le type '{type_routine}' est invalide. Types acceptés: {', '.join(TYPES_ROUTINE)}."
        )

    moment = data.get("moment")
    if moment and moment not in MOMENTS_JOURNEE:
        erreurs.append(
            f"Le moment '{moment}' est invalide. Moments acceptés: {', '.join(MOMENTS_JOURNEE)}."
        )

    duree = data.get("duree")
    if duree is not None and duree < 0:
        erreurs.append("La durée ne peut pas être négative.")

    return (len(erreurs) == 0, erreurs)


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_heure(heure: time | str) -> str:
    """Formate une heure en string HH:MM.

    Args:
        heure: Objet time ou string ISO.

    Returns:
        Chaîne formatée 'HH:MM'.
    """
    t = _parse_time(heure)
    if t is None:
        return "--:--"
    return t.strftime("%H:%M")


def formater_duree(minutes: int) -> str:
    """Formate une durée en minutes vers un format lisible.

    Args:
        minutes: Durée en minutes.

    Returns:
        Chaîne formatée (ex: '30min', '1h30', '2h').
    """
    if minutes < 60:
        return f"{minutes}min"
    heures = minutes // 60
    reste = minutes % 60
    if reste == 0:
        return f"{heures}h"
    return f"{heures}h{reste:02d}" if reste >= 10 else f"{heures}h{reste}"
