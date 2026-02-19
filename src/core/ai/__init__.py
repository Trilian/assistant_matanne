"""
Module IA - Client, Analyseur, Cache, Rate Limiting
Tout harmonisé en français avec exports propres
"""

from .cache import CacheIA
from .client import ClientIA, obtenir_client_ia
from .parser import AnalyseurIA, analyser_liste_reponse
from .rate_limit import RateLimitIA

# Alias pour compatibilité (RateLimitIA est la source de vérité)
LimiteDebit = RateLimitIA

__all__ = [
    "ClientIA",
    "obtenir_client_ia",
    "AnalyseurIA",
    "analyser_liste_reponse",
    "CacheIA",
    "RateLimitIA",
    "LimiteDebit",  # Alias vers RateLimitIA
]
