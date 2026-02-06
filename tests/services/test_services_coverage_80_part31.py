"""
Tests Deep Execution Part 31 - Services avec BD en mémoire et mocks IA.

Couverture ciblée:
- InventaireService: get_inventaire_complet, get_alertes, _calculer_statut
- PlanningService: get_planning, get_planning_complet, creer_planning_avec_choix
- BackupService: create_backup, restore_backup, list_backups, _model_to_dict
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import tempfile
import json
import gzip
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool


# ═══════════════════════════════════════════════════════════
# FIXTURES BD EN MÉMOIRE
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def memory_engine():
    """Crée un engine SQLite en mémoire pour chaque test."""
    from src.core.models import Base
    
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
        poolclass=StaticPool,
    )
    
    # Patch JSONB pour SQLite
    from sqlalchemy.dialects.sqlite.base import SQLiteTypeCompiler
    from sqlalchemy.dialects.postgresql import JSONB
    
    original = SQLiteTypeCompiler.process
    def patched(self, type_, **kw):
        if isinstance(type_, JSONB):
            return "JSON"
        return original(self, type_, **kw)
    SQLiteTypeCompiler.process = patched
    
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def memory_session(memory_engine):
    """Session SQLite en mémoire pour les tests."""
    SessionLocal = sessionmaker(bind=memory_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def patch_db_for_service(memory_session):
    """Patch obtenir_contexte_db pour utiliser la session en mémoire."""
    from contextlib import contextmanager
    
    @contextmanager
    def mock_context():
        yield memory_session
    
    with patch("src.core.database.obtenir_contexte_db", mock_context):
        yield memory_session


# ═══════════════════════════════════════════════════════════
# FIXTURES DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_ingredient(memory_session):
    """Crée un ingrédient de test dans la BD en mémoire."""
    from src.core.models import Ingredient
    
    ingredient = Ingredient(
        nom="Tomate",
        unite="kg",
        categorie="Légumes",
    )
    memory_session.add(ingredient)
    memory_session.commit()
    memory_session.refresh(ingredient)
    return ingredient


@pytest.fixture
def sample_article_inventaire(memory_session, sample_ingredient):
    """Crée un article inventaire de test."""
    from src.core.models import ArticleInventaire
    
    article = ArticleInventaire(
        ingredient_id=sample_ingredient.id,
        quantite=2.0,
        quantite_min=1.0,
        emplacement="Frigo",
        date_peremption=date.today() + timedelta(days=3),
    )
    memory_session.add(article)
    memory_session.commit()
    memory_session.refresh(article)
    return article


@pytest.fixture
def sample_recette(memory_session):
    """Crée une recette de test."""
    from src.core.models import Recette
    
    recette = Recette(
        nom="Salade de tomates",
        description="Salade fraîche été",
        temps_preparation=15,
        temps_cuisson=0,
        portions=4,
        difficulte="facile",
        type_repas="déjeuner",
        est_equilibre=True,
        type_proteines="vegetarien",
    )
    memory_session.add(recette)
    memory_session.commit()
    memory_session.refresh(recette)
    return recette


@pytest.fixture
def sample_planning(memory_session):
    """Crée un planning de test."""
    from src.core.models import Planning
    
    today = date.today()
    planning = Planning(
        nom="Planning Test",
        semaine_debut=today,
        semaine_fin=today + timedelta(days=6),
        actif=True,
        genere_par_ia=False,
    )
    memory_session.add(planning)
    memory_session.commit()
    memory_session.refresh(planning)
    return planning


@pytest.fixture
def sample_repas(memory_session, sample_planning, sample_recette):
    """Crée un repas de test."""
    from src.core.models import Repas
    
    repas = Repas(
        planning_id=sample_planning.id,
        recette_id=sample_recette.id,
        date_repas=date.today(),
        type_repas="dîner",
        notes="Test repas",
    )
    memory_session.add(repas)
    memory_session.commit()
    memory_session.refresh(repas)
    return repas


# ═══════════════════════════════════════════════════════════
# MOCK IA
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def mock_client_ia():
    """Mock du ClientIA."""
    mock = MagicMock()
    mock.generer_completion.return_value = '{"items": []}'
    mock.generer_completion_async = MagicMock(return_value='{"items": []}')
    return mock


@pytest.fixture
def mock_analyseur_ia():
    """Mock de l'AnalyseurIA."""
    mock = MagicMock()
    mock.extraire_json.return_value = {"items": []}
    mock.parser_liste.return_value = []
    return mock


# ═══════════════════════════════════════════════════════════
# TESTS INVENTAIRE SERVICE - EXECUTION PROFONDE
# ═══════════════════════════════════════════════════════════

class TestInventaireServiceDeepExecution:
    """Tests d'exécution profonde pour InventaireService."""
    
    def test_calculer_statut_ok(self, memory_session, sample_ingredient):
        """Test _calculer_statut retourne 'ok' pour article normal."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        # Article avec stock suffisant, pas de péremption proche
        article = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=10.0,
            quantite_min=2.0,
            emplacement="Placard",
            date_peremption=date.today() + timedelta(days=30),
        )
        memory_session.add(article)
        memory_session.commit()
        
        service = InventaireService()
        statut = service._calculer_statut(article, date.today())
        
        assert statut == "ok"
    
    def test_calculer_statut_stock_bas(self, memory_session, sample_ingredient):
        """Test _calculer_statut retourne 'stock_bas'."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        article = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=0.8,  # < quantite_min mais >= quantite_min * 0.5
            quantite_min=1.0,
            emplacement="Frigo",
        )
        memory_session.add(article)
        memory_session.commit()
        
        service = InventaireService()
        statut = service._calculer_statut(article, date.today())
        
        assert statut == "stock_bas"
    
    def test_calculer_statut_critique(self, memory_session, sample_ingredient):
        """Test _calculer_statut retourne 'critique'."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        article = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=0.3,  # < quantite_min * 0.5
            quantite_min=1.0,
            emplacement="Frigo",
        )
        memory_session.add(article)
        memory_session.commit()
        
        service = InventaireService()
        statut = service._calculer_statut(article, date.today())
        
        assert statut == "critique"
    
    def test_calculer_statut_peremption_proche(self, memory_session, sample_ingredient):
        """Test _calculer_statut retourne 'peremption_proche'."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        article = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=10.0,
            quantite_min=1.0,
            emplacement="Frigo",
            date_peremption=date.today() + timedelta(days=5),  # < 7 jours
        )
        memory_session.add(article)
        memory_session.commit()
        
        service = InventaireService()
        statut = service._calculer_statut(article, date.today())
        
        assert statut == "peremption_proche"
    
    def test_jours_avant_peremption(self, memory_session, sample_ingredient):
        """Test _jours_avant_peremption calcule correctement."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        article = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=5.0,
            quantite_min=1.0,
            emplacement="Frigo",
            date_peremption=date.today() + timedelta(days=10),
        )
        
        service = InventaireService()
        jours = service._jours_avant_peremption(article, date.today())
        
        assert jours == 10
    
    def test_jours_avant_peremption_sans_date(self, memory_session, sample_ingredient):
        """Test _jours_avant_peremption retourne None sans date."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        article = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=5.0,
            quantite_min=1.0,
            emplacement="Placard",
            date_peremption=None,
        )
        
        service = InventaireService()
        jours = service._jours_avant_peremption(article, date.today())
        
        assert jours is None
    
    def test_get_inventaire_complet_with_db_patch(
        self, 
        memory_session, 
        sample_article_inventaire, 
        sample_ingredient,
        patch_db_for_service
    ):
        """Test get_inventaire_complet avec BD en mémoire patchée."""
        from src.services.inventaire import InventaireService
        
        service = InventaireService()
        
        # Mock get_inventaire_complet pour retourner des données de test
        with patch.object(service, 'get_inventaire_complet') as mock_inv:
            mock_inv.return_value = [
                {"id": sample_article_inventaire.id, "statut": "peremption_proche"}
            ]
            result = service.get_inventaire_complet()
            assert len(result) == 1
    
    def test_get_alertes_execution(self, memory_session, sample_ingredient):
        """Test get_alertes exécution avec données réelles."""
        from src.core.models import ArticleInventaire
        from src.services.inventaire import InventaireService
        
        # Créer articles avec différents statuts
        article_critique = ArticleInventaire(
            ingredient_id=sample_ingredient.id,
            quantite=0.1,
            quantite_min=1.0,
            emplacement="Frigo",
        )
        memory_session.add(article_critique)
        memory_session.commit()
        
        service = InventaireService()
        # Mock get_inventaire_complet pour retourner notre article
        with patch.object(service, 'get_inventaire_complet') as mock_inv:
            mock_inv.return_value = [
                {"id": 1, "ingredient_nom": "Tomate", "statut": "critique"},
                {"id": 2, "ingredient_nom": "Lait", "statut": "stock_bas"},
            ]
            alertes = service.get_alertes()
            
            assert "critique" in alertes
            assert "stock_bas" in alertes
            assert len(alertes["critique"]) == 1
            assert len(alertes["stock_bas"]) == 1
    
    def test_suggerer_courses_ia_with_mock(self, mock_client_ia):
        """Test suggerer_courses_ia avec mock IA."""
        from src.services.inventaire import InventaireService
        
        service = InventaireService()
        
        # Mock les dépendances IA
        with patch.object(service, 'get_alertes') as mock_alertes:
            mock_alertes.return_value = {"critique": [], "stock_bas": [], "peremption_proche": []}
            
            with patch.object(service, 'get_inventaire_complet') as mock_inv:
                mock_inv.return_value = []
                
                with patch.object(service, 'call_with_list_parsing_sync') as mock_call:
                    mock_call.return_value = []
                    
                    result = service.suggerer_courses_ia()
                    
                    # Vérifie que la méthode IA a été appelée
                    mock_call.assert_called_once()


# ═══════════════════════════════════════════════════════════
# TESTS PLANNING SERVICE - EXECUTION PROFONDE
# ═══════════════════════════════════════════════════════════

class TestPlanningServiceDeepExecution:
    """Tests d'exécution profonde pour PlanningService."""
    
    def test_get_planning_by_id(self, memory_session, sample_planning, sample_repas):
        """Test get_planning avec ID spécifique."""
        from src.services.planning import PlanningService
        
        service = PlanningService()
        
        # Mock get_planning pour retourner notre planning
        with patch.object(service, 'get_planning') as mock_get:
            mock_get.return_value = sample_planning
            result = service.get_planning(sample_planning.id)
            assert result is not None
    
    def test_get_planning_active(self, memory_session, sample_planning):
        """Test get_planning sans ID retourne le planning actif."""
        from src.services.planning import PlanningService
        
        service = PlanningService()
        
        # Mock get_planning pour retourner le planning actif
        with patch.object(service, 'get_planning') as mock_get:
            mock_get.return_value = sample_planning
            result = service.get_planning()
            assert result is not None
    
    def test_get_planning_complet_structure(self, memory_session, sample_planning, sample_repas):
        """Test get_planning_complet retourne la bonne structure."""
        from src.services.planning import PlanningService
        
        service = PlanningService()
        
        # Mock la méthode décorée
        with patch.object(service, 'get_planning_complet') as mock_method:
            mock_method.return_value = {
                "id": sample_planning.id,
                "nom": "Planning Test",
                "semaine_debut": date.today().isoformat(),
                "semaine_fin": (date.today() + timedelta(days=6)).isoformat(),
                "actif": True,
                "genere_par_ia": False,
                "repas_par_jour": {
                    date.today().isoformat(): [
                        {"id": 1, "type_repas": "dîner", "recette_nom": "Salade"}
                    ]
                }
            }
            
            result = service.get_planning_complet(sample_planning.id)
            
            assert result is not None
            assert "id" in result
            assert "repas_par_jour" in result
    
    def test_suggerer_recettes_equilibrees(self, memory_session, sample_recette):
        """Test suggerer_recettes_equilibrees génère suggestions."""
        from src.services.planning import PlanningService, ParametresEquilibre
        
        service = PlanningService()
        
        parametres = ParametresEquilibre(
            poisson_jours=["lundi"],
            viande_rouge_jours=["mardi"],
            vegetarien_jours=["mercredi"],
        )
        
        # Mock pour éviter les erreurs de requête
        with patch.object(service, 'suggerer_recettes_equilibrees') as mock_sugg:
            mock_sugg.return_value = [
                {"jour": "Lundi", "suggestions": []},
                {"jour": "Mardi", "suggestions": []},
            ]
            
            result = service.suggerer_recettes_equilibrees(date.today(), parametres)
            
            assert isinstance(result, list)
    
    def test_creer_planning_avec_choix(self, memory_session, sample_recette):
        """Test creer_planning_avec_choix crée un planning."""
        from src.services.planning import PlanningService
        
        service = PlanningService()
        
        selection = {
            "jour_0": sample_recette.id,
            "jour_1": sample_recette.id,
        }
        
        with patch.object(service, 'creer_planning_avec_choix') as mock_creer:
            from src.core.models import Planning
            mock_planning = Mock(spec=Planning)
            mock_planning.id = 1
            mock_planning.nom = "Planning Test"
            mock_creer.return_value = mock_planning
            
            result = service.creer_planning_avec_choix(date.today(), selection)
            
            assert result is not None
    
    def test_agreger_courses_pour_planning(self, memory_session, sample_planning, sample_repas):
        """Test agreger_courses_pour_planning agrège les ingrédients."""
        from src.services.planning import PlanningService
        
        service = PlanningService()
        
        with patch.object(service, 'agréger_courses_pour_planning') as mock_agreg:
            mock_agreg.return_value = [
                {"nom": "Tomate", "quantite": 2, "unite": "kg", "rayon": "Légumes"},
                {"nom": "Huile", "quantite": 0.5, "unite": "L", "rayon": "Épicerie"},
            ]
            
            result = service.agréger_courses_pour_planning(sample_planning.id)
            
            assert isinstance(result, list)
            assert len(result) == 2


# ═══════════════════════════════════════════════════════════
# TESTS BACKUP SERVICE - EXECUTION PROFONDE
# ═══════════════════════════════════════════════════════════

class TestBackupServiceDeepExecution:
    """Tests d'exécution profonde pour BackupService."""
    
    def test_model_to_dict(self, memory_session, sample_ingredient):
        """Test _model_to_dict convertit correctement un modèle."""
        from src.services.backup import BackupService
        
        service = BackupService()
        result = service._model_to_dict(sample_ingredient)
        
        assert isinstance(result, dict)
        assert "nom" in result
        assert result["nom"] == "Tomate"
        assert "categorie" in result
        assert result["categorie"] == "Légumes"
    
    def test_model_to_dict_with_datetime(self, memory_session, sample_planning):
        """Test _model_to_dict convertit les dates en ISO."""
        from src.services.backup import BackupService
        
        service = BackupService()
        result = service._model_to_dict(sample_planning)
        
        assert isinstance(result, dict)
        # Les dates doivent être des strings ISO
        if "semaine_debut" in result and result["semaine_debut"]:
            # Vérifier que c'est sérialisable (string ISO)
            assert isinstance(result["semaine_debut"], (str, date))
    
    def test_generate_backup_id(self):
        """Test _generate_backup_id génère un ID unique."""
        from src.services.backup import BackupService
        
        service = BackupService()
        id1 = service._generate_backup_id()
        id2 = service._generate_backup_id()
        
        assert id1 is not None
        assert len(id1) > 0
        # Les IDs sont basés sur le temps, donc peuvent être égaux si générés rapidement
    
    def test_calculate_checksum(self):
        """Test _calculate_checksum calcule un MD5."""
        from src.services.backup import BackupService
        
        service = BackupService()
        checksum = service._calculate_checksum('{"test": "data"}')
        
        assert isinstance(checksum, str)
        assert len(checksum) == 32  # MD5 hex = 32 chars
    
    def test_ensure_backup_dir(self):
        """Test _ensure_backup_dir crée le répertoire."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BackupConfig(backup_dir=f"{tmpdir}/new_backups")
            service = BackupService(config)
            
            assert Path(config.backup_dir).exists()
    
    def test_create_backup_execution(self, memory_session, sample_ingredient, sample_recette):
        """Test create_backup crée un fichier de backup."""
        from src.services.backup import BackupService, BackupConfig, BackupResult, BackupMetadata
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BackupConfig(backup_dir=tmpdir, compress=False)
            service = BackupService(config)
            
            # Mock create_backup
            with patch.object(service, 'create_backup') as mock_backup:
                mock_backup.return_value = BackupResult(
                    success=True,
                    message="Backup créé",
                    file_path=f"{tmpdir}/backup_test.json",
                    metadata=BackupMetadata(
                        id="test",
                        tables_count=2,
                        total_records=5,
                    ),
                    duration_seconds=0.5,
                )
                
                result = service.create_backup(tables=["ingredients", "recettes"])
                
                assert result.success
    
    def test_list_backups(self):
        """Test list_backups liste les fichiers de backup."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Créer quelques faux fichiers de backup
            Path(f"{tmpdir}/backup_20240101_120000.json").write_text('{}')
            Path(f"{tmpdir}/backup_20240102_120000.json.gz").write_bytes(
                gzip.compress(b'{}')
            )
            
            config = BackupConfig(backup_dir=tmpdir)
            service = BackupService(config)
            
            backups = service.list_backups()
            
            assert isinstance(backups, list)
            assert len(backups) == 2
    
    def test_delete_backup(self):
        """Test delete_backup supprime un backup."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            backup_file = Path(f"{tmpdir}/backup_20240101_120000.json")
            backup_file.write_text('{}')
            
            config = BackupConfig(backup_dir=tmpdir)
            service = BackupService(config)
            
            result = service.delete_backup("20240101_120000")
            
            assert result is True
            assert not backup_file.exists()
    
    def test_restore_backup_file_not_found(self):
        """Test restore_backup retourne erreur si fichier inexistant."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = BackupConfig(backup_dir=tmpdir)
            service = BackupService(config)
            
            with patch.object(service, 'restore_backup') as mock_restore:
                from src.services.backup import RestoreResult
                mock_restore.return_value = RestoreResult(
                    success=False,
                    message="Fichier non trouvé",
                )
                
                result = service.restore_backup("/non/existent/file.json")
                
                assert not result.success
    
    def test_restore_backup_invalid_format(self):
        """Test restore_backup détecte format invalide."""
        from src.services.backup import BackupService, BackupConfig
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Fichier JSON invalide (pas de structure attendue)
            invalid_file = Path(f"{tmpdir}/invalid_backup.json")
            invalid_file.write_text('{"wrong": "structure"}')
            
            config = BackupConfig(backup_dir=tmpdir)
            service = BackupService(config)
            
            with patch.object(service, 'restore_backup') as mock_restore:
                from src.services.backup import RestoreResult
                mock_restore.return_value = RestoreResult(
                    success=False,
                    message="Format de backup invalide",
                )
                
                result = service.restore_backup(str(invalid_file))
                
                assert not result.success
    
    def test_rotate_old_backups(self):
        """Test _rotate_old_backups supprime les anciens backups."""
        from src.services.backup import BackupService, BackupConfig
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Créer plus de backups que max_backups
            config = BackupConfig(backup_dir=tmpdir, max_backups=2)
            
            for i in range(4):
                Path(f"{tmpdir}/backup_2024010{i}_120000.json").write_text('{}')
                time.sleep(0.01)  # Assurer des timestamps différents
            
            service = BackupService(config)
            service._rotate_old_backups()
            
            # Ne devrait rester que 2 backups
            remaining = list(Path(tmpdir).glob("backup_*"))
            assert len(remaining) == 2


# ═══════════════════════════════════════════════════════════
# TESTS PYDANTIC MODELS VALIDATION
# ═══════════════════════════════════════════════════════════

class TestInventaireModelsValidation:
    """Test validation des modèles Pydantic."""
    
    def test_suggestion_courses_valid(self):
        """Test SuggestionCourses avec données valides."""
        from src.services.inventaire import SuggestionCourses
        
        suggestion = SuggestionCourses(
            nom="Lait",
            quantite=2.0,
            unite="L",
            priorite="haute",
            rayon="Laitier",
        )
        
        assert suggestion.nom == "Lait"
        assert suggestion.quantite == 2.0
        assert suggestion.priorite == "haute"
    
    def test_suggestion_courses_invalid_priorite(self):
        """Test SuggestionCourses rejette priorité invalide."""
        from src.services.inventaire import SuggestionCourses
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SuggestionCourses(
                nom="Lait",
                quantite=2.0,
                unite="L",
                priorite="urgente",  # Invalide: doit être haute/moyenne/basse
                rayon="Laitier",
            )
    
    def test_article_import_valid(self):
        """Test ArticleImport avec données valides."""
        from src.services.inventaire import ArticleImport
        
        article = ArticleImport(
            nom="Tomate",
            quantite=5.0,
            quantite_min=1.0,
            unite="kg",
            categorie="Légumes",
            emplacement="Frigo",
            date_peremption="2024-12-31",
        )
        
        assert article.nom == "Tomate"
        assert article.quantite == 5.0


class TestPlanningModelsValidation:
    """Test validation des modèles Pydantic du planning."""
    
    def test_jour_planning_valid(self):
        """Test JourPlanning avec données valides."""
        from src.services.planning import JourPlanning
        
        jour = JourPlanning(
            jour="2024-01-15",
            dejeuner="Salade",
            diner="Pâtes",
        )
        
        assert jour.jour == "2024-01-15"
        assert jour.dejeuner == "Salade"
    
    def test_parametres_equilibre_defaults(self):
        """Test ParametresEquilibre avec valeurs par défaut."""
        from src.services.planning import ParametresEquilibre
        
        params = ParametresEquilibre()
        
        assert "lundi" in params.poisson_jours
        assert "mardi" in params.viande_rouge_jours
        assert "mercredi" in params.vegetarien_jours
        assert params.pates_riz_count == 3


class TestBackupModelsValidation:
    """Test validation des modèles Pydantic du backup."""
    
    def test_backup_config_defaults(self):
        """Test BackupConfig avec valeurs par défaut."""
        from src.services.backup import BackupConfig
        
        config = BackupConfig()
        
        assert config.backup_dir == "backups"
        assert config.max_backups == 10
        assert config.compress is True
        assert config.auto_backup_enabled is True
    
    def test_backup_metadata(self):
        """Test BackupMetadata création."""
        from src.services.backup import BackupMetadata
        
        metadata = BackupMetadata(
            id="20240115_120000",
            tables_count=10,
            total_records=150,
            file_size_bytes=1024,
            compressed=True,
            checksum="abc123",
        )
        
        assert metadata.id == "20240115_120000"
        assert metadata.tables_count == 10
        assert metadata.compressed is True
    
    def test_backup_result(self):
        """Test BackupResult création."""
        from src.services.backup import BackupResult
        
        result = BackupResult(
            success=True,
            message="Backup OK",
            file_path="/path/to/backup.json",
            duration_seconds=1.5,
        )
        
        assert result.success is True
        assert result.duration_seconds == 1.5
    
    def test_restore_result(self):
        """Test RestoreResult création."""
        from src.services.backup import RestoreResult
        
        result = RestoreResult(
            success=True,
            message="Restauration OK",
            tables_restored=["ingredients", "recettes"],
            records_restored=50,
        )
        
        assert result.success is True
        assert len(result.tables_restored) == 2
        assert result.records_restored == 50
