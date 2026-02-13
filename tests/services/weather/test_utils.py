"""
Tests pour src/services/weather/utils.py

Couvre les fonctions utilitaires pures du service météo.
"""

from datetime import date, datetime

from src.services.weather.utils import (
    DIRECTIONS_CARDINALES,
    SEUIL_CANICULE,
    SEUIL_CANICULE_SEVERE,
    # Constantes
    SEUIL_GEL,
    SEUIL_GEL_SEVERE,
    SEUIL_PLUIE_FORTE,
    SEUIL_PLUIE_VIOLENTE,
    SEUIL_SECHERESSE_JOURS,
    SEUIL_UV_ELEVE,
    SEUIL_UV_EXTREME,
    SEUIL_VENT_FORT,
    SEUIL_VENT_TEMPETE,
    WEATHERCODES,
    _safe_get_index,
    # Températures
    calculate_average_temperature,
    calculate_feels_like,
    calculate_temperature_amplitude,
    # Arrosage
    calculate_watering_need,
    celsius_to_fahrenheit,
    degrees_from_direction,
    detect_all_alerts,
    detect_canicule_alert,
    detect_drought_risk,
    # Alertes
    detect_gel_alert,
    detect_pluie_forte_alert,
    detect_uv_alert,
    detect_vent_fort_alert,
    # Conversions
    direction_from_degrees,
    fahrenheit_to_celsius,
    format_weather_summary,
    get_arrosage_factor,
    get_gardening_advice_for_weather,
    # Conseils
    get_season,
    # Parsing
    parse_open_meteo_daily,
    validate_coordinates,
    weathercode_to_condition,
    weathercode_to_icon,
)

# ═══════════════════════════════════════════════════════════
# TESTS CONSTANTES
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests des constantes météo."""

    def test_seuils_definis(self):
        """Vérifie que les seuils sont définis."""
        assert SEUIL_GEL == 2.0
        assert SEUIL_GEL_SEVERE == 0.0
        assert SEUIL_CANICULE == 35.0
        assert SEUIL_CANICULE_SEVERE == 40.0
        assert SEUIL_PLUIE_FORTE == 20.0
        assert SEUIL_PLUIE_VIOLENTE == 50.0
        assert SEUIL_VENT_FORT == 50.0
        assert SEUIL_VENT_TEMPETE == 80.0
        assert SEUIL_UV_ELEVE == 6
        assert SEUIL_UV_EXTREME == 10
        assert SEUIL_SECHERESSE_JOURS == 7

    def test_directions_cardinales(self):
        """Vérifie les directions cardinales."""
        assert len(DIRECTIONS_CARDINALES) == 8
        assert "N" in DIRECTIONS_CARDINALES
        assert "E" in DIRECTIONS_CARDINALES
        assert "S" in DIRECTIONS_CARDINALES
        assert "O" in DIRECTIONS_CARDINALES

    def test_weathercodes_structure(self):
        """Vérifie la structure des codes météo."""
        # Code 0 = Ensoleillé
        assert 0 in WEATHERCODES
        assert "condition" in WEATHERCODES[0]
        assert "icon" in WEATHERCODES[0]
        assert "arrosage_factor" in WEATHERCODES[0]

        # Vérifie quelques codes importants
        assert 95 in WEATHERCODES  # Orage
        assert 65 in WEATHERCODES  # Pluie forte


# ═══════════════════════════════════════════════════════════
# TESTS CONVERSIONS
# ═══════════════════════════════════════════════════════════


class TestDirectionFromDegrees:
    """Tests de la fonction direction_from_degrees."""

    def test_nord(self):
        """0° = Nord."""
        assert direction_from_degrees(0) == "N"
        assert direction_from_degrees(360) == "N"

    def test_est(self):
        """90° = Est."""
        assert direction_from_degrees(90) == "E"

    def test_sud(self):
        """180° = Sud."""
        assert direction_from_degrees(180) == "S"

    def test_ouest(self):
        """270° = Ouest."""
        assert direction_from_degrees(270) == "O"

    def test_nord_est(self):
        """45° = Nord-Est."""
        assert direction_from_degrees(45) == "NE"

    def test_sud_ouest(self):
        """225° = Sud-Ouest."""
        assert direction_from_degrees(225) == "SO"

    def test_valeurs_limites(self):
        """Test valeurs aux frontières."""
        # Autour de Est (90°) - 8 directions = 45° chacune
        # 67° / 45 = 1.49 â†’ arrondi 1 = NE
        assert direction_from_degrees(67) == "NE"
        # 112° / 45 = 2.49 â†’ arrondi 2 = E
        assert direction_from_degrees(112) == "E"

    def test_negatif_normalise(self):
        """Test avec valeurs négatives."""
        assert direction_from_degrees(-90) == "O"  # -90 % 360 = 270

    def test_none_retourne_vide(self):
        """None retourne chaîne vide."""
        assert direction_from_degrees(None) == ""


class TestDegreesFromDirection:
    """Tests de la fonction degrees_from_direction."""

    def test_nord(self):
        """Nord = 0°."""
        assert degrees_from_direction("N") == 0.0

    def test_est(self):
        """Est = 90°."""
        assert degrees_from_direction("E") == 90.0

    def test_sud(self):
        """Sud = 180°."""
        assert degrees_from_direction("S") == 180.0

    def test_ouest(self):
        """Ouest = 270°."""
        assert degrees_from_direction("O") == 270.0

    def test_nord_est(self):
        """Nord-Est = 45°."""
        assert degrees_from_direction("NE") == 45.0

    def test_minuscule_accepte(self):
        """Direction en minuscules acceptée."""
        assert degrees_from_direction("ne") == 45.0
        assert degrees_from_direction("so") == 225.0

    def test_espaces_trimes(self):
        """Espaces supprimés."""
        assert degrees_from_direction(" N ") == 0.0

    def test_invalide_retourne_none(self):
        """Direction invalide retourne None."""
        assert degrees_from_direction("X") is None
        assert degrees_from_direction("") is None
        assert degrees_from_direction("NORD") is None


class TestWeathercodeToCondition:
    """Tests de weathercode_to_condition."""

    def test_ensoleille(self):
        """Code 0 = Ensoleillé."""
        assert weathercode_to_condition(0) == "Ensoleillé"

    def test_pluie_moderee(self):
        """Code 63 = Pluie modérée."""
        assert weathercode_to_condition(63) == "Pluie modérée"

    def test_orage(self):
        """Code 95 = Orage."""
        assert weathercode_to_condition(95) == "Orage"

    def test_code_inconnu(self):
        """Code inconnu retourne 'Inconnu'."""
        assert weathercode_to_condition(999) == "Inconnu"

    def test_none_retourne_inconnu(self):
        """None retourne 'Inconnu'."""
        assert weathercode_to_condition(None) == "Inconnu"


class TestWeathercodeToIcon:
    """Tests de weathercode_to_icon."""

    def test_ensoleille(self):
        """Code 0 = â˜€ï¸."""
        assert weathercode_to_icon(0) == "â˜€ï¸"

    def test_orage(self):
        """Code 95 = â›ˆï¸."""
        assert weathercode_to_icon(95) == "â›ˆï¸"

    def test_neige(self):
        """Code 73 = â„ï¸."""
        assert weathercode_to_icon(73) == "â„ï¸"

    def test_code_inconnu(self):
        """Code inconnu retourne emoji par défaut."""
        assert weathercode_to_icon(999) == "ðŸŒ¡ï¸"

    def test_none_retourne_question(self):
        """None retourne â“."""
        assert weathercode_to_icon(None) == "â“"


class TestGetArrosageFactor:
    """Tests de get_arrosage_factor."""

    def test_ensoleille_augmente(self):
        """Soleil augmente besoin arrosage."""
        assert get_arrosage_factor(0) == 1.2

    def test_couvert_reduit(self):
        """Couvert réduit besoin arrosage."""
        assert get_arrosage_factor(3) == 0.8

    def test_pluie_forte_zero(self):
        """Pluie forte = pas d'arrosage."""
        assert get_arrosage_factor(65) == 0.0

    def test_code_inconnu_normal(self):
        """Code inconnu = facteur normal."""
        assert get_arrosage_factor(999) == 1.0

    def test_none_normal(self):
        """None = facteur normal."""
        assert get_arrosage_factor(None) == 1.0


# ═══════════════════════════════════════════════════════════
# TESTS TEMPÉRATURES
# ═══════════════════════════════════════════════════════════


class TestCalculateAverageTemperature:
    """Tests de calculate_average_temperature."""

    def test_moyenne_simple(self):
        """Moyenne de deux valeurs."""
        assert calculate_average_temperature(10, 20) == 15.0

    def test_negatives(self):
        """Avec valeurs négatives."""
        assert calculate_average_temperature(-5, 5) == 0.0

    def test_identiques(self):
        """Valeurs identiques."""
        assert calculate_average_temperature(15, 15) == 15.0


class TestCalculateTemperatureAmplitude:
    """Tests de calculate_temperature_amplitude."""

    def test_amplitude_positive(self):
        """Amplitude normale."""
        assert calculate_temperature_amplitude(10, 20) == 10.0

    def test_amplitude_inversee(self):
        """Amplitude avec valeurs inversées."""
        assert calculate_temperature_amplitude(20, 10) == 10.0

    def test_amplitude_zero(self):
        """Pas d'amplitude."""
        assert calculate_temperature_amplitude(15, 15) == 0.0


class TestCelsiusToFahrenheit:
    """Tests de celsius_to_fahrenheit."""

    def test_zero_celsius(self):
        """0°C = 32°F."""
        assert celsius_to_fahrenheit(0) == 32

    def test_cent_celsius(self):
        """100°C = 212°F."""
        assert celsius_to_fahrenheit(100) == 212

    def test_negatif(self):
        """-40°C = -40°F (point d'intersection)."""
        assert celsius_to_fahrenheit(-40) == -40


class TestFahrenheitToCelsius:
    """Tests de fahrenheit_to_celsius."""

    def test_32_fahrenheit(self):
        """32°F = 0°C."""
        assert fahrenheit_to_celsius(32) == 0

    def test_212_fahrenheit(self):
        """212°F = 100°C."""
        assert fahrenheit_to_celsius(212) == 100

    def test_negatif(self):
        """-40°F = -40°C."""
        assert fahrenheit_to_celsius(-40) == -40


class TestCalculateFeelsLike:
    """Tests de calculate_feels_like."""

    def test_froid_venteux(self):
        """Froid avec vent = température ressentie plus basse."""
        feels_like = calculate_feels_like(5, 50, 30)
        assert feels_like < 5  # Refroidissement éolien

    def test_chaud_humide(self):
        """Chaud avec humidité = température ressentie plus haute."""
        feels_like = calculate_feels_like(30, 80, 5)
        assert feels_like > 30  # Chaleur ressentie

    def test_conditions_normales(self):
        """Conditions modérées = température réelle."""
        feels_like = calculate_feels_like(15, 50, 10)
        assert feels_like == 15.0

    def test_froid_sans_vent(self):
        """Froid sans vent = température réelle."""
        feels_like = calculate_feels_like(5, 50, 2)  # Vent < 5 km/h
        assert feels_like == 5.0


# ═══════════════════════════════════════════════════════════
# TESTS ALERTES
# ═══════════════════════════════════════════════════════════


class TestDetectGelAlert:
    """Tests de detect_gel_alert."""

    def test_gel_severe(self):
        """Gel sévère sous 0°C."""
        alerte = detect_gel_alert(-2)
        assert alerte is not None
        assert alerte["niveau"] == "danger"
        assert alerte["temperature"] == -2

    def test_risque_gel(self):
        """Risque de gel entre 0 et 2°C."""
        alerte = detect_gel_alert(1)
        assert alerte is not None
        assert alerte["niveau"] == "attention"

    def test_pas_dalerte(self):
        """Pas d'alerte au-dessus de 2°C."""
        alerte = detect_gel_alert(5)
        assert alerte is None

    def test_seuil_exact(self):
        """Test au seuil exact."""
        alerte = detect_gel_alert(SEUIL_GEL)  # 2.0
        assert alerte is not None


class TestDetectCaniculeAlert:
    """Tests de detect_canicule_alert."""

    def test_canicule_extreme(self):
        """Canicule extrême >= 40°C."""
        alerte = detect_canicule_alert(42)
        assert alerte is not None
        assert alerte["niveau"] == "danger"

    def test_forte_chaleur(self):
        """Forte chaleur entre 35 et 40°C."""
        alerte = detect_canicule_alert(37)
        assert alerte is not None
        assert alerte["niveau"] == "attention"

    def test_pas_dalerte(self):
        """Pas d'alerte sous 35°C."""
        alerte = detect_canicule_alert(30)
        assert alerte is None


class TestDetectPluieForteAlert:
    """Tests de detect_pluie_forte_alert."""

    def test_pluie_violente(self):
        """Pluie violente >= 50mm."""
        alerte = detect_pluie_forte_alert(60)
        assert alerte is not None
        assert alerte["niveau"] == "danger"

    def test_pluie_forte(self):
        """Pluie forte entre 20 et 50mm."""
        alerte = detect_pluie_forte_alert(30)
        assert alerte is not None
        assert alerte["niveau"] == "attention"

    def test_pas_dalerte(self):
        """Pas d'alerte sous 20mm."""
        alerte = detect_pluie_forte_alert(10)
        assert alerte is None


class TestDetectVentFortAlert:
    """Tests de detect_vent_fort_alert."""

    def test_tempete(self):
        """Tempête >= 80 km/h."""
        alerte = detect_vent_fort_alert(90)
        assert alerte is not None
        assert alerte["niveau"] == "danger"

    def test_vent_fort(self):
        """Vent fort entre 50 et 80 km/h."""
        alerte = detect_vent_fort_alert(60)
        assert alerte is not None
        assert alerte["niveau"] == "attention"

    def test_pas_dalerte(self):
        """Pas d'alerte sous 50 km/h."""
        alerte = detect_vent_fort_alert(30)
        assert alerte is None


class TestDetectUVAlert:
    """Tests de detect_uv_alert."""

    def test_uv_extreme(self):
        """UV extrême >= 10."""
        alerte = detect_uv_alert(11)
        assert alerte is not None
        assert alerte["niveau"] == "danger"

    def test_uv_eleve(self):
        """UV élevé entre 6 et 10."""
        alerte = detect_uv_alert(7)
        assert alerte is not None
        assert alerte["niveau"] == "attention"

    def test_pas_dalerte(self):
        """Pas d'alerte sous 6."""
        alerte = detect_uv_alert(4)
        assert alerte is None


class TestDetectAllAlerts:
    """Tests de detect_all_alerts."""

    def test_toutes_alertes(self):
        """Détecte toutes les alertes présentes."""
        prevision = {
            "temp_min": -5,  # Gel
            "temp_max": 40,  # Canicule
            "precipitation_mm": 60,  # Pluie violente
            "vent_km_h": 90,  # Tempête
            "uv_index": 11,  # UV extrême
        }
        alertes = detect_all_alerts(prevision)
        assert len(alertes) == 5

        types = [a["type"] for a in alertes]
        assert "gel" in types
        assert "canicule" in types
        assert "pluie_forte" in types
        assert "vent_fort" in types
        assert "uv" in types

    def test_aucune_alerte(self):
        """Aucune alerte avec bonnes conditions."""
        prevision = {
            "temp_min": 10,
            "temp_max": 25,
            "precipitation_mm": 5,
            "vent_km_h": 20,
            "uv_index": 3,
        }
        alertes = detect_all_alerts(prevision)
        assert len(alertes) == 0

    def test_alternative_keys(self):
        """Supporte les clés alternatives (temperature_min/max)."""
        prevision = {
            "temperature_min": -2,  # Format alternatif
            "temperature_max": 37,  # Format alternatif
        }
        alertes = detect_all_alerts(prevision)
        types = [a["type"] for a in alertes]
        assert "gel" in types
        assert "canicule" in types


# ═══════════════════════════════════════════════════════════
# TESTS ARROSAGE
# ═══════════════════════════════════════════════════════════


class TestCalculateWateringNeed:
    """Tests de calculate_watering_need."""

    def test_pluie_significative_pas_arrosage(self):
        """Pas d'arrosage si pluie >= 5mm."""
        result = calculate_watering_need(25, 10, 10)
        assert result["besoin"] is False
        assert result["quantite_litres"] == 0.0

    def test_canicule_augmente_besoin(self):
        """Canicule augmente le besoin."""
        result = calculate_watering_need(38, 0, 10)
        assert result["besoin"] is True
        assert result["facteur"] > 1.0
        assert "très chaud" in result["raison"]

    def test_vent_augmente_besoin(self):
        """Vent fort augmente le besoin."""
        result = calculate_watering_need(25, 0, 40)
        assert "venteux" in result["raison"]

    def test_air_sec_augmente_besoin(self):
        """Air sec augmente le besoin."""
        result = calculate_watering_need(25, 0, 10, humidity=30)
        assert "air sec" in result["raison"]

    def test_air_humide_reduit_besoin(self):
        """Air humide réduit le besoin."""
        result = calculate_watering_need(25, 0, 10, humidity=80)
        assert "air humide" in result["raison"]

    def test_jours_sans_pluie_augmente_besoin(self):
        """Jours sans pluie augmente le besoin."""
        result = calculate_watering_need(25, 0, 10, jours_sans_pluie=6)
        assert result["facteur"] > 1.0

    def test_weathercode_modifie_facteur(self):
        """Weathercode modifie le facteur."""
        # Code 65 = pluie forte, facteur 0.0
        result = calculate_watering_need(25, 0, 10, weathercode=65)
        assert result["quantite_litres"] == 0.0

    def test_priorite_haute_si_facteur_eleve(self):
        """Priorité haute si facteur >= 1.5."""
        result = calculate_watering_need(40, 0, 40, humidity=20, jours_sans_pluie=7)
        assert result["priorite"] == 1

    def test_frais_reduit_besoin(self):
        """Température fraîche réduit le besoin."""
        result = calculate_watering_need(10, 0, 10)
        assert "frais" in result["raison"]


class TestDetectDroughtRisk:
    """Tests de detect_drought_risk."""

    def test_secheresse_detectee(self):
        """Sécheresse si >= 7 jours sans pluie."""
        previsions = [{"precipitation_mm": 0}] * 10
        risque, jours = detect_drought_risk(previsions)
        assert risque is True
        assert jours == 10

    def test_pas_de_secheresse(self):
        """Pas de sécheresse si pluie prévue."""
        previsions = [{"precipitation_mm": 0}] * 3 + [{"precipitation_mm": 10}]
        risque, jours = detect_drought_risk(previsions)
        assert risque is False
        assert jours == 3

    def test_seuil_personnalise(self):
        """Seuil de pluie personnalisable."""
        previsions = [{"precipitation_mm": 1}] * 5
        # Avec seuil 2mm, 1mm n'est pas significatif
        risque, jours = detect_drought_risk(previsions, seuil_pluie_mm=2.0)
        assert jours == 5


# ═══════════════════════════════════════════════════════════
# TESTS CONSEILS
# ═══════════════════════════════════════════════════════════


class TestGetSeason:
    """Tests de get_season."""

    def test_printemps(self):
        """Mars, Avril, Mai = printemps."""
        assert get_season(date(2025, 3, 15)) == "printemps"
        assert get_season(date(2025, 4, 15)) == "printemps"
        assert get_season(date(2025, 5, 15)) == "printemps"

    def test_ete(self):
        """Juin, Juillet, Août = été."""
        assert get_season(date(2025, 6, 15)) == "été"
        assert get_season(date(2025, 7, 15)) == "été"
        assert get_season(date(2025, 8, 15)) == "été"

    def test_automne(self):
        """Septembre, Octobre, Novembre = automne."""
        assert get_season(date(2025, 9, 15)) == "automne"
        assert get_season(date(2025, 10, 15)) == "automne"
        assert get_season(date(2025, 11, 15)) == "automne"

    def test_hiver(self):
        """Décembre, Janvier, Février = hiver."""
        assert get_season(date(2025, 12, 15)) == "hiver"
        assert get_season(date(2025, 1, 15)) == "hiver"
        assert get_season(date(2025, 2, 15)) == "hiver"

    def test_datetime_accepte(self):
        """Accepte datetime en plus de date."""
        assert get_season(datetime(2025, 6, 15, 12, 0)) == "été"

    def test_none_utilise_aujourdhui(self):
        """None utilise la date d'aujourd'hui."""
        saison = get_season(None)
        assert saison in ["printemps", "été", "automne", "hiver"]


class TestGetGardeningAdviceForWeather:
    """Tests de get_gardening_advice_for_weather."""

    def test_canicule_conseils(self):
        """Conseils en cas de canicule."""
        conseils = get_gardening_advice_for_weather("Ensoleillé", 35, 0)
        assert len(conseils) >= 2
        assert any("arrosage" in c["titre"].lower() for c in conseils)

    def test_gel_conseils(self):
        """Conseils en cas de gel."""
        conseils = get_gardening_advice_for_weather("Nuageux", 2, 0)
        assert any("protection" in c["titre"].lower() for c in conseils)

    def test_pluie_forte_conseils(self):
        """Conseils en cas de forte pluie."""
        conseils = get_gardening_advice_for_weather("Pluvieux", 15, 40)
        assert any("drainage" in c["titre"].lower() for c in conseils)

    def test_orage_conseils(self):
        """Conseils en cas d'orage."""
        conseils = get_gardening_advice_for_weather("Orage prévu", 20, 10)
        assert any("orage" in c["titre"].lower() for c in conseils)

    def test_ensoleille_conseils(self):
        """Conseils pour journée ensoleillée."""
        conseils = get_gardening_advice_for_weather("Ensoleillé", 22, 0)
        assert any("idéale" in c["titre"].lower() for c in conseils)

    def test_conseils_tries_par_priorite(self):
        """Conseils triés par priorité."""
        conseils = get_gardening_advice_for_weather("Ensoleillé", 35, 0)
        if len(conseils) >= 2:
            assert conseils[0]["priorite"] <= conseils[-1]["priorite"]


# ═══════════════════════════════════════════════════════════
# TESTS PARSING
# ═══════════════════════════════════════════════════════════


class TestFormatWeatherSummary:
    """Tests de format_weather_summary."""

    def test_summary_avec_pluie(self):
        """Résumé avec précipitations."""
        previsions = [
            {"temp_min": 10, "temp_max": 20, "precipitation_mm": 5},
            {"temp_min": 12, "temp_max": 22, "precipitation_mm": 10},
        ]
        summary = format_weather_summary(previsions)
        assert "2 jours" in summary
        assert "15mm" in summary  # Total précipitations
        assert "10°C" in summary  # Min
        assert "22°C" in summary  # Max

    def test_summary_sans_pluie(self):
        """Résumé sans précipitations."""
        previsions = [{"temp_min": 15, "temp_max": 25, "precipitation_mm": 0}]
        summary = format_weather_summary(previsions)
        assert "Pas de pluie" in summary

    def test_summary_vide(self):
        """Résumé avec liste vide."""
        summary = format_weather_summary([])
        assert "Aucune prévision" in summary

    def test_format_alternatif_keys(self):
        """Supporte les clés alternatives."""
        previsions = [{"temperature_min": 10, "temperature_max": 20, "precipitation_mm": 0}]
        summary = format_weather_summary(previsions)
        assert "10°C" in summary


class TestParseOpenMeteoDaily:
    """Tests de parse_open_meteo_daily."""

    def test_parse_complet(self):
        """Parse une réponse API complète."""
        data = {
            "daily": {
                "time": ["2025-01-15", "2025-01-16"],
                "temperature_2m_min": [5, 7],
                "temperature_2m_max": [15, 17],
                "precipitation_sum": [0, 5],
                "precipitation_probability_max": [10, 60],
                "wind_speed_10m_max": [20, 30],
                "wind_direction_10m_dominant": [180, 270],
                "uv_index_max": [3, 5],
                "weathercode": [0, 63],
                "sunrise": ["2025-01-15T07:30", "2025-01-16T07:29"],
                "sunset": ["2025-01-15T17:30", "2025-01-16T17:31"],
            }
        }
        previsions = parse_open_meteo_daily(data)

        assert len(previsions) == 2

        # Premier jour
        p1 = previsions[0]
        assert p1["date"] == "2025-01-15"
        assert p1["temperature_min"] == 5
        assert p1["temperature_max"] == 15
        assert p1["temperature_moyenne"] == 10.0
        assert p1["precipitation_mm"] == 0
        assert p1["direction_vent"] == "S"
        assert p1["condition"] == "Ensoleillé"
        assert p1["lever_soleil"] == "07:30"

        # Deuxième jour
        p2 = previsions[1]
        assert p2["condition"] == "Pluie modérée"
        assert p2["direction_vent"] == "O"

    def test_parse_donnees_manquantes(self):
        """Gère les données manquantes."""
        data = {"daily": {"time": ["2025-01-15"]}}
        previsions = parse_open_meteo_daily(data)

        assert len(previsions) == 1
        assert previsions[0]["precipitation_mm"] == 0
        assert previsions[0]["vent_km_h"] == 0

    def test_parse_vide(self):
        """Gère réponse vide."""
        previsions = parse_open_meteo_daily({})
        assert previsions == []


class TestSafeGetIndex:
    """Tests de _safe_get_index."""

    def test_acces_valide(self):
        """Accès à un index valide."""
        data = {"values": [10, 20, 30]}
        assert _safe_get_index(data, "values", 1) == 20

    def test_index_hors_limites(self):
        """Index hors limites retourne default."""
        data = {"values": [10, 20]}
        assert _safe_get_index(data, "values", 5) is None
        assert _safe_get_index(data, "values", 5, default=0) == 0

    def test_cle_manquante(self):
        """Clé manquante retourne default."""
        data = {}
        assert _safe_get_index(data, "values", 0) is None

    def test_liste_vide(self):
        """Liste vide retourne default."""
        data = {"values": []}
        assert _safe_get_index(data, "values", 0) is None


class TestValidateCoordinates:
    """Tests de validate_coordinates."""

    def test_coordonnees_valides(self):
        """Coordonnées valides."""
        valide, msg = validate_coordinates(48.8566, 2.3522)
        assert valide is True
        assert msg == ""

    def test_latitude_invalide_haute(self):
        """Latitude > 90 invalide."""
        valide, msg = validate_coordinates(100, 0)
        assert valide is False
        assert "Latitude invalide" in msg

    def test_latitude_invalide_basse(self):
        """Latitude < -90 invalide."""
        valide, msg = validate_coordinates(-100, 0)
        assert valide is False

    def test_longitude_invalide(self):
        """Longitude invalide."""
        valide, msg = validate_coordinates(0, 200)
        assert valide is False
        assert "Longitude invalide" in msg

    def test_latitude_non_numerique(self):
        """Latitude non numérique."""
        valide, msg = validate_coordinates("abc", 0)
        assert valide is False
        assert "nombre" in msg

    def test_longitude_non_numerique(self):
        """Longitude non numérique."""
        valide, msg = validate_coordinates(0, "xyz")
        assert valide is False
        assert "nombre" in msg

    def test_limites_exactes(self):
        """Coordonnées aux limites exactes."""
        valide, _ = validate_coordinates(90, 180)
        assert valide is True
        valide, _ = validate_coordinates(-90, -180)
        assert valide is True
