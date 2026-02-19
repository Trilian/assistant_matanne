"""
Tests pour src/modules/cuisine/batch_cooking_detaille.py

Tests du module batch cooking détaillé avec UI Streamlit mockée.
"""

from datetime import time
from unittest.mock import MagicMock, patch

import pytest

# =============================================================================
# FIXTURES
# =============================================================================


class SessionStateMock(dict):
    """Mock dict qui supporte aussi l'accès par attribut comme st.session_state."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name)


@pytest.fixture
def mock_st():
    """Mock complet de Streamlit."""
    with patch("src.modules.cuisine.batch_cooking_detaille.st") as st_mock:
        # Session state - utilise le mock dict custom
        st_mock.session_state = SessionStateMock(
            {
                "batch_type": "dimanche",
                "batch_data": {},
                "planning_data": {},
            }
        )

        # Columns context manager - return the right number based on argument
        def create_columns(n):
            cols = []
            for _ in range(n if isinstance(n, int) else len(n)):
                col = MagicMock()
                col.__enter__ = MagicMock(return_value=col)
                col.__exit__ = MagicMock(return_value=False)
                cols.append(col)
            return cols

        st_mock.columns.side_effect = create_columns

        # Container context manager
        container_mock = MagicMock()
        container_mock.__enter__ = MagicMock(return_value=container_mock)
        container_mock.__exit__ = MagicMock(return_value=False)
        st_mock.container.return_value = container_mock

        # Expander context manager
        expander_mock = MagicMock()
        expander_mock.__enter__ = MagicMock(return_value=expander_mock)
        expander_mock.__exit__ = MagicMock(return_value=False)
        st_mock.expander.return_value = expander_mock

        # Tabs context manager
        tab_mock = MagicMock()
        tab_mock.__enter__ = MagicMock(return_value=tab_mock)
        tab_mock.__exit__ = MagicMock(return_value=False)
        st_mock.tabs.return_value = [tab_mock, tab_mock, tab_mock]

        # time_input returns a proper time object
        st_mock.time_input.return_value = time(9, 0)

        yield st_mock


@pytest.fixture
def sample_planning_data():
    """Données de planning exemple."""
    return {
        "Lundi": {
            "midi": {"nom": "Pâtes bolognaise", "id": 1},
            "soir": {"nom": "Salade composée", "id": 2},
        },
        "Mardi": {
            "midi": {"nom": "Poulet rôti", "id": 3},
            "soir": {"nom": "Soupe légumes", "id": 4},
        },
    }


@pytest.fixture
def sample_batch_data():
    """Données de batch cooking exemple."""
    return {
        "session": {
            "duree_estimee_minutes": 120,
            "conseils_organisation": ["Préparer les légumes en premier", "Utiliser le Cookeo"],
        },
        "recettes": [
            {
                "nom": "Pâtes bolognaise",
                "pour_jours": ["Lundi midi"],
                "portions": 4,
                "ingredients": [
                    {
                        "nom": "carottes",
                        "quantite": 2,
                        "unite": "pièces",
                        "poids_g": 200,
                        "decoupe": "rondelles",
                        "taille_decoupe": "1cm",
                        "instruction_prep": "Éplucher et laver",
                        "jules_peut_aider": True,
                        "tache_jules": "Laver les carottes",
                    }
                ],
                "etapes_batch": [
                    {
                        "titre": "Préparer les légumes",
                        "description": "Éplucher et couper",
                        "duree_minutes": 15,
                        "est_passif": False,
                        "robot": None,
                        "jules_participation": True,
                        "tache_jules": "Aider à mélanger",
                    },
                    {
                        "titre": "Cuisson Cookeo",
                        "description": "Cuisson sous pression",
                        "duree_minutes": 20,
                        "est_passif": True,
                        "robot": {
                            "type": "cookeo",
                            "programme": "Sous pression",
                            "duree_secondes": 1200,
                        },
                        "jules_participation": False,
                    },
                ],
                "instructions_finition": ["Sortir du frigo 15min avant", "Réchauffer"],
                "stockage": "frigo",
                "duree_conservation_jours": 4,
                "temps_finition_minutes": 10,
                "version_jules": "Mixer plus finement",
            }
        ],
        "moments_jules": ["0-15min: Laver les légumes"],
        "liste_courses": {
            "fruits_legumes": [
                {"nom": "carottes", "quantite": 4, "unite": "pièces", "poids_g": 400}
            ],
            "viandes": [],
            "cremerie": [],
            "epicerie": [],
            "surgeles": [],
        },
    }


@pytest.fixture
def sample_ingredient():
    """Ingrédient exemple."""
    return {
        "nom": "oignons",
        "quantite": 3,
        "unite": "pièces",
        "poids_g": 300,
        "description": "taille moyenne",
        "decoupe": "cisele",
        "taille_decoupe": "fine",
        "instruction_prep": "Éplucher",
        "jules_peut_aider": True,
        "tache_jules": "Mettre dans le bol",
    }


@pytest.fixture
def sample_etape():
    """Étape de batch cooking exemple."""
    return {
        "titre": "Cuisson au four",
        "description": "Enfourner le gratin",
        "duree_minutes": 30,
        "est_passif": True,
        "robot": {
            "type": "four",
            "mode": "Chaleur tournante",
            "temperature": 180,
            "duree_secondes": 1800,
        },
        "jules_participation": False,
    }


# =============================================================================
# TESTS D'IMPORT
# =============================================================================


class TestImports:
    """Tests d'import du module."""

    def test_import_module(self):
        """Vérifie que le module s'importe sans erreur."""
        from src.modules.cuisine import batch_cooking_detaille

        assert batch_cooking_detaille is not None

    def test_import_app_function(self):
        """Vérifie que la fonction app() existe."""
        from src.modules.cuisine.batch_cooking_detaille import app

        assert callable(app)

    def test_import_constantes(self):
        """Vérifie que les constantes sont définies."""
        from src.modules.cuisine.batch_cooking_detaille import (
            TYPES_DECOUPE,
            TYPES_SESSION,
        )

        assert isinstance(TYPES_DECOUPE, dict)
        assert isinstance(TYPES_SESSION, dict)
        assert len(TYPES_DECOUPE) > 0
        assert len(TYPES_SESSION) > 0

    def test_import_render_functions(self):
        """Vérifie que les fonctions de rendu existent."""
        from src.modules.cuisine.batch_cooking_detaille import (
            afficher_etape_batch,
            afficher_finition_jour_j,
            afficher_ingredient_detaille,
            afficher_instruction_robot,
            afficher_liste_courses_batch,
            afficher_moments_jules,
            afficher_planning_semaine_preview,
            afficher_selecteur_session,
            afficher_timeline_session,
        )

        assert callable(afficher_selecteur_session)
        assert callable(afficher_planning_semaine_preview)
        assert callable(afficher_ingredient_detaille)
        assert callable(afficher_etape_batch)
        assert callable(afficher_instruction_robot)
        assert callable(afficher_timeline_session)
        assert callable(afficher_moments_jules)
        assert callable(afficher_liste_courses_batch)
        assert callable(afficher_finition_jour_j)

    def test_import_generer_batch_ia(self):
        """Vérifie que la fonction IA existe."""
        from src.modules.cuisine.batch_cooking_detaille import generer_batch_ia

        assert callable(generer_batch_ia)


# =============================================================================
# TESTS CONSTANTES
# =============================================================================


class TestConstantes:
    """Tests des constantes du module."""

    def test_types_decoupe_structure(self):
        """Vérifie la structure de TYPES_DECOUPE."""
        from src.modules.cuisine.batch_cooking_detaille import TYPES_DECOUPE

        for key, value in TYPES_DECOUPE.items():
            assert "label" in value
            assert "emoji" in value
            assert "description" in value

    def test_types_decoupe_values(self):
        """Vérifie les valeurs courantes de TYPES_DECOUPE."""
        from src.modules.cuisine.batch_cooking_detaille import TYPES_DECOUPE

        expected_keys = [
            "rondelles",
            "cubes",
            "julienne",
            "brunoise",
            "lamelles",
            "cisele",
            "emince",
            "rape",
        ]
        for key in expected_keys:
            assert key in TYPES_DECOUPE

    def test_types_session_structure(self):
        """Vérifie la structure de TYPES_SESSION."""
        from src.modules.cuisine.batch_cooking_detaille import TYPES_SESSION

        for key, value in TYPES_SESSION.items():
            assert "label" in value
            assert "duree_type" in value
            assert "avec_jules" in value
            assert "heure_defaut" in value
            assert "description" in value

    def test_types_session_dimanche(self):
        """Vérifie les paramètres de la session dimanche."""
        from src.modules.cuisine.batch_cooking_detaille import TYPES_SESSION

        dimanche = TYPES_SESSION.get("dimanche")
        assert dimanche is not None
        assert dimanche["avec_jules"] is True
        assert dimanche["heure_defaut"] == time(10, 0)

    def test_types_session_mercredi(self):
        """Vérifie les paramètres de la session mercredi."""
        from src.modules.cuisine.batch_cooking_detaille import TYPES_SESSION

        mercredi = TYPES_SESSION.get("mercredi")
        assert mercredi is not None
        assert mercredi["avec_jules"] is False
        assert mercredi["heure_defaut"] == time(20, 0)


# =============================================================================
# TESTS FONCTIONS RENDER
# =============================================================================


class TestRenderSelecteurSession:
    """Tests pour afficher_selecteur_session."""

    def test_render_selecteur_session(self, mock_st):
        """Teste le rendu du sélecteur de session."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_selecteur_session

        afficher_selecteur_session()

        mock_st.subheader.assert_called_once()
        mock_st.columns.assert_called_once()
        assert mock_st.button.call_count >= 2


class TestRenderPlanningPreview:
    """Tests pour afficher_planning_semaine_preview."""

    def test_render_planning_avec_donnees(self, mock_st, sample_planning_data):
        """Teste le rendu avec des données de planning."""
        from src.modules.cuisine.batch_cooking_detaille import (
            afficher_planning_semaine_preview,
        )

        afficher_planning_semaine_preview(sample_planning_data)

        mock_st.markdown.assert_called()
        # Vérifie que les jours sont affichés
        assert mock_st.container.call_count > 0

    def test_render_planning_vide(self, mock_st):
        """Teste le rendu sans données de planning."""
        from src.modules.cuisine.batch_cooking_detaille import (
            afficher_planning_semaine_preview,
        )

        afficher_planning_semaine_preview({})

        mock_st.info.assert_called_once()

    def test_render_planning_none(self, mock_st):
        """Teste le rendu avec None."""
        from src.modules.cuisine.batch_cooking_detaille import (
            afficher_planning_semaine_preview,
        )

        afficher_planning_semaine_preview(None)

        mock_st.info.assert_called_once()


class TestRenderIngredientDetaille:
    """Tests pour afficher_ingredient_detaille."""

    def test_render_ingredient_complet(self, mock_st, sample_ingredient):
        """Teste le rendu d'un ingrédient complet."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_ingredient_detaille

        afficher_ingredient_detaille(sample_ingredient, "test_key")

        mock_st.container.assert_called()
        mock_st.markdown.assert_called()

    def test_render_ingredient_minimal(self, mock_st):
        """Teste le rendu d'un ingrédient minimal."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_ingredient_detaille

        ingredient = {"nom": "sel", "quantite": 1, "unite": "pincée"}
        afficher_ingredient_detaille(ingredient, "test_key")

        mock_st.container.assert_called()

    def test_render_ingredient_jules_peut_aider(self, mock_st, sample_ingredient):
        """Teste l'affichage du badge Jules."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_ingredient_detaille

        afficher_ingredient_detaille(sample_ingredient, "test_key")

        # Jules peut aider devrait déclencher st.success
        mock_st.success.assert_called()


class TestRenderEtapeBatch:
    """Tests pour afficher_etape_batch."""

    def test_render_etape_active(self, mock_st):
        """Teste le rendu d'une étape active."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_etape_batch

        etape = {
            "titre": "Préparer les légumes",
            "description": "Éplucher et couper",
            "duree_minutes": 15,
            "est_passif": False,
        }

        afficher_etape_batch(etape, 1, "test_key")

        mock_st.container.assert_called()
        mock_st.divider.assert_called()

    def test_render_etape_passive(self, mock_st, sample_etape):
        """Teste le rendu d'une étape passive (robot)."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_etape_batch

        afficher_etape_batch(sample_etape, 1, "test_key")

        mock_st.container.assert_called()

    def test_render_etape_avec_jules(self, mock_st):
        """Teste le rendu d'une étape avec participation Jules."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_etape_batch

        etape = {
            "titre": "Mélanger",
            "description": "Mélanger les ingrédients",
            "duree_minutes": 5,
            "est_passif": False,
            "jules_participation": True,
            "tache_jules": "Remuer avec la cuillère",
        }

        afficher_etape_batch(etape, 1, "test_key")

        mock_st.success.assert_called()


class TestRenderInstructionRobot:
    """Tests pour afficher_instruction_robot."""

    def test_render_robot_cookeo(self, mock_st):
        """Teste le rendu d'instructions Cookeo."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_instruction_robot

        robot_config = {
            "type": "cookeo",
            "programme": "Sous pression",
            "duree_secondes": 1200,
        }

        afficher_instruction_robot(robot_config)

        mock_st.info.assert_called()

    def test_render_robot_monsieur_cuisine(self, mock_st):
        """Teste le rendu d'instructions Monsieur Cuisine."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_instruction_robot

        robot_config = {
            "type": "monsieur_cuisine",
            "vitesse": 5,
            "duree_secondes": 90,
            "temperature": 100,
        }

        afficher_instruction_robot(robot_config)

        mock_st.info.assert_called()

    def test_render_robot_four(self, mock_st):
        """Teste le rendu d'instructions Four."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_instruction_robot

        robot_config = {
            "type": "four",
            "mode": "Chaleur tournante",
            "temperature": 180,
            "duree_secondes": 1800,
        }

        afficher_instruction_robot(robot_config)

        mock_st.info.assert_called()

    def test_render_robot_inconnu(self, mock_st):
        """Teste le rendu d'un robot inconnu."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_instruction_robot

        robot_config = {"type": "unknown_robot"}

        afficher_instruction_robot(robot_config)

        mock_st.info.assert_called()


class TestRenderTimelineSession:
    """Tests pour afficher_timeline_session."""

    def test_render_timeline(self, mock_st):
        """Teste le rendu de la timeline."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_timeline_session

        etapes = [
            {"titre": "Préparation", "duree_minutes": 15, "est_passif": False},
            {"titre": "Cuisson", "duree_minutes": 30, "est_passif": True},
            {"titre": "Finition", "duree_minutes": 10, "est_passif": False},
        ]

        afficher_timeline_session(etapes, time(10, 0))

        mock_st.markdown.assert_called()
        mock_st.container.assert_called()

    def test_render_timeline_vide(self, mock_st):
        """Teste le rendu avec une liste vide."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_timeline_session

        afficher_timeline_session([], time(10, 0))

        mock_st.markdown.assert_called()


class TestRenderMomentsJules:
    """Tests pour afficher_moments_jules."""

    def test_render_moments_jules_avec_donnees(self, mock_st):
        """Teste le rendu des moments Jules."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_moments_jules

        moments = [
            "0-15min: Laver les légumes",
            "30-40min: Mélanger les ingrédients",
        ]

        afficher_moments_jules(moments)

        mock_st.markdown.assert_called()
        assert mock_st.success.call_count == 2

    def test_render_moments_jules_vide(self, mock_st):
        """Teste le rendu sans moments."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_moments_jules

        afficher_moments_jules([])

        mock_st.markdown.assert_not_called()

    def test_render_moments_jules_none(self, mock_st):
        """Teste le rendu avec None."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_moments_jules

        afficher_moments_jules(None)

        mock_st.markdown.assert_not_called()


class TestRenderListeCoursesBatch:
    """Tests pour afficher_liste_courses_batch."""

    def test_render_liste_courses(self, mock_st, sample_batch_data):
        """Teste le rendu de la liste de courses."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_liste_courses_batch

        afficher_liste_courses_batch(sample_batch_data["liste_courses"])

        mock_st.markdown.assert_called()
        mock_st.expander.assert_called()

    def test_render_liste_courses_vide(self, mock_st):
        """Teste le rendu avec liste vide."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_liste_courses_batch

        afficher_liste_courses_batch({})

        mock_st.markdown.assert_called()


class TestRenderFinitionJourJ:
    """Tests pour afficher_finition_jour_j."""

    def test_render_finition(self, mock_st, sample_batch_data):
        """Teste le rendu des instructions de finition."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_finition_jour_j

        recette = sample_batch_data["recettes"][0]
        afficher_finition_jour_j(recette)

        mock_st.markdown.assert_called()
        mock_st.caption.assert_called()

    def test_render_finition_avec_version_jules(self, mock_st, sample_batch_data):
        """Teste le rendu avec version Jules."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_finition_jour_j

        recette = sample_batch_data["recettes"][0]
        afficher_finition_jour_j(recette)

        mock_st.info.assert_called()


# =============================================================================
# TESTS GÉNÉRATION IA
# =============================================================================


class TestGenererBatchIA:
    """Tests pour generer_batch_ia."""

    @patch("src.modules.cuisine.batch_cooking_detaille.obtenir_client_ia")
    def test_generer_batch_ia_succes(
        self, mock_obtenir_client, mock_st, sample_planning_data, sample_batch_data
    ):
        """Teste la génération réussie des instructions batch."""
        from src.modules.cuisine.batch_cooking_detaille import generer_batch_ia

        mock_client = MagicMock()
        mock_client.generer_json.return_value = sample_batch_data
        mock_obtenir_client.return_value = mock_client

        result = generer_batch_ia(sample_planning_data, "dimanche", True)

        assert result == sample_batch_data
        mock_client.generer_json.assert_called_once()

    @patch("src.modules.cuisine.batch_cooking_detaille.obtenir_client_ia")
    def test_generer_batch_ia_client_none(self, mock_obtenir_client, mock_st, sample_planning_data):
        """Teste quand le client IA n'est pas disponible."""
        from src.modules.cuisine.batch_cooking_detaille import generer_batch_ia

        mock_obtenir_client.return_value = None

        result = generer_batch_ia(sample_planning_data, "dimanche", True)

        assert result == {}
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.batch_cooking_detaille.obtenir_client_ia")
    def test_generer_batch_ia_retourne_string_json(
        self, mock_obtenir_client, mock_st, sample_planning_data, sample_batch_data
    ):
        """Teste quand l'IA retourne une chaîne JSON."""
        import json

        from src.modules.cuisine.batch_cooking_detaille import generer_batch_ia

        mock_client = MagicMock()
        mock_client.generer_json.return_value = json.dumps(sample_batch_data)
        mock_obtenir_client.return_value = mock_client

        result = generer_batch_ia(sample_planning_data, "dimanche", True)

        assert result == sample_batch_data

    @patch("src.modules.cuisine.batch_cooking_detaille.obtenir_client_ia")
    def test_generer_batch_ia_erreur(self, mock_obtenir_client, mock_st, sample_planning_data):
        """Teste la gestion des erreurs IA."""
        from src.modules.cuisine.batch_cooking_detaille import generer_batch_ia

        mock_client = MagicMock()
        mock_client.generer_json.side_effect = Exception("Erreur API")
        mock_obtenir_client.return_value = mock_client

        result = generer_batch_ia(sample_planning_data, "dimanche", True)

        assert result == {}
        mock_st.error.assert_called()

    @patch("src.modules.cuisine.batch_cooking_detaille.obtenir_client_ia")
    def test_generer_batch_ia_session_mercredi(
        self, mock_obtenir_client, mock_st, sample_planning_data, sample_batch_data
    ):
        """Teste la génération pour une session mercredi (solo)."""
        from src.modules.cuisine.batch_cooking_detaille import generer_batch_ia

        mock_client = MagicMock()
        mock_client.generer_json.return_value = sample_batch_data
        mock_obtenir_client.return_value = mock_client

        result = generer_batch_ia(sample_planning_data, "mercredi", False)

        assert result == sample_batch_data
        # Vérifie que le prompt mentionne "solo" pour mercredi
        call_args = mock_client.generer_json.call_args
        prompt = call_args.kwargs.get("prompt") or call_args[1].get("prompt") or call_args[0][0]
        assert "solo" in prompt.lower() or "MERCREDI" in prompt


# =============================================================================
# TESTS FONCTION APP
# =============================================================================


class TestApp:
    """Tests pour la fonction app() principale."""

    def test_app_initialisation(self, mock_st):
        """Teste l'initialisation de l'app."""
        from src.modules.cuisine.batch_cooking_detaille import app

        app()

        mock_st.title.assert_called_once()
        mock_st.caption.assert_called()
        mock_st.tabs.assert_called()

    def test_app_session_state_init(self, mock_st):
        """Teste l'initialisation de la session state."""
        from src.modules.cuisine.batch_cooking_detaille import app

        # Vider la session state avec SessionStateMock
        mock_st.session_state = SessionStateMock({})

        app()

        assert "batch_type" in mock_st.session_state
        assert "batch_data" in mock_st.session_state

    def test_app_avec_planning_data(self, mock_st, sample_planning_data):
        """Teste l'app avec des données de planning."""
        from src.modules.cuisine.batch_cooking_detaille import app

        mock_st.session_state["planning_data"] = sample_planning_data

        app()

        mock_st.title.assert_called_once()

    def test_app_avec_batch_data(self, mock_st, sample_batch_data):
        """Teste l'app avec des données batch existantes."""
        from src.modules.cuisine.batch_cooking_detaille import app

        mock_st.session_state["batch_data"] = sample_batch_data

        app()

        mock_st.title.assert_called_once()

    def test_app_tabs_rendered(self, mock_st):
        """Vérifie que les trois onglets sont créés."""
        from src.modules.cuisine.batch_cooking_detaille import app

        app()

        mock_st.tabs.assert_called_once()
        call_args = mock_st.tabs.call_args[0][0]
        assert len(call_args) == 3
        assert "Préparer" in call_args[0]
        assert "Session" in call_args[1]
        assert "Finitions" in call_args[2]


# =============================================================================
# TESTS EDGE CASES
# =============================================================================


class TestEdgeCases:
    """Tests pour les cas limites."""

    def test_ingredient_sans_decoupe(self, mock_st):
        """Teste un ingrédient sans découpe."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_ingredient_detaille

        ingredient = {"nom": "huile", "quantite": 2, "unite": "cuillères"}
        afficher_ingredient_detaille(ingredient, "test_key")

        mock_st.container.assert_called()

    def test_etape_sans_robot(self, mock_st):
        """Teste une étape sans robot."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_etape_batch

        etape = {
            "titre": "Mélanger",
            "duree_minutes": 5,
            "est_passif": False,
            "robot": None,
        }

        afficher_etape_batch(etape, 1, "test_key")

        mock_st.container.assert_called()

    def test_robot_duree_secondes_conversion(self, mock_st):
        """Teste la conversion de durée en minutes."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_instruction_robot

        # Test avec durée > 60 secondes
        robot_config = {
            "type": "monsieur_cuisine",
            "vitesse": 3,
            "duree_secondes": 90,
        }

        afficher_instruction_robot(robot_config)

        call_args = mock_st.info.call_args[0][0]
        assert "1min30" in call_args or "1min" in call_args

    def test_timeline_calcul_temps(self, mock_st):
        """Teste le calcul des temps dans la timeline."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_timeline_session

        etapes = [
            {"titre": "Étape 1", "duree_minutes": 30, "est_passif": False},
            {"titre": "Étape 2", "duree_minutes": 20, "est_passif": True},
            {"titre": "Étape 3", "duree_minutes": 15, "est_passif": False},
        ]

        afficher_timeline_session(etapes, time(10, 0))

        # Le test vérifie que le calcul ne génère pas d'erreur
        mock_st.container.assert_called()

    def test_planning_preview_repas_manquant(self, mock_st):
        """Teste le preview avec repas manquant."""
        from src.modules.cuisine.batch_cooking_detaille import afficher_planning_semaine_preview

        planning = {
            "Lundi": {
                "midi": {"nom": "Pâtes"},
                # soir manquant
            }
        }

        afficher_planning_semaine_preview(planning)

        mock_st.container.assert_called()
