"""
Tests pour src/services/garmin/utils.py

Couvre:
- Parsing des données Garmin
- Conversion des unités
- Formatage des durées/distances
- Calculs statistiques
- Validation des configurations
"""

from datetime import date, datetime, timedelta

from src.services.garmin.utils import (
    build_api_params,
    calculate_activity_stats,
    calculate_daily_stats,
    calculate_goal_progress,
    calculate_streak,
    calculate_weekly_summary,
    date_to_garmin_timestamp,
    estimate_calories_burned,
    format_distance,
    format_duration,
    format_pace,
    format_speed,
    get_activity_icon,
    get_streak_badge,
    get_sync_date_range,
    is_sync_needed,
    parse_activity_data,
    parse_daily_summary,
    parse_garmin_date,
    parse_garmin_timestamp,
    translate_activity_type,
    validate_garmin_token,
    validate_oauth_config,
)

# ═══════════════════════════════════════════════════════════
# TESTS PARSING DONNÉES API
# ═══════════════════════════════════════════════════════════


class TestParseGarminTimestamp:
    """Tests pour parse_garmin_timestamp."""

    def test_timestamp_valide(self):
        """Un timestamp valide retourne une datetime."""
        result = parse_garmin_timestamp(1700000000)
        assert result is not None
        assert isinstance(result, datetime)
        # 14 novembre 2023 à 22:13:20 UTC
        assert result.year == 2023
        assert result.month == 11
        assert result.day == 14

    def test_timestamp_float(self):
        """Un timestamp float est correctement converti."""
        result = parse_garmin_timestamp(1700000000.5)
        assert result is not None
        assert result.year == 2023

    def test_timestamp_none(self):
        """None retourne None."""
        result = parse_garmin_timestamp(None)
        assert result is None

    def test_timestamp_zero(self):
        """0 retourne None (falsy)."""
        result = parse_garmin_timestamp(0)
        assert result is None

    def test_timestamp_negatif(self):
        """Un timestamp négatif retourne None (système dépendant)."""
        result = parse_garmin_timestamp(-1)
        # Peut retourner datetime ou None selon l'OS
        # On vérifie juste qu'il n'y a pas d'exception
        assert result is None or isinstance(result, datetime)


class TestParseGarminDate:
    """Tests pour parse_garmin_date."""

    def test_date_valide(self):
        """Une date au format YYYY-MM-DD est correctement parsée."""
        result = parse_garmin_date("2024-01-15")
        assert result == date(2024, 1, 15)

    def test_date_avec_timestamp(self):
        """Une date avec partie heure est tronquée."""
        result = parse_garmin_date("2024-01-15T12:30:00")
        assert result == date(2024, 1, 15)

    def test_date_none(self):
        """None retourne None."""
        result = parse_garmin_date(None)
        assert result is None

    def test_date_vide(self):
        """Une chaîne vide retourne None."""
        result = parse_garmin_date("")
        assert result is None

    def test_date_invalide(self):
        """Une date invalide retourne None."""
        result = parse_garmin_date("not-a-date")
        assert result is None

    def test_date_format_incorrect(self):
        """Un format de date incorrect retourne None."""
        result = parse_garmin_date("15/01/2024")
        assert result is None


class TestParseActivityData:
    """Tests pour parse_activity_data."""

    def test_activite_complete(self):
        """Parsing d'une activité complète."""
        raw = {
            "activityId": "12345",
            "activityType": {"typeKey": "running"},
            "activityName": "Course matinale",
            "description": "Beau temps",
            "startTimeInSeconds": 1700000000,
            "durationInSeconds": 3600,
            "distanceInMeters": 10000,
            "activeKilocalories": 500,
            "averageHeartRateInBeatsPerMinute": 145,
            "maxHeartRateInBeatsPerMinute": 175,
            "averageSpeedInMetersPerSecond": 2.78,
            "totalElevationGainInMeters": 100,
        }

        result = parse_activity_data(raw)

        assert result["garmin_id"] == "12345"
        assert result["type_activite"] == "running"
        assert result["type_activite_fr"] == "course"
        assert result["nom"] == "Course matinale"
        assert result["description"] == "Beau temps"
        assert result["duree_secondes"] == 3600
        assert result["distance_metres"] == 10000
        assert result["calories"] == 500
        assert result["fc_moyenne"] == 145
        assert result["fc_max"] == 175
        assert result["vitesse_moyenne"] == 2.78
        assert result["elevation_gain"] == 100
        assert result["icon"] == "🏃"

    def test_activite_minimale(self):
        """Parsing d'une activité avec données minimales."""
        raw = {"activityId": "999"}

        result = parse_activity_data(raw)

        assert result["garmin_id"] == "999"
        assert result["type_activite"] == "other"
        assert result["duree_secondes"] == 1  # fallback minimum

    def test_activite_sans_id(self):
        """Parsing sans ID utilise fallback 'unknown'."""
        raw = {"activityName": "Test"}

        result = parse_activity_data(raw)

        assert result["garmin_id"] == "unknown"

    def test_activite_type_string(self):
        """Le type d'activité string est géré."""
        raw = {"activityId": "1", "activityType": "swimming"}

        result = parse_activity_data(raw)

        assert result["type_activite"] == "swimming"

    def test_activite_summary_id(self):
        """summaryId est utilisé si activityId absent."""
        raw = {"summaryId": "SUM123"}

        result = parse_activity_data(raw)

        assert result["garmin_id"] == "SUM123"


class TestParseDailySummary:
    """Tests pour parse_daily_summary."""

    def test_summary_complet(self):
        """Parsing d'un résumé complet."""
        raw = {
            "calendarDate": "2024-01-15",
            "steps": 12500,
            "distanceInMeters": 9500,
            "totalKilocalories": 2200,
            "activeKilocalories": 450,
            "moderateIntensityMinutes": 30,
            "vigorousIntensityMinutes": 15,
            "restingHeartRateInBeatsPerMinute": 58,
            "minHeartRateInBeatsPerMinute": 52,
            "maxHeartRateInBeatsPerMinute": 165,
            "averageStressLevel": 35,
            "bodyBatteryChargedValue": 95,
            "bodyBatteryDrainedValue": 25,
        }

        result = parse_daily_summary(raw)

        assert result["date"] == date(2024, 1, 15)
        assert result["pas"] == 12500
        assert result["distance_metres"] == 9500
        assert result["calories_totales"] == 2200
        assert result["calories_actives"] == 450
        assert result["minutes_actives"] == 30
        assert result["minutes_tres_actives"] == 15
        assert result["fc_repos"] == 58
        assert result["fc_min"] == 52
        assert result["fc_max"] == 165
        assert result["stress_moyen"] == 35
        assert result["body_battery_max"] == 95
        assert result["body_battery_min"] == 25

    def test_summary_minimal(self):
        """Parsing avec données minimales."""
        raw = {}

        result = parse_daily_summary(raw)

        assert result["pas"] == 0
        assert result["distance_metres"] == 0
        assert isinstance(result["date"], date)

    def test_summary_avec_timestamp(self):
        """Date via startTimeInSeconds si calendarDate absent."""
        raw = {"startTimeInSeconds": 1700000000}

        result = parse_daily_summary(raw)

        assert result["date"] == date(2023, 11, 14)


# ═══════════════════════════════════════════════════════════
# TESTS TRADUCTION ET AFFICHAGE
# ═══════════════════════════════════════════════════════════


class TestTranslateActivityType:
    """Tests pour translate_activity_type."""

    def test_type_connu(self):
        """Un type connu est traduit."""
        assert translate_activity_type("running") == "course"
        assert translate_activity_type("cycling") == "vélo"
        assert translate_activity_type("swimming") == "natation"

    def test_type_majuscules(self):
        """Le type est normalisé en minuscules."""
        assert translate_activity_type("RUNNING") == "course"
        assert translate_activity_type("Running") == "course"

    def test_type_inconnu(self):
        """Un type inconnu est retourné tel quel."""
        assert translate_activity_type("zumba") == "zumba"


class TestGetActivityIcon:
    """Tests pour get_activity_icon."""

    def test_icon_connu(self):
        """Un type connu retourne son icône."""
        assert get_activity_icon("running") == "🏃"
        assert get_activity_icon("cycling") == "🚴"
        assert get_activity_icon("swimming") == "🏊"

    def test_icon_inconnu(self):
        """Un type inconnu retourne l'icône par défaut."""
        assert get_activity_icon("unknown") == "🏅"

    def test_icon_majuscules(self):
        """Le type est normalisé."""
        assert get_activity_icon("RUNNING") == "🏃"


# ═══════════════════════════════════════════════════════════
# TESTS FORMATAGE
# ═══════════════════════════════════════════════════════════


class TestFormatDuration:
    """Tests pour format_duration."""

    def test_heures_et_minutes(self):
        """Format avec heures et minutes."""
        assert format_duration(5400) == "1h 30m"
        assert format_duration(7200) == "2h 0m"

    def test_minutes_seules(self):
        """Format avec minutes seules."""
        assert format_duration(1800) == "30m"
        assert format_duration(60) == "1m"

    def test_zero(self):
        """0 secondes affiche 0m."""
        assert format_duration(0) == "0m"

    def test_negatif(self):
        """Valeur négative affiche 0m."""
        assert format_duration(-100) == "0m"

    def test_none(self):
        """None affiche 0m."""
        assert format_duration(None) == "0m"

    def test_float(self):
        """Float est converti en int."""
        assert format_duration(3661.5) == "1h 1m"


class TestFormatDistance:
    """Tests pour format_distance."""

    def test_kilometres(self):
        """Distance >= 1000m affichée en km."""
        assert format_distance(5000) == "5.00 km"
        assert format_distance(10500) == "10.50 km"

    def test_metres(self):
        """Distance < 1000m affichée en m."""
        assert format_distance(500) == "500 m"
        assert format_distance(999) == "999 m"

    def test_zero(self):
        """0 affiche 0 m."""
        assert format_distance(0) == "0 m"

    def test_none(self):
        """None affiche 0 m."""
        assert format_distance(None) == "0 m"


class TestFormatPace:
    """Tests pour format_pace."""

    def test_pace_valide(self):
        """Allure valide formatée en min:sec /km."""
        # 5 min/km = 0.3 sec/m
        result = format_pace(0.3)
        assert result == "5:00 /km"

    def test_pace_zero(self):
        """0 retourne N/A."""
        assert format_pace(0) == "N/A"

    def test_pace_none(self):
        """None retourne N/A."""
        assert format_pace(None) == "N/A"

    def test_pace_negatif(self):
        """Négatif retourne N/A."""
        assert format_pace(-0.3) == "N/A"


class TestFormatSpeed:
    """Tests pour format_speed."""

    def test_speed_valide(self):
        """Vitesse en m/s convertie en km/h."""
        # 10 m/s = 36 km/h
        assert format_speed(10.0) == "36.0 km/h"
        # 2.78 m/s â‰ˆ 10 km/h
        assert format_speed(2.78) == "10.0 km/h"

    def test_speed_zero(self):
        """0 affiche 0 km/h."""
        assert format_speed(0) == "0 km/h"

    def test_speed_none(self):
        """None affiche 0 km/h."""
        assert format_speed(None) == "0 km/h"


# ═══════════════════════════════════════════════════════════
# TESTS CALCULS STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCalculateDailyStats:
    """Tests pour calculate_daily_stats."""

    def test_stats_normales(self):
        """Calcul des stats sur plusieurs jours."""
        summaries = [
            {"pas": 10000, "calories_actives": 400, "distance_metres": 8000},
            {"pas": 12000, "calories_actives": 500, "distance_metres": 9500},
            {"pas": 8000, "calories_actives": 350, "distance_metres": 6000},
        ]

        result = calculate_daily_stats(summaries)

        assert result["total_pas"] == 30000
        assert result["total_calories"] == 1250
        assert result["total_distance_km"] == 23.5
        assert result["moyenne_pas_jour"] == 10000
        assert result["jours_avec_donnees"] == 3

    def test_stats_liste_vide(self):
        """Stats sur liste vide retourne des zéros."""
        result = calculate_daily_stats([])

        assert result["total_pas"] == 0
        assert result["total_calories"] == 0
        assert result["jours_avec_donnees"] == 0


class TestCalculateActivityStats:
    """Tests pour calculate_activity_stats."""

    def test_activity_stats_normales(self):
        """Stats d'activités normales."""
        activities = [
            {"type_activite": "running", "duree_secondes": 3600, "calories": 400},
            {"type_activite": "running", "duree_secondes": 1800, "calories": 200},
            {"type_activite": "cycling", "duree_secondes": 3600, "calories": 300},
        ]

        result = calculate_activity_stats(activities)

        assert result["total_activites"] == 3
        assert result["par_type"]["running"]["count"] == 2
        assert result["par_type"]["cycling"]["count"] == 1
        assert result["total_duree_minutes"] == 150
        assert result["total_calories"] == 900

    def test_activity_stats_vide(self):
        """Stats sur liste vide."""
        result = calculate_activity_stats([])

        assert result["total_activites"] == 0
        assert result["par_type"] == {}

    def test_activity_calories_none(self):
        """Calories None sont gérées."""
        activities = [{"type_activite": "running", "duree_secondes": 3600, "calories": None}]

        result = calculate_activity_stats(activities)

        assert result["total_calories"] == 0


class TestCalculateStreak:
    """Tests pour calculate_streak."""

    def test_streak_consecutif(self):
        """Streak de jours consécutifs."""
        today = date(2024, 1, 15)
        summaries = {
            date(2024, 1, 15): {"pas": 12000},
            date(2024, 1, 14): {"pas": 11000},
            date(2024, 1, 13): {"pas": 10500},
        }

        result = calculate_streak(summaries, goal_steps=10000, reference_date=today)

        assert result == 3

    def test_streak_interrupted(self):
        """Streak interrompu par un jour manqué."""
        today = date(2024, 1, 15)
        summaries = {
            date(2024, 1, 15): {"pas": 12000},
            date(2024, 1, 14): {"pas": 8000},  # Sous objectif
            date(2024, 1, 13): {"pas": 11000},
        }

        result = calculate_streak(summaries, goal_steps=10000, reference_date=today)

        assert result == 1

    def test_streak_aucun(self):
        """Pas de streak si aujourd'hui n'atteint pas l'objectif."""
        today = date(2024, 1, 15)
        summaries = {
            date(2024, 1, 15): {"pas": 5000},
        }

        result = calculate_streak(summaries, goal_steps=10000, reference_date=today)

        assert result == 0

    def test_streak_vide(self):
        """Aucune donnée = streak 0."""
        result = calculate_streak({}, goal_steps=10000, reference_date=date(2024, 1, 15))

        assert result == 0


class TestGetStreakBadge:
    """Tests pour get_streak_badge."""

    def test_badge_champion(self):
        """Streak >= 100 = Champion."""
        result = get_streak_badge(100)
        assert result == ("🏆", "Champion du mois")

    def test_badge_diamant(self):
        """Streak >= 60 = Diamant."""
        result = get_streak_badge(60)
        assert result == ("💎", "Diamant")

    def test_badge_on_fire(self):
        """Streak >= 30 = On fire."""
        result = get_streak_badge(30)
        assert result == ("🔥", "On fire!")

    def test_badge_star(self):
        """Streak >= 14 = Star."""
        result = get_streak_badge(14)
        assert result == ("⭐", "Star")

    def test_badge_semaine(self):
        """Streak >= 7 = 1 semaine."""
        result = get_streak_badge(7)
        assert result == ("⏰", "1 semaine")

    def test_badge_aucun(self):
        """Streak < 7 = pas de badge."""
        result = get_streak_badge(6)
        assert result is None

        result = get_streak_badge(0)
        assert result is None


class TestCalculateGoalProgress:
    """Tests pour calculate_goal_progress."""

    def test_objectif_atteint(self):
        """Objectif atteint = 100% vert."""
        percentage, color = calculate_goal_progress(10000, 10000)
        assert percentage == 100.0
        assert color == "green"

    def test_objectif_depasse(self):
        """Objectif dépassé = plafonné à 100%."""
        percentage, color = calculate_goal_progress(15000, 10000)
        assert percentage == 100.0
        assert color == "green"

    def test_75_pourcent(self):
        """75%+ = bleu."""
        percentage, color = calculate_goal_progress(7500, 10000)
        assert percentage == 75.0
        assert color == "blue"

    def test_50_pourcent(self):
        """50%+ = orange."""
        percentage, color = calculate_goal_progress(5000, 10000)
        assert percentage == 50.0
        assert color == "orange"

    def test_moins_50_pourcent(self):
        """<50% = rouge."""
        percentage, color = calculate_goal_progress(3000, 10000)
        assert percentage == 30.0
        assert color == "red"

    def test_objectif_zero(self):
        """Objectif 0 = 100% vert."""
        percentage, color = calculate_goal_progress(5000, 0)
        assert percentage == 100.0
        assert color == "green"


class TestEstimateCaloriesBurned:
    """Tests pour estimate_calories_burned."""

    def test_running_1h(self):
        """Estimation pour 1h de course à 70kg."""
        result = estimate_calories_burned("running", 3600, 70.0)
        # MET 10 * 70kg * 1h = 700 calories
        assert result == 700

    def test_walking_30min(self):
        """Estimation pour 30min de marche à 70kg."""
        result = estimate_calories_burned("walking", 1800, 70.0)
        # MET 3.5 * 70kg * 0.5h = 122.5 => 122
        assert result == 122

    def test_type_inconnu(self):
        """Type inconnu utilise MET 4.0."""
        result = estimate_calories_burned("zumba", 3600, 70.0)
        # MET 4.0 * 70kg * 1h = 280
        assert result == 280

    def test_poids_different(self):
        """Poids différent affecte le résultat."""
        result = estimate_calories_burned("running", 3600, 100.0)
        # MET 10 * 100kg * 1h = 1000
        assert result == 1000


class TestCalculateWeeklySummary:
    """Tests pour calculate_weekly_summary."""

    def test_semaine_complete(self):
        """Résumé d'une semaine complète."""
        # Semaine du 8 au 14 janvier 2024 (lundi au dimanche)
        summaries = [
            {
                "date": date(2024, 1, 8),
                "pas": 10000,
                "calories_actives": 400,
                "distance_metres": 8000,
            },
            {
                "date": date(2024, 1, 9),
                "pas": 12000,
                "calories_actives": 500,
                "distance_metres": 9500,
            },
            {
                "date": date(2024, 1, 10),
                "pas": 8000,
                "calories_actives": 350,
                "distance_metres": 6000,
            },
        ]

        result = calculate_weekly_summary(summaries, week_start=date(2024, 1, 8))

        assert result["total_pas"] == 30000
        assert result["semaine_debut"] == date(2024, 1, 8)
        assert result["semaine_fin"] == date(2024, 1, 14)
        assert result["jours_objectif_atteint"] == 2  # 10000 et 12000
        assert result["jours_manquants"] == 4  # 7 - 3


# ═══════════════════════════════════════════════════════════
# TESTS VALIDATION
# ═══════════════════════════════════════════════════════════


class TestValidateOauthConfig:
    """Tests pour validate_oauth_config."""

    def test_config_valide(self):
        """Configuration complète et valide."""
        config = {
            "consumer_key": "key123",
            "consumer_secret": "secret456",
            "request_token_url": "https://api.garmin.com/request",
            "access_token_url": "https://api.garmin.com/access",
            "authorize_url": "https://api.garmin.com/authorize",
            "api_base_url": "https://api.garmin.com",
        }

        is_valid, errors = validate_oauth_config(config)

        assert is_valid is True
        assert errors == []

    def test_config_cle_manquante(self):
        """Clé manquante signalée."""
        config = {
            "consumer_key": "key123",
            # consumer_secret manquant
            "request_token_url": "https://api.garmin.com/request",
            "access_token_url": "https://api.garmin.com/access",
            "authorize_url": "https://api.garmin.com/authorize",
        }

        is_valid, errors = validate_oauth_config(config)

        assert is_valid is False
        assert any("consumer_secret" in e for e in errors)

    def test_config_url_non_securisee(self):
        """URL http:// signalée."""
        config = {
            "consumer_key": "key123",
            "consumer_secret": "secret456",
            "request_token_url": "http://api.garmin.com/request",  # http
            "access_token_url": "https://api.garmin.com/access",
            "authorize_url": "https://api.garmin.com/authorize",
        }

        is_valid, errors = validate_oauth_config(config)

        assert is_valid is False
        assert any("non sécurisée" in e for e in errors)


class TestValidateGarminToken:
    """Tests pour validate_garmin_token."""

    def test_token_valide(self):
        """Token valide."""
        token = {
            "oauth_token": "token123",
            "oauth_token_secret": "secret456",
        }

        is_valid, error = validate_garmin_token(token)

        assert is_valid is True
        assert error == ""

    def test_token_none(self):
        """Token None invalide."""
        is_valid, error = validate_garmin_token(None)

        assert is_valid is False
        assert "Aucun token" in error

    def test_token_sans_oauth_token(self):
        """Token sans oauth_token."""
        token = {"oauth_token_secret": "secret"}

        is_valid, error = validate_garmin_token(token)

        assert is_valid is False
        assert "oauth_token manquant" in error

    def test_token_sans_secret(self):
        """Token sans oauth_token_secret."""
        token = {"oauth_token": "token"}

        is_valid, error = validate_garmin_token(token)

        assert is_valid is False
        assert "oauth_token_secret manquant" in error

    def test_token_expire_datetime(self):
        """Token expiré (datetime)."""
        token = {
            "oauth_token": "token",
            "oauth_token_secret": "secret",
            "expires_at": datetime.utcnow() - timedelta(hours=1),
        }

        is_valid, error = validate_garmin_token(token)

        assert is_valid is False
        assert "expiré" in error

    def test_token_expire_timestamp(self):
        """Token expiré (timestamp)."""
        token = {
            "oauth_token": "token",
            "oauth_token_secret": "secret",
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
        }

        is_valid, error = validate_garmin_token(token)

        assert is_valid is False
        assert "expiré" in error


class TestIsSyncNeeded:
    """Tests pour is_sync_needed."""

    def test_jamais_sync(self):
        """Jamais synchronisé = sync nécessaire."""
        assert is_sync_needed(None) is True

    def test_sync_recente(self):
        """Sync récente = pas de sync nécessaire."""
        last_sync = datetime.utcnow() - timedelta(minutes=10)
        assert is_sync_needed(last_sync, min_interval_minutes=30) is False

    def test_sync_ancienne(self):
        """Sync ancienne = sync nécessaire."""
        last_sync = datetime.utcnow() - timedelta(hours=1)
        assert is_sync_needed(last_sync, min_interval_minutes=30) is True


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION DATES
# ═══════════════════════════════════════════════════════════


class TestGetSyncDateRange:
    """Tests pour get_sync_date_range."""

    def test_range_7_jours(self):
        """Plage de 7 jours."""
        start, end = get_sync_date_range(7)

        assert end == date.today()
        assert start == date.today() - timedelta(days=7)

    def test_range_30_jours(self):
        """Plage de 30 jours."""
        start, end = get_sync_date_range(30)

        assert end == date.today()
        assert start == date.today() - timedelta(days=30)


class TestDateToGarminTimestamp:
    """Tests pour date_to_garmin_timestamp."""

    def test_conversion(self):
        """Conversion d'une date en timestamp."""
        d = date(2024, 1, 15)
        result = date_to_garmin_timestamp(d)

        # Doit être le début de la journée
        expected = datetime(2024, 1, 15, 0, 0, 0).timestamp()
        assert result == int(expected)


class TestBuildApiParams:
    """Tests pour build_api_params."""

    def test_params_construction(self):
        """Construction des paramètres API."""
        start = date(2024, 1, 10)
        end = date(2024, 1, 15)

        result = build_api_params(start, end)

        assert "uploadStartTimeInSeconds" in result
        assert "uploadEndTimeInSeconds" in result
        assert result["uploadStartTimeInSeconds"] < result["uploadEndTimeInSeconds"]
