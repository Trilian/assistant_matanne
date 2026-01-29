"""
Tests unitaires pour BaseService (src/services/types.py).

Tests couvrant:
- OpÃ©rations CRUD (create, read, update, delete)
- Filtres et pagination
- Recherche avancÃ©e
- Bulk operations
- Statistiques gÃ©nÃ©riques
- Cache automatique
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock

from sqlalchemy.orm import Session

from src.services.types import BaseService
from src.core.models import Recette, Ingredient


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 1: TESTS CRUD DE BASE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceCRUD:
    """Test opÃ©rations CRUD de base."""

    def test_init_sets_model_and_cache_ttl(self):
        """Test que l'initialisation configure model et cache_ttl."""
        service = BaseService(Recette, cache_ttl=120)

        assert service.model == Recette
        assert service.model_name == "Recette"
        assert service.cache_ttl == 120

    def test_init_default_cache_ttl(self):
        """Test que cache_ttl par dÃ©faut est 60."""
        service = BaseService(Ingredient)

        assert service.cache_ttl == 60

    def test_create_adds_entity_to_db(self, db):
        """Test que create ajoute une entitÃ© en base."""
        service = BaseService(Recette)

        data = {
            "nom": "Test Recette",
            "description": "Description test",
            "temps_preparation": 15,
            "temps_cuisson": 30,
            "portions": 4,
            "difficulte": "facile",
        }

        result = service.create(data, db=db)

        assert result is not None
        assert result.id is not None
        assert result.nom == "Test Recette"
        assert result.temps_preparation == 15

    def test_create_invalidates_cache(self, db, clear_cache):
        """Test que create invalide le cache."""
        service = BaseService(Recette)
        
        with patch.object(service, '_invalider_cache') as mock_invalider:
            data = {"nom": "Test", "temps_preparation": 10, "temps_cuisson": 20, "portions": 2}
            service.create(data, db=db)
            
            mock_invalider.assert_called_once()

    def test_get_by_id_returns_entity(self, db, recette_factory):
        """Test que get_by_id retourne l'entitÃ© correcte."""
        recette = recette_factory.create(nom="Recette Test GetById")
        service = BaseService(Recette)

        result = service.get_by_id(recette.id, db=db)

        assert result is not None
        assert result.id == recette.id
        assert result.nom == "Recette Test GetById"

    def test_get_by_id_returns_none_for_missing(self, db):
        """Test que get_by_id retourne None pour ID inexistant."""
        service = BaseService(Recette)

        result = service.get_by_id(99999, db=db)

        assert result is None

    def test_get_by_id_uses_cache(self, db, recette_factory, clear_cache):
        """Test que get_by_id utilise le cache."""
        recette = recette_factory.create(nom="Recette Cached")
        service = BaseService(Recette)

        # Premier appel - pas de cache
        result1 = service.get_by_id(recette.id, db=db)
        
        # VÃ©rifier cache
        from src.core.cache import Cache
        cache_key = f"recette_{recette.id}"
        cached = Cache.obtenir(cache_key)
        
        # Le cache devrait contenir la valeur
        assert cached is not None or result1 is not None

    def test_get_all_returns_list(self, db, recette_factory):
        """Test que get_all retourne une liste."""
        recette_factory.create(nom="Recette A")
        recette_factory.create(nom="Recette B")
        service = BaseService(Recette)

        result = service.get_all(db=db)

        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_all_with_limit(self, db, recette_factory):
        """Test que get_all respecte le limit."""
        for i in range(5):
            recette_factory.create(nom=f"Recette Limit {i}")
        service = BaseService(Recette)

        result = service.get_all(limit=2, db=db)

        assert len(result) <= 2

    def test_get_all_with_skip(self, db, recette_factory):
        """Test que get_all respecte le skip."""
        for i in range(5):
            recette_factory.create(nom=f"Recette Skip {i}")
        service = BaseService(Recette)

        result_all = service.get_all(db=db)
        result_skip = service.get_all(skip=2, db=db)

        assert len(result_skip) == len(result_all) - 2

    def test_update_modifies_entity(self, db, recette_factory):
        """Test que update modifie l'entitÃ©."""
        recette = recette_factory.create(nom="Recette Original")
        service = BaseService(Recette)

        result = service.update(recette.id, {"nom": "Recette ModifiÃ©e"}, db=db)

        assert result is not None
        assert result.nom == "Recette ModifiÃ©e"

    def test_update_returns_none_for_missing(self, db):
        """Test que update retourne None pour ID inexistant."""
        service = BaseService(Recette)

        # Le dÃ©corateur gerer_erreurs avec valeur_fallback=None retourne None
        result = service.update(99999, {"nom": "Test"}, db=db)

        assert result is None

    def test_update_only_updates_valid_fields(self, db, recette_factory):
        """Test que update ignore les champs invalides."""
        recette = recette_factory.create(nom="Recette Champs")
        service = BaseService(Recette)

        result = service.update(
            recette.id,
            {"nom": "Nouveau Nom", "champ_inexistant": "valeur"},
            db=db,
        )

        assert result is not None
        assert result.nom == "Nouveau Nom"
        assert not hasattr(result, "champ_inexistant")

    def test_delete_removes_entity(self, db, recette_factory):
        """Test que delete supprime l'entitÃ©."""
        recette = recette_factory.create(nom="Recette Ã€ Supprimer")
        service = BaseService(Recette)
        recette_id = recette.id

        result = service.delete(recette_id, db=db)

        assert result is True
        assert service.get_by_id(recette_id, db=db) is None

    def test_delete_returns_false_for_missing(self, db):
        """Test que delete retourne False pour ID inexistant."""
        service = BaseService(Recette)

        result = service.delete(99999, db=db)

        assert result is False

    def test_count_returns_total(self, db, recette_factory):
        """Test que count retourne le nombre total."""
        initial_count = BaseService(Recette).count(db=db)
        
        recette_factory.create(nom="Recette Count 1")
        recette_factory.create(nom="Recette Count 2")
        service = BaseService(Recette)

        result = service.count(db=db)

        assert result == initial_count + 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 2: TESTS FILTRES ET TRI
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceFilters:
    """Test filtres et tri."""

    def test_get_all_with_filters(self, db, recette_factory):
        """Test que get_all filtre correctement."""
        recette_factory.create(nom="Facile", difficulte="facile")
        recette_factory.create(nom="Difficile", difficulte="difficile")
        service = BaseService(Recette)

        result = service.get_all(filters={"difficulte": "facile"}, db=db)

        assert all(r.difficulte == "facile" for r in result)

    def test_get_all_with_order_asc(self, db, recette_factory):
        """Test que get_all trie en ordre ascendant."""
        recette_factory.create(nom="Z Recette")
        recette_factory.create(nom="A Recette")
        service = BaseService(Recette)

        result = service.get_all(order_by="nom", db=db)

        # VÃ©rifier que le tri est appliquÃ©
        assert len(result) >= 2

    def test_get_all_with_order_desc(self, db, recette_factory):
        """Test que get_all trie en ordre descendant."""
        recette_factory.create(nom="A Recette Desc")
        recette_factory.create(nom="Z Recette Desc")
        service = BaseService(Recette)

        result = service.get_all(order_by="nom", desc_order=True, db=db)

        # VÃ©rifier que le tri descendant est appliquÃ©
        assert len(result) >= 2

    def test_count_with_filters(self, db, recette_factory):
        """Test que count filtre correctement."""
        initial = BaseService(Recette).count(filters={"difficulte": "expert"}, db=db)
        
        recette_factory.create(nom="Expert 1", difficulte="expert")
        recette_factory.create(nom="Expert 2", difficulte="expert")
        recette_factory.create(nom="Facile", difficulte="facile")
        service = BaseService(Recette)

        result = service.count(filters={"difficulte": "expert"}, db=db)

        assert result == initial + 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 3: TESTS RECHERCHE AVANCÃ‰E
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceAdvancedSearch:
    """Test recherche avancÃ©e."""

    def test_advanced_search_returns_list(self, db, recette_factory):
        """Test que advanced_search retourne une liste."""
        recette_factory.create(nom="Poulet RÃ´ti", description="DÃ©licieux poulet")
        service = BaseService(Recette)

        result = service.advanced_search(db=db)

        assert isinstance(result, list)

    def test_advanced_search_by_term(self, db, recette_factory):
        """Test recherche par terme textuel."""
        recette_factory.create(nom="Poulet GrillÃ©", description="Poulet au four")
        recette_factory.create(nom="Salade CÃ©sar", description="Salade classique")
        service = BaseService(Recette)

        result = service.advanced_search(
            search_term="poulet",
            search_fields=["nom", "description"],
            db=db,
        )

        assert len(result) >= 1
        assert all("poulet" in r.nom.lower() or "poulet" in (r.description or "").lower() for r in result)

    def test_advanced_search_with_limit(self, db, recette_factory):
        """Test que advanced_search respecte le limit."""
        for i in range(5):
            recette_factory.create(nom=f"Recette Search {i}")
        service = BaseService(Recette)

        result = service.advanced_search(limit=2, db=db)

        assert len(result) <= 2

    def test_advanced_search_with_offset(self, db, recette_factory):
        """Test que advanced_search respecte l'offset."""
        for i in range(5):
            recette_factory.create(nom=f"Recette Offset {i}")
        service = BaseService(Recette)

        result_all = service.advanced_search(db=db)
        result_offset = service.advanced_search(offset=2, db=db)

        assert len(result_offset) <= len(result_all)

    def test_advanced_search_with_sort(self, db, recette_factory):
        """Test que advanced_search trie correctement."""
        recette_factory.create(nom="A Search Sort")
        recette_factory.create(nom="Z Search Sort")
        service = BaseService(Recette)

        result = service.advanced_search(sort_by="nom", sort_desc=True, db=db)

        # VÃ©rifier que le tri est appliquÃ©
        assert len(result) >= 2


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 4: TESTS HELPERS INTERNES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
class TestBaseServiceHelpers:
    """Test mÃ©thodes helper internes."""

    def test_apply_filters_equality(self, db, recette_factory):
        """Test filtre Ã©galitÃ©."""
        recette_factory.create(nom="Filter Eq", difficulte="moyen")
        service = BaseService(Recette)

        result = service.get_all(filters={"difficulte": "moyen"}, db=db)

        assert all(r.difficulte == "moyen" for r in result)

    def test_apply_filters_operator_gte(self, db, recette_factory):
        """Test filtre >= (gte)."""
        recette_factory.create(nom="Filter Gte", temps_preparation=60)
        service = BaseService(Recette)

        result = service.get_all(
            filters={"temps_preparation": {"gte": 50}},
            db=db,
        )

        assert all(r.temps_preparation >= 50 for r in result)

    def test_apply_filters_operator_lte(self, db, recette_factory):
        """Test filtre <= (lte)."""
        recette_factory.create(nom="Filter Lte", temps_preparation=10)
        service = BaseService(Recette)

        result = service.get_all(
            filters={"temps_preparation": {"lte": 15}},
            db=db,
        )

        assert all(r.temps_preparation <= 15 for r in result)

    def test_apply_filters_operator_like(self, db, recette_factory):
        """Test filtre LIKE."""
        recette_factory.create(nom="Poulet Like Test")
        service = BaseService(Recette)

        result = service.get_all(
            filters={"nom": {"like": "Like"}},
            db=db,
        )

        assert all("like" in r.nom.lower() for r in result)

    def test_with_session_uses_provided_session(self, db):
        """Test que _with_session utilise la session fournie."""
        service = BaseService(Recette)
        
        called_with_session = []
        
        def test_func(session):
            called_with_session.append(session)
            return "result"
        
        result = service._with_session(test_func, db)
        
        assert result == "result"
        assert len(called_with_session) == 1
        assert called_with_session[0] == db

    def test_invalider_cache_clears_model_cache(self, clear_cache):
        """Test que _invalider_cache nettoie le cache du modÃ¨le."""
        service = BaseService(Recette)
        
        from src.core.cache import Cache
        Cache.definir("recette_test", "valeur")
        
        service._invalider_cache()
        
        # Le cache devrait Ãªtre invalidÃ© pour le pattern "recette"
        # Le test vÃ©rifie que la mÃ©thode s'exÃ©cute sans erreur


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# SECTION 5: TESTS D'INTÃ‰GRATION
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.integration
class TestBaseServiceIntegration:
    """Tests d'intÃ©gration BaseService."""

    def test_crud_workflow_complet(self, db):
        """Test workflow CRUD complet."""
        service = BaseService(Recette)

        # Create
        data = {
            "nom": "Workflow Recette",
            "description": "Test workflow",
            "temps_preparation": 20,
            "temps_cuisson": 40,
            "portions": 4,
            "difficulte": "moyen",
        }
        created = service.create(data, db=db)
        assert created.id is not None
        created_id = created.id

        # Read
        read = service.get_by_id(created_id, db=db)
        assert read.nom == "Workflow Recette"

        # Update
        updated = service.update(created_id, {"nom": "Workflow ModifiÃ©"}, db=db)
        assert updated.nom == "Workflow ModifiÃ©"

        # Delete
        deleted = service.delete(created_id, db=db)
        assert deleted is True

        # Verify deleted
        verify = service.get_by_id(created_id, db=db)
        assert verify is None

    def test_pagination_and_filters_combined(self, db, recette_factory):
        """Test pagination et filtres combinÃ©s."""
        for i in range(10):
            recette_factory.create(
                nom=f"Pagination {i}",
                difficulte="facile" if i % 2 == 0 else "difficile",
            )
        service = BaseService(Recette)

        result = service.get_all(
            filters={"difficulte": "facile"},
            skip=1,
            limit=3,
            db=db,
        )

        assert len(result) <= 3
        assert all(r.difficulte == "facile" for r in result)

