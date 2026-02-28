from unittest.mock import Mock, patch

import pytest


@pytest.mark.unit
@patch("streamlit.warning")
@patch("streamlit.metric")
def test_afficher_global_stats_handles_recettes_exception(mock_metric, mock_warning):
    """Si obtenir_service_recettes().get_stats() lève, afficher_global_stats doit loguer et appeler st.warning."""
    # Préparer le service recettes qui lèvera
    mock_recettes_service = Mock()
    mock_recettes_service.get_stats.side_effect = Exception("DB error")

    # Services inventaire/courses/planning retournent des valeurs valides
    mock_inventaire_service = Mock()
    mock_inventaire_service.get_stats.return_value = {"total": 5}
    mock_inventaire_service.get_inventaire_complet.return_value = []

    mock_courses_service = Mock()
    mock_courses_service.get_stats.return_value = {"total": 2}

    mock_planning_service = Mock()
    mock_planning_service.get_planning.return_value = Mock(repas=[])

    with (
        patch(
            "src.services.cuisine.recettes.obtenir_service_recettes",
            return_value=mock_recettes_service,
        ),
        patch(
            "src.services.inventaire.obtenir_service_inventaire",
            return_value=mock_inventaire_service,
        ),
        patch(
            "src.services.cuisine.courses.obtenir_service_courses",
            return_value=mock_courses_service,
        ),
        patch(
            "src.services.cuisine.planning.obtenir_service_planning",
            return_value=mock_planning_service,
        ),
    ):
        # Importer la fonction sous test et l'exécuter
        from src.modules.accueil.stats import afficher_global_stats

        afficher_global_stats()

    # Vérifier que st.warning a été appelé pour les recettes
    assert mock_warning.called
