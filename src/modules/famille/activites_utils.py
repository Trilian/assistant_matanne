"""
Fonctions utilitaires pures pour les activités familiales.

Ce module contient la logique métier pure (sans dépendances Streamlit/DB)
pour le filtrage, les statistiques, la validation et les recommandations d'activités.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

TYPES_ACTIVITE: list[str] = [
    "Sport",
    "Culture",
    "Sortie",
    "Jeux",
    "Créatif",
    "Nature",
    "Éveil",
]

LIEUX: list[str] = [
    "Maison",
    "Parc",
    "Piscine",
    "Bibliothèque",
    "Centre culturel",
    "Forêt",
    "Plage",
    "Salle de sport",
]

CATEGORIES_AGE: list[str] = [
    "0-6 mois",
    "6-12 mois",
    "1-2 ans",
    "2-3 ans",
    "3+ ans",
]


# ═══════════════════════════════════════════════════════════
# HELPERS INTERNES
# ═══════════════════════════════════════════════════════════


def _parse_date(d: date | str) -> date:
    """Convertit une date string ISO en objet date si nécessaire."""
    if isinstance(d, str):
        return datetime.fromisoformat(d).date()
    return d


# ═══════════════════════════════════════════════════════════
# FILTRAGE
# ═══════════════════════════════════════════════════════════


def filtrer_par_type(activites: list[dict], type_activite: str) -> list[dict]:
    """Filtre les activités par type.

    Args:
        activites: Liste de dicts avec clé 'type'.
        type_activite: Type à filtrer (ex: 'Sport').

    Returns:
        Sous-liste des activités correspondant au type.
    """
    return [a for a in activites if a.get("type") == type_activite]


def filtrer_par_lieu(activites: list[dict], lieu: str) -> list[dict]:
    """Filtre les activités par lieu.

    Args:
        activites: Liste de dicts avec clé 'lieu'.
        lieu: Lieu à filtrer (ex: 'Parc').

    Returns:
        Sous-liste des activités correspondant au lieu.
    """
    return [a for a in activites if a.get("lieu") == lieu]


def filtrer_par_date(
    activites: list[dict],
    date_debut: date,
    date_fin: date,
) -> list[dict]:
    """Filtre les activités dans une période donnée (bornes incluses).

    Args:
        activites: Liste de dicts avec clé 'date' (date ou str ISO).
        date_debut: Date de début de la période.
        date_fin: Date de fin de la période.

    Returns:
        Sous-liste des activités dont la date est dans [date_debut, date_fin].
    """
    result: list[dict] = []
    for a in activites:
        d = _parse_date(a["date"])
        if date_debut <= d <= date_fin:
            result.append(a)
    return result


def get_activites_a_venir(activites: list[dict], jours: int = 7) -> list[dict]:
    """Retourne les activités des *jours* prochains jours (à partir d'aujourd'hui inclus).

    Args:
        activites: Liste de dicts avec clé 'date'.
        jours: Nombre de jours à considérer (défaut: 7).

    Returns:
        Sous-liste des activités à venir.
    """
    today = date.today()
    from datetime import timedelta

    fin = today + timedelta(days=jours)
    return filtrer_par_date(activites, today, fin)


def get_activites_passees(activites: list[dict], jours: int = 30) -> list[dict]:
    """Retourne les activités des *jours* derniers jours.

    Args:
        activites: Liste de dicts avec clé 'date'.
        jours: Nombre de jours passés à considérer (défaut: 30).

    Returns:
        Sous-liste des activités passées.
    """
    today = date.today()
    from datetime import timedelta

    debut = today - timedelta(days=jours)
    result: list[dict] = []
    for a in activites:
        d = _parse_date(a["date"])
        if debut <= d < today:
            result.append(a)
    return result


# ═══════════════════════════════════════════════════════════
# STATISTIQUES
# ═══════════════════════════════════════════════════════════


def calculer_statistiques_activites(activites: list[dict]) -> dict:
    """Calcule des statistiques agrégées sur une liste d'activités.

    Args:
        activites: Liste de dicts avec clés 'type', 'lieu', 'cout', 'duree'.

    Returns:
        Dict avec 'total', 'par_type', 'par_lieu', 'cout_total', 'cout_moyen', 'duree_moyenne'.
    """
    total = len(activites)
    if total == 0:
        return {
            "total": 0,
            "par_type": {},
            "par_lieu": {},
            "cout_total": 0.0,
            "cout_moyen": 0.0,
            "duree_moyenne": 0.0,
        }

    par_type: dict[str, int] = defaultdict(int)
    par_lieu: dict[str, int] = defaultdict(int)
    cout_total = 0.0
    duree_total = 0.0

    for a in activites:
        par_type[a.get("type", "Inconnu")] += 1
        par_lieu[a.get("lieu", "Inconnu")] += 1
        cout_total += a.get("cout", 0.0)
        duree_total += a.get("duree", 0)

    return {
        "total": total,
        "par_type": dict(par_type),
        "par_lieu": dict(par_lieu),
        "cout_total": cout_total,
        "cout_moyen": cout_total / total,
        "duree_moyenne": duree_total / total,
    }


def calculer_frequence_hebdomadaire(activites: list[dict], semaines: int = 4) -> float:
    """Calcule la fréquence hebdomadaire moyenne des activités.

    Args:
        activites: Liste d'activités.
        semaines: Nombre de semaines sur lesquelles calculer.

    Returns:
        Nombre moyen d'activités par semaine. 0.0 si semaines <= 0.
    """
    if semaines <= 0:
        return 0.0
    return len(activites) / semaines


# ═══════════════════════════════════════════════════════════
# RECOMMANDATIONS
# ═══════════════════════════════════════════════════════════

_SUGGESTIONS_PAR_AGE: dict[str, list[dict]] = {
    "bebe": [
        {"type": "Éveil", "titre": "Jeux d'éveil", "description": "Jouets sensoriels et hochets"},
        {"type": "Nature", "titre": "Promenade", "description": "Sortie en poussette au parc"},
        {"type": "Créatif", "titre": "Comptines", "description": "Chansons et comptines"},
        {
            "type": "Sport",
            "titre": "Motricité libre",
            "description": "Tapis d'éveil et exploration",
        },
    ],
    "1-2 ans": [
        {
            "type": "Éveil",
            "titre": "Jeux de manipulation",
            "description": "Empiler, encastrer, transvaser",
        },
        {"type": "Nature", "titre": "Parc à jeux", "description": "Toboggan, balançoire adapté"},
        {
            "type": "Créatif",
            "titre": "Peinture doigts",
            "description": "Peinture propre et pâte à modeler",
        },
        {"type": "Sport", "titre": "Parcours moteur", "description": "Grimper, ramper, sauter"},
    ],
    "2-3 ans": [
        {"type": "Éveil", "titre": "Jeux symboliques", "description": "Dînette, poupée, voitures"},
        {"type": "Culture", "titre": "Bibliothèque", "description": "Heure du conte"},
        {"type": "Créatif", "titre": "Bricolage", "description": "Collage, découpage, gommettes"},
        {
            "type": "Sport",
            "titre": "Vélo draisienne",
            "description": "Apprentissage de l'équilibre",
        },
    ],
    "3+ ans": [
        {
            "type": "Créatif",
            "titre": "Activités créatives",
            "description": "Dessin, peinture, collage avancé",
        },
        {
            "type": "Sport",
            "titre": "Sport collectif",
            "description": "Football, danse, gymnastique",
        },
        {"type": "Culture", "titre": "Musée enfants", "description": "Expositions interactives"},
        {"type": "Nature", "titre": "Randonnée", "description": "Balade nature avec observation"},
    ],
}


def suggerer_activites_age(age_mois: int) -> list[dict]:
    """Suggère des activités adaptées à l'âge de l'enfant.

    Args:
        age_mois: Âge de l'enfant en mois.

    Returns:
        Liste de dicts avec 'type', 'titre', 'description'.
    """
    if age_mois < 12:
        return _SUGGESTIONS_PAR_AGE["bebe"]
    elif age_mois < 24:
        return _SUGGESTIONS_PAR_AGE["1-2 ans"]
    elif age_mois < 36:
        return _SUGGESTIONS_PAR_AGE["2-3 ans"]
    else:
        return _SUGGESTIONS_PAR_AGE["3+ ans"]


def detecter_desequilibre_types(activites: list[dict]) -> dict:
    """Détecte les déséquilibres dans la répartition des types d'activités.

    Un type est considéré dominant s'il représente > 60% des activités.
    Les types absents sont signalés en recommandation.

    Args:
        activites: Liste de dicts avec clé 'type'.

    Returns:
        Dict avec 'equilibre' (bool) et 'recommandations' (list[str]).
    """
    if not activites:
        return {"equilibre": True, "recommandations": []}

    total = len(activites)
    par_type: dict[str, int] = defaultdict(int)
    for a in activites:
        par_type[a.get("type", "Inconnu")] += 1

    recommandations: list[str] = []

    # Vérifier les types dominants (> 60%)
    for type_act, count in par_type.items():
        pct = count / total * 100
        if pct > 60:
            recommandations.append(
                f"Type '{type_act}' surreprésenté ({pct:.0f}%). Diversifiez les activités."
            )

    # Vérifier les types essentiels absents
    types_essentiels = ["Sport", "Culture", "Sortie"]
    for type_ess in types_essentiels:
        if type_ess not in par_type:
            recommandations.append(f"Aucune activité de type '{type_ess}'. Pensez à en ajouter.")

    equilibre = len(recommandations) == 0
    return {"equilibre": equilibre, "recommandations": recommandations}


# ═══════════════════════════════════════════════════════════
# VALIDATION
# ═══════════════════════════════════════════════════════════


def valider_activite(data: dict) -> tuple[bool, list[str]]:
    """Valide les données d'une activité.

    Args:
        data: Dict avec les champs de l'activité.

    Returns:
        Tuple (valide: bool, erreurs: list[str]).
    """
    erreurs: list[str] = []

    if not data.get("titre"):
        erreurs.append("Le titre est obligatoire.")

    if not data.get("date"):
        erreurs.append("La date est obligatoire.")

    type_act = data.get("type")
    if type_act and type_act not in TYPES_ACTIVITE:
        erreurs.append(
            f"Le type '{type_act}' est invalide. Types acceptés: {', '.join(TYPES_ACTIVITE)}."
        )

    duree = data.get("duree")
    if duree is not None and duree < 0:
        erreurs.append("La durée ne peut pas être négative.")

    cout = data.get("cout")
    if cout is not None and cout < 0:
        erreurs.append("Le coût ne peut pas être négatif.")

    return (len(erreurs) == 0, erreurs)


# ═══════════════════════════════════════════════════════════
# FORMATAGE
# ═══════════════════════════════════════════════════════════


def formater_activite_resume(activite: dict) -> str:
    """Formate un résumé lisible d'une activité.

    Args:
        activite: Dict avec clés optionnelles 'titre', 'type', 'lieu'.

    Returns:
        Résumé formaté (ex: "Football (Sport) — Parc").
    """
    titre = activite.get("titre", "Activité")
    type_act = activite.get("type")
    lieu = activite.get("lieu")

    parts = [titre]
    if type_act:
        parts[0] = f"{titre} ({type_act})"
    if lieu:
        parts.append(lieu)

    return " — ".join(parts)


def grouper_par_mois(activites: list[dict]) -> dict[str, list[dict]]:
    """Groupe les activités par mois (format 'YYYY-MM').

    Args:
        activites: Liste de dicts avec clé 'date' (date ou str ISO).

    Returns:
        Dict {clé_mois: [activités]}.
    """
    groupes: dict[str, list[dict]] = defaultdict(list)
    for a in activites:
        d = _parse_date(a["date"])
        cle = d.strftime("%Y-%m")
        groupes[cle].append(a)
    return dict(groupes)
