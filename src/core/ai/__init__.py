"""
Module IA - Client, Parser, Cache
Mis à jour pour intégrer BaseAIService
"""

from .client import AIClient, get_ai_client
from .parser import AIParser, parse_list_response
from .cache import AICache

# Note: BaseAIService est dans src/services/
# (car il hérite de concepts métier)

__all__ = [
    "AIClient",
    "get_ai_client",
    "AIParser",
    "parse_list_response",
    "AICache"
]