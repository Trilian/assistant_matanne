"""
Détection de saison, conseils jardinage et résumé météo.

Fournit la logique de détermination de la saison courante,
la génération de conseils de jardinage contextuels et
le formatage de résumés météo textuels.
"""

from datetime import date, datetime

__all__ = [
    "get_season",
    "get_gardening_advice_for_weather",
    "format_weather_summary",
]


# ═══════════════════════════════════════════════════════════
# CONSEILS JARDINAGE
# ═══════════════════════════════════════════════════════════


def get_season(dt: date | datetime | None = None) -> str:
    """
    Détermine la saison pour une date donnée.

    Args:
        dt: Date (par défaut: aujourd'hui)

    Returns:
        Nom de la saison (printemps, été, automne, hiver)
    """
    if dt is None:
        dt = date.today()
    elif isinstance(dt, datetime):
        dt = dt.date()

    month = dt.month

    if month in [3, 4, 5]:
        return "printemps"
    elif month in [6, 7, 8]:
        return "été"
    elif month in [9, 10, 11]:
        return "automne"
    else:
        return "hiver"


def get_gardening_advice_for_weather(
    condition: str, temp_max: float, precipitation_mm: float
) -> list[dict]:
    """
    Génère des conseils de jardinage basés sur la météo.

    Args:
        condition: Condition météo (ensoleillé, pluvieux, etc.)
        temp_max: Température maximale
        precipitation_mm: Précipitations en mm

    Returns:
        Liste de conseils avec priorité et actions
    """
    conseils = []

    # Conseils selon la température
    if temp_max >= 30:
        conseils.append(
            {
                "priorite": 1,
                "icone": "💧",
                "titre": "Arrosage renforcé",
                "description": "Arrosez le soir ou tôt le matin pour limiter l'évaporation",
                "action": "Évitez l'arrosage en plein soleil (risque de brûlure)",
            }
        )
        conseils.append(
            {
                "priorite": 2,
                "icone": "🌿",
                "titre": "Paillage recommandé",
                "description": "Paillez le sol pour conserver l'humidité",
                "action": "Utilisez de la paille, des feuilles mortes ou du BRF",
            }
        )

    if temp_max < 5:
        conseils.append(
            {
                "priorite": 1,
                "icone": "🧥",
                "titre": "Protection hivernale",
                "description": "Protégez les plantes sensibles au froid",
                "action": "Utilisez un voile d'hivernage ou rentrez les pots",
            }
        )

    # Conseils selon les précipitations
    if precipitation_mm > 30:
        conseils.append(
            {
                "priorite": 1,
                "icone": "🌊",
                "titre": "Drainage à vérifier",
                "description": "De fortes pluies sont prévues",
                "action": "Vérifiez que l'eau s'écoule bien dans vos pots et jardinières",
            }
        )
    elif precipitation_mm < 1 and temp_max > 20:
        conseils.append(
            {
                "priorite": 2,
                "icone": "💧",
                "titre": "Vigilance arrosage",
                "description": "Pas de pluie prévue",
                "action": "Planifiez votre arrosage pour les prochains jours",
            }
        )

    # Conseils selon la condition
    if "ensoleillé" in condition.lower() or "soleil" in condition.lower():
        conseils.append(
            {
                "priorite": 3,
                "icone": "☀️",
                "titre": "Journée idéale au jardin",
                "description": "Conditions parfaites pour le jardinage",
                "action": "Profitez-en pour désherber, planter ou tailler",
            }
        )

    if "orage" in condition.lower():
        conseils.append(
            {
                "priorite": 1,
                "icone": "⚡",
                "titre": "Orages prévus",
                "description": "Risque de grêle et vents forts",
                "action": "Mettez à l'abri les plantes en pot et les objets légers",
            }
        )

    # Trier par priorité
    conseils.sort(key=lambda x: x["priorite"])

    return conseils


def format_weather_summary(previsions: list[dict]) -> str:
    """
    Formate un résumé météo textuel.

    Args:
        previsions: Liste de prévisions

    Returns:
        Résumé formaté
    """
    if not previsions:
        return "Aucune prévision disponible"

    # Calculer les moyennes
    temp_min = min(p.get("temp_min", p.get("temperature_min", 20)) for p in previsions)
    temp_max = max(p.get("temp_max", p.get("temperature_max", 20)) for p in previsions)
    total_precip = sum(p.get("precipitation_mm", 0) for p in previsions)

    nb_jours = len(previsions)

    summary = f"Prévisions sur {nb_jours} jours: "
    summary += f"Températures entre {temp_min:.0f}°C et {temp_max:.0f}°C. "

    if total_precip > 0:
        summary += f"Cumul de précipitations: {total_precip:.0f}mm."
    else:
        summary += "Pas de pluie prévue."

    return summary
