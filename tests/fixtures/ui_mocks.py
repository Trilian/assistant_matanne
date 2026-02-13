"""
Fixtures et mocks pour les tests UI Streamlit.

Fournit des utilitaires standardisés pour tester les composants UI:
- StreamlitMock complet avec tous les widgets
- Factories de contexte par domaine
- MockDatabase avec données fixtures
"""

from contextlib import contextmanager
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════
# STREAMLIT MOCK ÉTENDU
# ═══════════════════════════════════════════════════════════


class SessionStateMock(dict):
    """Mock pour st.session_state supportant accès attribut et dict."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


class ContextManagerMock(MagicMock):
    """Mock pour les context managers Streamlit (columns, tabs, container, etc.)"""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def create_streamlit_mock(session_state: dict[str, Any] = None) -> MagicMock:
    """
    Crée un mock Streamlit complet avec tous les widgets.

    Args:
        session_state: Données initiales pour session_state

    Returns:
        MagicMock configuré pour simuler Streamlit
    """
    mock_st = MagicMock()
    mock_st.session_state = SessionStateMock(session_state or {})

    # === Context Managers ===
    def make_columns(spec, **kwargs):
        if isinstance(spec, int):
            return [ContextManagerMock() for _ in range(spec)]
        elif isinstance(spec, (list, tuple)):
            return [ContextManagerMock() for _ in spec]
        return [ContextManagerMock(), ContextManagerMock()]

    def make_tabs(labels):
        return [ContextManagerMock() for _ in labels]

    mock_st.columns = MagicMock(side_effect=make_columns)
    mock_st.tabs = MagicMock(side_effect=make_tabs)
    mock_st.container = MagicMock(return_value=ContextManagerMock())
    mock_st.expander = MagicMock(return_value=ContextManagerMock())
    mock_st.form = MagicMock(return_value=ContextManagerMock())
    mock_st.sidebar = ContextManagerMock()
    mock_st.empty = MagicMock(return_value=ContextManagerMock())
    mock_st.spinner = MagicMock(return_value=ContextManagerMock())

    # === Display Functions (no return) ===
    mock_st.title = MagicMock()
    mock_st.header = MagicMock()
    mock_st.subheader = MagicMock()
    mock_st.write = MagicMock()
    mock_st.markdown = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.text = MagicMock()
    mock_st.code = MagicMock()
    mock_st.latex = MagicMock()
    mock_st.divider = MagicMock()

    # === Feedback ===
    mock_st.success = MagicMock()
    mock_st.error = MagicMock()
    mock_st.warning = MagicMock()
    mock_st.info = MagicMock()
    mock_st.toast = MagicMock()
    mock_st.balloons = MagicMock()
    mock_st.snow = MagicMock()

    # === Input Widgets (return default values) ===
    mock_st.button = MagicMock(return_value=False)
    mock_st.checkbox = MagicMock(return_value=False)
    mock_st.radio = MagicMock(return_value=None)
    mock_st.selectbox = MagicMock(return_value=None)
    mock_st.multiselect = MagicMock(return_value=[])
    mock_st.slider = MagicMock(return_value=0)
    mock_st.select_slider = MagicMock(return_value=None)
    mock_st.text_input = MagicMock(return_value="")
    mock_st.text_area = MagicMock(return_value="")
    mock_st.number_input = MagicMock(return_value=0)
    mock_st.date_input = MagicMock(return_value=date.today())
    mock_st.time_input = MagicMock(return_value=time(12, 0))
    mock_st.file_uploader = MagicMock(return_value=None)
    mock_st.color_picker = MagicMock(return_value="#000000")
    mock_st.form_submit_button = MagicMock(return_value=False)
    mock_st.download_button = MagicMock(return_value=False)

    # === Data Display ===
    mock_st.metric = MagicMock()
    mock_st.dataframe = MagicMock()
    mock_st.table = MagicMock()
    mock_st.json = MagicMock()
    mock_st.bar_chart = MagicMock()
    mock_st.line_chart = MagicMock()
    mock_st.area_chart = MagicMock()
    mock_st.plotly_chart = MagicMock()
    mock_st.pyplot = MagicMock()
    mock_st.image = MagicMock()
    mock_st.audio = MagicMock()
    mock_st.video = MagicMock()

    # === Control Flow ===
    mock_st.rerun = MagicMock()
    mock_st.stop = MagicMock()
    mock_st.experimental_rerun = MagicMock()

    # === Cache Decorators (return function as-is) ===
    mock_st.cache_data = MagicMock(side_effect=lambda *args, **kwargs: lambda f: f)
    mock_st.cache_resource = MagicMock(side_effect=lambda *args, **kwargs: lambda f: f)

    # === Progress ===
    mock_st.progress = MagicMock(return_value=ContextManagerMock())
    mock_st.status = MagicMock(return_value=ContextManagerMock())

    return mock_st


# ═══════════════════════════════════════════════════════════
# FIXTURES PAR DOMAINE
# ═══════════════════════════════════════════════════════════


def create_cuisine_session_state() -> dict[str, Any]:
    """Session state par défaut pour les tests cuisine."""
    return {
        "recette_selectionnee": None,
        "mode_edition": False,
        "liste_courses_active": None,
        "inventaire_filtre": "tous",
        "planificateur_semaine": date.today(),
    }


def create_famille_session_state() -> dict[str, Any]:
    """Session state par défaut pour les tests famille."""
    return {
        "jules_age_mois": 19,
        "weekend_date": date.today(),
        "suivi_perso_tab": 0,
        "achats_filtre": "tous",
    }


def create_jeux_session_state() -> dict[str, Any]:
    """Session state par défaut pour les tests jeux."""
    return {
        "paris_equipe_selectionnee": None,
        "loto_grille_courante": [],
        "paris_filtre_sport": "football",
    }


def create_maison_session_state() -> dict[str, Any]:
    """Session state par défaut pour les tests maison."""
    return {
        "depenses_mois": date.today().month,
        "depenses_annee": date.today().year,
        "jardin_zone_active": None,
    }


def create_planning_session_state() -> dict[str, Any]:
    """Session state par défaut pour les tests planning."""
    return {
        "cal_semaine_debut": date.today() - timedelta(days=date.today().weekday()),
        "planning_mode": "liste",
    }


DOMAIN_SESSION_STATES = {
    "cuisine": create_cuisine_session_state,
    "famille": create_famille_session_state,
    "jeux": create_jeux_session_state,
    "maison": create_maison_session_state,
    "planning": create_planning_session_state,
}


def create_ui_test_context(domain: str = None, extra_state: dict[str, Any] = None) -> MagicMock:
    """
    Crée un contexte de test UI complet pour un domaine.

    Args:
        domain: Nom du domaine (cuisine, famille, jeux, maison, planning)
        extra_state: Données supplémentaires pour session_state

    Returns:
        MagicMock Streamlit configuré
    """
    session_data = {}

    if domain and domain in DOMAIN_SESSION_STATES:
        session_data = DOMAIN_SESSION_STATES[domain]()

    if extra_state:
        session_data.update(extra_state)

    return create_streamlit_mock(session_data)


# ═══════════════════════════════════════════════════════════
# DONNÉES FIXTURES
# ═══════════════════════════════════════════════════════════


def create_sample_recette() -> dict:
    """Crée une recette de test."""
    return {
        "id": 1,
        "nom": "Pâtes Carbonara",
        "description": "Recette italienne classique",
        "temps_preparation": 15,
        "temps_cuisson": 20,
        "portions": 4,
        "difficulte": "facile",
        "categorie": "plat",
        "ingredients": [
            {"nom": "Pâtes", "quantite": 400, "unite": "g"},
            {"nom": "Lardons", "quantite": 200, "unite": "g"},
            {"nom": "Å’ufs", "quantite": 4, "unite": ""},
            {"nom": "Parmesan", "quantite": 100, "unite": "g"},
        ],
        "instructions": "1. Cuire les pâtes\n2. Faire revenir les lardons\n3. Mélanger",
        "tags": ["rapide", "italien"],
        "created_at": datetime.now(),
    }


def create_sample_ingredient_stock() -> dict:
    """Crée un ingrédient en stock de test."""
    return {
        "id": 1,
        "nom": "Tomates",
        "quantite": 5,
        "unite": "pièces",
        "categorie": "légumes",
        "emplacement": "frigo",
        "date_peremption": date.today() + timedelta(days=7),
        "seuil_alerte": 2,
    }


def create_sample_depense() -> dict:
    """Crée une dépense de test."""
    return {
        "id": 1,
        "categorie": "electricite",
        "montant": Decimal("85.50"),
        "consommation": Decimal("320"),
        "mois": date.today().month,
        "annee": date.today().year,
        "note": "Facture février",
    }


def create_sample_family_purchase() -> dict:
    """Crée un achat famille de test."""
    return {
        "id": 1,
        "nom": "Pantalon Jules",
        "categorie": "jules_vetements",
        "priorite": "moyenne",
        "prix_estime": 25.0,
        "taille": "86",
        "achete": False,
    }


# ═══════════════════════════════════════════════════════════
# PYTEST FIXTURES
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_st():
    """Fixture de base pour mock Streamlit."""
    return create_streamlit_mock()


@pytest.fixture
def mock_st_cuisine():
    """Mock Streamlit configuré pour le domaine cuisine."""
    return create_ui_test_context("cuisine")


@pytest.fixture
def mock_st_famille():
    """Mock Streamlit configuré pour le domaine famille."""
    return create_ui_test_context("famille")


@pytest.fixture
def mock_st_jeux():
    """Mock Streamlit configuré pour le domaine jeux."""
    return create_ui_test_context("jeux")


@pytest.fixture
def mock_st_maison():
    """Mock Streamlit configuré pour le domaine maison."""
    return create_ui_test_context("maison")


@pytest.fixture
def mock_st_planning():
    """Mock Streamlit configuré pour le domaine planning."""
    return create_ui_test_context("planning")


@pytest.fixture
def sample_recette():
    """Fixture recette de test."""
    return create_sample_recette()


@pytest.fixture
def sample_stock():
    """Fixture stock de test."""
    return create_sample_ingredient_stock()


@pytest.fixture
def sample_depense():
    """Fixture dépense de test."""
    return create_sample_depense()


@pytest.fixture
def sample_purchase():
    """Fixture achat famille de test."""
    return create_sample_family_purchase()


# ═══════════════════════════════════════════════════════════
# CONTEXT MANAGERS POUR PATCHER STREAMLIT
# ═══════════════════════════════════════════════════════════


@contextmanager
def patch_streamlit(session_state: dict[str, Any] = None):
    """
    Context manager pour patcher streamlit dans les imports.

    Usage:
        with patch_streamlit({"key": "value"}) as mock_st:
            from src.modules.cuisine.recettes import app
            app()
            mock_st.title.assert_called()
    """
    mock_st = create_streamlit_mock(session_state)

    with patch.dict("sys.modules", {"streamlit": mock_st}):
        yield mock_st


@contextmanager
def patch_streamlit_for_module(module_path: str, session_state: dict[str, Any] = None):
    """
    Patche streamlit spécifiquement pour un module.

    Args:
        module_path: Chemin du module (e.g., "src.modules.cuisine.recettes")
        session_state: Données session_state

    Usage:
        with patch_streamlit_for_module("src.modules.cuisine.recettes") as mock_st:
            from src.modules.cuisine.recettes import render_liste
            render_liste(mock_db)
    """
    mock_st = create_streamlit_mock(session_state)

    patches = [
        patch(f"{module_path}.st", mock_st),
        patch("streamlit", mock_st),
    ]

    for p in patches:
        p.start()

    try:
        yield mock_st
    finally:
        for p in patches:
            p.stop()


# ═══════════════════════════════════════════════════════════
# ASSERTIONS HELPERS
# ═══════════════════════════════════════════════════════════


def assert_streamlit_called(mock_st: MagicMock, method: str, times: int = None):
    """
    Vérifie qu'une méthode Streamlit a été appelée.

    Args:
        mock_st: Mock Streamlit
        method: Nom de la méthode (e.g., "title", "write")
        times: Nombre d'appels attendu (None = au moins 1)
    """
    method_mock = getattr(mock_st, method)
    if times is not None:
        assert (
            method_mock.call_count == times
        ), f"Expected {method} to be called {times} times, got {method_mock.call_count}"
    else:
        assert method_mock.called, f"Expected {method} to be called at least once"


def assert_metric_displayed(mock_st: MagicMock, label: str = None, value: Any = None):
    """
    Vérifie qu'un metric a été affiché.

    Args:
        mock_st: Mock Streamlit
        label: Label attendu (optionnel)
        value: Valeur attendue (optionnel)
    """
    assert mock_st.metric.called, "Expected st.metric to be called"

    if label or value:
        calls = mock_st.metric.call_args_list
        found = False
        for call in calls:
            args, kwargs = call
            call_label = args[0] if args else kwargs.get("label")
            call_value = args[1] if len(args) > 1 else kwargs.get("value")

            if label and call_label != label:
                continue
            if value and call_value != value:
                continue
            found = True
            break

        assert found, f"Expected metric with label='{label}', value='{value}' not found"


def assert_error_shown(mock_st: MagicMock, message_contains: str = None):
    """Vérifie qu'une erreur a été affichée."""
    assert mock_st.error.called, "Expected st.error to be called"

    if message_contains:
        calls = mock_st.error.call_args_list
        found = any(message_contains in str(call) for call in calls)
        assert found, f"Expected error containing '{message_contains}'"


def assert_success_shown(mock_st: MagicMock, message_contains: str = None):
    """Vérifie qu'un succès a été affiché."""
    assert mock_st.success.called, "Expected st.success to be called"

    if message_contains:
        calls = mock_st.success.call_args_list
        found = any(message_contains in str(call) for call in calls)
        assert found, f"Expected success containing '{message_contains}'"
