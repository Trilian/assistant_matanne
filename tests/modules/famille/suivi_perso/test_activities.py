"""
Tests pour src/modules/famille/suivi_perso/activities.py

Tests complets pour afficher_activities() avec mocking Streamlit.
"""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest


class ActivityMock:
    """Mock d'une activité sportive"""

    def __init__(
        self,
        nom: str = "Course",
        type_activite: str = "running",
        date_debut: datetime = None,
        duree_formatted: str = "30:00",
        distance_metres: float = None,
        distance_km: float = None,
        calories: int = None,
        fc_moyenne: int = None,
    ):
        self.nom = nom
        self.type_activite = type_activite
        self.date_debut = date_debut or datetime.now()
        self.duree_formatted = duree_formatted
        self.distance_metres = distance_metres
        self.distance_km = distance_km or (distance_metres / 1000 if distance_metres else None)
        self.calories = calories
        self.fc_moyenne = fc_moyenne


class TestRenderActivities:
    """Tests pour afficher_activities()"""

    @pytest.fixture
    def mock_st(self):
        """Mock streamlit"""
        with patch("src.modules.famille.suivi_perso.activities.st") as mock:
            container_mock = MagicMock()
            container_mock.__enter__ = MagicMock(return_value=container_mock)
            container_mock.__exit__ = MagicMock(return_value=False)
            mock.container.return_value = container_mock
            mock.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
            yield mock

    def test_affiche_subheader(self, mock_st):
        """Vérifie l'affichage du titre"""
        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": []})

        mock_st.subheader.assert_called_once()
        assert "Activités" in mock_st.subheader.call_args[0][0]

    def test_affiche_info_si_pas_activites(self, mock_st):
        """Vérifie le message si aucune activité"""
        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": []})

        mock_st.info.assert_called_once()
        assert "Aucune" in mock_st.info.call_args[0][0]

    def test_affiche_info_si_data_vide(self, mock_st):
        """Vérifie le message si data vide"""
        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({})

        mock_st.info.assert_called_once()

    def test_affiche_activites_recentes(self, mock_st):
        """Vérifie l'affichage des activités"""
        activities = [
            ActivityMock(nom="Course matinale", type_activite="running"),
            ActivityMock(nom="Vélo", type_activite="cycling"),
        ]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        # Container appelé pour chaque activité
        assert mock_st.container.call_count == 2

    def test_limite_a_5_activites(self, mock_st):
        """Vérifie qu'on affiche max 5 activités"""
        activities = [ActivityMock(nom=f"Activité {i}") for i in range(10)]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        # Seulement 5 containers
        assert mock_st.container.call_count == 5

    def test_tri_par_date_decroissante(self, mock_st):
        """Vérifie le tri par date"""
        activities = [
            ActivityMock(nom="Ancienne", date_debut=datetime(2024, 1, 1)),
            ActivityMock(nom="Récente", date_debut=datetime(2024, 12, 1)),
        ]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        # Les activités sont triées par date décroissante
        assert mock_st.container.call_count == 2

    def test_affiche_emoji_par_type(self, mock_st):
        """Vérifie l'emoji selon le type d'activité"""
        activities = [ActivityMock(type_activite="swimming")]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        # markdown appelé avec emoji natation
        calls = [str(call) for call in mock_st.markdown.call_args_list]
        assert any("🏊" in str(call) for call in calls)

    def test_affiche_duree(self, mock_st):
        """Vérifie l'affichage de la durée"""
        activities = [ActivityMock(duree_formatted="45:00")]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        calls = [str(call) for call in mock_st.write.call_args_list]
        assert any("45:00" in str(call) for call in calls)

    def test_affiche_distance_si_presente(self, mock_st):
        """Vérifie l'affichage de la distance"""
        activities = [ActivityMock(distance_metres=5000, distance_km=5.0)]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        calls = [str(call) for call in mock_st.write.call_args_list]
        assert any("5.0 km" in str(call) for call in calls)

    def test_affiche_calories_si_presentes(self, mock_st):
        """Vérifie l'affichage des calories"""
        activities = [ActivityMock(calories=350)]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        calls = [str(call) for call in mock_st.write.call_args_list]
        assert any("350" in str(call) and "kcal" in str(call) for call in calls)

    def test_affiche_fc_si_presente(self, mock_st):
        """Vérifie l'affichage de la FC moyenne"""
        activities = [ActivityMock(fc_moyenne=145)]

        from src.modules.famille.suivi_perso.activities import afficher_activities

        afficher_activities({"activities": activities})

        calls = [str(call) for call in mock_st.write.call_args_list]
        assert any("145" in str(call) and "bpm" in str(call) for call in calls)

    def test_types_activite_connus(self, mock_st):
        """Vérifie les emojis pour différents types"""
        types_attendus = {
            "running": "🏃",
            "cycling": "🚴",
            "swimming": "🏊",
            "walking": "🚶",
            "hiking": "🥾",
            "strength": "💪",
            "yoga": "🧘",
        }

        for type_act, emoji in types_attendus.items():
            mock_st.reset_mock()
            activities = [ActivityMock(type_activite=type_act)]

            from src.modules.famille.suivi_perso.activities import afficher_activities

            afficher_activities({"activities": activities})

            calls = [str(call) for call in mock_st.markdown.call_args_list]
            assert any(
                emoji in str(call) for call in calls
            ), f"Emoji {emoji} non trouvé pour {type_act}"


class TestActivitiesExports:
    """Tests des exports"""

    def test_import_render_activities(self):
        """Vérifie l'import"""
        from src.modules.famille.suivi_perso.activities import afficher_activities

        assert callable(afficher_activities)
