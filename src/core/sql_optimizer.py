"""
SQL Optimizer - Optimisation des requêtes SQLAlchemy.

Fonctionnalités :
- Écoute des événements SQLAlchemy
- Tracking automatique des requêtes
- Détection N+1 queries
- Suggestions d'optimisation
- Batch loading intelligent
"""

import logging
import re
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, TypeVar

import streamlit as st
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Query, Session, joinedload, selectinload

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ═══════════════════════════════════════════════════════════
# TYPES
# ═══════════════════════════════════════════════════════════


@dataclass
class QueryInfo:
    """Information sur une requête SQL."""
    
    sql: str
    duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    table: str = ""
    operation: str = ""  # SELECT, INSERT, UPDATE, DELETE
    parameters: dict = field(default_factory=dict)


@dataclass
class N1Detection:
    """Détection de problème N+1."""
    
    table: str
    parent_table: str
    count: int
    first_seen: datetime = field(default_factory=datetime.now)
    sample_query: str = ""


# ═══════════════════════════════════════════════════════════
# LISTENER SQLALCHEMY
# ═══════════════════════════════════════════════════════════


class SQLAlchemyListener:
    """
    Écoute les événements SQLAlchemy pour tracking.
    
    S'attache automatiquement à l'engine pour capturer
    toutes les requêtes exécutées.
    """
    
    SESSION_KEY = "_sqlalchemy_query_log"
    _installed = False
    _current_query_start: dict = {}
    
    @classmethod
    def install(cls, engine: Engine) -> None:
        """
        Installe les listeners sur l'engine.
        
        Args:
            engine: SQLAlchemy Engine
        """
        if cls._installed:
            return
        
        @event.listens_for(engine, "before_cursor_execute")
        def before_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info["query_start_time"] = time.perf_counter()
        
        @event.listens_for(engine, "after_cursor_execute")
        def after_execute(conn, cursor, statement, parameters, context, executemany):
            start_time = conn.info.pop("query_start_time", None)
            if start_time:
                duration_ms = (time.perf_counter() - start_time) * 1000
                cls._log_query(statement, duration_ms, parameters)
        
        cls._installed = True
        logger.info("✅ SQLAlchemy listener installé")
    
    @classmethod
    def _log_query(cls, sql: str, duration_ms: float, parameters: Any) -> None:
        """Enregistre une requête dans le log."""
        # Extraire table et opération
        operation = cls._extract_operation(sql)
        table = cls._extract_table(sql)
        
        query_info = QueryInfo(
            sql=sql[:500],  # Tronquer
            duration_ms=duration_ms,
            table=table,
            operation=operation,
            parameters=dict(parameters) if isinstance(parameters, dict) else {},
        )
        
        # Sauvegarder dans session
        if cls.SESSION_KEY not in st.session_state:
            st.session_state[cls.SESSION_KEY] = []
        
        st.session_state[cls.SESSION_KEY].append(query_info)
        
        # Garder seulement les 200 dernières
        if len(st.session_state[cls.SESSION_KEY]) > 200:
            st.session_state[cls.SESSION_KEY] = st.session_state[cls.SESSION_KEY][-200:]
        
        # Log si lente
        if duration_ms > 100:
            logger.warning(f"⚠️ Requête lente ({duration_ms:.0f}ms) sur {table}: {operation}")
    
    @classmethod
    def _extract_operation(cls, sql: str) -> str:
        """Extrait le type d'opération SQL."""
        sql_upper = sql.strip().upper()
        for op in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP"]:
            if sql_upper.startswith(op):
                return op
        return "OTHER"
    
    @classmethod
    def _extract_table(cls, sql: str) -> str:
        """Extrait le nom de la table principale."""
        patterns = [
            r"FROM\s+[\"']?(\w+)[\"']?",
            r"INTO\s+[\"']?(\w+)[\"']?",
            r"UPDATE\s+[\"']?(\w+)[\"']?",
            r"TABLE\s+[\"']?(\w+)[\"']?",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return "unknown"
    
    @classmethod
    def get_queries(cls) -> list[QueryInfo]:
        """Retourne toutes les requêtes loggées."""
        return st.session_state.get(cls.SESSION_KEY, [])
    
    @classmethod
    def get_stats(cls) -> dict:
        """Calcule les statistiques des requêtes."""
        queries = cls.get_queries()
        
        if not queries:
            return {
                "total": 0,
                "by_operation": {},
                "by_table": {},
                "slow_queries": [],
                "avg_time_ms": 0,
            }
        
        by_operation = defaultdict(int)
        by_table = defaultdict(int)
        total_time = 0
        slow = []
        
        for q in queries:
            by_operation[q.operation] += 1
            by_table[q.table] += 1
            total_time += q.duration_ms
            
            if q.duration_ms > 100:
                slow.append(q)
        
        return {
            "total": len(queries),
            "by_operation": dict(by_operation),
            "by_table": dict(sorted(by_table.items(), key=lambda x: x[1], reverse=True)[:10]),
            "slow_queries": slow[-10:],
            "avg_time_ms": round(total_time / len(queries), 2),
        }
    
    @classmethod
    def clear(cls) -> None:
        """Vide le log."""
        st.session_state[cls.SESSION_KEY] = []


# ═══════════════════════════════════════════════════════════
# DÉTECTEUR N+1
# ═══════════════════════════════════════════════════════════


class N1Detector:
    """
    Détecte les problèmes N+1 queries.
    
    Un problème N+1 se produit quand on fait N requêtes
    supplémentaires pour charger des relations, au lieu
    d'une seule requête avec JOIN.
    """
    
    SESSION_KEY = "_n1_detections"
    THRESHOLD = 5  # Min requêtes similaires pour alerter
    
    @classmethod
    def analyze(cls) -> list[N1Detection]:
        """
        Analyse les requêtes récentes pour détecter N+1.
        
        Returns:
            Liste des détections N+1
        """
        queries = SQLAlchemyListener.get_queries()
        
        if len(queries) < cls.THRESHOLD:
            return []
        
        # Grouper par pattern de requête
        patterns = defaultdict(list)
        
        for q in queries:
            if q.operation == "SELECT":
                # Normaliser la requête (retirer les valeurs)
                pattern = cls._normalize_query(q.sql)
                patterns[pattern].append(q)
        
        # Détecter les patterns répétés
        detections = []
        
        for pattern, pattern_queries in patterns.items():
            if len(pattern_queries) >= cls.THRESHOLD:
                # Probable N+1
                table = pattern_queries[0].table
                
                detection = N1Detection(
                    table=table,
                    parent_table=cls._guess_parent_table(pattern_queries),
                    count=len(pattern_queries),
                    sample_query=pattern_queries[0].sql[:200],
                )
                detections.append(detection)
        
        # Sauvegarder
        st.session_state[cls.SESSION_KEY] = detections
        
        if detections:
            logger.warning(f"⚠️ {len(detections)} problème(s) N+1 détecté(s)")
        
        return detections
    
    @classmethod
    def _normalize_query(cls, sql: str) -> str:
        """Normalise une requête pour comparaison."""
        # Retirer les valeurs numériques
        normalized = re.sub(r'\b\d+\b', '?', sql)
        # Retirer les strings
        normalized = re.sub(r"'[^']*'", "'?'", normalized)
        return normalized
    
    @classmethod
    def _guess_parent_table(cls, queries: list[QueryInfo]) -> str:
        """Devine la table parente d'un N+1."""
        # Chercher des patterns de FK
        for q in queries:
            match = re.search(r'WHERE\s+["\']?(\w+_id)["\']?\s*=', q.sql, re.IGNORECASE)
            if match:
                fk = match.group(1)
                return fk.replace("_id", "")
        return "unknown"
    
    @classmethod
    def get_detections(cls) -> list[N1Detection]:
        """Retourne les détections N+1."""
        return st.session_state.get(cls.SESSION_KEY, [])
    
    @classmethod
    def get_suggestions(cls) -> list[str]:
        """
        Génère des suggestions pour corriger les N+1.
        
        Returns:
            Liste de suggestions
        """
        detections = cls.get_detections()
        suggestions = []
        
        for d in detections:
            if d.parent_table != "unknown":
                suggestions.append(
                    f"💡 Table '{d.table}': Utiliser `joinedload({d.parent_table})` "
                    f"ou `selectinload({d.parent_table})` pour éviter {d.count} requêtes"
                )
            else:
                suggestions.append(
                    f"💡 Table '{d.table}': {d.count} requêtes similaires détectées. "
                    f"Considérer un eager loading des relations."
                )
        
        return suggestions


# ═══════════════════════════════════════════════════════════
# BATCH LOADER
# ═══════════════════════════════════════════════════════════


class BatchLoader:
    """
    Utilitaires pour le chargement par lots.
    """
    
    @staticmethod
    def load_in_batches(
        query: Query,
        batch_size: int = 100,
        callback: Callable[[list], None] | None = None,
    ) -> list:
        """
        Charge les résultats d'une requête par lots.
        
        Args:
            query: Requête SQLAlchemy
            batch_size: Taille des lots
            callback: Fonction appelée pour chaque lot
            
        Returns:
            Tous les résultats
        """
        results = []
        offset = 0
        
        while True:
            batch = query.offset(offset).limit(batch_size).all()
            
            if not batch:
                break
            
            results.extend(batch)
            
            if callback:
                callback(batch)
            
            offset += batch_size
            
            # Éviter boucle infinie
            if len(batch) < batch_size:
                break
        
        return results
    
    @staticmethod
    def chunked(items: list, chunk_size: int = 100):
        """
        Générateur qui découpe une liste en chunks.
        
        Args:
            items: Liste à découper
            chunk_size: Taille des chunks
            
        Yields:
            Chunks de la liste
        """
        for i in range(0, len(items), chunk_size):
            yield items[i:i + chunk_size]


# ═══════════════════════════════════════════════════════════
# QUERY BUILDER OPTIMISÉ
# ═══════════════════════════════════════════════════════════


class OptimizedQueryBuilder:
    """
    Builder de requêtes avec optimisations automatiques.
    """
    
    def __init__(self, session: Session, model: type):
        """
        Initialise le builder.
        
        Args:
            session: Session SQLAlchemy
            model: Modèle de base
        """
        self._session = session
        self._model = model
        self._query = session.query(model)
        self._eager_loads = []
        self._filters = []
        self._order_by = None
        self._limit = None
        self._offset = None
    
    def eager_load(self, *relationships: str) -> "OptimizedQueryBuilder":
        """
        Ajoute des relations en eager loading.
        
        Args:
            relationships: Noms des relations
            
        Returns:
            Self pour chaînage
        """
        for rel in relationships:
            self._eager_loads.append(rel)
        return self
    
    def filter_by(self, **kwargs) -> "OptimizedQueryBuilder":
        """
        Ajoute des filtres.
        
        Args:
            kwargs: Filtres clé=valeur
            
        Returns:
            Self pour chaînage
        """
        self._filters.append(kwargs)
        return self
    
    def order(self, column: str, desc: bool = False) -> "OptimizedQueryBuilder":
        """
        Définit l'ordre.
        
        Args:
            column: Colonne de tri
            desc: Ordre descendant
            
        Returns:
            Self pour chaînage
        """
        self._order_by = (column, desc)
        return self
    
    def paginate(self, page: int = 1, per_page: int = 20) -> "OptimizedQueryBuilder":
        """
        Applique pagination.
        
        Args:
            page: Numéro de page (1-based)
            per_page: Éléments par page
            
        Returns:
            Self pour chaînage
        """
        self._offset = (page - 1) * per_page
        self._limit = per_page
        return self
    
    def build(self) -> Query:
        """
        Construit la requête optimisée.
        
        Returns:
            Query SQLAlchemy
        """
        query = self._query
        
        # Appliquer eager loading
        for rel in self._eager_loads:
            if hasattr(self._model, rel):
                # Utiliser selectinload pour les collections
                query = query.options(selectinload(getattr(self._model, rel)))
        
        # Appliquer filtres
        for filter_kwargs in self._filters:
            query = query.filter_by(**filter_kwargs)
        
        # Appliquer ordre
        if self._order_by:
            column, desc = self._order_by
            col_attr = getattr(self._model, column, None)
            if col_attr is not None:
                query = query.order_by(col_attr.desc() if desc else col_attr)
        
        # Appliquer pagination
        if self._offset is not None:
            query = query.offset(self._offset)
        if self._limit is not None:
            query = query.limit(self._limit)
        
        return query
    
    def all(self) -> list:
        """Exécute et retourne tous les résultats."""
        return self.build().all()
    
    def first(self) -> Any | None:
        """Exécute et retourne le premier résultat."""
        return self.build().first()
    
    def count(self) -> int:
        """Compte les résultats."""
        return self.build().count()


# ═══════════════════════════════════════════════════════════
# COMPOSANTS UI
# ═══════════════════════════════════════════════════════════


def render_sql_analysis():
    """Affiche l'analyse SQL dans l'interface."""
    
    stats = SQLAlchemyListener.get_stats()
    
    with st.expander("🗃️ Analyse SQL", expanded=False):
        
        if stats["total"] == 0:
            st.info("Aucune requête enregistrée")
            return
        
        # Métriques générales
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total requêtes", stats["total"])
        with col2:
            st.metric("Temps moyen", f"{stats['avg_time_ms']}ms")
        with col3:
            slow_count = len(stats["slow_queries"])
            st.metric(
                "Requêtes lentes",
                slow_count,
                delta=f"-{slow_count}" if slow_count > 0 else None,
                delta_color="inverse",
            )
        
        # Par opération
        st.caption("📊 Par opération:")
        for op, count in stats["by_operation"].items():
            st.progress(count / stats["total"], text=f"{op}: {count}")
        
        # Détection N+1
        detections = N1Detector.analyze()
        if detections:
            st.warning(f"⚠️ {len(detections)} problème(s) N+1 détecté(s)")
            
            for suggestion in N1Detector.get_suggestions():
                st.caption(suggestion)
        
        # Boutons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Analyser N+1", key="analyze_n1"):
                N1Detector.analyze()
                st.rerun()
        with col2:
            if st.button("🗑️ Vider log", key="clear_sql_log"):
                SQLAlchemyListener.clear()
                st.rerun()


# ═══════════════════════════════════════════════════════════
# EXPORTS
# ═══════════════════════════════════════════════════════════


__all__ = [
    # Classes
    "QueryInfo",
    "N1Detection",
    "SQLAlchemyListener",
    "N1Detector",
    "BatchLoader",
    "OptimizedQueryBuilder",
    # UI
    "render_sql_analysis",
]
