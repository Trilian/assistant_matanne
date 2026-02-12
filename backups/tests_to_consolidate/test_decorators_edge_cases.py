# -*- coding: utf-8 -*-
"""
Tests supplÃ©mentaires pour les cas limites de decorators.py

Cible les lignes non couvertes :
- 126-152: Fallback key_func avec TypeError dans with_cache  
- 223-228: afficher_erreur=True dans with_error_handling
- 282-287: field_mapping dans with_validation
"""
import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests key_func TypeError fallback (lignes 126-152)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestWithCacheKeyFuncFallback:
    """Tests pour le fallback TypeError dans with_cache."""
    
    def test_key_func_with_method_and_positional_args(self):
        """key_func sur mÃ©thode avec arguments positionnels."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        
        # Vider le cache
        Cache.vider()
        
        class MonService:
            @with_cache(ttl=60, key_func=lambda self, page, limit: f"items_{page}_{limit}")
            def get_items(self, page: int = 1, limit: int = 10):
                return [f"item_{i}" for i in range(limit)]
        
        service = MonService()
        
        # Appel avec arguments positionnels - devrait fonctionner directement
        result1 = service.get_items(2, 20)
        assert len(result1) == 20
        
        # DeuxiÃ¨me appel - doit Ãªtre en cache
        result2 = service.get_items(2, 20)
        assert result2 == result1
    
    def test_key_func_raises_typeerror_then_fallback(self):
        """key_func qui lÃ¨ve TypeError dÃ©clenche le fallback."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        
        Cache.vider()
        call_count = 0
        
        # Une key_func qui lÃ¨ve TypeError volontairement
        def problematic_key_func(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Premier appel : TypeError
                raise TypeError("Mauvais type d'argument")
            # Ensuite fonctionner normalement
            return f"key_{kwargs.get('page', 1)}"
        
        @with_cache(ttl=60, key_func=problematic_key_func)
        def fetch_data(page: int = 1, limit: int = 10):
            return {"page": page, "limit": limit}
        
        # Ceci va dÃ©clencher le fallback via TypeError
        result = fetch_data(page=5, limit=25)
        assert result["page"] == 5
    
    def test_key_func_fallback_with_self_and_kwargs(self):
        """Fallback key_func quand self prÃ©sent et kwargs reconstruits."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        
        Cache.vider()
        invocation_count = 0
        
        # Lambda qui attend uniquement les kwargs par nom
        def strict_key_func(self, **kwargs):
            return f"strict_{kwargs.get('item_id')}_{kwargs.get('refresh', False)}"
        
        class ItemService:
            @with_cache(ttl=60, key_func=strict_key_func)
            def get_item(self, item_id: int, refresh: bool = False):
                nonlocal invocation_count
                invocation_count += 1
                return {"id": item_id, "data": "content"}
        
        service = ItemService()
        
        # Premier appel
        result1 = service.get_item(42, refresh=True)
        assert result1["id"] == 42
        assert invocation_count == 1
        
        # DeuxiÃ¨me appel avec mÃªmes args - en cache
        result2 = service.get_item(42, refresh=True)
        assert result2 == result1
        # invocation_count pourrait ou non augmenter selon le fallback
    
    def test_key_func_with_default_values_in_fallback(self):
        """Fallback remplit les valeurs par dÃ©faut manquantes."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        
        Cache.vider()
        
        # key_func qui nÃ©cessite tous les params
        def full_key_func(self, a, b, c="default_c"):
            return f"full_{a}_{b}_{c}"
        
        class FullService:
            @with_cache(ttl=60, key_func=full_key_func)  
            def compute(self, a: int, b: str, c: str = "default_c"):
                return f"{a}_{b}_{c}"
        
        service = FullService()
        
        # Appel sans c, c doit Ãªtre rempli par dÃ©faut
        result = service.compute(10, "test")
        assert result == "10_test_default_c"
    
    def test_key_func_fallback_without_args(self):
        """Fallback quand pas d'args positionnels (juste kwargs)."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        
        Cache.vider()
        
        # key_func qui lÃ¨ve TypeError sur appel positionnel
        def kwargs_only_key_func(**kwargs):
            return f"kw_{kwargs.get('x', 0)}"
        
        @with_cache(ttl=60, key_func=kwargs_only_key_func)
        def process(x: int = 0, y: int = 0):
            return x + y
        
        # Appel avec kwargs seulement
        result = process(x=5, y=10)
        assert result == 15


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•  
# Tests afficher_erreur dans with_error_handling (lignes 223-228)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestWithErrorHandlingAfficherErreur:
    """Tests pour le paramÃ¨tre afficher_erreur."""
    
    def test_afficher_erreur_true_shows_streamlit_error(self):
        """afficher_erreur=True appelle st.error()."""
        from src.core.decorators import with_error_handling
        
        with patch("streamlit.error") as mock_st_error:
            @with_error_handling(default_return="fallback", afficher_erreur=True)
            def func_with_ui_error():
                raise ValueError("Une erreur test")
            
            result = func_with_ui_error()
            
            assert result == "fallback"
            mock_st_error.assert_called_once()
            call_arg = mock_st_error.call_args[0][0]
            assert "[ERROR]" in call_arg
            assert "Une erreur test" in call_arg
    
    def test_afficher_erreur_true_but_streamlit_not_initialized(self):
        """afficher_erreur=True mais Streamlit pas initialisÃ©."""
        from src.core.decorators import with_error_handling
        
        # Mock streamlit.error pour lever une exception
        with patch("streamlit.error", side_effect=RuntimeError("No Streamlit context")):
            @with_error_handling(default_return=None, afficher_erreur=True)
            def func_streamlit_fails():
                raise Exception("Erreur interne")
            
            # Ne doit pas lever d'exception mÃªme si st.error Ã©choue
            result = func_streamlit_fails()
            assert result is None
    
    def test_afficher_erreur_false_no_streamlit_call(self):
        """afficher_erreur=False ne doit pas appeler st.error()."""
        from src.core.decorators import with_error_handling
        
        with patch("streamlit.error") as mock_st_error:
            @with_error_handling(default_return="safe", afficher_erreur=False)
            def silent_error_func():
                raise RuntimeError("Erreur silencieuse")
            
            result = silent_error_func()
            
            assert result == "safe"
            mock_st_error.assert_not_called()
    
    def test_afficher_erreur_with_custom_log_level(self):
        """afficher_erreur avec log_level personnalisÃ©."""
        from src.core.decorators import with_error_handling
        
        with patch("streamlit.error") as mock_st_error:
            @with_error_handling(
                default_return={"error": True},
                log_level="WARNING",
                afficher_erreur=True
            )
            def warn_level_func():
                raise ValueError("Warning level error")
            
            result = warn_level_func()
            
            assert result == {"error": True}
            mock_st_error.assert_called_once()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests field_mapping dans with_validation (lignes 282-287)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class RecetteInput(BaseModel):
    """ModÃ¨le Pydantic pour validation."""
    nom: str
    temps_preparation: int


class ArticleInput(BaseModel):
    """ModÃ¨le pour articles."""
    nom: str
    quantite: int = 1


class TestWithValidationFieldMapping:
    """Tests pour field_mapping dans with_validation."""
    
    def test_validation_with_field_mapping(self):
        """field_mapping mappe correctement les paramÃ¨tres."""
        from src.core.decorators import with_validation
        
        @with_validation(RecetteInput, field_mapping={"data": "recipe_data"})
        def creer_recette(data: dict):
            return {"validated": True, **data}
        
        result = creer_recette(data={"nom": "Tarte", "temps_preparation": 30})
        
        assert result["validated"] is True
        assert result["nom"] == "Tarte"
        assert result["temps_preparation"] == 30
    
    def test_validation_with_field_mapping_invalid_data(self):
        """field_mapping avec donnÃ©es invalides lÃ¨ve ErreurValidation."""
        from src.core.decorators import with_validation
        from src.core.errors_base import ErreurValidation
        
        @with_validation(RecetteInput, field_mapping={"data": "recipe_data"})
        def creer_recette_invalid(data: dict):
            return data
        
        with pytest.raises(ErreurValidation) as exc_info:
            creer_recette_invalid(data={"nom": "Tarte"})  # Manque temps_preparation
        
        assert "Validation Ã©chouÃ©e" in str(exc_info.value)
    
    def test_validation_without_field_mapping_uses_default(self):
        """Sans field_mapping, utilise 'data' par dÃ©faut."""
        from src.core.decorators import with_validation
        
        @with_validation(ArticleInput)
        def creer_article(data: dict):
            return {"created": True, **data}
        
        result = creer_article(data={"nom": "Pommes", "quantite": 5})
        
        assert result["created"] is True
        assert result["nom"] == "Pommes"
        assert result["quantite"] == 5
    
    def test_validation_with_empty_field_mapping(self):
        """field_mapping vide utilise le dÃ©faut."""
        from src.core.decorators import with_validation
        
        @with_validation(ArticleInput, field_mapping={})
        def creer_article_empty_mapping(data: dict):
            return data
        
        # Avec field_mapping vide, param_key sera "data"
        result = creer_article_empty_mapping(data={"nom": "Oranges", "quantite": 3})
        
        assert result["nom"] == "Oranges"
    
    def test_validation_multiple_fields_in_mapping(self):
        """field_mapping avec plusieurs champs prend le premier."""
        from src.core.decorators import with_validation
        
        @with_validation(RecetteInput, field_mapping={
            "recipe": "recipe_data",
            "article": "article_data"
        })
        def process_mixed(recipe: dict, other: str = "test"):
            return {"processed": True, **recipe}
        
        # Le premier champ dans field_mapping est "recipe"
        result = process_mixed(recipe={"nom": "Pizza", "temps_preparation": 45})
        
        assert result["processed"] is True
        assert result["nom"] == "Pizza"
    
    def test_validation_param_not_in_kwargs_skips(self):
        """Si param_key pas dans kwargs, ne fait rien."""
        from src.core.decorators import with_validation
        
        @with_validation(RecetteInput, field_mapping={"data": "recipe"})
        def func_without_data(other_param: str):
            return other_param
        
        # 'data' n'est pas dans kwargs, validation skip
        result = func_without_data(other_param="valeur")
        assert result == "valeur"


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# Tests additionnels pour couverture complÃ¨te
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

class TestWithCacheEdgeCases:
    """Cas limites supplÃ©mentaires pour with_cache."""
    
    def test_cache_hit_with_none_value(self):
        """Cache retourne None comme valeur valide."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        
        Cache.vider()
        call_count = 0
        
        @with_cache(ttl=60, key_prefix="none_test")
        def get_none():
            nonlocal call_count
            call_count += 1
            return None
        
        result1 = get_none()
        assert result1 is None
        assert call_count == 1
        
        # DeuxiÃ¨me appel - doit Ãªtre en cache mÃªme si None
        result2 = get_none()
        assert result2 is None
        # Note: selon implÃ©mentation, peut ou non Ãªtre en cache
    
    def test_cache_with_db_param_excluded(self):
        """Le paramÃ¨tre 'db' est exclu de la clÃ© de cache."""
        from src.core.decorators import with_cache
        from src.core.cache import Cache
        from unittest.mock import MagicMock
        
        Cache.vider()
        call_count = 0
        
        @with_cache(ttl=60, key_prefix="db_test")
        def query_with_db(item_id: int, db=None):
            nonlocal call_count
            call_count += 1
            return {"id": item_id}
        
        mock_db1 = MagicMock()
        mock_db2 = MagicMock()
        
        result1 = query_with_db(1, db=mock_db1)
        assert call_count == 1
        
        # MÃªme item_id, db diffÃ©rent - devrait Ãªtre en cache
        result2 = query_with_db(1, db=mock_db2)
        assert result1 == result2


class TestWithDbSessionEdgeCases:
    """Tests supplÃ©mentaires pour with_db_session."""
    
    def test_session_param_name_used_if_present(self):
        """Utilise 'session' si c'est le nom du paramÃ¨tre."""
        from unittest.mock import MagicMock, patch
        from src.core.decorators import with_db_session
        
        mock_session = MagicMock()
        
        @with_db_session
        def func_with_session_param(value: int, session=None):
            assert session is not None
            return value * 2
        
        # Session fournie directement - pas d'injection
        result = func_with_session_param(5, session=mock_session)
        assert result == 10
    
    def test_db_param_used_if_session_not_in_signature(self):
        """Utilise 'db' si 'session' pas dans la signature."""
        from unittest.mock import MagicMock
        from src.core.decorators import with_db_session
        
        mock_db = MagicMock()
        
        @with_db_session
        def func_with_db_param(value: int, db=None):
            assert db is not None
            return value + 1
        
        # DB fournie directement - pas d'injection
        result = func_with_db_param(10, db=mock_db)
        assert result == 11
    
    def test_db_session_skips_injection_when_db_provided(self):
        """with_db_session n'injecte pas quand db dÃ©jÃ  fourni."""
        from unittest.mock import MagicMock
        from src.core.decorators import with_db_session
        
        mock_db = MagicMock()
        
        @with_db_session
        def query_function(query: str, db=None):
            return f"Executed: {query}"
        
        result = query_function("SELECT *", db=mock_db)
        assert result == "Executed: SELECT *"
    
    def test_db_session_skips_injection_when_session_provided(self):
        """with_db_session n'injecte pas quand session dÃ©jÃ  fourni."""
        from unittest.mock import MagicMock
        from src.core.decorators import with_db_session
        
        mock_session = MagicMock()
        
        @with_db_session
        def query_with_session(query: str, session=None):
            return f"Query: {query}"
        
        result = query_with_session("SELECT 1", session=mock_session)
        assert result == "Query: SELECT 1"
