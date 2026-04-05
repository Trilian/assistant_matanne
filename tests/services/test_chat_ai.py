"""
Tests unitaires pour ChatAIService.

Couvre: résolution de contexte, mapping pages, system prompts, envoi de message.
"""

import pytest
from unittest.mock import Mock

from src.services.utilitaires.chat.chat_ai import (
    ChatAIService,
    MAPPING_PAGE_CONTEXTE,
    SYSTEM_PROMPTS,
)


class TestChatAIContexte:
    """Tests pour l'enrichissement contextuel du ChatAIService."""

    @pytest.fixture
    def service(self):
        return ChatAIService()

    # — _resoudre_contexte —

    def test_contexte_explicite_non_general(self, service):
        """Contexte explicite != general → retourné tel quel, peu importe la page."""
        assert service._resoudre_contexte("cuisine", "/maison/projets") == "cuisine"

    def test_contexte_general_sans_page(self, service):
        """Contexte general sans page → reste general."""
        assert service._resoudre_contexte("general", None) == "general"

    def test_contexte_general_page_cuisine(self, service):
        """Contexte general + page /cuisine → résolu en cuisine."""
        assert service._resoudre_contexte("general", "/cuisine/recettes") == "cuisine"

    def test_contexte_general_page_jardin(self, service):
        """Contexte general + page /jardin → résolu en jardin."""
        assert service._resoudre_contexte("general", "/jardin") == "jardin"

    def test_contexte_general_page_maison_jardin(self, service):
        """Contexte general + page /maison/jardin → résolu en maison (premier segment)."""
        assert service._resoudre_contexte("general", "/maison/jardin") == "maison"

    def test_contexte_general_page_jeux(self, service):
        """Contexte general + page /jeux/paris → résolu en jeux."""
        assert service._resoudre_contexte("general", "/jeux/paris") == "jeux"

    def test_contexte_general_page_planning(self, service):
        """Contexte general + page /planning → résolu en planning."""
        assert service._resoudre_contexte("general", "/planning") == "planning"

    def test_contexte_general_page_inventaire(self, service):
        """Contexte general + page /inventaire → résolu en inventaire."""
        assert service._resoudre_contexte("general", "/inventaire") == "inventaire"

    def test_contexte_general_page_inconnue(self, service):
        """Contexte general + page inconnue → reste general."""
        assert service._resoudre_contexte("general", "/page-inconnue") == "general"

    def test_contexte_general_page_batch_cooking(self, service):
        """Contexte general + page /batch-cooking → résolu en cuisine."""
        assert service._resoudre_contexte("general", "/batch-cooking") == "cuisine"

    # — MAPPING_PAGE_CONTEXTE —

    def test_mapping_couvre_modules(self):
        """Le mapping inclut les contextes attendus."""
        assert "jardin" in MAPPING_PAGE_CONTEXTE
        assert "jeux" in MAPPING_PAGE_CONTEXTE
        assert "paris" in MAPPING_PAGE_CONTEXTE
        assert "planning" in MAPPING_PAGE_CONTEXTE
        assert "inventaire" in MAPPING_PAGE_CONTEXTE

    # — SYSTEM_PROMPTS —

    def test_prompts_nouveaux_contextes(self):
        """Des system prompts existent pour les contextes enrichis."""
        for ctx in ("jardin", "jeux", "planning", "inventaire"):
            assert ctx in SYSTEM_PROMPTS, f"System prompt manquant pour '{ctx}'"

    def test_prompts_contenu_pertinent(self):
        """Les prompts mentionnent le bon sujet."""
        assert "jardin" in SYSTEM_PROMPTS["jardin"].lower()
        assert "paris" in SYSTEM_PROMPTS["jeux"].lower() or "jeux" in SYSTEM_PROMPTS["jeux"].lower()
        assert "repas" in SYSTEM_PROMPTS["planning"].lower() or "menu" in SYSTEM_PROMPTS["planning"].lower()
        assert "stock" in SYSTEM_PROMPTS["inventaire"].lower() or "péremption" in SYSTEM_PROMPTS["inventaire"].lower()

    # — envoyer_message avec contexte_page —

    def test_envoyer_message_avec_contexte_page(self, service):
        """envoyer_message accepte contexte_page et l'utilise."""
        service.call_with_cache_sync = Mock(return_value="Réponse test")

        result = service.envoyer_message(
            message="Bonjour",
            contexte="general",
            contexte_page="/cuisine/recettes",
        )
        assert result == "Réponse test"
        # Le system prompt utilisé doit être celui de "cuisine"
        call_args = service.call_with_cache_sync.call_args
        system_prompt = call_args.kwargs.get("system_prompt", "")
        assert "culinaire" in system_prompt or "cuisine" in system_prompt.lower()
