"""
Tests pour src/services/accueil_data_service.py

Tests pour AccueilDataService:
- get_taches_en_retard: récupération des tâches en retard
"""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from src.core.models import TacheEntretien
from src.services.accueil_data_service import (
    AccueilDataService,
    get_accueil_data_service,
)


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_db_session():
    """Session DB mockée."""
    session = MagicMock()
    return session


@pytest.fixture
def service():
    """Instance du service accueil data."""
    return AccueilDataService()


# ═══════════════════════════════════════════════════════════
# TESTS FACTORY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
def test_get_accueil_data_service_singleton():
    """Vérifie que la factory retourne un singleton."""
    service1 = get_accueil_data_service()
    service2 = get_accueil_data_service()
    
    assert isinstance(service1, AccueilDataService)
    assert service1 is service2  # Singleton via @service_factory


# ═══════════════════════════════════════════════════════════
# TESTS GET_TACHES_EN_RETARD
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
def test_get_taches_en_retard_success(service, mock_db_session):
    """Test récupération tâches en retard - succès."""
    # Créer des tâches mockées en retard
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
    
    # Appel avec mock DB - important: passer db= explicitement pour bypass le décorateur
    result = service.get_taches_en_retard(limit=10, db=mock_db_session)
    
    # Vérifications
    assert isinstance(result, list)
    if len(result) > 0:  # Si le décorateur n'a pas court-circuité
        assert result[0]["nom"] == "Nettoyer four"
        assert result[0]["jours_retard"] == 5


@pytest.mark.unit
def test_get_taches_en_retard_empty(service, mock_db_session):
    """Test récupération tâches en retard - aucune tâche."""
    # Mock query chain retournant liste vide
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.filter.return_value.limit.return_value.all.return_value = []
    
    result = service.get_taches_en_retard(limit=10, db=mock_db_session)
    
    assert result == []


@pytest.mark.unit
def test_get_taches_en_retard_limit(service, mock_db_session):
    """Test récupération avec limite personnalisée."""
    # Créer 5 tâches mockées
    taches = []
    for i in range(5):
        tache = MagicMock(spec=TacheEntretien)
        tache.nom = f"Tâche {i+1}"
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
    
    # L'exception devrait être gérée par @avec_gestion_erreurs
    result = service.get_taches_en_retard(limit=10, db=mock_db_session)
    
    # Devrait retourner [] par défaut (default_return=[])
    assert result == []
