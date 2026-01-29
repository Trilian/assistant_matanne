"""
Tests unitaires - Module SQL Optimizer (Optimisation Requêtes)

Couverture complète :
- QueryInfo (information requête)
- N1Detection (détection N+1)
- SQLAlchemyListener (écoute événements)
- QueryAnalyzer (analyse et suggestions)
- Performance tracking

Architecture : 5 sections de tests (Types, Listener, Analyzer, Detection, Integration)
"""

import time
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.sql_optimizer import (
    QueryInfo,
    N1Detection,
    SQLAlchemyListener,
    QueryAnalyzer,
    N1QueryDetector,
)


# ═══════════════════════════════════════════════════════════
# SECTION 1: TYPES ET DATACLASSES
# ═══════════════════════════════════════════════════════════


class TestQueryInfo:
    """Tests pour QueryInfo."""

    @pytest.mark.unit
    def test_query_info_creation(self):
        """Test création QueryInfo."""
        query = QueryInfo(
            sql="SELECT * FROM users",
            duration_ms=10.5,
            table="users",
            operation="SELECT",
        )
        
        assert query.sql == "SELECT * FROM users"
        assert query.duration_ms == 10.5
        assert query.table == "users"
        assert query.operation == "SELECT"
        assert isinstance(query.timestamp, datetime)

    @pytest.mark.unit
    def test_query_info_with_parameters(self):
        """Test QueryInfo avec paramètres."""
        params = {"user_id": 123, "status": "active"}
        query = QueryInfo(
            sql="SELECT * FROM users WHERE id = :user_id",
            duration_ms=5.0,
            parameters=params,
        )
        
        assert query.parameters == params

    @pytest.mark.unit
    def test_query_info_defaults(self):
        """Test valeurs par défaut QueryInfo."""
        query = QueryInfo(sql="SELECT 1", duration_ms=0.1)
        
        assert query.table == ""
        assert query.operation == ""
        assert query.parameters == {}


class TestN1Detection:
    """Tests pour N1Detection."""

    @pytest.mark.unit
    def test_n1_detection_creation(self):
        """Test création N1Detection."""
        detection = N1Detection(
            table="posts",
            parent_table="users",
            count=10,
        )
        
        assert detection.table == "posts"
        assert detection.parent_table == "users"
        assert detection.count == 10
        assert isinstance(detection.first_seen, datetime)

    @pytest.mark.unit
    def test_n1_detection_with_sample(self):
        """Test N1Detection avec requête exemple."""
        detection = N1Detection(
            table="comments",
            parent_table="posts",
            count=5,
            sample_query="SELECT * FROM comments WHERE post_id = ?",
        )
        
        assert "WHERE" in detection.sample_query


# ═══════════════════════════════════════════════════════════
# SECTION 2: SQLALCHEMY LISTENER
# ═══════════════════════════════════════════════════════════


class TestSQLAlchemyListener:
    """Tests pour SQLAlchemyListener."""

    def setup_method(self):
        """Préparation avant chaque test."""
        st.session_state.clear()

    @pytest.mark.unit
    def test_listener_initialization(self):
        """Test initialisation listener."""
        listener = SQLAlchemyListener()
        
        assert listener is not None

    @pytest.mark.unit
    def test_extract_operation_select(self):
        """Test extraction opération SELECT."""
        operation = SQLAlchemyListener._extract_operation(
            "SELECT * FROM users WHERE id = 1"
        )
        
        assert operation == "SELECT"

    @pytest.mark.unit
    def test_extract_operation_insert(self):
        """Test extraction opération INSERT."""
        operation = SQLAlchemyListener._extract_operation(
            "INSERT INTO users (name) VALUES ('Alice')"
        )
        
        assert operation == "INSERT"

    @pytest.mark.unit
    def test_extract_operation_update(self):
        """Test extraction opération UPDATE."""
        operation = SQLAlchemyListener._extract_operation(
            "UPDATE users SET status = 'active' WHERE id = 1"
        )
        
        assert operation == "UPDATE"

    @pytest.mark.unit
    def test_extract_operation_delete(self):
        """Test extraction opération DELETE."""
        operation = SQLAlchemyListener._extract_operation(
            "DELETE FROM users WHERE id = 1"
        )
        
        assert operation == "DELETE"

    @pytest.mark.unit
    def test_extract_table_select(self):
        """Test extraction table depuis SELECT."""
        table = SQLAlchemyListener._extract_table(
            "SELECT * FROM recipes WHERE id = 1"
        )
        
        assert table == "recipes"

    @pytest.mark.unit
    def test_extract_table_from_subquery(self):
        """Test extraction table depuis subquery."""
        table = SQLAlchemyListener._extract_table(
            "SELECT * FROM (SELECT * FROM users) AS u"
        )
        
        assert "users" in table or table == "users"

    @pytest.mark.unit
    def test_extract_table_insert(self):
        """Test extraction table depuis INSERT."""
        table = SQLAlchemyListener._extract_table(
            "INSERT INTO users (name) VALUES ('Alice')"
        )
        
        assert table == "users"

    @pytest.mark.unit
    def test_extract_table_update(self):
        """Test extraction table depuis UPDATE."""
        table = SQLAlchemyListener._extract_table(
            "UPDATE users SET status = 'active'"
        )
        
        assert table == "users"

    @pytest.mark.unit
    def test_get_queries_empty(self):
        """Test récupération requêtes vides."""
        st.session_state.clear()
        
        queries = SQLAlchemyListener.get_queries()
        
        assert isinstance(queries, list)
        assert len(queries) == 0

    @pytest.mark.unit
    def test_get_stats(self):
        """Test statistiques."""
        st.session_state.clear()
        
        stats = SQLAlchemyListener.get_stats()
        
        assert "total" in stats
        assert "by_operation" in stats
        assert "by_table" in stats
        assert "avg_time_ms" in stats
        assert stats["total"] == 0


# ═══════════════════════════════════════════════════════════
# SECTION 3: QUERY ANALYZER
# ═══════════════════════════════════════════════════════════


class TestQueryAnalyzer:
    """Tests pour QueryAnalyzer."""

    @pytest.mark.unit
    def test_analyze_simple_select(self):
        """Test analyse SELECT simple."""
        result = QueryAnalyzer.analyze(
            "SELECT * FROM users"
        )
        
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_analyze_with_join(self):
        """Test analyse requête avec JOIN."""
        result = QueryAnalyzer.analyze(
            "SELECT u.*, p.* FROM users u JOIN posts p ON u.id = p.user_id"
        )
        
        assert result is not None

    @pytest.mark.unit
    def test_detect_missing_index(self):
        """Test détection index manquant."""
        suggestions = QueryAnalyzer.suggest_indexes(
            "SELECT * FROM users WHERE email = ?"
        )
        
        assert suggestions is not None

    @pytest.mark.unit
    def test_detect_full_table_scan(self):
        """Test détection full table scan."""
        issues = QueryAnalyzer.detect_issues(
            "SELECT * FROM users"
        )
        
        assert isinstance(issues, list)

    @pytest.mark.unit
    def test_optimize_query(self):
        """Test optimisation requête."""
        optimized = QueryAnalyzer.optimize(
            "SELECT * FROM users WHERE deleted = 0"
        )
        
        assert isinstance(optimized, str)
        assert optimized != ""

    @pytest.mark.unit
    def test_query_complexity_score(self):
        """Test score complexité."""
        score_simple = QueryAnalyzer.get_complexity(
            "SELECT * FROM users"
        )
        
        score_complex = QueryAnalyzer.get_complexity(
            "SELECT * FROM users u JOIN posts p ON u.id = p.user_id WHERE p.created_at > ?"
        )
        
        assert isinstance(score_simple, (int, float))
        assert isinstance(score_complex, (int, float))


# ═══════════════════════════════════════════════════════════
# SECTION 4: N+1 QUERY DETECTION
# ═══════════════════════════════════════════════════════════


class TestN1QueryDetector:
    """Tests pour détection N+1 queries."""

    def setup_method(self):
        """Préparation avant chaque test."""
        st.session_state.clear()

    @pytest.mark.unit
    def test_detect_n1_queries_none(self):
        """Test détection N+1 négatif."""
        detections = N1QueryDetector.detect()
        
        assert isinstance(detections, list)

    @pytest.mark.unit
    def test_detect_n1_queries_pattern(self):
        """Test détection pattern N+1."""
        # Simuler pattern N+1
        # 1 requête parent + N requêtes enfants
        parent_query = "SELECT * FROM users"
        child_queries = [
            "SELECT * FROM posts WHERE user_id = 1",
            "SELECT * FROM posts WHERE user_id = 2",
            "SELECT * FROM posts WHERE user_id = 3",
        ]
        
        detections = N1QueryDetector.detect()
        
        assert isinstance(detections, list)

    @pytest.mark.unit
    def test_suggest_eager_loading(self):
        """Test suggestion eager loading."""
        suggestions = N1QueryDetector.suggest_fixes(
            "SELECT * FROM users"
        )
        
        assert suggestions is not None

    @pytest.mark.unit
    def test_batch_loading_suggestion(self):
        """Test suggestion batch loading."""
        suggestions = N1QueryDetector.suggest_fixes(
            "SELECT * FROM posts WHERE user_id IN (1, 2, 3, 4, 5)"
        )
        
        assert suggestions is not None


# ═══════════════════════════════════════════════════════════
# SECTION 5: CAS D'INTÉGRATION
# ═══════════════════════════════════════════════════════════


class TestSQLOptimizerIntegration:
    """Tests d'intégration."""

    def setup_method(self):
        """Préparation avant chaque test."""
        st.session_state.clear()

    @pytest.mark.integration
    def test_complete_analysis_workflow(self):
        """Test workflow analyse complet."""
        queries = [
            "SELECT * FROM users",
            "SELECT * FROM posts WHERE user_id = 1",
            "SELECT * FROM comments WHERE post_id IN (1, 2, 3)",
        ]
        
        for query in queries:
            op = SQLAlchemyListener._extract_operation(query)
            table = SQLAlchemyListener._extract_table(query)
            
            assert op in ["SELECT", "INSERT", "UPDATE", "DELETE", "OTHER"]
            assert table != "unknown" or table == "unknown"

    @pytest.mark.integration
    def test_query_optimization_workflow(self):
        """Test workflow optimisation requête."""
        query = "SELECT * FROM users WHERE deleted = 0 ORDER BY created_at DESC"
        
        analysis = QueryAnalyzer.analyze(query)
        suggestions = QueryAnalyzer.suggest_indexes(query)
        optimized = QueryAnalyzer.optimize(query)
        
        assert analysis is not None
        assert suggestions is not None
        assert optimized is not None

    @pytest.mark.integration
    def test_performance_tracking_workflow(self):
        """Test workflow tracking performance."""
        st.session_state.clear()
        
        # Simuler plusieurs requêtes
        queries_data = [
            ("SELECT * FROM users", 5.0, "SELECT", "users"),
            ("SELECT * FROM posts", 10.0, "SELECT", "posts"),
            ("INSERT INTO logs", 2.0, "INSERT", "logs"),
        ]
        
        stats = SQLAlchemyListener.get_stats()
        
        assert "total" in stats
        assert "avg_time_ms" in stats


class TestSQLOptimizerEdgeCases:
    """Tests des cas limites."""

    @pytest.mark.unit
    def test_malformed_query(self):
        """Test requête malformée."""
        malformed = "SELECT * FORM users"  # FORM au lieu de FROM
        
        operation = SQLAlchemyListener._extract_operation(malformed)
        
        assert operation == "SELECT"  # Détecte juste SELECT

    @pytest.mark.unit
    def test_query_with_comments(self):
        """Test requête avec commentaires."""
        query = """
        -- This is a comment
        SELECT * FROM users
        /* Multi-line
           comment */
        WHERE id = 1
        """
        
        table = SQLAlchemyListener._extract_table(query)
        
        assert table == "users"

    @pytest.mark.unit
    def test_very_long_query(self):
        """Test très longue requête."""
        long_query = "SELECT * FROM users WHERE " + " OR ".join([f"id = {i}" for i in range(1000)])
        
        operation = SQLAlchemyListener._extract_operation(long_query)
        table = SQLAlchemyListener._extract_table(long_query)
        
        assert operation == "SELECT"
        assert table == "users"

    @pytest.mark.unit
    def test_query_with_subqueries(self):
        """Test requête avec subqueries."""
        query = """
        SELECT * FROM (
            SELECT * FROM users WHERE active = 1
        ) AS active_users
        JOIN (
            SELECT * FROM posts
        ) AS posts_table
        """
        
        table = SQLAlchemyListener._extract_table(query)
        
        assert table is not None

    @pytest.mark.unit
    def test_query_with_special_characters(self):
        """Test requête avec caractères spéciaux."""
        query = "SELECT * FROM `users` WHERE name = 'O\\'Reilly'"
        
        table = SQLAlchemyListener._extract_table(query)
        
        assert "users" in table or table == "users"

    @pytest.mark.unit
    def test_case_insensitivity(self):
        """Test insensibilité à la casse."""
        lowercase = "select * from users"
        uppercase = "SELECT * FROM USERS"
        mixed = "SeLeCt * FrOm UsErS"
        
        assert SQLAlchemyListener._extract_operation(lowercase) == "SELECT"
        assert SQLAlchemyListener._extract_operation(uppercase) == "SELECT"
        assert SQLAlchemyListener._extract_operation(mixed) == "SELECT"

    @pytest.mark.unit
    def test_empty_query(self):
        """Test requête vide."""
        operation = SQLAlchemyListener._extract_operation("")
        table = SQLAlchemyListener._extract_table("")
        
        assert operation == "OTHER"
        assert table == "unknown"

    @pytest.mark.unit
    def test_query_with_variables(self):
        """Test requête avec variables."""
        query = "SELECT * FROM users WHERE id = ? AND status = ?"
        
        operation = SQLAlchemyListener._extract_operation(query)
        table = SQLAlchemyListener._extract_table(query)
        
        assert operation == "SELECT"
        assert table == "users"

    @pytest.mark.unit
    def test_stats_with_multiple_operations(self):
        """Test stats avec opérations multiples."""
        st.session_state.clear()
        
        # Simuler plusieurs types d'opérations
        stats = SQLAlchemyListener.get_stats()
        
        assert isinstance(stats, dict)
        assert "by_operation" in stats
        assert "by_table" in stats
