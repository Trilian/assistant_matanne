"""
Schémas Pydantic pour l'assistant (vocal, Google Assistant, chat IA).
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommandeVocaleResponse(BaseModel):
    """Résultat de l'interprétation d'une commande vocale."""

    action: str = Field(description="courses.ajout | routine.creation | planning.resume | incomprise")
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class IntentGoogleAssistant(BaseModel):
    """Intent disponible pour Google Assistant."""

    intent: str
    description: str = ""
    slots: list[str] = Field(default_factory=list)
    action_attendue: str = ""


class IntentsGoogleAssistantResponse(BaseModel):
    """Liste des intents Google Assistant."""

    intents: list[IntentGoogleAssistant] = Field(default_factory=list)


class ResultatIntentResponse(BaseModel):
    """Résultat d'exécution d'un intent."""

    action: str
    message: str = ""
    details: dict[str, Any] = Field(default_factory=dict)


class ExecIntentGoogleAssistantResponse(BaseModel):
    """Réponse de l'exécution d'un intent Google Assistant."""

    intent: str
    langue: str = "fr"
    commande: str = ""
    resultat: ResultatIntentResponse


class ContexteMetierChat(BaseModel):
    """Contexte métier injecté dans le chat IA."""

    planning: dict[str, int] = Field(default_factory=dict)
    inventaire: dict[str, int] = Field(default_factory=dict)
    budget: dict[str, float] = Field(default_factory=dict)
    score_jules: dict[str, Any] = Field(default_factory=dict)


class ChatIAResponse(BaseModel):
    """Réponse du chat IA."""

    reponse: str = ""
    contexte: str = ""
    memoire_utilisee: int = 0
    contexte_metier: ContexteMetierChat | None = None


class ExemplesCommandeVocaleResponse(BaseModel):
    """Liste d'exemples de commandes vocales."""

    exemples: list[str] = Field(default_factory=list)
