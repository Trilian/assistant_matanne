"""
Tests pour src/core/performance.py
Couvre :
- MetriquePerformance, StatistiquesFonction dataclasses
- ProfileurFonction (enregistrer, obtenir_toutes_stats, obtenir_plus_lentes, obtenir_plus_appelees)
- MoniteurMemoire (tracking, snapshots, cleanup)
- OptimiseurSQL (enregistrer_query, obtenir_statistiques)
- TableauBordPerformance (resume, score_sante)
- Décorateurs: profiler, antirrebond, limiter_debit
- Context managers: mesurer_temps, suivre_requete
- Composants UI
"""

import threading
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.core.performance import (
    ChargeurComposant,
    MetriquePerformance,
    MoniteurMemoire,
    OptimiseurSQL,
    ProfileurFonction,
    StatistiquesFonction,
    TableauBordPerformance,
    afficher_badge_mini_performance,
    afficher_panneau_performance,
    antirrebond,
    limiter_debit,
    mesurer_temps,
    profiler,
    suivre_requete,
)

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Tests Dataclasses de base
# ═══════════════════════════════════════════════════════════════════════════════


class TestMetriquePerformance:
    """Tests pour MetriquePerformance dataclass."""

    def test_creation_avec_valeurs(self):
        """Vérifie la création avec valeurs."""
        m = MetriquePerformance(name="test", duration_ms=123.4, memory_delta_kb=10)
        assert m.name == "test"
        assert m.duration_ms == 123.4
        assert m.memory_delta_kb == 10

    def test_timestamp_auto(self):
        """Vérifie que timestamp est auto-généré."""
        m = MetriquePerformance(name="test", duration_ms=50)
        assert isinstance(m.timestamp, datetime)

    def test_metadata_default(self):
        """Vérifie que metadata est un dict vide par défaut."""
        m = MetriquePerformance(name="test", duration_ms=50)
        assert m.metadata == {}

    def test_metadata_avec_valeurs(self):
        """Vérifie metadata avec valeurs."""
        m = MetriquePerformance(name="test", duration_ms=50, metadata={"key": "value"})
        assert m.metadata == {"key": "value"}


class TestStatistiquesFonction:
    """Tests pour StatistiquesFonction dataclass."""

    def test_creation_defaults(self):
        """Vérifie les valeurs par défaut."""
        s = StatistiquesFonction()
        assert s.call_count == 0
        assert s.total_time_ms == 0
        assert s.min_time_ms == float("inf")
        assert s.max_time_ms == 0
        assert s.avg_time_ms == 0
        assert s.last_call is None
        assert s.errors == 0

    def test_creation_avec_valeurs(self):
        """Vérifie la création avec valeurs."""
        s = StatistiquesFonction(
            call_count=5,
            total_time_ms=100,
            min_time_ms=10,
            max_time_ms=50,
            avg_time_ms=20,
            errors=1,
        )
        assert s.call_count == 5
        assert s.total_time_ms == 100
        assert s.min_time_ms == 10
        assert s.max_time_ms == 50
        assert s.avg_time_ms == 20
        assert s.errors == 1


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Tests ProfileurFonction
# ═══════════════════════════════════════════════════════════════════════════════


class TestProfileurFonction:
    """Tests pour ProfileurFonction."""

    @patch("src.core.performance.st")
    def test_get_stats_empty(self, mock_st):
        """Vérifie _get_stats retourne dict vide par défaut."""
        mock_st.session_state = {}
        stats = ProfileurFonction._get_stats()
        assert stats == {}

    @patch("src.core.performance.st")
    def test_enregistrer_nouvelle_fonction(self, mock_st):
        """Vérifie enregistrer crée une nouvelle entrée."""
        mock_st.session_state = {}
        ProfileurFonction.enregistrer("test_func", 50.0)

        stats = mock_st.session_state[ProfileurFonction.SESSION_KEY]
        assert "test_func" in stats
        assert stats["test_func"].call_count == 1
        assert stats["test_func"].total_time_ms == 50.0

    @patch("src.core.performance.st")
    def test_enregistrer_plusieurs_appels(self, mock_st):
        """Vérifie enregistrer accumule les stats."""
        mock_st.session_state = {}
        ProfileurFonction.enregistrer("test_func", 10.0)
        ProfileurFonction.enregistrer("test_func", 20.0)
        ProfileurFonction.enregistrer("test_func", 30.0)

        stats = mock_st.session_state[ProfileurFonction.SESSION_KEY]["test_func"]
        assert stats.call_count == 3
        assert stats.total_time_ms == 60.0
        assert stats.min_time_ms == 10.0
        assert stats.max_time_ms == 30.0
        assert stats.avg_time_ms == 20.0

    @patch("src.core.performance.st")
    def test_enregistrer_avec_erreur(self, mock_st):
        """Vérifie enregistrer compte les erreurs."""
        mock_st.session_state = {}
        ProfileurFonction.enregistrer("test_func", 50.0, error=True)

        stats = mock_st.session_state[ProfileurFonction.SESSION_KEY]["test_func"]
        assert stats.errors == 1

    @patch("src.core.performance.st")
    def test_obtenir_toutes_stats(self, mock_st):
        """Vérifie obtenir_toutes_stats."""
        mock_st.session_state = {
            ProfileurFonction.SESSION_KEY: {
                "func1": StatistiquesFonction(call_count=5),
                "func2": StatistiquesFonction(call_count=10),
            }
        }
        stats = ProfileurFonction.obtenir_toutes_stats()
        assert len(stats) == 2
        assert "func1" in stats
        assert "func2" in stats

    @patch("src.core.performance.st")
    def test_obtenir_plus_lentes(self, mock_st):
        """Vérifie obtenir_plus_lentes retourne triées par avg_time."""
        mock_st.session_state = {
            ProfileurFonction.SESSION_KEY: {
                "fast": StatistiquesFonction(avg_time_ms=10),
                "slow": StatistiquesFonction(avg_time_ms=100),
                "medium": StatistiquesFonction(avg_time_ms=50),
            }
        }
        slowest = ProfileurFonction.obtenir_plus_lentes(2)
        assert len(slowest) == 2
        assert slowest[0][0] == "slow"
        assert slowest[1][0] == "medium"

    @patch("src.core.performance.st")
    def test_obtenir_plus_appelees(self, mock_st):
        """Vérifie obtenir_plus_appelees retourne triées par call_count."""
        mock_st.session_state = {
            ProfileurFonction.SESSION_KEY: {
                "rare": StatistiquesFonction(call_count=1),
                "frequent": StatistiquesFonction(call_count=100),
                "normal": StatistiquesFonction(call_count=10),
            }
        }
        most_called = ProfileurFonction.obtenir_plus_appelees(2)
        assert len(most_called) == 2
        assert most_called[0][0] == "frequent"
        assert most_called[1][0] == "normal"

    @patch("src.core.performance.st")
    def test_effacer(self, mock_st):
        """Vérifie effacer reset les stats."""
        mock_st.session_state = {
            ProfileurFonction.SESSION_KEY: {"func": StatistiquesFonction(call_count=5)}
        }
        ProfileurFonction.effacer()
        assert mock_st.session_state[ProfileurFonction.SESSION_KEY] == {}


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Tests MoniteurMemoire
# ═══════════════════════════════════════════════════════════════════════════════


class TestMoniteurMemoire:
    """Tests pour MoniteurMemoire."""

    def test_demarrer_suivi(self):
        """Vérifie demarrer_suivi active le tracking."""
        MoniteurMemoire._tracking_active = False
        MoniteurMemoire.demarrer_suivi()
        assert MoniteurMemoire._tracking_active is True
        MoniteurMemoire.arreter_suivi()  # Cleanup

    def test_arreter_suivi(self):
        """Vérifie arreter_suivi désactive le tracking."""
        MoniteurMemoire._tracking_active = True
        # Ensure tracemalloc is started for this test
        import tracemalloc

        if not tracemalloc.is_tracing():
            tracemalloc.start()

        MoniteurMemoire.arreter_suivi()
        assert MoniteurMemoire._tracking_active is False

    def test_obtenir_utilisation_courante_sans_tracking(self):
        """Vérifie obtenir_utilisation_courante sans tracking."""
        MoniteurMemoire._tracking_active = False
        usage = MoniteurMemoire.obtenir_utilisation_courante()

        assert "current_mb" in usage
        assert "peak_mb" in usage
        assert "total_objects" in usage
        assert "top_types" in usage
        assert usage["current_mb"] == 0  # Pas de tracking

    def test_obtenir_utilisation_courante_avec_tracking(self):
        """Vérifie obtenir_utilisation_courante avec tracking."""
        MoniteurMemoire.demarrer_suivi()

        # Allouer de la mémoire
        _ = [i for i in range(1000)]

        usage = MoniteurMemoire.obtenir_utilisation_courante()

        assert usage["current_mb"] >= 0
        assert usage["total_objects"] > 0
        assert isinstance(usage["top_types"], dict)

        MoniteurMemoire.arreter_suivi()

    @patch("src.core.performance.st")
    def test_prendre_instantane(self, mock_st):
        """Vérifie prendre_instantane sauvegarde dans session."""
        mock_st.session_state = {}

        with patch.object(
            MoniteurMemoire,
            "obtenir_utilisation_courante",
            return_value={
                "current_mb": 100,
                "peak_mb": 150,
                "total_objects": 5000,
                "top_types": {},
            },
        ):
            snapshot = MoniteurMemoire.prendre_instantane("test_snapshot")

        assert snapshot["label"] == "test_snapshot"
        assert "timestamp" in snapshot
        assert len(mock_st.session_state[MoniteurMemoire.SESSION_KEY]) == 1

    @patch("src.core.performance.st")
    def test_prendre_instantane_limite_20(self, mock_st):
        """Vérifie que max 20 snapshots sont gardés."""
        mock_st.session_state = {
            MoniteurMemoire.SESSION_KEY: [{"label": f"old_{i}"} for i in range(25)]
        }

        with patch.object(
            MoniteurMemoire,
            "obtenir_utilisation_courante",
            return_value={
                "current_mb": 100,
                "peak_mb": 150,
                "total_objects": 5000,
                "top_types": {},
            },
        ):
            MoniteurMemoire.prendre_instantane("new")

        assert len(mock_st.session_state[MoniteurMemoire.SESSION_KEY]) == 20

    @patch("src.core.performance.st")
    def test_obtenir_instantanes(self, mock_st):
        """Vérifie obtenir_instantanes retourne les snapshots."""
        mock_st.session_state = {
            MoniteurMemoire.SESSION_KEY: [{"label": "test1"}, {"label": "test2"}]
        }
        snapshots = MoniteurMemoire.obtenir_instantanes()
        assert len(snapshots) == 2

    @patch("src.core.performance.st")
    @patch("src.core.performance.gc")
    def test_forcer_nettoyage(self, mock_gc, mock_st):
        """Vérifie forcer_nettoyage appelle gc.collect()."""
        mock_gc.collect.return_value = 50

        with patch.object(MoniteurMemoire, "obtenir_utilisation_courante") as mock_usage:
            mock_usage.side_effect = [
                {"current_mb": 200, "peak_mb": 250, "total_objects": 10000, "top_types": {}},
                {"current_mb": 150, "peak_mb": 250, "total_objects": 8000, "top_types": {}},
            ]
            result = MoniteurMemoire.forcer_nettoyage()

        assert result["objects_collected"] == 50
        assert result["memory_freed_mb"] == 50


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Tests OptimiseurSQL
# ═══════════════════════════════════════════════════════════════════════════════


class TestOptimiseurSQL:
    """Tests pour OptimiseurSQL."""

    @patch("src.core.performance.st")
    def test_get_stats_default(self, mock_st):
        """Vérifie _get_stats retourne structure par défaut."""
        mock_st.session_state = {}
        stats = OptimiseurSQL._get_stats()

        assert "queries" in stats
        assert "slow_queries" in stats
        assert "total_count" in stats
        assert "total_time_ms" in stats

    @patch("src.core.performance.st")
    def test_enregistrer_query(self, mock_st):
        """Vérifie enregistrer_query ajoute une requête."""
        mock_st.session_state = {}
        OptimiseurSQL.enregistrer_query("SELECT * FROM recettes", 25.0, 10)

        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert stats["total_count"] == 1
        assert stats["total_time_ms"] == 25.0
        assert len(stats["queries"]) == 1

    @patch("src.core.performance.st")
    def test_enregistrer_query_lente(self, mock_st):
        """Vérifie que les requêtes > 100ms sont marquées lentes."""
        mock_st.session_state = {}
        OptimiseurSQL.enregistrer_query("SELECT * FROM big_table", 150.0)

        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert len(stats["slow_queries"]) == 1

    @patch("src.core.performance.st")
    def test_enregistrer_query_tronque(self, mock_st):
        """Vérifie que les requêtes longues sont tronquées."""
        mock_st.session_state = {}
        long_query = "SELECT " + "a," * 100 + " FROM table"
        OptimiseurSQL.enregistrer_query(long_query, 10.0)

        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert len(stats["queries"][0]["query"]) <= 200

    @patch("src.core.performance.st")
    def test_obtenir_statistiques(self, mock_st):
        """Vérifie obtenir_statistiques."""
        mock_st.session_state = {
            OptimiseurSQL.SESSION_KEY: {
                "queries": [{"query": "test", "duration_ms": 10}],
                "slow_queries": [],
                "total_count": 5,
                "total_time_ms": 100.0,
            }
        }
        stats = OptimiseurSQL.obtenir_statistiques()

        assert stats["total_queries"] == 5
        assert stats["avg_time_ms"] == 20.0
        assert stats["slow_query_count"] == 0

    @patch("src.core.performance.st")
    def test_obtenir_statistiques_empty(self, mock_st):
        """Vérifie obtenir_statistiques avec aucune requête."""
        mock_st.session_state = {}
        stats = OptimiseurSQL.obtenir_statistiques()

        assert stats["total_queries"] == 0
        assert stats["avg_time_ms"] == 0

    @patch("src.core.performance.st")
    def test_effacer(self, mock_st):
        """Vérifie effacer reset les stats."""
        mock_st.session_state = {
            OptimiseurSQL.SESSION_KEY: {
                "queries": [{"test": 1}],
                "slow_queries": [{"test": 1}],
                "total_count": 10,
                "total_time_ms": 500,
            }
        }
        OptimiseurSQL.effacer()

        stats = mock_st.session_state[OptimiseurSQL.SESSION_KEY]
        assert stats["total_count"] == 0
        assert stats["queries"] == []


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Tests TableauBordPerformance
# ═══════════════════════════════════════════════════════════════════════════════


class TestTableauBordPerformance:
    """Tests pour TableauBordPerformance."""

    @patch("src.core.performance.st")
    @patch("src.core.performance.ChargeurModuleDiffere", create=True)
    def test_obtenir_resume(self, mock_loader, mock_st):
        """Vérifie obtenir_resume retourne toutes les métriques."""
        mock_st.session_state = {}

        # Mock lazy loader
        with patch("src.core.performance.ChargeurModuleDiffere") as mock_lazy:
            mock_lazy.obtenir_statistiques.return_value = {
                "cached_modules": 5,
                "total_load_time": 1.5,
                "average_load_time": 0.3,
            }

            with patch.object(ProfileurFonction, "obtenir_toutes_stats", return_value={}):
                with patch.object(ProfileurFonction, "obtenir_plus_lentes", return_value=[]):
                    with patch.object(
                        MoniteurMemoire,
                        "obtenir_utilisation_courante",
                        return_value={
                            "current_mb": 100,
                            "peak_mb": 150,
                            "total_objects": 5000,
                            "top_types": {},
                        },
                    ):
                        with patch.object(
                            OptimiseurSQL,
                            "obtenir_statistiques",
                            return_value={
                                "total_queries": 10,
                                "avg_time_ms": 25,
                                "slow_query_count": 1,
                                "recent_queries": [],
                                "slow_queries": [],
                            },
                        ):
                            summary = TableauBordPerformance.obtenir_resume()

        assert "lazy_loading" in summary
        assert "functions" in summary
        assert "memory" in summary
        assert "sql" in summary

    @patch("src.core.performance.st")
    def test_obtenir_score_sante_parfait(self, mock_st):
        """Vérifie score parfait sans pénalités."""
        mock_st.session_state = {}

        with patch.object(
            TableauBordPerformance,
            "obtenir_resume",
            return_value={
                "memory": {"current_mb": 50},
                "sql": {"slow_count": 0},
                "lazy_loading": {"avg_load_time_ms": 100},
                "functions": {"tracked_count": 0, "slowest": []},
            },
        ):
            score, status = TableauBordPerformance.obtenir_score_sante()

        assert score == 100
        assert status == "ðŸŸ¢"

    @patch("src.core.performance.st")
    def test_obtenir_score_sante_penalites_memoire(self, mock_st):
        """Vérifie pénalités mémoire."""
        mock_st.session_state = {}

        with patch.object(
            TableauBordPerformance,
            "obtenir_resume",
            return_value={
                "memory": {"current_mb": 600},  # > 500 = -20
                "sql": {"slow_count": 0},
                "lazy_loading": {"avg_load_time_ms": 100},
                "functions": {"tracked_count": 0, "slowest": []},
            },
        ):
            score, status = TableauBordPerformance.obtenir_score_sante()

        assert score == 80

    @patch("src.core.performance.st")
    def test_obtenir_score_sante_penalites_sql(self, mock_st):
        """Vérifie pénalités SQL lentes."""
        mock_st.session_state = {}

        with patch.object(
            TableauBordPerformance,
            "obtenir_resume",
            return_value={
                "memory": {"current_mb": 50},
                "sql": {"slow_count": 15},  # > 10 = -15
                "lazy_loading": {"avg_load_time_ms": 100},
                "functions": {"tracked_count": 0, "slowest": []},
            },
        ):
            score, status = TableauBordPerformance.obtenir_score_sante()

        assert score == 85

    @patch("src.core.performance.st")
    def test_obtenir_score_sante_status_jaune(self, mock_st):
        """Vérifie status jaune (60-79)."""
        mock_st.session_state = {}

        with patch.object(
            TableauBordPerformance,
            "obtenir_resume",
            return_value={
                "memory": {"current_mb": 300},  # -10
                "sql": {"slow_count": 15},  # -15
                "lazy_loading": {"avg_load_time_ms": 600},  # -10
                "functions": {"tracked_count": 0, "slowest": []},
            },
        ):
            score, status = TableauBordPerformance.obtenir_score_sante()

        assert 60 <= score < 80
        assert status == "ðŸŸ¡"


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Tests Décorateurs
# ═══════════════════════════════════════════════════════════════════════════════


class TestDecorateurs:
    """Tests pour les décorateurs de performance."""

    @patch("src.core.performance.ProfileurFonction")
    def test_profiler_sans_args(self, mock_profiler):
        """Vérifie le décorateur @profiler sans arguments."""

        @profiler
        def test_function():
            return 42

        result = test_function()
        assert result == 42
        mock_profiler.enregistrer.assert_called()

    @patch("src.core.performance.ProfileurFonction")
    def test_profiler_avec_nom(self, mock_profiler):
        """Vérifie le décorateur @profiler avec nom personnalisé."""

        @profiler(name="custom_name")
        def test_function():
            return "result"

        result = test_function()
        assert result == "result"
        # Vérifie que le nom personnalisé est utilisé
        call_args = mock_profiler.enregistrer.call_args
        assert call_args[0][0] == "custom_name"

    @patch("src.core.performance.ProfileurFonction")
    def test_profiler_avec_exception(self, mock_profiler):
        """Vérifie profiler marque les erreurs."""

        @profiler
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()

        call_args = mock_profiler.enregistrer.call_args
        assert call_args[0][2] is True  # error=True

    @patch("src.core.performance.ProfileurFonction")
    def test_mesurer_temps_context_manager(self, mock_profiler):
        """Vérifie le context manager mesurer_temps."""
        with mesurer_temps("test_block"):
            time.sleep(0.01)

        mock_profiler.enregistrer.assert_called_once()
        call_args = mock_profiler.enregistrer.call_args
        assert call_args[0][0] == "test_block"
        assert call_args[0][1] >= 10  # Au moins 10ms

    @patch("src.core.performance.ProfileurFonction")
    def test_mesurer_temps_avec_exception(self, mock_profiler):
        """Vérifie mesurer_temps enregistre même avec exception."""
        with pytest.raises(ValueError):
            with mesurer_temps("failing_block"):
                raise ValueError("Error")

        call_args = mock_profiler.enregistrer.call_args
        assert call_args[0][2] is True  # error=True

    def test_antirrebond(self):
        """Vérifie le décorateur antirrebond."""
        call_count = 0

        @antirrebond(wait_ms=100)
        def debounced_func():
            nonlocal call_count
            call_count += 1
            return call_count

        # Premier appel
        result1 = debounced_func()
        assert result1 == 1

        # Appel immédiat - devrait être ignoré
        result2 = debounced_func()
        assert result2 is None

        # Attendre et réessayer
        time.sleep(0.15)
        result3 = debounced_func()
        assert result3 == 2

    def test_limiter_debit(self):
        """Vérifie le décorateur limiter_debit."""
        call_count = 0

        @limiter_debit(max_calls=3, period_seconds=60)
        def throttled_func():
            nonlocal call_count
            call_count += 1
            return call_count

        # 3 appels OK
        assert throttled_func() == 1
        assert throttled_func() == 2
        assert throttled_func() == 3

        # 4e appel bloqué
        assert throttled_func() is None

    def test_limiter_debit_thread_safe(self):
        """Vérifie limiter_debit est thread-safe."""
        results = []

        @limiter_debit(max_calls=5, period_seconds=60)
        def throttled_func():
            results.append(1)
            return len(results)

        threads = [threading.Thread(target=throttled_func) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Seulement 5 appels doivent réussir
        assert len(results) == 5


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Tests ChargeurComposant
# ═══════════════════════════════════════════════════════════════════════════════


class TestChargeurComposant:
    """Tests pour ChargeurComposant."""

    def setup_method(self):
        """Reset avant chaque test."""
        ChargeurComposant._loaded = set()

    @patch("src.core.performance.st")
    @patch("src.core.performance.mesurer_temps")
    def test_composant_differe_premier_chargement(self, mock_mesurer, mock_st):
        """Vérifie le premier chargement d'un composant."""
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock()
        mock_mesurer.return_value.__enter__ = MagicMock()
        mock_mesurer.return_value.__exit__ = MagicMock()

        loader_called = []

        def loader():
            loader_called.append(1)

        ChargeurComposant.composant_differe("comp1", loader)

        assert len(loader_called) == 1
        assert "comp1" in ChargeurComposant._loaded

    @patch("src.core.performance.st")
    @patch("src.core.performance.mesurer_temps")
    def test_composant_differe_deja_charge(self, mock_mesurer, mock_st):
        """Vérifie qu'un composant déjà chargé n'affiche pas le spinner."""
        mock_mesurer.return_value.__enter__ = MagicMock()
        mock_mesurer.return_value.__exit__ = MagicMock()

        ChargeurComposant._loaded.add("comp2")

        loader_called = []

        def loader():
            loader_called.append(1)

        ChargeurComposant.composant_differe("comp2", loader)

        assert len(loader_called) == 1
        mock_st.spinner.assert_not_called()

    def test_reset(self):
        """Vérifie reset vide les composants chargés."""
        ChargeurComposant._loaded.add("test")
        ChargeurComposant.reset()
        assert len(ChargeurComposant._loaded) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Tests Composants UI
# ═══════════════════════════════════════════════════════════════════════════════


class TestComposantsUI:
    """Tests pour les composants UI."""

    @patch("src.core.performance.st")
    @patch("src.core.performance.TableauBordPerformance")
    def test_afficher_panneau_performance(self, mock_dashboard, mock_st):
        """Vérifie afficher_panneau_performance."""
        mock_dashboard.obtenir_resume.return_value = {
            "lazy_loading": {
                "modules_cached": 5,
                "avg_load_time_ms": 50,
                "total_load_time_ms": 250,
            },
            "functions": {"tracked_count": 10, "slowest": []},
            "memory": {"current_mb": 100, "total_objects": 5000},
            "sql": {"total_queries": 50, "slow_count": 2, "avg_time_ms": 20},
        }
        mock_dashboard.obtenir_score_sante.return_value = (85, "ðŸŸ¢")

        # Mock context managers
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock()
        mock_st.tabs.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_st.columns.return_value = [MagicMock(), MagicMock()]

        afficher_panneau_performance()

        mock_st.expander.assert_called_once()

    @patch("src.core.performance.st")
    @patch("src.core.performance.TableauBordPerformance")
    @patch("src.core.performance.MoniteurMemoire")
    def test_afficher_badge_mini_performance(self, mock_memory, mock_dashboard, mock_st):
        """Vérifie afficher_badge_mini_performance."""
        mock_dashboard.obtenir_score_sante.return_value = (90, "ðŸŸ¢")
        mock_memory.obtenir_utilisation_courante.return_value = {"current_mb": 75}

        afficher_badge_mini_performance()

        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "90%" in call_args
        assert "75MB" in call_args


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Tests suivre_requete
# ═══════════════════════════════════════════════════════════════════════════════


class TestSuivreRequete:
    """Tests pour le context manager suivre_requete."""

    @patch("src.core.performance.OptimiseurSQL")
    def test_suivre_requete_basic(self, mock_sql):
        """Vérifie suivre_requete enregistre la requête."""
        with suivre_requete("SELECT * FROM users"):
            time.sleep(0.01)

        mock_sql.enregistrer_query.assert_called_once()
        call_args = mock_sql.enregistrer_query.call_args[0]
        assert call_args[0] == "SELECT * FROM users"
        assert call_args[1] >= 10  # Au moins 10ms
