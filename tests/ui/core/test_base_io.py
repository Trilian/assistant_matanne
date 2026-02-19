"""
Tests complets pour src/ui/core/base_io.py
Couverture cible: >80%
"""

from unittest.mock import MagicMock, patch

# ═══════════════════════════════════════════════════════════
# CONFIGURATION IO
# ═══════════════════════════════════════════════════════════


class TestConfigurationIO:
    """Tests pour ConfigurationIO."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.core.base_io import ConfigurationIO

        assert ConfigurationIO is not None

    def test_creation_simple(self):
        """Test création basique."""
        from src.ui.core.base_io import ConfigurationIO

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        assert config.field_mapping == {"nom": "Nom"}
        assert config.required_fields == ["nom"]
        assert config.transformers is None

    def test_creation_with_transformers(self):
        """Test création avec transformers."""
        from src.ui.core.base_io import ConfigurationIO

        transformers = {"quantite": int}

        config = ConfigurationIO(
            field_mapping={"nom": "Nom", "quantite": "Quantité"},
            required_fields=["nom"],
            transformers=transformers,
        )

        assert config.transformers == transformers


# ═══════════════════════════════════════════════════════════
# SERVICE IO BASE - EXPORT
# ═══════════════════════════════════════════════════════════


class TestServiceIOBaseExport:
    """Tests pour ServiceIOBase export."""

    def test_import(self):
        """Test import réussi."""
        from src.ui.core.base_io import ServiceIOBase

        assert ServiceIOBase is not None

    def test_creation(self):
        """Test création."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        service = ServiceIOBase(config)

        assert service.config == config
        assert service.io_service is not None

    @patch("src.ui.core.base_io.IOService")
    def test_to_csv(self, mock_io_cls):
        """Test export CSV."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.to_csv.return_value = "nom\nTest"
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        service = ServiceIOBase(config)
        items = [{"nom": "Test"}]

        _result = service.to_csv(items)

        mock_io.to_csv.assert_called_once_with(items=items, field_mapping={"nom": "Nom"})

    @patch("src.ui.core.base_io.IOService")
    def test_to_json(self, mock_io_cls):
        """Test export JSON."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.to_json.return_value = '[{"nom": "Test"}]'
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        service = ServiceIOBase(config)
        items = [{"nom": "Test"}]

        _result = service.to_json(items, indent=4)

        mock_io.to_json.assert_called_once_with(items, indent=4)


# ═══════════════════════════════════════════════════════════
# SERVICE IO BASE - IMPORT
# ═══════════════════════════════════════════════════════════


class TestServiceIOBaseImport:
    """Tests pour ServiceIOBase import."""

    @patch("src.ui.core.base_io.IOService")
    def test_from_csv(self, mock_io_cls):
        """Test import CSV."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.from_csv.return_value = ([{"nom": "Test"}], [])
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        service = ServiceIOBase(config)

        items, errors = service.from_csv("nom\nTest")

        assert items == [{"nom": "Test"}]
        assert errors == []

    @patch("src.ui.core.base_io.IOService")
    def test_from_csv_with_transformers(self, mock_io_cls):
        """Test import CSV avec transformers."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.from_csv.return_value = ([{"nom": "Test", "quantite": "10"}], [])
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(
            field_mapping={"nom": "Nom", "quantite": "Quantité"},
            required_fields=["nom"],
            transformers={"quantite": int},
        )

        service = ServiceIOBase(config)

        items, errors = service.from_csv("nom,quantite\nTest,10")

        assert items[0]["quantite"] == 10  # Converti en int

    @patch("src.ui.core.base_io.IOService")
    def test_from_json(self, mock_io_cls):
        """Test import JSON."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.from_json.return_value = ([{"nom": "Test"}], [])
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        service = ServiceIOBase(config)

        items, errors = service.from_json('[{"nom": "Test"}]')

        assert items == [{"nom": "Test"}]
        assert errors == []

    @patch("src.ui.core.base_io.IOService")
    def test_from_json_with_transformers(self, mock_io_cls):
        """Test import JSON avec transformers."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.from_json.return_value = ([{"nom": "test", "upper": "hello"}], [])
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(
            field_mapping={"nom": "Nom"}, required_fields=["nom"], transformers={"upper": str.upper}
        )

        service = ServiceIOBase(config)

        items, errors = service.from_json('[{"nom": "test", "upper": "hello"}]')

        assert items[0]["upper"] == "HELLO"


# ═══════════════════════════════════════════════════════════
# TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════


class TestApplyTransformers:
    """Tests pour _apply_transformers."""

    @patch("src.ui.core.base_io.IOService")
    def test_apply_transformers_none(self, mock_io_cls):
        """Test sans transformers."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io_cls.return_value = MagicMock()

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=[])

        service = ServiceIOBase(config)

        items = [{"nom": "Test"}]
        result = service._apply_transformers(items)

        assert result == items

    @patch("src.ui.core.base_io.IOService")
    def test_apply_transformers_multiple(self, mock_io_cls):
        """Test avec plusieurs transformers."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io_cls.return_value = MagicMock()

        config = ConfigurationIO(
            field_mapping={"nom": "Nom", "qty": "Quantité"},
            required_fields=[],
            transformers={"nom": str.upper, "qty": int},
        )

        service = ServiceIOBase(config)

        items = [{"nom": "test", "qty": "42"}]
        result = service._apply_transformers(items)

        assert result[0]["nom"] == "TEST"
        assert result[0]["qty"] == 42

    @patch("src.ui.core.base_io.IOService")
    def test_apply_transformers_error_handling(self, mock_io_cls):
        """Test erreur transformation."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io_cls.return_value = MagicMock()

        def bad_transformer(value):
            raise ValueError("Erreur!")

        config = ConfigurationIO(
            field_mapping={"nom": "Nom"}, required_fields=[], transformers={"nom": bad_transformer}
        )

        service = ServiceIOBase(config)

        items = [{"nom": "test"}]
        result = service._apply_transformers(items)

        # L'erreur est loggée mais l'item reste intact
        assert result[0]["nom"] == "test"

    @patch("src.ui.core.base_io.IOService")
    def test_apply_transformers_missing_field(self, mock_io_cls):
        """Test transformer sur champ absent."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io_cls.return_value = MagicMock()

        config = ConfigurationIO(
            field_mapping={"nom": "Nom"},
            required_fields=[],
            transformers={"absent": str.upper},  # Champ inexistant
        )

        service = ServiceIOBase(config)

        items = [{"nom": "test"}]
        result = service._apply_transformers(items)

        # Pas d'erreur, item inchangé
        assert result == [{"nom": "test"}]


# ═══════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════


class TestFactory:
    """Tests pour factories."""

    @patch("src.ui.core.base_io.IOService")
    def test_creer_service_io(self, mock_io_cls):
        """Test creer_service_io."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase, creer_service_io

        mock_io_cls.return_value = MagicMock()

        config = ConfigurationIO(field_mapping={"nom": "Nom"}, required_fields=["nom"])

        service = creer_service_io(config)

        assert isinstance(service, ServiceIOBase)


# ═══════════════════════════════════════════════════════════
# INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration."""

    def test_exports_from_core(self):
        """Test exports depuis core."""
        from src.ui.core import (
            ConfigurationIO,
            ServiceIOBase,
            creer_service_io,
        )

        assert ConfigurationIO is not None
        assert ServiceIOBase is not None
        assert creer_service_io is not None

    def test_exports_from_ui(self):
        """Test exports depuis ui."""
        from src.ui import (
            ConfigurationIO,
            ServiceIOBase,
            creer_service_io,
        )

        assert ConfigurationIO is not None
        assert ServiceIOBase is not None
        assert creer_service_io is not None

    @patch("src.ui.core.base_io.IOService")
    def test_full_workflow(self, mock_io_cls):
        """Test workflow complet."""
        from src.ui.core.base_io import ConfigurationIO, ServiceIOBase

        mock_io = MagicMock()
        mock_io.to_csv.return_value = "Nom,Quantité\nPommes,10"
        mock_io.from_csv.return_value = ([{"nom": "Pommes", "quantite": "10"}], [])
        mock_io_cls.return_value = mock_io

        config = ConfigurationIO(
            field_mapping={"nom": "Nom", "quantite": "Quantité"},
            required_fields=["nom"],
            transformers={"quantite": int},
        )

        service = ServiceIOBase(config)

        # Export
        items = [{"nom": "Pommes", "quantite": 10}]
        csv = service.to_csv(items)

        # Import
        imported, errors = service.from_csv(csv)

        assert imported[0]["quantite"] == 10
        assert errors == []
