"""
Tests unitaires pour jardin.py

Module: src.core.models.jardin
Contient: AlerteMeteo, ConfigMeteo, NiveauAlerte, TypeAlerteMeteo
"""

from datetime import date
from decimal import Decimal

from src.core.models.jardin import (
    AlerteMeteo,
    ConfigMeteo,
    NiveauAlerte,
    TypeAlerteMeteo,
)

# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestNiveauAlerte:
    """Tests pour l'énumération NiveauAlerte."""

    def test_valeurs_disponibles(self):
        """Vérifie les niveaux d'alerte."""
        assert NiveauAlerte.INFO.value == "info"
        assert NiveauAlerte.ATTENTION.value == "attention"
        assert NiveauAlerte.DANGER.value == "danger"


class TestTypeAlerteMeteo:
    """Tests pour l'énumération TypeAlerteMeteo."""

    def test_valeurs_principales(self):
        """Vérifie les types d'alertes météo."""
        assert TypeAlerteMeteo.GEL.value == "gel"
        assert TypeAlerteMeteo.CANICULE.value == "canicule"
        assert TypeAlerteMeteo.PLUIE_FORTE.value == "pluie_forte"


# ═══════════════════════════════════════════════════════════
# TESTS MODÈLES
# ═══════════════════════════════════════════════════════════


class TestAlerteMeteo:
    """Tests pour le modèle AlerteMeteo."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert AlerteMeteo.__tablename__ == "alertes_meteo"

    def test_creation_instance(self):
        """Test de création d'une alerte."""
        alerte = AlerteMeteo(
            type_alerte="gel",
            niveau="attention",
            titre="Alerte gel",
            date_debut=date(2026, 2, 10),
        )
        assert alerte.type_alerte == "gel"
        assert alerte.niveau == "attention"
        assert alerte.titre == "Alerte gel"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = AlerteMeteo.__table__.columns
        assert colonnes["niveau"].default is not None
        assert colonnes["lu"].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        alerte = AlerteMeteo(id=1, type_alerte="gel", niveau="danger")
        result = repr(alerte)
        assert "AlerteMeteo" in result
        assert "gel" in result


class TestConfigMeteo:
    """Tests pour le modèle ConfigMeteo."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert ConfigMeteo.__tablename__ == "config_meteo"

    def test_creation_instance(self):
        """Test de création d'une config."""
        config = ConfigMeteo(
            ville="Lyon",
            latitude=Decimal("45.7640"),
            longitude=Decimal("4.8357"),
        )
        assert config.ville == "Lyon"

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut (Paris)."""
        colonnes = ConfigMeteo.__table__.columns
        assert colonnes["ville"].default is not None
        assert colonnes["notifications_gel"].default is not None
        assert colonnes["notifications_canicule"].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        config = ConfigMeteo(id=1, ville="Bordeaux")
        result = repr(config)
        assert "ConfigMeteo" in result
        assert "Bordeaux" in result
