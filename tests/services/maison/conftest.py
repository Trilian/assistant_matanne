"""
Fixtures partagées pour les tests des services maison.

Fournit:
- Mocks du client IA
- Session DB de test
- Données de test (projets, tâches, objets...)
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.orm import Session

from src.core.ai import ClientIA

# ═══════════════════════════════════════════════════════════
# FIXTURES CLIENT IA
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_client_ia() -> MagicMock:
    """Mock du client IA pour éviter les appels réels."""
    client = MagicMock(spec=ClientIA)

    # Simuler les réponses async
    client.generer = AsyncMock(return_value="Réponse simulée de l'IA")
    client.generer_json = AsyncMock(return_value={"result": "ok"})

    return client


@pytest.fixture
def mock_ia_response() -> str:
    """Réponse IA simulée standard."""
    return "Conseil simulé pour le test"


@pytest.fixture
def mock_ia_json_response() -> dict:
    """Réponse JSON IA simulée."""
    return {
        "conseils": ["Conseil 1", "Conseil 2"],
        "score": 85,
        "recommandations": ["Reco 1"],
    }


# ═══════════════════════════════════════════════════════════
# FIXTURES DONNÉES DE TEST
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def projet_test_data() -> dict:
    """Données de test pour un projet bricolage."""
    return {
        "id": 1,
        "nom": "Peinture chambre",
        "description": "Repeindre les murs de la chambre en blanc",
        "budget_estime": Decimal("200.00"),
        "date_debut_prevue": date.today(),
        "date_fin_prevue": date.today() + timedelta(days=7),
        "statut": "en_cours",
    }


@pytest.fixture
def tache_entretien_data() -> dict:
    """Données de test pour une tâche d'entretien."""
    return {
        "id": 1,
        "nom": "Nettoyage complet",
        "frequence": "hebdomadaire",
        "derniere_execution": date.today() - timedelta(days=8),
        "duree_minutes": 60,
        "pieces": ["Salon", "Cuisine", "Salle de bain"],
    }


@pytest.fixture
def plante_jardin_data() -> dict:
    """Données de test pour une plante du jardin."""
    return {
        "id": 1,
        "nom": "Tomate Roma",
        "variete": "Roma",
        "date_plantation": date.today() - timedelta(days=45),
        "position_x": 2.5,
        "position_y": 3.0,
        "zone_id": 1,
        "etat": "en_croissance",
        "derniere_irrigation": date.today() - timedelta(days=2),
    }


@pytest.fixture
def zone_jardin_data() -> dict:
    """Données de test pour une zone du jardin."""
    return {
        "id": 1,
        "nom": "Potager principal",
        "type": "potager",
        "x": 0.0,
        "y": 0.0,
        "largeur": 5.0,
        "hauteur": 4.0,
        "exposition": "sud",
    }


@pytest.fixture
def piece_maison_data() -> dict:
    """Données de test pour une pièce de la maison."""
    return {
        "id": 1,
        "nom": "Garage",
        "etage": 0,
        "surface_m2": 25.0,
        "conteneurs": [
            {"nom": "Établi", "type": "meuble"},
            {"nom": "Caisse outils", "type": "boite"},
        ],
    }


@pytest.fixture
def objet_inventaire_data() -> dict:
    """Données de test pour un objet de l'inventaire."""
    return {
        "id": 1,
        "nom": "Perceuse Bosch",
        "categorie": "outillage",
        "code_barre": "4006429040010",
        "piece_id": 1,
        "conteneur_id": 1,
        "valeur_estimee": Decimal("85.00"),
        "date_achat": date(2022, 3, 15),
    }


@pytest.fixture
def consommation_energie_data() -> dict:
    """Données de test pour la consommation énergétique."""
    return {
        "mois": date.today().month,
        "annee": date.today().year,
        "electricite_kwh": 320.5,
        "gaz_m3": 45.2,
        "eau_m3": 12.8,
        "cout_total": Decimal("185.50"),
    }


@pytest.fixture
def meteo_data() -> dict:
    """Données météo simulées."""
    return {
        "temperature": 18.5,
        "temperature_min": 12.0,
        "temperature_max": 22.0,
        "humidite": 65,
        "precipitation_mm": 0,
        "vent_kmh": 12,
        "description": "Ensoleillé",
        "gel_prevu": False,
    }


@pytest.fixture
def meteo_gel_data() -> dict:
    """Données météo avec gel simulées."""
    return {
        "temperature": 2.0,
        "temperature_min": -3.0,
        "temperature_max": 8.0,
        "humidite": 85,
        "precipitation_mm": 0,
        "vent_kmh": 5,
        "description": "Nuageux",
        "gel_prevu": True,
    }


# ═══════════════════════════════════════════════════════════
# FIXTURES SERVICES MOCKÉS
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_entretien_service(mock_client_ia):
    """Service entretien avec client IA mocké."""
    from src.services.maison.entretien_service import EntretienService

    with patch.object(EntretienService, "__init__", lambda self, client=None: None):
        service = EntretienService.__new__(EntretienService)
        service.client = mock_client_ia
        service._cache_prefix = "test_entretien"
        service._default_ttl = 3600
        service._service_name = "test_entretien"
        return service


@pytest.fixture
def mock_jardin_service(mock_client_ia):
    """Service jardin avec client IA mocké."""
    from src.services.maison.jardin_service import JardinService

    with patch.object(JardinService, "__init__", lambda self, client=None: None):
        service = JardinService.__new__(JardinService)
        service.client = mock_client_ia
        service._cache_prefix = "test_jardin"
        service._default_ttl = 3600
        service._service_name = "test_jardin"
        return service


@pytest.fixture
def mock_projets_service(mock_client_ia):
    """Service projets avec client IA mocké."""
    from src.services.maison.projets_service import ProjetsService

    with patch.object(ProjetsService, "__init__", lambda self, client=None: None):
        service = ProjetsService.__new__(ProjetsService)
        service.client = mock_client_ia
        service._cache_prefix = "test_projets"
        service._default_ttl = 3600
        service._service_name = "test_projets"
        return service


@pytest.fixture
def mock_energie_service(mock_client_ia):
    """Service énergie avec client IA mocké."""
    from src.services.maison.energie_service import EnergieService

    with patch.object(EnergieService, "__init__", lambda self, client=None: None):
        service = EnergieService.__new__(EnergieService)
        service.client = mock_client_ia
        service._cache_prefix = "test_energie"
        service._default_ttl = 3600
        service._service_name = "test_energie"
        return service


# ═══════════════════════════════════════════════════════════
# HELPERS DE TEST
# ═══════════════════════════════════════════════════════════


def assert_valid_briefing(briefing):
    """Vérifie qu'un briefing maison est valide."""
    assert briefing is not None
    assert hasattr(briefing, "date")
    assert hasattr(briefing, "resume")
    assert hasattr(briefing, "taches_jour")
    assert hasattr(briefing, "alertes")


def assert_valid_eco_score(score):
    """Vérifie qu'un éco-score est valide."""
    assert score is not None
    assert hasattr(score, "score")
    assert 0 <= score.score <= 100
    assert hasattr(score, "badges")


def assert_valid_pipeline_result(result):
    """Vérifie qu'un résultat de pipeline est valide."""
    assert result is not None
    assert hasattr(result, "succes")
    assert hasattr(result, "pipeline")
    assert hasattr(result, "etapes_completees")
    assert isinstance(result.etapes_completees, list)
