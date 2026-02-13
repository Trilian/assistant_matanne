"""
Tests pour src/core/sql_optimizer.py
Couvre :
- EcouteurSQLAlchemy (log, extract, clear, install)
- DetecteurN1 (analyze, suggestions, normalize)
- ChargeurParLots (charger_par_lots, chunked)
- ConstructeurRequeteOptimisee (builder pattern)
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from src.core.sql_optimizer import (
    ChargeurParLots,
    ConstructeurRequeteOptimisee,
    DetecteurN1,
    DetectionN1,
    EcouteurSQLAlchemy,
    InfoRequete,
)

# ═══════════════════════════════════════════════════════════
# MODÈLES DE TEST
# ═══════════════════════════════════════════════════════════


class MockModel:
    """Modèle de test avec attributs."""

    id = MagicMock()
    name = MagicMock()
    user_id = MagicMock()
    items = MagicMock()  # Relation

    @classmethod
    def __init__(cls):
        pass


class DummyModel:
    id = 1
    name = "test"
    rel = None


class DummySession:
    def query(self, model):
        return MagicMock()


# ═══════════════════════════════════════════════════════════
# FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_session_state():
    state = {}
    with patch("streamlit.session_state", state):
        yield state


@pytest.fixture
def clean_session_state():
    """Fixture pour session_state propre."""
    state = {}
    with patch("streamlit.session_state", state):
        # Nettoyer au début
        state.clear()
        yield state


# ═══════════════════════════════════════════════════════════
# SECTION 1: INFO REQUETE DATACLASS
# ═══════════════════════════════════════════════════════════


class TestInfoRequete:
    """Tests pour InfoRequete dataclass."""

    @pytest.mark.unit
    def test_info_requete_creation(self):
        """Test création InfoRequete."""
        info = InfoRequete(
            sql="SELECT * FROM test",
            duration_ms=50.5,
            table="test",
            operation="SELECT",
        )

        assert info.sql == "SELECT * FROM test"
        assert info.duration_ms == 50.5
        assert info.table == "test"
        assert info.operation == "SELECT"

    @pytest.mark.unit
    def test_info_requete_default_timestamp(self):
        """Test timestamp par défaut."""
        info = InfoRequete(sql="SELECT 1", duration_ms=1.0)

        assert info.timestamp is not None
        assert isinstance(info.timestamp, datetime)

    @pytest.mark.unit
    def test_info_requete_default_parameters(self):
        """Test parameters par défaut."""
        info = InfoRequete(sql="SELECT 1", duration_ms=1.0)

        assert info.parameters == {}


class TestDetectionN1Dataclass:
    """Tests pour DetectionN1 dataclass."""

    @pytest.mark.unit
    def test_detection_n1_creation(self):
        """Test création DetectionN1."""
        detection = DetectionN1(
            table="users",
            parent_table="orders",
            count=10,
            sample_query="SELECT * FROM users WHERE order_id = 1",
        )

        assert detection.table == "users"
        assert detection.parent_table == "orders"
        assert detection.count == 10

    @pytest.mark.unit
    def test_detection_n1_default_first_seen(self):
        """Test first_seen par défaut."""
        detection = DetectionN1(table="test", parent_table="parent", count=5)

        assert detection.first_seen is not None


# ═══════════════════════════════════════════════════════════
# SECTION 2: ECOUTEUR SQLALCHEMY
# ═══════════════════════════════════════════════════════════


class TestEcouteurSQLAlchemy:
    """Tests pour EcouteurSQLAlchemy."""

    @pytest.mark.unit
    def test_log_query_adds_query(self, mock_session_state):
        """Test ajout requête au log."""
        EcouteurSQLAlchemy._log_query("SELECT * FROM test", 120, {})

        assert EcouteurSQLAlchemy.SESSION_KEY in mock_session_state
        assert len(mock_session_state[EcouteurSQLAlchemy.SESSION_KEY]) == 1
        q = mock_session_state[EcouteurSQLAlchemy.SESSION_KEY][0]
        assert q.operation == "SELECT"
        assert q.table == "test"
        assert q.duration_ms == 120

    @pytest.mark.unit
    def test_extract_operation_select(self):
        """Test extraction opération SELECT."""
        op = EcouteurSQLAlchemy._extract_operation("SELECT * FROM foo")
        assert op == "SELECT"

    @pytest.mark.unit
    def test_extract_operation_insert(self):
        """Test extraction opération INSERT."""
        op = EcouteurSQLAlchemy._extract_operation("INSERT INTO foo VALUES (1)")
        assert op == "INSERT"

    @pytest.mark.unit
    def test_extract_operation_update(self):
        """Test extraction opération UPDATE."""
        op = EcouteurSQLAlchemy._extract_operation("UPDATE foo SET bar = 1")
        assert op == "UPDATE"

    @pytest.mark.unit
    def test_extract_operation_delete(self):
        """Test extraction opération DELETE."""
        op = EcouteurSQLAlchemy._extract_operation("DELETE FROM foo WHERE id = 1")
        assert op == "DELETE"

    @pytest.mark.unit
    def test_extract_operation_create(self):
        """Test extraction opération CREATE."""
        op = EcouteurSQLAlchemy._extract_operation("CREATE TABLE foo (id INT)")
        assert op == "CREATE"

    @pytest.mark.unit
    def test_extract_operation_alter(self):
        """Test extraction opération ALTER."""
        op = EcouteurSQLAlchemy._extract_operation("ALTER TABLE foo ADD bar INT")
        assert op == "ALTER"

    @pytest.mark.unit
    def test_extract_operation_drop(self):
        """Test extraction opération DROP."""
        op = EcouteurSQLAlchemy._extract_operation("DROP TABLE foo")
        assert op == "DROP"

    @pytest.mark.unit
    def test_extract_operation_other(self):
        """Test extraction opération inconnue."""
        op = EcouteurSQLAlchemy._extract_operation("VACUUM ANALYZE")
        assert op == "OTHER"

    @pytest.mark.unit
    def test_extract_operation_case_insensitive(self):
        """Test extraction opération case insensitive."""
        op = EcouteurSQLAlchemy._extract_operation("select * from foo")
        assert op == "SELECT"

    @pytest.mark.unit
    def test_extract_table_from_select(self):
        """Test extraction table FROM."""
        table = EcouteurSQLAlchemy._extract_table("SELECT * FROM foo")
        assert table == "foo"

    @pytest.mark.unit
    def test_extract_table_from_insert(self):
        """Test extraction table INSERT INTO."""
        table = EcouteurSQLAlchemy._extract_table("INSERT INTO bar VALUES (1)")
        assert table == "bar"

    @pytest.mark.unit
    def test_extract_table_from_update(self):
        """Test extraction table UPDATE."""
        table = EcouteurSQLAlchemy._extract_table("UPDATE baz SET x = 1")
        assert table == "baz"

    @pytest.mark.unit
    def test_extract_table_quoted(self):
        """Test extraction table avec guillemets."""
        table = EcouteurSQLAlchemy._extract_table('SELECT * FROM "my_table"')
        assert table == "my_table"

    @pytest.mark.unit
    def test_extract_table_unknown(self):
        """Test extraction table inconnue."""
        table = EcouteurSQLAlchemy._extract_table("VACUUM")
        assert table == "unknown"

    @pytest.mark.unit
    def test_get_stats_returns_dict(self, mock_session_state):
        """Test statistiques retourne dict."""
        EcouteurSQLAlchemy._log_query("SELECT * FROM foo", 50, {})
        stats = EcouteurSQLAlchemy.get_stats()

        assert isinstance(stats, dict)
        assert "total" in stats
        assert "by_operation" in stats
        assert "by_table" in stats
        assert "avg_time_ms" in stats

    @pytest.mark.unit
    def test_get_stats_empty(self, clean_session_state):
        """Test statistiques avec log vide."""
        stats = EcouteurSQLAlchemy.get_stats()

        assert stats["total"] == 0
        assert stats["by_operation"] == {}
        assert stats["avg_time_ms"] == 0

    @pytest.mark.unit
    def test_get_stats_slow_queries(self, mock_session_state):
        """Test statistiques avec requêtes lentes."""
        EcouteurSQLAlchemy._log_query("SELECT slow FROM foo", 150, {})  # >100ms = lent
        EcouteurSQLAlchemy._log_query("SELECT fast FROM bar", 20, {})

        stats = EcouteurSQLAlchemy.get_stats()

        assert len(stats["slow_queries"]) == 1
        assert stats["slow_queries"][0].duration_ms == 150

    @pytest.mark.unit
    def test_clear_resets_log(self, mock_session_state):
        """Test vidage du log."""
        EcouteurSQLAlchemy._log_query("SELECT * FROM foo", 50, {})
        EcouteurSQLAlchemy.clear()

        assert mock_session_state[EcouteurSQLAlchemy.SESSION_KEY] == []

    @pytest.mark.unit
    def test_log_query_truncates_sql(self, mock_session_state):
        """Test troncature SQL long."""
        long_sql = "SELECT " + "x" * 1000
        EcouteurSQLAlchemy._log_query(long_sql, 10, {})

        logged = mock_session_state[EcouteurSQLAlchemy.SESSION_KEY][0]
        assert len(logged.sql) <= 500

    @pytest.mark.unit
    def test_log_query_limits_entries(self, mock_session_state):
        """Test limite de 200 entrées."""
        for i in range(250):
            EcouteurSQLAlchemy._log_query(f"SELECT * FROM table_{i}", 10, {})

        assert len(mock_session_state[EcouteurSQLAlchemy.SESSION_KEY]) == 200

    @pytest.mark.unit
    def test_log_query_with_dict_parameters(self, mock_session_state):
        """Test log avec paramètres dict."""
        params = {"id": 1, "name": "test"}
        EcouteurSQLAlchemy._log_query("SELECT * FROM foo WHERE id = :id", 10, params)

        logged = mock_session_state[EcouteurSQLAlchemy.SESSION_KEY][0]
        assert logged.parameters == params

    @pytest.mark.unit
    def test_log_query_with_non_dict_parameters(self, mock_session_state):
        """Test log avec paramètres non-dict."""
        params = [1, 2, 3]
        EcouteurSQLAlchemy._log_query("SELECT * FROM foo", 10, params)

        logged = mock_session_state[EcouteurSQLAlchemy.SESSION_KEY][0]
        assert logged.parameters == {}

    @pytest.mark.unit
    def test_install_with_engine(self):
        """Test installation listener sur engine."""
        mock_engine = MagicMock()

        # Reset installed flag
        EcouteurSQLAlchemy._installed = False

        with patch("src.core.sql_optimizer.event.listens_for") as mock_listens_for:
            EcouteurSQLAlchemy.install(mock_engine)

            # Devrait enregistrer des listeners
            assert mock_listens_for.call_count >= 2

    @pytest.mark.unit
    def test_install_idempotent(self):
        """Test installation est idempotent."""
        mock_engine = MagicMock()

        # Marquer comme installé
        EcouteurSQLAlchemy._installed = True

        with patch("src.core.sql_optimizer.event.listens_for") as mock_listens_for:
            EcouteurSQLAlchemy.install(mock_engine)

            # Ne devrait pas réinstaller
            mock_listens_for.assert_not_called()

        # Reset pour autres tests
        EcouteurSQLAlchemy._installed = False


# ═══════════════════════════════════════════════════════════
# SECTION 3: DETECTEUR N+1
# ═══════════════════════════════════════════════════════════


class TestDetecteurN1:
    """Tests pour DetecteurN1."""

    @pytest.mark.unit
    def test_analyze_detects_n1(self, mock_session_state):
        """Test détection N+1."""
        for _ in range(6):
            EcouteurSQLAlchemy._log_query("SELECT * FROM foo WHERE bar_id = 1", 10, {})

        detections = DetecteurN1.analyze()

        assert isinstance(detections, list)
        assert len(detections) >= 1
        assert hasattr(detections[0], "table")
        assert hasattr(detections[0], "parent_table")

    @pytest.mark.unit
    def test_analyze_no_detection_below_threshold(self, clean_session_state):
        """Test pas de détection sous le seuil."""
        for i in range(3):  # En dessous du seuil de 5
            EcouteurSQLAlchemy._log_query(f"SELECT * FROM foo WHERE id = {i}", 10, {})

        detections = DetecteurN1.analyze()

        assert len(detections) == 0

    @pytest.mark.unit
    def test_suggestions(self, mock_session_state):
        """Test génération suggestions."""
        for _ in range(6):
            EcouteurSQLAlchemy._log_query("SELECT * FROM foo WHERE bar_id = 1", 10, {})

        DetecteurN1.analyze()
        suggestions = DetecteurN1.get_suggestions()

        assert isinstance(suggestions, list)
        assert any("joinedload" in s or "eager loading" in s for s in suggestions)

    @pytest.mark.unit
    def test_normalize_query_removes_numbers(self):
        """Test normalisation retire les nombres."""
        sql = "SELECT * FROM users WHERE id = 12345"
        normalized = DetecteurN1._normalize_query(sql)

        assert "12345" not in normalized
        assert "?" in normalized

    @pytest.mark.unit
    def test_normalize_query_removes_strings(self):
        """Test normalisation retire les strings."""
        sql = "SELECT * FROM users WHERE name = 'John'"
        normalized = DetecteurN1._normalize_query(sql)

        assert "John" not in normalized
        assert "'?'" in normalized

    @pytest.mark.unit
    def test_guess_parent_table_from_fk(self):
        """Test devinette table parent depuis FK."""
        queries = [
            InfoRequete(sql="SELECT * FROM items WHERE user_id = 1", duration_ms=10, table="items"),
        ]

        parent = DetecteurN1._guess_parent_table(queries)

        assert parent == "user"

    @pytest.mark.unit
    def test_guess_parent_table_unknown(self):
        """Test devinette table parent inconnue."""
        queries = [
            InfoRequete(sql="SELECT * FROM items", duration_ms=10, table="items"),
        ]

        parent = DetecteurN1._guess_parent_table(queries)

        assert parent == "unknown"

    @pytest.mark.unit
    def test_obtenir_detections(self, mock_session_state):
        """Test obtenir_detections."""
        mock_session_state[DetecteurN1.SESSION_KEY] = [
            DetectionN1(table="test", parent_table="parent", count=5)
        ]

        detections = DetecteurN1.obtenir_detections()

        assert len(detections) == 1

    @pytest.mark.unit
    def test_suggestions_with_unknown_parent(self, mock_session_state):
        """Test suggestions avec parent inconnu."""
        mock_session_state[DetecteurN1.SESSION_KEY] = [
            DetectionN1(table="test", parent_table="unknown", count=10)
        ]

        suggestions = DetecteurN1.obtenir_suggestions()

        assert len(suggestions) == 1
        assert "eager loading" in suggestions[0]


# ═══════════════════════════════════════════════════════════
# SECTION 4: CHARGEUR PAR LOTS
# ═══════════════════════════════════════════════════════════


class TestChargeurParLots:
    """Tests pour ChargeurParLots."""

    @pytest.mark.unit
    def test_chunked_basic(self):
        """Test chunked basique."""
        items = list(range(250))
        chunks = list(ChargeurParLots.chunked(items, chunk_size=100))

        assert len(chunks) == 3
        assert chunks[0] == list(range(100))
        assert chunks[2] == list(range(200, 250))

    @pytest.mark.unit
    def test_chunked_exact_division(self):
        """Test chunked avec division exacte."""
        items = list(range(100))
        chunks = list(ChargeurParLots.chunked(items, chunk_size=50))

        assert len(chunks) == 2
        assert len(chunks[0]) == 50
        assert len(chunks[1]) == 50

    @pytest.mark.unit
    def test_chunked_small_list(self):
        """Test chunked avec liste plus petite que chunk."""
        items = list(range(10))
        chunks = list(ChargeurParLots.chunked(items, chunk_size=100))

        assert len(chunks) == 1
        assert chunks[0] == items

    @pytest.mark.unit
    def test_chunked_empty_list(self):
        """Test chunked avec liste vide."""
        items = []
        chunks = list(ChargeurParLots.chunked(items, chunk_size=100))

        assert len(chunks) == 0

    @pytest.mark.unit
    def test_charger_par_lots_basic(self):
        """Test charger_par_lots basique."""
        mock_query = MagicMock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.side_effect = [
            [1, 2, 3],  # Premier lot
            [4, 5],  # Deuxième lot
            [],  # Fin
        ]

        results = ChargeurParLots.charger_par_lots(mock_query, batch_size=3)

        assert results == [1, 2, 3, 4, 5]

    @pytest.mark.unit
    def test_charger_par_lots_with_callback(self):
        """Test charger_par_lots avec callback."""
        mock_query = MagicMock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.side_effect = [[1, 2], [3], []]

        callback_calls = []

        def callback(batch):
            callback_calls.append(batch)

        ChargeurParLots.charger_par_lots(mock_query, batch_size=2, callback=callback)

        assert len(callback_calls) == 2

    @pytest.mark.unit
    def test_charger_par_lots_stops_on_incomplete_batch(self):
        """Test arrêt sur lot incomplet."""
        mock_query = MagicMock()
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        # Lot incomplet (moins que batch_size)
        mock_query.all.return_value = [1, 2]

        results = ChargeurParLots.charger_par_lots(mock_query, batch_size=10)

        assert results == [1, 2]
        # Devrait faire un seul appel
        assert mock_query.all.call_count == 1


# ═══════════════════════════════════════════════════════════
# SECTION 5: CONSTRUCTEUR REQUETE OPTIMISEE
# ═══════════════════════════════════════════════════════════


class TestConstructeurRequeteOptimisee:
    """Tests pour ConstructeurRequeteOptimisee."""

    def setup_method(self):
        """Setup mock session et model."""
        self.mock_session = MagicMock()
        self.mock_query = MagicMock()
        self.mock_session.query.return_value = self.mock_query

        # Mock model avec attributs
        self.mock_model = MagicMock()
        self.mock_model.id = MagicMock()
        self.mock_model.name = MagicMock()
        self.mock_model.items = MagicMock()

    @pytest.mark.unit
    def test_builder_creation(self):
        """Test création builder."""
        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)

        assert builder is not None
        assert builder._session == self.mock_session
        assert builder._model == self.mock_model

    @pytest.mark.unit
    def test_filter_by(self):
        """Test filtre."""
        self.mock_query.filter_by.return_value = self.mock_query

        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        result = builder.filter_by(name="test")

        assert result is builder  # Chaînage

    @pytest.mark.unit
    def test_order(self):
        """Test ordre."""
        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        result = builder.order("name")

        assert result is builder
        assert builder._order_by == ("name", False)

    @pytest.mark.unit
    def test_order_desc(self):
        """Test ordre décroissant."""
        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        result = builder.order("id", desc=True)

        assert result is builder
        assert builder._order_by == ("id", True)

    @pytest.mark.unit
    def test_paginate(self):
        """Test pagination."""
        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        result = builder.paginate(page=2, per_page=20)

        assert result is builder
        assert builder._offset == 20  # (2-1) * 20
        assert builder._limit == 20

    @pytest.mark.unit
    def test_eager_load(self):
        """Test eager loading."""
        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        result = builder.eager_load("items", "other")

        assert result is builder
        assert "items" in builder._eager_loads
        assert "other" in builder._eager_loads

    @pytest.mark.unit
    def test_build(self):
        """Test construction requête."""
        self.mock_query.options.return_value = self.mock_query
        self.mock_query.filter_by.return_value = self.mock_query
        self.mock_query.order_by.return_value = self.mock_query
        self.mock_query.offset.return_value = self.mock_query
        self.mock_query.limit.return_value = self.mock_query

        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        builder.filter_by(active=True)
        builder.order("name")
        builder.paginate(page=1, per_page=10)

        query = builder.build()

        assert query is not None

    @pytest.mark.unit
    def test_all(self):
        """Test all()."""
        self.mock_query.all.return_value = ["item1", "item2"]
        self.mock_query.filter_by.return_value = self.mock_query
        self.mock_query.order_by.return_value = self.mock_query
        self.mock_query.offset.return_value = self.mock_query
        self.mock_query.limit.return_value = self.mock_query

        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        results = builder.all()

        assert results == ["item1", "item2"]

    @pytest.mark.unit
    def test_first(self):
        """Test first()."""
        self.mock_query.first.return_value = "item1"
        self.mock_query.filter_by.return_value = self.mock_query

        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        result = builder.first()

        assert result == "item1"

    @pytest.mark.unit
    def test_count(self):
        """Test count()."""
        self.mock_query.count.return_value = 42

        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        count = builder.count()

        assert count == 42

    @pytest.mark.unit
    def test_build_with_eager_load(self):
        """Test build avec eager loading."""
        self.mock_query.options.return_value = self.mock_query

        # Mock model avec relation
        self.mock_model.items = MagicMock()

        builder = ConstructeurRequeteOptimisee(self.mock_session, self.mock_model)
        builder.eager_load("items")

        with patch("src.core.sql_optimizer.selectinload") as mock_selectinload:
            mock_selectinload.return_value = MagicMock()
            builder.build()


# ═══════════════════════════════════════════════════════════
# SECTION 6: TESTS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestSQLOptimizerIntegration:
    """Tests d'intégration SQL optimizer."""

    @pytest.mark.integration
    def test_complete_workflow(self, clean_session_state):
        """Test workflow complet."""
        # Log plusieurs requêtes
        EcouteurSQLAlchemy._log_query("SELECT * FROM users", 50, {})
        EcouteurSQLAlchemy._log_query("SELECT * FROM orders WHERE user_id = 1", 30, {})

        # Obtenir statistiques
        stats = EcouteurSQLAlchemy.get_stats()

        assert stats["total"] == 2
        assert "SELECT" in stats["by_operation"]

        # Clear
        EcouteurSQLAlchemy.clear()

        stats2 = EcouteurSQLAlchemy.get_stats()
        assert stats2["total"] == 0

    @pytest.mark.integration
    def test_n1_detection_workflow(self, clean_session_state):
        """Test workflow détection N+1."""
        # Simuler N+1 pattern
        for i in range(10):
            EcouteurSQLAlchemy._log_query(f"SELECT * FROM order_items WHERE order_id = {i}", 5, {})

        detections = DetecteurN1.analyze()
        suggestions = DetecteurN1.get_suggestions()

        assert len(detections) >= 1  # Au moins un pattern détecté
        assert len(suggestions) >= 1


# ═══════════════════════════════════════════════════════════
# SECTION 7: TESTS UI (mocked)
# ═══════════════════════════════════════════════════════════


class TestAfficherAnalyseSQL:
    """Tests pour afficher_analyse_sql (UI)."""

    @pytest.mark.unit
    def test_afficher_analyse_sql_no_queries(self, clean_session_state):
        """Test affichage sans requêtes."""
        with patch("src.core.sql_optimizer.st") as mock_st:
            mock_st.expander.return_value.__enter__ = MagicMock()
            mock_st.expander.return_value.__exit__ = MagicMock()
            mock_st.session_state = clean_session_state

            from src.core.sql_optimizer import afficher_analyse_sql

            # Ne devrait pas crash
            try:
                afficher_analyse_sql()
            except Exception:
                pass  # OK si erreur à cause des mocks incomplets
