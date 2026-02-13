"""
Conftest local pour les tests famille.
Surcharge le conftest root pour éviter les imports problématiques.
"""

from unittest.mock import MagicMock, patch

import pytest

# Ce conftest minimaliste évite les imports lourds du conftest root


@pytest.fixture
def mock_db():
    """Fixture pour mocker la base de données"""
    return MagicMock()


@pytest.fixture
def mock_streamlit():
    """Fixture pour mocker streamlit"""
    with patch("streamlit.session_state", {}):
        yield
