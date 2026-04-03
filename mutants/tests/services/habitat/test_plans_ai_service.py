"""Tests pour PlansHabitatAIService — analyse de plans et suggestions IA."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from src.services.habitat.plans_ai_service import (
    AnalysePlanIA,
    PlansHabitatAIService,
    SuggestionPieceIA,
)


# ═══════════════════════════════════════════════════════════
# FAKE OBJECTS
# ═══════════════════════════════════════════════════════════


class FauxPlan:
    def __init__(self, id=1, image_importee_url=None, scenario_id=None):
        self.id = id
        self.image_importee_url = image_importee_url
        self.scenario_id = scenario_id


class FauxPiece:
    def __init__(self, plan_id=1, nom="Salon", type_piece="sejour", surface=25.0):
        self.plan_id = plan_id
        self.nom = nom
        self.type_piece = type_piece
        self.surface = surface


class FauxQuery:
    def __init__(self, items):
        self._items = items

    def filter(self, *args, **kwargs):
        return self

    def all(self):
        return self._items

    def first(self):
        return self._items[0] if self._items else None


class FauxSession:
    def __init__(self, plans=None, pieces=None):
        self._plans = plans or []
        self._pieces = pieces or []
        self._call_count = 0

    def query(self, model):
        self._call_count += 1
        if self._call_count == 1:
            return FauxQuery(self._plans)
        return FauxQuery(self._pieces)


# ═══════════════════════════════════════════════════════════
# TESTS PYDANTIC MODELS
# ═══════════════════════════════════════════════════════════


class TestSuggestionPieceIA:
    def test_creation_minimale(self):
        sugg = SuggestionPieceIA(nom="Cuisine", type_piece="cuisine")
        assert sugg.nom == "Cuisine"
        assert sugg.type_piece == "cuisine"
        assert sugg.surface_m2 is None
        assert sugg.actions == []

    def test_creation_complete(self):
        sugg = SuggestionPieceIA(
            nom="Chambre",
            type_piece="chambre",
            surface_m2=12.5,
            actions=["Ajouter rangements", "Repeindre"],
        )
        assert sugg.surface_m2 == 12.5
        assert len(sugg.actions) == 2


class TestAnalysePlanIA:
    def test_creation_vide(self):
        analyse = AnalysePlanIA(resume="Petit appartement bien agencé")
        assert analyse.resume == "Petit appartement bien agencé"
        assert analyse.points_forts == []
        assert analyse.risques == []
        assert analyse.budget_estime is None
        assert analyse.circulation_note is None
        assert analyse.suggestions_pieces == []
        assert analyse.prompt_image is None

    def test_creation_complete(self):
        analyse = AnalysePlanIA(
            resume="Maison 100m²",
            points_forts=["Lumineux", "Bon agencement"],
            risques=["Isolation faible"],
            budget_estime=15000.0,
            circulation_note=8.5,
            suggestions_pieces=[
                SuggestionPieceIA(nom="Bureau", type_piece="bureau", surface_m2=9.0)
            ],
            prompt_image="Intérieur rénové lumineux",
        )
        assert analyse.circulation_note == 8.5
        assert len(analyse.suggestions_pieces) == 1

    def test_circulation_note_validation(self):
        with pytest.raises(Exception):
            AnalysePlanIA(resume="test", circulation_note=15.0)

        with pytest.raises(Exception):
            AnalysePlanIA(resume="test", circulation_note=-1.0)


# ═══════════════════════════════════════════════════════════
# TESTS SERVICE
# ═══════════════════════════════════════════════════════════


class TestPlansHabitatAIService:
    @patch("src.services.habitat.plans_ai_service.obtenir_multimodal_service")
    @patch("src.services.habitat.plans_ai_service.obtenir_service_generation_image")
    def test_init(self, mock_img, mock_multi):
        service = PlansHabitatAIService()
        assert service._multimodal is not None
        assert service._images is not None

    @patch("src.services.habitat.plans_ai_service.obtenir_multimodal_service")
    @patch("src.services.habitat.plans_ai_service.obtenir_service_generation_image")
    def test_charger_plan_existe(self, mock_img, mock_multi):
        service = PlansHabitatAIService()
        plan = FauxPlan(id=1)
        pieces = [FauxPiece(plan_id=1, nom="Salon"), FauxPiece(plan_id=1, nom="Cuisine")]
        session = FauxSession(plans=[plan], pieces=pieces)

        loaded_plan, loaded_pieces = service._charger_plan(session, 1)
        assert loaded_plan.id == 1
        assert len(loaded_pieces) == 2

    @patch("src.services.habitat.plans_ai_service.obtenir_multimodal_service")
    @patch("src.services.habitat.plans_ai_service.obtenir_service_generation_image")
    def test_charger_plan_introuvable(self, mock_img, mock_multi):
        service = PlansHabitatAIService()
        session = FauxSession(plans=[], pieces=[])

        with pytest.raises(ValueError, match="Plan habitat introuvable"):
            service._charger_plan(session, 999)

    @patch("src.services.habitat.plans_ai_service.obtenir_multimodal_service")
    @patch("src.services.habitat.plans_ai_service.obtenir_service_generation_image")
    def test_extraire_contexte_image_url_invalide(self, mock_img, mock_multi):
        service = PlansHabitatAIService()
        assert service._extraire_contexte_image(None) is None
        assert service._extraire_contexte_image("") is None
        assert service._extraire_contexte_image("fichier_local.jpg") is None

    @patch("src.services.habitat.plans_ai_service.obtenir_multimodal_service")
    @patch("src.services.habitat.plans_ai_service.obtenir_service_generation_image")
    @patch("src.services.habitat.plans_ai_service.httpx.Client")
    def test_extraire_contexte_image_erreur_reseau(self, mock_client_cls, mock_img, mock_multi):
        service = PlansHabitatAIService()
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = Exception("timeout")
        mock_client_cls.return_value = mock_client

        result = service._extraire_contexte_image("https://example.com/plan.jpg")
        assert result is None
