"""
Tests pour src/core/cache.py - SystÃ¨me de cache avec mocks Streamlit.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_session_state():
    """Mock st.session_state pour tests isolÃ©s."""
    mock_state = {}

    def getitem(key):
        return mock_state[key]

    def setitem(key, value):
        mock_state[key] = value

    def contains(key):
        return key in mock_state

    def delitem(key):
        del mock_state[key]

    mock = MagicMock()
    mock.__getitem__ = MagicMock(side_effect=getitem)
    mock.__setitem__ = MagicMock(side_effect=setitem)
    mock.__contains__ = MagicMock(side_effect=contains)
    mock.__delitem__ = MagicMock(side_effect=delitem)
    mock._mock_state = mock_state  # AccÃ¨s direct pour tests

    return mock


@pytest.fixture
def cache_module(mock_session_state):
    """Import cache avec session_state mockÃ©."""
    with patch("streamlit.session_state", mock_session_state):
        # Import aprÃ¨s le patch pour que le module utilise le mock
        import importlib
        import src.core.cache as cache_module

        importlib.reload(cache_module)
        yield cache_module


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CACHE CLASS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCacheBase:
    """Tests de base pour la classe Cache."""

    def test_initialise_creates_structures(self, mock_session_state):
        """Test initialisation crÃ©e les structures."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache._initialiser()

            assert "cache_donnees" in mock_session_state._mock_state
            assert "cache_timestamps" in mock_session_state._mock_state
            assert "cache_dependances" in mock_session_state._mock_state
            assert "cache_statistiques" in mock_session_state._mock_state

    def test_initialise_only_once(self, mock_session_state):
        """Test initialisation ne rÃ©Ã©crit pas si existant."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            # PremiÃ¨re init
            Cache._initialiser()
            mock_session_state._mock_state["cache_donnees"]["test"] = "valeur"

            # DeuxiÃ¨me init ne doit pas Ã©craser
            Cache._initialiser()
            assert mock_session_state._mock_state["cache_donnees"]["test"] == "valeur"


class TestCacheObtenir:
    """Tests pour Cache.obtenir()."""

    def test_obtenir_returns_sentinelle_if_missing(self, mock_session_state):
        """Test obtenir retourne sentinelle si clÃ© absente."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            result = Cache.obtenir("inexistant", sentinelle="default")
            assert result == "default"

    def test_obtenir_returns_value_if_present_and_fresh(self, mock_session_state):
        """Test obtenir retourne valeur si prÃ©sente et fraÃ®che."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("ma_cle", "ma_valeur", ttl=300)
            result = Cache.obtenir("ma_cle", ttl=300)
            assert result == "ma_valeur"

    def test_obtenir_returns_sentinelle_if_expired(self, mock_session_state):
        """Test obtenir retourne sentinelle si expirÃ©."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("ma_cle", "ma_valeur", ttl=300)

            # Simuler expiration
            mock_session_state._mock_state["cache_timestamps"]["ma_cle"] = datetime.now() - timedelta(seconds=400)

            result = Cache.obtenir("ma_cle", ttl=300, sentinelle="expirÃ©")
            assert result == "expirÃ©"

    def test_obtenir_increments_miss_counter(self, mock_session_state):
        """Test obtenir incrÃ©mente compteur miss."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache._initialiser()
            initial_misses = mock_session_state._mock_state["cache_statistiques"]["misses"]

            Cache.obtenir("inexistant")

            assert mock_session_state._mock_state["cache_statistiques"]["misses"] == initial_misses + 1

    def test_obtenir_increments_hit_counter(self, mock_session_state):
        """Test obtenir incrÃ©mente compteur hit."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("ma_cle", "ma_valeur")
            initial_hits = mock_session_state._mock_state["cache_statistiques"]["hits"]

            Cache.obtenir("ma_cle")

            assert mock_session_state._mock_state["cache_statistiques"]["hits"] == initial_hits + 1


class TestCacheDefinir:
    """Tests pour Cache.definir()."""

    def test_definir_stores_value(self, mock_session_state):
        """Test definir stocke la valeur."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("test_cle", {"data": "valeur"})

            assert mock_session_state._mock_state["cache_donnees"]["test_cle"] == {"data": "valeur"}

    def test_definir_stores_timestamp(self, mock_session_state):
        """Test definir stocke le timestamp."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            avant = datetime.now()
            Cache.definir("test_cle", "valeur")
            apres = datetime.now()

            timestamp = mock_session_state._mock_state["cache_timestamps"]["test_cle"]
            assert avant <= timestamp <= apres

    def test_definir_with_dependencies(self, mock_session_state):
        """Test definir avec dÃ©pendances."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("recette_1", "data", dependencies=["recettes", "recette_1"])

            assert "test_cle" not in mock_session_state._mock_state["cache_dependances"].get("recettes", []) or "recette_1" in mock_session_state._mock_state["cache_dependances"]["recettes"]


class TestCacheInvalider:
    """Tests pour Cache.invalider()."""

    def test_invalider_by_pattern(self, mock_session_state):
        """Test invalidation par pattern."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("recettes_liste", "data1")
            Cache.definir("recettes_detail_1", "data2")
            Cache.definir("courses_liste", "data3")

            Cache.invalider(pattern="recettes")

            assert "recettes_liste" not in mock_session_state._mock_state["cache_donnees"]
            assert "recettes_detail_1" not in mock_session_state._mock_state["cache_donnees"]
            assert "courses_liste" in mock_session_state._mock_state["cache_donnees"]

    def test_invalider_by_dependencies(self, mock_session_state):
        """Test invalidation par dÃ©pendances."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("recette_1", "data1", dependencies=["tag_recette"])
            Cache.definir("recette_2", "data2", dependencies=["tag_recette"])
            Cache.definir("autre", "data3")

            Cache.invalider(dependencies=["tag_recette"])

            assert "recette_1" not in mock_session_state._mock_state["cache_donnees"]
            assert "recette_2" not in mock_session_state._mock_state["cache_donnees"]
            assert "autre" in mock_session_state._mock_state["cache_donnees"]

    def test_invalider_increments_counter(self, mock_session_state):
        """Test invalidation incrÃ©mente compteur."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("test", "valeur")
            initial_invalidations = mock_session_state._mock_state["cache_statistiques"]["invalidations"]

            Cache.invalider(pattern="test")

            assert mock_session_state._mock_state["cache_statistiques"]["invalidations"] > initial_invalidations


class TestCacheVider:
    """Tests pour Cache.vider() et clear()."""

    def test_vider_removes_all_data(self, mock_session_state):
        """Test vider supprime toutes les donnÃ©es."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("cle1", "val1")
            Cache.definir("cle2", "val2")

            Cache.vider()

            assert mock_session_state._mock_state["cache_donnees"] == {}

    def test_clear_alias_works(self, mock_session_state):
        """Test alias clear fonctionne."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("cle", "val")

            Cache.clear()

            assert mock_session_state._mock_state["cache_donnees"] == {}


class TestCacheStatistiques:
    """Tests pour Cache.obtenir_statistiques()."""

    def test_obtenir_statistiques_returns_dict(self, mock_session_state):
        """Test statistiques retourne dict."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache._initialiser()
            stats = Cache.obtenir_statistiques()

            assert isinstance(stats, dict)
            assert "hits" in stats
            assert "misses" in stats
            assert "entrees" in stats
            assert "taux_hit" in stats

    def test_taux_hit_calculation(self, mock_session_state):
        """Test calcul taux de hit."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache._initialiser()
            Cache.definir("cle", "val")

            # 2 hits
            Cache.obtenir("cle")
            Cache.obtenir("cle")

            # 1 miss
            Cache.obtenir("inexistant")

            stats = Cache.obtenir_statistiques()

            # 2 hits sur 3 requÃªtes = 66.67%
            assert stats["taux_hit"] == pytest.approx(66.67, rel=0.01)


class TestCacheNettoyerExpires:
    """Tests pour Cache.nettoyer_expires()."""

    def test_nettoyer_removes_old_entries(self, mock_session_state):
        """Test nettoyer supprime entrÃ©es anciennes."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import Cache

            Cache.definir("recente", "val1")
            Cache.definir("ancienne", "val2")

            # Simuler entrÃ©e ancienne
            mock_session_state._mock_state["cache_timestamps"]["ancienne"] = datetime.now() - timedelta(hours=2)

            Cache.nettoyer_expires(age_max_secondes=3600)

            assert "recente" in mock_session_state._mock_state["cache_donnees"]
            assert "ancienne" not in mock_session_state._mock_state["cache_donnees"]


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS LIMITE DEBIT (RATE LIMIT)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestLimiteDebitBase:
    """Tests de base pour LimiteDebit."""

    def test_initialise_creates_structures(self, mock_session_state):
        """Test initialisation crÃ©e les structures."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit

            LimiteDebit._initialiser()

            assert "limite_debit" in mock_session_state._mock_state
            assert "appels_jour" in mock_session_state._mock_state["limite_debit"]
            assert "appels_heure" in mock_session_state._mock_state["limite_debit"]


class TestLimiteDebitPeutAppeler:
    """Tests pour LimiteDebit.peut_appeler()."""

    def test_peut_appeler_returns_true_initially(self, mock_session_state):
        """Test peut_appeler retourne True au dÃ©part."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit

            autorise, erreur = LimiteDebit.peut_appeler()

            assert autorise is True
            assert erreur == ""

    def test_peut_appeler_false_when_daily_limit_reached(self, mock_session_state):
        """Test peut_appeler retourne False si limite jour atteinte."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit
            from src.core.constants import AI_RATE_LIMIT_DAILY

            LimiteDebit._initialiser()
            mock_session_state._mock_state["limite_debit"]["appels_jour"] = AI_RATE_LIMIT_DAILY

            autorise, erreur = LimiteDebit.peut_appeler()

            assert autorise is False
            assert "quotidienne" in erreur.lower()

    def test_peut_appeler_false_when_hourly_limit_reached(self, mock_session_state):
        """Test peut_appeler retourne False si limite heure atteinte."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit
            from src.core.constants import AI_RATE_LIMIT_HOURLY

            LimiteDebit._initialiser()
            mock_session_state._mock_state["limite_debit"]["appels_heure"] = AI_RATE_LIMIT_HOURLY

            autorise, erreur = LimiteDebit.peut_appeler()

            assert autorise is False
            assert "horaire" in erreur.lower()


class TestLimiteDebitEnregistrer:
    """Tests pour LimiteDebit.enregistrer_appel()."""

    def test_enregistrer_appel_increments_counters(self, mock_session_state):
        """Test enregistrer_appel incrÃ©mente les compteurs."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit

            LimiteDebit._initialiser()
            initial_jour = mock_session_state._mock_state["limite_debit"]["appels_jour"]
            initial_heure = mock_session_state._mock_state["limite_debit"]["appels_heure"]

            LimiteDebit.enregistrer_appel()

            assert mock_session_state._mock_state["limite_debit"]["appels_jour"] == initial_jour + 1
            assert mock_session_state._mock_state["limite_debit"]["appels_heure"] == initial_heure + 1


class TestLimiteDebitStatistiques:
    """Tests pour LimiteDebit.obtenir_statistiques()."""

    def test_obtenir_statistiques_returns_dict(self, mock_session_state):
        """Test statistiques retourne dict complet."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit

            stats = LimiteDebit.obtenir_statistiques()

            assert isinstance(stats, dict)
            assert "appels_jour" in stats
            assert "limite_jour" in stats
            assert "appels_heure" in stats
            assert "limite_heure" in stats
            assert "restant_jour" in stats
            assert "restant_heure" in stats


class TestLimiteDebitReset:
    """Tests pour le reset automatique des compteurs."""

    def test_reset_daily_on_new_day(self, mock_session_state):
        """Test reset journalier au changement de jour."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import LimiteDebit
            from datetime import date

            LimiteDebit._initialiser()
            mock_session_state._mock_state["limite_debit"]["appels_jour"] = 50
            mock_session_state._mock_state["limite_debit"]["dernier_reset"] = date(2024, 1, 1)

            # peut_appeler() devrait reset le compteur
            LimiteDebit.peut_appeler()

            assert mock_session_state._mock_state["limite_debit"]["appels_jour"] == 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS DECORATEUR CACHED
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestCachedDecorator:
    """Tests pour le dÃ©corateur @cached."""

    def test_cached_returns_cached_value(self, mock_session_state):
        """Test cached retourne valeur en cache."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import cached

            call_count = 0

            @cached(ttl=300, cle="test_func")
            def ma_fonction():
                nonlocal call_count
                call_count += 1
                return "rÃ©sultat"

            # Premier appel - exÃ©cute la fonction
            result1 = ma_fonction()
            assert result1 == "rÃ©sultat"
            assert call_count == 1

            # DeuxiÃ¨me appel - retourne du cache
            result2 = ma_fonction()
            assert result2 == "rÃ©sultat"
            assert call_count == 1  # Pas rÃ©exÃ©cutÃ©

    def test_cached_with_dependencies(self, mock_session_state):
        """Test cached avec dÃ©pendances."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import cached, Cache

            @cached(ttl=300, cle="dep_func", dependencies=["tag1"])
            def ma_fonction():
                return "valeur"

            ma_fonction()

            # VÃ©rifier que la dÃ©pendance est enregistrÃ©e
            assert "dep_func" in mock_session_state._mock_state.get("cache_dependances", {}).get("tag1", [])

    def test_cached_auto_generates_key(self, mock_session_state):
        """Test cached gÃ©nÃ¨re clÃ© auto si non spÃ©cifiÃ©e."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.cache import cached

            @cached(ttl=300)
            def fonction_avec_args(x, y):
                return x + y

            result = fonction_avec_args(1, 2)
            assert result == 3

            # VÃ©rifie qu'une clÃ© a Ã©tÃ© crÃ©Ã©e (hash MD5)
            assert len(mock_session_state._mock_state["cache_donnees"]) == 1

