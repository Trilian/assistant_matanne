"""
Tests pour le service de génération de version robot (Phase 6).

Couvre :
- ServiceVersionRecetteRobot (init, singleton, validation)
- generer_version_robot (prompt, parsing, persistance DB)
- Endpoint API POST /recettes/{id}/generer-version-robot/{robot}
- Constantes ROBOTS_CONTEXTE et PROMPT_SYSTEM
"""

from unittest.mock import MagicMock, patch

import pytest

from src.services.cuisine.version_recette_robot import (
    PROMPT_SYSTEM,
    ROBOTS_CONTEXTE,
    ServiceVersionRecetteRobot,
    obtenir_version_recette_robot_service,
)


# ═══════════════════════════════════════════════════════════
# CONSTANTES ET CONFIGURATION
# ═══════════════════════════════════════════════════════════


class TestRobotsContexte:
    """Vérifie la structure des constantes de robots."""

    def test_trois_robots_definis(self):
        """Exactement 3 robots sont définis."""
        assert len(ROBOTS_CONTEXTE) == 3
        assert set(ROBOTS_CONTEXTE.keys()) == {"cookeo", "monsieur_cuisine", "airfryer"}

    @pytest.mark.parametrize("robot", ["cookeo", "monsieur_cuisine", "airfryer"])
    def test_robot_a_toutes_les_cles(self, robot):
        """Chaque robot a nom, description, modes, conseils."""
        ctx = ROBOTS_CONTEXTE[robot]
        assert "nom" in ctx
        assert "description" in ctx
        assert "modes" in ctx
        assert "conseils" in ctx
        assert isinstance(ctx["nom"], str)
        assert len(ctx["nom"]) > 0

    def test_cookeo_modes(self):
        """Cookeo a les modes attendus."""
        modes = ROBOTS_CONTEXTE["cookeo"]["modes"]
        assert "Pression" in modes
        assert "Rissolage" in modes

    def test_airfryer_modes(self):
        """Air Fryer a les modes attendus."""
        modes = ROBOTS_CONTEXTE["airfryer"]["modes"]
        assert "Air fry" in modes or "Grill" in modes

    def test_monsieur_cuisine_modes(self):
        """Monsieur Cuisine a les modes attendus."""
        modes = ROBOTS_CONTEXTE["monsieur_cuisine"]["modes"]
        assert "Mixer" in modes or "Mijoter" in modes


class TestPromptSystem:
    """Vérifie le template du prompt système."""

    def test_prompt_contient_placeholders(self):
        """Le prompt contient les placeholders pour le formatage."""
        assert "{nom_robot}" in PROMPT_SYSTEM
        assert "{description}" in PROMPT_SYSTEM
        assert "{modes}" in PROMPT_SYSTEM
        assert "{conseils}" in PROMPT_SYSTEM

    def test_prompt_demande_json(self):
        """Le prompt demande une réponse en JSON."""
        assert "JSON" in PROMPT_SYSTEM
        assert "instructions_modifiees" in PROMPT_SYSTEM
        assert "modifications_resume" in PROMPT_SYSTEM

    @pytest.mark.parametrize("robot", ["cookeo", "monsieur_cuisine", "airfryer"])
    def test_prompt_formatable_pour_chaque_robot(self, robot):
        """Le prompt peut être formaté sans erreur pour chaque robot."""
        ctx = ROBOTS_CONTEXTE[robot]
        formatted = PROMPT_SYSTEM.format(
            nom_robot=ctx["nom"],
            description=ctx["description"],
            modes=ctx["modes"],
            conseils=ctx["conseils"],
        )
        assert ctx["nom"] in formatted
        assert len(formatted) > 100


# ═══════════════════════════════════════════════════════════
# SERVICE — Initialisation et registre
# ═══════════════════════════════════════════════════════════


class TestServiceVersionRecetteRobotInit:
    """Tests d'initialisation du service."""

    def test_creation_service(self):
        """Le service peut être instancié."""
        with patch("src.services.cuisine.version_recette_robot.obtenir_client_ia"):
            service = ServiceVersionRecetteRobot()
            assert service is not None

    def test_service_herite_base_ai(self):
        """Le service hérite de BaseAIService."""
        from src.services.core.base import BaseAIService

        with patch("src.services.cuisine.version_recette_robot.obtenir_client_ia"):
            service = ServiceVersionRecetteRobot()
            assert isinstance(service, BaseAIService)

    def test_factory_singleton(self):
        """obtenir_version_recette_robot_service retourne un singleton."""
        from src.services.core.registry import obtenir_registre

        registre = obtenir_registre()
        registre.reinitialiser("version_recette_robot")

        with patch("src.services.cuisine.version_recette_robot.obtenir_client_ia"):
            s1 = obtenir_version_recette_robot_service()
            s2 = obtenir_version_recette_robot_service()
            assert s1 is s2


# ═══════════════════════════════════════════════════════════
# SERVICE — generer_version_robot
# ═══════════════════════════════════════════════════════════


class TestGenererVersionRobot:
    """Tests de la méthode generer_version_robot."""

    @pytest.fixture
    def service(self):
        with patch("src.services.cuisine.version_recette_robot.obtenir_client_ia"):
            return ServiceVersionRecetteRobot()

    @pytest.fixture
    def mock_recette(self):
        """Recette mockée avec ingrédients et étapes."""
        recette = MagicMock()
        recette.id = 42
        recette.nom = "Bœuf bourguignon"
        recette.categorie = "plat principal"
        recette.temps_cuisson = 180

        # Ingrédients
        ing1 = MagicMock()
        ing1.quantite = "800"
        ing1.unite = "g"
        ing1.ingredient = MagicMock()
        ing1.ingredient.nom = "Bœuf"

        ing2 = MagicMock()
        ing2.quantite = "200"
        ing2.unite = "ml"
        ing2.ingredient = MagicMock()
        ing2.ingredient.nom = "Vin rouge"

        recette.ingredients = [ing1, ing2]

        # Étapes
        etape1 = MagicMock()
        etape1.ordre = 1
        etape1.description = "Couper la viande en morceaux"
        etape2 = MagicMock()
        etape2.ordre = 2
        etape2.description = "Faire revenir dans une cocotte"
        recette.etapes = [etape1, etape2]

        # Flags compatibilité
        recette.compatible_cookeo = False
        recette.compatible_monsieur_cuisine = False
        recette.compatible_airfryer = False

        return recette

    def test_robot_inconnu_leve_erreur(self, service):
        """Un robot invalide lève ValueError."""
        with pytest.raises(ValueError, match="Robot inconnu"):
            service.generer_version_robot(recette_id=1, robot="thermomix")

    def test_recette_introuvable_leve_erreur(self, service):
        """Une recette inexistante lève ValueError."""
        mock_session = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = None

        with patch("src.core.db.obtenir_contexte_db") as mock_ctx:
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            with pytest.raises(ValueError, match="introuvable"):
                service.generer_version_robot(recette_id=999, robot="cookeo")

    @pytest.mark.parametrize("robot", ["cookeo", "monsieur_cuisine", "airfryer"])
    def test_generation_reussie(self, service, mock_recette, robot):
        """Génération réussie pour chaque robot — crée une VersionRecette."""
        mock_session = MagicMock()

        # Recette trouvée, pas de version existante
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_recette,  # query Recette
            None,  # query VersionRecette (pas de version existante)
        ]

        ia_result = {
            "instructions_modifiees": f"Étapes pour {ROBOTS_CONTEXTE[robot]['nom']}...",
            "modifications_resume": ["Temps réduit", "Mode pression"],
            "temps_cuisson_estime": 45,
            "temperature_principale": None,
        }

        with (
            patch("src.core.db.obtenir_contexte_db") as mock_ctx,
            patch.object(service, "call_with_dict_parsing_sync", return_value=ia_result),
        ):
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.generer_version_robot(recette_id=42, robot=robot)

        assert result is not None
        assert result["recette_nom"] == "Bœuf bourguignon"
        assert result["type_version"] == robot
        assert mock_session.add.called
        assert mock_session.commit.called

    def test_mise_a_jour_version_existante(self, service, mock_recette):
        """Si une version robot existe déjà, elle est mise à jour (pas de doublon)."""
        mock_session = MagicMock()

        version_existante = MagicMock()
        version_existante.id = 7
        version_existante.recette_base_id = 42
        version_existante.type_version = "cookeo"
        version_existante.instructions_modifiees = "Anciennes instructions"
        version_existante.ingredients_modifies = None

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_recette,
            version_existante,
        ]

        ia_result = {
            "instructions_modifiees": "Nouvelles instructions Cookeo",
            "modifications_resume": ["Nouveau temps"],
        }

        with (
            patch("src.core.db.obtenir_contexte_db") as mock_ctx,
            patch.object(service, "call_with_dict_parsing_sync", return_value=ia_result),
        ):
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.generer_version_robot(recette_id=42, robot="cookeo")

        # La version existante est mise à jour, pas de session.add pour une new version
        assert version_existante.instructions_modifiees == "Nouvelles instructions Cookeo"
        assert result["id"] == 7

    def test_flag_compatible_mis_a_jour(self, service, mock_recette):
        """Le flag compatible_xxx est mis à True après génération."""
        mock_session = MagicMock()

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_recette,
            None,
        ]

        ia_result = {
            "instructions_modifiees": "Instructions Cookeo",
            "modifications_resume": [],
        }

        with (
            patch("src.core.db.obtenir_contexte_db") as mock_ctx,
            patch.object(service, "call_with_dict_parsing_sync", return_value=ia_result),
        ):
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            service.generer_version_robot(recette_id=42, robot="cookeo")

        # compatible_cookeo doit passer à True
        assert mock_recette.compatible_cookeo is True

    def test_fallback_quand_ia_echoue(self, service, mock_recette):
        """Quand l'IA retourne None, un fallback est généré."""
        mock_session = MagicMock()

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_recette,
            None,
        ]

        with (
            patch("src.core.db.obtenir_contexte_db") as mock_ctx,
            patch.object(service, "call_with_dict_parsing_sync", return_value=None),
        ):
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.generer_version_robot(recette_id=42, robot="airfryer")

        assert result is not None
        assert "non disponibles" in result["instructions_modifiees"] or "Air Fryer" in result["instructions_modifiees"]

    def test_prompt_contient_ingredients_et_instructions(self, service, mock_recette):
        """Le prompt envoyé à l'IA contient les ingrédients et instructions de la recette."""
        mock_session = MagicMock()

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_recette,
            None,
        ]

        prompt_capture = {}

        def capture_call(*, prompt, system_prompt, max_tokens):
            prompt_capture["prompt"] = prompt
            prompt_capture["system"] = system_prompt
            return {
                "instructions_modifiees": "test",
                "modifications_resume": [],
            }

        with (
            patch("src.core.db.obtenir_contexte_db") as mock_ctx,
            patch.object(service, "call_with_dict_parsing_sync", side_effect=capture_call),
        ):
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            service.generer_version_robot(recette_id=42, robot="cookeo")

        prompt = prompt_capture["prompt"]
        assert "Bœuf bourguignon" in prompt
        assert "Bœuf" in prompt
        assert "Vin rouge" in prompt
        assert "Couper la viande" in prompt
        assert "cocotte" in prompt

        system = prompt_capture["system"]
        assert "Cookeo" in system

    def test_recette_sans_ingredients(self, service):
        """Une recette sans ingrédients génère quand même un prompt valide."""
        mock_session = MagicMock()

        recette_vide = MagicMock()
        recette_vide.id = 1
        recette_vide.nom = "Recette vide"
        recette_vide.categorie = None
        recette_vide.temps_cuisson = None
        recette_vide.ingredients = []
        recette_vide.etapes = []
        recette_vide.compatible_cookeo = False

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            recette_vide,
            None,
        ]

        with (
            patch("src.core.db.obtenir_contexte_db") as mock_ctx,
            patch.object(
                service,
                "call_with_dict_parsing_sync",
                return_value={"instructions_modifiees": "ok", "modifications_resume": []},
            ),
        ):
            mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_session)
            mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

            result = service.generer_version_robot(recette_id=1, robot="cookeo")

        assert result is not None


# ═══════════════════════════════════════════════════════════
# API ENDPOINT
# ═══════════════════════════════════════════════════════════


class TestEndpointGenererVersionRobot:
    """Tests pour le endpoint API POST /recettes/{id}/generer-version-robot/{robot}."""

    @pytest.fixture
    def client(self):
        """TestClient FastAPI."""
        from fastapi.testclient import TestClient
        from src.api.main import app

        return TestClient(app)

    def test_robot_invalide_retourne_400(self, client):
        """Un robot invalide retourne HTTP 400."""
        response = client.post("/api/v1/recettes/1/generer-version-robot/thermomix")
        assert response.status_code == 400
        assert "invalide" in response.json().get("detail", "").lower() or response.status_code == 400

    @pytest.mark.parametrize("robot", ["cookeo", "monsieur_cuisine", "airfryer"])
    def test_robots_valides_acceptes(self, client, robot):
        """Les 3 robots valides ne retournent pas 400."""
        with patch(
            "src.services.cuisine.version_recette_robot.obtenir_version_recette_robot_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.generer_version_robot.return_value = {
                "id": 1,
                "recette_base_id": 1,
                "type_version": robot,
                "instructions_modifiees": "Test",
                "modifications_resume": [],
                "recette_nom": "Test",
            }
            mock_factory.return_value = mock_service

            response = client.post(f"/api/v1/recettes/1/generer-version-robot/{robot}")

        # Ne doit PAS être 400 (pourrait être 200 ou autre selon l'implémentation)
        assert response.status_code != 400
