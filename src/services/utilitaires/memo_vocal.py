"""
Service IA pour la classification des mémos vocaux.

Le frontend utilise Web Speech API pour la transcription (STT).
Ce service reçoit le texte transcrit et le classifie dans le bon module
(courses, maison, note, routine, recette) avec l'action appropriée.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, Field

from src.services.core.base import BaseAIService
from src.services.core.registry import service_factory

logger = logging.getLogger(__name__)


class MemoClassifie(BaseModel):
    """Résultat de la classification d'un mémo vocal."""

    module: str = Field(
        "note",
        description="Module cible : courses, maison, note, routine, recette, jardin, famille, rappel",
    )
    action: str = Field(
        "ajouter",
        description="Action : ajouter, rappel, tache, modifier",
    )
    contenu: str = Field("", description="Contenu extrait et nettoyé")
    tags: list[str] = Field(default_factory=list, description="Tags auto-détectés")
    destination_url: str = Field("", description="URL de la page cible dans l'app")
    confiance: float = Field(0.0, ge=0.0, le=1.0, description="Score de confiance")


MODULES_VALIDES = {"courses", "maison", "note", "routine", "recette", "jardin", "famille", "rappel"}
ACTIONS_VALIDES = {"ajouter", "rappel", "tache", "modifier"}

MODULE_URLS = {
    "courses": "/cuisine/courses",
    "recette": "/cuisine/recettes",
    "maison": "/maison",
    "jardin": "/maison/jardin",
    "routine": "/famille/routines",
    "famille": "/famille",
    "note": "/outils/notes",
    "rappel": "/outils/notes",
}


class MemoVocalService(BaseAIService):
    """Service de classification des mémos vocaux via IA."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            cache_prefix="memo_vocal",
            default_ttl=1800,
            default_temperature=0.3,
            service_name="memo_vocal",
            **kwargs,
        )

    def transcrire_et_classer(self, texte: str) -> MemoClassifie:
        """Classifie un texte transcrit dans le bon module et action.

        Args:
            texte: Texte transcrit par Web Speech API côté frontend.

        Returns:
            MemoClassifie avec module, action, contenu nettoyé et URL cible.
        """
        if not texte or not texte.strip():
            return MemoClassifie(
                module="note",
                action="ajouter",
                contenu="",
                confiance=0.0,
            )

        texte_nettoye = texte.strip()[:2000]

        prompt = f"""Classifie ce mémo vocal dans le bon module familial.

Modules possibles : courses, maison, note, routine, recette, jardin, famille, rappel
Actions possibles : ajouter, rappel, tache, modifier

Exemples :
- "Acheter du lait et du pain" → module: courses, action: ajouter, contenu: "lait, pain"
- "Arroser les tomates demain" → module: jardin, action: rappel, contenu: "arroser les tomates"
- "Faire tourner la machine à laver" → module: maison, action: tache, contenu: "machine à laver"
- "Idée de tarte aux pommes pour dimanche" → module: recette, action: ajouter, contenu: "tarte aux pommes pour dimanche"
- "Donner le bain à Jules à 19h" → module: famille, action: rappel, contenu: "bain Jules 19h"

Mémo vocal :
---
{texte_nettoye}
---

Réponds en JSON : {{"module": "...", "action": "...", "contenu": "...", "tags": ["tag1"], "confiance": 0.9}}"""

        system_prompt = (
            "Tu es un assistant de classification de mémos vocaux familiaux. "
            "Tu analyses la phrase dictée et tu la classes dans le bon module "
            "avec l'action appropriée. Réponds uniquement en JSON valide."
        )

        result = self.call_with_parsing_sync(
            prompt=prompt,
            response_model=MemoClassifie,
            system_prompt=system_prompt,
            temperature=0.3,
            use_cache=False,
        )

        if result is None:
            return MemoClassifie(
                module="note",
                action="ajouter",
                contenu=texte_nettoye,
                confiance=0.3,
            )

        # Valider et normaliser
        if result.module not in MODULES_VALIDES:
            result.module = "note"
        if result.action not in ACTIONS_VALIDES:
            result.action = "ajouter"
        result.destination_url = MODULE_URLS.get(result.module, "/outils/notes")

        return result


@service_factory("memo_vocal", tags={"ia", "utilitaires"})
def get_memo_vocal_service() -> MemoVocalService:
    """Factory pour le service de classification des mémos vocaux."""
    return MemoVocalService()
