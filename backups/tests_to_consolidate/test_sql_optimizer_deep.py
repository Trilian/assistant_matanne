"""
Tests pour sql_optimizer.py - amÃ©lioration de la couverture

Cible:
- InfoRequete dataclass
- DetectionN1 dataclass
- EcouteurSQLAlchemy class
- DetecteurN1 class
"""

from unittest.mock import patch

import pytest


class TestQueryInfo:
    """Tests pour InfoRequete dataclass."""

    def test_default_values(self):
        """Valeurs par dÃ©faut correctes."""
        from src.core.sql_optimizer import InfoRequete

        info = InfoRequete(sql="SELECT * FROM users", duration_ms=50.0)

        assert info.sql == "SELECT * FROM users"
        assert info.duration_ms == 50.0
        assert info.table == ""
        assert info.operation == ""
        assert info.parameters == {}
        assert info.timestamp is not None

    def test_with_all_fields(self):
        """CrÃ©ation avec tous les champs."""
        from src.core.sql_optimizer import InfoRequete

        info = InfoRequete(
            sql="SELECT * FROM users WHERE id = :id",
            duration_ms=25.5,
            table="users",
            operation="SELECT",
            parameters={"id": 1},
        )

        assert info.table == "users"
        assert info.operation == "SELECT"
        assert info.parameters == {"id": 1}


class TestN1Detection:
    """Tests pour DetectionN1 dataclass."""

    def test_default_values(self):
        """Valeurs par dÃ©faut correctes."""
        from src.core.sql_optimizer import DetectionN1

        detection = DetectionN1(
            table="ingredients",
            parent_table="recettes",
            count=15,
        )

        assert detection.table == "ingredients"
        assert detection.parent_table == "recettes"
        assert detection.count == 15
        assert detection.sample_query == ""
        assert detection.first_seen is not None


class TestSQLAlchemyListener:
    """Tests pour EcouteurSQLAlchemy."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.sql_optimizer.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_extract_operation_select(self, mock_streamlit):
        """Extrait SELECT correctement."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_operation("SELECT * FROM users") == "SELECT"
        assert EcouteurSQLAlchemy._extract_operation("  select id FROM users") == "SELECT"

    def test_extract_operation_insert(self, mock_streamlit):
        """Extrait INSERT correctement."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_operation("INSERT INTO users VALUES (1)") == "INSERT"

    def test_extract_operation_update(self, mock_streamlit):
        """Extrait UPDATE correctement."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_operation("UPDATE users SET name='x'") == "UPDATE"

    def test_extract_operation_delete(self, mock_streamlit):
        """Extrait DELETE correctement."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_operation("DELETE FROM users WHERE id=1") == "DELETE"

    def test_extract_operation_other(self, mock_streamlit):
        """Retourne OTHER pour opÃ©rations inconnues."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_operation("EXPLAIN SELECT * FROM users") == "OTHER"

    def test_extract_table_from_select(self, mock_streamlit):
        """Extrait table depuis SELECT."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_table("SELECT * FROM users WHERE id=1") == "users"
        assert EcouteurSQLAlchemy._extract_table('SELECT * FROM "recettes"') == "recettes"

    def test_extract_table_from_insert(self, mock_streamlit):
        """Extrait table depuis INSERT."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert (
            EcouteurSQLAlchemy._extract_table("INSERT INTO ingredients (name) VALUES ('x')")
            == "ingredients"
        )

    def test_extract_table_from_update(self, mock_streamlit):
        """Extrait table depuis UPDATE."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_table("UPDATE inventaire SET qty=5") == "inventaire"

    def test_extract_table_unknown(self, mock_streamlit):
        """Retourne unknown si pas de table trouvÃ©e."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        assert EcouteurSQLAlchemy._extract_table("SET timezone='UTC'") == "unknown"

    def test_get_queries_empty(self, mock_streamlit):
        """get_queries retourne liste vide si pas de requÃªtes."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        queries = EcouteurSQLAlchemy.get_queries()
        assert queries == []

    def test_get_queries_with_data(self, mock_streamlit):
        """get_queries retourne les requÃªtes loggÃ©es."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy, InfoRequete

        mock_streamlit.session_state["_sqlalchemy_query_log"] = [
            InfoRequete(sql="SELECT 1", duration_ms=1.0),
            InfoRequete(sql="SELECT 2", duration_ms=2.0),
        ]

        queries = EcouteurSQLAlchemy.get_queries()
        assert len(queries) == 2

    def test_get_stats_empty(self, mock_streamlit):
        """get_stats pour liste vide."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy

        stats = EcouteurSQLAlchemy.get_stats()

        assert stats["total"] == 0
        assert stats["by_operation"] == {}
        assert stats["avg_time_ms"] == 0

    def test_get_stats_with_queries(self, mock_streamlit):
        """get_stats calcule les statistiques."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy, InfoRequete

        mock_streamlit.session_state["_sqlalchemy_query_log"] = [
            InfoRequete(sql="SELECT 1", duration_ms=10.0, operation="SELECT", table="users"),
            InfoRequete(sql="SELECT 2", duration_ms=20.0, operation="SELECT", table="users"),
            InfoRequete(sql="INSERT 1", duration_ms=5.0, operation="INSERT", table="logs"),
        ]

        stats = EcouteurSQLAlchemy.get_stats()

        assert stats["total"] == 3
        assert stats["by_operation"]["SELECT"] == 2
        assert stats["by_operation"]["INSERT"] == 1
        assert stats["avg_time_ms"] > 0

    def test_get_stats_slow_queries(self, mock_streamlit):
        """get_stats identifie les requÃªtes lentes."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy, InfoRequete

        mock_streamlit.session_state["_sqlalchemy_query_log"] = [
            InfoRequete(sql="FAST", duration_ms=10.0),
            InfoRequete(sql="SLOW1", duration_ms=150.0),
            InfoRequete(sql="SLOW2", duration_ms=200.0),
        ]

        stats = EcouteurSQLAlchemy.get_stats()

        assert len(stats["slow_queries"]) == 2

    def test_clear(self, mock_streamlit):
        """clear vide le log."""
        from src.core.sql_optimizer import EcouteurSQLAlchemy, InfoRequete

        mock_streamlit.session_state["_sqlalchemy_query_log"] = [
            InfoRequete(sql="test", duration_ms=1.0)
        ]

        EcouteurSQLAlchemy.clear()

        assert mock_streamlit.session_state["_sqlalchemy_query_log"] == []


class TestN1Detector:
    """Tests pour DetecteurN1."""

    @pytest.fixture(autouse=True)
    def mock_streamlit(self):
        """Mock streamlit session_state."""
        with patch("src.core.sql_optimizer.st") as mock_st:
            mock_st.session_state = {}
            yield mock_st

    def test_normalize_query(self, mock_streamlit):
        """Normalise les requÃªtes pour comparaison."""
        from src.core.sql_optimizer import DetecteurN1

        q1 = "SELECT * FROM users WHERE id = 123"
        q2 = "SELECT * FROM users WHERE name = 'John'"

        n1 = DetecteurN1._normalize_query(q1)
        n2 = DetecteurN1._normalize_query(q2)

        assert "123" not in n1
        assert "?" in n1
        assert "John" not in n2

    def test_guess_parent_table(self, mock_streamlit):
        """Devine la table parente depuis FK."""
        from src.core.sql_optimizer import DetecteurN1, InfoRequete

        queries = [
            InfoRequete(sql="SELECT * FROM ingredients WHERE recette_id = 5", duration_ms=1.0)
        ]

        parent = DetecteurN1._guess_parent_table(queries)
        assert parent == "recette"

    def test_guess_parent_table_unknown(self, mock_streamlit):
        """Retourne unknown si pas de FK trouvÃ©e."""
        from src.core.sql_optimizer import DetecteurN1, InfoRequete

        queries = [InfoRequete(sql="SELECT * FROM users", duration_ms=1.0)]

        parent = DetecteurN1._guess_parent_table(queries)
        assert parent == "unknown"

    def test_analyze_no_queries(self, mock_streamlit):
        """analyze retourne vide si peu de requÃªtes."""
        from src.core.sql_optimizer import DetecteurN1

        with patch("src.core.sql_optimizer.EcouteurSQLAlchemy") as mock_listener:
            mock_listener.get_queries.return_value = []

            detections = DetecteurN1.analyze()
            assert detections == []

    def test_analyze_detects_n1(self, mock_streamlit):
        """analyze dÃ©tecte les patterns N+1."""
        from src.core.sql_optimizer import DetecteurN1, InfoRequete

        # Simuler 10 requÃªtes similaires (N+1 pattern)
        repeated_queries = [
            InfoRequete(
                sql=f"SELECT * FROM ingredients WHERE recette_id = {i}",
                duration_ms=1.0,
                operation="SELECT",
                table="ingredients",
            )
            for i in range(10)
        ]

        with patch("src.core.sql_optimizer.EcouteurSQLAlchemy") as mock_listener:
            mock_listener.get_queries.return_value = repeated_queries

            detections = DetecteurN1.analyze()

            assert len(detections) >= 1
            assert detections[0].table == "ingredients"
            assert detections[0].count >= 5

    def test_get_detections_empty(self, mock_streamlit):
        """get_detections retourne liste vide par dÃ©faut."""
        from src.core.sql_optimizer import DetecteurN1

        detections = DetecteurN1.get_detections()
        assert detections == []

    def test_get_detections_with_data(self, mock_streamlit):
        """get_detections retourne les dÃ©tections sauvegardÃ©es."""
        from src.core.sql_optimizer import DetecteurN1, DetectionN1

        mock_streamlit.session_state["_n1_detections"] = [
            DetectionN1(table="test", parent_table="parent", count=10)
        ]

        detections = DetecteurN1.get_detections()
        assert len(detections) == 1
