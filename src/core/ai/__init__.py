"""
Module IA - Client, Parser, Cache + Cache Sémantique
"""

from .client import AIClient, get_ai_client
from .parser import AIParser, parse_list_response
from .cache import CacheIA

__all__ = [
    # Client
    "AIClient",
    "get_ai_client",

    # Parser
    "AIParser",
    "parse_list_response",

    # Cache classique
    "CacheIA",
]
