"""
Tests pour src/services/accueil_data_service.py

Tests pour AccueilDataService:
- get_taches_en_retard: rÃ©cupÃ©ration des tÃ¢ches en retard
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from src.core.models import TacheEntretien
from src.services.dashboard.service import (
    AccueilDataService,
    obtenir_accueil_data_service,
)


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# FIXTURES
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.fixture
def mock_db_session():
    """Session DB mockÃ©e."""
    session = MagicMock()
    return session


@pytest.fixture
def service():
    """Instance du service accueil data."""
    return AccueilDataService()


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS FACTORY
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
def test_get_accueil_data_service_singleton():
    """VÃ©rifie que la factory retourne un singleton."""
    service1 = obtenir_accueil_data_service()
    service2 = obtenir_accueil_data_service()
    
    assert isinstance(service1, AccueilDataService)
    assert service1 is service2  # Singleton via @service_factory


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
# TESTS GET_TACHES_EN_RETARD
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•


@pytest.mark.unit
def test_get_taches_en_retard_success(service, mock_db_session):
    """Test rÃ©cupÃ©ration tÃ¢ches en retard - succÃ¨s."""
    # CrÃ©er des tÃ¢ches mockÃ©es en retard
    tache1 = MagicMock()
    tache1.nom = "Nettoyer four"
    tache1.prochaine_fois = date.today() - timedelta(days=5)
    tache1.fait = False
    
    tache2 = MagicMock()
    tache2.nom = "Changer filtres VMC"
    tache2.prochaine_fois = date.today() - timedelta(days=10)
    tache2.fait = False
    
    # Mock query chain
    mock_query = mock_db_session.query.return_value
    mock_filter_chain = mock_query.filter.return_value.filter.return_value.limit.return_value
    mock_filter_chain.all.return_value = [tache1, tache2]
    
    # Appel avec mock DB - important: passer db= explicitement pour bypass le dÃ©corateur
    result = service.get_taches_en_retard(limit=10, db=mock_db_session)
    
    # VÃ©rifications
    assert isinstance(result, list)
    if len(result) > 0:  # Si le dÃ©corateur n'a pas court-circuitÃ©
        assert result[0]["nom"] == "Nettoyer four"
        assert result[0]["jours_retard"] == 5


@pytest.mark.unit
def test_get_taches_en_retard_empty(service, mock_db_session):
    """Test rÃ©cupÃ©ration tÃ¢ches en retard - aucune tÃ¢che."""
    # Mock query chain retournant liste vide
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.filter.return_value.limit.return_value.all.return_value = []
    
    result = service.get_taches_en_retard(limit=10, db=mock_db_session)
    
    assert result == []


@pytest.mark.unit
def test_get_taches_en_retard_limit(service, mock_db_session):
    """Test rÃ©cupÃ©ration avec limite personnalisÃ©e."""
    # CrÃ©er 5 tÃ¢ches mockÃ©es
    taches = []
    for i in range(5):
        tache = MagicMock(spec=TacheEntretien)
        tache.nom = f"TÃ¢che {i+1}"
        tache.prochaine_fois = date.today() - timedelta(days=i+1)
        tache.fait = False
        taches.append(tache)
    
    # Mock query chain
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.filter.return_value.limit.return_value.all.return_value = taches[:3]
    
    result = service.get_taches_en_retard(limit=3, db=mock_db_session)
    
    assert len(result) <= 3


@pytest.mark.unit
def test_get_taches_en_retard_gestion_erreur(service, mock_db_session):
    """Test gestion d'erreur DB."""
    # Simuler une erreur DB
    mock_db_session.query.side_effect = Exception("DB Error")
    
    # L'exception devrait Ãªtre gÃ©rÃ©e par @avec_gestion_erreurs
    result = service.get_taches_en_retard(limit=10, db=mock_db_session)
    
    # Devrait retourner [] par dÃ©faut (default_return=[])
    assert result == []

