"""Compatibilité legacy pour le bridge Chat → Contexte multi-modules."""

from src.services.utilitaires.bridges_chat_contexte import (
    ChatContexteMultiModuleService,
    obtenir_service_chat_contexte,
)

__all__ = [
    "ChatContexteMultiModuleService",
    "obtenir_service_chat_contexte",
]
