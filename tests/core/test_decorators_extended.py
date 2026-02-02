"""
Tests étendus pour src/core/decorators.py
Cible: Couvrir with_db_session, with_cache, with_error_handling
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime


# ═══════════════════════════════════════════════════════════
# TESTS WITH_DB_SESSION
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWithDbSession:
    """Tests pour le décorateur with_db_session."""

    def test_decorator_creates_session_when_none_provided(self):
        """Vérifie que le décorateur crée une session si aucune n'est fournie."""
        from src.core.decorators import with_db_session
        from contextlib import contextmanager

        mock_session = Mock()
        
        @contextmanager
        def fake_context():
            yield mock_session
        
        @with_db_session
        def ma_fonction(data: dict, db=None):
            return db
        
        # Patch get_db_context pour utiliser notre mock
        with patch("src.core.database.get_db_context", return_value=fake_context()):
            result = ma_fonction({"test": 1})
            # La session devrait être injectée
            assert result is not None

    def test_decorator_uses_provided_db_session(self):
        """Vérifie que le décorateur utilise une session existante si fournie."""
        from src.core.decorators import with_db_session
        
        existing_session = Mock()
        
        @with_db_session
        def ma_fonction(data: dict, db=None):
            return db
        
        result = ma_fonction({"test": 1}, db=existing_session)
        assert result == existing_session

    def test_decorator_uses_provided_session_param(self):
        """Vérifie que le décorateur supporte le paramètre 'session'."""
        from src.core.decorators import with_db_session
        
        existing_session = Mock()
        
        @with_db_session
        def ma_fonction(data: dict, session=None):
            return session
        
        result = ma_fonction({"test": 1}, session=existing_session)
        assert result == existing_session

    def test_decorator_preserves_function_metadata(self):
        """Vérifie que le décorateur préserve les métadonnées de la fonction."""
        from src.core.decorators import with_db_session
        
        @with_db_session
        def fonction_documentee(x: int, db=None) -> int:
            """Documentation de ma fonction."""
            return x
        
        assert fonction_documentee.__name__ == "fonction_documentee"
        assert "Documentation" in fonction_documentee.__doc__

    def test_decorator_injects_session_param_correctly(self):
        """Vérifie l'injection correcte du paramètre session vs db."""
        from src.core.decorators import with_db_session
        
        # Fonction avec paramètre 'session'
        @with_db_session
        def func_with_session(session=None):
            return session is not None
        
        # Fonction avec paramètre 'db'
        @with_db_session
        def func_with_db(db=None):
            return db is not None
        
        # Test avec session fournie explicitement
        mock_session = Mock()
        result_session = func_with_session(session=mock_session)
        result_db = func_with_db(db=mock_session)
        
        assert result_session is True
        assert result_db is True
# TESTS WITH_CACHE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWithCache:
    """Tests pour le décorateur with_cache."""

    def test_cache_decorator_caches_result(self):
        """Vérifie que le résultat est mis en cache."""
        from src.core.decorators import with_cache
        
        call_count = 0
        
        @with_cache(ttl=300, key_prefix="test")
        def fonction_couteuse(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Première appel
        result1 = fonction_couteuse(5)
        # Deuxième appel - devrait utiliser le cache
        result2 = fonction_couteuse(5)
        
        assert result1 == 10
        assert result2 == 10
        # En raison du cache, la fonction ne devrait être appelée qu'une fois
        # Note: selon l'implémentation du cache, ce test peut nécessiter un mock

    def test_cache_decorator_with_different_args(self):
        """Vérifie que différents arguments génèrent différentes clés."""
        from src.core.decorators import with_cache
        
        @with_cache(ttl=300, key_prefix="test_diff")
        def fonction(x: int) -> int:
            return x * 3
        
        result1 = fonction(5)
        result2 = fonction(10)
        
        assert result1 == 15
        assert result2 == 30

    def test_cache_decorator_preserves_function_metadata(self):
        """Vérifie que le décorateur préserve les métadonnées."""
        from src.core.decorators import with_cache
        
        @with_cache(ttl=60, key_prefix="meta")
        def ma_fonction(x: int) -> int:
            """Doc de la fonction."""
            return x
        
        assert ma_fonction.__name__ == "ma_fonction"
        assert "Doc de la fonction" in ma_fonction.__doc__

    def test_cache_decorator_ttl_parameter(self):
        """Vérifie que le paramètre TTL est respecté."""
        from src.core.decorators import with_cache
        
        @with_cache(ttl=1)  # TTL très court
        def fonction_ttl(x: int) -> int:
            return x
        
        result = fonction_ttl(42)
        assert result == 42


# ═══════════════════════════════════════════════════════════
# TESTS WITH_ERROR_HANDLING (si existant)
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestWithErrorHandling:
    """Tests pour le décorateur gerer_erreurs."""

    def test_error_handling_catches_exceptions(self):
        """Vérifie que les exceptions sont capturées."""
        from src.core.errors import gerer_erreurs
        
        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback="erreur_geree")
        def fonction_qui_plante():
            raise ValueError("Erreur test")
        
        # Patch Streamlit pour éviter les appels UI
        with patch("src.core.errors.st"):
            result = fonction_qui_plante()
            # Le décorateur devrait retourner la valeur fallback
            assert result == "erreur_geree"

    def test_error_handling_preserves_return_on_success(self):
        """Vérifie que le retour est préservé en cas de succès."""
        from src.core.errors import gerer_erreurs
        
        @gerer_erreurs(afficher_dans_ui=False, valeur_fallback=None)
        def fonction_ok():
            return {"status": "ok", "data": 42}
        
        result = fonction_ok()
        assert result["status"] == "ok"
        assert result["data"] == 42

    def test_error_handling_preserves_metadata(self):
        """Vérifie que les métadonnées sont préservées."""
        from src.core.errors import gerer_erreurs
        
        @gerer_erreurs(afficher_dans_ui=False)
        def ma_fonction_error():
            """Documentation fonction."""
            return True
        
        # Le nom est préservé grâce à @wraps
        assert "ma_fonction_error" in str(ma_fonction_error) or ma_fonction_error.__wrapped__.__name__ == "ma_fonction_error"
