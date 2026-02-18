"""
Génération de prompts IA pour le planning.

Contient les fonctions pour:
- Construction du contexte pour les prompts
- Parsing des réponses de l'IA
"""

from datetime import date

from src.core.constants import JOURS_SEMAINE


def build_planning_prompt_context(
    semaine_debut: date, preferences: dict | None = None, constraints: list[str] | None = None
) -> str:
    """
    Construit le contexte pour le prompt de génération IA.

    Args:
        semaine_debut: Date de début
        preferences: Préférences utilisateur
        constraints: Contraintes supplémentaires

    Returns:
        Contexte formaté pour le prompt
    """
    prefs = preferences or {}
    consts = constraints or []

    lines = [
        f"Semaine du {semaine_debut.strftime('%d/%m/%Y')}",
        "Durée: 7 jours (Lundi à Dimanche)",
    ]

    if prefs.get("nb_personnes"):
        lines.append(f"Nombre de personnes: {prefs['nb_personnes']}")

    if prefs.get("budget"):
        lines.append(f"Budget: {prefs['budget']}")

    if prefs.get("allergies"):
        lines.append(f"Allergies: {', '.join(prefs['allergies'])}")

    if prefs.get("preferences_cuisine"):
        lines.append(f"Préférences: {', '.join(prefs['preferences_cuisine'])}")

    for constraint in consts:
        lines.append(f"Contrainte: {constraint}")

    return "\n".join(lines)


def parse_ai_planning_response(response: list[dict]) -> list[dict]:
    """
    Parse et valide la réponse de l'IA pour le planning.

    Args:
        response: Liste de dicts {jour, dejeuner, diner}

    Returns:
        Liste validée et normalisée

    Examples:
        >>> resp = [{'jour': 'Lundi', 'dejeuner': 'Pâtes', 'diner': 'Salade'}]
        >>> parsed = parse_ai_planning_response(resp)
        >>> parsed[0]['jour']
        'Lundi'
    """
    parsed = []

    for item in response:
        jour = item.get("jour", "")

        # Valider le jour
        if jour not in JOURS_SEMAINE:
            # Tenter de normaliser
            for j in JOURS_SEMAINE:
                if j.lower() == jour.lower():
                    jour = j
                    break

        parsed.append(
            {
                "jour": jour,
                "dejeuner": item.get("dejeuner", "Non défini"),
                "diner": item.get("diner", "Non défini"),
            }
        )

    return parsed


__all__ = [
    "build_planning_prompt_context",
    "parse_ai_planning_response",
]
