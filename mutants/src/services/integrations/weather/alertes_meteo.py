"""
Calculs de températures et détection d'alertes météo.

Contient les fonctions de conversion de températures, le calcul du ressenti
et toutes les fonctions de détection d'alertes (gel, canicule, pluie, vent, UV).
"""

from .weather_codes import (
    SEUIL_CANICULE,
    SEUIL_CANICULE_SEVERE,
    SEUIL_GEL,
    SEUIL_GEL_SEVERE,
    SEUIL_PLUIE_FORTE,
    SEUIL_PLUIE_VIOLENTE,
    SEUIL_UV_ELEVE,
    SEUIL_UV_EXTREME,
    SEUIL_VENT_FORT,
    SEUIL_VENT_TEMPETE,
)

__all__ = [
    # Températures
    "calculate_average_temperature",
    "calculate_temperature_amplitude",
    "celsius_to_fahrenheit",
    "fahrenheit_to_celsius",
    "calculate_feels_like",
    # Alertes
    "detect_gel_alert",
    "detect_canicule_alert",
    "detect_pluie_forte_alert",
    "detect_vent_fort_alert",
    "detect_uv_alert",
    "detect_all_alerts",
]


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
