"""
Tests pour src/core/ai/cache.py - Cache IA avec mocks Streamlit.
"""

import hashlib
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_session_state():
    """Mock st.session_state pour tests isolés."""
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
    mock._mock_state = mock_state

    return mock


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA GENERATION CLE
# ═══════════════════════════════════════════════════════════


class TestCacheIAGenererCle:
    """Tests pour CacheIA.generer_cle()."""

    def test_generer_cle_returns_string(self):
        """Test génération clé retourne string."""
        from src.core.ai.cache import CacheIA

        cle = CacheIA.generer_cle("Mon prompt", "System", 0.7, "mistral")

        assert isinstance(cle, str)

    def test_generer_cle_prefixee(self):
        """Test clé préfixée avec ia_."""
        from src.core.ai.cache import CacheIA

        cle = CacheIA.generer_cle("Mon prompt")

        assert cle.startswith("ia_")

    def test_generer_cle_deterministe(self):
        """Test génération déterministe (même entrée = même clé)."""
        from src.core.ai.cache import CacheIA

        cle1 = CacheIA.generer_cle("prompt", "sys", 0.7, "model")
        cle2 = CacheIA.generer_cle("prompt", "sys", 0.7, "model")

        assert cle1 == cle2

    def test_generer_cle_differente_pour_prompts_differents(self):
        """Test clés différentes pour prompts différents."""
        from src.core.ai.cache import CacheIA

        cle1 = CacheIA.generer_cle("prompt1")
        cle2 = CacheIA.generer_cle("prompt2")

        assert cle1 != cle2

    def test_generer_cle_differente_pour_temperatures_differentes(self):
        """Test clés différentes pour températures différentes."""
        from src.core.ai.cache import CacheIA

        cle1 = CacheIA.generer_cle("prompt", temperature=0.5)
        cle2 = CacheIA.generer_cle("prompt", temperature=0.9)

        assert cle1 != cle2

    def test_generer_cle_hash_md5(self):
        """Test que la clé utilise un hash MD5."""
        from src.core.ai.cache import CacheIA

        cle = CacheIA.generer_cle("test")

        # Après préfixe, devrait être un hash MD5 (32 caractères hex)
        hash_part = cle[3:]  # Enlever "ia_"
        assert len(hash_part) == 32
        assert all(c in "0123456789abcdef" for c in hash_part)


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA OBTENIR
# ═══════════════════════════════════════════════════════════


class TestCacheIAObtenir:
    """Tests pour CacheIA.obtenir()."""

    def test_obtenir_returns_none_if_not_cached(self, mock_session_state):
        """Test obtenir retourne None si non caché."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            result = CacheIA.obtenir("prompt_inexistant")

            assert result is None

    def test_obtenir_returns_cached_value(self, mock_session_state):
        """Test obtenir retourne valeur cachée."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            # Définir d'abord
            CacheIA.definir("mon prompt", "réponse IA", "system", 0.7, "mistral")

            # Obtenir
            result = CacheIA.obtenir("mon prompt", "system", 0.7, "mistral")

            assert result == "réponse IA"

    def test_obtenir_with_custom_ttl(self, mock_session_state):
        """Test obtenir avec TTL personnalisé."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            CacheIA.definir("prompt", "réponse")

            # Devrait retourner avec TTL court
            result = CacheIA.obtenir("prompt", ttl=3600)

            assert result == "réponse"


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA DEFINIR
# ═══════════════════════════════════════════════════════════


class TestCacheIADefinir:
    """Tests pour CacheIA.definir()."""

    def test_definir_stores_value(self, mock_session_state):
        """Test definir stocke la valeur."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            CacheIA.definir("prompt", "réponse IA")

            # Vérifier via obtenir
            result = CacheIA.obtenir("prompt")
            assert result == "réponse IA"

    def test_definir_with_all_params(self, mock_session_state):
        """Test definir avec tous les paramètres."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            CacheIA.definir(
                prompt="Génère une recette",
                reponse="Voici une recette...",
                systeme="Tu es un chef",
                temperature=0.8,
                modele="mistral-large",
            )

            # Vérifier via obtenir avec mêmes params
            result = CacheIA.obtenir(
                prompt="Génère une recette",
                systeme="Tu es un chef",
                temperature=0.8,
                modele="mistral-large",
            )

            assert result == "Voici une recette..."


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA INVALIDER
# ═══════════════════════════════════════════════════════════


class TestCacheIAInvalider:
    """Tests pour CacheIA.invalider_tout()."""

    def test_invalider_tout_clears_ia_cache(self, mock_session_state):
        """Test invalider_tout efface le cache IA."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            # Ajouter des entrées
            CacheIA.definir("prompt1", "réponse1")
            CacheIA.definir("prompt2", "réponse2")

            # Invalider
            CacheIA.invalider_tout()

            # Vérifier suppression
            assert CacheIA.obtenir("prompt1") is None
            assert CacheIA.obtenir("prompt2") is None


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCacheIAStatistiques:
    """Tests pour CacheIA.obtenir_statistiques()."""

    def test_statistiques_returns_dict(self, mock_session_state):
        """Test statistiques retourne dict."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            stats = CacheIA.obtenir_statistiques()

            assert isinstance(stats, dict)

    def test_statistiques_contains_expected_keys(self, mock_session_state):
        """Test statistiques contient les clés attendues."""
        with patch("streamlit.session_state", mock_session_state):
            from src.core.ai.cache import CacheIA

            stats = CacheIA.obtenir_statistiques()

            # Le cache IA a ses propres clés
            assert "entrees_ia" in stats or "taux_hit" in stats or len(stats) > 0


# ═══════════════════════════════════════════════════════════
# TESTS PREFIXE ET TTL
# ═══════════════════════════════════════════════════════════


class TestCacheIAConstants:
    """Tests pour constantes CacheIA."""

    def test_prefixe_constant(self):
        """Test préfixe constant."""
        from src.core.ai.cache import CacheIA

        assert CacheIA.PREFIXE == "ia_"

    def test_ttl_par_defaut(self):
        """Test TTL par défaut défini."""
        from src.core.ai.cache import CacheIA

        assert CacheIA.TTL_PAR_DEFAUT > 0
        # Généralement 1h = 3600s
        assert CacheIA.TTL_PAR_DEFAUT >= 3600
