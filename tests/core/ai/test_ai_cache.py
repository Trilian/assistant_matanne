"""
Tests pour src/core/ai/cache.py - Cache IA.
"""

from unittest.mock import MagicMock, patch

import pytest


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

    def test_obtenir_returns_none_if_not_cached(self):
        """Test obtenir retourne None si non caché."""
        from src.core.ai.cache import CacheIA

        result = CacheIA.obtenir("prompt_inexistant")
        assert result is None

    def test_obtenir_returns_cached_value(self):
        """Test obtenir retourne valeur cachée."""
        from src.core.ai.cache import CacheIA

        CacheIA.definir("mon prompt", "réponse IA", "system", 0.7, "mistral")
        result = CacheIA.obtenir("mon prompt", "system", 0.7, "mistral")
        assert result == "réponse IA"

    def test_obtenir_with_custom_ttl(self):
        """Test obtenir avec TTL personnalisé."""
        from src.core.ai.cache import CacheIA

        CacheIA.definir("prompt", "réponse")
        result = CacheIA.obtenir("prompt", ttl=3600)
        assert result == "réponse"

    def test_obtenir_semantique_prompt_proche(self):
        """Le cache sémantique retrouve une réponse pour un prompt proche."""
        from src.core.ai.cache import CacheIA

        CacheIA.invalider_tout()
        CacheIA.definir(
            "Propose un menu familial rapide pour ce soir",
            "Menu: omelette, salade et soupe.",
            systeme="assistant cuisine",
            temperature=0.7,
            modele="mistral-large",
        )

        result = CacheIA.obtenir(
            "Propose un menu familial rapide ce soir",
            systeme="assistant cuisine",
            temperature=0.7,
            modele="mistral-large",
        )
        assert result == "Menu: omelette, salade et soupe."

    def test_obtenir_semantique_ignore_contexte_diff(self):
        """Le cache sémantique reste isolé par système/modèle."""
        from src.core.ai.cache import CacheIA

        CacheIA.invalider_tout()
        CacheIA.definir(
            "Résume le planning de demain",
            "Résumé planning",
            systeme="assistant planning",
            temperature=0.7,
            modele="mistral-large",
        )

        result = CacheIA.obtenir(
            "Résume mon planning demain",
            systeme="assistant budget",
            temperature=0.7,
            modele="mistral-large",
        )
        assert result is None


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA DEFINIR
# ═══════════════════════════════════════════════════════════


class TestCacheIADefinir:
    """Tests pour CacheIA.definir()."""

    def test_definir_stores_value(self):
        """Test definir stocke la valeur."""
        from src.core.ai.cache import CacheIA

        CacheIA.definir("prompt", "réponse IA")
        result = CacheIA.obtenir("prompt")
        assert result == "réponse IA"

    def test_definir_with_all_params(self):
        """Test definir avec tous les paramètres."""
        from src.core.ai.cache import CacheIA

        CacheIA.definir(
            prompt="Génère une recette",
            reponse="Voici une recette...",
            systeme="Tu es un chef",
            temperature=0.8,
            modele="mistral-large",
        )

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

    def test_invalider_tout_clears_ia_cache(self):
        """Test invalider_tout efface le cache IA."""
        from src.core.ai.cache import CacheIA

        CacheIA.definir("prompt1", "réponse1")
        CacheIA.definir("prompt2", "réponse2")

        CacheIA.invalider_tout()

        assert CacheIA.obtenir("prompt1") is None
        assert CacheIA.obtenir("prompt2") is None


# ═══════════════════════════════════════════════════════════
# TESTS CACHE IA STATISTIQUES
# ═══════════════════════════════════════════════════════════


class TestCacheIAStatistiques:
    """Tests pour CacheIA.obtenir_statistiques()."""

    def test_statistiques_returns_dict(self):
        """Test statistiques retourne dict."""
        from src.core.ai.cache import CacheIA

        stats = CacheIA.obtenir_statistiques()
        assert isinstance(stats, dict)

    def test_statistiques_contains_expected_keys(self):
        """Test statistiques contient les clés attendues."""
        from src.core.ai.cache import CacheIA

        stats = CacheIA.obtenir_statistiques()
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


# ═══════════════════════════════════════════════════════════
# TESTS NETTOYER CACHE EXPIRE
# ═══════════════════════════════════════════════════════════


class TestCacheIANettoyerExpires:
    """Tests pour CacheIA.nettoyer_expires()."""

    def test_nettoyer_expires_calls_cache_nettoyer(self):
        """Test nettoyer_expires appelle le nettoyage du cache L1."""
        from src.core.ai.cache import CacheIA

        with patch("src.core.ai.cache._cache") as mock_cache_fn:
            mock_l1 = MagicMock()
            mock_cache_fn.return_value.l1 = mock_l1
            CacheIA.nettoyer_expires()
            mock_l1.cleanup_expired.assert_called_once()

    def test_nettoyer_expires_with_custom_age(self):
        """Test nettoyer_expires avec âge personnalisé."""
        from src.core.ai.cache import CacheIA

        age_custom = 3600
        with patch("src.core.ai.cache._cache") as mock_cache_fn:
            mock_l1 = MagicMock()
            mock_cache_fn.return_value.l1 = mock_l1
            CacheIA.nettoyer_expires(age_max_secondes=age_custom)
            mock_l1.cleanup_expired.assert_called_once()

    def test_nettoyer_expires_logs_info(self, caplog):
        """Test nettoyer_expires écrit dans les logs."""
        import logging

        from src.core.ai.cache import CacheIA

        with patch("src.core.ai.cache._cache") as mock_cache_fn:
            mock_l1 = MagicMock()
            mock_cache_fn.return_value.l1 = mock_l1
            with caplog.at_level(logging.INFO):
                CacheIA.nettoyer_expires(age_max_secondes=1800)

            assert any("Nettoyage cache IA" in record.message for record in caplog.records)
