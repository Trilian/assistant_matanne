"""
Service IA pour l'auto-étiquetage des notes.

Analyse le contenu d'une note et propose des tags pertinents
basés sur le contexte familial (courses, maison, Jules, recette, etc.).
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class TagsProposes(BaseModel):
    """Résultat de l'auto-étiquetage IA."""

    tags: list[str] = Field(default_factory=list, description="Tags proposés")
    confiance: float = Field(0.0, ge=0.0, le=1.0, description="Score de confiance global")


TAGS_DISPONIBLES = [
    "courses",
    "recette",
    "cuisine",
    "maison",
    "jardin",
    "entretien",
    "jules",
    "famille",
    "budget",
    "sante",
    "voyage",
    "travaux",
    "administratif",
    "idee",
    "rappel",
    "urgent",
    "projet",
]


class NotesIAService(BaseAIService):
    """Service d'auto-étiquetage des notes via IA."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            cache_prefix="notes_ia",
            default_ttl=3600,
            default_temperature=0.3,
            service_name="notes_ia",
            **kwargs,
        )

    def auto_etiqueter(self, contenu: str, titre: str = "") -> TagsProposes:
        """Analyse le contenu d'une note et propose des tags pertinents.

        Args:
            contenu: Texte de la note à analyser.
            titre: Titre optionnel de la note.

        Returns:
            TagsProposes avec la liste de tags et un score de confiance.
        """
        if not contenu and not titre:
            return TagsProposes(tags=[], confiance=0.0)

        texte_complet = f"{titre}\n{contenu}" if titre else contenu

        prompt = f"""Analyse cette note familiale et propose les tags les plus pertinents.

Tags disponibles : {", ".join(TAGS_DISPONIBLES)}

Règles :
- Retourne entre 1 et 4 tags maximum
- Choisis uniquement parmi les tags disponibles
- Évalue ta confiance globale entre 0.0 et 1.0

Note à analyser :
---
{texte_complet[:1500]}
---

Réponds en JSON : {{"tags": ["tag1", "tag2"], "confiance": 0.85}}"""

        system_prompt = (
            "Tu es un classificateur de notes familiales. "
            "Tu analyses le contenu et proposes des tags pertinents. "
            "Réponds uniquement en JSON valide."
        )

        result = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=TagsProposes,
            system_prompt=system_prompt,
            temperature=0.3,
            use_cache=True,
        )

        if result is None:
            return TagsProposes(tags=[], confiance=0.0)

        # Filtrer les tags invalides
        result.tags = [t for t in result.tags if t in TAGS_DISPONIBLES]
        return result


@service_factory("notes_ia", tags={"ia", "utilitaires"})
def get_notes_ia_service() -> NotesIAService:
    """Factory pour le service d'auto-étiquetage des notes."""
    return NotesIAService()
