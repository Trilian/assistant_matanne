"""
Tests for weekend/components.py - Weekend planning UI components
"""

from datetime import date, time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


class SessionStateMock(dict):
    """Mock for st.session_state that behaves like a dict with attribute access"""

    def __getattr__(self, name: str) -> Any:
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value


def setup_mock_st(mock_st: MagicMock, session_data: dict | None = None) -> None:
    """Setup mock streamlit with common components"""

    def mock_columns(n, **kwargs):
        count = n if isinstance(n, int) else len(n)
        return [MagicMock() for _ in range(count)]

    mock_st.columns.side_effect = mock_columns
    mock_st.session_state = SessionStateMock(session_data or {})
    mock_st.tabs.return_value = [MagicMock() for _ in range(4)]
    mock_st.button.return_value = False
    mock_st.form.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.form.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.form_submit_button.return_value = False
    mock_st.container.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.container.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.spinner.return_value.__enter__ = MagicMock(return_value=MagicMock())
    mock_st.spinner.return_value.__exit__ = MagicMock(return_value=False)
    mock_st.selectbox.return_value = "Tous"
    mock_st.text_input.return_value = ""
    mock_st.text_area.return_value = ""
    mock_st.number_input.return_value = 0.0
    mock_st.slider.return_value = 50
    mock_st.checkbox.return_value = True
    mock_st.date_input.return_value = date.today()
    mock_st.time_input.return_value = time(10, 0)


# ═══════════════════════════════════════════════════════════
# TESTS D'IMPORT
# ═══════════════════════════════════════════════════════════


class TestImports:
    """Verify module imports work"""

    def test_import_render_planning(self) -> None:
        from src.modules.famille.weekend.components import render_planning

        assert callable(render_planning)

    def test_import_render_day_activities(self) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        assert callable(render_day_activities)

    def test_import_render_suggestions(self) -> None:
        from src.modules.famille.weekend.components import render_suggestions

        assert callable(render_suggestions)

    def test_import_render_lieux_testes(self) -> None:
        from src.modules.famille.weekend.components import render_lieux_testes

        assert callable(render_lieux_testes)

    def test_import_render_add_activity(self) -> None:
        from src.modules.famille.weekend.components import render_add_activity

        assert callable(render_add_activity)

    def test_import_render_noter_sortie(self) -> None:
        from src.modules.famille.weekend.components import render_noter_sortie

        assert callable(render_noter_sortie)


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_PLANNING
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderPlanning:
    """Tests for render_planning function"""

    @patch("src.modules.famille.weekend.components.get_budget_weekend")
    @patch("src.modules.famille.weekend.components.render_day_activities")
    @patch("src.modules.famille.weekend.components.get_weekend_activities")
    @patch("src.modules.famille.weekend.components.get_next_weekend")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_planning_basic(
        self, mock_st, mock_next, mock_activities, mock_day, mock_budget
    ) -> None:
        from src.modules.famille.weekend.components import render_planning

        setup_mock_st(mock_st)
        mock_next.return_value = (date(2026, 2, 21), date(2026, 2, 22))
        mock_activities.return_value = {"saturday": [], "sunday": []}
        mock_budget.return_value = {"estime": 100, "reel": 50}

        render_planning()

        mock_st.subheader.assert_called()
        mock_st.metric.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_DAY_ACTIVITIES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderDayActivities:
    """Tests for render_day_activities function"""

    @patch("src.modules.famille.weekend.components.st")
    def test_render_day_activities_empty(self, mock_st) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        setup_mock_st(mock_st)

        render_day_activities(date(2026, 2, 21), [])

        mock_st.caption.assert_called()

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.st")
    def test_render_day_activities_with_activities(self, mock_st) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        setup_mock_st(mock_st)
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.type_activite = "parc"
        mock_activity.titre = "Parc"
        mock_activity.lieu = "Jardin des Plantes"
        mock_activity.heure_debut = "14:00"
        mock_activity.cout_estime = 0
        mock_activity.statut = "planifie"

        render_day_activities(date(2026, 2, 21), [mock_activity])

        mock_st.markdown.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_SUGGESTIONS
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderSuggestions:
    """Tests for render_suggestions function"""

    @patch("src.modules.famille.weekend.components.get_age_jules_mois")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_suggestions_ui(self, mock_st, mock_age) -> None:
        from src.modules.famille.weekend.components import render_suggestions

        setup_mock_st(mock_st)
        mock_age.return_value = 20

        render_suggestions()

        mock_st.subheader.assert_called()
        mock_st.selectbox.assert_called()
        mock_st.slider.assert_called()
        mock_st.text_input.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_LIEUX_TESTES
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderLieuxTestes:
    """Tests for render_lieux_testes function"""

    @patch("src.modules.famille.weekend.components.get_lieux_testes")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_lieux_testes_empty(self, mock_st, mock_lieux) -> None:
        from src.modules.famille.weekend.components import render_lieux_testes

        setup_mock_st(mock_st)
        mock_lieux.return_value = []

        render_lieux_testes()

        mock_st.subheader.assert_called()
        mock_st.info.assert_called()

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.get_lieux_testes")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_lieux_testes_with_items(self, mock_st, mock_lieux) -> None:
        from src.modules.famille.weekend.components import render_lieux_testes

        setup_mock_st(mock_st)
        mock_lieu = MagicMock()
        mock_lieu.type_activite = "parc"
        mock_lieu.titre = "Parc Floral"
        mock_lieu.lieu = "Vincennes"
        mock_lieu.commentaire = "Super avec enfant"
        mock_lieu.note_lieu = 4
        mock_lieu.a_refaire = True
        mock_lieu.cout_reel = 5.0
        mock_lieu.date_prevue = date(2026, 2, 15)
        mock_lieux.return_value = [mock_lieu]

        render_lieux_testes()

        mock_st.selectbox.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_ADD_ACTIVITY
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderAddActivity:
    """Tests for render_add_activity function"""

    @patch("src.modules.famille.weekend.components.get_next_weekend")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_add_activity_form(self, mock_st, mock_weekend) -> None:
        from src.modules.famille.weekend.components import render_add_activity

        setup_mock_st(mock_st)
        mock_weekend.return_value = (date(2026, 2, 21), date(2026, 2, 22))

        render_add_activity()

        mock_st.subheader.assert_called()
        mock_st.form.assert_called()
        mock_st.text_input.assert_called()

    @patch("src.modules.famille.weekend.components.get_next_weekend")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_add_activity_submit_empty_title(self, mock_st, mock_weekend) -> None:
        from src.modules.famille.weekend.components import render_add_activity

        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = ""
        mock_weekend.return_value = (date(2026, 2, 21), date(2026, 2, 22))

        render_add_activity()

        mock_st.error.assert_called()


# ═══════════════════════════════════════════════════════════
# TESTS RENDER_NOTER_SORTIE
# ═══════════════════════════════════════════════════════════


@pytest.mark.unit
class TestRenderNoterSortie:
    """Tests for render_noter_sortie function"""

    @patch("src.modules.famille.weekend.components.obtenir_contexte_db")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_noter_sortie_no_activities(self, mock_st, mock_ctx) -> None:
        from src.modules.famille.weekend.components import render_noter_sortie

        setup_mock_st(mock_st)
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = []
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        render_noter_sortie()

        mock_st.subheader.assert_called()
        mock_st.info.assert_called()

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.obtenir_contexte_db")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_noter_sortie_with_activities(self, mock_st, mock_ctx) -> None:
        from src.modules.famille.weekend.components import render_noter_sortie

        setup_mock_st(mock_st)
        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.type_activite = "parc"
        mock_activity.titre = "Test"
        mock_activity.date_prevue = date(2026, 2, 15)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_activity]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        render_noter_sortie()

        mock_st.markdown.assert_called()
        mock_st.slider.assert_called()

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.obtenir_contexte_db")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_noter_sortie_save_button(self, mock_st, mock_ctx) -> None:
        """Test saving a rating via the save button (lines 279-288)"""
        from src.modules.famille.weekend.components import render_noter_sortie

        setup_mock_st(mock_st)
        mock_st.slider.return_value = 4
        mock_st.checkbox.return_value = True
        mock_st.number_input.return_value = 25.0
        mock_st.text_input.return_value = "Great place!"
        mock_st.button.return_value = True

        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.type_activite = "parc"
        mock_activity.titre = "Test"
        mock_activity.date_prevue = date(2026, 2, 15)

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_activity]
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        render_noter_sortie()

        assert mock_activity.note_lieu == 4
        assert mock_activity.a_refaire is True
        mock_db.commit.assert_called()
        mock_st.success.assert_called()


@pytest.mark.unit
class TestRenderDayActivitiesAddButton:
    """Tests for add button in render_day_activities (lines 54-56)"""

    @patch("src.modules.famille.weekend.components.st")
    def test_render_day_activities_add_button_click(self, mock_st) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        setup_mock_st(mock_st)
        mock_st.button.return_value = True

        test_date = date(2026, 2, 21)
        render_day_activities(test_date, [])

        assert mock_st.session_state["weekend_add_date"] == test_date
        assert mock_st.session_state["weekend_tab"] == "add"
        mock_st.rerun.assert_called()


@pytest.mark.unit
class TestRenderDayActivitiesDoneButton:
    """Tests for done button in render_day_activities (lines 76-82)"""

    @patch("src.modules.famille.weekend.components.mark_activity_done")
    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.st")
    def test_render_day_activities_done_button_click(self, mock_st, mock_mark_done) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        setup_mock_st(mock_st)
        mock_st.button.return_value = True

        mock_activity = MagicMock()
        mock_activity.id = 42
        mock_activity.type_activite = "parc"
        mock_activity.titre = "Parc"
        mock_activity.lieu = None
        mock_activity.heure_debut = "14:00"
        mock_activity.cout_estime = None
        mock_activity.statut = "planifie"

        render_day_activities(date(2026, 2, 21), [mock_activity])

        mock_mark_done.assert_called_with(42)
        mock_st.rerun.assert_called()

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.st")
    def test_render_day_activities_completed_with_rating(self, mock_st) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        setup_mock_st(mock_st)

        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.type_activite = "parc"
        mock_activity.titre = "Parc Test"
        mock_activity.lieu = "Paris"
        mock_activity.heure_debut = "10:00"
        mock_activity.cout_estime = 15.0
        mock_activity.statut = "termine"
        mock_activity.note_lieu = 4

        render_day_activities(date(2026, 2, 21), [mock_activity])

        mock_st.write.assert_called_with("⭐⭐⭐⭐")

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.st")
    def test_render_day_activities_completed_no_rating(self, mock_st) -> None:
        from src.modules.famille.weekend.components import render_day_activities

        setup_mock_st(mock_st)

        mock_activity = MagicMock()
        mock_activity.id = 1
        mock_activity.type_activite = "parc"
        mock_activity.titre = "Parc"
        mock_activity.lieu = None
        mock_activity.heure_debut = None
        mock_activity.cout_estime = None
        mock_activity.statut = "termine"
        mock_activity.note_lieu = None

        render_day_activities(date(2026, 2, 21), [mock_activity])

        mock_st.caption.assert_called_with("✅ Fait")


@pytest.mark.unit
class TestRenderSuggestionsGenerate:
    """Tests for generate button in render_suggestions (lines 104-121)"""

    @patch("src.modules.famille.weekend.components.WeekendAIService")
    @patch("src.modules.famille.weekend.components.get_age_jules_mois")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_suggestions_generate_success(self, mock_st, mock_age, mock_ai_service) -> None:
        from src.modules.famille.weekend.components import render_suggestions

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_st.selectbox.return_value = "ensoleille"
        mock_st.slider.return_value = 50
        mock_st.text_input.return_value = "Paris"
        mock_age.return_value = 20

        mock_service_instance = MagicMock()
        mock_ai_service.return_value = mock_service_instance

        async def mock_suggest(*args, **kwargs):
            return "Suggestion: Visiter le Jardin"

        mock_service_instance.suggerer_activites = mock_suggest

        render_suggestions()

        mock_st.markdown.assert_called()
        mock_st.info.assert_called()

    @patch("src.modules.famille.weekend.components.WeekendAIService")
    @patch("src.modules.famille.weekend.components.get_age_jules_mois")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_suggestions_generate_error(self, mock_st, mock_age, mock_ai_service) -> None:
        from src.modules.famille.weekend.components import render_suggestions

        setup_mock_st(mock_st)
        mock_st.button.return_value = True
        mock_age.return_value = 20
        mock_ai_service.side_effect = Exception("API Error")

        render_suggestions()

        mock_st.error.assert_called()


@pytest.mark.unit
class TestRenderLieuxTestesFilter:
    """Tests for filter in render_lieux_testes (line 140)"""

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {
            "parc": {"emoji": "🌳", "label": "Parc"},
            "musee": {"emoji": "🏛️", "label": "Musée"},
            "autre": {"emoji": "📌", "label": "Autre"},
        },
    )
    @patch("src.modules.famille.weekend.components.get_lieux_testes")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_lieux_filter_by_type(self, mock_st, mock_lieux) -> None:
        from src.modules.famille.weekend.components import render_lieux_testes

        setup_mock_st(mock_st)
        mock_st.selectbox.return_value = "musee"

        mock_lieu1 = MagicMock()
        mock_lieu1.type_activite = "parc"
        mock_lieu1.titre = "Parc Floral"
        mock_lieu1.lieu = "Vincennes"
        mock_lieu1.commentaire = None
        mock_lieu1.note_lieu = 4
        mock_lieu1.a_refaire = True
        mock_lieu1.cout_reel = None
        mock_lieu1.date_prevue = date(2026, 2, 15)

        mock_lieu2 = MagicMock()
        mock_lieu2.type_activite = "musee"
        mock_lieu2.titre = "Louvre"
        mock_lieu2.lieu = "Paris"
        mock_lieu2.commentaire = "Magnifique"
        mock_lieu2.note_lieu = 5
        mock_lieu2.a_refaire = True
        mock_lieu2.cout_reel = 20.0
        mock_lieu2.date_prevue = date(2026, 2, 10)

        mock_lieux.return_value = [mock_lieu1, mock_lieu2]

        render_lieux_testes()

        mock_st.selectbox.assert_called()

    @patch(
        "src.modules.famille.weekend.components.TYPES_ACTIVITES",
        {"parc": {"emoji": "🌳", "label": "Parc"}, "autre": {"emoji": "📌", "label": "Autre"}},
    )
    @patch("src.modules.famille.weekend.components.get_lieux_testes")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_lieux_with_a_refaire_false(self, mock_st, mock_lieux) -> None:
        from src.modules.famille.weekend.components import render_lieux_testes

        setup_mock_st(mock_st)

        mock_lieu = MagicMock()
        mock_lieu.type_activite = "parc"
        mock_lieu.titre = "Mauvais Parc"
        mock_lieu.lieu = None
        mock_lieu.commentaire = None
        mock_lieu.note_lieu = 1
        mock_lieu.a_refaire = False
        mock_lieu.cout_reel = None
        mock_lieu.date_prevue = date(2026, 2, 15)

        mock_lieux.return_value = [mock_lieu]

        render_lieux_testes()

        mock_st.write.assert_called()


@pytest.mark.unit
class TestRenderAddActivitySubmit:
    """Tests for form submission in render_add_activity (lines 217-239)"""

    @patch("src.modules.famille.weekend.components.WeekendActivity")
    @patch("src.modules.famille.weekend.components.obtenir_contexte_db")
    @patch("src.modules.famille.weekend.components.get_next_weekend")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_add_activity_submit_valid(
        self, mock_st, mock_weekend, mock_ctx, mock_activity_class
    ) -> None:
        from src.modules.famille.weekend.components import render_add_activity

        setup_mock_st(mock_st, {"weekend_add_date": date(2026, 2, 21)})
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "Jardin des Plantes"
        mock_st.selectbox.return_value = "parc"
        mock_st.date_input.return_value = date(2026, 2, 21)
        mock_st.time_input.return_value = time(14, 0)
        mock_st.number_input.return_value = 0.0
        mock_st.text_area.return_value = "Super sortie"
        mock_st.checkbox.return_value = True
        mock_weekend.return_value = (date(2026, 2, 21), date(2026, 2, 22))

        mock_db = MagicMock()
        mock_ctx.return_value.__enter__ = MagicMock(return_value=mock_db)
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        render_add_activity()

        mock_activity_class.assert_called()
        mock_db.add.assert_called()
        mock_db.commit.assert_called()
        mock_st.success.assert_called()
        mock_st.rerun.assert_called()

    @patch("src.modules.famille.weekend.components.WeekendActivity")
    @patch("src.modules.famille.weekend.components.obtenir_contexte_db")
    @patch("src.modules.famille.weekend.components.get_next_weekend")
    @patch("src.modules.famille.weekend.components.st")
    def test_render_add_activity_submit_exception(
        self, mock_st, mock_weekend, mock_ctx, mock_activity_class
    ) -> None:
        from src.modules.famille.weekend.components import render_add_activity

        setup_mock_st(mock_st)
        mock_st.form_submit_button.return_value = True
        mock_st.text_input.return_value = "Test Activity"
        mock_weekend.return_value = (date(2026, 2, 21), date(2026, 2, 22))

        mock_ctx.return_value.__enter__ = MagicMock(side_effect=Exception("Database error"))
        mock_ctx.return_value.__exit__ = MagicMock(return_value=False)

        render_add_activity()

        mock_st.error.assert_called()
