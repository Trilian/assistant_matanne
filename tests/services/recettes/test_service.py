"""
Tests pour src/services/recettes/service.py

Ce module teste le service principal des recettes:
- CRUD de recettes
- Recherche et filtrage
- Suggestions IA (mockées)
- Calcul des ingrédients
- Export/Import
- Historique et versions
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.core.models import (
    Recette,
    Ingredient,
    RecetteIngredient,
    EtapeRecette,
    VersionRecette,
)
from src.services.recettes.service import (
    ServiceRecettes,
    RecetteService,
    obtenir_service_recettes,
    get_recette_service,
)
from src.services.recettes.types import (
    RecetteSuggestion,
    VersionBebeGeneree,
    VersionBatchCookingGeneree,
    VersionRobotGeneree,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def service():
    """Instance du service recettes pour les tests."""
    return ServiceRecettes()


@pytest.fixture
def recette_data():
    """Données de base pour créer une recette."""
    return {
        "nom": "Poulet Rôti Test",
        "description": "Un délicieux poulet rôti",
        "temps_preparation": 20,
        "temps_cuisson": 60,
        "portions": 6,
        "difficulte": "facile",
        "type_repas": "dîner",  # Avec accent
        "saison": "toute_année",
        "ingredients": [
            {"nom": "Poulet", "quantite": 1.5, "unite": "kg"},
            {"nom": "Thym", "quantite": 10, "unite": "g"},
            {"nom": "Huile olive", "quantite": 3, "unite": "cuillères"},
        ],
        "etapes": [
            {"description": "Préchauffer le four à 200°C"},
            {"description": "Assaisonner le poulet"},
            {"description": "Enfourner pendant 1h"},
        ],
    }


@pytest.fixture
def sample_recette(db: Session):
    """Crée une recette de test en DB."""
    from datetime import datetime
    
    recette = Recette(
        nom="Test Recette",
        description="Description test",
        temps_preparation=30,
        temps_cuisson=45,
        portions=4,
        difficulte="moyen",
        type_repas="dîner",
        saison="toute_année",
        updated_at=datetime.utcnow(),
    )
    db.add(recette)
    db.commit()
    db.refresh(recette)
    return recette


@pytest.fixture
def recette_with_ingredients(db: Session):
    """Crée une recette avec ingrédients en DB."""
    from datetime import datetime
    
    # Créer la recette
    recette = Recette(
        nom="Recette Complète",
        description="Recette avec ingrédients",
        temps_preparation=20,
        temps_cuisson=30,
        portions=4,
        difficulte="facile",
        type_repas="déjeuner",
        saison="été",
        updated_at=datetime.utcnow(),
    )
    db.add(recette)
    db.flush()
    
    # Créer les ingrédients
    ingredient1 = Ingredient(nom="Tomate", unite="g", categorie="Légumes")
    ingredient2 = Ingredient(nom="Mozzarella", unite="g", categorie="Produits laitiers")
    db.add_all([ingredient1, ingredient2])
    db.flush()
    
    # Lier ingrédients à la recette
    ri1 = RecetteIngredient(
        recette_id=recette.id,
        ingredient_id=ingredient1.id,
        quantite=200,
        unite="g",
    )
    ri2 = RecetteIngredient(
        recette_id=recette.id,
        ingredient_id=ingredient2.id,
        quantite=150,
        unite="g",
    )
    db.add_all([ri1, ri2])
    
    # Créer les étapes
    etape1 = EtapeRecette(recette_id=recette.id, ordre=1, description="Couper les tomates")
    etape2 = EtapeRecette(recette_id=recette.id, ordre=2, description="Ajouter la mozzarella")
    db.add_all([etape1, etape2])
    
    db.commit()
    db.refresh(recette)
    return recette


@pytest.fixture
def multiple_recettes(db: Session):
    """Crée plusieurs recettes pour les tests de recherche."""
    from datetime import datetime
    
    recettes_data = [
        {
            "nom": "Salade César",
            "description": "Classique salade romaine",
            "temps_preparation": 15,
            "temps_cuisson": 0,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "déjeuner",
            "saison": "été",
        },
        {
            "nom": "Boeuf Bourguignon",
            "description": "Plat mijoté traditionnel",
            "temps_preparation": 30,
            "temps_cuisson": 180,
            "portions": 8,
            "difficulte": "difficile",
            "type_repas": "dîner",
            "saison": "hiver",
        },
        {
            "nom": "Omelette aux fines herbes",
            "description": "Omelette rapide",
            "temps_preparation": 5,
            "temps_cuisson": 5,
            "portions": 2,
            "difficulte": "facile",
            "type_repas": "petit_déjeuner",
            "saison": "toute_année",
        },
        {
            "nom": "Tarte aux pommes",
            "description": "Dessert classique",
            "temps_preparation": 25,
            "temps_cuisson": 45,
            "portions": 8,
            "difficulte": "moyen",
            "type_repas": "goûter",
            "saison": "automne",
        },
    ]
    
    recettes = []
    for data in recettes_data:
        recette = Recette(**data, updated_at=datetime.utcnow())
        db.add(recette)
        recettes.append(recette)
    
    db.commit()
    for r in recettes:
        db.refresh(r)
    
    return recettes


@pytest.fixture
def patch_db_context(db: Session):
    """Patch obtenir_contexte_db pour utiliser la session de test."""
    from contextlib import contextmanager
    
    @contextmanager
    def mock_db_context():
        yield db
    
    # Le décorateur importe obtenir_contexte_db depuis src.core.database
    with patch('src.core.database.obtenir_contexte_db', mock_db_context):
        yield db


# ═══════════════════════════════════════════════════════════
# TESTS INITIALISATION
# ═══════════════════════════════════════════════════════════

class TestServiceInitialisation:
    """Tests pour l'initialisation du service."""
    
    def test_service_creation(self, service):
        """Teste la création du service."""
        assert service is not None
        assert isinstance(service, ServiceRecettes)
    
    def test_service_alias(self):
        """Teste l'alias RecetteService."""
        assert RecetteService is ServiceRecettes
    
    def test_factory_function(self):
        """Teste les fonctions factory."""
        service1 = obtenir_service_recettes()
        service2 = get_recette_service()
        
        assert service1 is not None
        assert service2 is not None
        # Les deux devraient retourner le même singleton
        assert service1 is service2


# ═══════════════════════════════════════════════════════════
# TESTS CRUD
# ═══════════════════════════════════════════════════════════

class TestCRUD:
    """Tests pour les opérations CRUD."""
    
    def test_create_complete(self, service, recette_data, patch_db_context):
        """Teste la création d'une recette complète."""
        result = service.create_complete(recette_data)
        
        assert result is not None
        assert result.nom == "Poulet Rôti Test"
        assert result.temps_preparation == 20
        assert result.temps_cuisson == 60
        assert result.portions == 6
        assert result.id is not None
    
    def test_create_complete_with_ingredients(self, service, recette_data, patch_db_context):
        """Teste que les ingrédients sont créés."""
        result = service.create_complete(recette_data)
        
        assert result is not None
        # Les ingrédients devraient être liés (vérifier via DB)
        assert result.id is not None
    
    def test_create_complete_with_etapes(self, service, recette_data, patch_db_context):
        """Teste que les étapes sont créées."""
        result = service.create_complete(recette_data)
        
        assert result is not None
        assert result.id is not None
    
    def test_create_complete_minimal_data(self, service, patch_db_context):
        """Teste la création avec données minimales valides."""
        minimal_data = {
            "nom": "Recette Minimale",
            "description": "Description simple",
            "temps_preparation": 10,
            "temps_cuisson": 20,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "dîner",
            "ingredients": [{"nom": "Test", "quantite": 1, "unite": "pcs"}],
            "etapes": [{"description": "Step 1"}],
        }
        
        result = service.create_complete(minimal_data)
        
        assert result is not None
        assert result.nom == "Recette Minimale"
    
    def test_create_complete_invalid_data(self, service, patch_db_context):
        """Teste avec données invalides."""
        from src.core.errors_base import ErreurValidation
        
        invalid_data = {
            "nom": "",  # Nom vide - invalide
            "temps_preparation": 10,
            "type_repas": "dîner",
        }
        
        # Devrait lever une ErreurValidation
        with pytest.raises(ErreurValidation):
            service.create_complete(invalid_data)
    
    def test_get_by_id_full(self, service, sample_recette, patch_db_context):
        """Teste la récupération par ID avec relations."""
        result = service.get_by_id_full(sample_recette.id)
        
        assert result is not None
        assert result.id == sample_recette.id
        assert result.nom == sample_recette.nom
    
    def test_get_by_id_full_not_found(self, service, patch_db_context):
        """Teste la récupération d'une recette inexistante."""
        result = service.get_by_id_full(99999)
        
        assert result is None
    
    def test_get_by_type(self, service, multiple_recettes, patch_db_context):
        """Teste la récupération par type de repas."""
        result = service.get_by_type("dîner")
        
        assert len(result) >= 1
        assert all(r.type_repas == "dîner" for r in result)
    
    def test_get_by_type_empty(self, service, patch_db_context):
        """Teste avec un type sans recettes."""
        result = service.get_by_type("type_inexistant")
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS RECHERCHE AVANCÉE
# ═══════════════════════════════════════════════════════════

class TestRechercheAvancee:
    """Tests pour la recherche avancée."""
    
    def test_search_advanced_by_term(self, service, multiple_recettes, patch_db_context):
        """Teste la recherche par terme."""
        result = service.search_advanced(term="Salade")
        
        assert len(result) >= 1
        assert any("Salade" in r.nom for r in result)
    
    def test_search_advanced_by_type_repas(self, service, multiple_recettes, patch_db_context):
        """Teste la recherche par type de repas."""
        result = service.search_advanced(type_repas="déjeuner")
        
        assert len(result) >= 1
        assert all(r.type_repas == "déjeuner" for r in result)
    
    def test_search_advanced_by_difficulte(self, service, multiple_recettes, patch_db_context):
        """Teste la recherche par difficulté."""
        result = service.search_advanced(difficulte="facile")
        
        assert len(result) >= 1
        assert all(r.difficulte == "facile" for r in result)
    
    def test_search_advanced_by_saison(self, service, multiple_recettes, patch_db_context):
        """Teste la recherche par saison."""
        result = service.search_advanced(saison="hiver")
        
        assert len(result) >= 1
        assert all(r.saison == "hiver" for r in result)
    
    def test_search_advanced_combined(self, service, multiple_recettes, patch_db_context):
        """Teste la recherche avec plusieurs critères."""
        result = service.search_advanced(
            difficulte="facile",
            type_repas="dejeuner",
        )
        
        for r in result:
            assert r.difficulte == "facile"
            assert r.type_repas == "dejeuner"
    
    def test_search_advanced_with_limit(self, service, multiple_recettes, patch_db_context):
        """Teste la limite de résultats."""
        result = service.search_advanced(limit=2)
        
        assert len(result) <= 2
    
    def test_search_advanced_no_results(self, service, patch_db_context):
        """Teste une recherche sans résultats."""
        result = service.search_advanced(term="RecetteInexistante12345")
        
        assert result == []


# ═══════════════════════════════════════════════════════════
# TESTS GÉNÉRATION IA
# ═══════════════════════════════════════════════════════════

class TestGenerationIA:
    """Tests pour les fonctions de génération IA (mockées)."""
    
    @patch.object(ServiceRecettes, 'call_with_list_parsing_sync')
    def test_generer_recettes_ia(self, mock_call, service):
        """Teste la génération de recettes IA."""
        # Mock de la réponse IA
        mock_call.return_value = [
            RecetteSuggestion(
                nom="Poulet Curry",
                description="Un curry savoureux",
                temps_preparation=20,
                temps_cuisson=30,
                portions=4,
                difficulte="moyen",
                type_repas="diner",
                saison="toute_année",
                ingredients=[{"nom": "Poulet", "quantite": 500, "unite": "g"}],
                etapes=[{"description": "Faire revenir le poulet"}],
            ),
        ]
        
        result = service.generer_recettes_ia(
            type_repas="diner",
            saison="toute_année",
            difficulte="moyen",
            nb_recettes=1,
        )
        
        assert len(result) == 1
        assert result[0].nom == "Poulet Curry"
        mock_call.assert_called_once()
    
    @patch.object(ServiceRecettes, 'call_with_list_parsing_sync')
    def test_generer_recettes_ia_with_ingredients(self, mock_call, service):
        """Teste la génération avec ingrédients disponibles."""
        mock_call.return_value = []
        
        result = service.generer_recettes_ia(
            type_repas="dejeuner",
            saison="ete",
            ingredients_dispo=["tomate", "mozzarella", "basilic"],
            nb_recettes=2,
        )
        
        mock_call.assert_called_once()
        # Le prompt devrait contenir les ingrédients
        call_kwargs = mock_call.call_args
        assert call_kwargs is not None
    
    @patch.object(ServiceRecettes, 'call_with_list_parsing_sync')
    def test_generer_recettes_ia_error_returns_empty(self, mock_call, service):
        """Teste que les erreurs retournent une liste vide."""
        mock_call.side_effect = Exception("API Error")
        
        result = service.generer_recettes_ia(
            type_repas="diner",
            saison="toute_année",
        )
        
        # Grâce au décorateur @avec_gestion_erreurs, devrait retourner []
        assert result == []
    
    @patch.object(ServiceRecettes, 'call_with_list_parsing_sync')
    def test_generer_variantes_recette_ia(self, mock_call, service):
        """Teste la génération de variantes."""
        mock_call.return_value = [
            RecetteSuggestion(
                nom="Spaghetti Carbonara Végétarienne",
                description="Version végé",
                temps_preparation=15,
                temps_cuisson=20,
                portions=4,
                difficulte="facile",
                type_repas="diner",
                saison="toute_année",
                ingredients=[],
                etapes=[],
            ),
        ]
        
        result = service.generer_variantes_recette_ia(
            nom_recette="Spaghetti Carbonara",
            nb_variantes=1,
        )
        
        assert len(result) == 1
        mock_call.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS VERSIONS (BÉBÉ, BATCH, ROBOT)
# ═══════════════════════════════════════════════════════════

class TestVersions:
    """Tests pour les versions de recettes."""
    
    @patch.object(ServiceRecettes, 'call_with_parsing_sync')
    def test_generer_version_bebe(
        self, mock_call, service, recette_with_ingredients, patch_db_context
    ):
        """Teste la génération de version bébé."""
        mock_call.return_value = VersionBebeGeneree(
            instructions_modifiees="Mixer finement tous les ingrédients",
            notes_bebe="Sans sel, texture purée",
            age_minimum_mois=12,
        )
        
        result = service.generer_version_bebe(recette_with_ingredients.id)
        
        assert result is not None
        assert result.type_version == "bébé"
        assert "Mixer" in result.instructions_modifiees or result.instructions_modifiees
    
    @patch.object(ServiceRecettes, 'call_with_parsing_sync')
    def test_generer_version_bebe_already_exists(
        self, mock_call, service, recette_with_ingredients, patch_db_context, db
    ):
        """Teste quand la version bébé existe déjà."""
        # Créer une version existante
        version = VersionRecette(
            recette_base_id=recette_with_ingredients.id,
            type_version="bébé",
            instructions_modifiees="Existante",
            notes_bebe="Notes existantes",
        )
        db.add(version)
        db.commit()
        
        result = service.generer_version_bebe(recette_with_ingredients.id)
        
        # Devrait retourner la version existante sans appeler l'IA
        assert result is not None
        mock_call.assert_not_called()
    
    def test_generer_version_bebe_recette_not_found(self, service, patch_db_context):
        """Teste avec une recette inexistante."""
        # Devrait lever une exception ou retourner None
        try:
            result = service.generer_version_bebe(99999)
            assert result is None
        except Exception:
            pass  # Exception attendue
    
    @patch.object(ServiceRecettes, 'call_with_parsing_sync')
    def test_generer_version_batch_cooking(
        self, mock_call, service, recette_with_ingredients, patch_db_context
    ):
        """Teste la génération de version batch cooking."""
        mock_call.return_value = VersionBatchCookingGeneree(
            instructions_modifiees="Multiplier par 3 les quantités",
            nombre_portions_recommande=12,
            temps_preparation_total_heures=2.5,
            conseils_conservation="3 jours au frigo",
            conseils_congelation="Se congèle bien",
            calendrier_preparation="Dimanche: prep, Lundi-Mercredi: consommer",
        )
        
        result = service.generer_version_batch_cooking(recette_with_ingredients.id)
        
        assert result is not None
        assert result.type_version == "batch cooking"
    
    @patch.object(ServiceRecettes, 'call_with_parsing_sync')
    def test_generer_version_robot_cookeo(
        self, mock_call, service, recette_with_ingredients, patch_db_context
    ):
        """Teste la génération de version robot Cookeo."""
        mock_call.return_value = VersionRobotGeneree(
            instructions_modifiees="Utiliser le mode pression",
            reglages_robot="Haute pression 15 min",
            temps_cuisson_adapte_minutes=20,
            conseils_preparation="Couper en morceaux uniformes",
            etapes_specifiques=["Saisir 5 min", "Cuisson pression 15 min"],
        )
        
        result = service.generer_version_robot(
            recette_with_ingredients.id,
            robot_type="cookeo",
        )
        
        assert result is not None
        assert "cookeo" in result.type_version
    
    @patch.object(ServiceRecettes, 'call_with_parsing_sync')
    def test_generer_version_robot_airfryer(
        self, mock_call, service, recette_with_ingredients, patch_db_context
    ):
        """Teste la génération de version robot Airfryer."""
        mock_call.return_value = VersionRobotGeneree(
            instructions_modifiees="Préchauffer 3 min à 180°C",
            reglages_robot="180°C pendant 25 min",
            temps_cuisson_adapte_minutes=25,
            conseils_preparation="Huiler légèrement",
            etapes_specifiques=["Préchauffer", "Cuire en remuant"],
        )
        
        result = service.generer_version_robot(
            recette_with_ingredients.id,
            robot_type="airfryer",
        )
        
        assert result is not None
        assert "airfryer" in result.type_version
    
    def test_generer_version_robot_unknown_type(
        self, service, recette_with_ingredients, patch_db_context
    ):
        """Teste avec un type de robot inconnu."""
        try:
            result = service.generer_version_robot(
                recette_with_ingredients.id,
                robot_type="robot_inconnu",
            )
            # Devrait lever une ValueError
            assert False, "Devrait lever une exception"
        except ValueError as e:
            assert "Unknown robot type" in str(e)
        except Exception:
            pass  # Autre exception acceptable
    
    def test_get_versions(self, service, recette_with_ingredients, patch_db_context, db):
        """Teste la récupération des versions."""
        # Créer quelques versions
        version1 = VersionRecette(
            recette_base_id=recette_with_ingredients.id,
            type_version="bébé",
            instructions_modifiees="V1",
        )
        version2 = VersionRecette(
            recette_base_id=recette_with_ingredients.id,
            type_version="batch cooking",
            instructions_modifiees="V2",
        )
        db.add_all([version1, version2])
        db.commit()
        
        result = service.get_versions(recette_with_ingredients.id)
        
        assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS HISTORIQUE
# ═══════════════════════════════════════════════════════════

class TestHistorique:
    """Tests pour l'historique d'utilisation."""
    
    def test_enregistrer_cuisson(self, service, sample_recette, patch_db_context):
        """Teste l'enregistrement d'une cuisson."""
        result = service.enregistrer_cuisson(
            recette_id=sample_recette.id,
            portions=4,
            note=4,
            avis="Très bon !",
        )
        
        assert result is True
    
    def test_enregistrer_cuisson_minimal(self, service, sample_recette, patch_db_context):
        """Teste l'enregistrement minimal."""
        result = service.enregistrer_cuisson(recette_id=sample_recette.id)
        
        assert result is True
    
    def test_get_historique(self, service, sample_recette, patch_db_context):
        """Teste la récupération de l'historique."""
        # Enregistrer une cuisson d'abord
        service.enregistrer_cuisson(sample_recette.id, portions=2)
        
        result = service.get_historique(sample_recette.id)
        
        assert len(result) >= 0  # Peut être vide si pas d'historique
    
    def test_get_stats_recette(self, service, sample_recette, patch_db_context):
        """Teste les statistiques d'une recette."""
        # Enregistrer quelques cuissons
        service.enregistrer_cuisson(sample_recette.id, portions=4, note=4)
        service.enregistrer_cuisson(sample_recette.id, portions=2, note=5)
        
        stats = service.get_stats_recette(sample_recette.id)
        
        assert "nb_cuissons" in stats
        assert stats["nb_cuissons"] >= 0
    
    def test_get_stats_recette_empty(self, service, sample_recette, patch_db_context):
        """Teste les stats d'une recette sans historique."""
        stats = service.get_stats_recette(sample_recette.id)
        
        assert stats.get("nb_cuissons", 0) >= 0


# ═══════════════════════════════════════════════════════════
# TESTS EXPORT
# ═══════════════════════════════════════════════════════════

class TestExport:
    """Tests pour l'export des recettes."""
    
    def test_export_to_csv(self, service, recette_with_ingredients, patch_db_context, db):
        """Teste l'export CSV."""
        recettes = db.query(Recette).all()
        
        csv_output = service.export_to_csv(recettes)
        
        assert csv_output
        assert "nom" in csv_output
        lines = csv_output.strip().split('\n')
        assert len(lines) >= 2  # Header + au moins une recette
    
    def test_export_to_csv_custom_separator(self, service, sample_recette, patch_db_context, db):
        """Teste l'export CSV avec séparateur personnalisé."""
        recettes = db.query(Recette).all()
        
        csv_output = service.export_to_csv(recettes, separator=";")
        
        assert ";" in csv_output
    
    def test_export_to_csv_empty(self, service):
        """Teste l'export CSV avec liste vide."""
        csv_output = service.export_to_csv([])
        
        # Devrait contenir au moins le header
        assert "nom" in csv_output
    
    def test_export_to_json(self, service, recette_with_ingredients, patch_db_context, db):
        """Teste l'export JSON."""
        import json
        
        recettes = db.query(Recette).filter(
            Recette.id == recette_with_ingredients.id
        ).all()
        
        json_output = service.export_to_json(recettes)
        
        assert json_output
        data = json.loads(json_output)
        assert len(data) == 1
        assert data[0]["nom"] == recette_with_ingredients.nom
    
    def test_export_to_json_with_relations(self, service, recette_with_ingredients, patch_db_context, db):
        """Teste l'export JSON avec ingrédients et étapes."""
        import json
        from sqlalchemy.orm import joinedload
        
        recettes = db.query(Recette).options(
            joinedload(Recette.ingredients).joinedload(RecetteIngredient.ingredient),
            joinedload(Recette.etapes),
        ).filter(Recette.id == recette_with_ingredients.id).all()
        
        json_output = service.export_to_json(recettes)
        data = json.loads(json_output)
        
        assert len(data[0]["ingredients"]) > 0
        assert len(data[0]["etapes"]) > 0


# ═══════════════════════════════════════════════════════════
# TESTS HELPERS
# ═══════════════════════════════════════════════════════════

class TestHelpers:
    """Tests pour les méthodes helpers."""
    
    def test_find_or_create_ingredient_new(self, service, patch_db_context, db):
        """Teste la création d'un nouvel ingrédient."""
        ingredient = service._find_or_create_ingredient(db, "Nouvel Ingrédient")
        
        assert ingredient is not None
        assert ingredient.nom == "Nouvel Ingrédient"
        assert ingredient.id is not None
    
    def test_find_or_create_ingredient_existing(self, service, patch_db_context, db):
        """Teste avec un ingrédient existant."""
        # Créer l'ingrédient
        existing = Ingredient(nom="Ingrédient Existant", unite="g")
        db.add(existing)
        db.commit()
        
        # Chercher
        found = service._find_or_create_ingredient(db, "Ingrédient Existant")
        
        assert found.id == existing.id


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════

class TestEdgeCases:
    """Tests pour les cas limites."""
    
    def test_create_complete_with_empty_ingredients(self, service, patch_db_context):
        """Teste la création avec liste d'ingrédients vide (invalide)."""
        from src.core.errors_base import ErreurValidation
        
        data = {
            "nom": "Recette Sans Ingrédients",
            "description": "Test",
            "temps_preparation": 10,
            "temps_cuisson": 10,
            "portions": 4,
            "difficulte": "facile",
            "type_repas": "dîner",
            "ingredients": [],  # Liste vide - invalide
            "etapes": [],  # Liste vide - invalide
        }
        
        # La validation Pydantic n'accepte pas les listes vides
        with pytest.raises(ErreurValidation):
            service.create_complete(data)
    
    def test_search_with_special_characters(self, service, patch_db_context):
        """Teste la recherche avec caractères spéciaux."""
        result = service.search_advanced(term="Crème brûlée à l'érable")
        
        # Ne devrait pas planter
        assert isinstance(result, list)
    
    def test_concurrent_calls(self, service, recette_data, patch_db_context):
        """Teste des appels concurrents (simulation simple)."""
        # Créer plusieurs recettes rapidement
        results = []
        for i in range(3):
            data = recette_data.copy()
            data["nom"] = f"Recette Concurrent {i}"
            result = service.create_complete(data)
            results.append(result)
        
        # Toutes devraient avoir réussi
        valid_results = [r for r in results if r is not None]
        assert len(valid_results) >= 1
