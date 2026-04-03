"""Tests pour DecoHabitatService — concepts déco IA et synchronisation budget."""

from unittest.mock import MagicMock, patch

import pytest

from src.services.habitat.deco_service import ConceptDecoIA, DecoHabitatService


# ═══════════════════════════════════════════════════════════
# FAKE OBJECTS
# ═══════════════════════════════════════════════════════════


class FauxProjetDeco:
    def __init__(
        self,
        id=1,
        nom_piece="Salon",
        style=None,
        budget_prevu=5000,
        budget_depense=0,
        palette_couleurs=None,
        inspirations=None,
        notes="",
    ):
        self.id = id
        self.nom_piece = nom_piece
        self.style = style
        self.budget_prevu = budget_prevu
        self.budget_depense = budget_depense
        self.palette_couleurs = palette_couleurs or []
        self.inspirations = inspirations or []
        self.notes = notes


class FauxQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, *args, **kwargs):
        return self

    def first(self):
        return self._items[0] if self._items else None


class FauxSession:
    def __init__(self, items=None):
        self._items = items or []

    def query(self, model):
        return FauxQuery(self._items)


# ═══════════════════════════════════════════════════════════
# TESTS PYDANTIC MODEL
# ═══════════════════════════════════════════════════════════


class TestConceptDecoIA:
    def test_creation_minimale(self):
        concept = ConceptDecoIA(resume="Concept chaleureux")
        assert concept.resume == "Concept chaleureux"
        assert concept.palette_couleurs == []
        assert concept.materiaux == []
        assert concept.achats_prioritaires == []
        assert concept.prompt_image is None

    def test_creation_complete(self):
        concept = ConceptDecoIA(
            resume="Style scandinave",
            palette_couleurs=["#F2E7D8", "#3E4C42"],
            materiaux=["bois clair", "lin lavé"],
            achats_prioritaires=["luminaire", "coussins"],
            prompt_image="Salon scandinave lumineux",
        )
        assert len(concept.palette_couleurs) == 2
        assert len(concept.materiaux) == 2
        assert concept.prompt_image == "Salon scandinave lumineux"


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE
# ═══════════════════════════════════════════════════════════


class TestDecoHabitatService:
    @patch("src.services.habitat.deco_service.obtenir_service_generation_image")
    def test_init(self, mock_img):
        service = DecoHabitatService()
        assert service._images is not None

    @patch("src.services.habitat.deco_service.obtenir_bus")
    @patch("src.services.habitat.deco_service.obtenir_service_generation_image")
    def test_generer_concept_projet_introuvable(self, mock_img, mock_bus):
        service = DecoHabitatService()
        session = FauxSession(items=[])

        with pytest.raises(ValueError, match="Projet deco habitat introuvable"):
            service.generer_concept(session, projet_id=999)

    @patch("src.services.habitat.deco_service.obtenir_bus")
    @patch("src.services.habitat.deco_service.obtenir_service_generation_image")
    def test_generer_concept_fallback(self, mock_img, mock_bus):
        """Quand l'IA ne répond pas, le fallback est utilisé."""
        service = DecoHabitatService()
        service.call_with_parsing_sync = MagicMock(return_value=None)

        mock_bus_instance = MagicMock()
        mock_bus.return_value = mock_bus_instance

        projet = FauxProjetDeco(id=1, nom_piece="Chambre", budget_prevu=3000)
        session = FauxSession(items=[projet])

        result = service.generer_concept(session, projet_id=1)
        assert result is not None

    @patch("src.services.habitat.deco_service.obtenir_bus")
    @patch("src.services.habitat.deco_service.obtenir_service_generation_image")
    def test_generer_concept_avec_ia(self, mock_img, mock_bus):
        """Quand l'IA fournit un concept, il est utilisé."""
        service = DecoHabitatService()

        concept_ia = ConceptDecoIA(
            resume="Chambre zen",
            palette_couleurs=["#E8DCC8"],
            materiaux=["bambou"],
            achats_prioritaires=["tatami"],
            prompt_image=None,
        )
        service.call_with_parsing_sync = MagicMock(return_value=concept_ia)

        mock_bus_instance = MagicMock()
        mock_bus.return_value = mock_bus_instance

        projet = FauxProjetDeco(id=2, nom_piece="Chambre")
        session = FauxSession(items=[projet])

        service.generer_concept(session, projet_id=2)

        assert projet.palette_couleurs == ["#E8DCC8"]
        assert "[IA] Chambre zen" in projet.notes
