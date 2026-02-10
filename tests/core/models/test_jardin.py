"""
Tests unitaires pour jardin.py

Module: src.core.models.jardin
Contient: GardenZone, AlerteMeteo, ConfigMeteo
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

from src.core.models.jardin import (
    GardenZone,
    AlerteMeteo,
    ConfigMeteo,
    GardenZoneType,
    NiveauAlerte,
    TypeAlerteMeteo,
)


# ═══════════════════════════════════════════════════════════
# TESTS ENUMS
# ═══════════════════════════════════════════════════════════


class TestGardenZoneType:
    """Tests pour l'énumération GardenZoneType."""

    def test_valeurs_disponibles(self):
        """Vérifie que toutes les valeurs attendues existent."""
        valeurs = [v.value for v in GardenZoneType]
        assert "pelouse" in valeurs
        assert "potager" in valeurs
        assert "piscine" in valeurs
        assert "terrasse" in valeurs

    def test_acces_membre(self):
        """Test d'accès aux membres."""
        assert GardenZoneType.PELOUSE.value == "pelouse"
        assert GardenZoneType.POTAGER.value == "potager"


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


class TestGardenZone:
    """Tests pour le modèle GardenZone."""

    def test_tablename(self):
        """Vérifie le nom de la table."""
        assert GardenZone.__tablename__ == "garden_zones"

    def test_creation_instance(self):
        """Test de création d'une zone."""
        zone = GardenZone(
            nom="Pelouse principale",
            type_zone="pelouse",
            surface_m2=500,
            etat_note=3,
        )
        assert zone.nom == "Pelouse principale"
        assert zone.type_zone == "pelouse"
        assert zone.surface_m2 == 500
        assert zone.etat_note == 3

    def test_colonnes_avec_defauts(self):
        """Vérifie que les colonnes ont des valeurs par défaut."""
        colonnes = GardenZone.__table__.columns
        assert colonnes['etat_note'].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        zone = GardenZone(id=1, nom="Zone test", etat_note=4)
        result = repr(zone)
        assert "GardenZone" in result
        assert "Zone test" in result


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
        assert colonnes['niveau'].default is not None
        assert colonnes['lu'].default is not None

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
        assert colonnes['ville'].default is not None
        assert colonnes['notifications_gel'].default is not None
        assert colonnes['notifications_canicule'].default is not None

    def test_repr(self):
        """Test de la représentation string."""
        config = ConfigMeteo(id=1, ville="Bordeaux")
        result = repr(config)
        assert "ConfigMeteo" in result
        assert "Bordeaux" in result
