"""
Tests complets pour src/services/batch_cooking.py

Couverture cible: >80%
"""

import pytest
from datetime import date, datetime, time, timedelta
from unittest.mock import Mock, patch, MagicMock


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SCHÃ‰MAS PYDANTIC
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestEtapeBatchIA:
    """Tests schÃ©ma EtapeBatchIA."""

    def test_import_schema(self):
        from src.services.batch_cooking import EtapeBatchIA
        assert EtapeBatchIA is not None

    def test_creation_valide(self):
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=1,
            titre="PrÃ©parer les lÃ©gumes",
            description="Ã‰plucher et couper les lÃ©gumes",
            duree_minutes=15
        )
        
        assert etape.ordre == 1
        assert etape.titre == "PrÃ©parer les lÃ©gumes"
        assert etape.duree_minutes == 15

    def test_champs_optionnels(self):
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=2,
            titre="Cuisson",
            description="Cuire au four",
            duree_minutes=30,
            robots=["four"],
            groupe_parallele=1,
            est_supervision=True,
            alerte_bruit=False,
            temperature=180,
            recette_nom="Gratin"
        )
        
        assert etape.robots == ["four"]
        assert etape.groupe_parallele == 1
        assert etape.est_supervision is True
        assert etape.temperature == 180

    def test_validation_ordre_min(self):
        from src.services.batch_cooking import EtapeBatchIA
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EtapeBatchIA(
                ordre=0,  # Doit Ãªtre >= 1
                titre="Test",
                description="Test description",
                duree_minutes=10
            )

    def test_validation_duree_max(self):
        from src.services.batch_cooking import EtapeBatchIA
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            EtapeBatchIA(
                ordre=1,
                titre="Test",
                description="Test description",
                duree_minutes=200  # Max 180
            )


class TestSessionBatchIA:
    """Tests schÃ©ma SessionBatchIA."""

    def test_creation_valide(self):
        from src.services.batch_cooking import SessionBatchIA, EtapeBatchIA
        
        session = SessionBatchIA(
            recettes=["Poulet rÃ´ti", "Gratin dauphinois"],
            duree_totale_estimee=120,
            etapes=[
                EtapeBatchIA(
                    ordre=1,
                    titre="PrÃ©paration",
                    description="PrÃ©parer ingrÃ©dients",
                    duree_minutes=30
                )
            ]
        )
        
        assert len(session.recettes) == 2
        assert session.duree_totale_estimee == 120
        assert len(session.etapes) == 1

    def test_validation_recettes_min(self):
        from src.services.batch_cooking import SessionBatchIA, EtapeBatchIA
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SessionBatchIA(
                recettes=[],  # min_length=1
                duree_totale_estimee=60,
                etapes=[
                    EtapeBatchIA(
                        ordre=1,
                        titre="Test",
                        description="Test",
                        duree_minutes=10
                    )
                ]
            )


class TestPreparationIA:
    """Tests schÃ©ma PreparationIA."""

    def test_creation_valide(self):
        from src.services.batch_cooking import PreparationIA
        
        prep = PreparationIA(
            nom="Sauce bolognaise",
            portions=8,
            conservation_jours=5,
            localisation="frigo",
            container_suggere="Bocal en verre"
        )
        
        assert prep.nom == "Sauce bolognaise"
        assert prep.portions == 8
        assert prep.conservation_jours == 5

    def test_valeurs_par_defaut(self):
        from src.services.batch_cooking import PreparationIA
        
        prep = PreparationIA(
            nom="Test",
            portions=4,
            conservation_jours=3
        )
        
        assert prep.localisation == "frigo"
        assert prep.container_suggere == ""


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS CONSTANTES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBatchCookingConstants:
    """Tests constantes du module."""

    def test_jours_semaine(self):
        from src.services.batch_cooking import JOURS_SEMAINE
        
        assert len(JOURS_SEMAINE) == 7
        assert JOURS_SEMAINE[0] == "Lundi"
        assert JOURS_SEMAINE[6] == "Dimanche"

    def test_robots_disponibles(self):
        from src.services.batch_cooking import ROBOTS_DISPONIBLES
        
        assert "cookeo" in ROBOTS_DISPONIBLES
        assert "monsieur_cuisine" in ROBOTS_DISPONIBLES
        assert "four" in ROBOTS_DISPONIBLES
        assert "airfryer" in ROBOTS_DISPONIBLES
        
        # VÃ©rifier structure
        cookeo = ROBOTS_DISPONIBLES["cookeo"]
        assert "nom" in cookeo
        assert "emoji" in cookeo
        assert "parallele" in cookeo


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS SERVICE BATCH COOKING
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBatchCookingServiceInit:
    """Tests initialisation du service."""

    def test_import_service(self):
        from src.services.batch_cooking import BatchCookingService
        assert BatchCookingService is not None

    def test_init_service(self):
        from src.services.batch_cooking import BatchCookingService
        
        service = BatchCookingService()
        
        # VÃ©rifier que le service est bien crÃ©Ã©
        assert service is not None

    def test_heritage_multiple(self):
        from src.services.batch_cooking import BatchCookingService
        from src.services.types import BaseService
        from src.services.base_ai_service import BaseAIService
        
        service = BatchCookingService()
        
        assert isinstance(service, BaseService)
        assert isinstance(service, BaseAIService)


class TestBatchCookingServiceGetConfig:
    """Tests get_config."""

    def test_methode_existe(self):
        from src.services.batch_cooking import BatchCookingService
        
        service = BatchCookingService()
        
        assert hasattr(service, 'get_config')
        assert callable(service.get_config)


class TestBatchCookingServiceMethods:
    """Tests des mÃ©thodes du service."""

    def test_service_has_expected_methods(self):
        from src.services.batch_cooking import BatchCookingService
        
        service = BatchCookingService()
        
        # MÃ©thodes hÃ©ritÃ©es de BaseService
        assert hasattr(service, 'get_all')
        assert hasattr(service, 'get_by_id')
        assert hasattr(service, 'create')
        assert hasattr(service, 'update')
        assert hasattr(service, 'delete')
        
        # MÃ©thodes hÃ©ritÃ©es de BaseAIService
        assert hasattr(service, 'call_with_list_parsing_sync')


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS MODELS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBatchCookingModels:
    """Tests imports des modÃ¨les."""

    def test_import_models(self):
        from src.core.models import (
            ConfigBatchCooking,
            SessionBatchCooking,
            EtapeBatchCooking,
            PreparationBatch,
            StatutSessionEnum,
            StatutEtapeEnum,
            TypeRobotEnum,
            LocalisationStockageEnum,
        )
        
        assert ConfigBatchCooking is not None
        assert SessionBatchCooking is not None
        assert StatutSessionEnum is not None

    def test_statut_session_enum(self):
        from src.core.models import StatutSessionEnum
        
        # VÃ©rifier que l'enum a des valeurs
        assert len(StatutSessionEnum) > 0

    def test_type_robot_enum(self):
        from src.core.models import TypeRobotEnum
        
        assert len(TypeRobotEnum) > 0


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS EDGE CASES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


class TestBatchCookingEdgeCases:
    """Tests cas limites."""

    def test_etape_duree_minimale(self):
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=1,
            titre="Test rapide",
            description="Une Ã©tape trÃ¨s courte",
            duree_minutes=1  # Minimum
        )
        
        assert etape.duree_minutes == 1

    def test_etape_duree_maximale(self):
        from src.services.batch_cooking import EtapeBatchIA
        
        etape = EtapeBatchIA(
            ordre=1,
            titre="Cuisson longue",
            description="Mijoter pendant 3 heures",
            duree_minutes=180  # Maximum
        )
        
        assert etape.duree_minutes == 180

    def test_session_duree_min(self):
        from src.services.batch_cooking import SessionBatchIA, EtapeBatchIA
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SessionBatchIA(
                recettes=["Test"],
                duree_totale_estimee=4,  # Min is 5
                etapes=[
                    EtapeBatchIA(
                        ordre=1,
                        titre="Test",
                        description="Test",
                        duree_minutes=4
                    )
                ]
            )

    def test_session_duree_max(self):
        from src.services.batch_cooking import SessionBatchIA, EtapeBatchIA
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            SessionBatchIA(
                recettes=["Test"],
                duree_totale_estimee=500,  # Max is 480
                etapes=[
                    EtapeBatchIA(
                        ordre=1,
                        titre="Test",
                        description="Test",
                        duree_minutes=10
                    )
                ]
            )

    def test_preparation_portions_limites(self):
        from src.services.batch_cooking import PreparationIA
        from pydantic import ValidationError
        
        # Minimum
        prep = PreparationIA(
            nom="Test",
            portions=1,
            conservation_jours=3
        )
        assert prep.portions == 1
        
        # Maximum
        prep = PreparationIA(
            nom="Test",
            portions=20,
            conservation_jours=3
        )
        assert prep.portions == 20
        
        # Trop
        with pytest.raises(ValidationError):
            PreparationIA(
                nom="Test",
                portions=25,
                conservation_jours=3
            )

    def test_temperature_limites(self):
        from src.services.batch_cooking import EtapeBatchIA
        from pydantic import ValidationError
        
        # TempÃ©rature valide
        etape = EtapeBatchIA(
            ordre=1,
            titre="Cuisson",
            description="Description test",
            duree_minutes=30,
            temperature=200
        )
        assert etape.temperature == 200
        
        # TempÃ©rature 0 (valide - ex: congÃ©lation)
        etape = EtapeBatchIA(
            ordre=1,
            titre="CongÃ©lation",
            description="Description test",
            duree_minutes=30,
            temperature=0
        )
        assert etape.temperature == 0
        
        # TempÃ©rature trop Ã©levÃ©e
        with pytest.raises(ValidationError):
            EtapeBatchIA(
                ordre=1,
                titre="Test chaud",
                description="Description test",
                duree_minutes=30,
                temperature=350  # Max 300
            )


class TestBatchCookingIntegration:
    """Tests d'intÃ©gration."""

    def test_workflow_session_complÃ¨te(self):
        from src.services.batch_cooking import SessionBatchIA, EtapeBatchIA
        
        # CrÃ©er une session complÃ¨te avec plusieurs Ã©tapes
        etapes = [
            EtapeBatchIA(
                ordre=1,
                titre="PrÃ©paration lÃ©gumes",
                description="Ã‰plucher et couper tous les lÃ©gumes",
                duree_minutes=20,
                robots=["hachoir"],
                groupe_parallele=0
            ),
            EtapeBatchIA(
                ordre=2,
                titre="Cuisson poulet",
                description="Cuire le poulet au four",
                duree_minutes=45,
                robots=["four"],
                groupe_parallele=1,
                temperature=180
            ),
            EtapeBatchIA(
                ordre=3,
                titre="Sauce",
                description="PrÃ©parer la sauce au Cookeo",
                duree_minutes=30,
                robots=["cookeo"],
                groupe_parallele=1,  # En parallÃ¨le avec le four
                est_supervision=True
            ),
        ]
        
        session = SessionBatchIA(
            recettes=["Poulet rÃ´ti", "Sauce aux champignons"],
            duree_totale_estimee=95,
            etapes=etapes,
            conseils_jules=["Faire participer Jules Ã  la prÃ©paration des lÃ©gumes"],
            ordre_optimal="Commencer par les lÃ©gumes puis lancer four et Cookeo en parallÃ¨le"
        )
        
        assert len(session.etapes) == 3
        assert session.duree_totale_estimee == 95
        assert len(session.conseils_jules) == 1

    def test_robots_paralleles(self):
        from src.services.batch_cooking import ROBOTS_DISPONIBLES
        
        # VÃ©rifier quels robots peuvent tourner en parallÃ¨le
        robots_paralleles = [k for k, v in ROBOTS_DISPONIBLES.items() if v["parallele"]]
        robots_non_paralleles = [k for k, v in ROBOTS_DISPONIBLES.items() if not v["parallele"]]
        
        # La plupart des robots peuvent Ãªtre en parallÃ¨le
        assert len(robots_paralleles) > len(robots_non_paralleles)
        
        # Plaques et hachoir ne sont pas parallÃ¨les (nÃ©cessitent attention)
        assert "plaques" in robots_non_paralleles
        assert "mixeur" in robots_non_paralleles
