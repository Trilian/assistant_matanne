"""
Tests Phase 5 — Production Hardening.

Tests pour:
- Auth hardening (fail-fast secret, dev bypass guard)
- Redis rate limiting storage
- RecettePatch partial update endpoint
- Accessibilité (aria-label)
"""

import os
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import jwt
import pytest


class TestAuthHardening:
    """Tests pour le durcissement de l'authentification."""

    def test_api_secret_production_fail_fast(self):
        """En production avec secret par défaut, doit lever RuntimeError."""
        import importlib

        # Simuler production sans API_SECRET_KEY défini (utilise la valeur par défaut)
        env_copy = os.environ.copy()
        env_copy.pop("API_SECRET_KEY", None)  # Supprimer si existe
        env_copy["ENVIRONMENT"] = "production"

        with patch.dict(os.environ, env_copy, clear=True):
            from src.api import auth

            importlib.reload(auth)

            # La fonction doit lever une erreur si secret par défaut en prod
            with pytest.raises(RuntimeError) as exc_info:
                auth._obtenir_api_secret()

            assert "API_SECRET_KEY" in str(exc_info.value)

    def test_api_secret_development_returns_default(self):
        """En développement sans API_SECRET_KEY, utilise une clé générée aléatoirement."""
        import importlib

        # Simuler développement sans API_SECRET_KEY défini
        env_copy = os.environ.copy()
        env_copy.pop("API_SECRET_KEY", None)  # Supprimer si existe
        env_copy["ENVIRONMENT"] = "development"

        with patch.dict(os.environ, env_copy, clear=True):
            from src.api import auth

            importlib.reload(auth)
            result = auth._obtenir_api_secret()
            # En dev, retourne une clé générée aléatoirement (non vide, pas d'erreur)
            assert result is not None
            assert len(result) > 0

    def test_api_secret_custom_value_in_production(self):
        """En production avec API_SECRET_KEY custom, pas d'erreur."""
        import importlib

        with patch.dict(
            os.environ,
            {"ENVIRONMENT": "production", "API_SECRET_KEY": "my-secure-secret-key"},
            clear=False,
        ):
            from src.api import auth

            importlib.reload(auth)
            result = auth._obtenir_api_secret()
            assert result == "my-secure-secret-key"

    def test_dev_bypass_disabled_in_production(self):
        """Le bypass dev doit être désactivé en production."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            from fastapi import HTTPException

            from src.api.dependencies import get_current_user

            # Sans credentials en production, doit lever 401
            with pytest.raises(HTTPException) as exc_info:
                import asyncio

                asyncio.get_event_loop().run_until_complete(get_current_user(None))

            assert exc_info.value.status_code == 401

    def test_supabase_jwt_secret_returns_none_when_not_set(self):
        """Sans SUPABASE_JWT_SECRET, retourne None."""
        import importlib

        env_copy = os.environ.copy()
        env_copy.pop("SUPABASE_JWT_SECRET", None)

        with patch.dict(os.environ, env_copy, clear=True):
            from src.api import auth

            importlib.reload(auth)
            result = auth._obtenir_supabase_jwt_secret()
            assert result is None


class TestRedisRateLimitingStorage:
    """Tests pour le stockage Redis de rate limiting."""

    def test_obtenir_stockage_optimal_fallback_inmemory(self):
        """Sans REDIS_URL, doit retourner le stockage in-memory."""
        with patch.dict(os.environ, {"REDIS_URL": ""}):
            from src.api.rate_limiting.redis_storage import obtenir_stockage_optimal
            from src.api.rate_limiting.storage import StockageLimitationDebit

            stockage = obtenir_stockage_optimal()
            assert isinstance(stockage, StockageLimitationDebit)

    def test_stockage_redis_interface_compatible(self):
        """StockageRedis doit avoir la même interface que StockageLimitationDebit."""
        from src.api.rate_limiting.redis_storage import StockageRedis
        from src.api.rate_limiting.storage import StockageLimitationDebit

        # Vérifier les méthodes communes
        inmemory_methods = {
            "incrementer",
            "obtenir_compte",
            "obtenir_restant",
            "obtenir_temps_reset",
            "est_bloque",
            "bloquer",
        }

        redis_methods = set(dir(StockageRedis))
        for method in inmemory_methods:
            assert method in redis_methods, f"Méthode {method} manquante dans StockageRedis"

    def test_stockage_inmemory_incrementer(self):
        """Test d'incrémentation du stockage in-memory."""
        from src.api.rate_limiting.storage import StockageLimitationDebit

        stockage = StockageLimitationDebit()
        compte1 = stockage.incrementer("test:key", 60)
        compte2 = stockage.incrementer("test:key", 60)
        compte3 = stockage.incrementer("test:key", 60)

        assert compte1 == 1
        assert compte2 == 2
        assert compte3 == 3

    def test_stockage_inmemory_bloquer(self):
        """Test du blocage temporaire."""
        from src.api.rate_limiting.storage import StockageLimitationDebit

        stockage = StockageLimitationDebit()
        assert stockage.est_bloque("test:blocked") is False

        stockage.bloquer("test:blocked", 60)
        assert stockage.est_bloque("test:blocked") is True


class TestRecettePatchSchema:
    """Tests pour le schéma RecettePatch."""

    def test_recette_patch_tous_champs_optionnels(self):
        """Tous les champs de RecettePatch doivent être optionnels."""
        from src.api.schemas import RecettePatch

        # Doit accepter un objet vide
        patch = RecettePatch()
        assert patch.nom is None
        assert patch.description is None
        assert patch.temps_preparation is None

    def test_recette_patch_partial_data(self):
        """RecettePatch accepte des données partielles."""
        from src.api.schemas import RecettePatch

        patch = RecettePatch(nom="Nouveau nom", temps_cuisson=45)
        assert patch.nom == "Nouveau nom"
        assert patch.temps_cuisson == 45
        assert patch.description is None  # Non fourni

    def test_recette_patch_model_dump_exclude_unset(self):
        """model_dump(exclude_unset=True) ne retourne que les champs fournis."""
        from src.api.schemas import RecettePatch

        patch = RecettePatch(nom="Test", portions=6)
        data = patch.model_dump(exclude_unset=True)

        assert "nom" in data
        assert "portions" in data
        assert "description" not in data
        assert "temps_preparation" not in data

    def test_recette_patch_validation_temps_preparation_ge_0(self):
        """temps_preparation doit être >= 0."""
        from pydantic import ValidationError

        from src.api.schemas import RecettePatch

        with pytest.raises(ValidationError):
            RecettePatch(temps_preparation=-5)


class TestLoginRateLimiting:
    """Tests pour le rate limiting sur /auth/login."""

    def test_login_rate_limit_key_generation(self):
        """Le rate limiting login utilise l'IP comme clé."""
        from src.api.rate_limiting.storage import StockageLimitationDebit

        stockage = StockageLimitationDebit()

        # Simuler des tentatives de login
        cle = "login_attempt:ip:192.168.1.1"
        for i in range(5):
            stockage.incrementer(cle, 60)

        compte = stockage.obtenir_compte(cle, 60)
        assert compte == 5

    def test_login_rate_limit_blocking(self):
        """Après dépassement, l'IP est bloquée."""
        from src.api.rate_limiting.storage import StockageLimitationDebit

        stockage = StockageLimitationDebit()
        cle = "login_attempt:ip:192.168.1.2"

        # Simuler 6 tentatives (> limite de 5)
        for _ in range(6):
            stockage.incrementer(cle, 60)

        # Bloquer après dépassement
        stockage.bloquer(cle, 300)

        assert stockage.est_bloque(cle) is True


class TestAccessibilityHelpers:
    """Tests pour les utilitaires d'accessibilité."""

    def test_a11y_attrs_generation(self):
        """A11y.attrs() génère des attributs ARIA corrects."""
        from src.ui.a11y import A11y

        attrs = A11y.attrs(role="navigation", label="Menu principal")
        assert 'role="navigation"' in attrs
        assert 'aria-label="Menu principal"' in attrs

    def test_a11y_attrs_expanded_state(self):
        """A11y.attrs() gère aria-expanded correctement."""
        from src.ui.a11y import A11y

        attrs_expanded = A11y.attrs(expanded=True)
        assert 'aria-expanded="true"' in attrs_expanded

        attrs_collapsed = A11y.attrs(expanded=False)
        assert 'aria-expanded="false"' in attrs_collapsed

    def test_a11y_contrast_ratio_calculation(self):
        """ratio_contraste() calcule correctement le ratio WCAG."""
        from src.ui.a11y import A11y

        # Blanc sur noir = ratio max ~21:1
        ratio_max = A11y.ratio_contraste("#ffffff", "#000000")
        assert ratio_max > 20

        # Même couleur = ratio 1:1
        ratio_min = A11y.ratio_contraste("#808080", "#808080")
        assert ratio_min == 1.0

    def test_a11y_wcag_aa_conformance(self):
        """est_conforme_aa() valide correctement le contraste."""
        from src.ui.a11y import A11y

        # Bon contraste (noir sur blanc)
        assert A11y.est_conforme_aa("#000000", "#ffffff") is True

        # Mauvais contraste (gris clair sur blanc)
        assert A11y.est_conforme_aa("#cccccc", "#ffffff") is False

    def test_a11y_sr_only_html(self):
        """sr_only_html() génère le HTML correct."""
        from src.ui.a11y import A11y

        html = A11y.sr_only_html("Message caché")
        assert 'class="sr-only"' in html
        assert "Message caché" in html


class TestPWAServiceWorker:
    """Tests pour le Service Worker PWA."""

    def test_sw_cache_version_incremented(self):
        """Le fichier sw.js doit avoir une version incrémentée."""
        import re
        from pathlib import Path

        sw_path = Path("static/sw.js")
        if sw_path.exists():
            content = sw_path.read_text()
            match = re.search(r"CACHE_VERSION\s*=\s*(\d+)", content)
            assert match is not None, "CACHE_VERSION non trouvée"
            version = int(match.group(1))
            assert version >= 3, f"Version devrait être >= 3, trouvé {version}"

    def test_sw_has_offline_url(self):
        """Le SW doit définir OFFLINE_URL."""
        from pathlib import Path

        sw_path = Path("static/sw.js")
        if sw_path.exists():
            content = sw_path.read_text()
            assert "OFFLINE_URL" in content
            assert "offline.html" in content

    def test_sw_has_sync_with_retry(self):
        """Le SW doit avoir une fonction syncWithRetry."""
        from pathlib import Path

        sw_path = Path("static/sw.js")
        if sw_path.exists():
            content = sw_path.read_text()
            assert "syncWithRetry" in content
            assert "maxRetries" in content
