"""
Tests pour la génération IA de batch cooking.

Tests avec mock du client IA.
"""

import json
from unittest.mock import MagicMock, patch

import pytest


class TestGenererBatchIA:
    """Tests pour generer_batch_ia()."""

    @patch("src.modules.cuisine.batch_cooking_detaille.generation.st")
    @patch("src.modules.cuisine.batch_cooking_detaille.generation.obtenir_client_ia")
    def test_retourne_dict_avec_reponse_valide(self, mock_client, mock_st):
        from src.modules.cuisine.batch_cooking_detaille.generation import generer_batch_ia

        response_data = {
            "session": {
                "duree_estimee_minutes": 120,
                "conseils_organisation": ["Conseil 1"],
            },
            "recettes": [
                {
                    "nom": "Soupe de légumes",
                    "pour_jours": ["Lundi midi"],
                    "portions": 4,
                    "ingredients": [],
                    "etapes_batch": [],
                    "instructions_finition": [],
                    "stockage": "frigo",
                    "duree_conservation_jours": 4,
                    "temps_finition_minutes": 5,
                }
            ],
            "moments_jules": [],
            "liste_courses": {"fruits_legumes": [], "viandes": [], "cremerie": [], "epicerie": [], "surgeles": []},
        }

        client_instance = MagicMock()
        client_instance.generer_json.return_value = response_data
        mock_client.return_value = client_instance

        planning = {"Lundi": {"midi": {"nom": "Soupe de légumes"}}}
        result = generer_batch_ia(planning, "standard", False)

        assert isinstance(result, dict)
        assert "session" in result
        assert "recettes" in result
        assert len(result["recettes"]) == 1
        assert result["recettes"][0]["nom"] == "Soupe de légumes"

    @patch("src.modules.cuisine.batch_cooking_detaille.generation.st")
    @patch("src.modules.cuisine.batch_cooking_detaille.generation.obtenir_client_ia")
    def test_avec_jules(self, mock_client, mock_st):
        from src.modules.cuisine.batch_cooking_detaille.generation import generer_batch_ia

        client_instance = MagicMock()
        client_instance.generer_json.return_value = {"session": {}, "recettes": []}
        mock_client.return_value = client_instance

        planning = {"Lundi": {"midi": {"nom": "Pasta"}}}
        result = generer_batch_ia(planning, "standard", True)

        # Vérifier que "Jules" est mentionné dans le prompt
        call_args = client_instance.generer_json.call_args
        prompt = call_args[1].get("prompt", call_args[0][0] if call_args[0] else "")
        assert "Jules" in prompt

    @patch("src.modules.cuisine.batch_cooking_detaille.generation.st")
    @patch("src.modules.cuisine.batch_cooking_detaille.generation.obtenir_client_ia")
    def test_client_none_retourne_dict_vide(self, mock_client, mock_st):
        from src.modules.cuisine.batch_cooking_detaille.generation import generer_batch_ia

        mock_client.return_value = None

        result = generer_batch_ia({}, "standard", False)
        assert result == {}

    @patch("src.modules.cuisine.batch_cooking_detaille.generation.st")
    @patch("src.modules.cuisine.batch_cooking_detaille.generation.obtenir_client_ia")
    def test_erreur_ia_retourne_dict_vide(self, mock_client, mock_st):
        from src.modules.cuisine.batch_cooking_detaille.generation import generer_batch_ia

        client_instance = MagicMock()
        client_instance.generer_json.side_effect = Exception("API Error")
        mock_client.return_value = client_instance

        result = generer_batch_ia({"Lundi": {"midi": {"nom": "Test"}}}, "rapide", False)
        assert result == {}

    @patch("src.modules.cuisine.batch_cooking_detaille.generation.st")
    @patch("src.modules.cuisine.batch_cooking_detaille.generation.obtenir_client_ia")
    def test_reponse_string_json(self, mock_client, mock_st):
        from src.modules.cuisine.batch_cooking_detaille.generation import generer_batch_ia

        response_data = {"session": {"duree_estimee_minutes": 90}, "recettes": []}

        client_instance = MagicMock()
        client_instance.generer_json.return_value = json.dumps(response_data)
        mock_client.return_value = client_instance

        result = generer_batch_ia({"Lundi": {"soir": {"nom": "Salade"}}}, "standard", False)
        assert isinstance(result, dict)
        assert result.get("session", {}).get("duree_estimee_minutes") == 90

    @patch("src.modules.cuisine.batch_cooking_detaille.generation.st")
    @patch("src.modules.cuisine.batch_cooking_detaille.generation.obtenir_client_ia")
    def test_planning_multiple_jours(self, mock_client, mock_st):
        from src.modules.cuisine.batch_cooking_detaille.generation import generer_batch_ia

        client_instance = MagicMock()
        client_instance.generer_json.return_value = {"session": {}, "recettes": []}
        mock_client.return_value = client_instance

        planning = {
            "Lundi": {"midi": {"nom": "Soupe"}, "soir": {"nom": "Gratin"}},
            "Mardi": {"midi": {"nom": "Salade"}},
            "Mercredi": {"soir": {"nom": "Pasta"}},
        }

        result = generer_batch_ia(planning, "weekend", True)
        assert isinstance(result, dict)

        # Vérifier que toutes les recettes sont dans le prompt
        call_args = client_instance.generer_json.call_args
        prompt = call_args[1].get("prompt", call_args[0][0] if call_args[0] else "")
        assert "Soupe" in prompt
        assert "Gratin" in prompt
        assert "Salade" in prompt
        assert "Pasta" in prompt
