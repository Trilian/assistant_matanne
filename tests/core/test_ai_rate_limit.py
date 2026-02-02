"""
Tests pour src/core/ai/rate_limit.py
Cible: RateLimitIA - quotas, reset, statistiques
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, date, timedelta


# ═══════════════════════════════════════════════════════════
# TESTS RATE LIMIT IA
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRateLimitIA:
    """Tests pour la classe RateLimitIA."""

    @pytest.fixture
    def mock_session_state(self):
        """Fixture pour mocker st.session_state."""
        state = {}
        with patch("src.core.ai.rate_limit.st") as mock_st:
            mock_st.session_state = state
            yield state, mock_st

    def test_initialiser_creates_state(self, mock_session_state):
        """Vérifie que _initialiser crée l'état si absent."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        RateLimitIA._initialiser()
        
        assert RateLimitIA.CLE_RATE_LIMIT in state
        assert "appels_jour" in state[RateLimitIA.CLE_RATE_LIMIT]
        assert "appels_heure" in state[RateLimitIA.CLE_RATE_LIMIT]

    def test_initialiser_preserves_existing_state(self, mock_session_state):
        """Vérifie que _initialiser ne réinitialise pas un état existant."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        # Pré-remplir l'état
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 5,
            "appels_heure": 2,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        RateLimitIA._initialiser()
        
        # Les valeurs devraient être préservées
        assert state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"] == 5

    def test_peut_appeler_returns_true_when_under_limit(self, mock_session_state):
        """Vérifie que peut_appeler retourne True sous la limite."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        # Initialiser avec peu d'appels
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 1,
            "appels_heure": 1,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        autorise, message = RateLimitIA.peut_appeler()
        
        assert autorise is True
        assert message == ""

    def test_peut_appeler_returns_false_when_daily_limit_reached(self, mock_session_state):
        """Vérifie que peut_appeler retourne False si limite quotidienne atteinte."""
        from src.core.ai.rate_limit import RateLimitIA
        from src.core.constants import AI_RATE_LIMIT_DAILY
        
        state, mock_st = mock_session_state
        
        # Atteindre la limite quotidienne
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": AI_RATE_LIMIT_DAILY,
            "appels_heure": 0,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        autorise, message = RateLimitIA.peut_appeler()
        
        assert autorise is False
        assert "quotidienne" in message.lower()

    def test_peut_appeler_returns_false_when_hourly_limit_reached(self, mock_session_state):
        """Vérifie que peut_appeler retourne False si limite horaire atteinte."""
        from src.core.ai.rate_limit import RateLimitIA
        from src.core.constants import AI_RATE_LIMIT_HOURLY
        
        state, mock_st = mock_session_state
        
        # Atteindre la limite horaire
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 0,
            "appels_heure": AI_RATE_LIMIT_HOURLY,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        autorise, message = RateLimitIA.peut_appeler()
        
        assert autorise is False
        assert "horaire" in message.lower()

    def test_peut_appeler_resets_daily_counter_on_new_day(self, mock_session_state):
        """Vérifie le reset du compteur quotidien au changement de jour."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        hier = datetime.now().date() - timedelta(days=1)
        
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 100,  # Beaucoup d'appels hier
            "appels_heure": 0,
            "dernier_reset_jour": hier,  # Hier
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        autorise, message = RateLimitIA.peut_appeler()
        
        # Le compteur devrait être réinitialisé
        assert state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"] == 0
        assert autorise is True

    def test_peut_appeler_resets_hourly_counter_on_new_hour(self, mock_session_state):
        """Vérifie le reset du compteur horaire au changement d'heure."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        heure_precedente = (datetime.now() - timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 0,
            "appels_heure": 50,  # Beaucoup d'appels l'heure précédente
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": heure_precedente,
            "historique": [],
        }
        
        autorise, message = RateLimitIA.peut_appeler()
        
        # Le compteur horaire devrait être réinitialisé
        assert state[RateLimitIA.CLE_RATE_LIMIT]["appels_heure"] == 0
        assert autorise is True

    def test_enregistrer_appel_increments_counters(self, mock_session_state):
        """Vérifie que enregistrer_appel incrémente les compteurs."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 5,
            "appels_heure": 2,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        RateLimitIA.enregistrer_appel()
        
        assert state[RateLimitIA.CLE_RATE_LIMIT]["appels_jour"] == 6
        assert state[RateLimitIA.CLE_RATE_LIMIT]["appels_heure"] == 3

    def test_obtenir_statistiques_returns_dict(self, mock_session_state):
        """Vérifie que obtenir_statistiques retourne un dictionnaire."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state, mock_st = mock_session_state
        
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 10,
            "appels_heure": 3,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [{"timestamp": datetime.now(), "service": "test", "tokens": 0}],
        }
        
        stats = RateLimitIA.obtenir_statistiques()
        
        assert isinstance(stats, dict)
        assert "appels_jour" in stats
        assert "appels_heure" in stats

    def test_obtenir_statistiques_calculates_remaining(self, mock_session_state):
        """Vérifie le calcul des appels restants dans les statistiques."""
        from src.core.ai.rate_limit import RateLimitIA
        from src.core.constants import AI_RATE_LIMIT_DAILY, AI_RATE_LIMIT_HOURLY
        
        state, mock_st = mock_session_state
        
        state[RateLimitIA.CLE_RATE_LIMIT] = {
            "appels_jour": 10,
            "appels_heure": 5,
            "dernier_reset_jour": datetime.now().date(),
            "dernier_reset_heure": datetime.now().replace(minute=0, second=0, microsecond=0),
            "historique": [],
        }
        
        stats = RateLimitIA.obtenir_statistiques()
        
        assert stats["restant_jour"] == AI_RATE_LIMIT_DAILY - 10
        assert stats["restant_heure"] == AI_RATE_LIMIT_HOURLY - 5


# ═══════════════════════════════════════════════════════════
# TESTS INTEGRATION RATE LIMIT
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRateLimitIntegration:
    """Tests d'intégration pour le rate limiting."""

    def test_workflow_complet_appel_ia(self):
        """Teste le workflow complet d'un appel IA avec rate limiting."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state = {}
        
        with patch("src.core.ai.rate_limit.st") as mock_st:
            mock_st.session_state = state
            
            # 1. Vérifier qu'on peut appeler
            autorise, _ = RateLimitIA.peut_appeler()
            assert autorise is True
            
            # 2. Enregistrer l'appel
            RateLimitIA.enregistrer_appel()
            
            # 3. Vérifier les stats
            stats = RateLimitIA.obtenir_statistiques()
            assert stats["appels_jour"] == 1
            assert stats["appels_heure"] == 1

    def test_multiple_appels_increment_correctly(self):
        """Vérifie que plusieurs appels incrémentent correctement."""
        from src.core.ai.rate_limit import RateLimitIA
        
        state = {}
        
        with patch("src.core.ai.rate_limit.st") as mock_st:
            mock_st.session_state = state
            
            for i in range(5):
                RateLimitIA._initialiser()
                RateLimitIA.enregistrer_appel()
            
            stats = RateLimitIA.obtenir_statistiques()
            assert stats["appels_jour"] == 5
