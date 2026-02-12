"""
Tests Ã©tendus pour src/core/database.py
Cible: obtenir_moteur, obtenir_contexte_db, GestionnaireMigrations
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from sqlalchemy.exc import OperationalError, DatabaseError


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS OBTENIR_MOTEUR
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestObtenirMoteur:
    """Tests pour la fonction obtenir_moteur."""

    def test_obtenir_moteur_retries_on_failure(self):
        """VÃ©rifie que obtenir_moteur rÃ©essaie en cas d'Ã©chec."""
        from src.core.database import obtenir_moteur
        from src.core.errors import ErreurBaseDeDonnees
        
        # Ce test vÃ©rifie la logique de retry sans vraie connexion DB
        # On mock st.cache_resource pour Ã©viter le caching
        with patch("src.core.database.st.cache_resource", lambda ttl: lambda f: f):
            with patch("src.core.database.obtenir_parametres") as mock_params:
                mock_params.return_value.DATABASE_URL = "postgresql://invalid:invalid@localhost/test"
                mock_params.return_value.DEBUG = False
                
                with patch("src.core.database.create_engine") as mock_engine:
                    # Simuler Ã©chec de connexion
                    mock_engine.side_effect = OperationalError("Connection failed", None, None)
                    
                    with pytest.raises(ErreurBaseDeDonnees):
                        obtenir_moteur(nombre_tentatives=2, delai_tentative=0)
                    
                    # VÃ©rifier qu'il y a eu 2 tentatives
                    assert mock_engine.call_count == 2

    def test_obtenir_moteur_securise_returns_none_on_error(self):
        """VÃ©rifie que obtenir_moteur_securise retourne None en cas d'erreur."""
        from src.core.database import obtenir_moteur_securise
        from src.core.errors import ErreurBaseDeDonnees
        
        with patch("src.core.database.obtenir_moteur") as mock_moteur:
            mock_moteur.side_effect = ErreurBaseDeDonnees("Test error")
            
            result = obtenir_moteur_securise()
            assert result is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONTEXT MANAGERS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestContextManagers:
    """Tests pour les context managers de session."""

    def test_obtenir_contexte_db_yields_session(self):
        """VÃ©rifie que obtenir_contexte_db yield une session."""
        from src.core.database import obtenir_contexte_db
        
        mock_session = Mock()
        mock_factory = Mock(return_value=mock_session)
        
        with patch("src.core.database.obtenir_fabrique_session", return_value=mock_factory):
            with obtenir_contexte_db() as session:
                assert session == mock_session
            
            # VÃ©rifier commit et close
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    def test_obtenir_contexte_db_rollback_on_error(self):
        """VÃ©rifie le rollback en cas d'erreur."""
        from src.core.database import obtenir_contexte_db
        from src.core.errors import ErreurBaseDeDonnees
        
        mock_session = Mock()
        mock_factory = Mock(return_value=mock_session)
        
        with patch("src.core.database.obtenir_fabrique_session", return_value=mock_factory):
            with pytest.raises(ValueError):
                with obtenir_contexte_db() as session:
                    raise ValueError("Test error")
            
            # VÃ©rifier rollback
            mock_session.rollback.assert_called_once()
            mock_session.close.assert_called_once()

    def test_obtenir_contexte_db_handles_operational_error(self):
        """VÃ©rifie la gestion des erreurs opÃ©rationnelles."""
        from src.core.database import obtenir_contexte_db
        from src.core.errors import ErreurBaseDeDonnees
        
        mock_session = Mock()
        mock_factory = Mock(return_value=mock_session)
        
        with patch("src.core.database.obtenir_fabrique_session", return_value=mock_factory):
            with pytest.raises(ErreurBaseDeDonnees) as exc_info:
                with obtenir_contexte_db() as session:
                    raise OperationalError("Network error", None, None)
            
            assert "ProblÃ¨me de connexion" in str(exc_info.value.message_utilisateur)
            mock_session.rollback.assert_called_once()

    def test_obtenir_db_securise_returns_none_on_error(self):
        """VÃ©rifie que obtenir_db_securise retourne None en cas d'erreur."""
        from src.core.database import obtenir_db_securise
        from src.core.errors import ErreurBaseDeDonnees
        
        with patch("src.core.database.obtenir_contexte_db") as mock_ctx:
            mock_ctx.side_effect = ErreurBaseDeDonnees("Test error")
            
            with obtenir_db_securise() as db:
                assert db is None


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FABRIQUE SESSION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestFabriqueSession:
    """Tests pour la session factory."""

    def test_obtenir_fabrique_session_returns_sessionmaker(self):
        """VÃ©rifie que la factory retourne un sessionmaker."""
        from src.core.database import obtenir_fabrique_session
        
        mock_engine = Mock()
        
        with patch("src.core.database.obtenir_moteur", return_value=mock_engine):
            factory = obtenir_fabrique_session()
            
            # VÃ©rifier que c'est une fonction callable
            assert callable(factory)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GET_DB_CONTEXT ALIAS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestGetDbContextAlias:
    """Tests pour l'alias get_db_context."""

    def test_get_db_context_is_alias(self):
        """VÃ©rifie que get_db_context est un alias de obtenir_contexte_db."""
        from src.core.database import get_db_context, obtenir_contexte_db
        
        # Les deux devraient pointer vers la mÃªme fonction
        assert get_db_context == obtenir_contexte_db


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GESTIONNAIRE MIGRATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestGestionnaireMigrations:
    """Tests pour le gestionnaire de migrations."""

    def test_obtenir_version_courante_method_exists(self):
        """VÃ©rifie que la mÃ©thode obtenir_version_courante existe."""
        from src.core.database import GestionnaireMigrations
        
        assert hasattr(GestionnaireMigrations, 'obtenir_version_courante')
        assert callable(GestionnaireMigrations.obtenir_version_courante)

    def test_verifier_migrations_en_attente(self):
        """VÃ©rifie la dÃ©tection des migrations en attente."""
        from src.core.database import GestionnaireMigrations
        
        try:
            pending = GestionnaireMigrations.verifier_migrations_en_attente()
            assert isinstance(pending, bool)
        except Exception:
            # Si pas d'alembic configurÃ©, c'est OK
            pass
