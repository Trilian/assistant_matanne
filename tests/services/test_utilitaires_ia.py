"""
Tests unitaires pour les services IA utilitaires.

Couvre: NotesIAService (auto-étiquetage), MemoVocalService (classification vocale).
"""

import pytest
from unittest.mock import Mock

# ──────────────────────────────────────────────
# NotesIAService
# ──────────────────────────────────────────────

from src.services.utilitaires.notes_ia import (
    NotesIAService,
    TagsProposes,
    TAGS_DISPONIBLES,
)


class TestNotesIAService:
    """Tests pour le service d'auto-étiquetage des notes."""

    @pytest.fixture
    def service(self):
        return NotesIAService()

    def test_auto_etiqueter_contenu_vide(self, service):
        """Contenu et titre vides → tags vides."""
        result = service.auto_etiqueter(contenu="", titre="")
        assert result.tags == []
        assert result.confiance == 0.0

    def test_auto_etiqueter_retour_ia(self, service):
        """IA retourne des tags → filtrage et retour."""
        service.call_with_parsing_sync = Mock(
            return_value=TagsProposes(tags=["courses", "recette"], confiance=0.9)
        )
        result = service.auto_etiqueter(contenu="Acheter du lait et des oeufs pour la tarte")
        assert "courses" in result.tags
        assert "recette" in result.tags
        assert result.confiance == 0.9

    def test_auto_etiqueter_filtre_tags_invalides(self, service):
        """L'IA retourne des tags hors liste → ils sont filtrés."""
        service.call_with_parsing_sync = Mock(
            return_value=TagsProposes(tags=["courses", "tag_inventé", "maison"], confiance=0.8)
        )
        result = service.auto_etiqueter(contenu="Réparer le robinet et acheter du lait")
        assert "courses" in result.tags
        assert "maison" in result.tags
        assert "tag_inventé" not in result.tags

    def test_auto_etiqueter_ia_none(self, service):
        """IA retourne None → fallback tags vides."""
        service.call_with_parsing_sync = Mock(return_value=None)
        result = service.auto_etiqueter(contenu="Un texte quelconque")
        assert result.tags == []
        assert result.confiance == 0.0

    def test_auto_etiqueter_avec_titre(self, service):
        """Le titre est inclus dans le prompt envoyé à l'IA."""
        service.call_with_parsing_sync = Mock(
            return_value=TagsProposes(tags=["jardin"], confiance=0.85)
        )
        result = service.auto_etiqueter(contenu="Arroser les tomates", titre="Jardin")
        service.call_with_parsing_sync.assert_called_once()
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        assert "Jardin" in prompt
        assert result.tags == ["jardin"]

    def test_tags_disponibles_coherents(self):
        """Vérifie que la liste de tags contient les catégories attendues."""
        attendus = ["courses", "recette", "maison", "jardin", "jules", "famille", "budget"]
        for tag in attendus:
            assert tag in TAGS_DISPONIBLES


# ──────────────────────────────────────────────
# MemoVocalService
# ──────────────────────────────────────────────

from src.services.utilitaires.memo_vocal import (
    MemoVocalService,
    MemoClassifie,
    MODULES_VALIDES,
    ACTIONS_VALIDES,
    MODULE_URLS,
)


class TestMemoVocalService:
    """Tests pour le service de classification des mémos vocaux."""

    @pytest.fixture
    def service(self):
        return MemoVocalService()

    def test_texte_vide(self, service):
        """Texte vide → module note, confiance 0."""
        result = service.transcrire_et_classer("")
        assert result.module == "note"
        assert result.confiance == 0.0

    def test_texte_none_like(self, service):
        """Texte whitespace → même fallback."""
        result = service.transcrire_et_classer("   ")
        assert result.module == "note"
        assert result.confiance == 0.0

    def test_classification_courses(self, service):
        """Mémo courses → module courses."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="courses",
                action="ajouter",
                contenu="lait, pain",
                tags=["alimentation"],
                confiance=0.92,
            )
        )
        result = service.transcrire_et_classer("Acheter du lait et du pain")
        assert result.module == "courses"
        assert result.action == "ajouter"
        assert result.destination_url == "/cuisine/courses"

    def test_classification_jardin(self, service):
        """Mémo jardin → module jardin."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="jardin",
                action="rappel",
                contenu="arroser les tomates",
                tags=["potager"],
                confiance=0.85,
            )
        )
        result = service.transcrire_et_classer("Arroser les tomates demain")
        assert result.module == "jardin"
        assert result.destination_url == "/maison/jardin"

    def test_module_invalide_normalise(self, service):
        """Module inconnu → normalisé en 'note'."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="inconnu",
                action="ajouter",
                contenu="test",
                confiance=0.7,
            )
        )
        result = service.transcrire_et_classer("Un mémo quelconque")
        assert result.module == "note"
        assert result.destination_url == "/outils/notes"

    def test_action_invalide_normalise(self, service):
        """Action inconnue → normalisée en 'ajouter'."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(
                module="maison",
                action="detruire",
                contenu="test",
                confiance=0.8,
            )
        )
        result = service.transcrire_et_classer("Quelque chose pour la maison")
        assert result.action == "ajouter"

    def test_ia_none_fallback(self, service):
        """IA retourne None → fallback avec le texte original."""
        service.call_with_parsing_sync = Mock(return_value=None)
        result = service.transcrire_et_classer("Texte quelconque")
        assert result.module == "note"
        assert result.contenu == "Texte quelconque"
        assert result.confiance == 0.3

    def test_truncate_long_text(self, service):
        """Texte très long → tronqué à 2000 caractères dans le prompt."""
        service.call_with_parsing_sync = Mock(
            return_value=MemoClassifie(module="note", action="ajouter", contenu="...", confiance=0.5)
        )
        result = service.transcrire_et_classer("a" * 5000)
        prompt = service.call_with_parsing_sync.call_args.kwargs.get(
            "prompt", service.call_with_parsing_sync.call_args[1].get("prompt", "")
        )
        # Le texte dans le prompt ne doit pas dépasser 2000 chars de l'input
        assert "a" * 2001 not in prompt

    def test_tous_modules_ont_url(self):
        """Chaque module valide a une URL destination."""
        for module in MODULES_VALIDES:
            assert module in MODULE_URLS, f"Module {module} manque dans MODULE_URLS"
