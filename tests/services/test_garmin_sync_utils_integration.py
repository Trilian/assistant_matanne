"""
Tests complets pour garmin_sync_utils.py.

Couvre toutes les fonctions utilitaires pures du module.
Ces fonctions n'ont pas de dépendances DB/API.
"""

import pytest
from datetime import date, datetime, timedelta

from src.services.garmin import (
    # Constants
    ACTIVITY_TYPE_MAPPING,
    ACTIVITY_ICONS,
    STEPS_GOAL_DEFAULT,
    CALORIES_GOAL_DEFAULT,
    METERS_TO_KM,
    # Parsing functions
    parse_garmin_timestamp,
    parse_garmin_date,
    parse_activity_data,
    parse_daily_summary,
    # Translation/Display functions
    translate_activity_type,
    get_activity_icon,
    format_duration,
    format_distance,
    format_pace,
    format_speed,
    # Statistics functions
    calculate_daily_stats,
    calculate_activity_stats,
    calculate_streak,
    get_streak_badge,
    calculate_goal_progress,
    estimate_calories_burned,
    calculate_weekly_summary,
    # Validation functions
    validate_oauth_config,
    validate_garmin_token,
    is_sync_needed,
    # Date functions
    get_sync_date_range,
    date_to_garmin_timestamp,
    build_api_params,
)


# ═══════════════════════════════════════════════════════════
# TESTS - CONSTANTES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestConstants:
    """Tests des constantes du module."""

    def test_activity_type_mapping_not_empty(self):
        """ACTIVITY_TYPE_MAPPING n'est pas vide."""
        assert len(ACTIVITY_TYPE_MAPPING) > 0

    def test_activity_type_mapping_has_running(self):
        """running est présent dans le mapping."""
        assert "running" in ACTIVITY_TYPE_MAPPING
        assert ACTIVITY_TYPE_MAPPING["running"] == "course"

    def test_activity_icons_not_empty(self):
        """ACTIVITY_ICONS n'est pas vide."""
        assert len(ACTIVITY_ICONS) > 0

    def test_activity_icons_has_running(self):
        """running a une icône."""
        assert "running" in ACTIVITY_ICONS
        assert ACTIVITY_ICONS["running"] == "🏃"

    def test_steps_goal_default(self):
        """STEPS_GOAL_DEFAULT est défini."""
        assert STEPS_GOAL_DEFAULT == 10000

    def test_calories_goal_default(self):
        """CALORIES_GOAL_DEFAULT est défini."""
        assert CALORIES_GOAL_DEFAULT == 500


# ═══════════════════════════════════════════════════════════
# TESTS - PARSING TIMESTAMP
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestParseGarminTimestamp:
    """Tests pour parse_garmin_timestamp."""

    def test_parse_valid_timestamp(self):
        """Parse un timestamp valide."""
        ts = 1700000000
        result = parse_garmin_timestamp(ts)
        
        assert result is not None
        assert isinstance(result, datetime)

    def test_parse_none_returns_none(self):
        """None retourne None."""
        result = parse_garmin_timestamp(None)
        assert result is None

    def test_parse_zero_returns_none(self):
        """0 retourne None."""
        result = parse_garmin_timestamp(0)
        assert result is None

    def test_parse_float_timestamp(self):
        """Parse un timestamp float."""
        ts = 1700000000.5
        result = parse_garmin_timestamp(ts)
        
        assert result is not None
        assert isinstance(result, datetime)


# ═══════════════════════════════════════════════════════════
# TESTS - PARSING DATE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestParseGarminDate:
    """Tests pour parse_garmin_date."""

    def test_parse_valid_date(self):
        """Parse une date valide."""
        result = parse_garmin_date("2024-01-15")
        
        assert result == date(2024, 1, 15)

    def test_parse_none_returns_none(self):
        """None retourne None."""
        result = parse_garmin_date(None)
        assert result is None

    def test_parse_empty_returns_none(self):
        """Chaîne vide retourne None."""
        result = parse_garmin_date("")
        assert result is None

    def test_parse_invalid_format_returns_none(self):
        """Format invalide retourne None."""
        result = parse_garmin_date("15/01/2024")
        assert result is None

    def test_parse_date_with_time(self):
        """Parse une date avec heure (prend seulement la date)."""
        result = parse_garmin_date("2024-01-15T12:30:00")
        
        assert result == date(2024, 1, 15)


# ═══════════════════════════════════════════════════════════
# TESTS - PARSING ACTIVITY DATA
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestParseActivityData:
    """Tests pour parse_activity_data."""

    def test_parse_basic_activity(self):
        """Parse une activité basique."""
        raw = {
            "activityId": "12345",
            "activityType": "running",
            "durationInSeconds": 3600,
            "distanceInMeters": 10000,
        }
        
        result = parse_activity_data(raw)
        
        assert result["garmin_id"] == "12345"
        assert result["type_activite"] == "running"
        assert result["type_activite_fr"] == "course"
        assert result["duree_secondes"] == 3600
        assert result["distance_metres"] == 10000

    def test_parse_activity_with_dict_type(self):
        """Parse une activité avec type en dict."""
        raw = {
            "activityId": "123",
            "activityType": {"typeKey": "cycling"},
            "durationInSeconds": 1800,
        }
        
        result = parse_activity_data(raw)
        
        assert result["type_activite"] == "cycling"
        assert result["type_activite_fr"] == "vélo"

    def test_parse_activity_with_summary_id(self):
        """Parse avec summaryId au lieu de activityId."""
        raw = {"summaryId": "999"}
        
        result = parse_activity_data(raw)
        
        assert result["garmin_id"] == "999"

    def test_parse_activity_has_icon(self):
        """L'activité a une icône."""
        raw = {"activityType": "swimming"}
        
        result = parse_activity_data(raw)
        
        assert result["icon"] == "🏊"


# ═══════════════════════════════════════════════════════════
# TESTS - PARSING DAILY SUMMARY
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestParseDailySummary:
    """Tests pour parse_daily_summary."""

    def test_parse_basic_summary(self):
        """Parse un résumé quotidien basique."""
        raw = {
            "calendarDate": "2024-01-15",
            "steps": 12000,
            "distanceInMeters": 8500,
            "totalKilocalories": 2200,
        }
        
        result = parse_daily_summary(raw)
        
        assert result["date"] == date(2024, 1, 15)
        assert result["pas"] == 12000
        assert result["distance_metres"] == 8500
        assert result["calories_totales"] == 2200

    def test_parse_summary_with_all_fields(self):
        """Parse un résumé avec tous les champs."""
        raw = {
            "calendarDate": "2024-01-15",
            "steps": 10000,
            "activeKilocalories": 500,
            "moderateIntensityMinutes": 30,
            "vigorousIntensityMinutes": 15,
            "restingHeartRateInBeatsPerMinute": 55,
            "averageStressLevel": 30,
        }
        
        result = parse_daily_summary(raw)
        
        assert result["calories_actives"] == 500
        assert result["minutes_actives"] == 30
        assert result["minutes_tres_actives"] == 15
        assert result["fc_repos"] == 55
        assert result["stress_moyen"] == 30


# ═══════════════════════════════════════════════════════════
# TESTS - TRADUCTION
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestTranslateActivityType:
    """Tests pour translate_activity_type."""

    def test_translate_running(self):
        """Traduit running en course."""
        assert translate_activity_type("running") == "course"

    def test_translate_cycling(self):
        """Traduit cycling en vélo."""
        assert translate_activity_type("cycling") == "vélo"

    def test_translate_unknown_returns_itself(self):
        """Type inconnu retourne lui-même."""
        assert translate_activity_type("foo") == "foo"

    def test_translate_case_insensitive(self):
        """La traduction est insensible à la casse."""
        assert translate_activity_type("RUNNING") == "course"
        assert translate_activity_type("Running") == "course"


@pytest.mark.unit
class TestGetActivityIcon:
    """Tests pour get_activity_icon."""

    def test_icon_running(self):
        """Icône pour running."""
        assert get_activity_icon("running") == "🏃"

    def test_icon_cycling(self):
        """Icône pour cycling."""
        assert get_activity_icon("cycling") == "🚴"

    def test_icon_unknown_returns_default(self):
        """Type inconnu retourne icône par défaut."""
        assert get_activity_icon("unknown_sport") == "🏅"


# ═══════════════════════════════════════════════════════════
# TESTS - FORMATAGE DURÉE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestFormatDuration:
    """Tests pour format_duration."""

    def test_format_30_minutes(self):
        """30 minutes."""
        result = format_duration(1800)
        assert result == "30m"

    def test_format_90_minutes(self):
        """1h 30m."""
        result = format_duration(5400)
        assert result == "1h 30m"

    def test_format_zero(self):
        """0 secondes."""
        result = format_duration(0)
        assert result == "0m"

    def test_format_negative(self):
        """Valeur négative."""
        result = format_duration(-100)
        assert result == "0m"

    def test_format_none(self):
        """None."""
        result = format_duration(None)
        assert result == "0m"


# ═══════════════════════════════════════════════════════════
# TESTS - FORMATAGE DISTANCE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestFormatDistance:
    """Tests pour format_distance."""

    def test_format_5km(self):
        """5000m = 5.00 km."""
        result = format_distance(5000)
        assert result == "5.00 km"

    def test_format_500m(self):
        """500m reste en mètres."""
        result = format_distance(500)
        assert result == "500 m"

    def test_format_none(self):
        """None = 0 m."""
        result = format_distance(None)
        assert result == "0 m"

    def test_format_zero(self):
        """0 = 0 m."""
        result = format_distance(0)
        assert result == "0 m"


# ═══════════════════════════════════════════════════════════
# TESTS - FORMATAGE ALLURE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestFormatPace:
    """Tests pour format_pace."""

    def test_format_5min_per_km(self):
        """5 min/km = 0.3 s/m."""
        result = format_pace(0.3)  # 300s / 1000m = 5 min/km
        assert result == "5:00 /km"

    def test_format_none(self):
        """None = N/A."""
        result = format_pace(None)
        assert result == "N/A"

    def test_format_zero(self):
        """0 = N/A."""
        result = format_pace(0)
        assert result == "N/A"


# ═══════════════════════════════════════════════════════════
# TESTS - FORMATAGE VITESSE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestFormatSpeed:
    """Tests pour format_speed."""

    def test_format_10kmh(self):
        """10 km/h."""
        # 10 km/h = 2.78 m/s
        result = format_speed(2.78)
        assert "10.0" in result or "10.1" in result

    def test_format_none(self):
        """None = 0 km/h."""
        result = format_speed(None)
        assert result == "0 km/h"


# ═══════════════════════════════════════════════════════════
# TESTS - STATISTIQUES QUOTIDIENNES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCalculateDailyStats:
    """Tests pour calculate_daily_stats."""

    def test_empty_list(self):
        """Liste vide."""
        result = calculate_daily_stats([])
        
        assert result["total_pas"] == 0
        assert result["jours_avec_donnees"] == 0

    def test_single_summary(self):
        """Un seul résumé."""
        summaries = [{"pas": 10000, "calories_actives": 500, "distance_metres": 8000}]
        
        result = calculate_daily_stats(summaries)
        
        assert result["total_pas"] == 10000
        assert result["total_calories"] == 500
        assert result["jours_avec_donnees"] == 1

    def test_multiple_summaries(self):
        """Plusieurs résumés."""
        summaries = [
            {"pas": 10000, "calories_actives": 500, "distance_metres": 8000},
            {"pas": 8000, "calories_actives": 400, "distance_metres": 6000},
        ]
        
        result = calculate_daily_stats(summaries)
        
        assert result["total_pas"] == 18000
        assert result["moyenne_pas_jour"] == 9000


# ═══════════════════════════════════════════════════════════
# TESTS - STATISTIQUES ACTIVITÉS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCalculateActivityStats:
    """Tests pour calculate_activity_stats."""

    def test_empty_list(self):
        """Liste vide."""
        result = calculate_activity_stats([])
        
        assert result["total_activites"] == 0

    def test_single_activity(self):
        """Une seule activité."""
        activities = [
            {"type_activite": "running", "duree_secondes": 3600, "calories": 500}
        ]
        
        result = calculate_activity_stats(activities)
        
        assert result["total_activites"] == 1
        assert "running" in result["par_type"]

    def test_multiple_activity_types(self):
        """Plusieurs types d'activités."""
        activities = [
            {"type_activite": "running", "duree_secondes": 3600, "calories": 500},
            {"type_activite": "cycling", "duree_secondes": 1800, "calories": 300},
            {"type_activite": "running", "duree_secondes": 1800, "calories": 250},
        ]
        
        result = calculate_activity_stats(activities)
        
        assert result["total_activites"] == 3
        assert result["par_type"]["running"]["count"] == 2
        assert result["par_type"]["cycling"]["count"] == 1


# ═══════════════════════════════════════════════════════════
# TESTS - CALCUL STREAK
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCalculateStreak:
    """Tests pour calculate_streak."""

    def test_empty_dict(self):
        """Dict vide = streak 0."""
        result = calculate_streak({})
        assert result == 0

    def test_two_consecutive_days(self):
        """2 jours consécutifs."""
        ref_date = date(2024, 1, 15)
        summaries = {
            date(2024, 1, 15): {"pas": 12000},
            date(2024, 1, 14): {"pas": 11000},
        }
        
        result = calculate_streak(summaries, goal_steps=10000, reference_date=ref_date)
        
        assert result == 2

    def test_streak_broken(self):
        """Streak interrompu."""
        ref_date = date(2024, 1, 15)
        summaries = {
            date(2024, 1, 15): {"pas": 12000},
            date(2024, 1, 14): {"pas": 5000},  # Sous l'objectif
            date(2024, 1, 13): {"pas": 11000},
        }
        
        result = calculate_streak(summaries, goal_steps=10000, reference_date=ref_date)
        
        assert result == 1


# ═══════════════════════════════════════════════════════════
# TESTS - STREAK BADGE
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGetStreakBadge:
    """Tests pour get_streak_badge."""

    def test_no_badge_for_6_days(self):
        """Pas de badge pour 6 jours."""
        result = get_streak_badge(6)
        assert result is None

    def test_badge_for_7_days(self):
        """Badge pour 7 jours."""
        result = get_streak_badge(7)
        assert result is not None
        assert result[0] == "✨"

    def test_badge_for_30_days(self):
        """Badge pour 30 jours."""
        result = get_streak_badge(30)
        assert result is not None
        assert result[0] == "🔥"

    def test_badge_for_100_days(self):
        """Badge pour 100 jours."""
        result = get_streak_badge(100)
        assert result is not None
        assert result[0] == "🏆"


# ═══════════════════════════════════════════════════════════
# TESTS - GOAL PROGRESS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCalculateGoalProgress:
    """Tests pour calculate_goal_progress."""

    def test_100_percent(self):
        """100% atteint."""
        percentage, color = calculate_goal_progress(10000, 10000)
        
        assert percentage == 100.0
        assert color == "green"

    def test_over_100_percent(self):
        """Plus de 100%."""
        percentage, color = calculate_goal_progress(15000, 10000)
        
        assert percentage == 100.0  # Plafond à 100
        assert color == "green"

    def test_50_percent(self):
        """50%."""
        percentage, color = calculate_goal_progress(5000, 10000)
        
        assert percentage == 50.0
        assert color == "orange"

    def test_25_percent(self):
        """25%."""
        percentage, color = calculate_goal_progress(2500, 10000)
        
        assert percentage == 25.0
        assert color == "red"

    def test_zero_goal(self):
        """Objectif 0."""
        percentage, color = calculate_goal_progress(5000, 0)
        
        assert percentage == 100.0


# ═══════════════════════════════════════════════════════════
# TESTS - ESTIMATION CALORIES
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestEstimateCaloriesBurned:
    """Tests pour estimate_calories_burned."""

    def test_running_1_hour(self):
        """1h de course."""
        calories = estimate_calories_burned("running", 3600, weight_kg=70)
        
        # MET running = 10, calories = 10 * 70 * 1 = 700
        assert calories == 700

    def test_walking_30_min(self):
        """30 min de marche."""
        calories = estimate_calories_burned("walking", 1800, weight_kg=70)
        
        # MET walking = 3.5, calories = 3.5 * 70 * 0.5 = 122.5 -> 122
        assert calories == 122

    def test_unknown_activity(self):
        """Activité inconnue utilise MET par défaut."""
        calories = estimate_calories_burned("unknown_sport", 3600, weight_kg=70)
        
        # MET other = 4.0, calories = 4 * 70 * 1 = 280
        assert calories == 280


# ═══════════════════════════════════════════════════════════
# TESTS - WEEKLY SUMMARY
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestCalculateWeeklySummary:
    """Tests pour calculate_weekly_summary."""

    def test_empty_summaries(self):
        """Liste de résumés vide."""
        result = calculate_weekly_summary([])
        
        assert result["total_pas"] == 0
        assert result["jours_manquants"] == 7

    def test_with_week_data(self):
        """Avec données de la semaine."""
        week_start = date(2024, 1, 15)  # Lundi
        summaries = [
            {"date": date(2024, 1, 15), "pas": 10000, "calories_actives": 500, "distance_metres": 8000},
            {"date": date(2024, 1, 16), "pas": 12000, "calories_actives": 600, "distance_metres": 9000},
        ]
        
        result = calculate_weekly_summary(summaries, week_start=week_start)
        
        assert result["total_pas"] == 22000
        assert result["jours_avec_donnees"] == 2
        assert result["jours_objectif_atteint"] == 2


# ═══════════════════════════════════════════════════════════
# TESTS - VALIDATION OAUTH CONFIG
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestValidateOauthConfig:
    """Tests pour validate_oauth_config."""

    def test_valid_config(self):
        """Configuration valide."""
        config = {
            "consumer_key": "key123",
            "consumer_secret": "secret456",
            "request_token_url": "https://example.com/request",
            "access_token_url": "https://example.com/access",
            "authorize_url": "https://example.com/authorize",
        }
        
        is_valid, errors = validate_oauth_config(config)
        
        assert is_valid is True
        assert len(errors) == 0

    def test_missing_key(self):
        """Clé manquante."""
        config = {
            "consumer_key": "key123",
            # consumer_secret manquant
            "request_token_url": "https://example.com/request",
            "access_token_url": "https://example.com/access",
            "authorize_url": "https://example.com/authorize",
        }
        
        is_valid, errors = validate_oauth_config(config)
        
        assert is_valid is False
        assert len(errors) > 0

    def test_insecure_url(self):
        """URL non sécurisée."""
        config = {
            "consumer_key": "key123",
            "consumer_secret": "secret456",
            "request_token_url": "http://example.com/request",  # http au lieu de https
            "access_token_url": "https://example.com/access",
            "authorize_url": "https://example.com/authorize",
        }
        
        is_valid, errors = validate_oauth_config(config)
        
        assert is_valid is False
        assert any("non sécurisée" in e for e in errors)


# ═══════════════════════════════════════════════════════════
# TESTS - VALIDATION TOKEN
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestValidateGarminToken:
    """Tests pour validate_garmin_token."""

    def test_valid_token(self):
        """Token valide."""
        token = {
            "oauth_token": "token123",
            "oauth_token_secret": "secret456",
        }
        
        is_valid, error = validate_garmin_token(token)
        
        assert is_valid is True
        assert error == ""

    def test_missing_token(self):
        """Token manquant."""
        is_valid, error = validate_garmin_token(None)
        
        assert is_valid is False
        assert "Aucun token" in error

    def test_missing_oauth_token(self):
        """oauth_token manquant."""
        token = {"oauth_token_secret": "secret456"}
        
        is_valid, error = validate_garmin_token(token)
        
        assert is_valid is False
        assert "oauth_token" in error

    def test_expired_token(self):
        """Token expiré."""
        token = {
            "oauth_token": "token123",
            "oauth_token_secret": "secret456",
            "expires_at": datetime.utcnow() - timedelta(hours=1),
        }
        
        is_valid, error = validate_garmin_token(token)
        
        assert is_valid is False
        assert "expiré" in error


# ═══════════════════════════════════════════════════════════
# TESTS - IS SYNC NEEDED
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestIsSyncNeeded:
    """Tests pour is_sync_needed."""

    def test_no_last_sync(self):
        """Pas de dernière sync = sync nécessaire."""
        result = is_sync_needed(None)
        assert result is True

    def test_recent_sync(self):
        """Sync récente = pas de sync nécessaire."""
        last_sync = datetime.utcnow() - timedelta(minutes=10)
        
        result = is_sync_needed(last_sync, min_interval_minutes=30)
        
        assert result is False

    def test_old_sync(self):
        """Sync ancienne = sync nécessaire."""
        last_sync = datetime.utcnow() - timedelta(hours=2)
        
        result = is_sync_needed(last_sync, min_interval_minutes=30)
        
        assert result is True


# ═══════════════════════════════════════════════════════════
# TESTS - DATE FUNCTIONS
# ═══════════════════════════════════════════════════════════

@pytest.mark.unit
class TestGetSyncDateRange:
    """Tests pour get_sync_date_range."""

    def test_default_7_days(self):
        """7 jours par défaut."""
        start, end = get_sync_date_range()
        
        assert end == date.today()
        assert start == date.today() - timedelta(days=7)

    def test_custom_days(self):
        """Nombre de jours personnalisé."""
        start, end = get_sync_date_range(days_back=14)
        
        assert end == date.today()
        assert start == date.today() - timedelta(days=14)


@pytest.mark.unit
class TestDateToGarminTimestamp:
    """Tests pour date_to_garmin_timestamp."""

    def test_convert_date(self):
        """Convertit une date en timestamp."""
        d = date(2024, 1, 15)
        
        result = date_to_garmin_timestamp(d)
        
        assert isinstance(result, int)
        assert result > 0


@pytest.mark.unit
class TestBuildApiParams:
    """Tests pour build_api_params."""

    def test_builds_params(self):
        """Construit les paramètres API."""
        start = date(2024, 1, 1)
        end = date(2024, 1, 7)
        
        result = build_api_params(start, end)
        
        assert "uploadStartTimeInSeconds" in result
        assert "uploadEndTimeInSeconds" in result
        assert result["uploadStartTimeInSeconds"] < result["uploadEndTimeInSeconds"]
