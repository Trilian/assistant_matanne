"""
Calcul d'arrosage intelligent et détection de risque de sécheresse.

Détermine les besoins d'arrosage en fonction des conditions météo
et détecte les périodes de sécheresse prolongée.
"""

from .weather_codes import SEUIL_SECHERESSE_JOURS, get_arrosage_factor

__all__ = [
    "calculate_watering_need",
    "detect_drought_risk",
]


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
