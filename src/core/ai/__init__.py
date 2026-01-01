"""
Module IA - Client, Parser, Cache + Cache Sémantique
"""

from .client import AIClient, get_ai_client
from .parser import AIParser, parse_list_response
from .cache import AICache

# 🆕 Cache Sémantique
from .semantic_cache import (
    SemanticCache,
    SemanticCacheConfig,
    EmbeddingEngine,
    get_semantic_cached_response,
    set_semantic_cached_response
)

__all__ = [
    # Client
    "AIClient",
    "get_ai_client",

    # Parser
    "AIParser",
    "parse_list_response",

    # Cache classique
    "AICache",

    # 🆕 Cache Sémantique
    "SemanticCache",
    "SemanticCacheConfig",
    "EmbeddingEngine",
    "get_semantic_cached_response",
    "set_semantic_cached_response"
]
