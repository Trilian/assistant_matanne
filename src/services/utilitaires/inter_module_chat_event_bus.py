"""Compatibilité legacy pour le bridge Chat IA → Event Bus.

Ce module ré-exporte l'implémentation actuelle afin de préserver les
imports historiques utilisés par les tests et les anciens points d'entrée.
"""

from src.services.utilitaires.bridges_chat_event_bus import (
    ChatEventBusBridgeService,
    enregistrer_chat_event_bus_subscribers,
    obtenir_chat_event_bus_bridge,
)

get_chat_event_bus_bridge = obtenir_chat_event_bus_bridge

__all__ = [
    "ChatEventBusBridgeService",
    "obtenir_chat_event_bus_bridge",
    "get_chat_event_bus_bridge",
    "enregistrer_chat_event_bus_subscribers",
]
