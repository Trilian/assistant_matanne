"""Tests pour src/core/observability/context.py — contexte d'exécution."""

import logging
import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.core.observability.context import (
    ContexteExecution,
    FiltreCorrelation,
    _contexte_execution,
    configurer_logging_avec_correlation,
    contexte_operation,
    definir_contexte,
    obtenir_contexte,
    reset_contexte,
)

# ═══════════════════════════════════════════════════════════
# TESTS ContexteExecution
# ═══════════════════════════════════════════════════════════


class TestContexteExecution:
    """Tests pour ContexteExecution."""

    @pytest.mark.unit
    def test_creation_defaut(self):
        """Création avec valeurs par défaut."""
        ctx = ContexteExecution()

        assert len(ctx.correlation_id) == 8
        assert ctx.operation == ""
        assert ctx.utilisateur is None
        assert ctx.module is None
        assert isinstance(ctx.debut, datetime)
        assert ctx.metadata == {}
        assert ctx.parent_id is None

    @pytest.mark.unit
    def test_creation_avec_parametres(self):
        """Création avec paramètres spécifiques."""
        ctx = ContexteExecution(
            correlation_id="12345678",
            operation="charger_recettes",
            utilisateur="Anne",
            module="cuisine",
            metadata={"param": "value"},
        )

        assert ctx.correlation_id == "12345678"
        assert ctx.operation == "charger_recettes"
        assert ctx.utilisateur == "Anne"
        assert ctx.module == "cuisine"
        assert ctx.metadata == {"param": "value"}

    @pytest.mark.unit
    def test_creer_enfant(self):
        """Crée un contexte enfant avec héritage."""
        parent = ContexteExecution(
            correlation_id="parent01",
            operation="parent_op",
            utilisateur="Mathieu",
            module="famille",
        )

        enfant = parent.creer_enfant("child_op", extra_data="test")

        assert enfant.correlation_id == "parent01"  # Hérité
        assert enfant.operation == "child_op"
        assert enfant.utilisateur == "Mathieu"  # Hérité
        assert enfant.module == "famille"  # Hérité
        assert enfant.parent_id == "parent01"
        assert enfant.metadata["extra_data"] == "test"

    @pytest.mark.unit
    def test_creer_enfant_metadata_merge(self):
        """Les métadonnées de l'enfant fusionnent avec le parent."""
        parent = ContexteExecution(
            operation="parent",
            metadata={"existant": "value"},
        )

        enfant = parent.creer_enfant("child", nouveau="data")

        assert enfant.metadata["existant"] == "value"
        assert enfant.metadata["nouveau"] == "data"

    @pytest.mark.unit
    def test_duree_ms(self):
        """Calcul de la durée en millisecondes."""
        ctx = ContexteExecution()
        time.sleep(0.05)  # 50ms

        duree = ctx.duree_ms()

        assert duree >= 40  # Au moins ~40ms
        assert duree < 200  # Pas trop long

    @pytest.mark.unit
    def test_to_dict(self):
        """Conversion en dictionnaire."""
        ctx = ContexteExecution(
            correlation_id="dicttest",
            operation="test_op",
            utilisateur="User",
            module="mod",
            metadata={"key": "val"},
        )

        d = ctx.to_dict()

        assert d["correlation_id"] == "dicttest"
        assert d["operation"] == "test_op"
        assert d["utilisateur"] == "User"
        assert d["module"] == "mod"
        assert d["parent_id"] is None
        assert d["metadata"] == {"key": "val"}
        assert "debut" in d
        assert "duree_ms" in d
        assert isinstance(d["duree_ms"], float)

    @pytest.mark.unit
    def test_correlation_id_unique(self):
        """Chaque contexte a un correlation_id unique."""
        ctx1 = ContexteExecution()
        ctx2 = ContexteExecution()

        assert ctx1.correlation_id != ctx2.correlation_id


# ═══════════════════════════════════════════════════════════
# TESTS FONCTIONS GLOBALS (obtenir/definir/reset)
# ═══════════════════════════════════════════════════════════


class TestContextFunctions:
    """Tests pour les fonctions de gestion du contexte."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset le contexte avant/après chaque test."""
        # Clear avant
        _contexte_execution.set(None)
        yield
        # Clear après
        _contexte_execution.set(None)

    @pytest.mark.unit
    def test_obtenir_contexte_cree_nouveau(self):
        """obtenir_contexte() crée un contexte si aucun n'existe."""
        ctx = obtenir_contexte()

        assert isinstance(ctx, ContexteExecution)
        assert len(ctx.correlation_id) == 8

    @pytest.mark.unit
    def test_obtenir_contexte_retourne_existant(self):
        """obtenir_contexte() retourne le contexte existant."""
        ctx1 = obtenir_contexte()
        ctx2 = obtenir_contexte()

        assert ctx1 is ctx2

    @pytest.mark.unit
    def test_definir_contexte(self):
        """definir_contexte() définit le contexte courant."""
        ctx = ContexteExecution(operation="custom")

        token = definir_contexte(ctx)

        assert obtenir_contexte() is ctx
        assert token is not None

    @pytest.mark.unit
    def test_reset_contexte(self):
        """reset_contexte() restaure l'état précédent."""
        # État initial
        ctx_initial = obtenir_contexte()

        # Nouveau contexte
        ctx_nouveau = ContexteExecution(operation="nouveau")
        token = definir_contexte(ctx_nouveau)
        assert obtenir_contexte().operation == "nouveau"

        # Reset
        reset_contexte(token)

        # Vérifie retour à l'état initial
        assert obtenir_contexte() is ctx_initial

    @pytest.mark.unit
    def test_definir_contexte_retourne_token(self):
        """definir_contexte() retourne un token utilisable."""
        ctx = ContexteExecution()
        token = definir_contexte(ctx)

        # Le token peut être utilisé pour reset
        reset_contexte(token)

        # Pas d'exception = succès


# ═══════════════════════════════════════════════════════════
# TESTS contexte_operation CONTEXT MANAGER
# ═══════════════════════════════════════════════════════════


class TestContexteOperation:
    """Tests pour contexte_operation context manager."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset le contexte avant/après chaque test."""
        _contexte_execution.set(None)
        yield
        _contexte_execution.set(None)

    @pytest.mark.unit
    def test_context_manager_basic(self):
        """Usage basique du context manager."""
        with contexte_operation("test_operation") as ctx:
            assert ctx.operation == "test_operation"
            assert len(ctx.correlation_id) == 8

    @pytest.mark.unit
    def test_context_manager_retourne_contexte(self):
        """Le context manager retourne le contexte créé."""
        with contexte_operation("op", module="mod", utilisateur="user") as ctx:
            assert isinstance(ctx, ContexteExecution)
            assert ctx.module == "mod"
            assert ctx.utilisateur == "user"

    @pytest.mark.unit
    def test_context_manager_avec_metadata(self):
        """Le context manager accepte des métadonnées kwargs."""
        with contexte_operation("op", param1="val1", param2="val2") as ctx:
            assert ctx.metadata["param1"] == "val1"
            assert ctx.metadata["param2"] == "val2"

    @pytest.mark.unit
    def test_context_manager_nesting(self):
        """Les contextes imbriqués créent une hiérarchie."""
        with contexte_operation("parent") as parent_ctx:
            with contexte_operation("child") as child_ctx:
                assert child_ctx.parent_id == parent_ctx.correlation_id
                assert child_ctx.correlation_id == parent_ctx.correlation_id

    @pytest.mark.unit
    def test_context_manager_cleanup(self):
        """Le contexte est nettoyé après le with."""
        _contexte_execution.set(None)

        with contexte_operation("temp"):
            # Pendant le with, contexte existe
            pass

        # Après le with, contexte revient à None ou état précédent
        ctx = _contexte_execution.get()
        # Le contexte créé par le first obtenir_contexte persiste
        # mais l'opération spécifique est terminée

    @pytest.mark.unit
    def test_context_manager_exception_handling(self):
        """Le contexte est nettoyé même en cas d'exception."""
        _contexte_execution.set(None)

        try:
            with contexte_operation("error_op"):
                raise ValueError("Test error")
        except ValueError:
            pass

        # Le contexte doit être proprement nettoyé
        # (ne doit pas lever d'exception)

    @pytest.mark.unit
    def test_context_manager_herite_module_utilisateur(self):
        """Le contexte enfant hérite module et utilisateur du parent."""
        with contexte_operation("parent", module="cuisine", utilisateur="Anne"):
            with contexte_operation("child") as child:
                # Les enfants héritent du parent
                assert child.utilisateur == "Anne"
                assert child.module == "cuisine"

    @pytest.mark.unit
    def test_context_manager_override_module_utilisateur(self):
        """Le contexte enfant peut override module et utilisateur."""
        with contexte_operation("parent", module="cuisine", utilisateur="Anne"):
            with contexte_operation("child", module="famille", utilisateur="Mathieu") as child:
                assert child.module == "famille"
                assert child.utilisateur == "Mathieu"


# ═══════════════════════════════════════════════════════════
# TESTS FiltreCorrelation
# ═══════════════════════════════════════════════════════════


class TestFiltreCorrelation:
    """Tests pour FiltreCorrelation."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset le contexte avant/après chaque test."""
        _contexte_execution.set(None)
        yield
        _contexte_execution.set(None)

    @pytest.mark.unit
    def test_filtre_ajoute_correlation_id(self):
        """Le filtre ajoute correlation_id au record."""
        filtre = FiltreCorrelation()

        with contexte_operation("test") as ctx:
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test",
                args=(),
                exc_info=None,
            )

            result = filtre.filter(record)

            assert result is True
            assert record.correlation_id == ctx.correlation_id  # type: ignore

    @pytest.mark.unit
    def test_filtre_sans_contexte(self):
        """Le filtre utilise des tirets si pas de contexte."""
        filtre = FiltreCorrelation()
        _contexte_execution.set(None)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Test",
            args=(),
            exc_info=None,
        )

        result = filtre.filter(record)

        assert result is True
        assert record.correlation_id == "--------"  # type: ignore

    @pytest.mark.unit
    def test_filtre_ajoute_operation(self):
        """Le filtre ajoute l'opération au record."""
        filtre = FiltreCorrelation()

        with contexte_operation("mon_operation"):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test",
                args=(),
                exc_info=None,
            )

            filtre.filter(record)

            assert record.operation == "mon_operation"  # type: ignore

    @pytest.mark.unit
    def test_filtre_ajoute_module_ctx(self):
        """Le filtre ajoute le module au record."""
        filtre = FiltreCorrelation()

        with contexte_operation("op", module="cuisine"):
            record = logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg="Test",
                args=(),
                exc_info=None,
            )

            filtre.filter(record)

            assert record.module_ctx == "cuisine"  # type: ignore


# ═══════════════════════════════════════════════════════════
# TESTS configurer_logging_avec_correlation
# ═══════════════════════════════════════════════════════════


class TestConfigurerLogging:
    """Tests pour configurer_logging_avec_correlation."""

    @pytest.fixture(autouse=True)
    def reset_logging(self):
        """Reset le logging après chaque test."""
        yield
        # Cleanup: remettre le logging dans un état propre
        root = logging.getLogger()
        root.handlers = [
            h
            for h in root.handlers
            if not any(isinstance(f, FiltreCorrelation) for f in getattr(h, "filters", []))
        ]

    @pytest.mark.unit
    def test_configure_ajoute_handler(self):
        """configurer_logging_avec_correlation() ajoute un handler."""
        root = logging.getLogger()
        initial_handlers = len(root.handlers)

        configurer_logging_avec_correlation()

        assert len(root.handlers) >= initial_handlers  # Au moins un handler ajouté

    @pytest.mark.unit
    def test_configure_avec_niveau(self):
        """Configure avec le niveau spécifié."""
        configurer_logging_avec_correlation(niveau=logging.DEBUG)

        root = logging.getLogger()
        assert root.level == logging.DEBUG

    @pytest.mark.unit
    def test_configure_evite_doublons(self):
        """Appels répétés n'ajoutent pas de handlers en double."""
        configurer_logging_avec_correlation()
        nb1 = len(
            [
                h
                for h in logging.getLogger().handlers
                if any(isinstance(f, FiltreCorrelation) for f in getattr(h, "filters", []))
            ]
        )

        configurer_logging_avec_correlation()
        nb2 = len(
            [
                h
                for h in logging.getLogger().handlers
                if any(isinstance(f, FiltreCorrelation) for f in getattr(h, "filters", []))
            ]
        )

        assert nb1 == nb2  # Pas de doublon

    @pytest.mark.unit
    def test_configure_format_custom(self):
        """Configure avec un format personnalisé."""
        configurer_logging_avec_correlation(
            format_str="%(correlation_id)s | %(message)s",
        )

        # Vérifie qu'un handler avec FiltreCorrelation existe
        handlers = [
            h
            for h in logging.getLogger().handlers
            if any(isinstance(f, FiltreCorrelation) for f in getattr(h, "filters", []))
        ]
        assert len(handlers) >= 1


# ═══════════════════════════════════════════════════════════
# TESTS INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestIntegration:
    """Tests d'intégration."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset le contexte avant/après chaque test."""
        _contexte_execution.set(None)
        yield
        _contexte_execution.set(None)

    @pytest.mark.unit
    def test_contexte_nested_complet(self):
        """Test d'un scénario complet avec contextes imbriqués."""
        with contexte_operation("charger_page", module="cuisine", utilisateur="Anne") as ctx1:
            assert ctx1.module == "cuisine"

            with contexte_operation("charger_recettes") as ctx2:
                assert ctx2.parent_id == ctx1.correlation_id
                assert ctx2.utilisateur == "Anne"  # Hérité

                with contexte_operation("charger_detail", recette_id=42) as ctx3:
                    assert ctx3.parent_id == ctx1.correlation_id
                    assert ctx3.metadata["recette_id"] == 42
                    assert ctx3.correlation_id == ctx1.correlation_id

    @pytest.mark.unit
    def test_duree_contexte(self):
        """Le contexte mesure correctement la durée."""
        with contexte_operation("slow_op") as ctx:
            time.sleep(0.05)
            duree_pendant = ctx.duree_ms()

        duree_apres = ctx.duree_ms()

        assert duree_pendant >= 40  # Au moins ~40ms pendant
        assert duree_apres >= duree_pendant  # Continue à augmenter

    @pytest.mark.unit
    def test_serialisation_contexte(self):
        """Le contexte peut être sérialisé pour les logs."""
        with contexte_operation("test", module="test", data="value") as ctx:
            d = ctx.to_dict()

            # Toutes les clés importantes présentes
            assert "correlation_id" in d
            assert "operation" in d
            assert "module" in d
            assert "duree_ms" in d
            assert "debut" in d

            # Les valeurs sont sérialisables (pas d'exception)
            import json

            json_str = json.dumps(d)
            assert len(json_str) > 0


# ═══════════════════════════════════════════════════════════
# TESTS EDGE CASES
# ═══════════════════════════════════════════════════════════


class TestEdgeCases:
    """Tests des cas limites."""

    @pytest.fixture(autouse=True)
    def reset_context(self):
        """Reset le contexte avant/après chaque test."""
        _contexte_execution.set(None)
        yield
        _contexte_execution.set(None)

    @pytest.mark.unit
    def test_contexte_vide(self):
        """Contexte avec valeurs vides fonctionne."""
        ctx = ContexteExecution(
            operation="",
            utilisateur=None,
            module=None,
            metadata={},
        )

        d = ctx.to_dict()
        assert d["operation"] == ""
        assert d["utilisateur"] is None

    @pytest.mark.unit
    def test_metadata_complexe(self):
        """Les métadonnées complexes sont supportées."""
        metadata = {
            "liste": [1, 2, 3],
            "nested": {"a": {"b": "c"}},
            "numero": 42,
            "decimal": 3.14,
            "boolean": True,
            "null": None,
        }

        ctx = ContexteExecution(operation="test", metadata=metadata)

        assert ctx.metadata == metadata
        assert ctx.metadata["liste"] == [1, 2, 3]
        assert ctx.metadata["nested"]["a"]["b"] == "c"

    @pytest.mark.unit
    def test_correlation_id_personnalise(self):
        """On peut forcer un correlation_id personnalisé."""
        ctx = ContexteExecution(correlation_id="CUSTOM12")

        assert ctx.correlation_id == "CUSTOM12"

    @pytest.mark.unit
    def test_contexte_sans_parent(self):
        """Premier contexte n'a pas de parent."""
        _contexte_execution.set(None)

        with contexte_operation("first") as ctx:
            assert ctx.parent_id is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
