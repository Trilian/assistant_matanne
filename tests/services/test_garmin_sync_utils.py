"""
Tests unitaires pour garmin_sync_utils.py

Ces tests vérifient les fonctions pures sans dépendance API ou base de données.
"""

import pytest
from datetime import date, datetime, timedelta
from src.services.garmin import (
    # Parsing
    parse_garmin_timestamp,
    parse_garmin_date,
    parse_activity_data,
    parse_daily_summary,
    
    # Traduction et affichage
    translate_activity_type,
    get_activity_icon,
    format_duration,
    format_distance,
    format_pace,
    format_speed,
    
    # Calculs et statistiques
    calculate_daily_stats,
    calculate_activity_stats,
    calculate_streak,
    get_streak_badge,
    calculate_goal_progress,
    estimate_calories_burned,
    calculate_weekly_summary,
    
    # Validation
    validate_oauth_config,
    validate_garmin_token,
    is_sync_needed,
    
    # Dates et périodes
    get_sync_date_range,
    date_to_garmin_timestamp,
    build_api_params,
    
    # Constantes
    ACTIVITY_TYPE_MAPPING,
    ACTIVITY_ICONS,
)


# ═══════════════════════════════════════════════════════════
# Tests: Parsing des données API
# ═══════════════════════════════════════════════════════════


class TestParseGarminTimestamp:
    """Tests pour parse_garmin_timestamp"""
    
    def test_timestamp_valide(self):
        result = parse_garmin_timestamp(1700000000)
        assert isinstance(result, datetime)
    
    def test_timestamp_zero(self):
        result = parse_garmin_timestamp(0)
        assert result is None
    
    def test_timestamp_none(self):
        result = parse_garmin_timestamp(None)
        assert result is None
    
    def test_timestamp_float(self):
        result = parse_garmin_timestamp(1700000000.5)
        assert isinstance(result, datetime)


class TestParseGarminDate:
    """Tests pour parse_garmin_date"""
    
    def test_date_valide(self):
        result = parse_garmin_date("2024-06-15")
        assert result == date(2024, 6, 15)
    
    def test_date_avec_timezone(self):
        result = parse_garmin_date("2024-06-15T12:00:00Z")
        assert result == date(2024, 6, 15)
    
    def test_date_none(self):
        result = parse_garmin_date(None)
        assert result is None
    
    def test_date_invalide(self):
        result = parse_garmin_date("invalid-date")
        assert result is None


class TestParseActivityData:
    """Tests pour parse_activity_data"""
    
    def test_activite_complete(self):
        raw = {
            "activityId": "12345",
            "activityType": "running",
            "activityName": "Course matinale",
            "durationInSeconds": 3600,
            "distanceInMeters": 10000,
            "activeKilocalories": 500,
            "averageHeartRateInBeatsPerMinute": 150,
            "maxHeartRateInBeatsPerMinute": 180,
            "startTimeInSeconds": 1700000000,
        }
        result = parse_activity_data(raw)
        
        assert result["garmin_id"] == "12345"
        assert result["type_activite"] == "running"
        assert result["type_activite_fr"] == "course"
        assert result["nom"] == "Course matinale"
        assert result["duree_secondes"] == 3600
        assert result["distance_metres"] == 10000
        assert result["calories"] == 500
        assert result["fc_moyenne"] == 150
        assert result["fc_max"] == 180
    
    def test_activite_minimale(self):
        raw = {"summaryId": "999"}
        result = parse_activity_data(raw)
        
        assert result["garmin_id"] == "999"
        assert result["duree_secondes"] == 1  # Fallback minimum
    
    def test_activity_type_dict(self):
        raw = {"activityType": {"typeKey": "cycling"}}
        result = parse_activity_data(raw)
        assert result["type_activite"] == "cycling"


class TestParseDailySummary:
    """Tests pour parse_daily_summary"""
    
    def test_summary_complet(self):
        raw = {
            "calendarDate": "2024-06-15",
            "steps": 12000,
            "distanceInMeters": 8500,
            "totalKilocalories": 2500,
            "activeKilocalories": 500,
            "moderateIntensityMinutes": 30,
            "vigorousIntensityMinutes": 15,
            "restingHeartRateInBeatsPerMinute": 55,
        }
        result = parse_daily_summary(raw)
        
        assert result["date"] == date(2024, 6, 15)
        assert result["pas"] == 12000
        assert result["distance_metres"] == 8500
        assert result["calories_totales"] == 2500
        assert result["calories_actives"] == 500
        assert result["minutes_actives"] == 30
        assert result["minutes_tres_actives"] == 15
        assert result["fc_repos"] == 55
    
    def test_summary_sans_date(self):
        raw = {"startTimeInSeconds": 1700000000, "steps": 5000}
        result = parse_daily_summary(raw)
        assert result["date"] is not None
        assert result["pas"] == 5000


# ═══════════════════════════════════════════════════════════
# Tests: Traduction et affichage
# ═══════════════════════════════════════════════════════════


class TestTranslateActivityType:
    """Tests pour translate_activity_type"""
    
    def test_running(self):
        assert translate_activity_type("running") == "course"
    
    def test_cycling(self):
        assert translate_activity_type("cycling") == "vélo"
    
    def test_swimming(self):
        assert translate_activity_type("swimming") == "natation"
    
    def test_walking(self):
        assert translate_activity_type("walking") == "marche"
    
    def test_inconnu(self):
        assert translate_activity_type("unknown_type") == "unknown_type"
    
    def test_case_insensitive(self):
        assert translate_activity_type("RUNNING") == "course"
        assert translate_activity_type("Running") == "course"


class TestGetActivityIcon:
    """Tests pour get_activity_icon"""
    
    def test_running_icon(self):
        assert get_activity_icon("running") == "🏃"
    
    def test_cycling_icon(self):
        assert get_activity_icon("cycling") == "🚴"
    
    def test_swimming_icon(self):
        assert get_activity_icon("swimming") == "🏊"
    
    def test_default_icon(self):
        assert get_activity_icon("unknown") == "🏅"


class TestFormatDuration:
    """Tests pour format_duration"""
    
    def test_heures_et_minutes(self):
        assert format_duration(5400) == "1h 30m"
    
    def test_minutes_seules(self):
        assert format_duration(1800) == "30m"
    
    def test_une_heure(self):
        assert format_duration(3600) == "1h 0m"
    
    def test_zero(self):
        assert format_duration(0) == "0m"
    
    def test_negatif(self):
        assert format_duration(-100) == "0m"
    
    def test_none(self):
        assert format_duration(None) == "0m"


class TestFormatDistance:
    """Tests pour format_distance"""
    
    def test_kilometres(self):
        assert format_distance(5000) == "5.00 km"
    
    def test_metres(self):
        assert format_distance(500) == "500 m"
    
    def test_limite_km(self):
        assert format_distance(1000) == "1.00 km"
    
    def test_zero(self):
        assert format_distance(0) == "0 m"
    
    def test_none(self):
        assert format_distance(None) == "0 m"


class TestFormatPace:
    """Tests pour format_pace"""
    
    def test_allure_normale(self):
        # 5 min/km = 300 sec/1000m = 0.3 sec/m
        result = format_pace(0.3)
        assert "5:00" in result
    
    def test_allure_rapide(self):
        # 4 min/km
        result = format_pace(0.24)
        assert "/km" in result
    
    def test_zero(self):
        assert format_pace(0) == "N/A"
    
    def test_none(self):
        assert format_pace(None) == "N/A"


class TestFormatSpeed:
    """Tests pour format_speed"""
    
    def test_vitesse_normale(self):
        # 10 km/h = 2.78 m/s
        result = format_speed(2.78)
        assert "10" in result
        assert "km/h" in result
    
    def test_zero(self):
        assert format_speed(0) == "0 km/h"
    
    def test_none(self):
        assert format_speed(None) == "0 km/h"


# ═══════════════════════════════════════════════════════════
# Tests: Calculs et statistiques
# ═══════════════════════════════════════════════════════════


class TestCalculateDailyStats:
    """Tests pour calculate_daily_stats"""
    
    def test_stats_normales(self):
        summaries = [
            {"pas": 10000, "calories_actives": 400, "distance_metres": 7500},
            {"pas": 8000, "calories_actives": 300, "distance_metres": 6000},
        ]
        result = calculate_daily_stats(summaries)
        
        assert result["total_pas"] == 18000
        assert result["total_calories"] == 700
        assert result["total_distance_km"] == 13.5
        assert result["moyenne_pas_jour"] == 9000
        assert result["jours_avec_donnees"] == 2
    
    def test_stats_vides(self):
        result = calculate_daily_stats([])
        assert result["total_pas"] == 0
        assert result["jours_avec_donnees"] == 0


class TestCalculateActivityStats:
    """Tests pour calculate_activity_stats"""
    
    def test_stats_par_type(self):
        activities = [
            {"type_activite": "running", "duree_secondes": 3600, "calories": 500},
            {"type_activite": "running", "duree_secondes": 1800, "calories": 250},
            {"type_activite": "cycling", "duree_secondes": 7200, "calories": 600},
        ]
        result = calculate_activity_stats(activities)
        
        assert result["total_activites"] == 3
        assert result["par_type"]["running"]["count"] == 2
        assert result["par_type"]["cycling"]["count"] == 1
        assert result["total_duree_minutes"] == 210  # 5400 + 1800 + 7200 = 12600 / 60
    
    def test_stats_vides(self):
        result = calculate_activity_stats([])
        assert result["total_activites"] == 0


class TestCalculateStreak:
    """Tests pour calculate_streak"""
    
    def test_streak_continu(self):
        today = date.today()
        summaries = {
            today: {"pas": 12000},
            today - timedelta(days=1): {"pas": 11000},
            today - timedelta(days=2): {"pas": 10500},
        }
        result = calculate_streak(summaries, goal_steps=10000, reference_date=today)
        assert result == 3
    
    def test_streak_interrompu(self):
        today = date.today()
        summaries = {
            today: {"pas": 12000},
            today - timedelta(days=1): {"pas": 5000},  # Sous l'objectif
            today - timedelta(days=2): {"pas": 10500},
        }
        result = calculate_streak(summaries, goal_steps=10000, reference_date=today)
        assert result == 1
    
    def test_pas_de_streak(self):
        today = date.today()
        summaries = {
            today: {"pas": 5000},  # Sous l'objectif
        }
        result = calculate_streak(summaries, goal_steps=10000, reference_date=today)
        assert result == 0


class TestGetStreakBadge:
    """Tests pour get_streak_badge"""
    
    def test_badge_100_jours(self):
        badge = get_streak_badge(100)
        assert badge is not None
        assert badge[0] == "🏆"
    
    def test_badge_30_jours(self):
        badge = get_streak_badge(30)
        assert badge is not None
        assert badge[0] == "🔥"
    
    def test_badge_7_jours(self):
        badge = get_streak_badge(7)
        assert badge is not None
        assert badge[0] == "✨"
    
    def test_pas_de_badge(self):
        badge = get_streak_badge(5)
        assert badge is None


class TestCalculateGoalProgress:
    """Tests pour calculate_goal_progress"""
    
    def test_objectif_atteint(self):
        pct, color = calculate_goal_progress(10000, 10000)
        assert pct == 100.0
        assert color == "green"
    
    def test_objectif_depasse(self):
        pct, color = calculate_goal_progress(15000, 10000)
        assert pct == 100.0  # Plafonné
        assert color == "green"
    
    def test_75_pourcent(self):
        pct, color = calculate_goal_progress(7500, 10000)
        assert pct == 75.0
        assert color == "blue"
    
    def test_50_pourcent(self):
        pct, color = calculate_goal_progress(5000, 10000)
        assert pct == 50.0
        assert color == "orange"
    
    def test_25_pourcent(self):
        pct, color = calculate_goal_progress(2500, 10000)
        assert pct == 25.0
        assert color == "red"
    
    def test_objectif_zero(self):
        pct, color = calculate_goal_progress(5000, 0)
        assert pct == 100.0


class TestEstimateCaloriesBurned:
    """Tests pour estimate_calories_burned"""
    
    def test_course_1h(self):
        calories = estimate_calories_burned("running", 3600, weight_kg=70.0)
        # Running MET ~10, 70kg, 1h = 700 cal
        assert 650 <= calories <= 750
    
    def test_marche_30min(self):
        calories = estimate_calories_burned("walking", 1800, weight_kg=70.0)
        # Walking MET ~3.5, 70kg, 0.5h = 122.5 cal
        assert 100 <= calories <= 150
    
    def test_type_inconnu(self):
        calories = estimate_calories_burned("unknown", 3600, weight_kg=70.0)
        assert calories > 0  # Utilise le MET par défaut


class TestCalculateWeeklySummary:
    """Tests pour calculate_weekly_summary"""
    
    def test_semaine_complete(self):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        summaries = [
            {"date": week_start + timedelta(days=i), "pas": 10000, "calories_actives": 400, "distance_metres": 7500}
            for i in range(7)
        ]
        
        result = calculate_weekly_summary(summaries, week_start)
        
        assert result["total_pas"] == 70000
        assert result["jours_objectif_atteint"] == 7
        assert result["jours_manquants"] == 0
    
    def test_semaine_incomplete(self):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        summaries = [
            {"date": week_start, "pas": 10000, "calories_actives": 400, "distance_metres": 7500},
        ]
        
        result = calculate_weekly_summary(summaries, week_start)
        
        assert result["jours_avec_donnees"] == 1
        assert result["jours_manquants"] == 6


# ═══════════════════════════════════════════════════════════
# Tests: Validation
# ═══════════════════════════════════════════════════════════


class TestValidateOauthConfig:
    """Tests pour validate_oauth_config"""
    
    def test_config_valide(self):
        config = {
            "consumer_key": "abc",
            "consumer_secret": "xyz",
            "request_token_url": "https://api.example.com/request",
            "access_token_url": "https://api.example.com/access",
            "authorize_url": "https://api.example.com/auth",
            "api_base_url": "https://api.example.com",
        }
        is_valid, errors = validate_oauth_config(config)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_config_manquante(self):
        config = {"consumer_key": "abc"}
        is_valid, errors = validate_oauth_config(config)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_url_non_securisee(self):
        config = {
            "consumer_key": "abc",
            "consumer_secret": "xyz",
            "request_token_url": "http://api.example.com/request",  # HTTP au lieu de HTTPS
            "access_token_url": "https://api.example.com/access",
            "authorize_url": "https://api.example.com/auth",
        }
        is_valid, errors = validate_oauth_config(config)
        assert is_valid is False
        assert any("https" in e.lower() for e in errors)


class TestValidateGarminToken:
    """Tests pour validate_garmin_token"""
    
    def test_token_valide(self):
        token = {
            "oauth_token": "abc123",
            "oauth_token_secret": "xyz789",
        }
        is_valid, error = validate_garmin_token(token)
        assert is_valid is True
        assert error == ""
    
    def test_token_vide(self):
        is_valid, error = validate_garmin_token({})
        assert is_valid is False
    
    def test_token_none(self):
        is_valid, error = validate_garmin_token(None)
        assert is_valid is False
    
    def test_token_expire_datetime(self):
        token = {
            "oauth_token": "abc",
            "oauth_token_secret": "xyz",
            "expires_at": datetime.utcnow() - timedelta(hours=1),
        }
        is_valid, error = validate_garmin_token(token)
        assert is_valid is False
        assert "expiré" in error.lower()
    
    def test_token_expire_timestamp(self):
        token = {
            "oauth_token": "abc",
            "oauth_token_secret": "xyz",
            "expires_at": (datetime.utcnow() - timedelta(hours=1)).timestamp(),
        }
        is_valid, error = validate_garmin_token(token)
        assert is_valid is False


class TestIsSyncNeeded:
    """Tests pour is_sync_needed"""
    
    def test_jamais_sync(self):
        assert is_sync_needed(None) is True
    
    def test_sync_recente(self):
        last_sync = datetime.utcnow() - timedelta(minutes=15)
        assert is_sync_needed(last_sync, min_interval_minutes=30) is False
    
    def test_sync_ancienne(self):
        last_sync = datetime.utcnow() - timedelta(minutes=60)
        assert is_sync_needed(last_sync, min_interval_minutes=30) is True


# ═══════════════════════════════════════════════════════════
# Tests: Dates et périodes
# ═══════════════════════════════════════════════════════════


class TestGetSyncDateRange:
    """Tests pour get_sync_date_range"""
    
    def test_7_jours(self):
        start, end = get_sync_date_range(days_back=7)
        assert end == date.today()
        assert start == date.today() - timedelta(days=7)
    
    def test_30_jours(self):
        start, end = get_sync_date_range(days_back=30)
        assert (end - start).days == 30


class TestDateToGarminTimestamp:
    """Tests pour date_to_garmin_timestamp"""
    
    def test_conversion(self):
        d = date(2024, 1, 1)
        ts = date_to_garmin_timestamp(d)
        assert isinstance(ts, int)
        assert ts > 0
    
    def test_debut_journee(self):
        d = date(2024, 1, 1)
        ts = date_to_garmin_timestamp(d)
        dt = datetime.fromtimestamp(ts)
        assert dt.hour == 0
        assert dt.minute == 0


class TestBuildApiParams:
    """Tests pour build_api_params"""
    
    def test_params_structure(self):
        start = date(2024, 1, 1)
        end = date(2024, 1, 7)
        params = build_api_params(start, end)
        
        assert "uploadStartTimeInSeconds" in params
        assert "uploadEndTimeInSeconds" in params
        assert params["uploadStartTimeInSeconds"] < params["uploadEndTimeInSeconds"]


# ═══════════════════════════════════════════════════════════
# Tests: Constantes
# ═══════════════════════════════════════════════════════════


class TestConstantes:
    """Tests pour les constantes"""
    
    def test_activity_type_mapping(self):
        assert "running" in ACTIVITY_TYPE_MAPPING
        assert "cycling" in ACTIVITY_TYPE_MAPPING
        for en, fr in ACTIVITY_TYPE_MAPPING.items():
            assert isinstance(en, str)
            assert isinstance(fr, str)
    
    def test_activity_icons(self):
        assert "running" in ACTIVITY_ICONS
        for type_act, icon in ACTIVITY_ICONS.items():
            assert len(icon) > 0
