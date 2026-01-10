"""
Module IA - Client, Analyseur, Cache
Tout harmonisé en français
"""

from .client import ClientIA, obtenir_client_ia
from .parser import AnalyseurIA, analyser_liste_reponse
from .cache import CacheIA

# Alias anglais pour compatibilité
AIClient = ClientIA
get_ai_client = obtenir_client_ia
AIParser = AnalyseurIA
parse_list_response = analyser_liste_reponse
AICache = CacheIA

__all__ = [
    # Noms français (prioritaires)
    "ClientIA",
    "obtenir_client_ia",
    "AnalyseurIA",
    "analyser_liste_reponse",
    "CacheIA",

    # Alias anglais (compatibilité)
    "AIClient",
    "get_ai_client",
    "AIParser",
    "parse_list_response",
    "AICache",
]