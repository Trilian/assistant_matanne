"""
Tests unitaires - Module Multi-Tenant (Isolation Données)

Couverture complète :
- UserContext (contexte utilisateur courant)
- Context managers (user_context, admin_context)
- Décorateurs @with_user_isolation, @require_user
- MultiTenantQuery (helper requêtes)
- MultiTenantService (service base)

Architecture : 5 sections de tests (UserContext, Decorators, Query, Service, Integration)
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.multi_tenant import (
    UserContext,
    admin_context,
    user_context,
    with_user_isolation,
    require_user,
    MultiTenantQuery,
    MultiTenantService,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: USER CONTEXT
# ═══════════════════════════════════════════════════════════


class TestUserContext:
    """Tests pour UserContext."""

    def setup_method(self):
        """Préparation avant chaque test."""
        UserContext.clear()

    @pytest.mark.unit
    def test_set_get_user(self):
        """Test définition et récupération utilisateur."""
        UserContext.set_user("user-123")
        
        assert UserContext.get_user() == "user-123"

    @pytest.mark.unit
    def test_clear_user_context(self):
        """Test effacement contexte utilisateur."""
        UserContext.set_user("user-123")
        
        assert UserContext.get_user() == "user-123"
        
        UserContext.clear()
        
        assert UserContext.get_user() is None
        assert UserContext.is_bypassed() is False

    @pytest.mark.unit
    def test_get_user_no_context(self):
        """Test récupération utilisateur sans contexte."""
        UserContext.clear()
        
        result = UserContext.get_user()
        
        assert result is None

    @pytest.mark.unit
    def test_set_bypass(self):
        """Test activation bypass isolation."""
        assert UserContext.is_bypassed() is False
        
        UserContext.set_bypass(True)
        assert UserContext.is_bypassed() is True
        
        UserContext.set_bypass(False)
        assert UserContext.is_bypassed() is False

    @pytest.mark.unit
    def test_multiple_users_sequential(self):
        """Test changement utilisateur séquentiel."""
        UserContext.set_user("user-1")
        assert UserContext.get_user() == "user-1"
        
        UserContext.set_user("user-2")
        assert UserContext.get_user() == "user-2"
        
        UserContext.set_user("user-3")
        assert UserContext.get_user() == "user-3"


# ═══════════════════════════════════════════════════════════
# SECTION 2: CONTEXT MANAGERS
# ═══════════════════════════════════════════════════════════


class TestContextManagers:
    """Tests pour context managers."""

    def setup_method(self):
        """Préparation avant chaque test."""
        UserContext.clear()

    @pytest.mark.unit
    def test_user_context_manager(self):
        """Test context manager utilisateur."""
        UserContext.set_user("initial")
        
        with user_context("temporary"):
            assert UserContext.get_user() == "temporary"
        
        assert UserContext.get_user() == "initial"

    @pytest.mark.unit
    def test_user_context_nested(self):
        """Test context manager imbriqués."""
        UserContext.set_user("outer")
        
        with user_context("middle"):
            assert UserContext.get_user() == "middle"
            
            with user_context("inner"):
                assert UserContext.get_user() == "inner"
            
            assert UserContext.get_user() == "middle"
        
        assert UserContext.get_user() == "outer"

    @pytest.mark.unit
    def test_user_context_exception(self):
        """Test context manager avec exception."""
        UserContext.set_user("initial")
        
        try:
            with user_context("temporary"):
                assert UserContext.get_user() == "temporary"
                raise ValueError("Test error")
        except ValueError:
            pass
        
        # Devrait restaurer même après exception
        assert UserContext.get_user() == "initial"

    @pytest.mark.unit
    def test_admin_context_manager(self):
        """Test context manager admin."""
        assert UserContext.is_bypassed() is False
        
        with admin_context():
            assert UserContext.is_bypassed() is True
        
        assert UserContext.is_bypassed() is False

    @pytest.mark.unit
    def test_admin_context_nested(self):
        """Test context manager admin imbriqué."""
        with admin_context():
            assert UserContext.is_bypassed() is True
            
            with admin_context():
                assert UserContext.is_bypassed() is True
            
            assert UserContext.is_bypassed() is True
        
        assert UserContext.is_bypassed() is False

    @pytest.mark.unit
    def test_combined_contexts(self):
        """Test combinaison user_context et admin_context."""
        with user_context("user-1"):
            assert UserContext.get_user() == "user-1"
            
            with admin_context():
                assert UserContext.get_user() == "user-1"
                assert UserContext.is_bypassed() is True
            
            assert UserContext.is_bypassed() is False


# ═══════════════════════════════════════════════════════════
# SECTION 3: DÉCORATEURS
# ═══════════════════════════════════════════════════════════


class TestDecorators:
    """Tests pour décorateurs multi-tenant."""

    def setup_method(self):
        """Préparation avant chaque test."""
        UserContext.clear()

    @pytest.mark.unit
    def test_with_user_isolation_decorator(self):
        """Test décorateur @with_user_isolation."""
        UserContext.set_user("user-123")
        
        @with_user_isolation()
        def get_data(user_id: str = None) -> str:
            return user_id
        
        result = get_data()
        
        assert result == "user-123"

    @pytest.mark.unit
    def test_with_user_isolation_explicit_user(self):
        """Test décorateur avec user_id explicite."""
        UserContext.set_user("user-123")
        
        @with_user_isolation()
        def get_data(user_id: str = None) -> str:
            return user_id
        
        result = get_data(user_id="explicit-user")
        
        assert result == "explicit-user"

    @pytest.mark.unit
    def test_with_user_isolation_no_context(self):
        """Test décorateur sans contexte utilisateur."""
        UserContext.clear()
        
        @with_user_isolation()
        def get_data(user_id: str = None) -> str:
            return user_id
        
        result = get_data()
        
        assert result is None

    @pytest.mark.unit
    def test_with_user_isolation_bypass(self):
        """Test décorateur avec bypass activation."""
        UserContext.set_user("user-123")
        UserContext.set_bypass(True)
        
        @with_user_isolation()
        def get_data(user_id: str = None) -> str:
            return user_id
        
        result = get_data()
        
        # Bypass empêche injection user_id
        assert result is None

    @pytest.mark.unit
    def test_require_user_decorator_success(self):
        """Test décorateur @require_user avec utilisateur."""
        UserContext.set_user("user-123")
        
        @require_user()
        def create_data() -> str:
            return "created"
        
        result = create_data()
        
        assert result == "created"

    @pytest.mark.unit
    def test_require_user_decorator_fail(self):
        """Test décorateur @require_user sans utilisateur."""
        UserContext.clear()
        
        @require_user()
        def create_data() -> str:
            return "created"
        
        with pytest.raises(PermissionError):
            create_data()

    @pytest.mark.unit
    def test_require_user_decorator_bypass(self):
        """Test décorateur @require_user avec bypass."""
        UserContext.clear()
        UserContext.set_bypass(True)
        
        @require_user()
        def create_data() -> str:
            return "created"
        
        # Bypass permet accès sans utilisateur
        result = create_data()
        assert result == "created"


# ═══════════════════════════════════════════════════════════
# SECTION 4: MULTI-TENANT QUERY HELPERS
# ═══════════════════════════════════════════════════════════


class TestMultiTenantQuery:
    """Tests pour MultiTenantQuery helpers."""

    def setup_method(self):
        """Préparation avant chaque test."""
        UserContext.clear()

    @pytest.mark.unit
    def test_get_user_filter_with_user(self):
        """Test génération filtre utilisateur."""
        UserContext.set_user("user-123")
        
        # Mock modèle
        mock_model = Mock()
        mock_model.user_id = Mock()
        
        result = MultiTenantQuery.get_user_filter(mock_model)
        
        # Devrait retourner une condition filtre
        assert result is not None

    @pytest.mark.unit
    def test_get_user_filter_bypass(self):
        """Test filtre avec bypass activation."""
        UserContext.set_user("user-123")
        UserContext.set_bypass(True)
        
        mock_model = Mock()
        
        result = MultiTenantQuery.get_user_filter(mock_model)
        
        # Avec bypass, retourne True (pas de filtre)
        assert result is True

    @pytest.mark.unit
    def test_get_user_filter_no_user_id_attr(self):
        """Test filtre sur modèle sans user_id."""
        UserContext.set_user("user-123")
        
        mock_model = Mock(spec=[])  # Pas d'attribut user_id
        
        result = MultiTenantQuery.get_user_filter(mock_model)
        
        # Devrait retourner True (pas de filtre applicable)
        assert result is True

    @pytest.mark.unit
    def test_filter_by_user(self):
        """Test filtre_by_user helper."""
        UserContext.set_user("user-123")
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        
        mock_model = Mock()
        mock_model.user_id = Mock()
        
        result = MultiTenantQuery.filter_by_user(mock_query, mock_model)
        
        # Devrait appeler filter
        mock_query.filter.assert_called()

    @pytest.mark.unit
    def test_filter_by_user_bypass(self):
        """Test filter_by_user avec bypass."""
        UserContext.set_user("user-123")
        UserContext.set_bypass(True)
        
        mock_query = Mock()
        mock_model = Mock()
        
        result = MultiTenantQuery.filter_by_user(mock_query, mock_model)
        
        # Avec bypass, retourne query non filtrée
        assert result is mock_query
        mock_query.filter.assert_not_called()


# ═══════════════════════════════════════════════════════════
# SECTION 5: CAS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestMultiTenantIntegration:
    """Tests d'intégration multi-tenant."""

    def setup_method(self):
        """Préparation avant chaque test."""
        UserContext.clear()

    @pytest.mark.integration
    def test_complete_multitenant_workflow(self):
        """Test workflow complet multi-tenant."""
        
        # Utilisateur 1
        with user_context("user-1"):
            assert UserContext.get_user() == "user-1"
            
            @with_user_isolation()
            def get_data_for_user(user_id: str = None):
                return user_id
            
            result1 = get_data_for_user()
            assert result1 == "user-1"
        
        # Utilisateur 2
        with user_context("user-2"):
            result2 = get_data_for_user()
            assert result2 == "user-2"

    @pytest.mark.integration
    def test_admin_override_workflow(self):
        """Test workflow override admin."""
        UserContext.set_user("regular-user")
        
        # Mode utilisateur normal
        assert UserContext.is_bypassed() is False
        
        # Mode admin
        with admin_context():
            assert UserContext.is_bypassed() is True
            assert UserContext.get_user() == "regular-user"  # User ID persiste
        
        # Retour mode normal
        assert UserContext.is_bypassed() is False

    @pytest.mark.integration
    def test_permission_workflow(self):
        """Test workflow permissions."""
        
        @require_user()
        def protected_operation():
            return "success"
        
        # Sans utilisateur -> erreur
        UserContext.clear()
        with pytest.raises(PermissionError):
            protected_operation()
        
        # Avec utilisateur -> ok
        with user_context("user-123"):
            result = protected_operation()
            assert result == "success"

    @pytest.mark.integration
    def test_context_isolation_workflow(self):
        """Test isolation contexte entre utilisateurs."""
        results = []
        
        with user_context("user-1"):
            results.append(UserContext.get_user())
        
        results.append(UserContext.get_user())
        
        with user_context("user-2"):
            results.append(UserContext.get_user())
        
        results.append(UserContext.get_user())
        
        assert results == ["user-1", None, "user-2", None]


class TestMultiTenantEdgeCases:
    """Tests des cas limites."""

    def setup_method(self):
        """Préparation avant chaque test."""
        UserContext.clear()

    @pytest.mark.unit
    def test_empty_user_id(self):
        """Test avec ID utilisateur vide."""
        UserContext.set_user("")
        
        # String vide est accepté
        assert UserContext.get_user() == ""

    @pytest.mark.unit
    def test_special_characters_user_id(self):
        """Test avec caractères spéciaux."""
        special_id = "user-@#$%&123"
        UserContext.set_user(special_id)
        
        assert UserContext.get_user() == special_id

    @pytest.mark.unit
    def test_very_long_user_id(self):
        """Test avec très long ID utilisateur."""
        long_id = "x" * 10000
        UserContext.set_user(long_id)
        
        assert UserContext.get_user() == long_id

    @pytest.mark.unit
    def test_context_manager_none_user(self):
        """Test context manager avec None."""
        UserContext.set_user("initial")
        
        with user_context(None):
            assert UserContext.get_user() is None
        
        assert UserContext.get_user() == "initial"

    @pytest.mark.unit
    def test_bypass_toggle_rapid(self):
        """Test toggles rapides du bypass."""
        for _ in range(100):
            UserContext.set_bypass(True)
            assert UserContext.is_bypassed() is True
            UserContext.set_bypass(False)
            assert UserContext.is_bypassed() is False

    @pytest.mark.unit
    def test_decorator_return_types(self):
        """Test décorateurs avec différents types retournés."""
        UserContext.set_user("user-123")
        
        @with_user_isolation()
        def return_dict(user_id=None):
            return {"user": user_id}
        
        @with_user_isolation()
        def return_list(user_id=None):
            return [user_id]
        
        @with_user_isolation()
        def return_int(user_id=None):
            return 42
        
        assert return_dict() == {"user": "user-123"}
        assert return_list() == ["user-123"]
        assert return_int() == 42
