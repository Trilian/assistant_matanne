"""
Constantes et fonctions de conversion des codes météo WMO.

Contient les seuils d'alerte, les directions cardinales,
la table WEATHERCODES et les fonctions de conversion associées.
"""

__all__ = [
    # Seuils d'alerte
    "SEUIL_GEL",
    "SEUIL_GEL_SEVERE",
    "SEUIL_CANICULE",
    "SEUIL_CANICULE_SEVERE",
    "SEUIL_SECHERESSE_JOURS",
    "SEUIL_PLUIE_FORTE",
    "SEUIL_PLUIE_VIOLENTE",
    "SEUIL_VENT_FORT",
    "SEUIL_VENT_TEMPETE",
    "SEUIL_UV_ELEVE",
    "SEUIL_UV_EXTREME",
    # Directions
    "DIRECTIONS_CARDINALES",
    # Codes météo
    "WEATHERCODES",
    # Fonctions de conversion
    "direction_from_degrees",
    "degrees_from_direction",
    "weathercode_to_condition",
    "weathercode_to_icon",
    "get_arrosage_factor",
]

# ═══════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════

# Seuils d'alerte météo
SEUIL_GEL = 2.0  # °C
SEUIL_GEL_SEVERE = 0.0  # °C
SEUIL_CANICULE = 35.0  # °C
SEUIL_CANICULE_SEVERE = 40.0  # °C
SEUIL_SECHERESSE_JOURS = 7  # jours sans pluie significative
SEUIL_PLUIE_FORTE = 20.0  # mm/jour
SEUIL_PLUIE_VIOLENTE = 50.0  # mm/jour
SEUIL_VENT_FORT = 50.0  # km/h
SEUIL_VENT_TEMPETE = 80.0  # km/h
SEUIL_UV_ELEVE = 6
SEUIL_UV_EXTREME = 10

# Directions cardinales
DIRECTIONS_CARDINALES = ["N", "NE", "E", "SE", "S", "SO", "O", "NO"]

# Codes météo WMO (World Meteorological Organization)
WEATHERCODES = {
    0: {"condition": "Ensoleillé", "icon": "☀️", "arrosage_factor": 1.2},
    1: {"condition": "Peu nuageux", "icon": "🌤️", "arrosage_factor": 1.1},
    2: {"condition": "Partiellement nuageux", "icon": "⛅", "arrosage_factor": 1.0},
    3: {"condition": "Couvert", "icon": "☁️", "arrosage_factor": 0.8},
    45: {"condition": "Brouillard", "icon": "🌫️", "arrosage_factor": 0.5},
    48: {"condition": "Brouillard givrant", "icon": "🌫️", "arrosage_factor": 0.3},
    51: {"condition": "Bruine légère", "icon": "🌦️", "arrosage_factor": 0.7},
    53: {"condition": "Bruine", "icon": "🌧️", "arrosage_factor": 0.5},
    55: {"condition": "Bruine forte", "icon": "🌧️", "arrosage_factor": 0.3},
    61: {"condition": "Pluie légère", "icon": "🌧️", "arrosage_factor": 0.4},
    63: {"condition": "Pluie modérée", "icon": "🌧️", "arrosage_factor": 0.2},
    65: {"condition": "Pluie forte", "icon": "🌧️", "arrosage_factor": 0.0},
    71: {"condition": "Neige légère", "icon": "🌨️", "arrosage_factor": 0.0},
    73: {"condition": "Neige modérée", "icon": "❄️", "arrosage_factor": 0.0},
    75: {"condition": "Neige forte", "icon": "❄️", "arrosage_factor": 0.0},
    80: {"condition": "Averses légères", "icon": "🌦️", "arrosage_factor": 0.5},
    81: {"condition": "Averses", "icon": "🌧️", "arrosage_factor": 0.3},
    82: {"condition": "Averses violentes", "icon": "⛈️", "arrosage_factor": 0.0},
    95: {"condition": "Orage", "icon": "⛈️", "arrosage_factor": 0.0},
    96: {"condition": "Orage avec grêle légère", "icon": "⛈️", "arrosage_factor": 0.0},
    99: {"condition": "Orage avec grêle", "icon": "⛈️", "arrosage_factor": 0.0},
}


# ═══════════════════════════════════════════════════════════
# CONVERSION DE DONNÉES MÉTÉO
# ═══════════════════════════════════════════════════════════


def direction_from_degrees(degrees: float | None) -> str:
    """
    Convertit des degrés en direction cardinale.

    Args:
        degrees: Angle en degrés (0-360, 0=Nord)

    Returns:
        Direction cardinale (N, NE, E, SE, S, SO, O, NO)

    Examples:
        >>> direction_from_degrees(0)
        'N'
        >>> direction_from_degrees(90)
        'E'
        >>> direction_from_degrees(225)
        'SO'
    """
    if degrees is None:
        return ""

    # Normaliser entre 0 et 360
    degrees = degrees % 360

    # 8 directions = 45° chacune
    index = round(degrees / 45) % 8
    return DIRECTIONS_CARDINALES[index]


def degrees_from_direction(direction: str) -> float | None:
    """
    Convertit une direction cardinale en degrés.

    Args:
        direction: Direction cardinale

    Returns:
        Angle en degrés ou None si invalide

    Examples:
        >>> degrees_from_direction('N')
        0.0
        >>> degrees_from_direction('E')
        90.0
    """
    direction = direction.upper().strip()
    if direction not in DIRECTIONS_CARDINALES:
        return None

    index = DIRECTIONS_CARDINALES.index(direction)
    return float(index * 45)


def weathercode_to_condition(code: int | None) -> str:
    """
    Convertit le code météo WMO en description textuelle.

    Args:
        code: Code météo WMO

    Returns:
        Description de la condition météo

    Examples:
        >>> weathercode_to_condition(0)
        'Ensoleillé'
        >>> weathercode_to_condition(63)
        'Pluie modérée'
    """
    if code is None:
        return "Inconnu"

    info = WEATHERCODES.get(code)
    return info["condition"] if info else "Inconnu"


def weathercode_to_icon(code: int | None) -> str:
    """
    Convertit le code météo WMO en emoji.

    Args:
        code: Code météo WMO

    Returns:
        Emoji représentant la météo

    Examples:
        >>> weathercode_to_icon(0)
        '☀️'
        >>> weathercode_to_icon(95)
        '⛈️'
    """
    if code is None:
        return "❓"

    info = WEATHERCODES.get(code)
    return info["icon"] if info else "🌡️"


def get_arrosage_factor(code: int | None) -> float:
    """
    Retourne le facteur d'arrosage basé sur le code météo.

    0.0 = pas d'arrosage nécessaire (pluie)
    1.0 = arrosage normal
    1.2 = arrosage augmenté (soleil)

    Args:
        code: Code météo WMO

    Returns:
        Facteur multiplicateur pour l'arrosage
    """
    if code is None:
        return 1.0

    info = WEATHERCODES.get(code)
    return info["arrosage_factor"] if info else 1.0
