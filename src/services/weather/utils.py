"""
Fonctions utilitaires pures pour le service météo jardin.

Ces fonctions peuvent être testées sans dépendances HTTP ni base de données.
Elles représentent la logique métier pure extraite de weather.py.
"""

from datetime import date, datetime
from typing import Any

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
    0: {"condition": "Ensoleillé", "icon": "â˜€ï¸", "arrosage_factor": 1.2},
    1: {"condition": "Peu nuageux", "icon": "🌤️", "arrosage_factor": 1.1},
    2: {"condition": "Partiellement nuageux", "icon": "â›…", "arrosage_factor": 1.0},
    3: {"condition": "Couvert", "icon": "â˜ï¸", "arrosage_factor": 0.8},
    45: {"condition": "Brouillard", "icon": "🌫️", "arrosage_factor": 0.5},
    48: {"condition": "Brouillard givrant", "icon": "🌫️", "arrosage_factor": 0.3},
    51: {"condition": "Bruine légère", "icon": "🌦️", "arrosage_factor": 0.7},
    53: {"condition": "Bruine", "icon": "🌧️", "arrosage_factor": 0.5},
    55: {"condition": "Bruine forte", "icon": "🌧️", "arrosage_factor": 0.3},
    61: {"condition": "Pluie légère", "icon": "🌧️", "arrosage_factor": 0.4},
    63: {"condition": "Pluie modérée", "icon": "🌧️", "arrosage_factor": 0.2},
    65: {"condition": "Pluie forte", "icon": "🌧️", "arrosage_factor": 0.0},
    71: {"condition": "Neige légère", "icon": "🌨️", "arrosage_factor": 0.0},
    73: {"condition": "Neige modérée", "icon": "â„ï¸", "arrosage_factor": 0.0},
    75: {"condition": "Neige forte", "icon": "â„ï¸", "arrosage_factor": 0.0},
    80: {"condition": "Averses légères", "icon": "🌦️", "arrosage_factor": 0.5},
    81: {"condition": "Averses", "icon": "🌧️", "arrosage_factor": 0.3},
    82: {"condition": "Averses violentes", "icon": "â›ˆï¸", "arrosage_factor": 0.0},
    95: {"condition": "Orage", "icon": "â›ˆï¸", "arrosage_factor": 0.0},
    96: {"condition": "Orage avec grêle légère", "icon": "â›ˆï¸", "arrosage_factor": 0.0},
    99: {"condition": "Orage avec grêle", "icon": "â›ˆï¸", "arrosage_factor": 0.0},
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
        'â˜€ï¸'
        >>> weathercode_to_icon(95)
        'â›ˆï¸'
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


# ═══════════════════════════════════════════════════════════
# CALCUL DE TEMPÉRATURES
# ═══════════════════════════════════════════════════════════


def calculate_average_temperature(temp_min: float, temp_max: float) -> float:
    """
    Calcule la température moyenne.

    Args:
        temp_min: Température minimale
        temp_max: Température maximale

    Returns:
        Température moyenne
    """
    return (temp_min + temp_max) / 2


def calculate_temperature_amplitude(temp_min: float, temp_max: float) -> float:
    """
    Calcule l'amplitude thermique (écart min/max).

    Args:
        temp_min: Température minimale
        temp_max: Température maximale

    Returns:
        Amplitude thermique
    """
    return abs(temp_max - temp_min)


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convertit Celsius en Fahrenheit."""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """Convertit Fahrenheit en Celsius."""
    return (fahrenheit - 32) * 5 / 9


def calculate_feels_like(temp: float, humidity: int, wind_speed: float) -> float:
    """
    Calcule la température ressentie (approximation simplifiée).

    Combine l'effet du vent (refroidissement) et de l'humidité.

    Args:
        temp: Température en °C
        humidity: Humidité en %
        wind_speed: Vitesse du vent en km/h

    Returns:
        Température ressentie en °C
    """
    # Effet du vent (refroidissement éolien) si temp < 10°C
    if temp < 10 and wind_speed > 5:
        wind_chill = (
            13.12 + 0.6215 * temp - 11.37 * (wind_speed**0.16) + 0.3965 * temp * (wind_speed**0.16)
        )
        return round(wind_chill, 1)

    # Effet de l'humidité (chaleur ressentie) si temp > 20°C
    if temp > 20 and humidity > 40:
        # Formule simplifiée de l'indice de chaleur
        heat_factor = (humidity - 40) * 0.02  # +0.02°C par % d'humidité au-dessus de 40%
        return round(temp + heat_factor, 1)

    return round(temp, 1)


# ═══════════════════════════════════════════════════════════
# DÉTECTION D'ALERTES
# ═══════════════════════════════════════════════════════════


def detect_gel_alert(temp_min: float) -> dict | None:
    """
    Détecte une alerte gel basée sur la température minimale.

    Args:
        temp_min: Température minimale prévue

    Returns:
        Dict avec niveau et message, ou None si pas d'alerte

    Examples:
        >>> detect_gel_alert(-2)
        {'niveau': 'danger', 'message': 'Gel sévère prévu: -2°C'}
    """
    if temp_min > SEUIL_GEL:
        return None

    if temp_min <= SEUIL_GEL_SEVERE:
        return {
            "niveau": "danger",
            "message": f"Gel sévère prévu: {temp_min}°C",
            "conseil": "Protégez immédiatement vos plantes sensibles! Rentrez tous les pots.",
            "temperature": temp_min,
        }
    else:
        return {
            "niveau": "attention",
            "message": f"Risque de gel: {temp_min}°C",
            "conseil": "Préparez un voile d'hivernage pour vos plantes fragiles.",
            "temperature": temp_min,
        }


def detect_canicule_alert(temp_max: float) -> dict | None:
    """
    Détecte une alerte canicule basée sur la température maximale.

    Args:
        temp_max: Température maximale prévue

    Returns:
        Dict avec niveau et message, ou None si pas d'alerte
    """
    if temp_max < SEUIL_CANICULE:
        return None

    if temp_max >= SEUIL_CANICULE_SEVERE:
        return {
            "niveau": "danger",
            "message": f"Canicule extrême: {temp_max}°C",
            "conseil": "Arrosez abondamment matin et soir. Paillez le sol. Ombragez les plantes fragiles.",
            "temperature": temp_max,
        }
    else:
        return {
            "niveau": "attention",
            "message": f"Forte chaleur: {temp_max}°C",
            "conseil": "Arrosez le soir après le coucher du soleil. Évitez l'arrosage en plein soleil.",
            "temperature": temp_max,
        }


def detect_pluie_forte_alert(precipitation_mm: float) -> dict | None:
    """
    Détecte une alerte pluie forte.

    Args:
        precipitation_mm: Précipitations prévues en mm

    Returns:
        Dict avec niveau et message, ou None si pas d'alerte
    """
    if precipitation_mm < SEUIL_PLUIE_FORTE:
        return None

    if precipitation_mm >= SEUIL_PLUIE_VIOLENTE:
        return {
            "niveau": "danger",
            "message": f"Pluies violentes: {precipitation_mm}mm",
            "conseil": "Protégez les jeunes plants. Risque d'inondation et d'érosion.",
            "precipitation": precipitation_mm,
        }
    else:
        return {
            "niveau": "attention",
            "message": f"Fortes pluies: {precipitation_mm}mm",
            "conseil": "Vérifiez le drainage de vos pots et jardinières.",
            "precipitation": precipitation_mm,
        }


def detect_vent_fort_alert(wind_speed: float) -> dict | None:
    """
    Détecte une alerte vent fort.

    Args:
        wind_speed: Vitesse du vent en km/h

    Returns:
        Dict avec niveau et message, ou None si pas d'alerte
    """
    if wind_speed < SEUIL_VENT_FORT:
        return None

    if wind_speed >= SEUIL_VENT_TEMPETE:
        return {
            "niveau": "danger",
            "message": f"Tempête: rafales à {wind_speed} km/h",
            "conseil": "Rentrez tous les objets légers. Attachez les plantes hautes aux tuteurs.",
            "vent": wind_speed,
        }
    else:
        return {
            "niveau": "attention",
            "message": f"Vent fort: {wind_speed} km/h",
            "conseil": "Vérifiez les tuteurs et les protections des plantes grimpantes.",
            "vent": wind_speed,
        }


def detect_uv_alert(uv_index: int) -> dict | None:
    """
    Détecte une alerte UV élevé (risque pour les plantes sensibles).

    Args:
        uv_index: Index UV (0-11+)

    Returns:
        Dict avec niveau et message, ou None si pas d'alerte
    """
    if uv_index < SEUIL_UV_ELEVE:
        return None

    if uv_index >= SEUIL_UV_EXTREME:
        return {
            "niveau": "danger",
            "message": f"UV extrême: index {uv_index}",
            "conseil": "Ombragez les jeunes plants et les plantes délicates. Évitez tout travail au jardin aux heures chaudes.",
            "uv": uv_index,
        }
    else:
        return {
            "niveau": "attention",
            "message": f"UV élevé: index {uv_index}",
            "conseil": "Les plantes à feuillage délicat peuvent souffrir. Privilégiez l'arrosage tôt le matin.",
            "uv": uv_index,
        }


def detect_all_alerts(prevision: dict) -> list[dict]:
    """
    Détecte toutes les alertes pour une prévision météo.

    Args:
        prevision: Dict avec temp_min, temp_max, precipitation_mm, vent_km_h, uv_index

    Returns:
        Liste des alertes détectées
    """
    alertes = []

    # Gel
    if "temp_min" in prevision or "temperature_min" in prevision:
        temp_min = prevision.get("temp_min") or prevision.get("temperature_min")
        if temp_min is not None:
            alerte = detect_gel_alert(temp_min)
            if alerte:
                alerte["type"] = "gel"
                alertes.append(alerte)

    # Canicule
    if "temp_max" in prevision or "temperature_max" in prevision:
        temp_max = prevision.get("temp_max") or prevision.get("temperature_max")
        if temp_max is not None:
            alerte = detect_canicule_alert(temp_max)
            if alerte:
                alerte["type"] = "canicule"
                alertes.append(alerte)

    # Pluie forte
    if "precipitation_mm" in prevision:
        alerte = detect_pluie_forte_alert(prevision["precipitation_mm"])
        if alerte:
            alerte["type"] = "pluie_forte"
            alertes.append(alerte)

    # Vent fort
    if "vent_km_h" in prevision:
        alerte = detect_vent_fort_alert(prevision["vent_km_h"])
        if alerte:
            alerte["type"] = "vent_fort"
            alertes.append(alerte)

    # UV
    if "uv_index" in prevision:
        alerte = detect_uv_alert(prevision["uv_index"])
        if alerte:
            alerte["type"] = "uv"
            alertes.append(alerte)

    return alertes


# ═══════════════════════════════════════════════════════════
# CALCUL ARROSAGE INTELLIGENT
# ═══════════════════════════════════════════════════════════


def calculate_watering_need(
    temp_max: float,
    precipitation_mm: float,
    wind_speed: float,
    humidity: int = 50,
    weathercode: int | None = None,
    jours_sans_pluie: int = 0,
) -> dict:
    """
    Calcule le besoin d'arrosage basé sur les conditions météo.

    Args:
        temp_max: Température maximale en °C
        precipitation_mm: Précipitations prévues en mm
        wind_speed: Vitesse du vent en km/h
        humidity: Humidité relative en %
        weathercode: Code météo WMO
        jours_sans_pluie: Nombre de jours consécutifs sans pluie

    Returns:
        Dict avec besoin, quantite_litres, raison
    """
    # Base: pas d'arrosage si pluie significative
    if precipitation_mm >= 5:
        return {
            "besoin": False,
            "quantite_litres": 0.0,
            "raison": f"Pluie prévue ({precipitation_mm}mm), pas d'arrosage nécessaire",
            "priorite": 0,
        }

    # Calcul du besoin de base (litres par m²)
    besoin_base = 3.0  # litres/m² en conditions normales

    # Ajustements
    facteur = 1.0
    raisons = []

    # Température
    if temp_max >= 35:
        facteur += 0.5
        raisons.append("très chaud")
    elif temp_max >= 30:
        facteur += 0.3
        raisons.append("chaud")
    elif temp_max < 15:
        facteur -= 0.3
        raisons.append("frais")

    # Vent (augmente l'évaporation)
    if wind_speed >= 30:
        facteur += 0.2
        raisons.append("venteux")

    # Humidité (faible = plus d'évaporation)
    if humidity < 40:
        facteur += 0.2
        raisons.append("air sec")
    elif humidity > 70:
        facteur -= 0.2
        raisons.append("air humide")

    # Jours sans pluie
    if jours_sans_pluie >= 5:
        facteur += 0.3
        raisons.append(f"{jours_sans_pluie} jours sans pluie")
    elif jours_sans_pluie >= 3:
        facteur += 0.1

    # Facteur météo (si code météo fourni)
    if weathercode is not None:
        facteur *= get_arrosage_factor(weathercode)

    # Précipitations faibles réduisent le besoin
    if 0 < precipitation_mm < 5:
        facteur -= precipitation_mm / 10
        raisons.append(f"pluie légère prévue ({precipitation_mm}mm)")

    # Calcul final
    facteur = max(0.0, min(2.0, facteur))  # Limiter entre 0 et 2
    quantite = round(besoin_base * facteur, 1)

    # Construire la raison
    if raisons:
        raison = "Arrosage recommandé: " + ", ".join(raisons)
    else:
        raison = "Arrosage normal recommandé"

    # Priorité (1=haute, 3=basse)
    if facteur >= 1.5:
        priorite = 1
    elif facteur >= 1.0:
        priorite = 2
    else:
        priorite = 3

    return {
        "besoin": facteur > 0.2,
        "quantite_litres": quantite,
        "raison": raison,
        "facteur": facteur,
        "priorite": priorite,
    }


def detect_drought_risk(previsions: list[dict], seuil_pluie_mm: float = 2.0) -> tuple[bool, int]:
    """
    Détecte le risque de sécheresse sur une période.

    Args:
        previsions: Liste de prévisions météo
        seuil_pluie_mm: Seuil de pluie significative

    Returns:
        Tuple (risque_secheresse, jours_sans_pluie_prevus)
    """
    jours_sans_pluie = 0

    for prev in previsions:
        precipitation = prev.get("precipitation_mm", 0)
        if precipitation < seuil_pluie_mm:
            jours_sans_pluie += 1
        else:
            break  # Pluie prévue, on arrête de compter

    risque = jours_sans_pluie >= SEUIL_SECHERESSE_JOURS

    return risque, jours_sans_pluie


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
                "icone": "â˜€ï¸",
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


# ═══════════════════════════════════════════════════════════
# PARSING DE DONNÉES API
# ═══════════════════════════════════════════════════════════


def parse_open_meteo_daily(data: dict) -> list[dict]:
    """
    Parse les données daily de l'API Open-Meteo.

    Args:
        data: Réponse JSON de l'API

    Returns:
        Liste de dict avec les données formatées
    """
    daily = data.get("daily", {})
    dates = daily.get("time", [])

    previsions = []

    for i, date_str in enumerate(dates):
        temp_min = _safe_get_index(daily, "temperature_2m_min", i)
        temp_max = _safe_get_index(daily, "temperature_2m_max", i)

        prev = {
            "date": date_str,
            "temperature_min": temp_min,
            "temperature_max": temp_max,
            "temperature_moyenne": calculate_average_temperature(temp_min or 15, temp_max or 25),
            "precipitation_mm": _safe_get_index(daily, "precipitation_sum", i) or 0,
            "probabilite_pluie": _safe_get_index(daily, "precipitation_probability_max", i) or 0,
            "vent_km_h": _safe_get_index(daily, "wind_speed_10m_max", i) or 0,
            "direction_vent": direction_from_degrees(
                _safe_get_index(daily, "wind_direction_10m_dominant", i)
            ),
            "uv_index": _safe_get_index(daily, "uv_index_max", i) or 0,
            "weathercode": _safe_get_index(daily, "weathercode", i),
        }

        # Ajouter condition et icône
        prev["condition"] = weathercode_to_condition(prev["weathercode"])
        prev["icone"] = weathercode_to_icon(prev["weathercode"])

        # Lever/coucher du soleil
        sunrise = _safe_get_index(daily, "sunrise", i)
        sunset = _safe_get_index(daily, "sunset", i)

        if sunrise and "T" in sunrise:
            prev["lever_soleil"] = sunrise.split("T")[1]
        if sunset and "T" in sunset:
            prev["coucher_soleil"] = sunset.split("T")[1]

        previsions.append(prev)

    return previsions


def _safe_get_index(data: dict, key: str, index: int, default=None) -> Any:
    """
    Récupère une valeur à un index de façon sécurisée.

    Args:
        data: Dictionnaire contenant les listes
        key: Clé de la liste
        index: Index à récupérer
        default: Valeur par défaut

    Returns:
        Valeur à l'index ou default
    """
    lst = data.get(key, [])
    if lst and 0 <= index < len(lst):
        return lst[index]
    return default


def validate_coordinates(latitude: float, longitude: float) -> tuple[bool, str]:
    """
    Valide des coordonnées GPS.

    Args:
        latitude: Latitude (-90 à 90)
        longitude: Longitude (-180 à 180)

    Returns:
        Tuple (valide, message_erreur)
    """
    if not isinstance(latitude, (int, float)):
        return False, "La latitude doit être un nombre"

    if not isinstance(longitude, (int, float)):
        return False, "La longitude doit être un nombre"

    if latitude < -90 or latitude > 90:
        return False, f"Latitude invalide: {latitude} (doit être entre -90 et 90)"

    if longitude < -180 or longitude > 180:
        return False, f"Longitude invalide: {longitude} (doit être entre -180 et 180)"

    return True, ""
